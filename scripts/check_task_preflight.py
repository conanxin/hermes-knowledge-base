#!/usr/bin/env python3
"""Task preflight checker — validates repo state before starting work.

Usage:
    python3 scripts/check_task_preflight.py
    python3 scripts/check_task_preflight.py --planned-tag v0.3.38-task-name
    python3 scripts/check_task_preflight.py --allow-warnings --planned-tag v0.3.38-task-name

Exit codes:
    0 - PASS or PASS_WITH_WARNINGS (with --allow-warnings)
    1 - FAIL (repo dirty, tag exists, version conflict, etc.)
"""

import argparse
import json
import os
import re
import subprocess
import sys


def run_git(*args, check=True):
    """Run git command and return stdout."""
    try:
        result = subprocess.run(
            ["git", *args],
            capture_output=True,
            text=True,
            check=check,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None
    except FileNotFoundError:
        return None


def run_check_script(script_path):
    """Run a check script and return (status, output)."""
    try:
        result = subprocess.run(
            ["python3", script_path],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
        output = result.stdout.strip()
        # Check exit code first, then parse output
        if result.returncode != 0:
            return "FAIL", output
        if "STATUS: PASS_WITH_WARNINGS" in output:
            return "PASS_WITH_WARNINGS", output
        elif "STATUS: PASS" in output:
            return "PASS", output
        elif "STATUS: WARNING" in output:
            return "WARNING", output
        else:
            return "FAIL", output
    except subprocess.TimeoutExpired:
        return "TIMEOUT", f"{script_path} timed out"
    except Exception as e:
        return "ERROR", str(e)


def parse_minor_version(tag_name):
    """Extract minor version from v0.3.N-tag format."""
    match = re.match(r"v0\.3\.(\d+)-", tag_name)
    if match:
        return int(match.group(1))
    return None


def get_recommended_minor():
    """Get recommended next minor from check_release_tags.py."""
    status, output = run_check_script("scripts/check_release_tags.py")
    if status in ("PASS", "PASS_WITH_WARNINGS"):
        match = re.search(r"recommended_next_minor:\s*v0\.3\.(\d+)", output)
        if match:
            return int(match.group(1))
    return None


def main():
    parser = argparse.ArgumentParser(description="Task preflight checker")
    parser.add_argument("--planned-tag", help="Planned version tag for the task")
    parser.add_argument("--allow-warnings", action="store_true", help="Allow PASS_WITH_WARNINGS status")
    parser.add_argument("--skip-heavy-checks", action="store_true", help="Skip heavy checks like check_tracks.py")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    args = parser.parse_args()

    results = {
        "status": "PASS",
        "checks": {},
        "warnings": [],
        "errors": [],
    }

    # 1. Check git repo
    git_dir = run_git("rev-parse", "--git-dir", check=False)
    if not git_dir:
        results["errors"].append("Not a git repository")
        results["status"] = "FAIL"
        _output(results, args.json)
        sys.exit(1)
    results["checks"]["git_repo"] = "PASS"

    # 2. Check git status
    status_output = run_git("status", "--short", check=False)
    if status_output:
        results["errors"].append(f"Working tree dirty:\n{status_output}")
        results["status"] = "FAIL"
    else:
        results["checks"]["git_status"] = "PASS"

    # 3. Check HEAD vs origin/main
    head = run_git("rev-parse", "HEAD", check=False)
    origin_head = run_git("rev-parse", "origin/main", check=False)
    if head and origin_head:
        if head == origin_head:
            results["checks"]["head_sync"] = "PASS"
        else:
            results["errors"].append(f"HEAD ({head[:8]}) != origin/main ({origin_head[:8]})")
            results["status"] = "FAIL"
    else:
        results["warnings"].append("Could not verify HEAD vs origin/main")

    # 4. Check planned tag
    if args.planned_tag:
        # Local tag check
        local_tags = run_git("tag", "--list", args.planned_tag, check=False)
        if local_tags:
            results["errors"].append(f"Local tag already exists: {args.planned_tag}")
            results["status"] = "FAIL"

        # Remote tag check
        remote_tags = run_git("ls-remote", "--tags", "origin", args.planned_tag, check=False)
        if remote_tags and args.planned_tag in remote_tags:
            results["errors"].append(f"Remote tag already exists: {args.planned_tag}")
            results["status"] = "FAIL"

        # Minor version check
        planned_minor = parse_minor_version(args.planned_tag)
        if planned_minor is not None:
            recommended = get_recommended_minor()
            if recommended is not None:
                if planned_minor < recommended:
                    results["errors"].append(
                        f"Planned minor v0.3.{planned_minor} < recommended v0.3.{recommended}. "
                        f"Do not reuse minor numbers."
                    )
                    results["status"] = "FAIL"
                elif planned_minor > recommended:
                    results["warnings"].append(
                        f"Planned minor v0.3.{planned_minor} > recommended v0.3.{recommended}. "
                        f"Gap is acceptable but verify no skipped versions."
                    )
                else:
                    results["checks"]["version_number"] = "PASS"
            else:
                results["warnings"].append("Could not determine recommended minor version")
        else:
            results["warnings"].append(f"Could not parse minor version from {args.planned_tag}")

        if "version_number" not in results["checks"] and not any(
            e.startswith("Planned minor") for e in results["errors"]
        ):
            results["checks"]["tag_available"] = "PASS"

    # 5. Run check_release_tags.py
    rt_status, rt_output = run_check_script("scripts/check_release_tags.py")
    results["checks"]["check_release_tags"] = rt_status
    if rt_status == "FAIL":
        results["errors"].append("check_release_tags.py failed")
        results["status"] = "FAIL"

    # 6. Run check_kb.py
    kb_status, kb_output = run_check_script("scripts/check_kb.py")
    results["checks"]["check_kb"] = kb_status
    if kb_status == "FAIL":
        results["errors"].append("check_kb.py failed")
        results["status"] = "FAIL"

    # 7. Run check_pages_sync.py
    ps_status, ps_output = run_check_script("scripts/check_pages_sync.py")
    results["checks"]["check_pages_sync"] = ps_status
    if ps_status == "FAIL":
        results["errors"].append("check_pages_sync.py failed")
        results["status"] = "FAIL"

    # 8. Run check_tracks.py (if exists)
    if os.path.exists("scripts/check_tracks.py") and not args.skip_heavy_checks:
        ct_status, ct_output = run_check_script("scripts/check_tracks.py")
        results["checks"]["check_tracks"] = ct_status
        if ct_status == "FAIL":
            results["errors"].append("check_tracks.py failed")
            results["status"] = "FAIL"

    # Determine final status
    if results["errors"]:
        results["status"] = "FAIL"
    elif results["warnings"] and not args.allow_warnings:
        results["status"] = "FAIL"
    elif results["warnings"]:
        results["status"] = "PASS_WITH_WARNINGS"
    else:
        results["status"] = "PASS"

    _output(results, args.json)
    sys.exit(0 if results["status"] in ("PASS", "PASS_WITH_WARNINGS") else 1)


def _output(results, use_json):
    if use_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"STATUS: {results['status']}")
        print()
        print("Checks:")
        for check, status in results["checks"].items():
            print(f"  {check}: {status}")
        print()
        if results["warnings"]:
            print("Warnings:")
            for w in results["warnings"]:
                print(f"  - {w}")
            print()
        if results["errors"]:
            print("Errors:")
            for e in results["errors"]:
                print(f"  - {e}")
            print()


if __name__ == "__main__":
    main()
