#!/usr/bin/env python3
"""
Pages sync integrity check.

Verifies that site/ (development source) and docs/ (GitHub Pages deploy) are
byte-identical for every published file. This guards against the failure mode
where `update_site.py` ran successfully but `git add` skipped one of the
synced docs/ files — leaving GitHub Pages serving a stale version while the
local working tree looks correct.

Checks:
  1. Top-level files in SYNC_FILES are identical (site/X == docs/X).
  2. site/items/ and docs/items/ have the same set of slugs.
  3. site/items/<slug>/index.html == docs/items/<slug>/index.html for every slug.
  4. v0.3.70: every content/articles/<slug>/metadata.yaml has a corresponding
     item page in BOTH site/items/ and docs/items/. Catches the failure mode
     where generate_item_pages.py silently skipped records (e.g. the Windows
     backslash path bug) and the item page count drifted below the KB count.

Exit codes:
  0 = PASS (everything consistent)
  1 = FAIL (at least one mismatch — print a structured report and stop)
  2 = unexpected error
"""

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DIR = REPO_ROOT / "site"
DOCS_DIR = REPO_ROOT / "docs"
CONTENT_DIR = REPO_ROOT / "content"

# Top-level files that must match byte-for-byte. Mirrors
# scripts/sync_pages_docs.py:SYNC_FILES — keep them in sync if you add one.
TOP_LEVEL_FILES = [
    "index.html",
    "app.js",
    "styles.css",
    "data/catalog.json",
]

# Item subtree that must mirror between site/ and docs/.
ITEMS_SUBDIR = "items"


def file_hash(path: Path) -> str:
    """Stable content hash (sha256, lowercase hex)."""
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()[:16]  # short hash is enough for diff-by-eye


def check_top_level() -> tuple[bool, list[str], list[str], list[str]]:
    """Returns (ok, mismatched, missing_in_docs, missing_in_site).

    Each list contains paths relative to repo root.
    """
    mismatched: list[str] = []
    missing_in_docs: list[str] = []
    missing_in_site: list[str] = []

    for rel in TOP_LEVEL_FILES:
        src = SITE_DIR / rel
        dst = DOCS_DIR / rel
        if not src.exists():
            missing_in_site.append(f"site/{rel}")
            continue
        if not dst.exists():
            missing_in_docs.append(f"docs/{rel}")
            continue
        if file_hash(src) != file_hash(dst):
            mismatched.append(rel)

    ok = not mismatched and not missing_in_docs and not missing_in_site
    return ok, mismatched, missing_in_docs, missing_in_site


def _slug_list(root: Path) -> set[str]:
    """Return the set of slug subdirectories under root/<ITEMS_SUBDIR>/."""
    items_dir = root / ITEMS_SUBDIR
    if not items_dir.exists():
        return set()
    return {p.name for p in items_dir.iterdir() if p.is_dir()}


def _expected_slugs_from_content() -> set[str]:
    """v0.3.70: derive the expected set of item-page slugs from content/.

    Scans content/**/metadata.yaml and returns the set of parent directory
    names. This is the ground-truth set of slugs that should each have a
    site/items/<slug>/index.html and docs/items/<slug>/index.html.
    """
    slugs: set[str] = set()
    if not CONTENT_DIR.exists():
        return slugs
    for meta_file in CONTENT_DIR.rglob("metadata.yaml"):
        # The slug is the immediate parent directory name of metadata.yaml.
        slug = meta_file.parent.name
        if slug:
            slugs.add(slug)
    return slugs


def check_items() -> tuple[
    bool,
    set[str],
    set[str],
    set[str],
    list[str],
]:
    """Returns (ok, missing_in_docs, extra_in_docs, extra_in_site, content_mismatches).

    - missing_in_docs: slugs present in site/items/ but not docs/items/.
    - extra_in_docs:   slugs present in docs/items/ but not site/items/ (stale).
    - extra_in_site:   not used (parity with above); kept for symmetric reporting.
    - content_mismatches: slug/index.html pairs whose content differs.
    """
    site_slugs = _slug_list(SITE_DIR)
    docs_slugs = _slug_list(DOCS_DIR)

    missing_in_docs = site_slugs - docs_slugs
    extra_in_docs = docs_slugs - site_slugs
    extra_in_site: set[str] = set()  # always empty by construction
    content_mismatches: list[str] = []

    common = site_slugs & docs_slugs
    for slug in sorted(common):
        rel = f"{ITEMS_SUBDIR}/{slug}/index.html"
        src = SITE_DIR / rel
        dst = DOCS_DIR / rel
        # Missing index.html inside a slug dir is itself a mismatch worth surfacing.
        if not src.exists():
            content_mismatches.append(f"{rel} (missing in site)")
            continue
        if not dst.exists():
            content_mismatches.append(f"{rel} (missing in docs)")
            continue
        if file_hash(src) != file_hash(dst):
            content_mismatches.append(rel)

    ok = (
        not missing_in_docs
        and not extra_in_docs
        and not content_mismatches
    )
    return ok, missing_in_docs, extra_in_docs, extra_in_site, content_mismatches


def check_content_completeness() -> tuple[bool, set[str], set[str], set[str]]:
    """v0.3.70: verify every content/<slug>/metadata.yaml has an item page.

    Returns (ok, expected, missing_in_site, missing_in_docs).
    - expected: the full ground-truth slug set derived from content/.
    - missing_in_site: slugs that exist in content/ but not in site/items/.
    - missing_in_docs: slugs that exist in content/ but not in docs/items/.
    """
    expected = _expected_slugs_from_content()
    site_slugs = _slug_list(SITE_DIR)
    docs_slugs = _slug_list(DOCS_DIR)
    missing_in_site = expected - site_slugs
    missing_in_docs = expected - docs_slugs
    ok = not missing_in_site and not missing_in_docs
    return ok, expected, missing_in_site, missing_in_docs


def render_report(
    top_ok: bool,
    mismatched: list[str],
    missing_in_docs_top: list[str],
    missing_in_site_top: list[str],
    items_ok: bool,
    missing_in_docs_items: set[str],
    extra_in_docs_items: set[str],
    content_mismatches: list[str],
    completeness_ok: bool,
    expected_slugs: set[str],
    missing_in_site_completeness: set[str],
    missing_in_docs_completeness: set[str],
) -> int:
    site_count = len(_slug_list(SITE_DIR))
    docs_count = len(_slug_list(DOCS_DIR))
    expected_count = len(expected_slugs)

    print(f"\n{'=' * 60}")
    print("Pages sync integrity check")
    print(f"{'=' * 60}")

    # --- Top-level files ---
    print("\n[1/3] Top-level files (must be byte-identical)")
    print(f"  {'Path':<30} {'site/':<10} {'docs/':<10} {'Status'}")
    print(f"  {'-' * 30} {'-' * 10} {'-' * 10} {'-' * 10}")
    for rel in TOP_LEVEL_FILES:
        src_h = file_hash(SITE_DIR / rel) if (SITE_DIR / rel).exists() else "—"
        dst_h = file_hash(DOCS_DIR / rel) if (DOCS_DIR / rel).exists() else "—"
        if rel in mismatched:
            status = "MISMATCH"
        elif f"site/{rel}" in missing_in_site_top:
            status = "MISSING (site)"
        elif f"docs/{rel}" in missing_in_docs_top:
            status = "MISSING (docs)"
        else:
            status = "OK"
        print(f"  {rel:<30} {src_h:<10} {dst_h:<10} {status}")

    # --- Items site↔docs parity ---
    print(f"\n[2/3] Item pages (site/items/ ↔ docs/items/)")
    print(f"  site slugs: {site_count}")
    print(f"  docs slugs: {docs_count}")
    if missing_in_docs_items or extra_in_docs_items or content_mismatches:
        if missing_in_docs_items:
            print(f"  MISSING in docs/ ({len(missing_in_docs_items)}):")
            for slug in sorted(missing_in_docs_items):
                print(f"    - items/{slug}/index.html")
        if extra_in_docs_items:
            print(f"  STALE in docs/ ({len(extra_in_docs_items)}):")
            for slug in sorted(extra_in_docs_items):
                print(f"    - items/{slug}/index.html")
        if content_mismatches:
            print(f"  CONTENT MISMATCH ({len(content_mismatches)}):")
            for rel in content_mismatches:
                print(f"    - {rel}")
    else:
        print(f"  all {site_count} slugs present and byte-identical.")

    # --- Content completeness (v0.3.70) ---
    print(f"\n[3/3] Content→items completeness (v0.3.70)")
    print(f"  content/ metadata.yaml count: {expected_count}")
    print(f"  site/items/ slug count:       {site_count}")
    print(f"  docs/items/ slug count:       {docs_count}")
    if completeness_ok:
        print(f"  every content/ entry has an item page in both site/ and docs/.")
    else:
        if missing_in_site_completeness:
            print(f"  MISSING in site/items/ ({len(missing_in_site_completeness)}):")
            for slug in sorted(missing_in_site_completeness):
                print(f"    - items/{slug}/index.html  (content/ entry has no site page)")
        if missing_in_docs_completeness:
            print(f"  MISSING in docs/items/ ({len(missing_in_docs_completeness)}):")
            for slug in sorted(missing_in_docs_completeness):
                print(f"    - items/{slug}/index.html  (content/ entry has no docs page)")

    # --- Summary ---
    overall_ok = top_ok and items_ok and completeness_ok
    print(f"\n{'=' * 60}")
    if overall_ok:
        print("STATUS: PASS")
    else:
        print("STATUS: FAIL")
        print()
        print("site/ and docs/ are out of sync, or item pages are missing.")
        print("To fix:")
        print("  python3 scripts/update_site.py")
        print()
        print("If update_site.py reports PASS but this check fails, either:")
        print("  - you forgot to `git add` a synced docs/ file (git status), or")
        print("  - generate_item_pages.py skipped records (check its log for")
        print("    'Skipping record with non-content path' lines).")
    print(f"{'=' * 60}\n")

    return 0 if overall_ok else 1


def main() -> int:
    try:
        top_ok, mismatched, missing_in_docs_top, missing_in_site_top = check_top_level()
        items_ok, missing_items, extra_items, _extra_site, content_mm = check_items()
        comp_ok, expected, miss_site, miss_docs = check_content_completeness()
        return render_report(
            top_ok,
            mismatched,
            missing_in_docs_top,
            missing_in_site_top,
            items_ok,
            missing_items,
            extra_items,
            content_mm,
            comp_ok,
            expected,
            miss_site,
            miss_docs,
        )
    except Exception as exc:
        print(f"UNEXPECTED ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())