#!/usr/bin/env python3
"""Release-backed asset integrity checker.

Scans all content entries for asset_storage: github_release and verifies:
  1. Required metadata fields are present and valid.
  2. docs/releases.md contains the release tag and KB slug.
  3. source_url in metadata matches asset_release_url.
  4. GitHub Release exists and matches metadata (if gh CLI is available).

Usage:
    python3 scripts/check_release_assets.py

Exit codes:
    0 - PASS or PASS_WITH_WARNINGS
    1 - FAIL
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).parent.parent.resolve()
CONTENT_DIR = REPO_ROOT / "content"
RELEASES_DOC = REPO_ROOT / "docs" / "releases.md"

# Fields required in metadata.yaml for github_release entries
REQUIRED_METADATA_FIELDS = [
    "asset_release_tag",
    "asset_release_url",
    "asset_count",
    "asset_size_mb",
    "asset_license",
]

# Fields that must be positive numbers
POSITIVE_NUMERIC_FIELDS = ["asset_count", "asset_size_mb"]


def run_git(*args, check=False) -> Optional[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=check,
        )
        return result.stdout.strip()
    except FileNotFoundError:
        return None
    except subprocess.CalledProcessError:
        return None


def find_release_backed_entries() -> List[Tuple[Path, dict]]:
    """Find all metadata.yaml entries with asset_storage: github_release."""
    entries = []
    for metadata_path in CONTENT_DIR.rglob("metadata.yaml"):
        try:
            import yaml
            with open(metadata_path, encoding="utf-8") as f:
                meta = yaml.safe_load(f) or {}
        except Exception:
            continue
        if meta.get("asset_storage") == "github_release":
            entries.append((metadata_path, meta))
    return entries


def check_metadata_fields(meta: dict, entry_path: Path) -> List[str]:
    """Check required metadata fields. Returns list of error messages."""
    errors = []
    for field in REQUIRED_METADATA_FIELDS:
        if not meta.get(field):
            errors.append(f"{entry_path}: missing required field '{field}'")

    for field in POSITIVE_NUMERIC_FIELDS:
        val = meta.get(field)
        if val is not None:
            try:
                num = float(val)
                if num <= 0:
                    errors.append(
                        f"{entry_path}: '{field}' must be positive, got {val}"
                    )
            except (TypeError, ValueError):
                errors.append(
                    f"{entry_path}: '{field}' must be numeric, got {val!r}"
                )

    # asset_release_url must be a GitHub Release tag URL
    url = meta.get("asset_release_url", "")
    if url:
        pattern = r"https://github\.com/[^/]+/[^/]+/releases/tag/.+"
        if not re.match(pattern, url):
            errors.append(
                f"{entry_path}: asset_release_url does not look like a GitHub Release tag URL: {url}"
            )

    return errors


def check_source_url_consistency(meta: dict, entry_path: Path) -> List[str]:
    """Check source_url matches or points to asset_release_url."""
    source_url = meta.get("source_url", "")
    asset_url = meta.get("asset_release_url", "")
    if source_url and asset_url:
        # source_url should be equal to or a variation of asset_release_url
        # (it should at minimum contain the same tag reference)
        tag = meta.get("asset_release_tag", "")
        if tag and tag not in source_url and asset_url not in source_url:
            return [
                f"{entry_path}: source_url does not reference asset_release_url or its tag.\n"
                f"  source_url: {source_url}\n"
                f"  asset_release_url: {asset_url}"
            ]
    return []


def check_releases_doc(entry_path: Path, meta: dict) -> List[str]:
    """Check docs/releases.md contains the release tag and KB slug."""
    errors = []
    if not RELEASES_DOC.exists():
        errors.append(f"{entry_path}: docs/releases.md not found")
        return errors

    try:
        doc_content = RELEASES_DOC.read_text(encoding="utf-8")
    except Exception as e:
        errors.append(f"{entry_path}: cannot read docs/releases.md: {e}")
        return errors

    tag = meta.get("asset_release_tag", "")
    slug = entry_path.parent.name  # e.g. 2026-07-02-bingzhu-you-mv-production

    if tag and tag not in doc_content:
        errors.append(
            f"{entry_path}: release tag '{tag}' not found in docs/releases.md"
        )

    if slug and slug not in doc_content:
        errors.append(
            f"{entry_path}: KB entry slug '{slug}' not found in docs/releases.md"
        )

    return errors


def gh_available() -> bool:
    """Check if gh CLI is available and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def check_gh_release(meta: dict, entry_path: Path) -> Tuple[str, List[str]]:
    """Check GitHub Release via gh CLI. Returns (status, error_messages)."""
    tag = meta.get("asset_release_url", "")
    if not tag:
        return "FAIL", [f"{entry_path}: no asset_release_url to check"]

    # gh release view requires the tag name, not full URL
    # Extract tag from URL: https://github.com/owner/repo/releases/tag/<tag>
    match = re.search(r"/releases/tag/(.+)$", tag)
    if not match:
        return "FAIL", [f"{entry_path}: cannot extract tag from asset_release_url: {tag}"]
    tag_name = match.group(1)

    try:
        result = subprocess.run(
            [
                "gh", "release", "view", tag_name,
                "--json", "tagName,name,url,assets",
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return "WARN", [f"{entry_path}: gh release view timed out for tag '{tag_name}'"]
    except subprocess.CalledProcessError as e:
        err = e.stderr.strip() if e.stderr else ""
        return "FAIL", [f"{entry_path}: gh release view failed for '{tag_name}': {err}"]
    except FileNotFoundError:
        return "WARN", ["gh CLI not available, skipping live release validation"]

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as e:
        return "WARN", [f"{entry_path}: failed to parse gh JSON output: {e}"]

    errors = []

    # Check URL matches
    meta_url = meta.get("asset_release_url", "")
    gh_url = data.get("url", "")
    if meta_url and gh_url and meta_url != gh_url:
        # Normalize: gh returns the release HTML URL; meta stores the tag URL
        # They should be the same for our format
        if meta_url.rstrip("/") != gh_url.rstrip("/"):
            errors.append(
                f"{entry_path}: asset_release_url mismatch.\n"
                f"  metadata: {meta_url}\n"
                f"  gh url:   {gh_url}"
            )

    # Check asset count
    meta_count = meta.get("asset_count")
    assets = data.get("assets", [])
    gh_count = len(assets)
    if meta_count is not None:
        try:
            if int(meta_count) != int(gh_count):
                errors.append(
                    f"{entry_path}: asset count mismatch.\n"
                    f"  metadata: {meta_count}\n"
                    f"  gh asset count: {gh_count}"
                )
        except (TypeError, ValueError):
            pass

    # Check assets list is non-empty
    if not assets:
        errors.append(f"{entry_path}: gh reports 0 assets for tag '{tag_name}'")

    # Check asset sizes sum vs asset_size_mb (approximate, allow rounding)
    meta_size_mb = meta.get("asset_size_mb")
    if meta_size_mb is not None and assets:
        try:
            total_bytes = sum(a.get("size", 0) for a in assets)
            total_mb = total_bytes / (1024 * 1024)
            meta_mb = float(meta_size_mb)
            # Allow ±0.5 MB tolerance for rounding differences
            if abs(total_mb - meta_mb) > 0.5:
                errors.append(
                    f"{entry_path}: asset size mismatch.\n"
                    f"  metadata: {meta_mb:.2f} MB\n"
                    f"  gh computed: {total_mb:.2f} MB\n"
                    f"  (tolerance: ±0.5 MB)"
                )
        except (TypeError, ValueError):
            pass

    if errors:
        return "FAIL", errors
    return "PASS", []


def main() -> None:
    all_errors: List[str] = []
    warnings: List[str] = []

    entries = find_release_backed_entries()

    if not entries:
        # No github_release entries is valid - this is a forward-compatibility check
        print("STATUS: PASS")
        print("No asset_storage: github_release entries found.")
        sys.exit(0)

    print(f"Found {len(entries)} release-backed entry(ies):")
    for path, meta in entries:
        slug = path.parent.name
        tag = meta.get("asset_release_tag", "N/A")
        print(f"  - {slug} (tag: {tag})")
    print()

    gh_ok = gh_available()
    if not gh_ok:
        warnings.append("gh CLI unavailable — skipped live GitHub Release validation.")

    for metadata_path, meta in entries:
        entry_path = metadata_path  # for error messages
        slug = metadata_path.parent.name

        print(f"Checking: {slug}")

        # 1. Metadata fields
        field_errors = check_metadata_fields(meta, entry_path)
        all_errors.extend(field_errors)

        # 2. source_url consistency
        source_errors = check_source_url_consistency(meta, entry_path)
        all_errors.extend(source_errors)

        # 3. docs/releases.md index
        doc_errors = check_releases_doc(entry_path, meta)
        all_errors.extend(doc_errors)

        # 4. gh live check (if available)
        if gh_ok:
            gh_status, gh_errors = check_gh_release(meta, entry_path)
            all_errors.extend(gh_errors)
            if gh_status == "WARN":
                warnings.extend(gh_errors)
        else:
            print(f"  [gh unavailable, skipping live check]")

        print()

    # Emit results
    if all_errors:
        print("=" * 60)
        print("FAIL: Release asset integrity check failed")
        print("=" * 60)
        for err in all_errors:
            print(f"  ERROR: {err}")
        if warnings:
            print()
            print("Warnings:")
            for w in warnings:
                print(f"  WARN: {w}")
        sys.exit(1)
    elif warnings:
        print("=" * 60)
        print("STATUS: PASS_WITH_WARNINGS")
        print("=" * 60)
        print(f"entries_found: {len(entries)}")
        for w in warnings:
            print(f"  WARN: {w}")
        sys.exit(0)
    else:
        print("=" * 60)
        print("STATUS: PASS")
        print("=" * 60)
        print(f"entries_found: {len(entries)}")
        print("All release-backed entries are consistent.")


if __name__ == "__main__":
    main()
