#!/usr/bin/env python3
"""Check v0.3.x release tags for duplicates and recommend next version.

Usage:
    python3 scripts/check_release_tags.py

Exit codes:
    0 - PASS or PASS_WITH_WARNINGS
    1 - FAIL (git not available or other error)
"""

import re
import subprocess
import sys


def run_git(*args):
    """Run git command and return stdout."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"FAIL: git command failed: {' '.join(args)}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("FAIL: git not found in PATH")
        sys.exit(1)


def parse_version(tag_name):
    """Extract minor version from v0.3.N-tag format."""
    match = re.match(r"v0\.3\.(\d+)-", tag_name)
    if match:
        return int(match.group(1))
    return None


def main():
    # Get all v0.3.* tags
    tags_output = run_git("tag", "--list", "v0.3.*", "--sort=version:refname")
    
    if not tags_output:
        print("STATUS: PASS")
        print("No v0.3.x tags found.")
        print("recommended_next_minor: v0.3.0")
        return

    tags = tags_output.split("\n")
    
    # Group by minor version
    minor_groups = {}
    for tag in tags:
        minor = parse_version(tag)
        if minor is not None:
            minor_groups.setdefault(minor, []).append(tag)

    # Check for duplicates
    duplicates = {}
    known_exceptions = {36}  # v0.3.36 is known exception
    
    for minor, tag_list in minor_groups.items():
        if len(tag_list) > 1:
            duplicates[minor] = tag_list

    # Determine status
    has_unknown_duplicates = any(m not in known_exceptions for m in duplicates)
    
    if duplicates:
        if has_unknown_duplicates:
            status = "PASS_WITH_WARNINGS"
        else:
            status = "PASS_WITH_WARNINGS"
    else:
        status = "PASS"

    # Find max minor version
    max_minor = max(minor_groups.keys()) if minor_groups else 0
    recommended_next = max_minor + 1

    # Output
    print(f"STATUS: {status}")
    print()
    print(f"v0.3 tags: {len(tags)}")
    print(f"unique minor versions: {len(minor_groups)}")
    print()

    if duplicates:
        print("duplicate minor versions:")
        for minor in sorted(duplicates.keys()):
            tag_list = duplicates[minor]
            is_known = minor in known_exceptions
            marker = " [KNOWN EXCEPTION]" if is_known else ""
            print(f"  v0.3.{minor}: {', '.join(tag_list)}{marker}")
        print()

    print(f"latest minor: v0.3.{max_minor}")
    print(f"recommended_next_minor: v0.3.{recommended_next}")
    print()

    # Check remote tags
    try:
        remote_output = run_git("ls-remote", "--tags", "origin", "v0.3.*")
        remote_tags = []
        for line in remote_output.split("\n"):
            if line.strip():
                parts = line.split()
                if len(parts) >= 2:
                    ref = parts[1]
                    tag_name = ref.replace("refs/tags/", "")
                    if "^{}" not in tag_name:
                        remote_tags.append(tag_name)

        print(f"remote v0.3 tags: {len(remote_tags)}")

        # Check for local/remote mismatch
        local_set = set(tags)
        remote_set = set(remote_tags)

        only_local = local_set - remote_set
        only_remote = remote_set - local_set

        if only_local:
            print(f"warning: {len(only_local)} tags not pushed to origin")
            for tag in sorted(only_local):
                print(f"  - {tag}")

        if only_remote:
            print(f"warning: {len(only_remote)} tags only on origin (fetch to sync)")
            for tag in sorted(only_remote):
                print(f"  - {tag}")

    except SystemExit:
        raise
    except Exception as e:
        print(f"warning: could not check remote tags: {e}")

    print()

    # v0.3.96+: Tag SHA sanity check.
    # Explicitly distinguish:
    #   - "tag object SHA"      : `git rev-parse v0.3.X`  (annotated tag object's SHA;
    #                                                 equals commit SHA only for lightweight tags)
    #   - "dereferenced commit SHA": `git rev-parse v0.3.X^{}` (always the pointed-to commit)
    # For protected tags (stable baseline + asset release), both SHAs must be tracked so
    # future agents can verify the tag has not been moved silently.
    protected_tags = [
        "v0.3.91-material-ingestion-stable-baseline",
        "v0.3.92-bingzhu-you-mv-assets",
    ]
    print("tag SHA sanity (annotated object vs dereferenced commit):")
    sha_check_ok = True
    for tag in protected_tags:
        try:
            obj_sha = run_git("rev-parse", tag)
            commit_sha = run_git("rev-parse", f"{tag}^{{}}")
            obj_short = obj_sha[:12] if obj_sha else "N/A"
            commit_short = commit_sha[:12] if commit_sha else "N/A"
            if obj_sha == commit_sha:
                kind = "lightweight"
            else:
                kind = "annotated"
            print(f"  {tag}")
            print(f"    tag_object_sha:       {obj_short}")
            print(f"    dereferenced_commit:  {commit_short}")
            print(f"    kind: {kind}")
        except SystemExit:
            raise
        except Exception as e:
            sha_check_ok = False
            print(f"  {tag}: ERROR {e}")
    print()

    if status == "PASS_WITH_WARNINGS":
        print("Notes:")
        print("- v0.3.36 duplicate is a known exception (repo-health + repo-hygiene)")
        print("- From v0.3.37 onwards, avoid reusing minor numbers")
        print(f"- Next available: v0.3.{recommended_next}")
        if not sha_check_ok:
            print("- Tag SHA sanity check had errors (review above)")
    
    # Exit 0 for PASS and PASS_WITH_WARNINGS (non-blocking)
    sys.exit(0)


if __name__ == "__main__":
    main()
