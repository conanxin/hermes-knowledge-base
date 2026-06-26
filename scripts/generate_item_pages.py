"""Generate static item detail pages for the knowledge base browser.

Reads `site/data/catalog.json` (produced by export_site_data.py) and writes
one `site/items/<slug>/index.html` per record. Each page renders the
record's metadata, summary, source/translation/notes/collection body
based on the record type, and links back to the homepage and the GitHub
folder.

Markdown rendering is implemented with stdlib only (re + html.escape) —
no external dependencies. Supported elements:

  - ATX headings  (# / ## / ### / ####)
  - Paragraphs
  - Unordered lists  (- / *)
  - Ordered lists    (1. 2. ...)
  - Blockquotes      (>)
  - Fenced code      (```)
  - Inline code      (`code`)
  - Bold / italic    (** / *)
  - Links            ([text](url))
  - Horizontal rule  (---)
  - GFM-style tables (| col | col |)
  - Footnote refs    ([^1])  — kept as superscript text
  - HTML entity escape for safety

The intent is "good enough" rendering for translated Chinese articles and
English notes, not a fully spec-compliant Markdown parser.
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Paths & constants
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent.parent
CATALOG_JSON = REPO_ROOT / "site" / "data" / "catalog.json"
ITEMS_DIR = REPO_ROOT / "site" / "items"

GITHUB_REPO_BASE = "https://github.com/conanxin/hermes-knowledge-base/tree/main/"
SITE_BASE = "https://conanxin.github.io/hermes-knowledge-base/"

# Type-specific body files (relative to the record directory).
# The `summary` slot, when present, is rendered as the first body section
# (default-expanded) and is what the page TOC is sourced from. The order
# here also drives the visual order on the page.
BODY_FILES_BY_TYPE: Dict[str, List[Tuple[str, str]]] = {
    "article": [
        ("summary", "summary.md"),
        ("translation", "translation.zh-CN.md"),
        ("source", "source.md"),
    ],
    "resource_collection": [
        ("summary", "summary.md"),
        ("collection", "collection.md"),
    ],
    "note": [
        ("summary", "summary.md"),
        ("source", "source.md"),
    ],
    "project": [
        ("summary", "summary.md"),
        ("source", "source.md"),
    ],
}

# Human-readable labels for body sections
SECTION_LABELS: Dict[str, str] = {
    "translation": "中文翻译",
    "source": "原文 / 源文本",
    "summary": "摘要",
    "notes": "笔记",
    "collection": "资源集合",
}

SECTION_ORDER: List[str] = ["summary", "translation", "collection", "source", "notes"]


# ---------------------------------------------------------------------------
# Slug & URL helpers
# ---------------------------------------------------------------------------
def slug_from_path(path: str) -> str:
    """Return the final path segment as the slug."""
    return path.rstrip("/").split("/")[-1] if path else ""


# ---------------------------------------------------------------------------
# Markdown rendering (stdlib only)
# ---------------------------------------------------------------------------
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)")
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)\s]+)\)")
_FOOTNOTE_RE = re.compile(r"\[\^([^\]]+)\]")


def _apply_inline(text: str) -> str:
    """Apply inline transforms. Caller must pass a single text line."""
    if not text:
        return ""

    # Escape HTML first so user content is safe, then re-introduce our tags.
    s = html.escape(text, quote=False)

    # Footnote refs: [^1] → <sup>[1]</sup>
    s = _FOOTNOTE_RE.sub(r"<sup>[\1]</sup>", s)

    # Inline code: `code` → <code>code</code>
    s = _INLINE_CODE_RE.sub(r"<code>\1</code>", s)

    # Links: [text](url) → <a> (do after escaping, since URL may contain
    # legitimate & that html.escape turned into &amp;)
    def _link_sub(m: re.Match) -> str:
        label, url = m.group(1), m.group(2)
        url = url.replace("&amp;", "&")
        return f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noopener">{label}</a>'

    s = _LINK_RE.sub(_link_sub, s)

    # Bold then italic.
    s = _BOLD_RE.sub(r"<strong>\1</strong>", s)
    s = _ITALIC_RE.sub(r"<em>\1</em>", s)

    return s


_TABLE_SEP_RE = re.compile(r"^\s*\|?\s*:?-+:?\s*(\|\s*:?-+:?\s*)+\|?\s*$")


def _render_table(lines: List[str], start: int) -> Tuple[str, int]:
    """Render a GFM-style table starting at line index `start`.

    Returns (html, next_index). The header row is the first `lines[start]`
    and the separator is `lines[start+1]`.
    """
    header_cells = [c.strip() for c in lines[start].strip().strip("|").split("|")]
    body_rows: List[List[str]] = []
    i = start + 2
    while i < len(lines) and lines[i].strip().startswith("|"):
        row_cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
        # Pad / trim to header length.
        if len(row_cells) < len(header_cells):
            row_cells += [""] * (len(header_cells) - len(row_cells))
        elif len(row_cells) > len(header_cells):
            row_cells = row_cells[: len(header_cells)]
        body_rows.append(row_cells)
        i += 1

    out = ['<table class="md-table">']
    out.append("<thead><tr>")
    for cell in header_cells:
        out.append(f"<th>{_apply_inline(cell)}</th>")
    out.append("</tr></thead>")
    if body_rows:
        out.append("<tbody>")
        for row in body_rows:
            out.append("<tr>")
            for cell in row:
                out.append(f"<td>{_apply_inline(cell)}</td>")
            out.append("</tr>")
        out.append("</tbody>")
    out.append("</table>")
    return "".join(out), i


def _render_list(items: List[Tuple[str, bool]], ordered: bool) -> str:
    """Render a list. `items` is a list of (text, is_ordered_index)."""
    tag = "ol" if ordered else "ul"
    out = [f"<{tag}>"]
    for text, _ in items:
        out.append(f"<li>{_apply_inline(text)}</li>")
    out.append(f"</{tag}>")
    return "".join(out)


def _slugify(text: str, used_ids: set[str]) -> str:
    """Make a URL-safe, Chinese-friendly id from heading text.

    Strategy:
      1. Lowercase.
      2. Replace whitespace with '-'.
      3. Strip everything outside [a-z0-9\\u4e00-\\u9fff-].
      4. Collapse repeated '-'.
      5. Deduplicate against `used_ids` by suffixing -2, -3, ...
    """
    s = text.lower().strip()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^\w\u4e00-\u9fff\-]+", "", s, flags=re.UNICODE)
    s = re.sub(r"-+", "-", s).strip("-")
    if not s:
        s = "section"
    base = s
    n = 1
    while s in used_ids:
        n += 1
        s = f"{base}-{n}"
    used_ids.add(s)
    return s


def render_markdown(
    md: str,
    track_cards: Optional[Dict[int, str]] = None,
    track_card_context: str = "",
) -> Tuple[str, List[Tuple[int, str, str]]]:
    """Convert a Markdown string to HTML, returning (html, toc).

    `toc` is a list of `(level, text, id)` tuples for h2/h3 headings —
    level 2 and 3 only. Headings get stable id attributes so they can be
    linked to from the page TOC.

    `track_cards` (optional): dict mapping rank (int) → pre-rendered HTML
    string. When an H2 heading's text matches "#NNN. ..." where NNN is
    in track_cards, the corresponding HTML is inserted immediately after
    the H2. This is the music-track feature for listicle articles.

    `track_card_context` (optional): a string class-name suffix used to
    namespace the inserted cards (e.g. "track-card--in-translation").
    """
    if not md:
        return "", []

    # Normalize line endings, split lines.
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")

    out: List[str] = []
    toc: List[Tuple[int, str, str]] = []
    used_ids: set[str] = set()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        stripped = line.strip()

        # Blank line — paragraph break.
        if not stripped:
            i += 1
            continue

        # Horizontal rule.
        if re.match(r"^-{3,}$|^\*{3,}$", stripped):
            out.append("<hr>")
            i += 1
            continue

        # Fenced code block.
        if stripped.startswith("```"):
            lang = stripped[3:].strip()
            i += 1
            code_lines: List[str] = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            lang_attr = f' data-lang="{html.escape(lang)}"' if lang else ""
            out.append(
                f"<pre{lang_attr}><code>{html.escape(chr(10).join(code_lines))}</code></pre>"
            )
            continue

        # Headings.
        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            raw_text = m.group(2).strip()
            heading_id = _slugify(raw_text, used_ids)
            if level in (2, 3):
                toc.append((level, raw_text, heading_id))
            out.append(
                f'<h{level} id="{heading_id}">{_apply_inline(raw_text)}</h{level}>'
            )
            # Music-track feature: if H2 starts with a recognized rank
            # and we have a card for it, insert after the H2.
            if track_cards and level == 2:
                rank_m = re.match(r"^#?(\d+)\.", raw_text)
                if rank_m:
                    rank = int(rank_m.group(1))
                    card_html = track_cards.get(rank)
                    if card_html:
                        out.append(card_html)
            i += 1
            continue

        # Tables: header row, then separator, then body rows.
        if "|" in stripped and i + 1 < n and _TABLE_SEP_RE.match(lines[i + 1].strip()):
            html_table, next_i = _render_table(lines, i)
            out.append(html_table)
            i = next_i
            continue

        # Blockquote (collect contiguous > lines).
        if stripped.startswith(">"):
            quote_lines: List[str] = []
            while i < n and lines[i].strip().startswith(">"):
                # Strip leading '>' and optional space.
                quote_lines.append(re.sub(r"^>\s?", "", lines[i].lstrip()))
                i += 1
            inner_md = "\n".join(quote_lines)
            inner_html, _ = render_markdown(inner_md)
            out.append(f"<blockquote>{inner_html}</blockquote>")
            continue

        # Unordered list.
        if re.match(r"^[-*+]\s+", stripped):
            items: List[Tuple[str, bool]] = []
            while i < n:
                m_li = re.match(r"^(\s*)[-*+]\s+(.*)$", lines[i])
                if not m_li:
                    break
                items.append((m_li.group(2), False))
                i += 1
            out.append(_render_list(items, ordered=False))
            continue

        # Ordered list.
        if re.match(r"^\d+\.\s+", stripped):
            items = []
            while i < n:
                m_li = re.match(r"^\s*\d+\.\s+(.*)$", lines[i])
                if not m_li:
                    break
                items.append((m_li.group(1), True))
                i += 1
            out.append(_render_list(items, ordered=True))
            continue

        # Paragraph: collect contiguous non-blank, non-block lines.
        para_lines: List[str] = []
        while i < n:
            cur = lines[i]
            cur_stripped = cur.strip()
            if not cur_stripped:
                break
            if cur_stripped.startswith(("#", ">", "```", "-", "*", "+")) and re.match(
                r"^(#{1,4}\s|>\s|```|[-*+]\s)", cur_stripped
            ):
                break
            if re.match(r"^\d+\.\s", cur_stripped):
                break
            if "|" in cur_stripped and i + 1 < n and _TABLE_SEP_RE.match(
                lines[i + 1].strip()
            ):
                break
            if re.match(r"^-{3,}$|^\*{3,}$", cur_stripped):
                break
            para_lines.append(cur_stripped)
            i += 1
        if para_lines:
            out.append(f"<p>{_apply_inline(' '.join(para_lines))}</p>")

    return "\n".join(out), toc


# ---------------------------------------------------------------------------
# Record loading
# ---------------------------------------------------------------------------
def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _safe_load_yaml(path: Path) -> Dict[str, Any]:
    """Minimal YAML loader covering the 15-field metadata schema.

    Avoids depending on PyYAML. Handles:
      - key: value
      - key: null
      - list values prefixed with "  - item"
      - inline list: ["a", "b"]
      - block scalars (|2 etc) — not needed for current metadata
    """
    if not path.exists():
        return {}

    text = path.read_text(encoding="utf-8")
    result: Dict[str, Any] = {}
    current_key: Optional[str] = None
    current_list: List[str] = []

    def _flush_list() -> None:
        nonlocal current_key, current_list
        if current_key is not None and current_list:
            result[current_key] = current_list
        current_key = None
        current_list = []

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if line.startswith("  - "):
            # List item — value is line[4:].strip(); strip surrounding quotes.
            val = line[4:].strip()
            if (val.startswith('"') and val.endswith('"')) or (
                val.startswith("'") and val.endswith("'")
            ):
                val = val[1:-1]
            current_list.append(val)
            continue
        # New key.
        _flush_list()
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
        if not m:
            continue
        key, value = m.group(1), m.group(2).strip()
        if value == "" or value == "~" or value.lower() == "null":
            current_key = key
            current_list = []
            continue
        # Inline list?  [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1]
            parts: List[str] = []
            buf = ""
            in_str = False
            quote = ""
            for ch in inner:
                if in_str:
                    if ch == quote:
                        in_str = False
                    buf += ch
                elif ch in ('"', "'"):
                    in_str = True
                    quote = ch
                    buf += ch
                elif ch == ",":
                    parts.append(buf.strip().strip('"').strip("'"))
                    buf = ""
                else:
                    buf += ch
            if buf.strip():
                parts.append(buf.strip().strip('"').strip("'"))
            result[key] = [p for p in parts if p]
            current_key = None
            current_list = []
            continue
        # Scalar: strip surrounding quotes, treat unquoted "null"/"true"/"false".
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        elif value.lower() == "true":
            value = True
        elif value.lower() == "false":
            value = False
        # Numeric scalars.
        elif re.match(r"^-?\d+$", value):
            value = int(value)
        # word_count: { ... }  (block-style mapping on one line) — parse
        # simple key/value pairs.
        elif value.startswith("{") and value.endswith("}"):
            inner = value[1:-1]
            sub: Dict[str, Any] = {}
            for piece in inner.split(","):
                if ":" not in piece:
                    continue
                k, v = piece.split(":", 1)
                v = v.strip()
                if re.match(r"^-?\d+$", v):
                    sub[k.strip()] = int(v)
                else:
                    sub[k.strip()] = v.strip().strip('"').strip("'")
            value = sub
        result[key] = value
        current_key = None
        current_list = []

    _flush_list()
    return result


def load_record_body(record: Dict[str, Any], content_root: Path) -> Dict[str, Any]:
    """Load metadata + type-specific body files for a record.

    Returns dict with keys: metadata, sections, missing_sections, tracks_data
    """
    record_path = content_root / record["path"]
    meta: Dict[str, Any] = {}
    meta_path = record_path / "metadata.yaml"
    if meta_path.exists():
        meta = _safe_load_yaml(meta_path)

    # Resolve type & body files.
    record_type = meta.get("type") or record.get("type", "article")
    body_specs = BODY_FILES_BY_TYPE.get(record_type, BODY_FILES_BY_TYPE["article"])

    sections: Dict[str, str] = {}
    missing: List[str] = []
    for key, fname in body_specs:
        body = _read_text(record_path / fname)
        if body:
            sections[key] = body
        else:
            missing.append(key)

    # notes.md is shared across all types.
    notes_body = _read_text(record_path / "notes.md")
    if notes_body:
        sections["notes"] = notes_body
    else:
        missing.append("notes")

    # Optional tracks.yaml (music-track feature for listicle articles).
    tracks_data: Dict[str, Any] = {}
    tracks_path = record_path / "tracks.yaml"
    if tracks_path.exists():
        tracks_data = _load_tracks_yaml(tracks_path)

    return {
        "metadata": meta,
        "sections": sections,
        "missing": missing,
        "type": record_type,
        "tracks_data": tracks_data,
    }


def _load_tracks_yaml(path: Path) -> Dict[str, Any]:
    """Load tracks.yaml using PyYAML if available, else the fallback parser.

    Mirrors the parser in scripts/check_tracks.py. Kept here so
    generate_item_pages.py has no import-cycle with check_tracks.
    """
    if not path.exists():
        return {}
    try:
        import yaml  # type: ignore
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        pass
    return _parse_tracks_yaml_fallback(path)


def _parse_tracks_yaml_fallback(path: Path) -> Dict[str, Any]:
    """Focused YAML-ish parser for the tracks.yaml shape used in this repo."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()

    root: Dict[str, Any] = {}
    block_key: Optional[str] = None
    block_indent: Optional[int] = None
    block_lines: List[str] = []
    pending_list_key: Optional[str] = None
    list_items: List[Any] = []
    current_item: Optional[Dict[str, Any]] = None

    def _strip_quotes(s: str):
        if len(s) >= 2 and ((s[0] == '"' and s[-1] == '"') or (s[0] == "'" and s[-1] == "'")):
            return s[1:-1]
        if s == "" or s == "~" or s.lower() == "null":
            return ""
        if re.match(r"^-?\d+$", s):
            return int(s)
        return s

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
        if "#" in raw:
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

        if block_key is not None and indent > (block_indent or 0) and not stripped.startswith("-"):
            block_lines.append(stripped)
            continue

        if block_key is not None and (indent <= (block_indent or 0) or stripped.startswith("-")):
            finalize_block()

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

        if indent == 2 and stripped.startswith("- "):
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

        if indent == 4 and current_item is not None:
            m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", line)
            if m:
                k, v = m.group(1), m.group(2).strip()
                current_item[k] = _strip_quotes(v)
                continue

    finalize_block()
    finalize_list()
    return root


def _build_track_cards(
    tracks: List[Dict[str, Any]],
) -> Dict[int, str]:
    """Render a dict[rank] -> track-card HTML for all tracks.

    Returns a dict so render_markdown can look up cards by rank number.
    Cards are not embedded with iframes by default — the embed_url is
    stored as a data attribute and rendered on click via site/app.js.
    """
    cards: Dict[int, str] = {}
    for t in tracks:
        if not isinstance(t, dict):
            continue
        rank = t.get("rank")
        if not isinstance(rank, int):
            continue
        artist = html.escape(str(t.get("artist") or ""))
        title = html.escape(str(t.get("title") or ""))
        year = html.escape(str(t.get("year") or ""))
        conf = str(t.get("confidence") or "needs_verification")
        embed_url = str(t.get("youtube_embed_url") or "")
        youtube_url = str(t.get("youtube_url") or "")
        spotify_url = str(t.get("spotify_url") or "")
        apple_url = str(t.get("apple_music_url") or "")
        search_url = str(t.get("search_url") or "")

        # External action links (rendered only if URL is present).
        actions: List[str] = []
        if youtube_url:
            actions.append(
                f'<a class="track-link track-link-youtube" href="{html.escape(youtube_url, quote=True)}" '
                f'target="_blank" rel="noopener">YouTube ↗</a>'
            )
        if spotify_url:
            actions.append(
                f'<a class="track-link track-link-spotify" href="{html.escape(spotify_url, quote=True)}" '
                f'target="_blank" rel="noopener">Spotify ↗</a>'
            )
        if apple_url:
            actions.append(
                f'<a class="track-link track-link-apple" href="{html.escape(apple_url, quote=True)}" '
                f'target="_blank" rel="noopener">Apple Music ↗</a>'
            )
        if search_url and not (youtube_url or spotify_url or apple_url):
            actions.append(
                f'<a class="track-link track-link-search" href="{html.escape(search_url, quote=True)}" '
                f'target="_blank" rel="noopener">查找版本 ↗</a>'
            )

        # Play button (only when embed_url is present).
        play_btn = ""
        if embed_url:
            play_btn = (
                f'<button type="button" class="track-play-button" '
                f'data-embed-url="{html.escape(embed_url, quote=True)}" '
                f'aria-label="播放 {title}">▶ 播放</button>'
            )

        # Confidence badge.
        conf_label = {
            "verified": "verified",
            "needs_verification": "待验证",
            "search_only": "搜索链接",
        }.get(conf, conf)
        conf_class = (
            "track-confidence-verified" if conf == "verified"
            else "track-confidence-needs-verification"
        )

        card = (
            f'<div class="track-card" data-rank="{rank}">'
            f'<div class="track-meta">'
            f'<span class="track-artist">{artist}</span>'
            f'<span class="track-year"> · {year}</span>'
            f'</div>'
            f'<div class="track-title">{title}</div>'
            f'<div class="track-actions">'
            f'{play_btn}'
            f'{"".join(actions)}'
            f'</div>'
            f'<div class="track-confidence {conf_class}">'
            f'链接置信度: {html.escape(conf_label)}'
            f'</div>'
            f'</div>'
        )
        cards[rank] = card
    return cards


# ---------------------------------------------------------------------------
# HTML page template
# ---------------------------------------------------------------------------
TEMPLATE_HEAD = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title_zh} · hermes-knowledge-base</title>
<meta name="description" content="{desc_escaped}">
<link rel="stylesheet" href="{up}styles.css">
</head>
<body class="detail-page" id="top">
<header class="detail-header">
<a class="back-link" href="{up}">← 返回首页</a>
</header>
<main class="detail-main">
<article class="detail-article">
<div class="detail-title-block">
<span class="type-badge {type_class}">{type_label}</span>
<h1 class="detail-title">{title_zh}</h1>
<p class="detail-title-en">{title}</p>
</div>
"""

TEMPLATE_METADATA_GRID = """
<section class="detail-meta">
{rows}
</section>
"""

# Section template — uses native <details>/<summary> for collapse. The
# `open_attr` is either ' open' (default expanded) or '' (default collapsed).
TEMPLATE_SECTION = """
<section class="detail-section" id="section-{key}">
<details class="section-details"{open_attr}>
<summary class="section-summary">
<span class="section-summary-label">{label}</span>
{tag}
<span class="section-summary-toggle" aria-hidden="true"></span>
</summary>
<div class="markdown-body">
{body}
</div>
</details>
</section>
"""

TEMPLATE_TOC = """
<nav class="detail-toc" aria-label="页内目录">
<div class="toc-title">目录</div>
<ol class="toc-list">
{toc_items}
</ol>
</nav>
"""

TEMPLATE_ACTIONS = """
<nav class="detail-actions">
{source_btn}
<a class="action-link primary" href="{github_url}" target="_blank" rel="noopener">GitHub 文件夹 →</a>
<button class="action-btn" id="copy-path-btn" data-path="{path}">复制 path</button>
<span class="action-feedback" id="copy-feedback" aria-live="polite"></span>
</nav>
<a class="back-to-top" href="#top" aria-label="返回顶部" title="返回顶部">↑</a>
"""

TEMPLATE_FOOTER = """
</article>
</main>
<footer>
<p><a href="{up}">hermes-knowledge-base</a> · 站内详情页</p>
</footer>
<script src="../../app.js" defer></script>
<script>
(function() {{
  const btn = document.getElementById('copy-path-btn');
  const fb = document.getElementById('copy-feedback');
  if (btn) {{
    btn.addEventListener('click', function() {{
      const path = btn.getAttribute('data-path') || '';
      const done = function() {{
        if (fb) {{
          fb.textContent = '已复制: ' + path;
          setTimeout(function() {{ fb.textContent = ''; }}, 2500);
        }}
      }};
      if (navigator.clipboard && navigator.clipboard.writeText) {{
        navigator.clipboard.writeText(path).then(done, function() {{
          // Fallback for non-secure contexts.
          const ta = document.createElement('textarea');
          ta.value = path;
          document.body.appendChild(ta);
          ta.select();
          try {{ document.execCommand('copy'); done(); }} catch (e) {{}}
          document.body.removeChild(ta);
        }});
      }}
    }});
  }}

  // Show/hide the back-to-top button based on scroll position.
  const topBtn = document.querySelector('.back-to-top');
  if (topBtn) {{
    const onScroll = function() {{
      if (window.scrollY > 400) {{
        topBtn.classList.add('visible');
      }} else {{
        topBtn.classList.remove('visible');
      }}
    }};
    window.addEventListener('scroll', onScroll, {{ passive: true }});
    onScroll();
  }}
}})();
</script>
</body>
</html>
"""


def _type_label(type_str: str) -> str:
    return {
        "article": "article",
        "note": "note",
        "project": "project",
        "resource_collection": "collection",
    }.get(type_str, type_str)


# Type-aware section open/close defaults (matches task spec).
# Sections not in the map default to closed.
SECTION_OPEN_BY_TYPE: Dict[str, set[str]] = {
    "article": {"summary", "translation"},
    "resource_collection": {"summary", "collection"},
    "note": {"summary", "source"},
    "project": {"summary", "source"},
}


def _section_open(record_type: str, key: str) -> bool:
    return key in SECTION_OPEN_BY_TYPE.get(record_type, set())


def _build_source_btn(source_url: Any) -> str:
    """Return HTML for the 原文链接 button if source_url is non-empty."""
    if not source_url:
        return ""
    s = str(source_url).strip()
    if not s or s.lower() in ("null", "~", "none"):
        return ""
    safe = html.escape(s, quote=True)
    return (
        f'<a class="action-link source-link" href="{safe}" '
        f'target="_blank" rel="noopener">原文链接 ↗</a>'
    )


def _build_toc_html(toc: List[Tuple[int, str, str]]) -> str:
    """Render the page TOC from collected h2/h3 entries."""
    if not toc:
        return ""
    items: List[str] = []
    for level, text, hid in toc:
        safe_text = html.escape(text)
        items.append(
            f'<li class="toc-item toc-level-{level}">'
            f'<a class="toc-link" href="#{hid}">{safe_text}</a></li>'
        )
    return TEMPLATE_TOC.format(toc_items="\n".join(items))


def _build_metadata_rows(meta: Dict[str, Any]) -> str:
    """Return HTML rows for the metadata grid."""
    rows: List[str] = []

    def _row(label: str, value: Any) -> str:
        if value is None or value == "" or value == []:
            return ""
        if isinstance(value, list):
            chips = "".join(f'<span class="chip">{html.escape(str(v))}</span>' for v in value)
            return f'<div class="meta-row"><div class="meta-label">{html.escape(label)}</div><div class="meta-value meta-tags">{chips}</div></div>'
        return f'<div class="meta-row"><div class="meta-label">{html.escape(label)}</div><div class="meta-value">{html.escape(str(value))}</div></div>'

    rows.append(_row("类型", meta.get("type")))
    rows.append(_row("作者", meta.get("author")))
    rows.append(_row("来源", meta.get("source_site")))
    rows.append(_row("发布日期", meta.get("published_date")))
    rows.append(_row("采集日期", meta.get("captured_date")))
    rows.append(_row("迁移日期", meta.get("migrated_date")))
    rows.append(_row("标签", meta.get("tags")))
    rows.append(_row("主题", meta.get("topics")))
    return "\n".join(r for r in rows if r)


def _build_description(meta: Dict[str, Any], record: Dict[str, Any]) -> str:
    title_zh = meta.get("title_zh") or record.get("title_zh") or meta.get("title") or record.get("title") or ""
    author = meta.get("author") or record.get("author") or ""
    return f"{title_zh} — {author}".strip(" —")


def _primary_body_key(record_type: str) -> str:
    """The section key that holds the main body text (used for TOC)."""
    return {
        "article": "translation",
        "resource_collection": "collection",
        "note": "source",
        "project": "source",
    }.get(record_type, "source")


def _build_sections_html(
    sections: Dict[str, str],
    missing: List[str],
    record_type: str,
    track_cards: Optional[Dict[int, str]] = None,
) -> Tuple[str, List[Tuple[int, str, str]]]:
    """Render all body sections, accumulating a page TOC.

    The page TOC is built only from the *primary* body section
    (`translation` for article, `collection` for resource_collection,
    `source` for note/project). Other sections (notes, source as
    secondary) do NOT contribute to the TOC to keep it focused on the
    main content.

    `track_cards` (optional): when provided, cards are inserted into
    H2 headings that match "#NNN. ..." pattern. Only the primary body
    section receives track cards (avoids duplication if the same
    article is rendered multiple times across sections).

    Returns (sections_html, page_toc).
    """
    out: List[str] = []
    primary_key = _primary_body_key(record_type)
    page_toc: List[Tuple[int, str, str]] = []
    rendered_keys: set[str] = set()

    for key in SECTION_ORDER:
        if key in sections:
            body_md = sections[key]
            # Only the primary section gets track cards.
            cards_for_this = track_cards if key == primary_key else None
            body_html, section_toc = render_markdown(body_md, track_cards=cards_for_this)
            if key == primary_key:
                page_toc.extend(section_toc)
            tag = ""
            if not body_md.strip():
                tag = '<span class="section-tag">空</span>'
            elif not _section_open(record_type, key):
                tag = '<span class="section-tag section-tag-collapsed">默认折叠</span>'
            open_attr = " open" if _section_open(record_type, key) else ""
            out.append(
                TEMPLATE_SECTION.format(
                    key=key,
                    label=SECTION_LABELS.get(key, key),
                    body=body_html or "<p class='placeholder'>暂无该部分</p>",
                    tag=tag,
                    open_attr=open_attr,
                )
            )
            rendered_keys.add(key)
    for key in missing:
        label = SECTION_LABELS.get(key, key)
        # Missing sections: render closed.
        out.append(
            TEMPLATE_SECTION.format(
                key=key,
                label=label,
                body="<p class='placeholder'>暂无该部分</p>",
                tag='<span class="section-tag">未提供</span>',
                open_attr="",
            )
        )
    return "\n".join(out), page_toc


# ---------------------------------------------------------------------------
# Main generation loop
# ---------------------------------------------------------------------------
def render_record_page(record: Dict[str, Any], body: Dict[str, Any]) -> str:
    meta = body["metadata"]
    record_type = body["type"]

    title_zh = meta.get("title_zh") or record.get("title_zh") or meta.get("title") or record.get("title") or "无标题"
    title = meta.get("title") or record.get("title") or ""
    desc = _build_description(meta, record)

    head = TEMPLATE_HEAD.format(
        title_zh=html.escape(title_zh),
        title=html.escape(title) if title else "",
        desc_escaped=html.escape(desc, quote=True),
        up="../../",
        type_class=record_type,
        type_label=html.escape(_type_label(record_type)),
    )

    meta_rows = _build_metadata_rows(meta)
    meta_section = TEMPLATE_METADATA_GRID.format(rows=meta_rows) if meta_rows else ""

    # Music-track cards (only if tracks.yaml present).
    track_cards: Optional[Dict[int, str]] = None
    tracks_data = body.get("tracks_data") or {}
    if isinstance(tracks_data, dict) and isinstance(tracks_data.get("tracks"), list):
        track_cards = _build_track_cards(tracks_data["tracks"])

    sections_html, page_toc = _build_sections_html(
        body["sections"], body["missing"], record_type,
        track_cards=track_cards,
    )
    toc_html = _build_toc_html(page_toc)

    actions = TEMPLATE_ACTIONS.format(
        source_btn=_build_source_btn(meta.get("source_url")),
        github_url=GITHUB_REPO_BASE + record["path"],
        path=record["path"],
    )

    footer = TEMPLATE_FOOTER.format(up="../../")
    return head + toc_html + meta_section + sections_html + actions + footer


def generate_item_pages() -> int:
    if not CATALOG_JSON.exists():
        print(f"Missing catalog: {CATALOG_JSON}")
        print("Run scripts/export_site_data.py first.")
        return 1

    records: List[Dict[str, Any]] = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    # Sort by path so iteration order is stable across re-runs. export_site_data.py
    # already sorts, but reading from a stale jsonl or pre-optimization catalog
    # could leave records in arbitrary order. This guarantees the HTML pages
    # are generated in the same order every time.
    records.sort(key=lambda r: r.get("path", ""))
    content_root = REPO_ROOT

    if ITEMS_DIR.exists():
        # Don't wipe unrelated subdirs — only remove old item directories
        # that no longer correspond to a current record. This keeps the
        # site/items/ tree idempotent across re-runs without nuking any
        # future non-record subdirs.
        active_slugs = {slug_from_path(r["path"]) for r in records if r.get("path")}
        for existing in list(ITEMS_DIR.iterdir()):
            if not existing.is_dir():
                continue
            if existing.name not in active_slugs:
                # Only remove if it looks like a generated item page
                # (contains index.html). Manual subdirs are preserved.
                if (existing / "index.html").exists():
                    import shutil
                    shutil.rmtree(existing)
                    print(f"  Pruned stale item dir: {existing.name}")

    generated = 0
    skipped = 0
    for record in records:
        path_str = record.get("path", "")
        slug = slug_from_path(path_str)
        if not slug:
            print(f"  Skipping record without path: {record.get('title_zh') or record.get('title')}")
            skipped += 1
            continue
        if not path_str.startswith("content/"):
            print(f"  Skipping record with non-content path: {path_str}")
            skipped += 1
            continue
        body = load_record_body(record, content_root)
        html_doc = render_record_page(record, body)
        out_dir = ITEMS_DIR / slug
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "index.html").write_text(html_doc, encoding="utf-8")
        generated += 1
    print(f"Generated {generated} item pages under {ITEMS_DIR} (skipped: {skipped}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(generate_item_pages())
