"""Build the static site (with hard-stop on quality gate + post-sync check).

Pipeline order (HARD-STOP at the first step):

  1. scripts/check_kb.py            ← quality gate
  2. scripts/build_index.py
  3. scripts/export_site_data.py
  4. scripts/generate_item_pages.py
  5. scripts/sync_pages_docs.py
  6. scripts/check_pages_sync.py    ← post-sync integrity check

If `check_kb.py` exits non-zero, `update_site.py` MUST return non-zero
without running any of the build/export/generate/sync steps. This is the
quality gate enforcement: a broken catalog must never be published to
`site/data/catalog.json` or `docs/`.

If `check_pages_sync.py` exits non-zero (after sync_pages_docs.py ran
successfully), that means `site/` and `docs/` are out of sync — typically
because `git add` skipped a synced docs/ file. `update_site.py` MUST return
non-zero so the operator catches the drift before committing.
"""

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Quality gate first — every later step depends on the KB being healthy.
QUALITY_GATE = "scripts/check_kb.py"

# Build / export / generate / sync chain (in order).
BUILD_CHAIN = [
    "scripts/build_index.py",
    "scripts/export_site_data.py",
    "scripts/generate_item_pages.py",
    "scripts/sync_pages_docs.py",
]

# Post-sync integrity check. Runs AFTER sync_pages_docs.py so the check
# sees the freshly synced files. If check_pages_sync.py fails, the publish
# surface (docs/) and the dev surface (site/) are inconsistent — refuse
# to declare success.
POST_SYNC_CHECK = "scripts/check_pages_sync.py"


def run_script(path: str) -> bool:
    print(f"\n{'=' * 50}")
    print(f"Running: {path}")
    print(f"{'=' * 50}")
    result = subprocess.run([sys.executable, path], cwd=REPO_ROOT)
    return result.returncode == 0


def update_site() -> int:
    # ---------------------------------------------------------------
    # HARD-STOP: quality gate (check_kb.py) must pass first.
    # If it fails, no build/export/generate/sync runs and we exit 1.
    # ---------------------------------------------------------------
    print(f"\n{'#' * 50}")
    print("# STEP 0/5: Quality gate (check_kb.py)")
    print(f"{'#' * 50}")
    gate_ok = run_script(QUALITY_GATE)
    if not gate_ok:
        print(f"\n{'!' * 50}")
        print(f"! HARD-STOP: {QUALITY_GATE} FAILED.")
        print("! The knowledge base has integrity issues. Refusing to:")
        print("!   - rebuild index/catalog.jsonl")
        print("!   - regenerate site/data/catalog.json")
        print("!   - generate site/items/ detail pages")
        print("!   - sync to docs/")
        print("!")
        print("! Fix the issues reported above, then re-run update_site.py.")
        print(f"{'!' * 50}")
        return 1

    # ---------------------------------------------------------------
    # Build chain (only reachable if the quality gate passed).
    # ---------------------------------------------------------------
    total = len(BUILD_CHAIN) + 1  # +1 for the post-sync check
    for i, script in enumerate(BUILD_CHAIN, start=1):
        if not run_script(script):
            print(f"\nFAILED: {script}")
            print(f"\n{'=' * 50}")
            print("Some steps failed. Review output above.")
            print(f"{'=' * 50}")
            return 1
        print(f"[{i}/{total}] {script} OK")

    # ---------------------------------------------------------------
    # Post-sync integrity check. Detects site/ ↔ docs/ drift that would
    # leave GitHub Pages serving stale files.
    # ---------------------------------------------------------------
    print(f"\n{'#' * 50}")
    print(f"# STEP {total}/{total}: Post-sync integrity (check_pages_sync.py)")
    print(f"{'#' * 50}")
    if not run_script(POST_SYNC_CHECK):
        print(f"\n{'!' * 50}")
        print(f"! HARD-STOP: {POST_SYNC_CHECK} FAILED.")
        print("! site/ and docs/ are out of sync after sync_pages_docs.py.")
        print("! This usually means a synced docs/ file was not `git add`ed,")
        print("! OR sync_pages_docs.py has a bug. Investigate before committing.")
        print(f"{'!' * 50}")
        return 1
    print(f"[{total}/{total}] {POST_SYNC_CHECK} OK")

    print(f"\n{'=' * 50}")
    print("All steps completed successfully.")
    print("Run 'git status' to review changes before committing.")
    print(f"{'=' * 50}")
    return 0


if __name__ == "__main__":
    sys.exit(update_site())
