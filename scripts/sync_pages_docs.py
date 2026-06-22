"""Sync files from site/ (development source) to docs/ (GitHub Pages).

Strict rules:
  * Only files in SYNC_FILES (root level) and the site/items/ tree are synced.
  * The docs/items/ tree is updated to mirror site/items/ — stale slugs are
    pruned, but no file outside docs/items/ is ever deleted (preserves
    hand-authored documentation like README.md, AGENT_COMMANDS.md, etc.).
  * The docs/data/catalog.json file is overwritten from site/data/catalog.json
    only when that exact path is in SYNC_FILES.
"""

import shutil
from pathlib import Path

# Paths
SITE_DIR = Path("site")
DOCS_DIR = Path("docs")

# Top-level files to sync from site/ to docs/
SYNC_FILES = [
    "index.html",
    "app.js",
    "styles.css",
    "data/catalog.json",
]

# Subtrees that should mirror site/ → docs/ (overwrite + prune stale entries)
MIRROR_DIRS = [
    "items",
]


def sync_top_level_files() -> list[str]:
    synced = []
    for f in SYNC_FILES:
        src = SITE_DIR / f
        if not src.exists():
            continue  # optional — generator may not have run yet
        dst = DOCS_DIR / f
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        synced.append(f)
    return synced


def _copy_tree(src_root: Path, dst_root: Path) -> tuple[list[str], list[str]]:
    """Mirror src_root into dst_root (file copy only, no metadata ACLs).

    Returns (copied_relative_paths, removed_relative_paths).
    """
    copied: list[str] = []
    if not src_root.exists():
        # If source side has no items dir, don't touch anything in dst.
        return copied, []

    src_paths: dict[str, Path] = {}
    for p in src_root.rglob("*"):
        if p.is_file():
            rel = p.relative_to(src_root).as_posix()
            src_paths[rel] = p

    dst_paths: dict[str, Path] = {}
    if dst_root.exists():
        for p in dst_root.rglob("*"):
            if p.is_file():
                rel = p.relative_to(dst_root).as_posix()
                dst_paths[rel] = p

    # Copy / overwrite.
    for rel, src_p in src_paths.items():
        dst_p = dst_root / rel
        dst_p.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src_p, dst_p)
        copied.append(rel)

    # Remove files in dst that no longer have a corresponding src file.
    # Critical: we only remove files inside dst_root, never anywhere else
    # in docs/. This protects hand-authored docs from being wiped.
    removed: list[str] = []
    stale = set(dst_paths.keys()) - set(src_paths.keys())
    for rel in sorted(stale):
        dst_p = dst_root / rel
        if dst_p.is_file():
            dst_p.unlink()
            removed.append(rel)
    # Best-effort cleanup of empty directories left behind.
    if dst_root.exists():
        for p in sorted(dst_root.rglob("*"), reverse=True):
            if p.is_dir() and not any(p.iterdir()):
                try:
                    p.rmdir()
                except OSError:
                    pass
    return copied, removed


def sync_pages_docs():
    synced_files = sync_top_level_files()
    mirror_copied: list[str] = []
    mirror_removed: list[str] = []
    for sub in MIRROR_DIRS:
        copied, removed = _copy_tree(SITE_DIR / sub, DOCS_DIR / sub)
        mirror_copied.extend(f"{sub}/{c}" for c in copied)
        mirror_removed.extend(f"{sub}/{r}" for r in removed)

    print(f"Synced {len(synced_files)} top-level files from site/ to docs/:")
    for f in synced_files:
        print(f"  {f}")
    if mirror_copied:
        print(f"Mirrored {len(mirror_copied)} files under site/items/ → docs/items/.")
    if mirror_removed:
        print(f"Pruned {len(mirror_removed)} stale files in docs/items/.")

    return 0


if __name__ == "__main__":
    exit(sync_pages_docs())
