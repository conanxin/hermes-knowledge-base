#!/usr/bin/env python3
"""wechat_batch_import.py — Batch WeChat article → Hermes KB import with dedup.

This is the WorkBuddy-facing entry point for the batch short commands:

    批量解读并入库这些公众号文章：
    <urls.txt 或多行 mp.weixin.qq.com 链接>

    批量解读并入库这些公众号本地文件：
    <files.txt 或多行 .html/.md/.txt 路径>

What it does
------------
1. Accept one or more inputs:
     --input <file>           a file with one URL or local path per line
                              (blank lines and lines starting with '#' are skipped)
     --url "<url>"            a single URL (repeatable: --url A --url B)
     --html-file <path>       a single local HTML file (repeatable)
     --markdown-file <path>   a single local Markdown file (repeatable)
     --text-file <path>       a single local plain-text file (repeatable)
2. For each input, invoke scripts/wechat_url_to_kb.py (which itself invokes
   scripts/import_wechat_article_capture.py). One bad input never crashes
   the whole batch — failures are recorded and the batch continues.
3. Three-layer dedup is applied BEFORE invoking the import script:
   - Layer 1: source_url already exists in content/**/metadata.yaml
   - Layer 2: title + account_name + published_date already exists
   - Layer 3: sha256 of the cleaned visible body already exists
   A duplicate is recorded as SKIPPED_DUPLICATE (or DRY_RUN_DUPLICATE in
   --dry-run mode) and not re-imported.
4. After every input is processed, a manifest is written:
     reports/wechat_batch_import_YYYYMMDD_HHMMSS.md
     reports/wechat_batch_import_YYYYMMDD_HHMMSS.json
5. If --import and at least one IMPORTED result, the script runs the quality
   gates (check_kb / update_site / audit_kb_state / check_pages_sync) at the
   end and records pass/fail in the manifest. Gate failure does NOT unwind
   already-written KB entries — it only blocks commit/push (the operator
   must inspect and decide).

Usage
-----
    python3 scripts/wechat_batch_import.py --input urls.txt --dry-run
    python3 scripts/wechat_batch_import.py --input urls.txt --import
    python3 scripts/wechat_batch_import.py --url "https://mp.weixin.qq.com/s/xxx" --url "..." --dry-run
    python3 scripts/wechat_batch_import.py --html-file a.html --html-file b.html --import

Exit codes
----------
0  - Batch completed (regardless of per-item outcomes). Inspect the manifest.
1  - Hard usage error (no inputs, missing file).
2  - One or more quality gates failed (only set in --import mode).
3  - Runtime error (write failure, etc.).
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

KB_HOME = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = KB_HOME / "scripts"
URL_SCRIPT = SCRIPTS_DIR / "wechat_url_to_kb.py"
IMPORT_SCRIPT = SCRIPTS_DIR / "import_wechat_article_capture.py"
CONTENT_DIR = KB_HOME / "content"
REPORTS_DIR = KB_HOME / "reports"

# Status vocabulary (single source of truth).
S_IMPORTED = "IMPORTED"
S_DRY_RUN_OK = "DRY_RUN_OK"
S_DRY_RUN_DUPLICATE = "DRY_RUN_DUPLICATE"
S_SKIPPED_DUPLICATE = "SKIPPED_DUPLICATE"
S_BLOCKED_FETCH_FAILED = "BLOCKED_FETCH_FAILED"
S_BLOCKED_INCOMPLETE_TEXT = "BLOCKED_INCOMPLETE_TEXT"
S_FAILED_IMPORT = "FAILED_IMPORT"
S_FAILED_GATE = "FAILED_GATE"

# Inputs the URL script accepts (mirror its CLI flags so we can route each
# input line to the right --html-file / --markdown-file / --text-file / --url).
URL_INPUT_FLAGS = {"--url"}
FILE_EXT_TO_FLAG = {
    ".html": "--html-file",
    ".htm": "--html-file",
    ".md": "--markdown-file",
    ".markdown": "--markdown-file",
    ".txt": "--text-file",
}


# ---------------------------------------------------------------------------
# Input parsing
# ---------------------------------------------------------------------------

def _classify_line(line: str) -> Optional[tuple[str, str]]:
    """Classify a single input line into (flag, value).

    Returns None for blank/comment lines. Raises ValueError if the line is
    neither a recognizable URL nor a known file extension.
    """
    s = line.strip()
    if not s or s.startswith("#"):
        return None
    # mp.weixin.qq.com URL
    if s.startswith("http://") or s.startswith("https://"):
        if "mp.weixin.qq.com" in s:
            return ("--url", s)
        # Non-WeChat URL — still try as URL (the URL script will reject it).
        return ("--url", s)
    # Local file path
    p = Path(s)
    ext = p.suffix.lower()
    if ext in FILE_EXT_TO_FLAG:
        return (FILE_EXT_TO_FLAG[ext], s)
    # Bare path without recognized extension — raise so the caller can log
    # an explicit BLOCKED_FETCH_FAILED rather than silently dropping it.
    raise ValueError(f"unrecognized input line (not a URL, not .html/.md/.txt): {s!r}")


def collect_inputs(args: argparse.Namespace) -> list[tuple[str, str]]:
    """Collect all inputs from --input files and repeatable --url/--html-file/..."""
    inputs: list[tuple[str, str]] = []
    # Repeatable flags first (so order is stable & predictable).
    for u in (args.url or []):
        inputs.append(("--url", u))
    for f in (args.html_file or []):
        inputs.append(("--html-file", f))
    for f in (args.markdown_file or []):
        inputs.append(("--markdown-file", f))
    for f in (args.text_file or []):
        inputs.append(("--text-file", f))
    # Then --input files.
    for inp in (args.input or []):
        ip = Path(inp)
        if not ip.exists():
            raise FileNotFoundError(f"--input file not found: {inp}")
        for raw in ip.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                cls = _classify_line(raw)
            except ValueError as e:
                # Record an explicit failure entry instead of crashing.
                inputs.append(("__BAD__", raw.strip()))
                print(f"[warn] {e}", file=sys.stderr)
                continue
            if cls:
                inputs.append(cls)
    return inputs


# ---------------------------------------------------------------------------
# Dedup: build the existing-article index from content/**/metadata.yaml
# ---------------------------------------------------------------------------

# Match source_url: "..." in metadata.yaml (single line). Tolerates both
# double-quoted and unquoted scalars.
_RE_SOURCE_URL = re.compile(r'^source_url\s*:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)
_RE_TITLE = re.compile(r'^title\s*:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)
_RE_SOURCE_SITE = re.compile(r'^source_site\s*:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)
_RE_PUBLISHED_DATE = re.compile(r'^published_date\s*:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)
_RE_DEDUPE_KEY = re.compile(r'^dedupe_key\s*:\s*"?([^"\n]+)"?\s*$', re.MULTILINE)


def _read_yaml_field(text: str, pattern: re.Pattern) -> str:
    m = pattern.search(text)
    return m.group(1).strip() if m else ""


def build_existing_index() -> dict:
    """Scan content/**/metadata.yaml and return a dedup index.

    Returns a dict with:
      by_source_url: {url_norm: item_dir}
      by_title_account_date: {(title, account, date): item_dir}
      by_content_hash: {sha256_hex: item_dir}   (computed on cleaned source.md)
      all_entries: [{path, source_url, title, account, date, dedupe_key}, ...]
    """
    index = {
        "by_source_url": {},
        "by_title_account_date": {},
        "by_content_hash": {},
        "all_entries": [],
    }
    if not CONTENT_DIR.exists():
        return index
    for meta in CONTENT_DIR.rglob("metadata.yaml"):
        try:
            text = meta.read_text(encoding="utf-8")
        except Exception:
            continue
        item_dir = meta.parent
        rel = item_dir.relative_to(KB_HOME).as_posix()
        source_url = _read_yaml_field(text, _RE_SOURCE_URL)
        title = _read_yaml_field(text, _RE_TITLE)
        account = _read_yaml_field(text, _RE_SOURCE_SITE)
        pub_date = _read_yaml_field(text, _RE_PUBLISHED_DATE)
        dedupe_key = _read_yaml_field(text, _RE_DEDUPE_KEY)
        index["all_entries"].append({
            "path": rel + "/",
            "source_url": source_url,
            "title": title,
            "account": account,
            "date": pub_date,
            "dedupe_key": dedupe_key,
        })
        # Layer 1
        if source_url:
            # Normalize: strip trailing slash, drop query/fragment for the key
            # but keep the original for reporting.
            norm = _normalize_url(source_url)
            if norm:
                index["by_source_url"].setdefault(norm, rel)
        # Layer 2
        if title and account and pub_date:
            key2 = (title.strip(), account.strip(), pub_date.strip())
            index["by_title_account_date"].setdefault(key2, rel)
        # Layer 3: hash of cleaned visible body from source.md
        source_md = item_dir / "source.md"
        if source_md.exists():
            try:
                body = source_md.read_text(encoding="utf-8")
                h = _content_hash(body)
                if h:
                    index["by_content_hash"].setdefault(h, rel)
            except Exception:
                pass
    return index


def _normalize_url(url: str) -> str:
    """Normalize a URL for dedup comparison: lowercase host, strip trailing slash."""
    if not url:
        return ""
    s = url.strip().lower()
    # Drop fragment
    if "#" in s:
        s = s.split("#", 1)[0]
    s = s.rstrip("/&")
    return s


def _content_hash(text: str) -> str:
    """sha256 of the cleaned visible text (reuse import script's extractor if available)."""
    try:
        sys.path.insert(0, str(SCRIPTS_DIR))
        import import_wechat_article_capture as m  # type: ignore
        visible = m.extract_visible_text(text)
    except Exception:
        # Fallback: hash the raw text if the import script isn't importable.
        visible = text
    return hashlib.sha256(visible.encode("utf-8", errors="replace")).hexdigest()


# ---------------------------------------------------------------------------
# Per-input processing
# ---------------------------------------------------------------------------

def _run_url_script(flag: str, value: str, dry_run: bool) -> tuple[int, str, str, Optional[Path]]:
    """Invoke wechat_url_to_kb.py with the given flag/value.

    Returns (exit_code, stdout, stderr, capture_json_path).
    The capture JSON path is parsed from the script's stderr line
    '[capture] <rel_path>'.
    """
    cmd = [sys.executable, str(URL_SCRIPT), flag, value]
    if dry_run:
        cmd.append("--dry-run")
    else:
        cmd.append("--import")
    # Force UTF-8 stdio on the child (Windows gbk otherwise breaks Chinese).
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8",
            errors="replace", env=env,
        )
    except Exception as e:
        return 3, "", f"failed to invoke wechat_url_to_kb.py: {e}", None
    out = (proc.stdout or "") + (proc.stderr or "")
    # Parse capture JSON path from stderr.
    cap_path: Optional[Path] = None
    m = re.search(r"\[capture\]\s+(.+?)(?:\s|$)", proc.stderr or "")
    if m:
        candidate = Path(m.group(1).strip())
        # The script prints a path relative to KB_HOME (POSIX or native).
        if not candidate.is_absolute():
            candidate = KB_HOME / candidate
        if candidate.exists():
            cap_path = candidate
    return proc.returncode, proc.stdout or "", proc.stderr or "", cap_path


def _load_capture(cap_path: Path) -> dict:
    try:
        return json.loads(cap_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _parse_imported_kb_path(stdout: str, stderr: str) -> Optional[str]:
    """Extract the 'imported to <path>' line from the import script's output."""
    text = (stdout or "") + (stderr or "")
    m = re.search(r"imported to\s+(.+?)(?:\s|$)", text)
    if m:
        return m.group(1).strip()
    return None


def _classify_url_script_exit(code: int, stderr: str) -> str:
    """Map wechat_url_to_kb.py exit code to a batch status."""
    if code == 0:
        return ""  # caller decides IMPORTED vs DRY_RUN_OK based on mode
    if code == 1:
        # HARD STOP — either fetch failed or content incomplete.
        if any(p in stderr for p in ("无法直接抓全文", "网络错误", "network error", "non-200")):
            return S_BLOCKED_FETCH_FAILED
        return S_BLOCKED_INCOMPLETE_TEXT
    if code == 2:
        return S_BLOCKED_FETCH_FAILED  # input error
    return S_FAILED_IMPORT


# ---------------------------------------------------------------------------
# Manifest writing
# ---------------------------------------------------------------------------

def _now_stamp() -> tuple[str, str]:
    now = _dt.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S"), now.strftime("%Y-%m-%dT%H:%M:%S")


def _write_manifest(results: list[dict], stamp: str, iso: str,
                    dry_run: bool, gate_results: list[dict]) -> tuple[Path, Path]:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    base = f"wechat_batch_import_{stamp}"
    md_path = REPORTS_DIR / f"{base}.md"
    json_path = REPORTS_DIR / f"{base}.json"

    # --- JSON manifest ---
    manifest = {
        "generated_at": iso,
        "mode": "dry-run" if dry_run else "import",
        "total": len(results),
        "summary": _summarize(results),
        "gate_results": gate_results,
        "items": results,
    }
    json_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- Markdown report ---
    lines: list[str] = []
    lines.append(f"# WeChat Batch Import Manifest — {stamp}")
    lines.append("")
    lines.append(f"- **Generated**: {iso}")
    lines.append(f"- **Mode**: {'dry-run' if dry_run else 'import'}")
    lines.append(f"- **Total inputs**: {len(results)}")
    lines.append("")
    s = _summarize(results)
    lines.append("## Summary")
    lines.append("")
    lines.append("| Status | Count |")
    lines.append("|--------|-------|")
    for k in [S_IMPORTED, S_DRY_RUN_OK, S_DRY_RUN_DUPLICATE, S_SKIPPED_DUPLICATE,
              S_BLOCKED_FETCH_FAILED, S_BLOCKED_INCOMPLETE_TEXT,
              S_FAILED_IMPORT, S_FAILED_GATE]:
        if s.get(k, 0) > 0:
            lines.append(f"| {k} | {s[k]} |")
    lines.append("")
    lines.append("## Per-input results")
    lines.append("")
    lines.append("| # | Input | Status | Title | Account | Date | KB path | Duplicate of | Reason |")
    lines.append("|---|-------|--------|-------|---------|------|---------|--------------|--------|")
    for i, r in enumerate(results, 1):
        inp = (r.get("input") or "")[:60]
        title = (r.get("title") or "")[:40]
        acct = (r.get("account_name") or "")[:20]
        kb = (r.get("kb_article_path") or "")[:40]
        dup = (r.get("duplicate_of") or "")[:40]
        reason = (r.get("failure_reason") or "")[:60]
        lines.append(
            f"| {i} | {inp} | {r.get('status','')} | {title} | {acct} | "
            f"{r.get('published_date','')} | {kb} | {dup} | {reason} |"
        )
    lines.append("")
    if gate_results:
        lines.append("## Quality gates (run only in --import mode with ≥1 IMPORTED)")
        lines.append("")
        lines.append("| Gate | Exit | Status |")
        lines.append("|------|------|--------|")
        for g in gate_results:
            lines.append(f"| {g['name']} | {g['exit']} | {'PASS' if g['exit']==0 else 'FAIL'} |")
        lines.append("")
    lines.append(f"## JSON manifest\n\n{json_path.name}\n")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def _summarize(results: list[dict]) -> dict:
    s: dict[str, int] = {}
    for r in results:
        st = r.get("status", "")
        s[st] = s.get(st, 0) + 1
    return s


# ---------------------------------------------------------------------------
# Quality gates (only run in --import mode with ≥1 IMPORTED)
# ---------------------------------------------------------------------------

GATE_SCRIPTS = [
    ("check_kb.py", "scripts/check_kb.py"),
    ("update_site.py", "scripts/update_site.py"),
    ("audit_kb_state.py", "scripts/audit_kb_state.py"),
    ("check_pages_sync.py", "scripts/check_pages_sync.py"),
]


def run_gates() -> list[dict]:
    out: list[dict] = []
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
    for name, rel in GATE_SCRIPTS:
        script = KB_HOME / rel
        proc = subprocess.run(
            [sys.executable, str(script)],
            capture_output=True, text=True, encoding="utf-8",
            errors="replace", env=env,
        )
        out.append({
            "name": name,
            "exit": proc.returncode,
            "stdout_tail": (proc.stdout or "")[-400:],
            "stderr_tail": (proc.stderr or "")[-200:],
        })
    return out


# ---------------------------------------------------------------------------
# Main per-input pipeline
# ---------------------------------------------------------------------------

def process_one(flag: str, value: str, dry_run: bool,
                index: dict) -> dict:
    """Process a single input. Returns a result dict.

    Never raises — all errors are captured into the result.
    """
    result: dict = {
        "input": value,
        "input_type": flag,
        "status": "",
        "title": "",
        "account_name": "",
        "published_date": "",
        "source_url": "",
        "capture_json_path": "",
        "kb_article_path": "",
        "docs_item_path": "",
        "site_item_path": "",
        "failure_reason": "",
        "duplicate_of": "",
    }

    # --- Bad input line (unrecognized) ---
    if flag == "__BAD__":
        result["status"] = S_BLOCKED_FETCH_FAILED
        result["failure_reason"] = "unrecognized input (not a URL or .html/.md/.txt)"
        return result

    # --- For local files, verify existence before invoking ---
    if flag in ("--html-file", "--markdown-file", "--text-file"):
        if not Path(value).exists():
            result["status"] = S_BLOCKED_FETCH_FAILED
            result["failure_reason"] = f"local file not found: {value}"
            return result

    # --- Phase 1: dry-run first to get the capture JSON WITHOUT writing a KB entry ---
    # This lets us compute dedup keys (source_url, title/account/date, content hash)
    # from the capture before committing. If --import, we then re-invoke with --import.
    code, out, err, cap_path = _run_url_script(flag, value, dry_run=True)
    if code != 0:
        result["status"] = _classify_url_script_exit(code, err)
        result["failure_reason"] = (err or out or "")[-400:]
        return result
    if not cap_path:
        result["status"] = S_FAILED_IMPORT
        result["failure_reason"] = "wechat_url_to_kb.py dry-run did not produce a capture JSON"
        return result

    cap = _load_capture(cap_path)
    result["capture_json_path"] = str(cap_path.relative_to(KB_HOME).as_posix()) if cap_path.is_absolute() and str(cap_path).startswith(str(KB_HOME)) else str(cap_path)
    result["title"] = cap.get("title", "")
    result["account_name"] = cap.get("account_name", "")
    result["published_date"] = cap.get("published_date", "")
    result["source_url"] = cap.get("source_url", "")

    # --- Dedup Layer 1: source_url ---
    src_url = cap.get("source_url", "")
    norm_url = _normalize_url(src_url)
    if norm_url and norm_url in index["by_source_url"]:
        result["status"] = S_SKIPPED_DUPLICATE if not dry_run else S_DRY_RUN_DUPLICATE
        result["duplicate_of"] = index["by_source_url"][norm_url]
        return result

    # --- Dedup Layer 2: title + account + date ---
    title = cap.get("title", "").strip()
    account = cap.get("account_name", "").strip()
    pub_date = cap.get("published_date", "").strip()
    key2 = (title, account, pub_date)
    if title and account and pub_date and key2 in index["by_title_account_date"]:
        result["status"] = S_SKIPPED_DUPLICATE if not dry_run else S_DRY_RUN_DUPLICATE
        result["duplicate_of"] = index["by_title_account_date"][key2]
        return result

    # --- Dedup Layer 3: content hash ---
    body = cap.get("content_markdown", "")
    chash = _content_hash(body) if body else ""
    if chash and chash in index["by_content_hash"]:
        result["status"] = S_SKIPPED_DUPLICATE if not dry_run else S_DRY_RUN_DUPLICATE
        result["duplicate_of"] = index["by_content_hash"][chash]
        return result

    # --- Not a duplicate: ---
    if dry_run:
        result["status"] = S_DRY_RUN_OK
        # v0.3.71: still update the in-memory index so a later input in the
        # SAME batch that hits the same source_url / (title,account,date) /
        # content hash is flagged as DRY_RUN_DUPLICATE. The "path" is a
        # synthetic marker indicating it was seen earlier in this batch.
        batch_marker = f"(dry-run batch item #{len(index['all_entries']) + 1})"
        if norm_url:
            index["by_source_url"].setdefault(norm_url, batch_marker)
        if title and account and pub_date:
            index["by_title_account_date"].setdefault(key2, batch_marker)
        if chash:
            index["by_content_hash"].setdefault(chash, batch_marker)
        return result

    # --- --import: re-run the URL script in --import mode to actually write the KB entry ---
    code2, out2, err2, _ = _run_url_script(flag, value, dry_run=False)
    if code2 != 0:
        result["status"] = S_FAILED_IMPORT if code2 == 3 else _classify_url_script_exit(code2, err2)
        result["failure_reason"] = (err2 or out2 or "")[-400:]
        return result

    # Parse the imported KB path from the import script's SUCCESS line.
    kb_path = _parse_imported_kb_path(out2, err2)
    result["kb_article_path"] = kb_path or ""
    # Derive docs/site item paths from the slug (last path segment of kb_path).
    if kb_path:
        slug = kb_path.rstrip("/").split("/")[-1]
        result["docs_item_path"] = f"docs/items/{slug}/index.html"
        result["site_item_path"] = f"site/items/{slug}/index.html"
    result["status"] = S_IMPORTED

    # --- Update the in-memory index so subsequent inputs in the same batch
    #     can dedup against this freshly-imported article. ---
    if norm_url:
        index["by_source_url"].setdefault(norm_url, kb_path or "")
    if title and account and pub_date:
        index["by_title_account_date"].setdefault(key2, kb_path or "")
    if chash:
        index["by_content_hash"].setdefault(chash, kb_path or "")
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Batch WeChat article → Hermes KB import with 3-layer dedup.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--input", action="append", default=[],
                   help="file with one URL or local path per line (repeatable)")
    p.add_argument("--url", action="append", default=[],
                   help="single mp.weixin.qq.com URL (repeatable)")
    p.add_argument("--html-file", action="append", default=[],
                   help="single local HTML file (repeatable)")
    p.add_argument("--markdown-file", action="append", default=[],
                   help="single local Markdown file (repeatable)")
    p.add_argument("--text-file", action="append", default=[],
                   help="single local plain-text file (repeatable)")
    p.add_argument("--dry-run", action="store_true",
                   help="validate + dedup-check every input but do NOT write KB entries")
    p.add_argument("--import", dest="do_import", action="store_true",
                   help="actually write KB entries (runs gates at the end)")
    p.add_argument("--no-gates", action="store_true",
                   help="skip the post-import quality gates (only valid in --import mode)")
    return p


def main() -> int:
    args = build_arg_parser().parse_args()
    dry_run = not args.do_import

    if not (args.input or args.url or args.html_file or args.markdown_file or args.text_file):
        print("ERROR: must provide at least one of --input / --url / --html-file / --markdown-file / --text-file",
              file=sys.stderr)
        return 1

    try:
        inputs = collect_inputs(args)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    if not inputs:
        print("ERROR: no valid inputs collected (all blank/comment?)", file=sys.stderr)
        return 1

    print(f"[batch] mode={'dry-run' if dry_run else 'import'} inputs={len(inputs)}", file=sys.stderr)

    # Build dedup index once (mutated as we import, so later inputs see earlier ones).
    index = build_existing_index()
    print(f"[batch] dedup index: {len(index['by_source_url'])} urls, "
          f"{len(index['by_title_account_date'])} (title,account,date), "
          f"{len(index['by_content_hash'])} content hashes", file=sys.stderr)

    results: list[dict] = []
    for i, (flag, value) in enumerate(inputs, 1):
        print(f"\n--- [{i}/{len(inputs)}] {flag} {value[:80]} ---", file=sys.stderr)
        try:
            r = process_one(flag, value, dry_run=dry_run, index=index)
        except Exception as e:
            r = {
                "input": value, "input_type": flag, "status": S_FAILED_IMPORT,
                "failure_reason": f"unhandled exception: {e}",
                "title": "", "account_name": "", "published_date": "",
                "source_url": "", "capture_json_path": "", "kb_article_path": "",
                "docs_item_path": "", "site_item_path": "", "duplicate_of": "",
            }
        print(f"    → {r['status']}" +
              (f" (dup of {r['duplicate_of']})" if r['duplicate_of'] else "") +
              (f" :: {r['failure_reason'][:120]}" if r['failure_reason'] else ""),
              file=sys.stderr)
        results.append(r)

    # --- Quality gates (only in --import mode with ≥1 IMPORTED) ---
    gate_results: list[dict] = []
    any_imported = any(r["status"] == S_IMPORTED for r in results)
    if (not dry_run) and any_imported and (not args.no_gates):
        print("\n[batch] running quality gates ...", file=sys.stderr)
        gate_results = run_gates()
        for g in gate_results:
            tag = "PASS" if g["exit"] == 0 else "FAIL"
            print(f"  {g['name']}: {tag} (exit {g['exit']})", file=sys.stderr)

    # --- Write manifest ---
    stamp, iso = _now_stamp()
    md_path, json_path = _write_manifest(results, stamp, iso, dry_run, gate_results)
    print(f"\n[batch] manifest: {md_path}", file=sys.stderr)
    print(f"[batch] manifest: {json_path}", file=sys.stderr)

    # --- Exit code ---
    if gate_results and any(g["exit"] != 0 for g in gate_results):
        print("[batch] one or more gates failed — inspect manifest before commit/push.",
              file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
