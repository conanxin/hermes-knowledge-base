#!/usr/bin/env python3
"""wechat_url_to_kb.py — Direct WeChat Official Account URL → Hermes Knowledge Base import.

This is the WorkBuddy-facing entry point for the short command:

    解读并入库这篇公众号文章：
    <mp.weixin.qq.com 链接>

and the local-file fallback:

    解读并入库这个公众号文章本地文件：
    <本地 html/md/txt 路径>

What it does
------------
1. Accept one of: --url <mp.weixin.qq.com link> | --html-file <path>
   | --markdown-file <path> | --text-file <path>
2. For --url: attempt a *public* fetch of the page (browser-like User-Agent).
   No login, no QR code, no cookie reading, no OpenClaw, no bypass of WeChat
   access restrictions. If the public page does not return a full article body,
   we HARD STOP and tell the user to save the page locally instead.
3. Extract: title, account_name, author, published_date, source_url, full body,
   cover image, digest (when reliably available).
4. Convert the body to Markdown.
5. Emit a standard capture JSON to inbox/raw/wechat/YYYY-MM-DD-<slug>.json
   (schema compatible with scripts/import_wechat_article_capture.py).
6. Invoke scripts/import_wechat_article_capture.py:
     --dry-run (default) → import script runs in --dry-run mode (no KB entry written)
     --import            → import script writes the KB entry under
                           content/articles/YYYY/YYYY-MM-DD-wechat-<account>-<title>/

Hard-stop conditions (HARD STOP, no half-baked KB entry, report only)
---------------------------------------------------------------------
- Full body cannot be retrieved
- Page requires login / returns only an abstract
- Body is obviously truncated or title-only
- WeChat blocks public access
- Title/body correspondence cannot be confirmed
- The downstream import validation fails

Usage
-----
    python3 scripts/wechat_url_to_kb.py --url "<mp.weixin.qq.com链接>" --dry-run
    python3 scripts/wechat_url_to_kb.py --url "<mp.weixin.qq.com链接>" --import
    python3 scripts/wechat_url_to_kb.py --html-file <path> --dry-run
    python3 scripts/wechat_url_to_kb.py --markdown-file <path> --import
    python3 scripts/wechat_url_to_kb.py --text-file <path> --dry-run

Exit codes
----------
0  - Success (dry-run or import both OK)
1  - HARD STOP (content incomplete / blocked / validation failed)
2  - Input error (bad URL, file not found, mutually exclusive flags)
3  - Runtime error (write failure, import script crashed)
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

# --- Heavy imports (requests / bs4) are deferred to where they are actually
#     needed, so that --html-file / --markdown-file / --text-file paths and
#     --help work even if those packages are missing. ---


KB_HOME = Path(__file__).resolve().parent.parent
INBOX_WECHAT = KB_HOME / "inbox" / "raw" / "wechat"
IMPORT_SCRIPT = KB_HOME / "scripts" / "import_wechat_article_capture.py"

WECHAT_HOSTS = ("mp.weixin.qq.com",)
BROWSER_UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Reuse the import script's content validator so the hard-stop rules are
# guaranteed to match exactly what the downstream import will accept.
_IMPORT_SCRIPT_DIR = KB_HOME / "scripts"
if str(_IMPORT_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_IMPORT_SCRIPT_DIR))


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str, max_len: int = 40) -> str:
    """URL-safe slug for Chinese/English text (mirrors import script's slugify)."""
    if not text:
        return "untitled"
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"[^\u4e00-\u9fff\w\s-]", "", text)
    text = re.sub(r"[\s]+", "-", text.strip())
    text = re.sub(r"-+", "-", text)
    if len(text) > max_len:
        head = text[:max_len]
        text = head.rsplit("-", 1)[0] if "-" in head else head
    return text.lower().strip("-") or "untitled"


def _decode_response_bytes(raw: bytes, content_type: str) -> str:
    """Decode HTTP response bytes, preferring charset from Content-Type then meta."""
    charset = "utf-8"
    if content_type:
        m = re.search(r"charset=([\w-]+)", content_type, re.IGNORECASE)
        if m:
            charset = m.group(1)
    try:
        return raw.decode(charset, errors="replace")
    except (LookupError, TypeError):
        return raw.decode("utf-8", errors="replace")


def _is_wechat_url(url: str) -> bool:
    try:
        host = urlparse(url).netloc.lower()
    except Exception:
        return False
    return any(host == h or host.endswith("." + h) for h in WECHAT_HOSTS)


def _now_iso() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def _today_date() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Public URL fetch
# ---------------------------------------------------------------------------

def fetch_url_html(url: str, timeout: int = 20) -> tuple[str, str, int]:
    """Fetch a public URL with a browser-like UA. Returns (html, final_url, status).

    Uses the system proxy env (HTTP_PROXY/HTTPS_PROXY) by default via requests.
    Raises RuntimeError on network failure.
    """
    try:
        import requests  # type: ignore
    except ImportError as e:
        raise RuntimeError("requests is required for --url (pip install requests)") from e

    headers = {
        "User-Agent": BROWSER_UA,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Cache-Control": "no-cache",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    except Exception as e:
        raise RuntimeError(f"network error fetching URL: {e}") from e
    html = _decode_response_bytes(resp.content, resp.headers.get("Content-Type", ""))
    return html, resp.url, resp.status_code


# ---------------------------------------------------------------------------
# HTML → Markdown (lightweight, dependency-only-on-bs4)
# ---------------------------------------------------------------------------

def _html_to_markdown(soup_node) -> str:
    """Convert a BeautifulSoup node into a reasonably clean Markdown string."""
    try:
        from bs4 import NavigableString, Tag  # type: ignore
    except ImportError as e:
        raise RuntimeError("beautifulsoup4 is required for HTML parsing (pip install beautifulsoup4)") from e

    lines: list[str] = []

    def emit(text: str):
        if text:
            lines.append(text)

    def walk(node):
        if isinstance(node, NavigableString):
            text = str(node)
            # Collapse whitespace for inline text nodes
            if text.strip():
                emit(re.sub(r"\s+", " ", text))
            return
        if not isinstance(node, Tag):
            return
        name = node.name.lower()

        # Drop script/style/noscript entirely
        if name in ("script", "style", "noscript", "iframe", "svg"):
            return

        if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
            level = int(name[1])
            emit("\n" + "#" * level + " " + node.get_text(strip=True) + "\n")
            return
        if name == "p":
            text = node.get_text(separator=" ", strip=True)
            if text:
                emit("\n" + text + "\n")
            return
        if name == "br":
            emit("\n")
            return
        if name == "blockquote":
            inner = node.get_text(separator=" ", strip=True)
            if inner:
                for ln in inner.splitlines():
                    emit("\n> " + ln)
                emit("\n")
            return
        if name in ("ul", "ol"):
            for i, li in enumerate(node.find_all("li", recursive=False)):
                marker = f"{i+1}." if name == "ol" else "-"
                emit(f"\n{marker} {li.get_text(' ', strip=True)}")
            emit("\n")
            return
        if name == "img":
            src = node.get("data-src") or node.get("src") or ""
            alt = node.get("alt", "").strip()
            if src:
                emit(f"\n![{alt}]({src})\n")
            return
        if name == "a":
            href = node.get("href", "").strip()
            text = node.get_text(strip=True)
            if href and text:
                emit(f"[{text}]({href})")
            elif text:
                emit(text)
            return
        if name in ("strong", "b"):
            text = node.get_text(strip=True)
            if text:
                emit(f"**{text}**")
            return
        if name in ("em", "i"):
            text = node.get_text(strip=True)
            if text:
                emit(f"*{text}*")
            return
        if name in ("code",):
            text = node.get_text()
            if text:
                emit(f"`{text}`")
            return
        if name == "pre":
            text = node.get_text()
            if text:
                emit("\n```\n" + text.rstrip() + "\n```\n")
            return
        # Default: recurse into children
        for child in node.children:
            walk(child)

    walk(soup_node)
    raw = "\n".join(lines)
    # Collapse 3+ blank lines into 2
    raw = re.sub(r"\n{3,}", "\n\n", raw)
    return raw.strip()


# ---------------------------------------------------------------------------
# WeChat HTML field extraction
# ---------------------------------------------------------------------------

def _meta_content(soup, prop: str) -> str:
    """Read a <meta property=... content=...> or <meta name=... content=...>."""
    for selector_attr in ("property", "name"):
        tag = soup.find("meta", attrs={selector_attr: prop})
        if tag and tag.get("content"):
            return tag["content"].strip()
    return ""


def _clean_text(s: Optional[str]) -> str:
    if not s:
        return ""
    return re.sub(r"\s+", " ", s).strip()


def parse_wechat_html(html: str, source_url: str) -> dict:
    """Parse a WeChat article HTML page into a capture dict.

    Returns a dict with keys: title, source_url, account_name, author,
    published_date, captured_at, content_markdown, cover_url, digest.
    Raises ValueError if the page looks like a login wall / block / abstract-only.
    """
    try:
        from bs4 import BeautifulSoup  # type: ignore
    except ImportError as e:
        raise RuntimeError("beautifulsoup4 is required (pip install beautifulsoup4)") from e

    soup = BeautifulSoup(html, "html.parser")

    # --- Detect login / block / "open in WeChat" walls BEFORE trusting any body ---
    page_text = soup.get_text(" ", strip=True)
    blocked_phrases = [
        "请在微信客户端打开", "请在微信打开", "请使用微信查看", "请在手机端查看",
        "此链接无法在微信外打开", "请使用微信客户端",
        "该内容已被发布者删除", "此内容因违规无法查看", "此内容无法访问",
        "登录后查看", "扫码关注",
    ]
    for bp in blocked_phrases:
        if bp in page_text:
            raise ValueError(f"WeChat blocked / login wall detected: phrase '{bp}' present")

    # --- Title ---
    title = ""
    h1 = soup.find(id="activity-name") or soup.find("h1", class_="rich_media_title") or soup.find("h1")
    if h1:
        title = _clean_text(h1.get_text(" ", strip=True))
    if not title:
        title = _meta_content(soup, "og:title")
    if not title:
        t = soup.find("title")
        if t:
            title = _clean_text(t.get_text())
    # Strip trailing platform suffix like " - 公众号名"
    title = re.sub(r"\s*[-—|]\s*公众号.*$", "", title).strip()
    if not title:
        raise ValueError("cannot extract article title")

    # --- Account name ---
    account_name = ""
    acc_tag = soup.find(id="js_name")
    if acc_tag:
        account_name = _clean_text(acc_tag.get_text(" ", strip=True))
    if not account_name:
        nick = soup.find("strong", class_="profile_nickname")
        if nick:
            account_name = _clean_text(nick.get_text())
    if not account_name:
        account_name = _meta_content(soup, "og:article:author") or _meta_content(soup, "og:nickname")
    if not account_name:
        account_name = ""  # leave empty; import script will treat as missing-required if so

    # --- Author ---
    author = ""
    a_tag = soup.find(id="js_author_name")
    if a_tag:
        raw = _clean_text(a_tag.get_text(" ", strip=True))
        author = re.sub(r"^作者[:：]\s*", "", raw)
    if not author:
        # Sometimes appears as a <span class="rich_media_meta_text">作者：XXX</span>
        for span in soup.find_all("span", class_="rich_media_meta_text"):
            txt = _clean_text(span.get_text())
            m = re.match(r"^作者[:：]\s*(.+)$", txt)
            if m:
                author = m.group(1).strip()
                break
    if not author:
        author = _meta_content(soup, "og:article:author")

    # --- Published date ---
    published_date = ""
    pt_tag = soup.find(id="publish_time")
    if pt_tag:
        raw = _clean_text(pt_tag.get_text(" ", strip=True))
        m = re.search(r"(\d{4}[-/年]\d{1,2}[-/月]\d{1,2})", raw)
        if m:
            published_date = m.group(1).replace("年", "-").replace("月", "-").replace("/", "-")
    if not published_date:
        # Look for var ct = "<unix>" and convert
        m = re.search(r'\bct\s*=\s*["\'](\d{10})["\']', html)
        if m:
            try:
                published_date = _dt.datetime.fromtimestamp(int(m.group(1))).strftime("%Y-%m-%d")
            except (ValueError, OSError):
                pass
    if not published_date:
        # Last resort: og:article:published_time
        ogpt = _meta_content(soup, "og:article:published_time")
        if ogpt:
            m = re.search(r"(\d{4}-\d{2}-\d{2})", ogpt)
            if m:
                published_date = m.group(1)
    if not published_date:
        published_date = _today_date()  # fall back to today; import script accepts it

    # --- Cover & digest (best-effort) ---
    cover_url = _meta_content(soup, "og:image")
    digest = _meta_content(soup, "og:description") or _meta_content(soup, "description")

    # --- Body (the real article) ---
    body_node = (
        soup.find(id="js_content")
        or soup.find("div", class_="rich_media_content")
        or soup.find("div", id="page-content")
    )
    if not body_node:
        raise ValueError("cannot locate article body (#js_content / .rich_media_content missing)")

    content_markdown = _html_to_markdown(body_node)
    if not content_markdown or len(content_markdown) < 50:
        raise ValueError("article body is empty or near-empty after extraction")

    # Title/body correspondence check: title must appear (even loosely) in the
    # page; if the body has no overlap with the title at all, we cannot confirm
    # they belong together.
    title_chars = set(re.findall(r"[\u4e00-\u9fff]", title))
    body_chars = set(re.findall(r"[\u4e00-\u9fff]", content_markdown))
    if title_chars and not (title_chars & body_chars):
        # Allow a small grace: maybe the title is English-only. Only hard-stop
        # when the title has CJK chars but NONE appear in the body.
        raise ValueError("title/body correspondence cannot be confirmed (no shared CJK chars)")

    return {
        "title": title,
        "source_url": source_url,
        "account_name": account_name,
        "author": author,
        "published_date": published_date,
        "captured_at": _now_iso(),
        "content_markdown": content_markdown,
        "cover_url": cover_url,
        "digest": digest,
    }


# ---------------------------------------------------------------------------
# Local file fallbacks
# ---------------------------------------------------------------------------

def parse_html_file(path: Path, source_url_hint: str = "") -> dict:
    html = path.read_text(encoding="utf-8", errors="replace")
    # Prefer an embedded canonical / og:url if present; else the hint; else the file path.
    url = source_url_hint
    if not url:
        try:
            from bs4 import BeautifulSoup  # type: ignore
            soup = BeautifulSoup(html, "html.parser")
            og_url = _meta_content(soup, "og:url")
            if og_url:
                url = og_url
        except Exception:
            pass
    if not url:
        url = f"file://{path.as_posix()}"
    return parse_wechat_html(html, url)


def _infer_frontmatter(text: str) -> tuple[str, str, str, str, str]:
    """Best-effort infer (title, account, author, date, source_url) from raw text.

    Looks for simple 'key: value' lines at the top and a Markdown H1 title.
    Returns empty strings for anything not found.
    """
    title, account, author, date, url = "", "", "", "", ""
    lines = text.splitlines()
    for ln in lines[:30]:
        s = ln.strip()
        if not s:
            continue
        m = re.match(r"^#\s+(.+)$", s)
        if m and not title:
            title = m.group(1).strip()
            continue
        m = re.match(r"^(标题|公众号|账号|来源|作者|发布日期|发布时间|原文链接|链接|URL|source_url)\s*[:：]\s*(.+)$", s, re.IGNORECASE)
        if m:
            k = m.group(1).strip().lower()
            v = m.group(2).strip().strip("<>").strip()
            if k in ("标题",) and not title:
                title = v
            elif k in ("公众号", "账号", "来源") and not account:
                account = v
            elif k in ("作者",) and not author:
                author = v
            elif k in ("发布日期", "发布时间") and not date:
                m2 = re.search(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})", v)
                if m2:
                    date = m2.group(1).replace("/", "-")
            elif k in ("原文链接", "链接", "url", "source_url") and not url:
                url = v
        if title and account and author and date and url:
            break
    return title, account, author, date, url


def parse_markdown_file(path: Path, source_url_hint: str = "") -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    title, account, author, date, url = _infer_frontmatter(text)
    if not title:
        # Use filename stem
        title = path.stem
    if not url:
        url = source_url_hint or f"file://{path.as_posix()}"
    if not date:
        date = _today_date()
    return {
        "title": title,
        "source_url": url,
        "account_name": account or "本地文件",
        "author": author,
        "published_date": date,
        "captured_at": _now_iso(),
        "content_markdown": text.strip(),
        "cover_url": "",
        "digest": "",
    }


def parse_text_file(path: Path, source_url_hint: str = "") -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    title, account, author, date, url = _infer_frontmatter(text)
    if not title:
        title = path.stem
    if not url:
        url = source_url_hint or f"file://{path.as_posix()}"
    if not date:
        date = _today_date()
    # Wrap plain text into pseudo-markdown paragraphs
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    content_markdown = "\n\n".join(paras)
    return {
        "title": title,
        "source_url": url,
        "account_name": account or "本地文件",
        "author": author,
        "published_date": date,
        "captured_at": _now_iso(),
        "content_markdown": content_markdown,
        "cover_url": "",
        "digest": "",
    }


# ---------------------------------------------------------------------------
# Capture JSON write + import invocation
# ---------------------------------------------------------------------------

def write_capture_json(capture: dict, out_dir: Path = INBOX_WECHAT) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    date_str = capture.get("published_date") or _today_date()
    slug = slugify(capture.get("title", "untitled"), max_len=40)
    fname = f"{date_str}-{slug}.json"
    out_path = out_dir / fname
    # Avoid clobbering an existing capture from the same day/slug
    i = 2
    while out_path.exists():
        out_path = out_dir / f"{date_str}-{slug}-{i}.json"
        i += 1
    out_path.write_text(
        json.dumps(capture, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return out_path


def validate_via_import_script(capture_path: Path, dry_run: bool) -> tuple[int, str]:
    """Run import_wechat_article_capture.py on the capture. Returns (exit_code, output)."""
    if not IMPORT_SCRIPT.exists():
        return 3, f"import script not found: {IMPORT_SCRIPT}"
    cmd = [sys.executable, str(IMPORT_SCRIPT)]
    if dry_run:
        cmd.append("--dry-run")
    cmd.append(str(capture_path))
    # Force UTF-8 on the child's stdio so Chinese output decodes correctly on
    # Windows (default system locale is often gbk/cp936).
    child_env = os.environ.copy()
    child_env["PYTHONIOENCODING"] = "utf-8"
    child_env["PYTHONUTF8"] = "1"
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            errors="replace", env=child_env,
        )
    except Exception as e:
        return 3, f"failed to invoke import script: {e}"
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Direct WeChat URL → Hermes KB import (public fetch, no login).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="public mp.weixin.qq.com article URL")
    src.add_argument("--html-file", help="local HTML file saved from a WeChat article")
    src.add_argument("--markdown-file", help="local Markdown file of a WeChat article")
    src.add_argument("--text-file", help="local plain-text file of a WeChat article")

    p.add_argument("--dry-run", action="store_true",
                   help="generate capture JSON + validate via import script in --dry-run mode; do NOT write a KB entry")
    p.add_argument("--import", dest="do_import", action="store_true",
                   help="generate capture JSON and write the KB entry (calls import script without --dry-run)")
    p.add_argument("--out", help="optional explicit output path for the capture JSON")
    p.add_argument("--timeout", type=int, default=20, help="HTTP fetch timeout in seconds (default 20)")
    return p


def main() -> int:
    args = build_arg_parser().parse_args()

    # Default mode: if neither --dry-run nor --import given, default to --dry-run (safe).
    dry_run = True
    if args.do_import:
        dry_run = False

    # --- 1. Obtain a capture dict from the chosen source ---
    capture: dict
    try:
        if args.url:
            if not _is_wechat_url(args.url):
                print("ERROR: --url must be a mp.weixin.qq.com link", file=sys.stderr)
                return 2
            print(f"[fetch] {args.url}", file=sys.stderr)
            try:
                html, final_url, status = fetch_url_html(args.url, timeout=args.timeout)
            except RuntimeError as e:
                print(f"HARD STOP: {e}", file=sys.stderr)
                print("\n这个链接无法直接抓全文，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。",
                      file=sys.stderr)
                return 1
            if status != 200:
                print(f"HARD STOP: non-200 HTTP status ({status}) for {args.url}", file=sys.stderr)
                print("\n这个链接无法直接抓全文，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。",
                      file=sys.stderr)
                return 1
            try:
                capture = parse_wechat_html(html, source_url=final_url or args.url)
            except ValueError as e:
                print(f"HARD STOP: {e}", file=sys.stderr)
                print("\n这个链接无法直接抓全文，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。",
                      file=sys.stderr)
                return 1
        elif args.html_file:
            p = Path(args.html_file)
            if not p.exists():
                print(f"ERROR: file not found: {p}", file=sys.stderr)
                return 2
            try:
                capture = parse_html_file(p)
            except ValueError as e:
                print(f"HARD STOP: {e}", file=sys.stderr)
                print("\n这个文件无法解析出完整正文，请确认它是从公众号文章完整另存的 HTML。",
                      file=sys.stderr)
                return 1
        elif args.markdown_file:
            p = Path(args.markdown_file)
            if not p.exists():
                print(f"ERROR: file not found: {p}", file=sys.stderr)
                return 2
            capture = parse_markdown_file(p)
        elif args.text_file:
            p = Path(args.text_file)
            if not p.exists():
                print(f"ERROR: file not found: {p}", file=sys.stderr)
                return 2
            capture = parse_text_file(p)
        else:
            # Unreachable (mutually exclusive group is required), but keep for safety.
            print("ERROR: must provide exactly one of --url / --html-file / --markdown-file / --text-file",
                  file=sys.stderr)
            return 2
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3

    # --- 2. Write capture JSON ---
    try:
        if args.out:
            out_path = Path(args.out)
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(capture, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        else:
            out_path = write_capture_json(capture)
    except Exception as e:
        print(f"ERROR: failed to write capture JSON: {e}", file=sys.stderr)
        return 3

    rel = out_path.relative_to(KB_HOME) if out_path.is_absolute() and str(out_path).startswith(str(KB_HOME)) else out_path
    print(f"[capture] {rel}", file=sys.stderr)
    print(f"  title: {capture.get('title')}", file=sys.stderr)
    print(f"  account: {capture.get('account_name')}", file=sys.stderr)
    print(f"  author: {capture.get('author')}", file=sys.stderr)
    print(f"  published_date: {capture.get('published_date')}", file=sys.stderr)
    print(f"  content_chars: {len(capture.get('content_markdown', ''))}", file=sys.stderr)

    # --- 3. Invoke the import script (dry-run or real) ---
    code, out = validate_via_import_script(out_path, dry_run=dry_run)
    print(out, file=sys.stderr if code not in (0,) else sys.stdout)
    if code == 1:
        # Import-script HARD STOP (validation failed)
        print("\nHARD STOP: downstream import validation failed. No KB entry was written.",
              file=sys.stderr)
        print("这个链接/文件的正文不完整或被截断，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。",
              file=sys.stderr)
        return 1
    if code == 2:
        print("\nERROR: capture JSON rejected by import script (input error).", file=sys.stderr)
        return 2
    if code == 3:
        print("\nERROR: import script runtime error.", file=sys.stderr)
        return 3

    # code == 0
    if dry_run:
        print("\nSTATUS: DRY_RUN_OK", file=sys.stderr)
    else:
        print("\nSTATUS: PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
