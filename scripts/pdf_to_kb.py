#!/usr/bin/env python3
"""Local PDF (text-layer) -> Hermes KB import.

Conservative importer for **extractable-text** PDFs only. Uses `pymupdf`
(`fitz`) for text extraction. Scanned PDFs (no embedded text layer) are
hard-stopped as `BLOCKED_NEEDS_OCR` instead of attempting OCR in this script
— OCR is the responsibility of the existing `pdf-ocr-kb-import` workflow
(see `docs/import-recipes/PDF_OCR_LOCAL.md`).

Hard constraints:
- No video / network egress in the text-extraction phase.
- No OCR, no Tesseract invocation here. OCR is owned by the PDF_OCR_LOCAL
  recipe, which is a separate, downstream tool.
- No cookies / no login state / no impersonation.
- `BLOCKED_NEEDS_OCR` / `BLOCKED_INCOMPLETE_TEXT` / `BLOCKED_UNSUPPORTED`
  are all hard-stops — they never produce partial KB entries.
- Dedup by `pdf_sha256` (file content) AND by (title, author, page_count)
  tuple AND by extracted `content_hash`. SKIPPED_DUPLICATE returns the
  existing entry and writes nothing new.

Usage:
    python scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --dry-run
    python scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --import
    python scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --allow-partial-text
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

KB_HOME = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = KB_HOME / "scripts"
CONTENT_DIR = KB_HOME / "content"
ARTICLES_DIR = CONTENT_DIR / "articles"
INBOX_PDF = KB_HOME / "inbox" / "raw" / "pdf"
UPDATER = SCRIPTS_DIR / "update_site.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

try:
    import fitz  # PyMuPDF
except ImportError as exc:  # pragma: no cover - import guarded for clarity
    raise SystemExit(
        "pymupdf is required for pdf_to_kb.py. Install with: pip install --user pymupdf"
    ) from exc

import import_wechat_article_capture as kb_helpers  # type: ignore

STATUS_IMPORTED = "IMPORTED"
STATUS_DRY_RUN_OK = "DRY_RUN_OK"
STATUS_DRY_RUN_DUPLICATE = "DRY_RUN_DUPLICATE"
STATUS_SKIPPED_DUPLICATE = "SKIPPED_DUPLICATE"
STATUS_BLOCKED_UNSUPPORTED = "BLOCKED_UNSUPPORTED"
STATUS_BLOCKED_NEEDS_OCR = "BLOCKED_NEEDS_OCR"
STATUS_BLOCKED_INCOMPLETE_TEXT = "BLOCKED_INCOMPLETE_TEXT"
STATUS_FAILED_IMPORT = "FAILED_IMPORT"
STATUS_FAILED_GATE = "FAILED_GATE"

# Minimum thresholds (these mirror web_article_to_kb.py when content is text)
MIN_TOTAL_CHARS = 400
MIN_AVG_CHARS_PER_PAGE = 80
MIN_PARAGRAPHS = 2
MIN_CJK_CHARS_FOR_CHINESE_PDF = 80
MIN_ENGLISH_WORDS = 80

# Reasonable safety caps (so a 1000-page PDF doesn't try to import everything)
MAX_PAGES = 200
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB


class PdfImportError(Exception):
    """Hard-stop signal caught by main()."""

    def __init__(self, status: str, message: str):
        super().__init__(message)
        self.status = status
        self.message = message


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import a local text-layer PDF into Hermes KB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--pdf-file", required=True, help="absolute or workspace-relative path to a local PDF file"
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="validate and report; do not write KB entries")
    mode.add_argument("--import", dest="do_import", action="store_true", help="write the KB article entry")
    parser.add_argument(
        "--allow-partial-text",
        action="store_true",
        help="relax MIN_TOTAL_CHARS threshold; still BLOCKED if a scanned PDF",
    )
    parser.add_argument(
        "--no-localize-images",
        action="store_true",
        help="keep any extracted image references as remote URLs (default behavior here)",
    )
    return parser


def now_stamp() -> tuple[str, str]:
    now = dt.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S"), now.strftime("%Y-%m-%dT%H:%M:%S")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(64 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def extract_text_with_metadata(pdf_path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Return (per-page records, pdf-level metadata) using pymupdf.

    Each per-page record is {page, char_count, text}. Pages with zero characters
    are kept (so the caller can detect scanned pages) but flagged.
    """
    if not pdf_path.exists():
        raise PdfImportError(STATUS_FAILED_IMPORT, f"PDF not found: {pdf_path}")

    file_size = pdf_path.stat().st_size
    if file_size > MAX_FILE_SIZE:
        raise PdfImportError(
            STATUS_BLOCKED_UNSUPPORTED,
            f"PDF exceeds 50MB safety cap ({file_size} bytes); split it first",
        )

    try:
        doc = fitz.open(pdf_path)
    except Exception as exc:
        raise PdfImportError(STATUS_BLOCKED_UNSUPPORTED, f"cannot open PDF: {exc}") from exc

    if doc.is_encrypted or doc.needs_pass:
        doc.close()
        raise PdfImportError(
            STATUS_BLOCKED_UNSUPPORTED, "encrypted/password-protected PDFs are not supported"
        )

    pdf_meta = doc.metadata or {}
    raw_metadata = {
        "title": pdf_meta.get("title") or "",
        "author": pdf_meta.get("author") or "",
        "subject": pdf_meta.get("subject") or "",
        "producer": pdf_meta.get("producer") or "",
        "creator": pdf_meta.get("creator") or "",
        "creation_date": str(pdf_meta.get("creationDate") or ""),
        "mod_date": str(pdf_meta.get("modDate") or ""),
        "page_count": doc.page_count,
        "encrypted": False,
        "file_size": file_size,
        "file_name": pdf_path.name,
        "absolute_path": str(pdf_path.resolve()),
    }

    if doc.page_count == 0:
        doc.close()
        raise PdfImportError(STATUS_BLOCKED_INCOMPLETE_TEXT, "PDF has zero pages")

    if doc.page_count > MAX_PAGES:
        doc.close()
        raise PdfImportError(
            STATUS_BLOCKED_UNSUPPORTED,
            f"PDF exceeds {MAX_PAGES} pages ({doc.page_count}); split it first",
        )

    pages: list[dict[str, Any]] = []
    for idx in range(doc.page_count):
        page = doc.load_page(idx)
        text = page.get_text("text") or ""
        text = text.strip()
        pages.append(
            {
                "page": idx + 1,
                "char_count": len(text),
                "text": text,
            }
        )

    doc.close()
    return pages, raw_metadata


def join_page_text(pages: list[dict[str, Any]], max_pages: int | None = None) -> str:
    """Concatenate per-page text with page-tag separators."""
    chunks: list[str] = []
    iterable = pages if max_pages is None else pages[:max_pages]
    for p in iterable:
        if not p["text"]:
            continue
        chunks.append(f"\n\n<!-- page {p['page']} -->\n\n{p['text']}")
    return "\n".join(chunks).strip()


def classify_pdf(pages: list[dict[str, Any]], raw_meta: dict[str, Any], allow_partial: bool) -> dict[str, Any]:
    """Return classification dict describing the PDF.

    classification keys:
      - has_text_layer (bool)
      - total_chars (int)
      - avg_chars_per_page (float)
      - empty_page_count (int)
      - non_empty_page_count (int)
      - cjk_char_count (int)
      - page_count (int)
      - is_chinese (bool)
      - source_language (str)
      - file_sha256 (str)  -- set later
      - text_layer_strategy ("full" | "partial" | "needs_ocr")
      - hard_stop (str or "")
      - hard_stop_reason (str or "")
    """
    total_chars = sum(p["char_count"] for p in pages)
    page_count = len(pages)
    avg_chars = total_chars / max(page_count, 1)
    empty_count = sum(1 for p in pages if p["char_count"] == 0)
    non_empty_count = page_count - empty_count

    full_text = "\n".join(p["text"] for p in pages)
    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", full_text))
    has_cjk = cjk_count > 0 and (cjk_count / max(total_chars, 1)) > 0.05
    is_chinese = has_cjk
    source_language = "zh-CN" if is_chinese else ("en" if total_chars > 0 else "")

    cls: dict[str, Any] = {
        "has_text_layer": total_chars > 0,
        "total_chars": total_chars,
        "avg_chars_per_page": round(avg_chars, 2),
        "empty_page_count": empty_count,
        "non_empty_page_count": non_empty_count,
        "cjk_char_count": cjk_count,
        "page_count": page_count,
        "is_chinese": is_chinese,
        "source_language": source_language,
        "text_layer_strategy": "full",
        "hard_stop": "",
        "hard_stop_reason": "",
    }

    # Scanned detection
    if total_chars == 0 or (empty_count / max(page_count, 1)) >= 0.6 and total_chars < page_count * 10:
        cls["text_layer_strategy"] = "needs_ocr"
        cls["hard_stop"] = STATUS_BLOCKED_NEEDS_OCR
        cls["hard_stop_reason"] = (
            f"PDF appears to be scanned: total_chars={total_chars}, "
            f"empty_page_count={empty_count}/{page_count}. "
            "Use the pdf-ocr-kb-import workflow instead."
        )
        return cls

    if avg_chars < MIN_AVG_CHARS_PER_PAGE and not allow_partial:
        cls["text_layer_strategy"] = "partial"
        # Not a hard stop on its own -- we still have a flag for it.
    return cls


def count_paragraphs(pages: list[dict[str, Any]]) -> int:
    """Count paragraphs across pages.

    A paragraph may be separated by:
      - a blank line (\n\n)
      - a single newline (real-world PDFs frequently use single-newline)
      - a >40 char gap

    We treat each non-empty line as at least one paragraph, so a long PDF
    with continuous paragraphs still passes the gate.
    """
    count = 0
    for p in pages:
        text = p["text"]
        if not text:
            continue
        # split on any newline, count non-blank lines
        lines = [ln for ln in text.split("\n") if ln.strip()]
        count += len(lines)
    return count


def validate_for_import(
    pages: list[dict[str, Any]], cls: dict[str, Any], allow_partial: bool
) -> tuple[bool, str]:
    """Check the gate thresholds; return (allowed, reason)."""
    if cls["text_layer_strategy"] == "needs_ocr":
        return False, cls["hard_stop_reason"]

    total = cls["total_chars"]
    if total < (MIN_TOTAL_CHARS // 2 if allow_partial else MIN_TOTAL_CHARS):
        return False, f"total chars too low ({total} < {MIN_TOTAL_CHARS})"

    paragraphs = count_paragraphs(pages)
    if paragraphs < MIN_PARAGRAPHS and not allow_partial:
        return False, f"too few paragraphs ({paragraphs} < {MIN_PARAGRAPHS})"

    if cls["is_chinese"]:
        if cls["cjk_char_count"] < MIN_CJK_CHARS_FOR_CHINESE_PDF and not allow_partial:
            return False, f"too few CJK chars ({cls['cjk_char_count']} < {MIN_CJK_CHARS_FOR_CHINESE_PDF})"
    else:
        words = sum(len(re.findall(r"[A-Za-z]+", p["text"])) for p in pages)
        if words < MIN_ENGLISH_WORDS and not allow_partial:
            return False, f"too few English words ({words} < {MIN_ENGLISH_WORDS})"

    return True, ""


def _read_yaml_field(text: str, key: str) -> str:
    """Tiny YAML scalar extraction (avoids extra dep)."""
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", re.MULTILINE)
    for line in text.splitlines():
        m = pattern.match(line)
        if not m:
            continue
        value = m.group(1).strip()
        if value.startswith('"') and value.endswith('"'):
            return value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            return value[1:-1]
        return value
    return ""


def build_dedup_index() -> dict[str, dict[str, str]]:
    """Index existing KB articles for PDF-specific dedup keys."""
    index: dict[str, dict[str, str]] = {
        "by_pdf_sha256": {},
        "by_path": {},
        "by_title_author_pages": {},
        "by_source_path": {},
    }
    if not ARTICLES_DIR.exists():
        return index

    for meta in ARTICLES_DIR.rglob("metadata.yaml"):
        rel = meta.parent.relative_to(KB_HOME).as_posix()
        try:
            text = meta.read_text(encoding="utf-8")
        except OSError:
            continue
        source_site = _read_yaml_field(text, "source_site")
        title = _read_yaml_field(text, "title")
        author = _read_yaml_field(text, "author")
        if source_site == "local":
            local_source = _read_yaml_field(text, "local_source")
            sha = _read_yaml_field(text, "source_pdf_sha256")
            if local_source:
                index["by_source_path"].setdefault(local_source, rel)
            if sha:
                index["by_pdf_sha256"].setdefault(sha, rel)
        # title + author + page_count key
        raw_payload = meta.parent / "raw_payload.json"
        page_count = ""
        if raw_payload.exists():
            try:
                payload = json.loads(raw_payload.read_text(encoding="utf-8"))
                page_count = str(payload.get("page_count") or "")
            except Exception:
                page_count = ""
        if title and author and page_count:
            index["by_title_author_pages"].setdefault(
                f"{title}\0{author}\0{page_count}", rel
            )
    return index


def find_duplicate(
    sha: str,
    abs_path: str,
    title: str,
    author: str,
    page_count: int,
    index: dict[str, dict[str, str]],
) -> tuple[str, str]:
    """Return (status, relative_path) where status is one of the duplicate markers
    or '' if no duplicate found."""
    if sha and index["by_pdf_sha256"].get(sha):
        return STATUS_SKIPPED_DUPLICATE, index["by_pdf_sha256"][sha]
    if index["by_source_path"].get(abs_path):
        return STATUS_SKIPPED_DUPLICATE, index["by_source_path"][abs_path]
    if title and author and page_count > 0:
        key = f"{title}\0{author}\0{page_count}"
        if index["by_title_author_pages"].get(key):
            return STATUS_SKIPPED_DUPLICATE, index["by_title_author_pages"][key]
    return "", ""


def slugify_date_title(captured_date: dt.date, title: str) -> str:
    base = kb_helpers.slugify(title, max_len=40) or "pdf-document"
    return f"{captured_date.isoformat()}-{base}"


def build_capture(
    pdf_path: Path,
    pages: list[dict[str, Any]],
    cls: dict[str, Any],
    raw_meta: dict[str, Any],
    sha: str,
    captured_at: str,
) -> dict[str, Any]:
    page_text = join_page_text(pages)
    return {
        "schema_version": 1,
        "kind": "pdf_text_layer_capture",
        "pdf_file": str(pdf_path.resolve()),
        "pdf_file_name": pdf_path.name,
        "pdf_sha256": sha,
        "pdf_file_size": pdf_path.stat().st_size,
        "extracted_at": captured_at,
        "extraction_backend": "pymupdf",
        "page_count": cls["page_count"],
        "total_chars": cls["total_chars"],
        "source_language": cls["source_language"],
        "is_chinese": cls["is_chinese"],
        "cjk_char_count": cls["cjk_char_count"],
        "title": raw_meta.get("title") or pdf_path.stem,
        "author": raw_meta.get("author") or "",
        "subject": raw_meta.get("subject") or "",
        "pdf_metadata": {
            "producer": raw_meta.get("producer", ""),
            "creator": raw_meta.get("creator", ""),
            "creation_date": raw_meta.get("creation_date", ""),
            "mod_date": raw_meta.get("mod_date", ""),
        },
        "content_markdown": page_text,
        "page_records": [
            {"page": p["page"], "char_count": p["char_count"]} for p in pages
        ],
        "text_layer_strategy": cls["text_layer_strategy"],
        "classification": cls,
    }


def render_source_md(capture: dict[str, Any]) -> str:
    title = capture["title"]
    author = capture["author"]
    sha = capture["pdf_sha256"]
    page_count = capture["page_count"]
    producer = capture["pdf_metadata"].get("producer", "")
    creation = capture["pdf_metadata"].get("creation_date", "")
    body = capture["content_markdown"]
    return (
        f"# {title}\n\n"
        f"_Author: {author or 'Unknown'}_\n"
        f"_Pages: {page_count} | "
        f"Producer: {producer or 'unknown'} | "
        f"PDF CreationDate: {creation or 'unknown'} | "
        f"SHA256: `{sha}`_\n\n"
        "---\n\n"
        "## Extracted Text\n\n"
        f"{body}\n"
    )


def render_translation_md(capture: dict[str, Any]) -> str:
    """For text-layer PDFs, we don't have a real translation engine in v0.3.86.

    The output mirrors the source body but is marked needs_review; consumers
    should treat it as a placeholder and either supply a real translation
    or accept the source-only entry.
    """
    title = capture["title"]
    return (
        f"# {title}（占位翻译）\n\n"
        "> 注：v0.3.86 PDF 路由不内置翻译引擎；本文件由 `pdf_to_kb.py` 自动生成"
        "并标记为占位，等待人工/下游翻译管线补充。\n"
        "> 若不需要翻译，可在 `metadata.yaml` 中将 "
        "`translation_language` 设为 `null` 并删除本文件。\n\n"
        "## 翻译占位\n\n"
        f"原文摘要请见 `source.md`（共 {capture['page_count']} 页，"
        f"{capture['total_chars']} 字符）。\n"
    )


def render_summary_md(capture: dict[str, Any]) -> str:
    title = capture["title"]
    author = capture["author"]
    pages = capture["page_count"]
    return (
        f"# 总结：{title}\n\n"
        f"- **作者**：{author or '未知'}\n"
        f"- **页数**：{pages}\n"
        f"- **来源语言**：{capture['source_language']}\n"
        f"- **正文长度**：{capture['total_chars']} 字符\n\n"
        "## 一句话总结\n\n"
        f"待填写（基于 {pages} 页文本）。\n\n"
        "## 核心问题\n\n- 待填写\n\n"
        "## 主要观点\n\n- 待填写\n\n"
        "## 关键概念\n\n- 待填写\n"
    )


def render_notes_md(capture: dict[str, Any]) -> str:
    title = capture["title"]
    return (
        f"# 阅读笔记：{title}\n\n"
        "## 我接受的观点\n\n- 待填写\n\n"
        "## 我反思的观点\n\n- 待填写\n\n"
        "## 可执行行动\n\n- 待填写\n\n"
        "## 复读提醒\n\n- 待填写\n"
    )


def render_metadata_yaml(capture: dict[str, Any], wc: dict[str, int], slug: str) -> str:
    raw = capture
    is_chinese = raw["is_chinese"]
    tags = ["pdf", "local-document", "text-layer"]
    topics = ["Local PDF"]
    if is_chinese:
        tags.append("chinese-source")
        translation_language = "zh-CN"
        is_translation_mirror = True
    else:
        translation_language = "zh-CN"
        is_translation_mirror = False
    today = raw["extracted_at"][:10]
    lines = [
        f'title: "{_yaml_escape(raw["title"])}"',
        f'title_zh: "{_yaml_escape(raw["title"])}"',
        f'author: "{_yaml_escape(raw["author"]) or "Unknown"}"',
        'source_url: ""',
        'source_url_missing: true',
        'source_site: "local"',
        'type: "article"',
        'content_kind: "pdf_document"',
        f'local_source: "{_yaml_escape(raw["pdf_file"])}"',
        f'source_pdf_sha256: "{raw["pdf_sha256"]}"',
        f'published_date: "{_today_iso(raw["pdf_metadata"].get("creation_date", "")) or today}"',
        f'captured_date: "{today}"',
        f'language: "{raw["source_language"] or "en"}"',
        f'translation_language: "{translation_language}"',
        'is_translation_mirror: true' if is_translation_mirror else 'is_translation_mirror: false',
        f'extraction_method: "pymupdf-{capture["pdf_metadata"].get("producer", "unknown")[:32] or "unknown"}"',
        f'extraction_scope: "all {raw["page_count"]} pages extracted"',
        'status: "translated"',
        'topics:',
    ]
    for t in topics:
        lines.append(f'  - "{_yaml_escape(t)}"')
    lines.append('tags:')
    for tg in tags:
        lines.append(f'  - "{_yaml_escape(tg)}"')
    lines.append('word_count:')
    lines.append(f'  source: {wc["source"]}')
    lines.append(f'  translation: {wc["translation"]}')
    return "\n".join(lines) + "\n"


def _yaml_escape(value: str) -> str:
    return (value or "").replace('"', '\\"')


def _today_iso(date_str: str) -> str:
    if not date_str:
        return ""
    m = re.match(r"(\d{4})(\d{2})(\d{2})", date_str)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return ""


def write_capture(capture: dict[str, Any], dry_run: bool) -> Path | None:
    INBOX_PDF.mkdir(parents=True, exist_ok=True)
    slug = slugify_date_title(
        dt.datetime.strptime(capture["extracted_at"][:10], "%Y-%m-%d").date(),
        capture["title"],
    )
    safe_sha = (capture.get("pdf_sha256") or "noSHA")[:16]
    out = INBOX_PDF / f"{slug}-{safe_sha}.json"
    if dry_run:
        # Dry-run: still write to inbox so the capture is auditable,
        # but mark it explicitly with a dry_run flag.
        capture = {**capture, "dry_run": True}
    out.write_text(json.dumps(capture, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def build_article_entry(capture: dict[str, Any]) -> Path:
    today = capture["extracted_at"][:10]
    slug = slugify_date_title(
        dt.datetime.strptime(today, "%Y-%m-%d").date(),
        capture["title"],
    )
    item_dir = ARTICLES_DIR / today[:4] / slug
    item_dir.mkdir(parents=True, exist_ok=True)
    source_path = item_dir / "source.md"
    translation_path = item_dir / "translation.zh-CN.md"
    summary_path = item_dir / "summary.md"
    notes_path = item_dir / "notes.md"
    raw_payload_path = item_dir / "raw_payload.json"
    metadata_path = item_dir / "metadata.yaml"

    source_path.write_text(render_source_md(capture), encoding="utf-8")
    translation_path.write_text(render_translation_md(capture), encoding="utf-8")
    summary_path.write_text(render_summary_md(capture), encoding="utf-8")
    notes_path.write_text(render_notes_md(capture), encoding="utf-8")

    raw_payload = {
        "pdf_file": capture["pdf_file"],
        "pdf_file_name": capture["pdf_file_name"],
        "pdf_sha256": capture["pdf_sha256"],
        "extracted_at": capture["extracted_at"],
        "extraction_backend": capture["extraction_backend"],
        "page_count": capture["page_count"],
        "page_records": capture["page_records"],
        "content_markdown": capture["content_markdown"],
        "content_hash": hashlib.sha256(capture["content_markdown"].encode("utf-8")).hexdigest(),
        "page_count_for_dedup": capture["page_count"],
        "title_for_dedup": capture["title"],
        "author_for_dedup": capture["author"],
        "source_language": capture["source_language"],
    }
    raw_payload_path.write_text(json.dumps(raw_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    src_words = len(re.findall(r"\S+", capture["content_markdown"]))
    trans_words = len(re.findall(r"\S+", translation_path.read_text(encoding="utf-8")))
    metadata_yaml = render_metadata_yaml(
        capture, {"source": src_words, "translation": trans_words}, slug
    )
    metadata_path.write_text(metadata_yaml, encoding="utf-8")

    return item_dir


def run_gates() -> tuple[bool, list[str]]:
    """Run the KB check + page sync gates. Returns (ok, messages)."""
    messages: list[str] = []
    cmds = [
        [sys.executable, str(SCRIPTS_DIR / "check_kb.py")],
        [sys.executable, str(SCRIPTS_DIR / "check_pages_sync.py")],
    ]
    all_ok = True
    for cmd in cmds:
        proc = subprocess.run(cmd, cwd=KB_HOME, capture_output=True, text=True, encoding="utf-8")
        ok = proc.returncode == 0
        all_ok = all_ok and ok
        messages.append(f"$ {' '.join(cmd)} -> rc={proc.returncode}")
    return all_ok, messages


def main() -> int:
    args = build_arg_parser().parse_args()
    if not args.dry_run and not args.do_import:
        args.dry_run = True

    pdf_path = Path(args.pdf_file).expanduser().resolve()
    captured_at = now_stamp()[1]

    # 1. Open + extract
    pages, raw_meta = extract_text_with_metadata(pdf_path)
    # 2. Classify
    cls = classify_pdf(pages, raw_meta, allow_partial=args.allow_partial_text)
    cls["file_sha256"] = file_sha256(pdf_path)
    cls["absolute_path"] = str(pdf_path)

    # 3. Print quick STDOUT summary for the router / operator
    print(
        f"[pdf] pdf={pdf_path} pages={cls['page_count']} "
        f"chars={cls['total_chars']} strategy={cls['text_layer_strategy']}",
        file=sys.stderr,
    )

    # 4. Hard-stop cases
    if cls["hard_stop"] == STATUS_BLOCKED_NEEDS_OCR:
        print(
            f"[pdf] status={STATUS_BLOCKED_NEEDS_OCR} "
            f"reason={cls['hard_stop_reason']}",
            file=sys.stderr,
        )
        # still emit a dry-run capture in inbox for audit
        try:
            sha = cls["file_sha256"]
            capture = {
                "schema_version": 1,
                "kind": "pdf_text_layer_capture",
                "pdf_file": str(pdf_path),
                "pdf_sha256": sha,
                "page_count": cls["page_count"],
                "total_chars": cls["total_chars"],
                "extracted_at": captured_at,
                "extraction_backend": "pymupdf",
                "extraction_status": STATUS_BLOCKED_NEEDS_OCR,
                "blocked_reason": cls["hard_stop_reason"],
                "page_records": [
                    {"page": p["page"], "char_count": p["char_count"]} for p in pages
                ],
                "dry_run": True,
            }
            INBOX_PDF.mkdir(parents=True, exist_ok=True)
            slug = slugify_date_title(
                dt.datetime.strptime(captured_at[:10], "%Y-%m-%d").date(),
                pdf_path.stem,
            )
            capture_path = INBOX_PDF / f"{slug}-{sha[:16]}-BLOCKED_NEEDS_OCR.json"
            capture_path.write_text(
                json.dumps(capture, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"[pdf] capture_json_path: {capture_path}")
        except Exception:
            pass
        print(f"[pdf] status: {STATUS_BLOCKED_NEEDS_OCR}")
        print(f"STATUS: {STATUS_BLOCKED_NEEDS_OCR}")
        return 4  # exit code signals BLOCKED in main()
        # still emit a dry-run capture in inbox for audit
        try:
            sha = cls["file_sha256"]
            capture = {
                "schema_version": 1,
                "kind": "pdf_text_layer_capture",
                "pdf_file": str(pdf_path),
                "pdf_sha256": sha,
                "page_count": cls["page_count"],
                "total_chars": cls["total_chars"],
                "extracted_at": captured_at,
                "extraction_backend": "pymupdf",
                "extraction_status": STATUS_BLOCKED_NEEDS_OCR,
                "blocked_reason": cls["hard_stop_reason"],
                "page_records": [
                    {"page": p["page"], "char_count": p["char_count"]} for p in pages
                ],
                "dry_run": True,
            }
            INBOX_PDF.mkdir(parents=True, exist_ok=True)
            slug = slugify_date_title(
                dt.datetime.strptime(captured_at[:10], "%Y-%m-%d").date(),
                pdf_path.stem,
            )
            capture_path = INBOX_PDF / f"{slug}-{sha[:16]}-BLOCKED_NEEDS_OCR.json"
            capture_path.write_text(
                json.dumps(capture, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            print(f"[pdf] capture_json_path: {capture_path}")
        except Exception:
            pass
        return 4  # exit code signals BLOCKED in main()

    allowed, deny_reason = validate_for_import(
        pages, cls, allow_partial=args.allow_partial_text
    )
    if not allowed:
        print(
            f"[pdf] status={STATUS_BLOCKED_INCOMPLETE_TEXT} reason={deny_reason}",
            file=sys.stderr,
        )
        # emit dry-run capture for audit
        try:
            capture_incomplete = {
                "schema_version": 1,
                "kind": "pdf_text_layer_capture",
                "pdf_file": str(pdf_path),
                "pdf_sha256": cls["file_sha256"],
                "page_count": cls["page_count"],
                "total_chars": cls["total_chars"],
                "extracted_at": captured_at,
                "extraction_backend": "pymupdf",
                "extraction_status": STATUS_BLOCKED_INCOMPLETE_TEXT,
                "blocked_reason": deny_reason,
                "page_records": [
                    {"page": p["page"], "char_count": p["char_count"]} for p in pages
                ],
                "dry_run": True,
            }
            INBOX_PDF.mkdir(parents=True, exist_ok=True)
            sha = cls["file_sha256"]
            slug = slugify_date_title(
                dt.datetime.strptime(captured_at[:10], "%Y-%m-%d").date(),
                pdf_path.stem,
            )
            ipath = INBOX_PDF / f"{slug}-{sha[:16]}-BLOCKED_INCOMPLETE_TEXT.json"
            ipath.write_text(
                json.dumps(capture_incomplete, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"[pdf] capture_json_path: {ipath}")
        except Exception:
            pass
        print(f"[pdf] status: {STATUS_BLOCKED_INCOMPLETE_TEXT}")
        print(f"STATUS: {STATUS_BLOCKED_INCOMPLETE_TEXT}")
        return 4

    # 5. Build capture
    capture = build_capture(pdf_path, pages, cls, raw_meta, cls["file_sha256"], captured_at)

    # 6. Dedup
    index = build_dedup_index()
    dup_status, dup_of = find_duplicate(
        capture["pdf_sha256"],
        capture["pdf_file"],
        capture["title"],
        capture["author"],
        capture["page_count"],
        index,
    )
    if dup_status:
        print(f"[pdf] status={dup_status} duplicate_of={dup_of}", file=sys.stderr)
        capture_path = write_capture(capture, dry_run=True)
        print(f"[pdf] capture_json_path: {capture_path}")
        print(f"[pdf] duplicate_of: {dup_of}")
        print(f"[pdf] status: {dup_status}")
        print(f"STATUS: {dup_status}")
        return 0

    # 7. Write capture JSON (always; both dry-run and import)
    capture_path = write_capture(capture, dry_run=args.dry_run)

    if args.dry_run:
        preview_dir = ARTICLES_DIR / "DRY_RUN_PREVIEW"
        # Dry-run creates a tiny preview file so the user sees exactly what would be written
        preview_dir.mkdir(parents=True, exist_ok=True)
        (preview_dir / "latest_capture.json").write_text(
            json.dumps(capture, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[pdf] capture_json_path: {capture_path}")
        print(f"[pdf] status: {STATUS_DRY_RUN_OK}")
        print(f"STATUS: {STATUS_DRY_RUN_OK}")
        print(
            f"[pdf] page_count: {capture['page_count']} "
            f"chars: {capture['total_chars']} strategy: {capture['text_layer_strategy']}",
            file=sys.stderr,
        )
        return 0

    # 8. Import
    item_dir = build_article_entry(capture)

    # 9. Run gates (incremental site update, not full update_site.py, to keep
    #    this import isolated)
    try:
        item_dir_rel = item_dir.relative_to(KB_HOME).as_posix()
        slug = item_dir.name
        proc = subprocess.run(
            [sys.executable, str(UPDATER), "--only", slug],
            cwd=KB_HOME, capture_output=True, text=True, encoding="utf-8",
        )
        gate_ok = proc.returncode == 0
    except Exception as exc:
        print(f"[pdf] gate run failed: {exc}", file=sys.stderr)
        gate_ok = False

    if not gate_ok:
        print(
            f"[pdf] status={STATUS_FAILED_GATE} kb_article_path={item_dir_rel}",
            file=sys.stderr,
        )
        return 5

    print(f"[pdf] capture_json_path: {capture_path}")
    print(f"[pdf] kb_article_path: {item_dir_rel}")
    print(
        f"[pdf] docs_item_path: docs/items/{item_dir.name}/index.html\n"
        f"[pdf] site_item_path: site/items/{item_dir.name}/index.html"
    )
    print(f"[pdf] status: {STATUS_IMPORTED}")
    print(f"STATUS: {STATUS_IMPORTED}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except PdfImportError as exc:
        print(f"[pdf] status={exc.status} {exc.message}", file=sys.stderr)
        sys.exit(4)
