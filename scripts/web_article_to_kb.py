#!/usr/bin/env python3
"""Generic public web article -> Hermes KB import.

This is a conservative importer for ordinary article pages. It does not log in,
read browser cookies, bypass paywalls, or execute authenticated JavaScript. When
it cannot extract a complete visible article body, it hard-stops instead of
writing a partial KB entry.

Usage:
    python scripts/web_article_to_kb.py --url "<URL>" --dry-run
    python scripts/web_article_to_kb.py --url "<URL>" --import
    python scripts/web_article_to_kb.py --html-file article.html --dry-run
    python scripts/web_article_to_kb.py --markdown-file article.md --dry-run
    python scripts/web_article_to_kb.py --text-file article.txt --dry-run
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
import unicodedata
import urllib.parse
import urllib.robotparser
from pathlib import Path
from typing import Any

KB_HOME = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = KB_HOME / "scripts"
CONTENT_DIR = KB_HOME / "content"
ARTICLES_DIR = CONTENT_DIR / "articles"
INBOX_WEB = KB_HOME / "inbox" / "raw" / "web"
LOCALIZE_SCRIPT = SCRIPTS_DIR / "localize_article_images.py"

if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import import_wechat_article_capture as kb_helpers  # type: ignore

BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

STATUS_IMPORTED = "IMPORTED"
STATUS_DRY_RUN_OK = "DRY_RUN_OK"
STATUS_DRY_RUN_DUPLICATE = "DRY_RUN_DUPLICATE"
STATUS_SKIPPED_DUPLICATE = "SKIPPED_DUPLICATE"
STATUS_BLOCKED_UNSUPPORTED = "BLOCKED_UNSUPPORTED"
STATUS_BLOCKED_FETCH_FAILED = "BLOCKED_FETCH_FAILED"
STATUS_BLOCKED_INCOMPLETE_TEXT = "BLOCKED_INCOMPLETE_TEXT"
STATUS_FAILED_IMPORT = "FAILED_IMPORT"

MIN_VISIBLE_CHARS = 320
MIN_PARAGRAPHS = 3
MIN_CJK_CHARS = 80
MIN_ENGLISH_WORDS = 100

BLOCKED_PAGE_MARKERS = [
    "sign in to continue",
    "log in to continue",
    "login to continue",
    "subscribe to continue",
    "subscription required",
    "paywall",
    "enable javascript",
    "please enable javascript",
    "access denied",
    "forbidden",
    "阅读全文",
    "继续阅读",
    "阅读更多",
    "付费阅读",
    "登录后查看",
    "订阅后继续阅读",
]


class WebArticleError(Exception):
    def __init__(self, status: str, reason: str):
        super().__init__(reason)
        self.status = status
        self.reason = reason


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import a public web article into Hermes KB.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url", help="public ordinary web article URL")
    source.add_argument("--html-file", help="local HTML file saved from an article page")
    source.add_argument("--markdown-file", help="local Markdown article file")
    source.add_argument("--text-file", help="local plain-text article file")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="validate and show outputs without writing KB entry")
    mode.add_argument("--import", dest="do_import", action="store_true", help="write the KB article entry")

    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")
    parser.add_argument("--localize-images", action="store_true", help="download remote Markdown images after import")
    parser.add_argument("--no-localize-images", action="store_true", help="keep remote image URLs as-is (default)")
    return parser


def _now_iso() -> str:
    return dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _today_date() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d")


def slugify(text: str, max_len: int = 48) -> str:
    if not text:
        return "untitled"
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\u4e00-\u9fff\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    if len(text) > max_len:
        head = text[:max_len]
        text = head.rsplit("-", 1)[0] if "-" in head else head
    return text.lower().strip("-") or "untitled"


def _clean_text(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def _decode_response_bytes(raw: bytes, content_type: str) -> str:
    charset = "utf-8"
    if content_type:
        m = re.search(r"charset=([\w.-]+)", content_type, re.IGNORECASE)
        if m:
            charset = m.group(1)
    try:
        return raw.decode(charset, errors="replace")
    except (LookupError, TypeError):
        return raw.decode("utf-8", errors="replace")


def _normalize_url(url: str) -> str:
    if not url:
        return ""
    parsed = urllib.parse.urlsplit(url.strip())
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or "/"
    query = parsed.query
    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


def _domain_of(url: str) -> str:
    return urllib.parse.urlparse(url).netloc.lower()


def _file_url(path: Path) -> str:
    return path.resolve().as_uri()


def _safe_date(value: str) -> str:
    if not value:
        return ""
    value = value.strip()
    m = re.search(r"(\d{4})[-/.年](\d{1,2})[-/.月](\d{1,2})", value)
    if m:
        y, mo, d = m.groups()
        return f"{int(y):04d}-{int(mo):02d}-{int(d):02d}"
    m = re.match(r"(\d{4}-\d{2}-\d{2})", value)
    if m:
        return m.group(1)
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.strftime("%Y-%m-%d")
    except ValueError:
        return ""


def _robots_allows(url: str) -> tuple[bool, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return False, "invalid URL"
    robots_url = urllib.parse.urlunparse((parsed.scheme, parsed.netloc, "/robots.txt", "", "", ""))
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception:
        return True, "robots.txt unavailable; proceeding with ordinary public fetch"
    try:
        if not rp.can_fetch(BROWSER_UA, url) or not rp.can_fetch("*", url):
            return False, f"robots.txt disallows fetching {url}"
    except Exception:
        return True, "robots.txt parse failed; proceeding with ordinary public fetch"
    return True, ""


def fetch_url_html(url: str, timeout: int = 20) -> tuple[str, str]:
    if not url.startswith(("http://", "https://")):
        raise WebArticleError(STATUS_BLOCKED_FETCH_FAILED, "URL must start with http:// or https://")
    host = _domain_of(url)
    if "mp.weixin.qq.com" in host or "youtube.com" in host or "youtu.be" in host:
        raise WebArticleError(STATUS_BLOCKED_UNSUPPORTED, "this route is for ordinary web articles, not WeChat or YouTube")

    allowed, reason = _robots_allows(url)
    if not allowed:
        raise WebArticleError(STATUS_BLOCKED_UNSUPPORTED, reason)

    try:
        import requests  # type: ignore
    except ImportError as exc:
        raise WebArticleError(STATUS_FAILED_IMPORT, "requests is required for --url") from exc

    headers = {
        "User-Agent": BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    except Exception as exc:
        raise WebArticleError(STATUS_BLOCKED_FETCH_FAILED, f"network error fetching URL: {exc}") from exc

    if resp.status_code != 200:
        raise WebArticleError(STATUS_BLOCKED_FETCH_FAILED, f"non-200 HTTP status: {resp.status_code}")
    ctype = resp.headers.get("Content-Type", "")
    if ctype and "html" not in ctype.lower() and "text/plain" not in ctype.lower():
        raise WebArticleError(STATUS_BLOCKED_UNSUPPORTED, f"unsupported Content-Type: {ctype}")
    return _decode_response_bytes(resp.content, ctype), resp.url


def _meta_content(soup, key: str) -> str:
    for attr in ("property", "name", "itemprop"):
        tag = soup.find("meta", attrs={attr: key})
        if tag and tag.get("content"):
            return _clean_text(tag["content"])
    return ""


def _json_ld_objects(soup) -> list[dict[str, Any]]:
    objects: list[dict[str, Any]] = []
    for tag in soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)}):
        raw = tag.string or tag.get_text()
        if not raw or not raw.strip():
            continue
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            continue
        stack = payload if isinstance(payload, list) else [payload]
        while stack:
            obj = stack.pop(0)
            if not isinstance(obj, dict):
                continue
            objects.append(obj)
            graph = obj.get("@graph")
            if isinstance(graph, list):
                stack.extend(graph)
    return objects


def _type_names(obj: dict[str, Any]) -> set[str]:
    typ = obj.get("@type") or obj.get("type")
    if isinstance(typ, list):
        return {str(t).lower() for t in typ}
    if typ:
        return {str(typ).lower()}
    return set()


def _select_jsonld_article(objects: list[dict[str, Any]]) -> dict[str, Any]:
    wanted = {"article", "newsarticle", "blogposting", "reportagearticle", "scholarlyarticle"}
    for obj in objects:
        if _type_names(obj) & wanted:
            return obj
    return {}


def _jsonld_author(value: Any) -> str:
    if isinstance(value, str):
        return _clean_text(value)
    if isinstance(value, dict):
        return _clean_text(str(value.get("name") or ""))
    if isinstance(value, list):
        names = [_jsonld_author(v) for v in value]
        return ", ".join(n for n in names if n)
    return ""


def _jsonld_image(value: Any) -> list[str]:
    if not value:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        url = value.get("url") or value.get("@id")
        return [str(url)] if url else []
    if isinstance(value, list):
        out: list[str] = []
        for v in value:
            out.extend(_jsonld_image(v))
        return out
    return []


def _jsonld_publisher_name(value: Any) -> str:
    if isinstance(value, dict):
        return _clean_text(str(value.get("name") or ""))
    return ""


def _jsonld_main_url(value: Any) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return str(value.get("@id") or value.get("url") or "")
    return ""


def _absolute_url(url: str, base_url: str) -> str:
    if not url:
        return ""
    if url.startswith("data:"):
        return ""
    return urllib.parse.urljoin(base_url, url)


def _html_to_markdown(soup_node, base_url: str) -> str:
    try:
        from bs4 import NavigableString, Tag  # type: ignore
    except ImportError as exc:
        raise WebArticleError(STATUS_FAILED_IMPORT, "beautifulsoup4 is required for HTML parsing") from exc

    lines: list[str] = []

    def emit(text: str) -> None:
        if text:
            lines.append(text)

    def walk(node) -> None:
        if isinstance(node, NavigableString):
            text = re.sub(r"\s+", " ", str(node))
            if text.strip():
                emit(text.strip())
            return
        if not isinstance(node, Tag):
            return
        name = (node.name or "").lower()
        if name in ("script", "style", "noscript", "iframe", "svg", "form", "button"):
            return
        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = min(int(name[1]), 4)
            text = node.get_text(" ", strip=True)
            if text:
                emit("\n" + "#" * level + " " + text + "\n")
            return
        if name == "p":
            text = node.get_text(" ", strip=True)
            if text:
                emit("\n" + text + "\n")
            return
        if name == "br":
            emit("\n")
            return
        if name == "blockquote":
            inner = node.get_text(" ", strip=True)
            if inner:
                emit("\n" + "\n".join("> " + ln.strip() for ln in inner.splitlines() if ln.strip()) + "\n")
            return
        if name in ("ul", "ol"):
            for i, li in enumerate(node.find_all("li", recursive=False), 1):
                marker = f"{i}." if name == "ol" else "-"
                text = li.get_text(" ", strip=True)
                if text:
                    emit(f"\n{marker} {text}")
            emit("\n")
            return
        if name == "img":
            src = node.get("data-src") or node.get("src") or node.get("data-original") or ""
            src = _absolute_url(str(src), base_url)
            alt = _clean_text(str(node.get("alt") or ""))
            if src:
                emit(f"\n![{alt}]({src})\n")
            return
        if name == "a":
            href = _absolute_url(str(node.get("href") or ""), base_url)
            text = node.get_text(" ", strip=True)
            if href and text:
                emit(f"[{text}]({href})")
            elif text:
                emit(text)
            return
        if name in ("strong", "b"):
            text = node.get_text(" ", strip=True)
            if text:
                emit(f"**{text}**")
            return
        if name in ("em", "i"):
            text = node.get_text(" ", strip=True)
            if text:
                emit(f"*{text}*")
            return
        if name == "code":
            text = node.get_text()
            if text:
                emit(f"`{text}`")
            return
        if name == "pre":
            text = node.get_text()
            if text:
                emit("\n```\n" + text.rstrip() + "\n```\n")
            return
        for child in node.children:
            walk(child)

    walk(soup_node)
    raw = "\n".join(lines)
    raw = re.sub(r"[ \t]+\n", "\n", raw)
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


def _remove_page_noise(soup) -> None:
    for selector in ["script", "style", "noscript", "iframe", "svg", "nav", "header", "footer", "aside", "form"]:
        for node in soup.find_all(selector):
            node.decompose()


def _candidate_nodes(soup) -> list[tuple[str, Any]]:
    selectors = [
        ("article", "article"),
        ("main", "main"),
        ("schema_article_body", '[itemprop="articleBody"]'),
        ("article_body_class", ".article-body"),
        ("article_content_class", ".article-content"),
        ("post_content_class", ".post-content"),
        ("entry_content_class", ".entry-content"),
        ("story_body_class", ".story-body"),
        ("content_id", "#content"),
        ("content_class", ".content"),
    ]
    out: list[tuple[str, Any]] = []
    seen: set[int] = set()
    for method, selector in selectors:
        for node in soup.select(selector):
            node_id = id(node)
            if node_id not in seen:
                out.append((method, node))
                seen.add(node_id)
    body = soup.find("body")
    if body is not None:
        out.append(("body_fallback", body))
    return out


def _visible_text_from_markdown(markdown: str) -> str:
    text = kb_helpers.extract_visible_text(markdown)
    text = re.sub(r"^[#>\-\d. ]+", "", text, flags=re.MULTILINE)
    return re.sub(r"\s+", " ", text).strip()


def _score_markdown(markdown: str) -> tuple[int, int, int]:
    visible = _visible_text_from_markdown(markdown)
    paragraphs = [p for p in markdown.split("\n\n") if _visible_text_from_markdown(p)]
    return (len(visible), len(paragraphs), kb_helpers.count_cjk_chars(visible))


def _best_body_from_html(soup, base_url: str, jsonld_article: dict[str, Any]) -> tuple[str, str]:
    _remove_page_noise(soup)
    best_method = ""
    best_md = ""
    best_score = (-1, -1, -1)
    for method, node in _candidate_nodes(soup):
        md = _html_to_markdown(node, base_url)
        score = _score_markdown(md)
        if score > best_score:
            best_method = method
            best_md = md
            best_score = score

    article_body = _clean_text(str(jsonld_article.get("articleBody") or ""))
    if article_body:
        schema_md = "\n\n".join(p.strip() for p in re.split(r"\n{2,}|(?<=[。！？.!?])\s+", article_body) if p.strip())
        schema_score = _score_markdown(schema_md)
        if schema_score[0] > max(best_score[0], MIN_VISIBLE_CHARS):
            return schema_md, "jsonld_article_body"
    return best_md, best_method or "body_fallback"


def _first_nonempty(*values: str) -> str:
    for value in values:
        if value and value.strip():
            return value.strip()
    return ""


def _collect_images(soup, selected_markdown: str, jsonld_article: dict[str, Any], base_url: str) -> list[dict[str, str]]:
    urls: list[tuple[str, str]] = []
    for raw in _jsonld_image(jsonld_article.get("image")):
        abs_url = _absolute_url(raw, base_url)
        if abs_url:
            urls.append((abs_url, "json-ld"))
    for meta_key in ("og:image", "twitter:image", "twitter:image:src"):
        raw = _meta_content(soup, meta_key)
        abs_url = _absolute_url(raw, base_url)
        if abs_url:
            urls.append((abs_url, meta_key))
    for match in re.finditer(r"!\[[^\]]*\]\((https?://[^)]+)\)", selected_markdown):
        urls.append((match.group(1), "markdown"))

    seen: set[str] = set()
    out: list[dict[str, str]] = []
    for url, source in urls:
        if url in seen:
            continue
        seen.add(url)
        out.append({"url": url, "source": source})
    return out[:30]


def parse_html_capture(html: str, source_url: str, final_url: str | None = None) -> dict[str, Any]:
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except ImportError as exc:
        raise WebArticleError(STATUS_FAILED_IMPORT, "beautifulsoup4 is required for HTML parsing") from exc

    final_url = final_url or source_url
    soup = BeautifulSoup(html, "html.parser")
    jsonld_article = _select_jsonld_article(_json_ld_objects(soup))

    page_text = soup.get_text(" ", strip=True).lower()
    for marker in BLOCKED_PAGE_MARKERS:
        if marker in page_text and len(page_text) < 3000:
            raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"blocked or incomplete page marker detected: {marker}")

    title = _first_nonempty(
        _clean_text(str(jsonld_article.get("headline") or "")),
        _clean_text(str(jsonld_article.get("name") or "")),
        _meta_content(soup, "og:title"),
        _meta_content(soup, "twitter:title"),
        _clean_text(soup.title.get_text(" ", strip=True) if soup.title else ""),
        _clean_text(soup.find("h1").get_text(" ", strip=True) if soup.find("h1") else ""),
    )
    if not title:
        raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, "cannot extract article title")

    canonical_tag = soup.find("link", rel=lambda value: value and "canonical" in value)
    canonical_url = ""
    if canonical_tag and canonical_tag.get("href"):
        canonical_url = _absolute_url(str(canonical_tag.get("href")), final_url)
    canonical_url = _first_nonempty(canonical_url, _jsonld_main_url(jsonld_article.get("mainEntityOfPage")), final_url)

    site_name = _first_nonempty(
        _meta_content(soup, "og:site_name"),
        _jsonld_publisher_name(jsonld_article.get("publisher")),
        _domain_of(canonical_url or final_url),
    )
    author = _first_nonempty(
        _jsonld_author(jsonld_article.get("author")),
        _meta_content(soup, "author"),
        _meta_content(soup, "article:author"),
        _meta_content(soup, "twitter:creator"),
        "Unknown",
    )
    published_date = _safe_date(_first_nonempty(
        str(jsonld_article.get("datePublished") or ""),
        _meta_content(soup, "article:published_time"),
        _meta_content(soup, "datePublished"),
        _meta_content(soup, "date"),
        _meta_content(soup, "dc.date"),
        _meta_content(soup, "DC.date.issued"),
    ))
    description = _first_nonempty(
        str(jsonld_article.get("description") or ""),
        _meta_content(soup, "description"),
        _meta_content(soup, "og:description"),
        _meta_content(soup, "twitter:description"),
    )
    content_markdown, extraction_method = _best_body_from_html(soup, canonical_url or final_url, jsonld_article)
    source_language = detect_language(content_markdown)
    validate_content_markdown(content_markdown, title, source_language)
    content_hash = _content_hash(content_markdown)

    capture = {
        "title": title,
        "source_url": source_url,
        "canonical_url": canonical_url,
        "site_name": site_name or _domain_of(final_url),
        "source_site": site_name or _domain_of(final_url),
        "domain": _domain_of(canonical_url or final_url),
        "author": author,
        "published_date": published_date,
        "captured_at": _now_iso(),
        "description": description,
        "source_language": source_language,
        "translation_language": "zh-CN",
        "content_markdown": content_markdown,
        "content_hash": content_hash,
        "extraction_method": extraction_method,
        "images": _collect_images(soup, content_markdown, jsonld_article, canonical_url or final_url),
        "raw": {
            "final_url": final_url,
            "jsonld_article_found": bool(jsonld_article),
        },
    }
    return capture


def parse_markdown_capture(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    title = ""
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+)$", line.strip())
        if m:
            title = m.group(1).strip()
            break
    if not title:
        title = path.stem.replace("-", " ").strip() or "Untitled article"
    source_url = _file_url(path)
    source_language = detect_language(text)
    validate_content_markdown(text, title, source_language)
    return {
        "title": title,
        "source_url": source_url,
        "canonical_url": source_url,
        "site_name": "Local file",
        "source_site": "Local file",
        "domain": "",
        "author": "Unknown",
        "published_date": "",
        "captured_at": _now_iso(),
        "description": "",
        "source_language": source_language,
        "translation_language": "zh-CN",
        "content_markdown": text.strip(),
        "content_hash": _content_hash(text),
        "extraction_method": "local_markdown",
        "images": [],
        "raw": {"local_path": str(path)},
    }


def parse_text_capture(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    title = lines[0] if lines else path.stem.replace("-", " ")
    body = "\n\n".join(lines[1:] if len(lines) > 1 else lines)
    markdown = f"# {title}\n\n{body}" if not body.startswith("#") else body
    source_language = detect_language(markdown)
    validate_content_markdown(markdown, title, source_language)
    source_url = _file_url(path)
    return {
        "title": title,
        "source_url": source_url,
        "canonical_url": source_url,
        "site_name": "Local file",
        "source_site": "Local file",
        "domain": "",
        "author": "Unknown",
        "published_date": "",
        "captured_at": _now_iso(),
        "description": "",
        "source_language": source_language,
        "translation_language": "zh-CN",
        "content_markdown": markdown,
        "content_hash": _content_hash(markdown),
        "extraction_method": "local_text",
        "images": [],
        "raw": {"local_path": str(path)},
    }


def detect_language(markdown: str) -> str:
    visible = _visible_text_from_markdown(markdown)
    cjk = kb_helpers.count_cjk_chars(visible)
    words = len(re.findall(r"[A-Za-z]{2,}", visible))
    if cjk >= 80 and cjk >= words:
        return "zh-CN"
    if words >= 50 and words > cjk:
        return "en"
    return "zh-CN" if cjk else "en"


def validate_content_markdown(markdown: str, title: str, source_language: str) -> None:
    if not markdown or not markdown.strip():
        raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, "content_markdown is empty")
    visible = _visible_text_from_markdown(markdown)
    if len(visible) < MIN_VISIBLE_CHARS:
        raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"content too short ({len(visible)} chars < {MIN_VISIBLE_CHARS})")
    paragraphs = [p for p in markdown.split("\n\n") if len(_visible_text_from_markdown(p)) >= 20]
    if len(paragraphs) < MIN_PARAGRAPHS:
        raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"too few paragraphs ({len(paragraphs)} < {MIN_PARAGRAPHS})")
    lower = visible.lower()
    for marker in BLOCKED_PAGE_MARKERS:
        if marker in lower[-600:]:
            raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"blocked or truncation marker near end: {marker}")
    cjk = kb_helpers.count_cjk_chars(visible)
    words = len(re.findall(r"[A-Za-z]{2,}", visible))
    if source_language == "zh-CN" and cjk < MIN_CJK_CHARS:
        raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"too few Chinese characters ({cjk} < {MIN_CJK_CHARS})")
    if source_language != "zh-CN" and words < MIN_ENGLISH_WORDS:
        raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, f"too few English words ({words} < {MIN_ENGLISH_WORDS})")
    title_clean = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", title)
    body_clean = re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", visible)
    if title_clean and body_clean.startswith(title_clean) and len(body_clean) - len(title_clean) < 240:
        raise WebArticleError(STATUS_BLOCKED_INCOMPLETE_TEXT, "content appears to be only title plus a small snippet")


def _content_hash(markdown: str) -> str:
    visible = _visible_text_from_markdown(markdown)
    return hashlib.sha256(visible.encode("utf-8", errors="replace")).hexdigest()


def _yaml_quote(value: str) -> str:
    return kb_helpers.escape_yaml_string(value or "")


def _yaml_list(items: list[str], indent: int = 0) -> str:
    return kb_helpers.format_yaml_list(items, indent=indent)


def _format_web_images(images: list[dict[str, str]], indent: int = 2) -> str:
    if not images:
        return " " * indent + "[]"
    lines: list[str] = []
    for image in images[:10]:
        lines.append(" " * indent + f'- url: "{_yaml_quote(image.get("url", ""))}"')
        lines.append(" " * (indent + 2) + f'source: "{_yaml_quote(image.get("source", ""))}"')
    return "\n".join(lines)


def _infer_web_tags(content: str, title: str, source_site: str) -> list[str]:
    tags = [t for t in kb_helpers.infer_tags(content, title, source_site) if t not in {"公众号", "微信"}]
    for tag in [source_site, "网页文章", "Web", "阅读", "文章"]:
        if tag and tag not in tags:
            tags.append(tag)
    return tags[:12]


def _captured_date(capture: dict[str, Any]) -> str:
    captured = str(capture.get("captured_at") or "")
    if "T" in captured:
        return captured.split("T", 1)[0]
    return captured[:10] or _today_date()


def _published_or_captured_date(capture: dict[str, Any]) -> str:
    return capture.get("published_date") or _captured_date(capture)


def item_dir_for_capture(capture: dict[str, Any]) -> Path:
    date_part = _published_or_captured_date(capture)
    year = (date_part or _today_date())[:4]
    site_slug = slugify(capture.get("source_site") or capture.get("domain") or "web", max_len=24)
    title_slug = slugify(capture.get("title") or "untitled", max_len=54)
    slug = f"{date_part}-web-{site_slug}-{title_slug}"
    return ARTICLES_DIR / year / slug


def dedupe_key_for_capture(capture: dict[str, Any]) -> str:
    url_key = _normalize_url(capture.get("canonical_url") or capture.get("source_url") or "")
    if url_key:
        digest = hashlib.sha1(url_key.encode("utf-8", errors="replace")).hexdigest()[:12]
        return f"web:{digest}:{slugify(capture.get('title', 'untitled'), max_len=30)}"
    return f"web:{capture.get('content_hash', '')[:12]}:{slugify(capture.get('title', 'untitled'), max_len=30)}"


def _translation_for_capture(capture: dict[str, Any]) -> tuple[str, bool]:
    content = capture.get("content_markdown", "").strip()
    if capture.get("source_language") == "zh-CN":
        return content, True
    title = capture.get("title", "Untitled")
    body_preview = "\n".join(
        line for line in content.splitlines()
        if line.startswith("#") or (line.strip() and not line.startswith("!"))
    )
    body_preview = body_preview[:1800].strip()
    translation = f"""# 中文翻译（待人工补全）：{title}

> 本条目由普通网页导入路线生成。当前仓库未配置稳定翻译引擎，因此这里先保留合法的中文占位草稿，避免伪造完整人工翻译。
> 请在后续人工或 LLM 校对流程中补全正式译文。

## 原文结构参考

{body_preview or "（未提取到可用结构，请查看 source.md）"}
"""
    return translation.strip(), False


def generate_source_md(capture: dict[str, Any]) -> str:
    title = capture.get("title", "Untitled")
    lines = [f"# {title}", ""]
    if capture.get("author"):
        lines.extend([f"**作者**：{capture['author']}", ""])
    if capture.get("source_site"):
        lines.extend([f"**来源**：{capture['source_site']}", ""])
    if capture.get("published_date"):
        lines.extend([f"**发布日期**：{capture['published_date']}", ""])
    if capture.get("canonical_url"):
        lines.extend([f"**Canonical URL**：{capture['canonical_url']}", ""])
    lines.extend([f"**原文链接**：{capture.get('source_url', '')}", "", "---", "", capture.get("content_markdown", "").strip(), ""])
    return "\n".join(lines)


def generate_metadata_yaml(capture: dict[str, Any], item_dir: Path, source_md: str,
                           translation_md: str, is_mirror: bool,
                           localize_images: bool) -> str:
    source_count = int(kb_helpers.count_words_mixed(source_md))
    translation_count = int(kb_helpers.count_cjk_chars(translation_md))
    if translation_count <= 0:
        translation_count = int(kb_helpers.count_words_mixed(translation_md))
    topics = kb_helpers.infer_topics(capture.get("content_markdown", ""), capture.get("title", ""))
    tags = _infer_web_tags(capture.get("content_markdown", ""), capture.get("title", ""), capture.get("source_site", ""))
    captured_date = _captured_date(capture)
    status = "translated" if is_mirror else "needs_translation_review"
    dedupe_key = dedupe_key_for_capture(capture)
    rel_path = item_dir.relative_to(KB_HOME).as_posix() + "/"
    return f'''title: "{_yaml_quote(capture.get('title', ''))}"
title_zh: "{_yaml_quote(capture.get('title', ''))}"
source_url: "{_yaml_quote(capture.get('source_url', ''))}"
canonical_url: "{_yaml_quote(capture.get('canonical_url', ''))}"
source_site: "{_yaml_quote(capture.get('source_site', ''))}"
author: "{_yaml_quote(capture.get('author', 'Unknown'))}"
published_date: "{_yaml_quote(capture.get('published_date', ''))}"
captured_date: "{captured_date}"
language: "{_yaml_quote(capture.get('source_language', ''))}"
source_language: "{_yaml_quote(capture.get('source_language', ''))}"
translation_language: "zh-CN"
status: "{status}"
type: "article"
content_kind: "web_article"
source_platform: "web"
dedupe_key: "{dedupe_key}"
content_hash: "{_yaml_quote(capture.get('content_hash', ''))}"
is_translation_mirror: {str(is_mirror).lower()}
topics:
{_yaml_list(topics, indent=2)}
tags:
{_yaml_list(tags, indent=2)}
word_count:
  source: {source_count}
  translation: {translation_count}
web:
  domain: "{_yaml_quote(capture.get('domain', ''))}"
  extraction_method: "{_yaml_quote(capture.get('extraction_method', ''))}"
  description: "{_yaml_quote(capture.get('description', ''))}"
  image_count: {len(capture.get('images', []))}
  localize_images: {str(localize_images).lower()}
  images:
{_format_web_images(capture.get('images', []), indent=4)}
capture:
  tool: "web_article_to_kb.py"
  captured_at: "{_yaml_quote(capture.get('captured_at', ''))}"
  version: "1.0"
path: "{rel_path}"
'''


def generate_output_bundle(capture: dict[str, Any], localize_images: bool = False) -> dict[str, str]:
    item_dir = item_dir_for_capture(capture)
    source_md = generate_source_md(capture)
    translation_md, is_mirror = _translation_for_capture(capture)
    summary_md = kb_helpers.generate_summary_md(
        capture.get("title", "Untitled"),
        capture.get("content_markdown", ""),
        capture.get("author", ""),
        capture.get("source_site", ""),
    )
    notes_md = kb_helpers.generate_notes_md(capture.get("title", "Untitled"), capture.get("content_markdown", ""))
    metadata_yaml = generate_metadata_yaml(capture, item_dir, source_md, translation_md, is_mirror, localize_images)
    return {
        "metadata.yaml": metadata_yaml,
        "source.md": source_md,
        "translation.zh-CN.md": translation_md,
        "summary.md": summary_md,
        "notes.md": notes_md,
        "raw_payload.json": json.dumps(capture, ensure_ascii=False, indent=2),
    }


def _read_yaml_field(text: str, field: str) -> str:
    m = re.search(rf"^{re.escape(field)}\s*:\s*\"?([^\"\n]*)\"?\s*$", text, re.MULTILINE)
    return m.group(1).strip() if m else ""


def build_existing_index() -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {
        "by_source_url": {},
        "by_canonical_url": {},
        "by_title_site_date": {},
        "by_content_hash": {},
    }
    for meta in CONTENT_DIR.rglob("metadata.yaml"):
        try:
            text = meta.read_text(encoding="utf-8")
        except OSError:
            continue
        rel = meta.parent.relative_to(KB_HOME).as_posix()
        source_url = _read_yaml_field(text, "source_url")
        canonical_url = _read_yaml_field(text, "canonical_url")
        title = _read_yaml_field(text, "title")
        site = _read_yaml_field(text, "source_site")
        published = _read_yaml_field(text, "published_date")
        content_hash = _read_yaml_field(text, "content_hash")
        if source_url:
            index["by_source_url"].setdefault(_normalize_url(source_url), rel)
        if canonical_url:
            index["by_canonical_url"].setdefault(_normalize_url(canonical_url), rel)
        if title and site and published:
            index["by_title_site_date"].setdefault(f"{title}\0{site}\0{published}", rel)
        raw_payload = meta.parent / "raw_payload.json"
        if not content_hash and raw_payload.exists():
            try:
                payload = json.loads(raw_payload.read_text(encoding="utf-8"))
                content_hash = payload.get("content_hash") or _content_hash(payload.get("content_markdown", ""))
            except Exception:
                content_hash = ""
        if not content_hash:
            source_md = meta.parent / "source.md"
            if source_md.exists():
                try:
                    content_hash = _content_hash(source_md.read_text(encoding="utf-8"))
                except OSError:
                    content_hash = ""
        if content_hash:
            index["by_content_hash"].setdefault(content_hash, rel)
    return index


def find_duplicate(capture: dict[str, Any], index: dict[str, dict[str, str]]) -> tuple[str, str, str]:
    source_norm = _normalize_url(capture.get("source_url", ""))
    if source_norm and source_norm in index["by_source_url"]:
        return "source_url", index["by_source_url"][source_norm], "source_url already exists"
    canonical_norm = _normalize_url(capture.get("canonical_url", ""))
    if canonical_norm and canonical_norm in index["by_canonical_url"]:
        return "canonical_url", index["by_canonical_url"][canonical_norm], "canonical_url already exists"
    title = capture.get("title", "").strip()
    site = capture.get("source_site", "").strip()
    published = capture.get("published_date", "").strip()
    key = f"{title}\0{site}\0{published}"
    if title and site and published and key in index["by_title_site_date"]:
        return "title_site_date", index["by_title_site_date"][key], "title + source_site + published_date already exists"
    content_hash = capture.get("content_hash", "")
    if content_hash and content_hash in index["by_content_hash"]:
        return "content_hash", index["by_content_hash"][content_hash], "content_hash already exists"
    return "", "", ""


def _unique_capture_path(capture: dict[str, Any]) -> Path:
    date_part = _published_or_captured_date(capture)
    slug = slugify(capture.get("title", "untitled"), max_len=64)
    base = INBOX_WEB / f"{date_part}-{slug}.json"
    if not base.exists():
        return base
    for i in range(2, 1000):
        candidate = INBOX_WEB / f"{date_part}-{slug}-{i}.json"
        if not candidate.exists():
            return candidate
    raise WebArticleError(STATUS_FAILED_IMPORT, "could not allocate unique capture path")


def write_capture(capture: dict[str, Any]) -> Path:
    INBOX_WEB.mkdir(parents=True, exist_ok=True)
    path = _unique_capture_path(capture)
    path.write_text(json.dumps(capture, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def write_kb_entry(capture: dict[str, Any], bundle: dict[str, str]) -> Path:
    item_dir = item_dir_for_capture(capture)
    if item_dir.exists():
        raise WebArticleError(STATUS_FAILED_IMPORT, f"target article directory already exists: {item_dir.relative_to(KB_HOME).as_posix()}")
    item_dir.mkdir(parents=True)
    for name, text in bundle.items():
        (item_dir / name).write_text(text, encoding="utf-8")
    return item_dir


def localize_images_if_requested(item_dir: Path, localize_images: bool) -> None:
    if not localize_images:
        return
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        [sys.executable, str(LOCALIZE_SCRIPT), "--article-path", str(item_dir.relative_to(KB_HOME).as_posix())],
        cwd=KB_HOME,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )
    if proc.returncode != 0:
        raise WebArticleError(STATUS_FAILED_IMPORT, "localize_article_images.py failed: " + ((proc.stderr or proc.stdout or "")[-300:]))


def build_capture_from_args(args: argparse.Namespace) -> dict[str, Any]:
    if args.url:
        html, final_url = fetch_url_html(args.url, timeout=args.timeout)
        return parse_html_capture(html, source_url=args.url, final_url=final_url)
    if args.html_file:
        path = Path(args.html_file)
        if not path.exists():
            raise WebArticleError(STATUS_BLOCKED_FETCH_FAILED, f"local file not found: {args.html_file}")
        html = path.read_text(encoding="utf-8", errors="replace")
        return parse_html_capture(html, source_url=_file_url(path), final_url=_file_url(path))
    if args.markdown_file:
        path = Path(args.markdown_file)
        if not path.exists():
            raise WebArticleError(STATUS_BLOCKED_FETCH_FAILED, f"local file not found: {args.markdown_file}")
        return parse_markdown_capture(path)
    if args.text_file:
        path = Path(args.text_file)
        if not path.exists():
            raise WebArticleError(STATUS_BLOCKED_FETCH_FAILED, f"local file not found: {args.text_file}")
        return parse_text_capture(path)
    raise WebArticleError(STATUS_BLOCKED_FETCH_FAILED, "no input provided")


def _print_capture_summary(capture: dict[str, Any], capture_path: Path) -> None:
    rel = capture_path.relative_to(KB_HOME).as_posix()
    print(f"[capture] {rel}", file=sys.stderr)
    print(f"  title: {capture.get('title')}", file=sys.stderr)
    print(f"  site: {capture.get('source_site')}", file=sys.stderr)
    print(f"  canonical_url: {capture.get('canonical_url')}", file=sys.stderr)
    print(f"  published_date: {capture.get('published_date')}", file=sys.stderr)
    print(f"  source_language: {capture.get('source_language')}", file=sys.stderr)
    print(f"  content_chars: {len(capture.get('content_markdown', ''))}", file=sys.stderr)


def main() -> int:
    args = build_arg_parser().parse_args()
    dry_run = not args.do_import
    localize_images = bool(args.localize_images and not args.no_localize_images)

    try:
        capture = build_capture_from_args(args)
        capture_path = write_capture(capture)
        _print_capture_summary(capture, capture_path)

        index = build_existing_index()
        dup_layer, duplicate_of, dup_reason = find_duplicate(capture, index)
        if duplicate_of:
            status = STATUS_DRY_RUN_DUPLICATE if dry_run else STATUS_SKIPPED_DUPLICATE
            print(f"DUPLICATE: {dup_reason}", file=sys.stderr)
            print(f"DUPLICATE_LAYER: {dup_layer}", file=sys.stderr)
            print(f"DUPLICATE_OF: {duplicate_of}", file=sys.stderr)
            print(f"\nSTATUS: {status}")
            return 0

        bundle = generate_output_bundle(capture, localize_images=localize_images)
        target_dir = item_dir_for_capture(capture)

        if dry_run:
            print("DRY RUN: Would create the following files:")
            print(f"  Directory: {target_dir}")
            for name, text in bundle.items():
                print(f"    - {name} ({len(text)} chars)")
            print(f"  Dedupe key: {dedupe_key_for_capture(capture)}")
            print(f"  Content hash: {capture.get('content_hash')}")
            print("\nSTATUS: DRY_RUN_OK")
            return 0

        item_dir = write_kb_entry(capture, bundle)
        localize_images_if_requested(item_dir, localize_images)
        print(f"SUCCESS: web article imported to {item_dir}")
        print(f"  Dedupe key: {dedupe_key_for_capture(capture)}")
        print(f"  Content hash: {capture.get('content_hash')}")
        print("\nSTATUS: IMPORTED")
        return 0
    except WebArticleError as exc:
        print(f"{exc.status}: {exc.reason}", file=sys.stderr)
        print(f"\nSTATUS: {exc.status}", file=sys.stderr)
        return 1 if exc.status in {
            STATUS_BLOCKED_UNSUPPORTED,
            STATUS_BLOCKED_FETCH_FAILED,
            STATUS_BLOCKED_INCOMPLETE_TEXT,
        } else 3
    except Exception as exc:
        print(f"{STATUS_FAILED_IMPORT}: unhandled error: {exc}", file=sys.stderr)
        print(f"\nSTATUS: {STATUS_FAILED_IMPORT}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    sys.exit(main())
