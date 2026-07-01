#!/usr/bin/env python3
"""localize_article_images.py — Download remote WeChat images to local assets/.

For each article under content/articles/YYYY/<slug>/:
1. Scan source.md and translation.zh-CN.md for Markdown image syntax: ![alt](url)
2. Download each remote image to content/articles/YYYY/<slug>/assets/image-NNN.<ext>
3. Rewrite the Markdown image URL to the local relative path: ![alt](assets/image-NNN.<ext>)
4. For Chinese-mirror articles (source ≈ translation), sync both files so
   check_kb.py word_count drift stays low.

Supports:
    python3 scripts/localize_article_images.py --article-path "content/articles/2026/<slug>"
    python3 scripts/localize_article_images.py --all-wechat
    python3 scripts/localize_article_images.py --all-wechat --dry-run

Download failures are recorded but do NOT crash the script — the original
remote URL is kept and the failure is logged. No login, no cookie, no
bypass of WeChat access restrictions.

Exit codes:
    0 - Completed (some images may have failed individually)
    1 - Usage error
    2 - Runtime error
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional

KB_HOME = Path(__file__).resolve().parent.parent
CONTENT_DIR = KB_HOME / "content"

# Regex for Markdown images: ![alt](url) — alt can be empty.
# Captures group(1)=alt, group(2)=url.
_MD_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]*)\)")

# Only http/https URLs are candidates for localization.
_REMOTE_URL_RE = re.compile(r"^https?://", re.IGNORECASE)

# Content-Type → extension mapping.
CONTENT_TYPE_EXT = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
}

# URL path → extension fallback.
_URL_EXT_RE = re.compile(r"\.(jpg|jpeg|png|gif|webp|svg|bmp|tiff)(?:\?|$)", re.IGNORECASE)

# Browser-like UA for downloading images (some CDNs reject default Python UA).
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)


def _infer_extension(url: str, content_type: str) -> str:
    """Infer file extension from Content-Type header or URL path."""
    ct = content_type.lower().split(";")[0].strip()
    if ct in CONTENT_TYPE_EXT:
        return CONTENT_TYPE_EXT[ct]
    m = _URL_EXT_RE.search(url)
    if m:
        ext = m.group(1).lower()
        return ".jpeg" if ext == "jpg" else "." + ext
    return ".jpg"  # safe default


def _download_image(url: str, timeout: int = 20) -> tuple[bytes, str]:
    """Download a remote image. Returns (data, content_type).

    Raises urllib.error.URLError or urllib.error.HTTPError on failure.
    Uses the system proxy env (HTTP_PROXY/HTTPS_PROXY).
    """
    proxy_handler = urllib.request.ProxyHandler()  # auto-detect from env
    opener = urllib.request.build_opener(proxy_handler)
    req = urllib.request.Request(url, headers={
        "User-Agent": BROWSER_UA,
        "Accept": "image/*,*/*;q=0.8",
        "Referer": "https://mp.weixin.qq.com/",
    })
    resp = opener.open(req, timeout=timeout)
    data = resp.read()
    content_type = resp.headers.get("Content-Type", "")
    return data, content_type


def _is_mirror_article(meta_path: Path) -> bool:
    """Check if article has is_translation_mirror: true in metadata.yaml."""
    if not meta_path.exists():
        return False
    text = meta_path.read_text(encoding="utf-8")
    return bool(re.search(r"^is_translation_mirror:\s*true\s*$", text, re.MULTILINE))


def _find_wechat_articles() -> list[Path]:
    """Find all wechat articles under content/articles/."""
    articles: list[Path] = []
    for meta in CONTENT_DIR.rglob("metadata.yaml"):
        text = meta.read_text(encoding="utf-8")
        if re.search(r'^content_kind:\s*"wechat_official_article"', text, re.MULTILINE):
            articles.append(meta.parent)
    return sorted(articles)


def _rewrite_markdown(md_text: str, url_to_local: dict[str, str]) -> str:
    """Rewrite Markdown image URLs to local paths using url_to_local mapping."""
    def _replace(m: re.Match) -> str:
        alt = m.group(1)
        url = m.group(2)
        if url in url_to_local:
            return f"![{alt}]({url_to_local[url]})"
        return m.group(0)  # keep original

    return _MD_IMAGE_RE.sub(_replace, md_text)


def localize_article(article_path: Path, dry_run: bool = False) -> dict:
    """Localize images for a single article.

    Returns a dict with:
        article_path, image_total, image_localized, image_failed,
        assets_path, failures (list of {url, reason}), dry_run
    """
    result = {
        "article_path": str(article_path.relative_to(KB_HOME).as_posix()) + "/",
        "image_total": 0,
        "image_localized": 0,
        "image_failed": 0,
        "assets_path": "",
        "failures": [],
        "dry_run": dry_run,
    }

    source_md_path = article_path / "source.md"
    trans_md_path = article_path / "translation.zh-CN.md"
    meta_path = article_path / "metadata.yaml"

    if not source_md_path.exists():
        result["failures"].append({"url": "", "reason": "source.md not found"})
        return result

    source_text = source_md_path.read_text(encoding="utf-8")
    trans_text = trans_md_path.read_text(encoding="utf-8") if trans_md_path.exists() else ""
    is_mirror = _is_mirror_article(meta_path)

    # Collect all remote image URLs from source.md (and translation if mirror).
    urls_to_download: list[str] = []
    seen_urls: set[str] = set()

    for m in _MD_IMAGE_RE.finditer(source_text):
        url = m.group(2)
        if url and _REMOTE_URL_RE.match(url) and url not in seen_urls:
            urls_to_download.append(url)
            seen_urls.add(url)

    if is_mirror and trans_text:
        for m in _MD_IMAGE_RE.finditer(trans_text):
            url = m.group(2)
            if url and _REMOTE_URL_RE.match(url) and url not in seen_urls:
                urls_to_download.append(url)
                seen_urls.add(url)

    result["image_total"] = len(urls_to_download)
    if not urls_to_download:
        return result  # No remote images to localize.

    assets_dir = article_path / "assets"
    result["assets_path"] = str(assets_dir.relative_to(KB_HOME).as_posix()) + "/"

    if dry_run:
        # In dry-run, just report what would be downloaded.
        result["image_localized"] = len(urls_to_download)
        return result

    # Download images.
    url_to_local: dict[str, str] = {}
    for i, url in enumerate(urls_to_download, 1):
        try:
            data, content_type = _download_image(url)
            ext = _infer_extension(url, content_type)
            filename = f"image-{i:03d}{ext}"
            local_rel = f"assets/{filename}"

            assets_dir.mkdir(parents=True, exist_ok=True)
            (assets_dir / filename).write_bytes(data)
            url_to_local[url] = local_rel
            result["image_localized"] += 1
        except Exception as e:
            result["image_failed"] += 1
            result["failures"].append({
                "url": url[:200],
                "reason": str(e)[:200],
            })

    # Rewrite source.md
    if url_to_local:
        new_source = _rewrite_markdown(source_text, url_to_local)
        source_md_path.write_text(new_source, encoding="utf-8")

        # Rewrite translation.zh-CN.md (mirror articles should stay in sync)
        if is_mirror and trans_text:
            new_trans = _rewrite_markdown(trans_text, url_to_local)
            trans_md_path.write_text(new_trans, encoding="utf-8")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Download remote WeChat images to local assets/.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--article-path", help="path to a single article directory")
    p.add_argument("--all-wechat", action="store_true",
                   help="process all wechat_official_article entries")
    p.add_argument("--dry-run", action="store_true",
                   help="report what would be downloaded without actually downloading")
    return p


def main() -> int:
    args = build_arg_parser().parse_args()

    if not args.article_path and not args.all_wechat:
        print("ERROR: must provide --article-path or --all-wechat", file=sys.stderr)
        return 1

    articles: list[Path] = []
    if args.article_path:
        p = Path(args.article_path)
        if not p.is_absolute():
            p = KB_HOME / p
        if not p.exists() or not p.is_dir():
            print(f"ERROR: article path not found: {p}", file=sys.stderr)
            return 1
        articles.append(p)

    if args.all_wechat:
        articles = _find_wechat_articles()
        print(f"[localize] found {len(articles)} wechat articles", file=sys.stderr)

    if not articles:
        print("ERROR: no articles to process", file=sys.stderr)
        return 1

    results: list[dict] = []
    total_images = 0
    total_localized = 0
    total_failed = 0

    for i, ap in enumerate(articles, 1):
        print(f"\n--- [{i}/{len(articles)}] {ap.name} ---", file=sys.stderr)
        r = localize_article(ap, dry_run=args.dry_run)
        results.append(r)
        total_images += r["image_total"]
        total_localized += r["image_localized"]
        total_failed += r["image_failed"]
        tag = "DRY_RUN" if args.dry_run else "DONE"
        print(f"    → {tag}: total={r['image_total']} "
              f"localized={r['image_localized']} failed={r['image_failed']}",
              file=sys.stderr)
        if r["failures"]:
            for f in r["failures"][:3]:
                print(f"      FAIL: {f['url'][:80]} :: {f['reason'][:80]}", file=sys.stderr)

    print(f"\n[localize] summary: articles={len(articles)} "
          f"images={total_images} localized={total_localized} failed={total_failed}",
          file=sys.stderr)

    # Write a JSON summary to stdout for programmatic consumption.
    summary = {
        "articles_processed": len(articles),
        "image_total": total_images,
        "image_localized": total_localized,
        "image_failed": total_failed,
        "dry_run": args.dry_run,
        "articles": results,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
