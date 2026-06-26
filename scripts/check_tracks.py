#!/usr/bin/env python3
"""
Validate tracks.yaml files across content/articles/.

For each tracks.yaml under content/articles/**/, this script verifies:
  - File loads as YAML
  - `tracks:` is a non-empty list
  - Each track has: rank (int, unique within file), artist (non-empty str),
    title (non-empty str), confidence ∈ {verified, needs_verification, search_only}
  - youtube_embed_url (if non-empty) must match YouTube embed pattern
  - search_url (if non-empty) must be a URL with a scheme

For the canonical Paste 1960s article, additional structural checks are enforced:
  - tracks count == 50
  - rank range == 100..51 (50 unique continuous numbers)
  - source.md and translation.zh-CN.md H2 count == 50 (cross-check)

Output: STATUS line (PASS / WARNING / FAIL) and an exit code:
  - exit 0: PASS or WARNING (warnings allowed for needs_verification on embeds)
  - exit 1: FAIL (structural problems)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = REPO_ROOT / "content" / "articles"

CANONICAL_PASTE_SLUG = "2026-06-26-paste-greatest-songs-1960s"
CANONICAL_PASTE_RANK_RANGE = (51, 100)  # inclusive

VALID_CONFIDENCE = {"verified", "needs_verification", "search_only"}

YOUTUBE_EMBED_PATTERN = re.compile(
    r"^https?://(?:www\.)?youtube\.com/embed/[A-Za-z0-9_-]+(?:[?&].*)?$"
)
URL_PATTERN = re.compile(r"^https?://\S+$", re.I)


def _strip_quotes(s: str):
    if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
        return s[1:-1]
    if s == "" or s == "~" or s.lower() == "null":
        return ""
    if re.match(r"^-?\d+$", s):
        return int(s)
    return s


def _try_pyyaml():
    try:
        import yaml  # type: ignore
        return yaml
    except ImportError:
        return None


def _load_yaml(path: Path) -> dict:
    """Load tracks.yaml using PyYAML if available, else a focused fallback parser.

    The fallback parser supports the schema written by this project's tools:
    - top-level key: value
    - key: | literal block scalar (collected from following indented lines)
    - key: [a, b, c] inline list
    - tracks: list of mappings with 2-space leading dash and 4-space fields
    """
    if not path.exists():
        return {}
    yaml = _try_pyyaml()
    if yaml is not None:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    # Fallback: line-state machine.
    return _parse_yaml_fallback(path)


def _parse_yaml_fallback(path: Path) -> dict:
    """Robust YAML-ish parser for the project's tracks.yaml shape."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    root: dict = {}
    block_key: str | None = None
    block_indent: int | None = None
    block_lines: list[str] = []
    pending_list_key: str | None = None  # key whose list we are building
    list_items: list = []
    current_item: dict | None = None

    def finalize_block() -> None:
        nonlocal block_key, block_indent, block_lines
        if block_key is not None:
            root[block_key] = "\n".join(block_lines).rstrip()
        block_key = None
        block_indent = None
        block_lines = []

    def finalize_list() -> None:
        nonlocal pending_list_key, list_items, current_item
        if current_item is not None and pending_list_key is not None:
            list_items.append(current_item)
            current_item = None
        if pending_list_key is not None:
            root[pending_list_key] = list_items
        pending_list_key = None
        list_items = []

    for raw in lines:
        # Drop comments.
        if "#" in raw:
            # Naive comment strip — fine for our files (no # inside strings).
            in_str = None
            cleaned = []
            for ch in raw:
                if in_str:
                    cleaned.append(ch)
                    if ch == in_str:
                        in_str = None
                elif ch in ('"', "'"):
                    in_str = ch
                    cleaned.append(ch)
                elif ch == "#":
                    break
                else:
                    cleaned.append(ch)
            line = "".join(cleaned).rstrip()
        else:
            line = raw.rstrip()

        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        # Block scalar continuation (deeper indent than block_key's value).
        if block_key is not None and indent > (block_indent or 0) and not stripped.startswith("-"):
            block_lines.append(stripped)
            continue

        # Finalize any pending block when we encounter a non-continuation line.
        if block_key is not None and (indent <= (block_indent or 0) or stripped.startswith("-")):
            finalize_block()

        # Top-level key.
        if indent == 0:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
            if m:
                key, value = m.group(1), m.group(2).strip()
                finalize_list()
                if value == "" or value == "~" or value.lower() == "null":
                    pending_list_key = key
                    list_items = []
                    current_item = None
                elif value == "|":
                    block_key = key
                    block_indent = 0
                    block_lines = []
                elif value.startswith("[") and value.endswith("]"):
                    root[key] = [
                        _strip_quotes(x.strip())
                        for x in value[1:-1].split(",")
                        if x.strip()
                    ]
                else:
                    root[key] = _strip_quotes(value)
                continue

        # 2-space list item "- ..."
        if indent == 2 and stripped.startswith("- "):
            # Finalize any open list before starting next item? No — same list.
            if pending_list_key is None:
                continue
            if current_item is not None:
                list_items.append(current_item)
            current_item = {}
            rest = stripped[2:].strip()
            sub = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", rest)
            if sub:
                k, v = sub.group(1), sub.group(2).strip()
                current_item[k] = _strip_quotes(v)
            continue

        # 4-space field under current_item.
        if indent == 4 and current_item is not None:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
            if m:
                k, v = m.group(1), m.group(2).strip()
                current_item[k] = _strip_quotes(v)
                continue

        # Anything else: ignore.

    finalize_block()
    finalize_list()
    return root


def validate_tracks_file(path: Path) -> list[str]:
    """Return list of issue strings. Empty list = OK."""
    issues: list[str] = []
    try:
        data = _load_yaml(path)
    except Exception as e:
        return [f"YAML parse error in {path.name}: {e}"]

    tracks = data.get("tracks")
    if not isinstance(tracks, list) or len(tracks) == 0:
        return [f"{path.name}: 'tracks' missing or empty"]

    ranks_seen: set[int] = set()
    for i, t in enumerate(tracks):
        label = f"{path.name} tracks[{i}]"

        if not isinstance(t, dict):
            issues.append(f"{label}: not a mapping (got {type(t).__name__})")
            continue

        rank = t.get("rank")
        if not isinstance(rank, int) or rank < 1:
            issues.append(f"{label}: rank must be int >= 1 (got {rank!r})")
        else:
            if rank in ranks_seen:
                issues.append(f"{label}: duplicate rank {rank}")
            ranks_seen.add(rank)

        artist = t.get("artist")
        if not isinstance(artist, str) or not artist.strip():
            issues.append(f"{label}: artist must be non-empty string")
        title = t.get("title")
        if not isinstance(title, str) or not title.strip():
            issues.append(f"{label}: title must be non-empty string")

        conf = t.get("confidence", "")
        if conf not in VALID_CONFIDENCE:
            issues.append(f"{label}: confidence must be one of {sorted(VALID_CONFIDENCE)} (got {conf!r})")

        embed = t.get("youtube_embed_url", "") or ""
        if embed and not YOUTUBE_EMBED_PATTERN.match(embed):
            issues.append(f"{label}: youtube_embed_url is set but doesn't match embed pattern ({embed[:60]!r})")

        search = t.get("search_url", "") or ""
        if search and not URL_PATTERN.match(search):
            issues.append(f"{label}: search_url is set but not a valid URL ({search[:60]!r})")

    return issues


def cross_check_paste_1960s(tracks_path: Path) -> list[str]:
    """For the canonical Paste 1960s article: rank range + source/translation H2 counts."""
    issues: list[str] = []
    if not tracks_path.exists():
        return [f"{tracks_path.name}: file not found"]

    data = _load_yaml(tracks_path)
    tracks = data.get("tracks", [])
    if len(tracks) != 50:
        issues.append(f"expected 50 tracks, got {len(tracks)}")

    ranks = sorted([t.get("rank") for t in tracks if isinstance(t.get("rank"), int)])
    expected = list(range(CANONICAL_PASTE_RANK_RANGE[0], CANONICAL_PASTE_RANK_RANGE[1] + 1))
    if ranks != expected:
        issues.append(f"rank set != expected continuous 100..51 (got {ranks[:5]}...{ranks[-3:]})")

    article_dir = tracks_path.parent
    src = article_dir / "source.md"
    tr = article_dir / "translation.zh-CN.md"

    def _count_h2_with_numbers(p: Path) -> int:
        if not p.exists():
            return -1
        text = p.read_text(encoding="utf-8")
        return len(re.findall(r"^##\s+\d+\.\s+", text, re.M))

    src_count = _count_h2_with_numbers(src)
    tr_count = _count_h2_with_numbers(tr)
    if src_count != 50:
        issues.append(f"source.md has {src_count} numbered H2 (expected 50)")
    if tr_count != 50:
        issues.append(f"translation.zh-CN.md has {tr_count} numbered H2 (expected 50)")

    return issues


def main() -> int:
    if not CONTENT_DIR.exists():
        print(f"Missing content dir: {CONTENT_DIR}")
        return 1

    tracks_files = sorted(CONTENT_DIR.rglob("tracks.yaml"))
    if not tracks_files:
        print("STATUS: WARNING — no tracks.yaml files found under content/articles/")
        return 0

    all_issues: list[str] = []
    cross_issues: list[str] = []
    summary_rows: list[str] = []

    for tf in tracks_files:
        rel = tf.relative_to(REPO_ROOT)
        issues = validate_tracks_file(tf)
        if issues:
            all_issues.extend(f"[{rel}] {x}" for x in issues)
            summary_rows.append(f"  {rel}: FAIL ({len(issues)} issues)")
        else:
            data = _load_yaml(tf)
            n = len(data.get("tracks", []))
            summary_rows.append(f"  {rel}: PASS ({n} tracks)")

        # Paste 1960s: additional cross-check.
        if tf.parent.name == CANONICAL_PASTE_SLUG:
            x_issues = cross_check_paste_1960s(tf)
            if x_issues:
                cross_issues.extend(f"[{rel}] {x}" for x in x_issues)

    print("Tracks validation:")
    for row in summary_rows:
        print(row)

    has_structural_problems = bool(all_issues) or bool(cross_issues)

    print("")
    if has_structural_problems:
        print("ISSUES:")
        for i in all_issues + cross_issues:
            print(f"  - {i}")
        print("")
        print("STATUS: FAIL")
        return 1

    # Aggregate confidence breakdown for the Paste article (informational).
    paste_path = CONTENT_DIR / "2026" / CANONICAL_PASTE_SLUG / "tracks.yaml"
    if paste_path.exists():
        data = _load_yaml(paste_path)
        tracks = data.get("tracks", [])
        conf_counts: dict[str, int] = {}
        with_embed = 0
        with_search = 0
        for t in tracks:
            c = t.get("confidence", "")
            conf_counts[c] = conf_counts.get(c, 0) + 1
            if t.get("youtube_embed_url"):
                with_embed += 1
            if t.get("search_url"):
                with_search += 1
        print("")
        print("Paste 1960s confidence breakdown:")
        for k in sorted(conf_counts.keys()):
            print(f"  {k}: {conf_counts[k]}")
        print(f"  tracks with youtube_embed_url: {with_embed}")
        print(f"  tracks with search_url: {with_search}")
        print("")
        if conf_counts.get("verified", 0) == 0:
            print("STATUS: WARNING — no tracks with confidence=verified; all require human URL review")
        else:
            print("STATUS: PASS")
    else:
        print("")
        print("STATUS: PASS")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())