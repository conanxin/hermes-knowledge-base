import json
import os
import sys
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"
INDEX_DIR = BASE_DIR / "index"


# Canonical field order for catalog.jsonl / catalog.json. Records are
# reconstructed in this order so the serialized output is byte-stable
# regardless of the source metadata.yaml key order.
FIELD_ORDER = [
    "title",
    "title_zh",
    "type",
    "path",
    "author",
    "source_url",
    "source_site",
    "source_url_missing",
    "language",
    "translation_language",
    "status",
    "published_date",
    "captured_date",
    "migrated_date",
    "item_count",
    "topics",
    "tags",
    "word_count",
    "slug",
    "detail_url",
    "github_url",
    "updated_date",
]


def scan_metadata():
    """Scan all metadata.yaml files under content/, sorted by path for stability."""
    records = []
    # Sort rglob results by path string so the iteration order is deterministic
    # across filesystems and Python versions.
    meta_files = sorted(CONTENT_DIR.rglob("metadata.yaml"), key=lambda p: str(p))
    for meta_file in meta_files:
        rel_path = meta_file.relative_to(BASE_DIR)
        try:
            import yaml
            with open(meta_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except ImportError:
            # Fallback: simple key:value parser
            data = {}
            with open(meta_file, "r", encoding="utf-8") as f:
                for line in f:
                    if ":" in line and not line.strip().startswith("#"):
                        key, val = line.split(":", 1)
                        data[key.strip()] = val.strip().strip('"').strip("'")
        # Reconstruct dict in canonical FIELD_ORDER so the jsonl output is
        # stable regardless of the order keys appear in metadata.yaml.
        ordered = {}
        for key in FIELD_ORDER:
            if key in data:
                ordered[key] = data[key]
        # Append any unknown keys at the end (deterministic order via sort).
        for key in sorted(data.keys()):
            if key not in ordered:
                ordered[key] = data[key]
        ordered["path"] = str(rel_path.parent)
        records.append(ordered)
    return records


def build_catalog(records):
    """Build catalog.jsonl"""
    catalog_path = INDEX_DIR / "catalog.jsonl"
    with open(catalog_path, "w", encoding="utf-8") as f:
        for r in records:
            # Ensure item_count is preserved for resource_collection
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"catalog.jsonl: {len(records)} records")


def build_tags(records):
    """Build tags.md"""
    tags = {}
    for r in records:
        for tag in r.get("tags", []) or []:
            tags.setdefault(tag, []).append(r.get("title", "untitled"))
    tags_path = INDEX_DIR / "tags.md"
    with open(tags_path, "w", encoding="utf-8") as f:
        f.write("# Tags Index\n\n")
        for tag, items in sorted(tags.items()):
            f.write(f"## {tag}\n\n")
            for item in items:
                f.write(f"- {item}\n")
            f.write("\n")
    print(f"tags.md: {len(tags)} tags")


def build_authors(records):
    """Build authors.md"""
    authors = {}
    for r in records:
        author = r.get("author", "")
        if author:
            authors.setdefault(author, []).append(r.get("title", "untitled"))
    authors_path = INDEX_DIR / "authors.md"
    with open(authors_path, "w", encoding="utf-8") as f:
        f.write("# Authors Index\n\n")
        for author, items in sorted(authors.items()):
            f.write(f"## {author}\n\n")
            for item in items:
                f.write(f"- {item}\n")
            f.write("\n")
    print(f"authors.md: {len(authors)} authors")


def build_timeline(records):
    """Build timeline.md"""
    timeline = {}
    for r in records:
        date = r.get("captured_date", "")
        if date:
            month = date[:7] if len(date) >= 7 else date
            timeline.setdefault(month, []).append(r.get("title", "untitled"))
    timeline_path = INDEX_DIR / "timeline.md"
    with open(timeline_path, "w", encoding="utf-8") as f:
        f.write("# Timeline\n\n")
        for month, items in sorted(timeline.items(), reverse=True):
            f.write(f"## {month}\n\n")
            for item in items:
                f.write(f"- {item}\n")
            f.write("\n")
    print(f"timeline.md: {len(timeline)} months")


def main():
    records = scan_metadata()
    build_catalog(records)
    build_tags(records)
    build_authors(records)
    build_timeline(records)
    print("Index build complete.")


if __name__ == "__main__":
    main()
