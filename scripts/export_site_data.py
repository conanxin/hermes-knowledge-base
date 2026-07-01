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

# Fields to preserve, in the canonical output order. This is the single
# source of truth for the order in which keys appear in catalog.json.
# Records are reconstructed in this exact order so the output is
# byte-stable regardless of how keys were ordered in the source
# metadata.yaml or in index/catalog.jsonl.
FIELDS = [
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


def get_updated_date(data):
    """Return the most relevant date for display, or None."""
    for key in ("captured_date", "migrated_date", "published_date"):
        if data.get(key):
            return data[key]
    return None


def slug_from_path(path: str) -> str:
    """Return the final path segment as the slug.

    Path-OS-agnostic: normalizes backslashes to forward slashes first so the
    same slug is produced on Windows (content\\articles\\2026\\...) and on
    Linux (content/articles/2026/...). v0.3.70 fix.
    """
    if not path:
        return ""
    # Normalize to POSIX so split("/") works on both Windows and POSIX.
    posix_path = path.replace("\\", "/")
    return posix_path.rstrip("/").split("/")[-1]


def export_site_data():
    records = []
    with open(CATALOG_JSONL, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            # Reconstruct in canonical FIELDS order so the output is
            # byte-stable regardless of the order keys appear in
            # metadata.yaml or catalog.jsonl.
            filtered = {}
            for key in FIELDS:
                if key in data:
                    filtered[key] = data[key]
            # Append any unknown keys at the end (deterministic order via sort).
            for key in sorted(data.keys()):
                if key not in filtered:
                    filtered[key] = data[key]
            filtered["updated_date"] = get_updated_date(data)

            # Detail page support: derive slug, detail_url, github_url.
            path = filtered.get("path", "")
            slug = slug_from_path(path)
            # v0.3.70: normalize to POSIX before the "content/" prefix check
            # so Windows backslash paths (content\articles\...) are accepted.
            posix_path = path.replace("\\", "/")
            if slug and posix_path.startswith("content/"):
                filtered["slug"] = slug
                filtered["detail_url"] = f"items/{slug}/"
                # github_url uses POSIX paths (forward slashes) regardless of OS.
                filtered["github_url"] = GITHUB_REPO_BASE + posix_path
            else:
                # Non-content records (e.g. legacy or future virtual items)
                # still get github_url so cards can always offer a fallback.
                filtered["slug"] = slug
                filtered["detail_url"] = ""
                filtered["github_url"] = GITHUB_REPO_BASE + posix_path if posix_path else ""

            records.append(filtered)

    # Sort records by path for stable output order. Records with no path
    # are placed at the end (alphabetically by their stringified key state).
    records.sort(key=lambda r: r.get("path", ""))

    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    # Write with ensure_ascii=False so non-ASCII characters are preserved
    # verbatim, and emit a trailing newline so editors/git don't flag the
    # file as "no newline at end of file".
    with open(OUTPUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(records, f, ensure_ascii=False, indent=2, sort_keys=False)
        f.write("\n")

    n_with_detail = sum(1 for r in records if r.get("detail_url"))
    print(
        f"Exported {len(records)} records to {OUTPUT_JSON} "
        f"({n_with_detail} with detail_url)."
    )


if __name__ == "__main__":
    export_site_data()
