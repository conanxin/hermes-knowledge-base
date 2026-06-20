import os
import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"

REQUIRED_FIELDS = [
    "title", "title_zh", "source_url", "source_site", "author",
    "published_date", "captured_date", "language", "translation_language",
    "status", "type", "topics", "tags", "word_count"
]

ARTICLE_REQUIRED_FILES = [
    "source.md",
    "translation.zh-CN.md",
    "summary.md",
    "notes.md",
]


def check_kb():
    """Check knowledge base integrity"""
    issues = []
    total = 0
    ok = 0

    # Recursively scan all metadata.yaml files, same as build_index.py
    for meta_file in CONTENT_DIR.rglob("metadata.yaml"):
        item_dir = meta_file.parent
        total += 1

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

        # Check title_zh not empty
        title_zh = data.get("title_zh", "")
        if not title_zh or title_zh == "PLACEHOLDER":
            issues.append(f"EMPTY title_zh in {meta_file.relative_to(BASE_DIR)}")

        # Get item_type early for conditional checks
        item_type = data.get("type", "")

        # Check word_count
        word_count = data.get("word_count", {})
        if not isinstance(word_count, dict):
            issues.append(f"INVALID word_count type in {meta_file.relative_to(BASE_DIR)}")
        else:
            for key in ["source"]:
                val = word_count.get(key, 0)
                if not isinstance(val, int) or val <= 0:
                    issues.append(f"INVALID word_count.{key}={val} in {meta_file.relative_to(BASE_DIR)}")
            # translation word_count only required for articles
            if item_type == "article":
                val = word_count.get("translation", 0)
                if not isinstance(val, int) or val <= 0:
                    issues.append(f"INVALID word_count.translation={val} in {meta_file.relative_to(BASE_DIR)}")

        # Check topics and tags not empty
        topics = data.get("topics", [])
        if not topics or len(topics) == 0:
            issues.append(f"EMPTY topics in {meta_file.relative_to(BASE_DIR)}")
        tags = data.get("tags", [])
        if not tags or len(tags) == 0:
            issues.append(f"EMPTY tags in {meta_file.relative_to(BASE_DIR)}")

        # Check type-specific required files
        if item_type == "article":
            for req_file in ARTICLE_REQUIRED_FILES:
                req_path = item_dir / req_file
                if not req_path.exists():
                    issues.append(f"MISSING {req_file}: {item_dir.relative_to(BASE_DIR)}")

        # Check translation exists (only for articles)
        if item_type == "article":
            trans_file = item_dir / "translation.zh-CN.md"
            if not trans_file.exists():
                issues.append(f"MISSING translation.zh-CN.md: {item_dir.relative_to(BASE_DIR)}")

        # Count as OK if no issues for this item
        item_issues = [i for i in issues if str(meta_file.relative_to(BASE_DIR)) in i or str(item_dir.relative_to(BASE_DIR)) in i]
        if not missing and not item_issues:
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
