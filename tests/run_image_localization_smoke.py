#!/usr/bin/env python3
"""Smoke tests for WeChat image localization (v0.3.75).

Verifies:
1. localize_article_images.py dry-run reports per-file image counts.
2. After localization, source.md contains assets/ paths, not remote mmbiz URLs.
3. mirror articles: source.md and translation.zh-CN.md are both rewritten.
4. generate_item_pages.py copies assets to site/items/<slug>/assets/.
5. Generated HTML uses local assets/ paths, not remote mmbiz URLs.
6. check_pages_sync.py still PASS.
7. Empty image ![]() does not create broken local files.
8. summary.md and notes.md remote images are localized.

Usage:
    python3 tests/run_image_localization_smoke.py
"""

from __future__ import annotations

import json
import importlib.util
import os
import re
import subprocess
import sys
import tempfile
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


def load_localizer_module():
    spec = importlib.util.spec_from_file_location("localize_article_images", LOCALIZE_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load localize_article_images.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def smoke_1_localize_dry_run() -> bool:
    """Dry-run reports per-file image counts for all wechat articles."""
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
    file_entries = [
        file_entry["file"]
        for article in data.get("articles", [])
        for file_entry in article.get("markdown_files", [])
    ]
    ok &= check("summary.md" in file_entries, "dry-run includes summary.md file results")
    ok &= check("notes.md" in file_entries, "dry-run includes notes.md file results")
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
    print("\n=== Smoke 5: generated HTML has no remote mmbiz ===")
    html = REPO_ROOT / "site/items" / TWO_STEP_SLUG / "index.html"
    if not check(html.exists(), "HTML page exists"):
        return False
    text = html.read_text(encoding="utf-8")
    local_count = len(re.findall(r'src="assets/image-', text))
    remote_mmbiz = len(re.findall(r"mmbiz\.qpic\.cn", text))
    ok = check(local_count > 0, f"HTML has local assets/ img src ({local_count})")
    ok &= check(remote_mmbiz == 0, f"sample HTML has no remote mmbiz ({remote_mmbiz})")

    bad: list[str] = []
    for root in [REPO_ROOT / "site/items", REPO_ROOT / "docs/items"]:
        for html_file in root.glob("*/index.html"):
            if "mmbiz.qpic.cn" in html_file.read_text(encoding="utf-8"):
                bad.append(str(html_file.relative_to(REPO_ROOT)))
    ok &= check(len(bad) == 0, f"all generated item HTML has no remote mmbiz (bad={len(bad)})",
                ", ".join(bad[:5]) if bad else "")
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


def smoke_8_temp_article_all_public_markdown_files() -> bool:
    """summary.md/notes.md are localized; assets and empty images are ignored."""
    print("\n=== Smoke 8: temp article localizes all public markdown files ===")
    module = load_localizer_module()
    calls: list[str] = []

    def fake_download(url: str):
        calls.append(url)
        return b"fake image bytes", "image/png"

    original_download = module._download_image
    module._download_image = fake_download
    try:
        with tempfile.TemporaryDirectory(prefix=".image-localization-smoke-", dir=REPO_ROOT) as tmp:
            article = Path(tmp) / "article"
            assets = article / "assets"
            assets.mkdir(parents=True)
            (assets / "image-777.png").write_bytes(b"existing")
            (article / "metadata.yaml").write_text(
                'content_kind: "wechat_official_article"\nis_translation_mirror: true\n',
                encoding="utf-8",
            )
            (article / "source.md").write_text(
                "# Source\n\n"
                "![source](https://mmbiz.qpic.cn/source/640?wx_fmt=png)\n\n"
                "![already local](assets/image-777.png)\n\n"
                "![]()\n",
                encoding="utf-8",
            )
            (article / "translation.zh-CN.md").write_text(
                "![translation](https://mmbiz.qpic.cn/translation/640?wx_fmt=png)\n",
                encoding="utf-8",
            )
            (article / "summary.md").write_text(
                "Human summary text stays put.\n\n"
                "![summary](https://mmbiz.qpic.cn/summary/640?wx_fmt=png)\n",
                encoding="utf-8",
            )
            (article / "notes.md").write_text(
                "Human notes text stays put.\n\n"
                "![notes](https://mmbiz.qpic.cn/notes/640?wx_fmt=png)\n",
                encoding="utf-8",
            )

            result = module.localize_article(article)
            file_stats = {entry["file"]: entry for entry in result["markdown_files"]}
            ok = check(result["image_total"] == 4, f"four unique remote images found ({result['image_total']})")
            ok &= check(result["image_localized"] == 4, f"four images localized ({result['image_localized']})")
            ok &= check(result["image_failed"] == 0, f"no image failures ({result['image_failed']})")
            ok &= check(len(calls) == 4, f"download called only for four remote URLs ({len(calls)})")
            ok &= check(all("assets/" not in url for url in calls), "existing assets image was not downloaded")

            for fname in ["source.md", "translation.zh-CN.md", "summary.md", "notes.md"]:
                text = (article / fname).read_text(encoding="utf-8")
                ok &= check("mmbiz.qpic.cn" not in text, f"{fname} has no remote mmbiz")
                ok &= check("assets/image-" in text, f"{fname} has localized assets path")
                ok &= check(file_stats[fname]["image_total"] == 1, f"{fname} image_total == 1")
                ok &= check(file_stats[fname]["image_localized"] == 1, f"{fname} image_localized == 1")
                ok &= check(file_stats[fname]["image_failed"] == 0, f"{fname} image_failed == 0")
                ok &= check(file_stats[fname]["file_changed"] is True, f"{fname} file_changed true")

            source_text = (article / "source.md").read_text(encoding="utf-8")
            ok &= check("![]()" in source_text, "empty image stays unchanged")
            ok &= check((assets / "image-777.png").read_bytes() == b"existing",
                        "pre-existing local asset was not overwritten")
            ok &= check((assets / "image-778.png").exists(), "new downloads start after existing image-NNN")
            return ok
    finally:
        module._download_image = original_download


def main() -> int:
    print("=" * 60)
    print("Image localization smoke tests (v0.3.75)")
    print("=" * 60)
    results = [
        smoke_1_localize_dry_run(),
        smoke_2_source_uses_local_assets(),
        smoke_3_mirror_synced(),
        smoke_4_assets_in_site_and_docs(),
        smoke_5_html_uses_local_images(),
        smoke_6_pages_sync_pass(),
        smoke_7_no_broken_empty_images(),
        smoke_8_temp_article_all_public_markdown_files(),
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
