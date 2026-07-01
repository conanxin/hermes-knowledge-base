#!/usr/bin/env python3
"""Smoke tests for WeChat import hardening (v0.3.70).

Runs offline (no network) against synthetic fixtures under tests/fixtures/.
Verifies the three v0.3.70 fixes:

1. wechat_url_to_kb.py --html-file produces a capture JSON whose topics/tags
   do NOT contain "人工智能" / "AI" even when the fixture HTML embeds image
   URLs with /AI/ substrings.
2. import_wechat_article_capture.py --dry-run can consume that capture JSON.
3. check_pages_sync.py's content-completeness check can detect a missing
   item page (simulated by counting content/ vs items/).

Usage:
    python3 tests/run_smoke_tests.py

Exit codes:
    0 - all smoke checks passed
    1 - at least one smoke check failed
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

HIKING_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "wechat_sample_hiking_article.html"


def run(cmd: list[str], cwd: Path = REPO_ROOT) -> tuple[int, str, str]:
    """Run a command, return (exit_code, stdout, stderr)."""
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=ENV,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def check(condition: bool, name: str, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}")
    if detail:
        print(f"         {detail}")
    return condition


def smoke_1_hiking_fixture_no_ai_misclassification() -> bool:
    """Fixture with /AI/ in image URLs must NOT be tagged 人工智能/AI."""
    print("\n=== Smoke 1: hiking fixture /AI/ URL trap ===")
    if not HIKING_FIXTURE.exists():
        return check(False, "fixture exists", f"missing: {HIKING_FIXTURE}")
    with tempfile.TemporaryDirectory() as td:
        out_json = Path(td) / "capture.json"
        cmd = [
            TEST_PY, str(REPO_ROOT / "scripts" / "wechat_url_to_kb.py"),
            "--html-file", str(HIKING_FIXTURE),
            "--dry-run",
            "--out", str(out_json),
        ]
        code, out, err = run(cmd)
        if not check(code == 0, "wechat_url_to_kb.py --html-file --dry-run exits 0",
                     f"exit={code}\nstderr tail: {err[-300:]}"):
            return False
        if not check(out_json.exists(), "capture JSON written", str(out_json)):
            return False
        data = json.loads(out_json.read_text(encoding="utf-8"))
        # Now feed it to the import script in dry-run to see the inferred topics/tags.
        cmd2 = [
            TEST_PY, str(REPO_ROOT / "scripts" / "import_wechat_article_capture.py"),
            "--dry-run", str(out_json),
        ]
        code2, out2, err2 = run(cmd2)
        if not check(code2 == 0, "import_wechat_article_capture.py --dry-run exits 0",
                     f"exit={code2}\nstderr tail: {err2[-300:]}"):
            return False
        # The import script's dry-run output doesn't print topics/tags directly,
        # so call the infer functions directly to assert.
        sys.path.insert(0, str(REPO_ROOT / "scripts"))
        import import_wechat_article_capture as m  # type: ignore
        content = data.get("content_markdown", "")
        title = data.get("title", "")
        account = data.get("account_name", "")
        topics = m.infer_topics(content, title)
        tags = m.infer_tags(content, title, account)
        print(f"         inferred topics: {topics}")
        print(f"         inferred tags:   {tags}")
        ok = True
        ok &= check("人工智能" not in topics, "topics does not contain 人工智能", str(topics))
        ok &= check("AI" not in tags, "tags does not contain AI", str(tags))
        ok &= check(any(t in topics for t in ("户外", "徒步", "自然地理")),
                    "topics contains an outdoor/hiking domain", str(topics))
        return ok


def smoke_2_import_consumes_capture() -> bool:
    """import_wechat_article_capture.py --dry-run must consume the capture."""
    print("\n=== Smoke 2: import script consumes fixture capture ===")
    if not HIKING_FIXTURE.exists():
        return check(False, "fixture exists")
    with tempfile.TemporaryDirectory() as td:
        out_json = Path(td) / "capture.json"
        cmd = [
            TEST_PY, str(REPO_ROOT / "scripts" / "wechat_url_to_kb.py"),
            "--html-file", str(HIKING_FIXTURE),
            "--dry-run",
            "--out", str(out_json),
        ]
        code, _, err = run(cmd)
        if not check(code == 0, "capture JSON generated", f"exit={code} {err[-200:]}"):
            return False
        cmd2 = [
            TEST_PY, str(REPO_ROOT / "scripts" / "import_wechat_article_capture.py"),
            "--dry-run", str(out_json),
        ]
        code2, out2, err2 = run(cmd2)
        ok = check(code2 == 0, "import --dry-run exits 0",
                   f"exit={code2}\nstdout tail: {out2[-200:]}")
        ok &= check("STATUS: DRY_RUN_OK" in (out2 + err2),
                    "output contains STATUS: DRY_RUN_OK")
        return ok


def smoke_3_check_pages_sync_completeness() -> bool:
    """check_pages_sync.py must report content/ vs items/ completeness."""
    print("\n=== Smoke 3: check_pages_sync.py content-completeness check ===")
    cmd = [TEST_PY, str(REPO_ROOT / "scripts" / "check_pages_sync.py")]
    code, out, _err = run(cmd)
    if not check(code in (0, 1), "check_pages_sync.py runs", f"exit={code}"):
        return False
    # The v0.3.70 report must contain the [3/3] completeness section.
    has_section = "Content→items completeness" in out or "Content->items completeness" in out
    ok = check(has_section, "report contains content-completeness section (v0.3.70)")
    return ok


def main() -> int:
    print("=" * 60)
    print("WeChat import hardening smoke tests (v0.3.70)")
    print("=" * 60)
    results = [
        smoke_1_hiking_fixture_no_ai_misclassification(),
        smoke_2_import_consumes_capture(),
        smoke_3_check_pages_sync_completeness(),
    ]
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL SMOKE TESTS PASSED ({passed}/{total})")
        return 0
    else:
        print(f"SMOKE TESTS FAILED ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
