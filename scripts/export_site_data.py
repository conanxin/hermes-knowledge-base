import json
from pathlib import Path

# Paths
CATALOG_JSONL = Path("index/catalog.jsonl")
OUTPUT_JSON = Path("site/data/catalog.json")

# Fields to preserve
FIELDS = [
    "title",
    "title_zh",
    "type",
    "path",
    "tags",
    "topics",
    "author",
    "captured_date",
    "migrated_date",
    "published_date",
    "item_count",
]


def get_updated_date(data):
    """Return the most relevant date for display, or None."""
    for key in ("captured_date", "migrated_date", "published_date"):
        if data.get(key):
            return data[key]
    return None


def export_site_data():
    records = []
    with open(CATALOG_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            filtered = {k: v for k, v in data.items() if k in FIELDS}
            filtered["updated_date"] = get_updated_date(data)
            records.append(filtered)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(records)} records to {OUTPUT_JSON}")


if __name__ == "__main__":
    export_site_data()
