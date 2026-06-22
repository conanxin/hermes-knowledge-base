import subprocess
import sys
from pathlib import Path

SCRIPTS = [
    "scripts/build_index.py",
    "scripts/export_site_data.py",
    "scripts/generate_item_pages.py",
    "scripts/sync_pages_docs.py",
]


def run_script(path: str) -> bool:
    print(f"\n{'='*50}")
    print(f"Running: {path}")
    print(f"{'='*50}")
    result = subprocess.run([sys.executable, path], cwd=Path(__file__).parent.parent)
    return result.returncode == 0


def update_site():
    all_pass = True
    for script in SCRIPTS:
        if not run_script(script):
            all_pass = False
            print(f"\nFAILED: {script}")
            break

    if all_pass:
        print(f"\n{'='*50}")
        print("All steps completed successfully.")
        print("Run 'git status' to review changes before committing.")
        print(f"{'='*50}")
    else:
        print(f"\n{'='*50}")
        print("Some steps failed. Review output above.")
        print(f"{'='*50}")
        sys.exit(1)


if __name__ == "__main__":
    update_site()
