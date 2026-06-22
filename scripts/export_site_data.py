"""Export site data from the canonical catalog into the static site.

Reads `index/catalog.jsonl` and writes `site/data/catalog.json` with the
fields consumed by the static browser, plus per-record `slug`,
`detail_url`, and `github_url` so the homepage can route clicks to
in-site detail pages instead of GitHub folder URLs.
"""

import json
from pathlib import Path

# Paths
CATALOG_JSONL = Path("index/catalog.jsonl")
OUTPUT_JSON = Path("site/data/catalog.json")

# GitHub Pages + repo base URLs (kept in sync with the static site).
GITHUB_REPO_BASE = "https://github.com/conanxin/hermes-knowledge-base/tree/main/"

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


def slug_from_path(path: str) -> str:
    """Return the final path segment as the slug."""
    if not path:
        return ""
    return path.rstrip("/").split("/")[-1]


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

            # Detail page support: derive slug, detail_url, github_url.
            path = filtered.get("path", "")
            slug = slug_from_path(path)
            if slug and path.startswith("content/"):
                filtered["slug"] = slug
                filtered["detail_url"] = f"items/{slug}/"
                filtered["github_url"] = GITHUB_REPO_BASE + path
            else:
                # Non-content records (e.g. legacy or future virtual items)
                # still get github_url so cards can always offer a fallback.
                filtered["slug"] = slug
                filtered["detail_url"] = ""
                filtered["github_url"] = GITHUB_REPO_BASE + path if path else ""

            records.append(filtered)

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    n_with_detail = sum(1 for r in records if r.get("detail_url"))
    print(
        f"Exported {len(records)} records to {OUTPUT_JSON} "
        f"({n_with_detail} with detail_url)."
    )


if __name__ == "__main__":
    export_site_data()
