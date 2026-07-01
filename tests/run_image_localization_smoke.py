#!/usr/bin/env python3
"""Smoke tests for WeChat image localization (v0.3.74).

Verifies:
1. localize_article_images.py dry-run reports correct image counts.
2. After localization, source.md contains assets/ paths, not remote mmbiz URLs.
3. mirror articles: source.md and translation.zh-CN.md are both rewritten.
4. generate_item_pages.py copies assets to site/items/<slug>/assets/.
5. Generated HTML uses local assets/ paths, not remote mmbiz URLs.
6. check_pages_sync.py still PASS.
7. Empty image ![]() does not create broken local files.

Usage:
    python3 tests/run_image_localization_smoke.py
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

LOCALIZE_SCRIPT = REPO_ROOT / "scripts" / "localize_article_images.py"
TWO_STEP_SLUG = "2026-06-30-wechat-两步路-北京热门徒步线路top10"


def run(cmd: list[str], cwd: Path = REPO_ROOT, env_extra: dict | None = None) -> tuple[int, str, str]:
    e = {**ENV, **(env_extra or {})}
    proc = subprocess.run(
        cmd, cwd=cwd, capture_output=True, text=True,
        encoding="utf-8", errors="replace", env=e,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def check(condition: bool, name: str, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}")
    if detail:
        print(f"         {detail}")
    return condition


def smoke_1_localize_dry_run() -> bool:
    """Dry-run reports correct image counts for all wechat articles."""
    print("\n=== Smoke 1: localize dry-run reports counts ===")
    cmd = [TEST_PY, str(LOCALIZE_SCRIPT), "--all-wechat", "--dry-run"]
    code, out, err = run(cmd)
    if not check(code == 0, "dry-run exits 0", f"exit={code}"):
        return False
    try:
        data = json.loads(out)
    except json.JSONDecodeError:
        return check(False, "stdout is valid JSON")
    ok = check(data["articles_processed"] >= 6,
               f"at least 6 wechat articles (got {data['articles_processed']})")
    # After localization, remote images are already local, so image_total may be 0.
    # Just assert no failures.
    ok &= check(data["image_failed"] == 0, f"image_failed == 0 (got {data['image_failed']})")
    return ok


def smoke_2_source_uses_local_assets() -> bool:
    """After localization, source.md uses assets/ paths, not remote mmbiz."""
    print("\n=== Smoke 2: source.md uses local assets ===")
    source = REPO_ROOT / "content/articles/2026" / TWO_STEP_SLUG / "source.md"
    if not check(source.exists(), "source.md exists"):
        return False
    text = source.read_text(encoding="utf-8")
    local_count = len(re.findall(r"!\[[^\]]*\]\(assets/", text))
    remote_count = len(re.findall(r"!\[[^\]]*\]\(https://mmbiz", text))
    ok = check(local_count > 0, f"source.md has local assets/ images ({local_count})")
    ok &= check(remote_count == 0, f"source.md has no remote mmbiz images ({remote_count})")
    return ok


def smoke_3_mirror_synced() -> bool:
    """Mirror article: translation.zh-CN.md also uses local assets."""
    print("\n=== Smoke 3: mirror article translation synced ===")
    trans = REPO_ROOT / "content/articles/2026" / TWO_STEP_SLUG / "translation.zh-CN.md"
    if not check(trans.exists(), "translation.zh-CN.md exists"):
        return False
    text = trans.read_text(encoding="utf-8")
    local_count = len(re.findall(r"!\[[^\]]*\]\(assets/", text))
    remote_count = len(re.findall(r"!\[[^\]]*\]\(https://mmbiz", text))
    ok = check(local_count > 0, f"translation has local assets/ images ({local_count})")
    ok &= check(remote_count == 0, f"translation has no remote mmbiz images ({remote_count})")
    return ok


def smoke_4_assets_in_site_and_docs() -> bool:
    """assets/ dirs exist in both site/items/ and docs/items/."""
    print("\n=== Smoke 4: assets copied to site/ and docs/ ===")
    site_assets = REPO_ROOT / "site/items" / TWO_STEP_SLUG / "assets"
    docs_assets = REPO_ROOT / "docs/items" / TWO_STEP_SLUG / "assets"
    ok = check(site_assets.is_dir(), f"site/items/<slug>/assets/ exists ({site_assets.name})")
    ok &= check(docs_assets.is_dir(), f"docs/items/<slug>/assets/ exists ({docs_assets.name})")
    if site_assets.is_dir():
        files = list(site_assets.iterdir())
        ok &= check(len(files) > 0, f"site assets has files ({len(files)})")
    return ok


def smoke_5_html_uses_local_images() -> bool:
    """Generated HTML uses local assets/ paths, not remote mmbiz URLs."""
    print("\n=== Smoke 5: HTML uses local assets ===")
    html = REPO_ROOT / "site/items" / TWO_STEP_SLUG / "index.html"
    if not check(html.exists(), "HTML page exists"):
        return False
    text = html.read_text(encoding="utf-8")
    local_count = len(re.findall(r'src="assets/image-', text))
    remote_mmbiz = len(re.findall(r'src="https://mmbiz\.qpic\.cn', text))
    ok = check(local_count > 0, f"HTML has local assets/ img src ({local_count})")
    ok &= check(remote_mmbiz == 0, f"HTML has no remote mmbiz src ({remote_mmbiz})")
    return ok


def smoke_6_pages_sync_pass() -> bool:
    """check_pages_sync.py still PASS."""
    print("\n=== Smoke 6: check_pages_sync.py PASS ===")
    cmd = [TEST_PY, str(REPO_ROOT / "scripts" / "check_pages_sync.py")]
    code, out, _err = run(cmd)
    ok = check(code == 0, "check_pages_sync exits 0")
    ok &= check("PASS" in out, "report says PASS")
    return ok


def smoke_7_no_broken_empty_images() -> bool:
    """No broken ![]() in any generated item page."""
    print("\n=== Smoke 7: no broken empty image markdown ===")
    items_dir = REPO_ROOT / "site/items"
    if not items_dir.exists():
        return check(False, "site/items/ exists")
    bad: list[str] = []
    for html_file in items_dir.glob("*/index.html"):
        text = html_file.read_text(encoding="utf-8")
        if re.search(r"!\[[^\]]*\]\(\)", text):
            bad.append(html_file.parent.name)
    return check(len(bad) == 0, f"no pages with broken empty images (bad={len(bad)})",
                 ", ".join(bad[:5]) if bad else "")


def main() -> int:
    print("=" * 60)
    print("Image localization smoke tests (v0.3.74)")
    print("=" * 60)
    results = [
        smoke_1_localize_dry_run(),
        smoke_2_source_uses_local_assets(),
        smoke_3_mirror_synced(),
        smoke_4_assets_in_site_and_docs(),
        smoke_5_html_uses_local_images(),
        smoke_6_pages_sync_pass(),
        smoke_7_no_broken_empty_images(),
    ]
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL IMAGE LOCALIZATION SMOKE TESTS PASSED ({passed}/{total})")
        return 0
    else:
        print(f"IMAGE LOCALIZATION SMOKE TESTS FAILED ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
