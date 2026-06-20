import os
import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"

# Fields that must exist in every metadata.yaml
REQUIRED_FIELDS = [
    "title", "title_zh", "source_url", "source_site", "author",
    "published_date", "captured_date", "language", "translation_language",
    "status", "type", "topics", "tags", "word_count"
]

# Fields that must have a non-empty value regardless of type
MUST_BE_NON_EMPTY = {"title", "title_zh", "captured_date", "status", "type"}

# Base files required for ALL types
BASE_REQUIRED_FILES = [
    "metadata.yaml",
    "source.md",
    "summary.md",
    "notes.md",
]


def is_empty(val):
    """Return True if value is considered empty/missing."""
    if val is None:
        return True
    if isinstance(val, str) and val.strip() == "":
        return True
    if isinstance(val, list) and len(val) == 0:
        return True
    if isinstance(val, dict) and len(val) == 0:
        return True
    return False


def check_kb():
    """Check knowledge base integrity"""
    issues = []
    total = 0
    ok = 0

    for meta_file in CONTENT_DIR.rglob("metadata.yaml"):
        item_dir = meta_file.parent
        total += 1

        # Parse metadata
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

        item_type = data.get("type", "")
        source_url_missing = data.get("source_url_missing", False)
        rel_meta = meta_file.relative_to(BASE_DIR)
        rel_dir = item_dir.relative_to(BASE_DIR)

        # --- 1. Check required fields exist ---
        missing_keys = [f for f in REQUIRED_FIELDS if f not in data]
        if missing_keys:
            issues.append(f"MISSING keys {missing_keys} in {rel_meta}")

        # --- 2. Check must-be-non-empty fields ---
        for f in MUST_BE_NON_EMPTY:
            if f in data and is_empty(data[f]):
                issues.append(f"EMPTY {f} in {rel_meta}")

        # --- 3. source_url rules ---
        if source_url_missing:
            # source_url_missing=true: source_url can be null/empty, but key must exist
            if "source_url" in data and not is_empty(data["source_url"]):
                # Optional: warn if source_url is set but missing flag is true
                pass
        else:
            # source_url_missing=false: source_url must be non-empty
            if "source_url" in data and is_empty(data["source_url"]):
                issues.append(f"EMPTY source_url (but source_url_missing=false) in {rel_meta}")
            elif "source_url" not in data:
                issues.append(f"MISSING source_url (source_url_missing=false) in {rel_meta}")

        # --- 4. source_site rules ---
        # source_site can be empty for legacy notes, but key must exist
        if "source_site" in data and is_empty(data["source_site"]):
            # Legacy note/project: allow empty source_site
            if item_type not in ("note", "project", "resource", "report", "prompt"):
                issues.append(f"EMPTY source_site in {rel_meta}")

        # --- 5. translation_language rules ---
        if item_type == "article":
            trans_lang = data.get("translation_language", "")
            if is_empty(trans_lang) or trans_lang not in ("zh-CN", "zh"):
                issues.append(f"INVALID translation_language='{trans_lang}' for article in {rel_meta}")
            trans_file = item_dir / "translation.zh-CN.md"
            if not trans_file.exists():
                issues.append(f"MISSING translation.zh-CN.md: {rel_dir}")
        else:
            # note/project/resource/report/prompt/resource_collection: translation_language can be null/empty
            pass

        # --- 6. word_count rules ---
        word_count = data.get("word_count", {})
        if not isinstance(word_count, dict):
            issues.append(f"INVALID word_count type in {rel_meta}")
        else:
            wc_val = word_count.get("source", 0)
            if not isinstance(wc_val, int) or wc_val <= 0:
                issues.append(f"INVALID word_count.source={wc_val} in {rel_meta}")
            # Only check translation word_count if the field exists
            if "translation" in word_count:
                wc_trans = word_count["translation"]
                if not isinstance(wc_trans, int) or wc_trans < 0:
                    issues.append(f"INVALID word_count.translation={wc_trans} in {rel_meta}")

        # --- 7. item_count rules (for resource_collection) ---
        if item_type == "resource_collection":
            item_count = data.get("item_count", 0)
            if not isinstance(item_count, int) or item_count <= 0:
                issues.append(f"INVALID item_count={item_count} for resource_collection in {rel_meta}")

        # --- 8. topics and tags ---
        topics = data.get("topics", [])
        if not isinstance(topics, list) or len(topics) == 0:
            issues.append(f"EMPTY topics in {rel_meta}")
        tags = data.get("tags", [])
        if not isinstance(tags, list) or len(tags) == 0:
            issues.append(f"EMPTY tags in {rel_meta}")

        # --- 9. Check base required files for ALL types ---
        # resource_collection uses collection.md instead of source.md
        if item_type == "resource_collection":
            req_files = ["metadata.yaml", "collection.md", "summary.md", "notes.md"]
        else:
            req_files = BASE_REQUIRED_FILES
        for req_file in req_files:
            req_path = item_dir / req_file
            if not req_path.exists():
                issues.append(f"MISSING {req_file}: {rel_dir}")

        # --- 10. Count OK if no issues for this item ---
        item_issues = [i for i in issues if str(rel_meta) in i or str(rel_dir) in i]
        if not missing_keys and not item_issues:
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
