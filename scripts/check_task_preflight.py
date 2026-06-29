#!/usr/bin/env python3
"""Task preflight checker — validates repo state before starting work.

Usage:
    python3 scripts/check_task_preflight.py
    python3 scripts/check_task_preflight.py --planned-tag v0.3.38-task-name
    python3 scripts/check_task_preflight.py --allow-warnings --planned-tag v0.3.38-task-name
    python3 scripts/check_task_preflight.py --classify-dirty          # see working-tree dirty buckets
    python3 scripts/check_task_preflight.py --classify-dirty --json  # machine-readable

Exit codes:
    0 - PASS or PASS_WITH_WARNINGS (with --allow-warnings)
    1 - FAIL (repo dirty, tag exists, version conflict, etc.)

Flags:
    --planned-tag NAME         Verify the planned tag is unused and the minor matches recommended.
    --allow-warnings           Treat PASS_WITH_WARNINGS as an acceptable end state (exit 0).
    --classify-dirty           Instead of FAILing on dirty tree, classify the dirty entries and
                               downgrade to PASS_WITH_WARNINGS if every dirty entry is in an
                               external / non-task bucket (e.g. pre-existing reports/*.md SHA
                               backfills from another session). Default strict behavior is
                               preserved: omitting this flag still FAILs on any dirty tree.
    --skip-heavy-checks        Skip scripts/check_tracks.py (saves ~10s).
    --json                     Emit machine-readable JSON.

Notes (v0.3.66+):
    - --classify-dirty NEVER auto-stages, auto-restores, auto-commits, or auto-`git add`s
      anything. It only classifies.
    - The default strict gate is preserved as the recommended gate for new agents; --classify-dirty
      is for triage and audit trails only.
    - When --classify-dirty is set and all dirty entries are classified as "external / non-task"
      (e.g. pre-existing dirty files under reports/ that this task will not stage), the gate
      emits PASS_WITH_WARNINGS rather than FAIL.
    - When --classify-dirty is set AND any dirty file looks task-relevant (e.g. README.md,
      scripts/*.py, content/*, site/*, docs/*), the gate falls back to FAIL to mirror the
      strict default — operating on dirty work that looks self-introduced is unsafe under
      this flag.
    - JSON output includes a `dirty_classification` block when --classify-dirty is set, with
      per-entry buckets.
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


# Paths whose modifications are considered "self-introduced / task-relevant" by the
# --classify-dirty heuristic. If any dirty entry hits one of these prefixes, the gate does
# NOT downgrade to PASS_WITH_WARNINGS — it stays at strict FAIL.
_TASK_RELEVANT_PATH_PREFIXES = (
    "README.md",
    "CLAUDE.md",
    "CHANGELOG.md",
    "DESIGN_RATIONALE.md",
    "content/",
    "site/",
    "docs/",
    "scripts/",
    "templates/",
    "inbox/",
    "memory/",  # v0.3.68+: memory/ is task-relevant; was missing and caused false-EXTERNAL
    "docs/releases/",  # v0.3.68+: per-version release notes are task-relevant
)

# Heuristic: a historical "reports/*.md SHA backfill" pattern is a single-line edit where
# the diff replaces a `待完成` / `TBD` / `pending` placeholder with a 7-40 char hex SHA, often
# in the table row that carries `| **新 Commit** | ...` style content. We use a simple count
# of SHA-shaped tokens added across `git diff <path>` to flag external SHA backfills.
_SHA_TOKEN_RE = re.compile(r"\b[0-9a-f]{7,40}\b")
_BACKFILL_PLACEHOLDER_RE = re.compile(r"待完成|TBD|PENDING|pending|\.\.\.")


def classify_dirty_entries(status_output):
    """Classify porcelain git status --short output.

    Returns a dict with:
      - entries:                list of {status, path, bucket} (one per status line)
      - counts_by_bucket:       {bucket: int}
      - has_self_introduced:    bool (True iff any entry is "task-relevant")
      - summary:                human-readable summary string
    Buckets:
      - "staged"             : porcelain XY in {M,A,D,R,C} and uppercase stage letter
      - "unstaged"           : porcelain Y in lowercase (index modification / deletion) but X is space
      - "untracked"          : "??" prefix
      - "report-external-sha-backfill" : under reports/*.md path AND diff looks like a SHA backfill
      - "report-other"       : under reports/*.md path but not classified as SHA backfill
      - "other-external"     : anything not covered by the above (probably task-irrelevant too)
      - "task-relevant"      : path matches _TASK_RELEVANT_PATH_PREFIXES
    Note: an entry's bucket is the most-specific classification. An entry under reports/*.md
    whose diff also matches the SHA-backfill heuristic gets bucket="report-external-sha-backfill",
    NOT "report-other". A README.md entry is always bucket="task-relevant".
    """
    entries = []
    counts = {}
    has_self = False

    for line in (status_output or "").splitlines():
        line = line.rstrip()
        if not line:
            continue
        # Porcelain v1 format: XY<SP>PATH (where <SP> is a literal space, not whitespace)
        if len(line) < 4 or line[2] != " ":
            # Skip malformed lines; shouldn't happen in normal `git status --short` output.
            continue
        x = line[0]
        y = line[1]
        path = line[3:].strip()
        # For renames/copies, take the right side ("path1 -> path2"), take path2.
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip('"')

        # Bucket assignment: most-specific first.
        bucket = None

        # 1. Path-prefix based: README / scripts / content / ... → always task-relevant.
        if any(path == p or path.startswith(p) for p in _TASK_RELEVANT_PATH_PREFIXES):
            bucket = "task-relevant"

        # 2. reports/*.md + SHA backfill heuristic → external SHA backfill
        if bucket is None and path.startswith("reports/") and path.endswith(".md"):
            # Run a small diff to count SHA-token insertions. This is best-effort; if git
            # fails for any reason, fall back to "report-other".
            try:
                diff_out = subprocess.run(
                    ["git", "diff", "--", path],
                    capture_output=True, text=True, check=False,
                ).stdout
                added_sha_hits = 0
                removed_placeholder_hits = 0
                for dline in diff_out.splitlines():
                    if dline.startswith("+") and not dline.startswith("+++"):
                        added_sha_hits += len(_SHA_TOKEN_RE.findall(dline))
                    elif dline.startswith("-") and not dline.startswith("---"):
                        removed_placeholder_hits += len(_BACKFILL_PLACEHOLDER_RE.findall(dline))
                if added_sha_hits >= 1 and removed_placeholder_hits >= 1:
                    bucket = "report-external-sha-backfill"
                else:
                    bucket = "report-other"
            except Exception:
                bucket = "report-other"

        # 3. porcelain state-tag buckets — only kicks in when no specific bucket was set
        #    by the path-prefix / reports-SHA-backfill logic above. Every branch must guard
        #    with `bucket is None` so a previously-set bucket (task-relevant / report-*) is
        #    never silently overwritten by the porcelain fallback.
        if bucket is None:
            if x == "?" and y == "?":
                bucket = "untracked"
            elif x != " " and x != "?":
                bucket = "staged"
            elif y != " " and y != "?":
                bucket = "unstaged"
            else:
                bucket = "other-external"

        # has_self_introduced: task-relevant always counts.
        if bucket == "task-relevant":
            has_self = True

        entries.append({
            "status": line[:2],
            "path": path,
            "bucket": bucket,
        })
        counts[bucket] = counts.get(bucket, 0) + 1

    return {
        "entries": entries,
        "counts_by_bucket": counts,
        "has_self_introduced": has_self,
        "summary": _format_summary(counts, has_self),
    }


def _format_summary(counts, has_self):
    if not counts:
        return "working tree clean"
    parts = [f"{bucket}={n}" for bucket, n in sorted(counts.items())]
    sigil = "SELF" if has_self else "EXTERNAL"
    return f"{sigil}: " + ", ".join(parts)


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
    parser.add_argument(
        "--classify-dirty",
        action="store_true",
        help=(
            "v0.3.66+: instead of FAILing on a dirty working tree, classify each dirty entry "
            "and downgrade to PASS_WITH_WARNINGS when every entry is in an external bucket "
            "(e.g. pre-existing reports/*.md SHA backfills from another session). When any entry "
            "is task-relevant (README.md, scripts/*, content/*, site/*, docs/*), the gate "
            "still FAILs to mirror strict default. Never auto-stages or auto-restores."
        ),
    )
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

    # 2. Check git status — strict default: any dirty → FAIL.
    #    v0.3.66+: --classify-dirty downgrades to PASS_WITH_WARNINGS iff every entry is
    #    classified as external / non-task; it NEVER auto-stages anything.
    #    NB: do NOT use run_git(..., check=False).strip() here, because .strip() removes the
    #    leading space of ` M` (unstaged modification) porcelain entries, silently corrupting
    #    the first line of every dirty tree. We want raw status output, trailing newline excepted.
    try:
        _status_proc = subprocess.run(
            ["git", "status", "--short"],
            capture_output=True, text=True, check=False,
        )
        status_output = _status_proc.stdout.rstrip("\n")
    except FileNotFoundError:
        status_output = None
    if status_output:
        if args.classify_dirty:
            classification = classify_dirty_entries(status_output)
            results["checks"]["git_status"] = "PASS_WITH_WARNINGS"
            results["checks"]["git_status_classification"] = classification["summary"]
            results["dirty_classification"] = classification
            if classification["has_self_introduced"]:
                results["errors"].append(
                    "Working tree dirty (classify mode): SELF-introduced files present.\n"
                    + status_output
                    + "\nClassification: " + classification["summary"]
                )
                results["status"] = "FAIL"
            else:
                results["warnings"].append(
                    "Working tree dirty but all entries are EXTERNAL (pre-existing / not this task). "
                    "Classified: " + classification["summary"]
                    + "\n" + status_output
                    + "\nNo auto-stage, no auto-restore, no auto-commit. Carry on cautiously."
                )
        else:
            results["errors"].append(f"Working tree dirty:\n{status_output}")
            results["status"] = "FAIL"
    else:
        results["checks"]["git_status"] = "PASS"

    # 3. Check HEAD vs origin/main — strict default: any divergence → FAIL.
    #    v0.3.68+: also record a divergence summary in the results so agents and humans
    #    can read the local-vs-remote state from the JSON. Default strict behavior is
    #    preserved: omitting --classify-dirty still FAILs on any divergence.
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

    # 3b. Divergence summary (v0.3.68+) — read-only. NEVER auto-resolves; if HEAD diverges
    #     from origin/main, the agent must follow the spec'd decision tree (see
    #     docs/AGENT_COMMANDS.md §"Task-startup divergence check"):
    #       a. local ahead AND ahead is in current task plan   → continue, record
    #       b. local ahead AND ahead is external session work  → stop, ask user
    #       c. origin ahead local AND working tree is clean    → git pull --ff-only
    #       d. diverged                                        → stop, ask user
    #     No automatic merge/rebase/reset/force-push from this script.
    try:
        _head = head or run_git("rev-parse", "HEAD", check=False)
        _origin = origin_head or run_git("rev-parse", "origin/main", check=False)
        if _head and _origin:
            _merge_base = subprocess.run(
                ["git", "merge-base", _head, _origin],
                capture_output=True, text=True, check=False,
            ).stdout.strip() or None
            _ahead_behind = subprocess.run(
                ["git", "rev-list", "--left-right", "--count", f"{_head}...{_origin}"],
                capture_output=True, text=True, check=False,
            ).stdout.strip()  # e.g. "0\t0" or "1\t2"
            _ahead, _behind = (0, 0)
            if _ahead_behind and "\t" in _ahead_behind:
                _ahead, _behind = (int(x) for x in _ahead_behind.split("\t"))
            results["git_divergence"] = {
                "head": _head,
                "origin_main": _origin,
                "merge_base": _merge_base,
                "ahead_count": _ahead,
                "behind_count": _behind,
                "is_diverged": bool(_ahead and _behind),
                "is_ahead": bool(_ahead and not _behind),
                "is_behind": bool(_behind and not _ahead),
                "is_synced": bool(not _ahead and not _behind),
            }
        else:
            results["git_divergence"] = {
                "head": _head,
                "origin_main": _origin,
                "merge_base": None,
                "ahead_count": None,
                "behind_count": None,
                "is_diverged": None,
                "is_ahead": None,
                "is_behind": None,
                "is_synced": None,
            }
    except Exception as _e:
        # Never let the divergence-summary probe break preflight.
        results["git_divergence"] = {"error": repr(_e)}

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
