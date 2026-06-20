import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"

REQUIRED_FIELDS = ["title", "source_url", "captured_date", "status", "type", "tags"]


def check_kb():
    """Check knowledge base integrity"""
    issues = []
    total = 0
    ok = 0

    for content_dir in CONTENT_DIR.iterdir():
        if not content_dir.is_dir():
            continue
        for item_dir in content_dir.iterdir():
            if not item_dir.is_dir():
                continue
            total += 1
            meta_file = item_dir / "metadata.yaml"
            if not meta_file.exists():
                issues.append(f"MISSING metadata.yaml: {item_dir.relative_to(BASE_DIR)}")
                continue

            # Check required fields
            try:
                import yaml
                with open(meta_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}
            except ImportError:
                data = {}
                with open(meta_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if ":" in line and not line.strip().startswith("#"):
                            key, val = line.split(":", 1)
                            data[key.strip()] = val.strip().strip('"').strip("'")

            missing = [f for f in REQUIRED_FIELDS if f not in data or not data[f]]
            if missing:
                issues.append(f"MISSING fields {missing} in {meta_file.relative_to(BASE_DIR)}")

            # Check translation
            trans_file = item_dir / "translation.zh-CN.md"
            if not trans_file.exists():
                issues.append(f"MISSING translation.zh-CN.md: {item_dir.relative_to(BASE_DIR)}")

            if not missing and trans_file.exists():
                ok += 1

    print(f"\n{'='*50}")
    print(f"Knowledge Base Check")
    print(f"{'='*50}")
    print(f"Total items: {total}")
    print(f"PASS: {ok}")
    print(f"FAIL: {total - ok}")

    if issues:
        print(f"\nIssues ({len(issues)}):")
        for issue in issues:
            print(f"  - {issue}")
        return 1
    else:
        print("\nSTATUS: PASS")
        return 0


if __name__ == "__main__":
    sys.exit(check_kb())
