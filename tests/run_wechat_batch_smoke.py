#!/usr/bin/env python3
"""Smoke tests for WeChat batch import (v0.3.71).

Runs offline (no network) against synthetic fixtures under tests/fixtures/.
Verifies:

1. batch --input with multiple local fixtures processes each one.
2. duplicate input is detected and marked DRY_RUN_DUPLICATE / SKIPPED_DUPLICATE.
3. an image URL containing /AI/ in the hiking fixture does NOT cause the
   article to be tagged 人工智能/AI (regression guard for v0.3.70 fix).
4. a missing local file in the input list is BLOCKED_FETCH_FAILED and does
   NOT crash the whole batch (failure isolation).
5. check_pages_sync.py still reports 55 slugs (no item pages lost).

Usage:
    python3 tests/run_wechat_batch_smoke.py

Exit codes:
    0 - all smoke checks passed
    1 - at least one smoke check failed
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

BATCH_SCRIPT = REPO_ROOT / "scripts" / "wechat_batch_import.py"
BATCH_URLS = REPO_ROOT / "tests" / "fixtures" / "wechat_batch_urls.txt"
BATCH_DUP = REPO_ROOT / "tests" / "fixtures" / "wechat_batch_duplicate_urls.txt"
BATCH_FAIL = REPO_ROOT / "tests" / "fixtures" / "wechat_batch_failure_isolation.txt"
HIKING_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "wechat_sample_hiking_article.html"


def run(cmd: list[str], cwd: Path = REPO_ROOT) -> tuple[int, str, str]:
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


def _find_latest_manifest(prefix: str = "wechat_batch_import_") -> Path | None:
    """Return the most recent manifest JSON under reports/ matching the prefix."""
    reports = REPO_ROOT / "reports"
    if not reports.exists():
        return None
    files = sorted(reports.glob(f"{prefix}*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def smoke_1_batch_multi_local_fixtures() -> bool:
    """Batch --input with two local fixtures -> both DRY_RUN_OK (or DUPLICATE)."""
    print("\n=== Smoke 1: batch --input multiple local fixtures (dry-run) ===")
    if not BATCH_URLS.exists():
        return check(False, "fixture exists", str(BATCH_URLS))
    cmd = [TEST_PY, str(BATCH_SCRIPT), "--input", str(BATCH_URLS), "--dry-run"]
    code, out, err = run(cmd)
    if not check(code == 0, "batch exits 0", f"exit={code}\nstderr tail: {err[-300:]}"):
        return False
    manifest = _find_latest_manifest()
    if not check(manifest is not None and manifest.exists(), "manifest JSON written"):
        return False
    data = json.loads(manifest.read_text(encoding="utf-8"))  # type: ignore
    items = data.get("items", [])
    if not check(len(items) == 2, "manifest has 2 items", f"got {len(items)}"):
        return False
    # Both should be DRY_RUN_OK (fixtures are synthetic, not in KB).
    ok_statuses = {"DRY_RUN_OK", "DRY_RUN_DUPLICATE"}
    ok = all(it["status"] in ok_statuses for it in items)
    return check(ok, "all items DRY_RUN_OK or DRY_RUN_DUPLICATE",
                 str([it["status"] for it in items]))


def smoke_2_duplicate_detection() -> bool:
    """Same fixture twice -> second one is DRY_RUN_DUPLICATE."""
    print("\n=== Smoke 2: duplicate detection (Layer 3 content hash) ===")
    if not BATCH_DUP.exists():
        return check(False, "fixture exists", str(BATCH_DUP))
    cmd = [TEST_PY, str(BATCH_SCRIPT), "--input", str(BATCH_DUP), "--dry-run"]
    code, out, err = run(cmd)
    if not check(code == 0, "batch exits 0", f"exit={code}\n{err[-300:]}"):
        return False
    manifest = _find_latest_manifest()
    data = json.loads(manifest.read_text(encoding="utf-8"))  # type: ignore
    items = data.get("items", [])
    if not check(len(items) == 2, "manifest has 2 items", f"got {len(items)}"):
        return False
    # The second item must be a duplicate of the first.
    second = items[1]
    ok = check(second["status"] == "DRY_RUN_DUPLICATE",
               "second item is DRY_RUN_DUPLICATE",
               f"got {second['status']}")
    ok &= check(bool(second.get("duplicate_of")),
                "duplicate_of is populated",
                str(second.get("duplicate_of")))
    return ok


def smoke_3_ai_url_trap_regression() -> bool:
    """Hiking fixture with /AI/ in image URLs must NOT be tagged 人工智能/AI."""
    print("\n=== Smoke 3: /AI/ URL trap regression guard ===")
    if not HIKING_FIXTURE.exists():
        return check(False, "hiking fixture exists")
    # Run a single-input batch on the hiking fixture.
    cmd = [TEST_PY, str(BATCH_SCRIPT), "--html-file", str(HIKING_FIXTURE), "--dry-run"]
    code, out, err = run(cmd)
    if not check(code == 0, "batch exits 0", f"exit={code}\n{err[-300:]}"):
        return False
    manifest = _find_latest_manifest()
    data = json.loads(manifest.read_text(encoding="utf-8"))  # type: ignore
    items = data.get("items", [])
    if not check(len(items) == 1, "manifest has 1 item"):
        return False
    # Now directly invoke the import script's infer functions on the capture
    # (the batch manifest doesn't carry topics/tags, so we assert via the
    # import script's helpers).
    cap_path = items[0].get("capture_json_path", "")
    if not cap_path:
        return check(False, "capture_json_path populated")
    full_cap = REPO_ROOT / cap_path if not Path(cap_path).is_absolute() else Path(cap_path)
    if not check(full_cap.exists(), "capture JSON exists on disk", str(full_cap)):
        return False
    cap = json.loads(full_cap.read_text(encoding="utf-8"))
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    import import_wechat_article_capture as m  # type: ignore
    topics = m.infer_topics(cap.get("content_markdown", ""), cap.get("title", ""))
    tags = m.infer_tags(cap.get("content_markdown", ""), cap.get("title", ""), cap.get("account_name", ""))
    ok = check("人工智能" not in topics, "topics does not contain 人工智能", str(topics))
    ok &= check("AI" not in tags, "tags does not contain AI", str(tags))
    ok &= check(any(t in topics for t in ("户外", "徒步", "自然地理")),
                "topics contains an outdoor domain", str(topics))
    return ok


def smoke_4_failure_isolation() -> bool:
    """A missing local file in the middle of the batch must NOT crash it."""
    print("\n=== Smoke 4: failure isolation (missing file mid-batch) ===")
    if not BATCH_FAIL.exists():
        return check(False, "fixture exists", str(BATCH_FAIL))
    cmd = [TEST_PY, str(BATCH_SCRIPT), "--input", str(BATCH_FAIL), "--dry-run"]
    code, out, err = run(cmd)
    if not check(code == 0, "batch exits 0 (did not crash)", f"exit={code}\n{err[-300:]}"):
        return False
    manifest = _find_latest_manifest()
    data = json.loads(manifest.read_text(encoding="utf-8"))  # type: ignore
    items = data.get("items", [])
    if not check(len(items) == 3, "manifest has 3 items", f"got {len(items)}"):
        return False
    statuses = [it["status"] for it in items]
    # Item 1 (hiking) and item 3 (sample) must be OK; item 2 (missing) must be BLOCKED.
    ok = check(statuses[1] == "BLOCKED_FETCH_FAILED",
               "middle item is BLOCKED_FETCH_FAILED", str(statuses))
    ok &= check(statuses[0] in {"DRY_RUN_OK", "DRY_RUN_DUPLICATE"},
                "first item is OK", str(statuses))
    ok &= check(statuses[2] in {"DRY_RUN_OK", "DRY_RUN_DUPLICATE"},
                "third item is OK", str(statuses))
    return ok


def smoke_5_pages_sync_still_intact() -> bool:
    """check_pages_sync.py still passes and item pages are not lost.

    v0.3.88: dropped the `site == docs == content` equality assertion.

    Background: previous versions required site, docs and content counts to be
    equal. That assertion was over-strict — it produced a false positive every
    time `scripts/pdf_to_kb.py` smoke_4 ran, because that smoke creates an
    article directory in `content/articles/2026/...` and runs an incremental
    `update_site.py --only <slug>` which generates `site/items/<slug>/` and
    `docs/items/<slug>/`. The article directory is then left in place between
    PDF smoke runs (only deduplicated on re-run), so the triple-count equality
    was unreliable.

    check_pages_sync.py is already the canonical sync integrity check; it
    enforces site==docs, top-level byte-equality, and the content->items
    coverage rule. When that script says PASS, the publish surface and dev
    surface are consistent, and every content/ entry has an item page.

    This smoke now asserts:
      (a) check_pages_sync.py exits 0,
      (b) site slugs == docs slugs (real sync guarantee),
      (c) site slugs >= 55 (v0.3.70 baseline; no item pages silently lost),
      (d) content slugs <= site slugs (every content entry has an item page).

    A genuine regression (e.g. batch dry-run nuking a site/items/<slug>) will
    still trip check_pages_sync.py (via site != docs) and fail this smoke.
    """
    print("\n=== Smoke 5: check_pages_sync.py content/items intact ===")
    cmd = [TEST_PY, str(REPO_ROOT / "scripts" / "check_pages_sync.py")]
    code, out, _err = run(cmd)
    if not check(code == 0, "check_pages_sync.py exits 0", f"exit={code}"):
        return False
    import re
    m = re.search(r"site slugs:\s*(\d+)", out)
    site_n = int(m.group(1)) if m else -1
    m2 = re.search(r"docs slugs:\s*(\d+)", out)
    docs_n = int(m2.group(1)) if m2 else -1
    m3 = re.search(r"metadata\.yaml count:\s*(\d+)", out)
    content_n = int(m3.group(1)) if m3 else -1
    ok = check(site_n == docs_n,
               f"site({site_n}) == docs({docs_n}) (publish/dev sync)")
    ok &= check(site_n >= 55, f"site slugs >= 55 (got {site_n})")
    ok &= check(content_n <= site_n,
                f"content({content_n}) <= site({site_n}) (every content entry has an item page)")
    ok &= check("PASS" in out, "report says PASS")
    return ok


def main() -> int:
    print("=" * 60)
    print("WeChat batch import smoke tests (v0.3.71)")
    print("=" * 60)
    results = [
        smoke_1_batch_multi_local_fixtures(),
        smoke_2_duplicate_detection(),
        smoke_3_ai_url_trap_regression(),
        smoke_4_failure_isolation(),
        smoke_5_pages_sync_still_intact(),
    ]
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL BATCH SMOKE TESTS PASSED ({passed}/{total})")
        return 0
    else:
        print(f"BATCH SMOKE TESTS FAILED ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
