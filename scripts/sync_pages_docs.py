import shutil
from pathlib import Path

# Paths
SITE_DIR = Path("site")
DOCS_DIR = Path("docs")

# Files to sync from site/ to docs/
SYNC_FILES = [
    "index.html",
    "app.js",
    "styles.css",
    "data/catalog.json",
]


def sync_pages_docs():
    missing = []
    for f in SYNC_FILES:
        src = SITE_DIR / f
        if not src.exists():
            missing.append(str(src))

    if missing:
        print(f"Missing source files: {missing}")
        return 1

    synced = []
    for f in SYNC_FILES:
        src = SITE_DIR / f
        dst = DOCS_DIR / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        synced.append(f)

    print(f"Synced {len(synced)} files from site/ to docs/:")
    for f in synced:
        print(f"  {f}")

    return 0


if __name__ == "__main__":
    exit(sync_pages_docs())
