#!/usr/bin/env python3
"""Task postflight checker — validates a task report file against a profile.

This is the post-write counterpart to scripts/check_task_preflight.py:

  check_task_preflight.py  →  run BEFORE the task starts (T0): git state,
                              planned tag, gate scripts exist / PASS.
  check_task_postflight.py →  run AFTER the task ends (T1): the report
                              file is structurally aligned with the chosen
                              profile, contains the required segments, and
                              (for publish profile) references a real commit
                              and a live verification step.

The two scripts are intentionally separate. Preflight is "before-task"
state; postflight is "after-task" report shape. They do not share
exit-code semantics, do not share profiles, and do not call each other.

USAGE

    python3 scripts/check_task_postflight.py \
        --report-file reports/<task>.md \
        --profile publish

    python3 scripts/check_task_postflight.py \
        --report-file reports/<task>.md \
        --profile auto --json

    python3 scripts/check_task_postflight.py \
        --report-file reports/<task>.md \
        --profile publish --strict

PROFILES

    readonly       — template 1 (3 segments: STATUS, Scope, Evidence)
    write_local    — template 2 (5 segments, no push, no live)
    publish        — template 3 (9 segments, with commit + push + live)
    article_import — legacy article_import_<slug>_<date>.md format
    versioned      — legacy v0.3.x 7-segment constraint reports
    auto           — infer from filename / heading

DEFAULT BEHAVIOR

    WARN-only: missing required segments are reported as warnings, the
    script exits 0. This is the explicit safe default per the planning
    assessment (2026-06-27 WARN). Pass --strict to make missing required
    segments return a non-zero exit code (FAIL).

    The script does NOT scan the reports/ directory on its own. You must
    pass --report-file explicitly. This avoids silent re-evaluation of
    legacy reports.

EXIT CODES

    0  — PASS or PASS_WITH_WARNINGS
    1  — FAIL (only reachable with --strict, or when --report-file is
          missing and no --json is requested)
    2  — uncaught exception / malformed input

DEPENDENCIES

    Pure stdlib (argparse, json, re, sys, pathlib). No third-party deps.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Status words recognized in STATUS segments (REPORTING_TEMPLATE §2)
# ---------------------------------------------------------------------------
STATUS_WORDS = (
    "PASS",
    "WARN",
    "FAIL",
    "PENDING_CDN_SYNC",
    "RESOLVED",
)

# Action tags (REPORTING_TEMPLATE §3)
ACTION_TAGS = ("[READ-ONLY]", "[WRITE]", "[GENERATE]", "[PUSH]", "[LIVE]")

# Lifecycle markers (REPORTING_TEMPLATE §3)
LIFECYCLE_MARKERS = ("proposed", "applied", "pushed", "live")


# ---------------------------------------------------------------------------
# Segment extraction
# ---------------------------------------------------------------------------

# Match H2 (`## `) and H3 (`### `) headings. H4+ are ignored for the
# segment map. We deliberately do NOT require a specific prefix (e.g.
# "1. STATUS") — section names are matched against the profile's expected
# set with case-insensitive comparison and a small alias table.
H_HEADING = re.compile(r"^(#{2,3})\s+(.+?)\s*$", re.MULTILINE)


def extract_segments(text: str) -> dict:
    """Return {normalized_segment_name: raw_heading_line} for every H2/H3.

    Normalization rules:
      * lowercase
      * strip leading numeric / bullet prefixes ("1.", "2)", "-", "*", "§")
      * strip trailing colon and whitespace
      * collapse internal whitespace
    """
    segments: dict = {}
    for match in H_HEADING.finditer(text):
        heading = match.group(2).strip()
        normalized = _normalize_heading(heading)
        if normalized:
            segments[normalized] = heading
    return segments


def _normalize_heading(heading: str) -> str:
    # Strip leading numbering / bullets / sections
    s = re.sub(r"^[\s§]*[\-•\.\)]*\s*\d*[\.\)]*\s*", "", heading)
    s = s.strip().rstrip(":")
    s = re.sub(r"\s+", " ", s)
    return s.lower()


# Aliases let one profile accept multiple phrasings for the same segment.
# Keep aliases lowercase.
SEGMENT_ALIASES = {
    "status": ("status", "状态", "task status"),
    "scope": ("scope", "boundaries", "范围"),
    "actions": (
        "actions",
        "actions taken",
        "what was done",
        "动作",
        "操作",
    ),
    "evidence": ("evidence", "proof", "验证", "证据"),
    "checks": ("checks", "quality checks", "check results", "check 结果"),
    "files changed": (
        "files changed",
        "files written",
        "files modified",
        "files updated",
        "files 改动",
        "file diff",
        "git diff",
        "changed files",
    ),
    "known limitations": (
        "known limitations",
        "limitations",
        "已知限制",
        "restrictions",
    ),
    "next action": (
        "next action",
        "next steps",
        "follow up",
        "followup",
        "next",
        "后续",
    ),
    "summary": ("summary", "executive summary", "概述", "简介"),
    "pipeline execution": (
        "pipeline execution",
        "execution",
        "pipeline",
        "执行",
    ),
    "final state": ("final state", "outcome", "end state", "最终状态"),
    "constraints honored": (
        "constraints honored",
        "constraints",
        "约束",
    ),
    "starting state": (
        "starting state",
        "initial state",
        "起始状态",
        "初始状态",
    ),
    "generated diff": (
        "generated diff",
        "diff",
    ),
    "links": ("links", "references", "链接"),
}


def _find_segment_alias(segments: dict, alias_group_name: str) -> str | None:
    """Return the raw heading line that matches any alias in the given group,
    or None if not present."""
    aliases = SEGMENT_ALIASES.get(alias_group_name, (alias_group_name,))
    aliases_lc = tuple(a.lower() for a in aliases)
    for seg_lc, raw in segments.items():
        if seg_lc in aliases_lc:
            return raw
    return None


# ---------------------------------------------------------------------------
# Per-profile checks
# ---------------------------------------------------------------------------


def _has_status_word(text: str) -> bool:
    """Any of the canonical status words appear in the report."""
    text_lc = text.lower()
    return any(w.lower() in text_lc for w in STATUS_WORDS)


def _has_any_action_tag(text: str) -> bool:
    return any(tag in text for tag in ACTION_TAGS)


def _has_commit_reference(text: str) -> bool:
    """Loose check: a 40-char hex or 7+ char short SHA appears somewhere."""
    return bool(
        re.search(r"\b[0-9a-f]{40}\b", text, re.IGNORECASE)
        or re.search(r"\b[0-9a-f]{7,12}\b", text, re.IGNORECASE)
    )


def _has_push_reference(text: str) -> bool:
    return bool(
        re.search(r"\bgit\s+push\b", text, re.IGNORECASE)
        or "push range" in text.lower()
        or "push status" in text.lower()
    )


def _has_live_reference(text: str) -> bool:
    return bool(
        "live" in text.lower()
        or "cdn" in text.lower()
        or "byte-identical" in text.lower()
        or re.search(r"curl\s+", text, re.IGNORECASE) is not None
    )


def _check_readonly(text: str, segments: dict) -> tuple[list, list, list]:
    checks: list = []
    warnings: list = []
    errors: list = []
    has_status = _find_segment_alias(segments, "status") is not None
    has_scope = _find_segment_alias(segments, "scope") is not None
    has_evidence = _find_segment_alias(segments, "evidence") is not None
    has_next = _find_segment_alias(segments, "next action") is not None

    checks.append(("status_segment", "PASS" if has_status else "MISSING"))
    checks.append(("scope_segment", "PASS" if has_scope else "MISSING"))
    checks.append(("evidence_segment", "PASS" if has_evidence else "MISSING"))
    if not has_status:
        warnings.append("WARN: missing STATUS segment (readonly profile)")
    if not has_scope:
        warnings.append("WARN: missing Scope segment (readonly profile)")
    if not has_evidence:
        warnings.append("WARN: missing Evidence segment (readonly profile)")
    if not has_next:
        warnings.append("WARN: recommended Next action segment absent (readonly profile)")
    return checks, warnings, errors


def _check_write_local(text: str, segments: dict) -> tuple[list, list, list]:
    checks: list = []
    warnings: list = []
    errors: list = []
    required = (
        ("status_segment", "status"),
        ("scope_segment", "scope"),
        ("actions_segment", "actions"),
        ("files_changed_segment", "files changed"),
        ("evidence_segment", "evidence"),
    )
    for check_name, alias in required:
        present = _find_segment_alias(segments, alias) is not None
        checks.append((check_name, "PASS" if present else "MISSING"))
        if not present:
            warnings.append(
                f"WARN: missing required segment '{alias}' (write_local profile)"
            )
    if _find_segment_alias(segments, "checks") is not None:
        checks.append(("checks_segment", "PASS"))
    else:
        checks.append(("checks_segment", "OPTIONAL"))
    if _find_segment_alias(segments, "known limitations") is None:
        warnings.append(
            "WARN: recommended Known limitations segment absent (write_local profile)"
        )
    if _find_segment_alias(segments, "next action") is None:
        warnings.append(
            "WARN: recommended Next action segment absent (write_local profile)"
        )
    return checks, warnings, errors


def _check_publish(text: str, segments: dict) -> tuple[list, list, list]:
    checks: list = []
    warnings: list = []
    errors: list = []
    required_segments = (
        ("status_segment", "status"),
        ("scope_segment", "scope"),
        ("actions_segment", "actions"),
        ("files_changed_segment", "files changed"),
        ("evidence_segment", "evidence"),
        ("checks_segment", "checks"),
        ("known_limitations_segment", "known limitations"),
        ("next_action_segment", "next action"),
    )
    for check_name, alias in required_segments:
        present = _find_segment_alias(segments, alias) is not None
        checks.append((check_name, "PASS" if present else "MISSING"))
        if not present:
            warnings.append(
                f"WARN: missing required segment '{alias}' (publish profile)"
            )
    # commit / push / live presence
    has_commit = _has_commit_reference(text)
    has_push = _has_push_reference(text)
    has_live = _has_live_reference(text)
    checks.append(("commit_reference", "PASS" if has_commit else "MISSING"))
    checks.append(("push_reference", "PASS" if has_push else "MISSING"))
    checks.append(("live_reference", "PASS" if has_live else "MISSING"))
    if not has_commit:
        warnings.append("WARN: no commit hash detected (publish profile)")
    if not has_push:
        warnings.append("WARN: no push reference detected (publish profile)")
    if not has_live:
        warnings.append("WARN: no live/CDN/curl reference detected (publish profile)")
    # status words
    if _has_status_word(text):
        checks.append(("status_word_recognized", "PASS"))
    else:
        checks.append(("status_word_recognized", "MISSING"))
        warnings.append(
            "WARN: no recognized status word "
            f"({'/'.join(STATUS_WORDS)}) found (publish profile)"
        )
    # action tags (recommended, not required)
    if _has_any_action_tag(text):
        checks.append(("action_tag_present", "PASS"))
    else:
        checks.append(("action_tag_present", "OPTIONAL"))
        warnings.append(
            "WARN: none of the 5 action tags "
            f"({', '.join(ACTION_TAGS)}) found (publish profile, recommended)"
        )
    return checks, warnings, errors


def _check_article_import(text: str, segments: dict) -> tuple[list, list, list]:
    checks: list = []
    warnings: list = []
    errors: list = []
    # Compatibility: any of these classic section names is a soft PASS.
    classic = (
        "summary",
        "pipeline execution",
        "files changed",
        "checks",
        "final state",
    )
    hits = sum(1 for key in classic if _find_segment_alias(segments, key) is not None)
    checks.append(("classic_section_match", f"{hits}/{len(classic)}"))
    if hits == 0:
        warnings.append("WARN: no classic article_import sections matched (Summary / Pipeline execution / Files written / Quality checks / Final state)")
    # STATUS is recommended but not required for legacy.
    if _find_segment_alias(segments, "status") is not None:
        checks.append(("status_segment", "PASS"))
    else:
        checks.append(("status_segment", "OPTIONAL"))
        warnings.append("WARN: legacy article_import format does not require STATUS segment (postflight only checks classic section shape)")
    return checks, warnings, errors


def _check_versioned(text: str, segments: dict) -> tuple[list, list, list]:
    checks: list = []
    warnings: list = []
    errors: list = []
    # Versioned reports use 7-12 H2 numbered sections under a top STATUS
    # line that may be H2 (`## STATUS: **PASS** ✅`) or H3.
    has_top_status = bool(
        re.search(
            r"^#{1,3}\s+status\s*:?\s*\*?\*?(pass|warn|fail|partial|noop_clean)",
            text,
            re.IGNORECASE | re.MULTILINE,
        )
    )
    has_starting_state = _find_segment_alias(segments, "starting state") is not None
    has_checks = _find_segment_alias(segments, "checks") is not None
    has_files = _find_segment_alias(segments, "files changed") is not None
    has_constraints = _find_segment_alias(segments, "constraints honored") is not None
    if has_top_status:
        checks.append(("status_segment", "PASS"))
    else:
        checks.append(("status_segment", "MISSING"))
        warnings.append("WARN: no top-level STATUS line (versioned profile, e.g. '## STATUS: **PASS** ✅')")
    for name, present in (
        ("starting_state_section", has_starting_state),
        ("checks_section", has_checks),
        ("files_changed_section", has_files),
        ("constraints_honored_section", has_constraints),
    ):
        checks.append((name, "PASS" if present else "MISSING"))
        if not present:
            warnings.append(
                f"WARN: classic versioned section '{name}' missing (versioned profile)"
            )
    return checks, warnings, errors


PROFILE_CHECKS = {
    "readonly": _check_readonly,
    "write_local": _check_write_local,
    "publish": _check_publish,
    "article_import": _check_article_import,
    "versioned": _check_versioned,
}


# ---------------------------------------------------------------------------
# Auto-detection
# ---------------------------------------------------------------------------


def auto_detect_profile(path: Path, text: str) -> str:
    """Heuristic profile selection. Never used with --strict."""
    name = path.name.lower()
    if name.startswith("article_import_"):
        return "article_import"
    if re.search(r"_v0[0-9]+", name) or "_v03" in name:
        return "versioned"
    # Heading-based heuristics
    text_lc = text.lower()[:4000]  # only first ~80 lines matter
    if "live" in text_lc and ("push" in text_lc or "commit" in text_lc):
        return "publish"
    if "files changed" in text_lc and ("push" in text_lc or "live" in text_lc):
        return "publish"
    if "files changed" in text_lc or "files written" in text_lc:
        return "write_local"
    return "readonly"


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def _output_text(result: dict) -> None:
    print(f"STATUS: {result['status']}")
    print(f"profile: {result['profile']}")
    print(f"report: {result['report']}")
    print()
    print("Checks:")
    for name, status in result["checks"]:
        print(f"  {name}: {status}")
    print()
    if result["warnings"]:
        print("Warnings:")
        for w in result["warnings"]:
            print(f"  - {w}")
        print()
    if result["errors"]:
        print("Errors:")
        for e in result["errors"]:
            print(f"  - {e}")
        print()


def _output_json(result: dict) -> None:
    print(json.dumps(result, indent=2, ensure_ascii=False))


def run_check(report_path: Path, profile: str, strict: bool) -> dict:
    """Run the profile check, return a result dict. Never raises."""
    if not report_path.exists():
        return {
            "status": "FAIL",
            "profile": profile,
            "report": str(report_path),
            "checks": [],
            "warnings": [],
            "errors": [f"report file does not exist: {report_path}"],
        }
    try:
        text = report_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = report_path.read_text(encoding="utf-8", errors="replace")

    segments = extract_segments(text)
    checker = PROFILE_CHECKS.get(profile)
    if checker is None:
        return {
            "status": "FAIL",
            "profile": profile,
            "report": str(report_path),
            "checks": [],
            "warnings": [],
            "errors": [f"unknown profile: {profile}"],
        }
    checks, warnings, errors = checker(text, segments)

    # Overall status: FAIL only if --strict AND any required-segment MISSING.
    overall = "PASS"
    if any(status == "MISSING" for _, status in checks):
        if strict:
            overall = "FAIL"
        else:
            overall = "PASS_WITH_WARNINGS"
    if errors:
        overall = "FAIL"

    return {
        "status": overall,
        "profile": profile,
        "report": str(report_path),
        "checks": checks,
        "warnings": warnings,
        "errors": errors,
    }


# ---------------------------------------------------------------------------
# Git state checks (for --expect-clean / --expect-head-origin)
# ---------------------------------------------------------------------------

import subprocess as sp


def _git_rev_parse(what: str) -> str | None:
    try:
        return sp.check_output(
            ["git", "rev-parse", what], text=True, stderr=sp.DEVNULL
        ).strip()
    except sp.CalledProcessError:
        return None


def _git_status_short() -> str:
    try:
        return sp.check_output(
            ["git", "status", "--short"], text=True, stderr=sp.DEVNULL
        ).strip()
    except sp.CalledProcessError:
        return ""


def _git_tag_exists(tag: str) -> bool:
    try:
        sp.check_output(["git", "tag", "--list", tag], text=True, stderr=sp.DEVNULL)
        return tag in sp.check_output(
            ["git", "tag", "--list", tag], text=True, stderr=sp.DEVNULL
        ).strip()
    except sp.CalledProcessError:
        return False


def _git_remote_tag_exists(tag: str) -> bool:
    try:
        output = sp.check_output(
            ["git", "ls-remote", "--tags", "origin", tag + "*"],
            text=True,
            stderr=sp.DEVNULL,
        ).strip()
        return bool(output)
    except sp.CalledProcessError:
        return False


def _git_tag_deref(tag: str) -> str | None:
    try:
        return sp.check_output(
            ["git", "rev-parse", tag + "^{}"], text=True, stderr=sp.DEVNULL
        ).strip()
    except sp.CalledProcessError:
        return None


def run_git_checks(
    expect_clean: bool,
    expect_head_origin: bool,
    tag: str | None,
    commit: str | None,
) -> tuple[list, list, list]:
    """Run git state checks, return (checks, warnings, errors)."""
    checks: list = []
    warnings: list = []
    errors: list = []

    # Git repo check
    head = _git_rev_parse("HEAD")
    checks.append(("git_repo", "PASS" if head else "FAIL"))
    if not head:
        errors.append("ERROR: not a git repo or HEAD unreadable")
        return checks, warnings, errors

    # Working tree check
    status = _git_status_short()
    is_clean = not status
    checks.append(("git_status", "PASS" if is_clean else "DIRTY"))
    if expect_clean and not is_clean:
        warnings.append(f"WARN: working tree not clean:\n{status}")
    elif not is_clean:
        warnings.append(f"WARN: working tree not clean (expected)")

    # HEAD / origin/main check
    origin_main = _git_rev_parse("origin/main")
    checks.append(("origin_main", "PASS" if origin_main else "MISSING"))
    if origin_main:
        head_matches = head == origin_main
        checks.append(("head_sync", "PASS" if head_matches else "MISMATCH"))
        if expect_head_origin and not head_matches:
            warnings.append(
                f"WARN: HEAD ({head[:8]}) != origin/main ({origin_main[:8]})"
            )
        elif not head_matches:
            warnings.append(
                f"WARN: HEAD ({head[:8]}) != origin/main ({origin_main[:8]})"
            )
    else:
        if expect_head_origin:
            warnings.append("WARN: origin/main not found")

    # Tag check
    if tag:
        local_exists = _git_tag_exists(tag)
        remote_exists = _git_remote_tag_exists(tag)
        deref = _git_tag_deref(tag)
        checks.append(("tag_local", "PASS" if local_exists else "MISSING"))
        checks.append(("tag_remote", "PASS" if remote_exists else "MISSING"))
        checks.append(("tag_deref", "PASS" if deref else "MISSING"))
        if not local_exists:
            warnings.append(f"WARN: local tag '{tag}' not found")
        if not remote_exists:
            warnings.append(f"WARN: remote tag '{tag}' not found")
        if deref and commit:
            deref_matches = deref == commit
            checks.append(("tag_commit_match", "PASS" if deref_matches else "MISMATCH"))
            if not deref_matches:
                warnings.append(
                    f"WARN: tag deref ({deref[:8]}) != expected commit ({commit[:8]})"
                )
        elif not deref:
            warnings.append(f"WARN: tag '{tag}' deref failed")

    return checks, warnings, errors


# ---------------------------------------------------------------------------
# Report field checks (for --report)
# ---------------------------------------------------------------------------

REPORT_REQUIRED_FIELDS = (
    "STATUS",
    "commit",
    "tag",
    "check_kb.py",
    "check_pages_sync.py",
    "git status",
)

REPORT_IMPORT_RECOMMENDED_FIELDS = (
    "source URL",
    "content directory",
    "GitHub Pages URL",
)

REPORT_FEATURE_RECOMMENDED_FIELDS = (
    "modified files",
    "checks",
    "tag deref",
)


def run_report_checks(report_path: Path) -> tuple[list, list, list]:
    """Check report file for required/recommended fields."""
    checks: list = []
    warnings: list = []
    errors: list = []

    if not report_path.exists():
        checks.append(("report_exists", "MISSING"))
        warnings.append(f"WARN: report file does not exist: {report_path}")
        return checks, warnings, errors

    checks.append(("report_exists", "PASS"))

    try:
        text = report_path.read_text(encoding="utf-8")
    except Exception as exc:
        checks.append(("report_readable", "FAIL"))
        errors.append(f"ERROR: cannot read report: {exc}")
        return checks, warnings, errors

    checks.append(("report_readable", "PASS"))

    text_lc = text.lower()

    # Check required fields
    missing_required = []
    for field in REPORT_REQUIRED_FIELDS:
        if field.lower() in text_lc:
            checks.append((f"report_field_{field}", "PASS"))
        else:
            checks.append((f"report_field_{field}", "MISSING"))
            missing_required.append(field)

    if missing_required:
        warnings.append(
            f"WARN: report missing required fields: {', '.join(missing_required)}"
        )

    # Check recommended fields (import)
    missing_import = []
    for field in REPORT_IMPORT_RECOMMENDED_FIELDS:
        if field.lower() in text_lc:
            checks.append((f"report_field_{field}", "PASS"))
        else:
            checks.append((f"report_field_{field}", "OPTIONAL"))
            missing_import.append(field)

    if missing_import:
        warnings.append(
            f"WARN: report missing recommended import fields: {', '.join(missing_import)}"
        )

    # Check recommended fields (feature)
    missing_feature = []
    for field in REPORT_FEATURE_RECOMMENDED_FIELDS:
        if field.lower() in text_lc:
            checks.append((f"report_field_{field}", "PASS"))
        else:
            checks.append((f"report_field_{field}", "OPTIONAL"))
            missing_feature.append(field)

    if missing_feature:
        warnings.append(
            f"WARN: report missing recommended feature fields: {', '.join(missing_feature)}"
        )

    return checks, warnings, errors


def _output_text_v2(result: dict) -> None:
    print(f"STATUS: {result['status']}")
    print(f"warnings: {result['warnings_count']}")
    print()
    print("Checks:")
    for name, status in result["checks"]:
        print(f"  {name}: {status}")
    print()
    if result["warnings"]:
        print("Warnings:")
        for w in result["warnings"]:
            print(f"  - {w}")
        print()
    if result["errors"]:
        print("Errors:")
        for e in result["errors"]:
            print(f"  - {e}")
        print()
    print("Git state:")
    print(f"  HEAD: {result.get('head', 'N/A')}")
    print(f"  origin/main: {result.get('origin_main', 'N/A')}")
    print(f"  working tree: {'clean' if result.get('git_clean') else 'dirty'}")
    print()
    print("Report:")
    print(f"  path: {result.get('report_path', 'N/A')}")
    print(f"  exists: {result.get('report_exists', 'N/A')}")
    print()
    print("Tag:")
    print(f"  tag: {result.get('tag', 'N/A')}")
    print(f"  deref: {result.get('tag_deref', 'N/A')}")
    print()
    print("Recommended action:")
    print(f"  {result.get('recommended_action', 'Review warnings above')}")


def _output_json_v2(result: dict) -> None:
    print(json.dumps(result, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Task postflight checker (WARN-only by default).",
    )
    # Legacy profile-based args
    parser.add_argument(
        "--report-file",
        help="Path to the task report file (legacy, use --report instead).",
    )
    parser.add_argument(
        "--profile",
        default="auto",
        choices=("readonly", "write_local", "publish", "article_import", "versioned", "auto"),
        help="Report profile to check against (default: auto-detect).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat missing required segments as FAIL (non-zero exit). Default is WARN-only.",
    )
    # New v0.3.41 args
    parser.add_argument(
        "--report",
        help="Path to the task report file (v0.3.41+).",
    )
    parser.add_argument(
        "--tag",
        help="Tag name to verify (v0.3.41+).",
    )
    parser.add_argument(
        "--commit",
        help="Expected commit hash for tag deref (v0.3.41+).",
    )
    parser.add_argument(
        "--expect-clean",
        action="store_true",
        help="Warn if working tree is not clean (v0.3.41+).",
    )
    parser.add_argument(
        "--expect-head-origin",
        action="store_true",
        help="Warn if HEAD != origin/main (v0.3.41+).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of the default text report.",
    )
    args = parser.parse_args()

    # Determine report path (prefer --report over --report-file)
    report_path_str = args.report or args.report_file
    if not report_path_str:
        msg = "ERROR: --report is required. The script does not scan reports/ on its own."
        if args.json:
            print(json.dumps({"status": "FAIL", "errors": [msg]}, indent=2))
        else:
            print(msg, file=sys.stderr)
            parser.print_usage(sys.stderr)
        return 1

    report_path = Path(report_path_str).resolve()

    # Run git state checks
    git_checks, git_warnings, git_errors = run_git_checks(
        expect_clean=args.expect_clean,
        expect_head_origin=args.expect_head_origin,
        tag=args.tag,
        commit=args.commit,
    )

    # Run report checks
    report_checks, report_warnings, report_errors = run_report_checks(report_path)

    # Combine all checks
    all_checks = git_checks + report_checks
    all_warnings = git_warnings + report_warnings
    all_errors = git_errors + report_errors

    # Determine status
    if all_errors:
        status = "FAIL"
    elif all_warnings:
        status = "PASS_WITH_WARNINGS"
    else:
        status = "PASS"

    # Build result
    head = _git_rev_parse("HEAD")
    origin_main = _git_rev_parse("origin/main")
    tag_deref = _git_tag_deref(args.tag) if args.tag else None

    result = {
        "status": status,
        "warnings_count": len(all_warnings),
        "checks": all_checks,
        "warnings": all_warnings,
        "errors": all_errors,
        "head": head,
        "origin_main": origin_main,
        "git_clean": not _git_status_short(),
        "report_path": str(report_path),
        "report_exists": report_path.exists(),
        "tag": args.tag,
        "tag_deref": tag_deref,
        "recommended_action": (
            "Review warnings above and consider fixing before next task"
            if all_warnings
            else "All checks passed, no action needed"
        ),
    }

    if args.json:
        _output_json_v2(result)
    else:
        _output_text_v2(result)

    # WARN-only: only fail on errors, not warnings
    if all_errors:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001
        print(f"UNCAUGHT EXCEPTION: {exc!r}", file=sys.stderr)
        sys.exit(2)
