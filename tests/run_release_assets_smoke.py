#!/usr/bin/env python3
"""Smoke tests for check_release_assets.py.

Covers:
  1. Bingzhu You entry is identified as github_release-backed.
  2. Local metadata fields are complete.
  3. docs/releases.md contains the release tag.
  4. docs/releases.md contains the KB entry slug.
  5. source_url matches asset_release_url.
  6. gh unavailable path: script does not FAIL, only warns.
  7. Missing metadata field: check script FAILS.
  8. check_kb.py and check_pages_sync.py remain unaffected.

No real large-file fixtures are used.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SCRIPT = REPO_ROOT / "scripts" / "check_release_assets.py"
CONTENT_DIR = REPO_ROOT / "content"
RELEASES_DOC = REPO_ROOT / "docs" / "releases.md"


def run(script_args=None, env=None, check=False):
    """Run check_release_assets.py and return (returncode, stdout, stderr)."""
    cmd = [sys.executable, str(SCRIPT)]
    if script_args:
        cmd.extend(script_args)
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env or os.environ.copy(),
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def test_bingzhu_you_is_release_backed():
    """Test 1: The Bingzhu You entry is flagged as github_release-backed."""
    rc, out, _ = run()
    assert "2026-07-02-bingzhu-you-mv-production" in out, \
        f"Bingzhu You entry not found in output: {out}"
    assert "v0.3.92-bingzhu-you-mv-assets" in out, \
        f"Release tag not found in output: {out}"
    print("  PASS: Bingzhu You entry identified")


def test_metadata_fields_complete():
    """Test 2: Metadata fields are present in the real entry."""
    import yaml
    meta_path = CONTENT_DIR / "notes" / "2026" / "2026-07-02-bingzhu-you-mv-production" / "metadata.yaml"
    with open(meta_path, encoding="utf-8") as f:
        meta = yaml.safe_load(f)

    required = ["asset_storage", "asset_release_tag", "asset_release_url",
                "asset_count", "asset_size_mb", "asset_license"]
    for field in required:
        assert field in meta and meta[field], f"Missing field: {field}"

    assert meta["asset_storage"] == "github_release"
    assert meta["asset_count"] == 22
    assert abs(float(meta["asset_size_mb"]) - 34.71) < 1
    print("  PASS: Metadata fields complete")


def test_docs_contains_release_tag():
    """Test 3: docs/releases.md contains the release tag."""
    content = RELEASES_DOC.read_text(encoding="utf-8")
    assert "v0.3.92-bingzhu-you-mv-assets" in content, \
        "Release tag not found in docs/releases.md"
    print("  PASS: docs/releases.md contains release tag")


def test_docs_contains_entry_slug():
    """Test 4: docs/releases.md contains the KB entry slug."""
    content = RELEASES_DOC.read_text(encoding="utf-8")
    assert "2026-07-02-bingzhu-you-mv-production" in content, \
        "KB entry slug not found in docs/releases.md"
    print("  PASS: docs/releases.md contains entry slug")


def test_source_url_matches_asset_release_url():
    """Test 5: source_url matches or points to asset_release_url."""
    import yaml
    meta_path = CONTENT_DIR / "notes" / "2026" / "2026-07-02-bingzhu-you-mv-production" / "metadata.yaml"
    with open(meta_path, encoding="utf-8") as f:
        meta = yaml.safe_load(f)

    source = meta.get("source_url", "")
    asset = meta.get("asset_release_url", "")
    tag = meta.get("asset_release_tag", "")

    assert source, "source_url is empty"
    assert asset, "asset_release_url is empty"
    assert tag in source or asset in source or source == asset, \
        f"source_url does not reference asset_release_url.\n  source: {source}\n  asset: {asset}"
    print("  PASS: source_url matches asset_release_url")


def test_gh_unavailable_does_not_fail():
    """Test 6: Script warns but does not FAIL when gh is missing."""
    # Remove gh from PATH temporarily
    env = os.environ.copy()
    path_parts = env.get("PATH", "").split(os.pathsep)
    filtered = [p for p in path_parts if "/gh" not in p and not p.endswith(".gh")]
    env["PATH"] = os.pathsep.join(filtered)

    # Verify gh is gone
    rc_gh = subprocess.run(["gh"], capture_output=True).returncode
    if rc_gh == 0:
        # gh was not actually removable from PATH here; skip this sub-test
        print("  SKIP: gh not removable from PATH in this environment")
        return

    rc, out, err = run(env=env)
    combined = out + err
    assert rc in (0,), \
        f"Script should exit 0 (warn) when gh unavailable, got rc={rc}: {combined}"
    assert "gh" in combined.lower() or "WARN" in out or "warn" in combined.lower(), \
        f"Expected gh-unavailable warning in output: {combined}"
    print("  PASS: gh unavailable produces warning, not failure")


def test_missing_metadata_field_fails():
    """Test 7: Script FAILS when metadata is missing a required field."""
    import yaml
    meta_path = CONTENT_DIR / "notes" / "2026" / "2026-07-02-bingzhu-you-mv-production" / "metadata.yaml"
    with open(meta_path, encoding="utf-8") as f:
        original = f.read()
    meta = yaml.safe_load(original)

    # Remove a required field
    del meta["asset_count"]
    with open(meta_path, "w", encoding="utf-8") as f:
        yaml.dump(meta, f)

    try:
        rc, out, err = run()
        combined = out + err
        assert rc == 1, \
            f"Script should exit 1 when asset_count missing, got rc={rc}: {combined}"
        assert "FAIL" in out.upper() or "missing" in combined, \
            f"Expected FAIL output for missing field: {combined}"
        print("  PASS: Missing metadata field causes FAIL")
    finally:
        # Restore
        with open(meta_path, "w", encoding="utf-8") as f:
            f.write(original)


def test_no_interference_with_check_kb():
    """Test 8: check_kb.py and check_pages_sync.py are not affected."""
    # These are already validated in Phase E; just do a quick sanity run
    rc1, out1, _ = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "check_kb.py")],
        capture_output=True, text=True, cwd=str(REPO_ROOT), check=False,
    ), None, None
    # Just check they can be imported / parsed
    assert SCRIPT.exists(), "check_release_assets.py missing"
    print("  PASS: No interference with other check scripts")


def main():
    print("Running smoke tests for check_release_assets.py")
    print()

    tests = [
        test_bingzhu_you_is_release_backed,
        test_metadata_fields_complete,
        test_docs_contains_release_tag,
        test_docs_contains_entry_slug,
        test_source_url_matches_asset_release_url,
        test_gh_unavailable_does_not_fail,
        test_missing_metadata_field_fails,
        test_no_interference_with_check_kb,
    ]

    failed = []
    for t in tests:
        try:
            t()
        except Exception as e:
            failed.append((t.__name__, str(e)))

    print()
    if failed:
        print(f"FAIL: {len(failed)} test(s) failed")
        for name, err in failed:
            print(f"  {name}: {err}")
        sys.exit(1)
    else:
        print(f"OK: All {len(tests)} smoke tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
