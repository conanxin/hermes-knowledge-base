#!/usr/bin/env python3
"""Smoke tests for the unified material import router (v0.3.76/v0.3.77).

Runs offline against local fixtures, a local HTTP server, and unsupported
placeholder routes.

Verifies:
1. WeChat URLs are recognized as wechat_url.
2. Local HTML and Markdown are recognized as local_text_article.
3. Generic web URLs are recognized and routed to web_article_to_kb.py.
4. YouTube URLs return BLOCKED_UNSUPPORTED when no stable route is wired.
5. Local PDFs return BLOCKED_UNSUPPORTED when no stable route is wired.
6. input-list skips blank lines and # comments.
7. dry-run does not write KB entries.
8. Mixed batches do not stop on BLOCKED_UNSUPPORTED.
9. Markdown and JSON reports are generated.

Usage:
    python3 tests/run_material_router_smoke.py
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

ROUTER_SCRIPT = REPO_ROOT / "scripts" / "material_to_kb.py"
MIXED_INPUTS = REPO_ROOT / "tests" / "fixtures" / "material_inputs_mixed.txt"
HTML_FIXTURE = "tests/fixtures/wechat_sample_article.html"
MD_FIXTURE = "tests/fixtures/wechat_chinese_with_images.md"
WEB_FIXTURE_DIR = REPO_ROOT / "tests" / "fixtures"
WEB_FIXTURE_NAME = "web_sample_article.html"
YOUTUBE_URL = "https://youtu.be/material-router-smoke"
GENERIC_URL = "https://example.com/material-router-smoke"
PDF_FIXTURE = "tests/fixtures/material_router_sample.pdf"


def run(cmd: list[str], cwd: Path = REPO_ROOT) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=ENV,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def check(condition: bool, name: str, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}")
    if detail:
        print(f"         {detail}")
    return condition


def load_router_module():
    spec = importlib.util.spec_from_file_location("material_to_kb", ROUTER_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load material_to_kb.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def metadata_count() -> int:
    return len(list((REPO_ROOT / "content").glob("**/metadata.yaml")))


def parse_router_stdout(stdout: str) -> dict:
    try:
        return json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"router stdout was not JSON: {exc}\n{stdout[:500]}") from exc


def item_by_input(items: list[dict], value: str) -> dict:
    for item in items:
        if item.get("input") == value:
            return item
    raise AssertionError(f"missing item for input: {value}")


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:  # noqa: A003 - stdlib signature
        return


def start_fixture_server():
    handler = partial(QuietHandler, directory=str(WEB_FIXTURE_DIR))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/{WEB_FIXTURE_NAME}"


def smoke_1_inference_rules() -> bool:
    """Direct inference covers supported and unsupported material types."""
    print("\n=== Smoke 1: inference rules ===")
    module = load_router_module()
    cases = [
        ("https://mp.weixin.qq.com/s/example", "wechat_url", True),
        (HTML_FIXTURE, "local_text_article", True),
        (MD_FIXTURE, "local_text_article", True),
        (GENERIC_URL, "generic_web_url", True),
        (YOUTUBE_URL, "youtube_url", False),
        (PDF_FIXTURE, "pdf_file", False),
    ]
    ok = True
    for idx, (value, expected_type, supported) in enumerate(cases):
        item = module.infer_input(value, index=idx)
        ok &= check(item["inferred_type"] == expected_type,
                    f"{value} inferred as {expected_type}",
                    f"got {item['inferred_type']}")
        ok &= check(item["supported"] is supported,
                    f"{value} supported={supported}",
                    f"got {item['supported']}")
    return ok


def smoke_2_input_list_and_reports() -> bool:
    """Mixed dry-run produces a complete report and keeps KB count unchanged."""
    print("\n=== Smoke 2: mixed input-list dry-run ===")
    server, web_url = start_fixture_server()
    try:
        with tempfile.TemporaryDirectory(prefix=".material-router-smoke-", dir=REPO_ROOT) as tmp:
            input_list = Path(tmp) / "materials.txt"
            input_list.write_text(
                "\n".join([
                    "# comments are skipped",
                    "",
                    HTML_FIXTURE,
                    MD_FIXTURE,
                    web_url,
                    YOUTUBE_URL,
                    PDF_FIXTURE,
                    "",
                ]),
                encoding="utf-8",
            )
            before = metadata_count()
            code, out, err = run([TEST_PY, str(ROUTER_SCRIPT), "--input-list", str(input_list), "--dry-run"])
            after = metadata_count()
    finally:
        server.shutdown()
        server.server_close()

    if not check(code == 0, "router exits 0", f"exit={code}\nstderr tail: {err[-300:]}"):
        return False
    data = parse_router_stdout(out)
    items = data.get("items", [])
    summary = data.get("summary", {})

    ok = check(summary.get("total") == 5, "input-list skips blanks/comments", str(summary))
    ok &= check(len(items) == 5, "all five material inputs reported", f"got {len(items)}")
    ok &= check(before == after, "dry-run does not change metadata count", f"before={before}, after={after}")

    html_item = item_by_input(items, HTML_FIXTURE)
    md_item = item_by_input(items, MD_FIXTURE)
    yt_item = item_by_input(items, YOUTUBE_URL)
    web_item = item_by_input(items, web_url)
    pdf_item = item_by_input(items, PDF_FIXTURE)

    ok &= check(html_item["inferred_type"] == "local_text_article",
                "local HTML inferred as local_text_article")
    ok &= check(md_item["inferred_type"] == "local_text_article",
                "local Markdown inferred as local_text_article")
    ok &= check(html_item["status"] in {"DRY_RUN_OK", "SKIPPED_DUPLICATE"},
                "local HTML dry-run completed", html_item["status"])
    ok &= check(md_item["status"] in {"DRY_RUN_OK", "SKIPPED_DUPLICATE"},
                "local Markdown dry-run completed", md_item["status"])

    ok &= check(web_item["inferred_type"] == "generic_web_url",
                "generic web inferred as generic_web_url")
    ok &= check(web_item["route"] == "web_article_to_kb.py",
                "generic web routed to web_article_to_kb.py", web_item["route"])
    ok &= check(web_item["status"] in {"DRY_RUN_OK", "SKIPPED_DUPLICATE"},
                "generic web dry-run completed", web_item["status"])

    ok &= check(yt_item["status"] == "BLOCKED_UNSUPPORTED",
                "YouTube returns BLOCKED_UNSUPPORTED", yt_item.get("failure_reason", ""))
    ok &= check("YouTube import route not implemented yet" in yt_item.get("failure_reason", ""),
                "YouTube unsupported reason is explicit")
    ok &= check(pdf_item["status"] == "BLOCKED_UNSUPPORTED",
                "PDF returns BLOCKED_UNSUPPORTED", pdf_item.get("failure_reason", ""))
    ok &= check("PDF import/OCR route not implemented yet" in pdf_item.get("failure_reason", ""),
                "PDF unsupported reason is explicit")

    ok &= check(summary.get("blocked_unsupported") == 2,
                "unsupported items counted without aborting batch", str(summary))
    ok &= check(summary.get("dry_run_ok", 0) + summary.get("skipped_duplicate", 0) == 3,
                "supported dry-run items counted", str(summary))

    md_report = REPO_ROOT / data.get("report_markdown", "")
    json_report = REPO_ROOT / data.get("report_json", "")
    ok &= check(md_report.exists(), "markdown report generated", str(md_report))
    ok &= check(json_report.exists(), "json report generated", str(json_report))
    if json_report.exists():
        report_data = json.loads(json_report.read_text(encoding="utf-8"))
        ok &= check(report_data.get("summary", {}).get("total") == 5,
                    "json report has summary total=5")
    if md_report.exists():
        text = md_report.read_text(encoding="utf-8")
        ok &= check("BLOCKED_UNSUPPORTED" in text and "web_article_to_kb.py" in text,
                    "markdown report includes statuses and inferred types")
    return ok


def smoke_3_single_input_dry_run_report() -> bool:
    """Single local input uses the single-file route and emits a report."""
    print("\n=== Smoke 3: single local input dry-run ===")
    before = metadata_count()
    code, out, err = run([TEST_PY, str(ROUTER_SCRIPT), "--input", HTML_FIXTURE, "--dry-run"])
    after = metadata_count()
    if not check(code == 0, "single input router exits 0", f"exit={code}\nstderr tail: {err[-300:]}"):
        return False
    data = parse_router_stdout(out)
    items = data.get("items", [])
    if not check(len(items) == 1, "single run has one item", f"got {len(items)}"):
        return False
    item = items[0]
    ok = check(item["route"] == "wechat_url_to_kb.py local file mode",
               "single local file uses wechat_url_to_kb.py local route",
               item["route"])
    ok &= check(item["status"] in {"DRY_RUN_OK", "SKIPPED_DUPLICATE"},
                "single local file dry-run completed", item["status"])
    ok &= check(before == after, "single dry-run does not change metadata count",
                f"before={before}, after={after}")
    ok &= check(Path(REPO_ROOT / data.get("report_markdown", "")).exists(),
                "single run markdown report generated")
    ok &= check(Path(REPO_ROOT / data.get("report_json", "")).exists(),
                "single run json report generated")
    return ok


def smoke_4_no_remote_mmbiz_in_generated_html() -> bool:
    """Existing published HTML remains free of remote WeChat image URLs."""
    print("\n=== Smoke 4: generated HTML has no remote mmbiz ===")
    bad: list[str] = []
    for html_file in (REPO_ROOT / "site" / "items").glob("*/index.html"):
        text = html_file.read_text(encoding="utf-8")
        if re.search(r"mmbiz\.qpic\.cn", text):
            bad.append(str(html_file.relative_to(REPO_ROOT)))
    return check(len(bad) == 0, "site item HTML has no mmbiz.qpic.cn", ", ".join(bad[:5]) if bad else "")


def main() -> int:
    print("=" * 60)
    print("Material import router smoke tests (v0.3.76/v0.3.77)")
    print("=" * 60)
    results = [
        smoke_1_inference_rules(),
        smoke_2_input_list_and_reports(),
        smoke_3_single_input_dry_run_report(),
        smoke_4_no_remote_mmbiz_in_generated_html(),
    ]
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL MATERIAL ROUTER SMOKE TESTS PASSED ({passed}/{total})")
        return 0
    print(f"MATERIAL ROUTER SMOKE TESTS FAILED ({passed}/{total})")
    return 1


if __name__ == "__main__":
    sys.exit(main())
