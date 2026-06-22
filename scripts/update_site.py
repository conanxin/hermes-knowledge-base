"""Build the static site (with hard-stop on quality gate).

Pipeline order (HARD-STOP at the first step):

  1. scripts/check_kb.py            ← quality gate
  2. scripts/build_index.py
  3. scripts/export_site_data.py
  4. scripts/generate_item_pages.py
  5. scripts/sync_pages_docs.py

If `check_kb.py` exits non-zero, `update_site.py` MUST return non-zero
without running any of the build/export/generate/sync steps. This is the
quality gate enforcement: a broken catalog must never be published to
`site/data/catalog.json` or `docs/`.
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
    print("# STEP 0/4: Quality gate (check_kb.py)")
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
    for i, script in enumerate(BUILD_CHAIN, start=1):
        if not run_script(script):
            print(f"\nFAILED: {script}")
            print(f"\n{'=' * 50}")
            print("Some steps failed. Review output above.")
            print(f"{'=' * 50}")
            return 1
        print(f"[{i}/{len(BUILD_CHAIN)}] {script} OK")

    print(f"\n{'=' * 50}")
    print("All steps completed successfully.")
    print("Run 'git status' to review changes before committing.")
    print(f"{'=' * 50}")
    return 0


if __name__ == "__main__":
    sys.exit(update_site())
