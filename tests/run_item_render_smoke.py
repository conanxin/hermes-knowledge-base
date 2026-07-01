#!/usr/bin/env python3
"""Smoke tests for item page rendering fixes (v0.3.72).

Verifies:
1. Chinese-mirror article: "中文翻译" section suppressed, "正文 / 中文原文" shown.
2. English article: both "中文翻译" and "原文 / 源文本" sections still present.
3. Markdown images render as <img>, not raw ![](url) text.
4. No raw markdown image links in the generated HTML.
5. 两步路 article page: no raw mmbiz.qpic.cn markdown links.
6. check_pages_sync.py still PASS.

Usage:
    python3 tests/run_item_render_smoke.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

SITE_ITEMS = REPO_ROOT / "site" / "items"
TWO_STEP_SLUG = "2026-06-30-wechat-两步路-北京热门徒步线路top10"
ENGLISH_SLUG = "2026-06-22-paulgraham-superlinear-returns"


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


def _read_page(slug: str) -> str:
    p = SITE_ITEMS / slug / "index.html"
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8")


def smoke_1_chinese_mirror_no_duplicate_translation() -> bool:
    """Chinese-mirror article should NOT show '中文翻译' and SHOULD show '正文 / 中文原文'."""
    print("\n=== Smoke 1: Chinese-mirror article — no duplicate translation ===")
    page = _read_page(TWO_STEP_SLUG)
    if not check(bool(page), "two-step page exists"):
        return False
    ok = check("中文翻译" not in page, "page does NOT contain '中文翻译'")
    ok &= check("正文 / 中文原文" in page, "page contains '正文 / 中文原文'")
    return ok


def smoke_2_english_article_keeps_both_sections() -> bool:
    """English article should still show both '中文翻译' and '原文 / 源文本'."""
    print("\n=== Smoke 2: English article — both sections preserved ===")
    page = _read_page(ENGLISH_SLUG)
    if not check(bool(page), "English article page exists"):
        return False
    ok = check("中文翻译" in page, "page contains '中文翻译'")
    ok &= check("原文 / 源文本" in page, "page contains '原文 / 源文本'")
    return ok


def smoke_3_images_render_as_img_tags() -> bool:
    """Markdown images should render as <img> tags in the two-step page."""
    print("\n=== Smoke 3: images render as <img> tags ===")
    page = _read_page(TWO_STEP_SLUG)
    if not check(bool(page), "page exists"):
        return False
    img_count = page.count("<img ")
    ok = check(img_count > 0, f"page has <img> tags (count={img_count})")
    return ok


def smoke_4_no_raw_markdown_image_links() -> bool:
    """No raw ![](url) markdown should appear in any generated HTML."""
    print("\n=== Smoke 4: no raw markdown image links in any item page ===")
    if not SITE_ITEMS.exists():
        return check(False, "site/items/ exists")
    bad: list[str] = []
    for html_file in SITE_ITEMS.glob("*/index.html"):
        text = html_file.read_text(encoding="utf-8")
        # Look for the markdown image pattern that was NOT converted.
        # We check for "![(" which is the signature of unrendered image markdown.
        # (The HTML-escaped version would be "![(" too since ! [ ( are not escaped.)
        if "![" in text and "](" in text:
            # More precise: look for ![...](  pattern
            import re
            if re.search(r"!\[[^\]]*\]\(", text):
                bad.append(html_file.parent.name)
    return check(len(bad) == 0, f"no pages with raw markdown images (bad={len(bad)})",
                 ", ".join(bad[:5]) if bad else "")


def smoke_5_two_step_no_raw_mmbiz() -> bool:
    """Two-step page should NOT have raw mmbiz.qpic.cn markdown links."""
    print("\n=== Smoke 5: two-step page — no raw mmbiz markdown ===")
    page = _read_page(TWO_STEP_SLUG)
    if not check(bool(page), "page exists"):
        return False
    import re
    # Look for ![...](https://mmbiz...  — unrendered image markdown
    raw_mmbiz = re.search(r"!\[[^\]]*\]\(https://mmbiz", page)
    return check(raw_mmbiz is None, "no raw mmbiz markdown image links")


def smoke_6_pages_sync_pass() -> bool:
    """check_pages_sync.py still PASS."""
    print("\n=== Smoke 6: check_pages_sync.py PASS ===")
    cmd = [TEST_PY, str(REPO_ROOT / "scripts" / "check_pages_sync.py")]
    code, out, _err = run(cmd)
    ok = check(code == 0, "check_pages_sync exits 0")
    ok &= check("PASS" in out, "report says PASS")
    return ok


def main() -> int:
    print("=" * 60)
    print("Item page rendering smoke tests (v0.3.72)")
    print("=" * 60)
    results = [
        smoke_1_chinese_mirror_no_duplicate_translation(),
        smoke_2_english_article_keeps_both_sections(),
        smoke_3_images_render_as_img_tags(),
        smoke_4_no_raw_markdown_image_links(),
        smoke_5_two_step_no_raw_mmbiz(),
        smoke_6_pages_sync_pass(),
    ]
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"ALL RENDER SMOKE TESTS PASSED ({passed}/{total})")
        return 0
    else:
        print(f"RENDER SMOKE TESTS FAILED ({passed}/{total} passed)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
