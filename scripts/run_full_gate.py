#!/usr/bin/env python3
"""Unified full gate runner for hermes-knowledge-base.

Runs every smoke / check / audit step in a fixed order, captures per-step
metrics, and reports clean working-tree state at the end.

Usage:
    python3 scripts/run_full_gate.py                 # full mode (default)
    python3 scripts/run_full_gate.py --quick         # quick subset
    python3 scripts/run_full_gate.py --json          # machine-readable
    python3 scripts/run_full_gate.py --output PATH   # write JSON report
    python3 scripts/run_full_gate.py --fail-fast     # stop on first FAIL
    python3 scripts/run_full_gate.py --no-update-site# skip update_site.py
    python3 scripts/run_full_gate.py --list          # dry-run plan, no execution

Exit codes:
    0 - all PASS (or PASS_WITH_WARNINGS)
    1 - any FAIL or FAILED_CLEANLINESS

This runner does NOT push. Tag/check operations are read-only.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).parent.parent.resolve()
TAIL_LINES = 30  # tail of stdout/stderr per step to keep JSON small

# Step definition: (name, command-list, timeout-seconds)
# Both full and quick modes share the same step tuple shape.
FULL_STEPS = [
    ("py_compile", ["python3", "-m", "py_compile", "scripts/audit_kb_state.py", "scripts/build_index.py", "scripts/check_kb.py", "scripts/check_pages_sync.py", "scripts/check_release_tags.py", "scripts/check_release_assets.py", "scripts/check_task_postflight.py", "scripts/check_task_preflight.py", "scripts/check_tracks.py", "scripts/check_translation_residue.py", "scripts/export_site_data.py", "scripts/generate_item_pages.py", "scripts/sync_pages_docs.py", "scripts/update_site.py"], 120),
    ("run_smoke_tests", ["python3", "tests/run_smoke_tests.py"], 300),
    ("run_wechat_batch_smoke", ["python3", "tests/run_wechat_batch_smoke.py"], 300),
    ("run_item_render_smoke", ["python3", "tests/run_item_render_smoke.py"], 300),
    ("run_image_localization_smoke", ["python3", "tests/run_image_localization_smoke.py"], 300),
    ("run_material_router_smoke", ["python3", "tests/run_material_router_smoke.py"], 300),
    ("run_web_article_smoke", ["python3", "tests/run_web_article_smoke.py"], 300),
    ("run_youtube_import_smoke", ["python3", "tests/run_youtube_import_smoke.py"], 300),
    ("run_fetch_layer_smoke", ["python3", "tests/run_fetch_layer_smoke.py"], 300),
    ("run_pdf_import_smoke", ["python3", "tests/run_pdf_import_smoke.py"], 300),
    ("run_release_assets_smoke", ["python3", "tests/run_release_assets_smoke.py"], 300),
    ("check_release_assets", ["python3", "scripts/check_release_assets.py"], 120),
    ("check_kb", ["python3", "scripts/check_kb.py"], 120),
    ("update_site", ["python3", "scripts/update_site.py"], 300),
    ("audit_kb_state", ["python3", "scripts/audit_kb_state.py"], 120),
    ("check_pages_sync", ["python3", "scripts/check_pages_sync.py"], 120),
]

QUICK_STEPS = [
    ("py_compile", ["python3", "-m", "py_compile", "scripts/check_kb.py", "scripts/check_pages_sync.py", "scripts/check_release_assets.py", "scripts/check_release_tags.py"], 120),
    ("run_material_router_smoke", ["python3", "tests/run_material_router_smoke.py"], 300),
    ("run_pdf_import_smoke", ["python3", "tests/run_pdf_import_smoke.py"], 300),
    ("run_release_assets_smoke", ["python3", "tests/run_release_assets_smoke.py"], 300),
    ("check_release_assets", ["python3", "scripts/check_release_assets.py"], 120),
    ("check_kb", ["python3", "scripts/check_kb.py"], 120),
    ("check_pages_sync", ["python3", "scripts/check_pages_sync.py"], 120),
]


def tail_text(text: str, max_lines: int = TAIL_LINES) -> str:
    """Return last `max_lines` lines of text (handles None and empty)."""
    if not text:
        return ""
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    return "\n".join(lines[-max_lines:])


def run_step(name: str, cmd: List[str], timeout: int, cwd: str) -> dict:
    """Run a single shell step and capture diagnostics."""
    started = time.time()
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        elapsed = time.time() - started
        stdout_tail = tail_text(result.stdout)
        stderr_tail = tail_text(result.stderr)
        exit_code = result.returncode
        status = "PASS" if exit_code == 0 else "FAIL"

        # Parse output for PASS_WITH_WARNINGS signals.
        # We treat "PASS_WITH_WARNINGS" in stdout as PASS-with-note, not FAIL.
        combined = stdout_tail + stderr_tail
        is_pww = (
            exit_code == 0
            and "STATUS: PASS_WITH_WARNINGS" in combined
        )

        return {
            "name": name,
            "command": " ".join(cmd),
            "exit_code": exit_code,
            "duration_seconds": round(elapsed, 2),
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
            "status": "PASS_WITH_WARNINGS" if is_pww else status,
        }
    except subprocess.TimeoutExpired:
        elapsed = time.time() - started
        return {
            "name": name,
            "command": " ".join(cmd),
            "exit_code": -1,
            "duration_seconds": round(elapsed, 2),
            "stdout_tail": "",
            "stderr_tail": f"step timed out after {timeout}s",
            "status": "FAIL",
            "timed_out": True,
        }
    except Exception as e:
        elapsed = time.time() - started
        return {
            "name": name,
            "command": " ".join(cmd),
            "exit_code": -1,
            "duration_seconds": round(elapsed, 2),
            "stdout_tail": "",
            "stderr_tail": f"step exception: {e!r}",
            "status": "FAIL",
        }


def check_working_tree_cleanliness() -> dict:
    """After all gates, check that tracked working tree is clean."""
    info: dict = {
        "tracked_dirty_files": [],
        "untracked_files": [],
        "diff_stat": "",
    }
    # git status --short
    try:
        s_proc = subprocess.run(
            ["git", "status", "--short"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, check=False,
        )
        status_output = s_proc.stdout.rstrip("\n")
    except Exception as e:
        info["diff_stat"] = f"git status failed: {e!r}"
        return info

    for line in (status_output or "").splitlines():
        line = line.rstrip()
        if not line or len(line) < 4 or line[2] != " ":
            continue
        x, y = line[0], line[1]
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip('"')
        if x == "?" and y == "?":
            info["untracked_files"].append(path)
        else:
            info["tracked_dirty_files"].append(f"{x}{y} {path}")

    # git diff --stat (staged + unstaged compared to HEAD)
    try:
        d_proc = subprocess.run(
            ["git", "diff", "--stat"],
            cwd=str(REPO_ROOT), capture_output=True, text=True, check=False,
        )
        info["diff_stat"] = d_proc.stdout.rstrip("\n")
    except Exception:
        pass

    return info


def evaluate_cleanliness(clean_info: dict) -> str:
    """Decide if working tree is clean enough."""
    tracked = clean_info.get("tracked_dirty_files", [])
    if tracked:
        return "FAILED_CLEANLINESS"
    return "PASS"


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full hermes-knowledge-base gate suite")
    parser.add_argument("--quick", action="store_true", help="Run quick subset only")
    parser.add_argument("--json", action="store_true", help="Output JSON report")
    parser.add_argument("--output", type=str, help="Write JSON report to file")
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first FAIL")
    parser.add_argument("--no-update-site", action="store_true",
                        help="Skip update_site step")
    parser.add_argument("--list", action="store_true",
                        help="Print planned steps as JSON and exit (no execution)")
    parser.add_argument("--cwd", type=str, default=str(REPO_ROOT),
                        help="Working directory (default: repo root)")
    args = parser.parse_args()

    if args.quick:
        steps = list(QUICK_STEPS)
    else:
        steps = list(FULL_STEPS)

    if args.no_update_site:
        steps = [(n, c, t) for (n, c, t) in steps if n != "update_site"]

    # --list: dry-run plan, exit immediately with JSON plan (no execution)
    if args.list:
        plan = {
            "mode": "quick" if args.quick else "full",
            "step_count": len(steps),
            "steps": [
                {"name": n, "command": " ".join(c), "timeout_seconds": t}
                for (n, c, t) in steps
            ],
        }
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        sys.exit(0)

    started = time.time()
    results: List[dict] = []

    if not args.json:
        print(f"Running {'quick' if args.quick else 'full'} gate suite "
              f"({len(steps)} steps)...")
        print(f"Repo: {args.cwd}")
        print(f"Fail-fast: {args.fail_fast}")
        print()

    for (name, cmd, timeout) in steps:
        if not args.json:
            print(f"[{name}] ... ", end="", flush=True)
        res = run_step(name, cmd, timeout, args.cwd)
        results.append(res)
        if not args.json:
            status = res["status"]
            dur = res["duration_seconds"]
            print(f"{status} ({dur}s, exit={res['exit_code']})")
            if res["status"] != "PASS" and not args.fail_fast:
                # Print brief stdout tail for context
                tail = res["stdout_tail"]
                if tail:
                    print(f"  --- output tail ---\n  {tail.splitlines()[-3][0:200] if tail.splitlines() else ''}")

        if args.fail_fast and res["status"] not in ("PASS", "PASS_WITH_WARNINGS"):
            if not args.json:
                print(f"\n[fail-fast] stopped at step {name}")
            break

    elapsed = time.time() - started

    # Working tree cleanliness check
    if not args.json:
        print()
        print("[working_tree] checking cleanliness...")
    clean_info = check_working_tree_cleanliness()
    clean_status = evaluate_cleanliness(clean_info)

    passed = sum(1 for r in results if r["status"] == "PASS")
    pww = sum(1 for r in results if r["status"] == "PASS_WITH_WARNINGS")
    failed_steps = [r for r in results if r["status"] == "FAIL"]

    # Final status logic
    if failed_steps:
        final_status = "FAILED_GATE"
    elif clean_status == "FAILED_CLEANLINESS":
        final_status = "FAILED_CLEANLINESS"
    elif pww > 0:
        final_status = "PASS_WITH_WARNINGS"
    else:
        final_status = "PASS"

    report = {
        "status": final_status,
        "mode": "quick" if args.quick else "full",
        "total_steps": len(results),
        "passed": passed,
        "passed_with_warnings": pww,
        "failed": len(failed_steps),
        "total_duration_seconds": round(elapsed, 2),
        "failed_step_names": [r["name"] for r in failed_steps],
        "steps": results,
        "working_tree": {
            **clean_info,
            "status": clean_status,
        },
    }

    if args.json:
        out = json.dumps(report, indent=2, ensure_ascii=False)
        if args.output:
            out_path = Path(args.output)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(out, encoding="utf-8")
            print(f"JSON report written: {args.output}")
        else:
            print(out)
    else:
        print()
        print("=" * 60)
        print(f"STATUS: {final_status}")
        print("=" * 60)
        print(f"Steps: {passed + pww}/{len(results)} passed "
              f"(+{pww} with warnings, {len(failed_steps)} failed)")
        print(f"Total duration: {elapsed:.1f}s")
        print(f"Working tree: {clean_status}")
        if clean_info.get("tracked_dirty_files"):
            print(f"  Tracked dirty: {len(clean_info['tracked_dirty_files'])} file(s)")
            for f in clean_info["tracked_dirty_files"][:10]:
                print(f"    {f}")
        if clean_info.get("untracked_files"):
            print(f"  Untracked: {len(clean_info['untracked_files'])} file(s) "
                  f"(informational, not a gate failure)")
        if failed_steps:
            print()
            print("Failed steps:")
            for r in failed_steps:
                print(f"  - {r['name']} (exit={r['exit_code']})")
                if r["stderr_tail"]:
                    first = r["stderr_tail"].splitlines()[-1] if r["stderr_tail"].splitlines() else ""
                    if first:
                        print(f"    stderr tail: {first[:200]}")

    sys.exit(0 if final_status in ("PASS", "PASS_WITH_WARNINGS") else 1)


if __name__ == "__main__":
    main()
