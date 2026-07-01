#!/usr/bin/env python3
"""Smoke tests for YouTube transcript import (v0.3.79).

The tests are offline and use synthetic metadata/VTT fixtures. They do not
fetch YouTube, download video files, or rely on external caption services.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

YOUTUBE_SCRIPT = REPO_ROOT / "scripts" / "youtube_to_kb.py"
ROUTER_SCRIPT = REPO_ROOT / "scripts" / "material_to_kb.py"
METADATA_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "youtube_sample_metadata.json"
TRANSCRIPT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "youtube_sample_transcript.vtt"
PDF_FIXTURE = "tests/fixtures/material_router_sample.pdf"
YOUTUBE_URL = "https://youtu.be/ytfixture123"


def run(cmd: list[str], cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env or ENV,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def check(condition: bool, name: str, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}")
    if detail:
        print(f"         {detail}")
    return condition


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"failed to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def parse_capture_path(stderr: str) -> Path:
    match = re.search(r"\[capture\]\s+(.+?)(?:\r?\n|$)", stderr)
    if not match:
        raise AssertionError("missing [capture] line")
    path = Path(match.group(1).strip())
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def metadata_count() -> int:
    return len(list((REPO_ROOT / "content").glob("**/metadata.yaml")))


def parse_router_stdout(stdout: str) -> dict:
    return json.loads(stdout)


def smoke_1_inference_rules() -> bool:
    print("\n=== Smoke 1: router inference rules ===")
    router = load_module(ROUTER_SCRIPT, "material_to_kb")
    yt = router.infer_input("https://www.youtube.com/watch?v=ytfixture123", index=0)
    short = router.infer_input("https://youtube.com/shorts/ytfixture123", index=1)
    web = router.infer_input("https://example.com/article", index=2)
    wechat = router.infer_input("https://mp.weixin.qq.com/s/example", index=3)
    pdf = router.infer_input(PDF_FIXTURE, index=4)
    ok = check(yt["inferred_type"] == "youtube_url" and yt["route"] == "youtube_to_kb.py" and yt["supported"] is True,
               "watch URL inferred as supported youtube_url", str(yt))
    ok &= check(short["inferred_type"] == "youtube_url" and short["route"] == "youtube_to_kb.py",
                "shorts URL inferred as youtube_url", str(short))
    ok &= check(web["inferred_type"] == "generic_web_url" and web["route"] == "web_article_to_kb.py",
                "generic web route unaffected", str(web))
    ok &= check(wechat["inferred_type"] == "wechat_url" and wechat["route_kind"] == "wechat",
                "WeChat route unaffected", str(wechat))
    ok &= check(pdf["status"] if "status" in pdf else pdf["supported"] is False,
                "PDF remains unsupported at inference layer", str(pdf))
    return ok


def smoke_2_youtube_script_fixture_dry_run() -> tuple[bool, Path | None]:
    print("\n=== Smoke 2: youtube_to_kb fixture dry-run ===")
    before = metadata_count()
    code, out, err = run([
        TEST_PY,
        str(YOUTUBE_SCRIPT),
        "--url",
        YOUTUBE_URL,
        "--metadata-file",
        str(METADATA_FIXTURE),
        "--transcript-file",
        str(TRANSCRIPT_FIXTURE),
        "--dry-run",
    ])
    after = metadata_count()
    ok = check(code == 0, "youtube_to_kb exits 0", f"exit={code}\nstderr tail: {err[-300:]}")
    ok &= check("STATUS: DRY_RUN_OK" in out, "dry-run reports STATUS: DRY_RUN_OK")
    ok &= check(before == after, "dry-run does not write KB entry", f"before={before}, after={after}")
    if not ok:
        return False, None
    cap_path = parse_capture_path(err)
    ok &= check(cap_path.exists(), "capture JSON written", str(cap_path))
    return ok, cap_path


def smoke_3_capture_and_bundle(cap_path: Path) -> bool:
    print("\n=== Smoke 3: capture fields and generated bundle ===")
    module = load_module(YOUTUBE_SCRIPT, "youtube_to_kb")
    data = json.loads(cap_path.read_text(encoding="utf-8"))
    bundle = module.generate_output_bundle(data)
    ok = check(data.get("video_id") == "ytfixture123", "video_id captured", data.get("video_id", ""))
    ok &= check(data.get("transcript_language") == "en", "transcript language captured", data.get("transcript_language", ""))
    ok &= check(data.get("transcript_kind") == "manual", "manual transcript selected", data.get("transcript_kind", ""))
    ok &= check(len(data.get("content_markdown", "")) > 500, "transcript Markdown non-empty")
    ok &= check('content_kind: "youtube_transcript"' in bundle["metadata.yaml"],
                "metadata marks youtube_transcript")
    ok &= check('source_platform: "youtube"' in bundle["metadata.yaml"],
                "metadata marks source_platform youtube")
    ok &= check("status: \"needs_translation_review\"" in bundle["metadata.yaml"],
                "English transcript uses needs_translation_review")
    ok &= check("## 视频核心问题" in bundle["summary.md"], "summary includes video section")
    ok &= check("## 复看提醒" in bundle["notes.md"], "notes includes rewatch reminder")
    return ok


def smoke_4_no_transcript_falls_back_partial() -> bool:
    print("\n=== Smoke 4: missing transcript falls back to partial capture ===")
    code, out, err = run([
        TEST_PY,
        str(YOUTUBE_SCRIPT),
        "--url",
        YOUTUBE_URL,
        "--metadata-file",
        str(METADATA_FIXTURE),
        "--dry-run",
    ])
    combined = out + "\n" + err
    ok = check(code == 0, "missing transcript exits 0 via fallback", f"exit={code}")
    ok &= check("STATUS: DRY_RUN_OK" in combined,
                "missing transcript reports DRY_RUN_OK", combined[-300:])
    ok &= check("fetch_quality: partial" in combined or "fetch_quality: metadata_only" in combined,
                "fallback reports partial or metadata_only quality", combined[-300:])
    return ok


def smoke_5_duplicate_video_id() -> bool:
    print("\n=== Smoke 5: duplicate video_id detection ===")
    duplicate_meta = json.loads(METADATA_FIXTURE.read_text(encoding="utf-8"))
    duplicate_meta["video_id"] = "F3fCktnkBbc"
    duplicate_meta["source_url"] = "https://www.youtube.com/watch?v=F3fCktnkBbc"
    duplicate_meta["canonical_url"] = "https://www.youtube.com/watch?v=F3fCktnkBbc"
    with tempfile.TemporaryDirectory(prefix=".youtube-dup-smoke-", dir=REPO_ROOT) as tmp:
        meta_path = Path(tmp) / "metadata.json"
        meta_path.write_text(json.dumps(duplicate_meta, ensure_ascii=False, indent=2), encoding="utf-8")
        code, out, err = run([
            TEST_PY,
            str(YOUTUBE_SCRIPT),
            "--url",
            "https://www.youtube.com/watch?v=F3fCktnkBbc",
            "--metadata-file",
            str(meta_path),
            "--transcript-file",
            str(TRANSCRIPT_FIXTURE),
            "--dry-run",
        ])
    combined = out + "\n" + err
    ok = check(code == 0, "duplicate dry-run exits 0", f"exit={code}")
    ok &= check("STATUS: DRY_RUN_DUPLICATE" in combined or "STATUS: SKIPPED_DUPLICATE" in combined,
                "duplicate status emitted", combined[-300:])
    ok &= check("DUPLICATE_OF:" in combined and "2026-06-25-conan-harvard-commencement-2026" in combined,
                "duplicate_of points to existing KB path", combined[-300:])
    return ok


def smoke_6_material_router_youtube_route() -> bool:
    print("\n=== Smoke 6: material_to_kb routes YouTube offline ===")
    env = {
        **ENV,
        "HERMES_YOUTUBE_FIXTURE_METADATA": str(METADATA_FIXTURE),
        "HERMES_YOUTUBE_FIXTURE_TRANSCRIPT": str(TRANSCRIPT_FIXTURE),
    }
    before = metadata_count()
    code, out, err = run([TEST_PY, str(ROUTER_SCRIPT), "--input", YOUTUBE_URL, "--dry-run"], env=env)
    after = metadata_count()
    ok = check(code == 0, "router exits 0", f"exit={code}\nstderr tail: {err[-300:]}")
    data = parse_router_stdout(out)
    item = data.get("items", [{}])[0]
    ok &= check(item.get("inferred_type") == "youtube_url", "router item inferred as youtube_url", str(item))
    ok &= check(item.get("route") == "youtube_to_kb.py", "router item routed to youtube_to_kb.py", str(item))
    ok &= check(item.get("status") in {"DRY_RUN_OK", "SKIPPED_DUPLICATE"}, "router dry-run completed", item.get("status", ""))
    ok &= check(before == after, "router dry-run does not write KB entry", f"before={before}, after={after}")
    ok &= check((REPO_ROOT / data.get("report_markdown", "")).exists(), "markdown report generated")
    ok &= check((REPO_ROOT / data.get("report_json", "")).exists(), "json report generated")
    return ok


def smoke_7_pdf_still_unsupported() -> bool:
    print("\n=== Smoke 7: PDF remains unsupported ===")
    code, out, err = run([TEST_PY, str(ROUTER_SCRIPT), "--input", PDF_FIXTURE, "--dry-run"])
    ok = check(code == 0, "router exits 0 for unsupported PDF", f"exit={code}\nstderr tail: {err[-300:]}")
    data = parse_router_stdout(out)
    item = data.get("items", [{}])[0]
    ok &= check(item.get("status") == "BLOCKED_UNSUPPORTED", "PDF status is BLOCKED_UNSUPPORTED", str(item))
    ok &= check("PDF import/OCR route not implemented yet" in item.get("failure_reason", ""),
                "PDF unsupported reason preserved")
    return ok


def smoke_8_quality_gates() -> bool:
    print("\n=== Smoke 8: check_kb and check_pages_sync ===")
    code1, out1, _ = run([TEST_PY, str(REPO_ROOT / "scripts" / "check_kb.py")])
    code2, out2, _ = run([TEST_PY, str(REPO_ROOT / "scripts" / "check_pages_sync.py")])
    ok = check(code1 == 0 and "STATUS: PASS" in out1, "check_kb.py PASS", f"exit={code1}")
    ok &= check(code2 == 0 and "STATUS: PASS" in out2, "check_pages_sync.py PASS", f"exit={code2}")
    return ok


def main() -> int:
    print("=" * 60)
    print("YouTube transcript import smoke tests (v0.3.79)")
    print("=" * 60)
    results = [smoke_1_inference_rules()]
    ok2, cap_path = smoke_2_youtube_script_fixture_dry_run()
    results.append(ok2)
    results.append(smoke_3_capture_and_bundle(cap_path) if cap_path else False)
    results.extend([
        smoke_4_no_transcript_falls_back_partial(),
        smoke_5_duplicate_video_id(),
        smoke_6_material_router_youtube_route(),
        smoke_7_pdf_still_unsupported(),
        smoke_8_quality_gates(),
    ])
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL YOUTUBE IMPORT SMOKE TESTS PASSED ({passed}/{total})")
        return 0
    print(f"YOUTUBE IMPORT SMOKE TESTS FAILED ({passed}/{total})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
