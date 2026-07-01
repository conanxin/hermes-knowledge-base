#!/usr/bin/env python3
"""Smoke tests for the material fetch layer (v0.3.80)."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from fetchers.wechat_fetcher import WeChatFetcher  # type: ignore
from fetchers.web_fetcher import WebFetcher  # type: ignore
from fetchers.youtube_fetcher import YouTubeFetcher  # type: ignore

TEST_PY = sys.executable
ROUTER_SCRIPT = SCRIPTS_DIR / "material_to_kb.py"
WECHAT_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "wechat_sample_article.html"
WEB_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "web_sample_article.html"
YOUTUBE_METADATA = REPO_ROOT / "tests" / "fixtures" / "youtube_sample_metadata.json"
YTDLP_TRANSCRIPT = REPO_ROOT / "tests" / "fixtures" / "youtube_ytdlp_subtitle.vtt"
YOUTUBE_URL = "https://youtu.be/ytfixture123"
ENV = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}


def check(condition: bool, label: str, detail: str = "") -> bool:
    if condition:
        print(f"  [PASS] {label}")
        if detail:
            print(f"         {detail}")
        return True
    print(f"  [FAIL] {label}")
    if detail:
        print(f"         {detail}")
    return False


def metadata_count() -> int:
    return len(list((REPO_ROOT / "content").glob("**/metadata.yaml")))


def run(cmd: list[str], *, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env or ENV,
    )
    return proc.returncode, proc.stdout, proc.stderr


def parse_router_stdout(stdout: str) -> dict:
    start = stdout.find("{")
    if start < 0:
        return {}
    return json.loads(stdout[start:])


def smoke_1_wechat_fetch() -> bool:
    print("\n=== Smoke 1: WeChat fetcher returns text ===")
    result = WeChatFetcher(route_flag="--html-file").fetch(str(WECHAT_FIXTURE))
    ok = check(result.get("status") == "ok", "WeChat fetch status ok", str(result))
    ok &= check(len(result.get("text", "")) > 200, "WeChat fetch returns article text")
    ok &= check(result.get("fetch_quality") == "full", "WeChat fetch quality full")
    return ok


def smoke_2_web_fetch() -> bool:
    print("\n=== Smoke 2: Web fetcher returns text ===")
    result = WebFetcher(route_flag="--html-file").fetch(str(WEB_FIXTURE))
    ok = check(result.get("status") == "ok", "Web fetch status ok", str(result))
    ok &= check(len(result.get("text", "")) > 300, "Web fetch returns article text")
    ok &= check(result.get("fetch_quality") == "full", "Web fetch quality full")
    ok &= check(bool(result.get("metadata", {}).get("extraction_method")), "Web extraction method recorded")
    return ok


def smoke_3_youtube_metadata_fallback() -> bool:
    print("\n=== Smoke 3: YouTube fetcher returns metadata_only without captions ===")
    old_meta = os.environ.get("HERMES_YOUTUBE_FIXTURE_METADATA")
    old_transcript = os.environ.get("HERMES_YOUTUBE_FIXTURE_TRANSCRIPT")
    os.environ["HERMES_YOUTUBE_FIXTURE_METADATA"] = str(YOUTUBE_METADATA)
    os.environ.pop("HERMES_YOUTUBE_FIXTURE_TRANSCRIPT", None)
    try:
        result = YouTubeFetcher(route_flag="--url").fetch(YOUTUBE_URL)
    finally:
        if old_meta is None:
            os.environ.pop("HERMES_YOUTUBE_FIXTURE_METADATA", None)
        else:
            os.environ["HERMES_YOUTUBE_FIXTURE_METADATA"] = old_meta
        if old_transcript is None:
            os.environ.pop("HERMES_YOUTUBE_FIXTURE_TRANSCRIPT", None)
        else:
            os.environ["HERMES_YOUTUBE_FIXTURE_TRANSCRIPT"] = old_transcript
    ok = check(result.get("status") == "partial", "YouTube fetch status partial", str(result))
    ok &= check(result.get("fetch_quality") == "metadata_only", "YouTube quality is metadata_only")
    ok &= check(len(result.get("text", "")) > 80, "YouTube fallback returns metadata/description text")
    ok &= check("transcript" in result.get("reason", "").lower(), "YouTube fallback records transcript reason")
    capture = result.get("metadata", {}).get("capture", {})
    ok &= check(capture.get("import_allowed") is False, "YouTube fallback import_allowed false", str(capture))
    ok &= check(bool(capture.get("import_block_reason")), "YouTube fallback records import block reason", str(capture))
    return ok


def smoke_4_router_uses_fetch_layer() -> bool:
    print("\n=== Smoke 4: material router records fetch fallback ===")
    env = {
        **ENV,
        "HERMES_YOUTUBE_FIXTURE_METADATA": str(YOUTUBE_METADATA),
    }
    env.pop("HERMES_YOUTUBE_FIXTURE_TRANSCRIPT", None)
    before = metadata_count()
    code, out, err = run([TEST_PY, str(ROUTER_SCRIPT), "--input", YOUTUBE_URL, "--dry-run"], env=env)
    after = metadata_count()
    data = parse_router_stdout(out)
    item = data.get("items", [{}])[0]
    ok = check(code == 0, "router exits 0", f"exit={code}\nstderr tail: {err[-300:]}")
    ok &= check(item.get("inferred_type") == "youtube_url", "router recognizes YouTube URL", str(item))
    ok &= check(item.get("fetch_status") == "partial", "router records partial fetch", str(item))
    ok &= check(item.get("fetch_quality") in {"partial", "metadata_only"}, "router records fallback quality", str(item))
    ok &= check(item.get("status") == "DRY_RUN_OK", "router allows partial dry-run", str(item))
    ok &= check(item.get("import_allowed") is False, "router records fallback import_allowed false", str(item))
    ok &= check(bool(item.get("import_block_reason")), "router records fallback import block reason", str(item))
    ok &= check(before == after, "dry-run does not write KB entry", f"before={before}, after={after}")
    ok &= check((REPO_ROOT / data.get("report_markdown", "")).exists(), "markdown report generated")
    ok &= check((REPO_ROOT / data.get("report_json", "")).exists(), "json report generated")
    return ok


def smoke_5_youtube_ytdlp_fixture_fallback() -> bool:
    print("\n=== Smoke 5: YouTube fetcher can use yt-dlp fixture fallback ===")
    old_env = {name: os.environ.get(name) for name in [
        "HERMES_YOUTUBE_FIXTURE_METADATA",
        "HERMES_YOUTUBE_FIXTURE_TRANSCRIPT",
        "HERMES_YTDLP_FIXTURE_SUBTITLE",
        "HERMES_YTDLP_FIXTURE_KIND",
        "HERMES_YTDLP_FIXTURE_LANGUAGE",
    ]}
    os.environ["HERMES_YOUTUBE_FIXTURE_METADATA"] = str(YOUTUBE_METADATA)
    os.environ.pop("HERMES_YOUTUBE_FIXTURE_TRANSCRIPT", None)
    os.environ["HERMES_YTDLP_FIXTURE_SUBTITLE"] = str(YTDLP_TRANSCRIPT)
    os.environ["HERMES_YTDLP_FIXTURE_KIND"] = "auto"
    os.environ["HERMES_YTDLP_FIXTURE_LANGUAGE"] = "en"
    try:
        result = YouTubeFetcher(route_flag="--url").fetch(YOUTUBE_URL)
    finally:
        for name, old in old_env.items():
            if old is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = old
    capture = result.get("metadata", {}).get("capture", {})
    attempts = capture.get("provider_attempts") or []
    ok = check(result.get("status") == "ok", "YouTube yt-dlp fixture fetch status ok", str(result))
    ok &= check(result.get("fetch_quality") == "full", "YouTube yt-dlp fixture quality full")
    ok &= check(capture.get("transcript_kind") == "auto", "auto transcript kind recorded", str(capture))
    ok &= check(capture.get("transcript_needs_review") is True, "auto transcript marked needs_review", str(capture))
    ok &= check(capture.get("import_allowed") is False, "auto transcript import blocked by default", str(capture))
    ok &= check(any(a.get("provider") == "yt-dlp" and a.get("status") == "ok" for a in attempts if isinstance(a, dict)),
                "provider_attempts include yt-dlp ok", str(attempts))
    return ok


def main() -> int:
    print("=" * 60)
    print("Material fetch layer smoke tests (v0.3.80)")
    print("=" * 60)
    results = [
        smoke_1_wechat_fetch(),
        smoke_2_web_fetch(),
        smoke_3_youtube_metadata_fallback(),
        smoke_4_router_uses_fetch_layer(),
        smoke_5_youtube_ytdlp_fixture_fallback(),
    ]
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL FETCH LAYER SMOKE TESTS PASSED ({passed}/{total})")
        return 0
    print(f"FETCH LAYER SMOKE TESTS FAILED ({passed}/{total})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
