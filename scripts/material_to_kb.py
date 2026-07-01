#!/usr/bin/env python3
"""Unified material -> Hermes KB import router.

This is a thin router. It detects the material type, delegates supported
WeChat routes to the existing import scripts, and reports unsupported routes
explicitly instead of inventing new importers.

Supported CLI:
    python scripts/material_to_kb.py --input "<URL_OR_FILE>" --dry-run
    python scripts/material_to_kb.py --input "<URL_OR_FILE>" --import
    python scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run
    python scripts/material_to_kb.py --input-list tmp/materials.txt --import
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

KB_HOME = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = KB_HOME / "scripts"
REPORTS_DIR = KB_HOME / "reports"
WECHAT_SINGLE_SCRIPT = SCRIPTS_DIR / "wechat_url_to_kb.py"
WECHAT_BATCH_SCRIPT = SCRIPTS_DIR / "wechat_batch_import.py"
LOCALIZE_SCRIPT = SCRIPTS_DIR / "localize_article_images.py"

STATUS_IMPORTED = "IMPORTED"
STATUS_DRY_RUN_OK = "DRY_RUN_OK"
STATUS_SKIPPED_DUPLICATE = "SKIPPED_DUPLICATE"
STATUS_BLOCKED_UNSUPPORTED = "BLOCKED_UNSUPPORTED"
STATUS_BLOCKED_FETCH_FAILED = "BLOCKED_FETCH_FAILED"
STATUS_BLOCKED_INCOMPLETE_TEXT = "BLOCKED_INCOMPLETE_TEXT"
STATUS_FAILED_IMPORT = "FAILED_IMPORT"
STATUS_FAILED_GATE = "FAILED_GATE"

SUMMARY_KEYS = {
    STATUS_IMPORTED: "imported",
    STATUS_DRY_RUN_OK: "dry_run_ok",
    STATUS_SKIPPED_DUPLICATE: "skipped_duplicate",
    STATUS_BLOCKED_UNSUPPORTED: "blocked_unsupported",
    STATUS_BLOCKED_FETCH_FAILED: "blocked_fetch_failed",
    STATUS_BLOCKED_INCOMPLETE_TEXT: "blocked_incomplete_text",
    STATUS_FAILED_IMPORT: "failed_import",
    STATUS_FAILED_GATE: "failed_gate",
}

LOCAL_TEXT_EXT_TO_FLAG = {
    ".html": "--html-file",
    ".htm": "--html-file",
    ".md": "--markdown-file",
    ".markdown": "--markdown-file",
    ".txt": "--text-file",
}


def now_stamp() -> tuple[str, str]:
    now = dt.datetime.now()
    return now.strftime("%Y%m%d_%H%M%S"), now.strftime("%Y-%m-%dT%H:%M:%S")


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Route URLs/files to the existing Hermes KB import scripts.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", action="append", default=[], help="single URL or local file path")
    source.add_argument("--input-list", action="append", default=[], help="file with one URL/path per line")

    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="route and validate without writing KB entries")
    mode.add_argument("--import", dest="do_import", action="store_true", help="run supported import routes")
    return parser


def read_inputs(args: argparse.Namespace) -> list[str]:
    values: list[str] = []
    values.extend(args.input or [])
    for list_path in args.input_list or []:
        path = Path(list_path)
        if not path.exists():
            raise FileNotFoundError(f"--input-list not found: {list_path}")
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            values.append(line)
    return values


def is_url(value: str) -> bool:
    return value.startswith("http://") or value.startswith("https://")


def host_of(url: str) -> str:
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def is_wechat_url(value: str) -> bool:
    host = host_of(value)
    return host == "mp.weixin.qq.com" or host.endswith(".mp.weixin.qq.com") or host == "weixin.qq.com" or host.endswith(".weixin.qq.com")


def is_youtube_url(value: str) -> bool:
    host = host_of(value)
    return host == "youtube.com" or host.endswith(".youtube.com") or host == "youtu.be" or host.endswith(".youtu.be")


def infer_input(value: str, index: int = 0) -> dict[str, Any]:
    item: dict[str, Any] = {
        "index": index,
        "input": value,
        "inferred_type": "",
        "route": "",
        "route_kind": "",
        "route_flag": "",
        "supported": False,
        "failure_reason": "",
    }

    if is_url(value):
        if is_wechat_url(value):
            item.update({
                "inferred_type": "wechat_url",
                "route": "wechat_url_to_kb.py URL mode",
                "route_kind": "wechat",
                "route_flag": "--url",
                "supported": True,
            })
        elif is_youtube_url(value):
            item.update({
                "inferred_type": "youtube_url",
                "route": "unsupported",
                "failure_reason": "YouTube import route not implemented yet in unified router",
            })
        else:
            item.update({
                "inferred_type": "generic_web_url",
                "route": "unsupported",
                "failure_reason": "generic web article import route not implemented yet",
            })
        return item

    suffix = Path(value).suffix.lower()
    if suffix in LOCAL_TEXT_EXT_TO_FLAG:
        item.update({
            "inferred_type": "local_text_article",
            "route": "wechat_url_to_kb.py local file mode",
            "route_kind": "wechat",
            "route_flag": LOCAL_TEXT_EXT_TO_FLAG[suffix],
            "supported": True,
        })
    elif suffix == ".pdf":
        item.update({
            "inferred_type": "pdf_file",
            "route": "unsupported",
            "failure_reason": "PDF import/OCR route not implemented yet",
        })
    else:
        item.update({
            "inferred_type": "unknown",
            "route": "unsupported",
            "failure_reason": "no supported import route for this input",
        })
    return item


def base_result(item: dict[str, Any], status: str = "") -> dict[str, Any]:
    return {
        "input": item["input"],
        "inferred_type": item["inferred_type"],
        "route": item["route"],
        "status": status,
        "title": "",
        "source_url": "",
        "kb_article_path": "",
        "docs_item_path": "",
        "site_item_path": "",
        "capture_json_path": "",
        "route_report_path": "",
        "failure_reason": item.get("failure_reason", ""),
    }


def run_command(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    return subprocess.run(
        cmd,
        cwd=KB_HOME,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
    )


def normalize_status(status: str, dry_run: bool) -> str:
    if status == "DRY_RUN_DUPLICATE":
        return STATUS_SKIPPED_DUPLICATE
    if status in SUMMARY_KEYS:
        return status
    if status == "PASS" and dry_run:
        return STATUS_DRY_RUN_OK
    if status == "PASS":
        return STATUS_IMPORTED
    return status or STATUS_FAILED_IMPORT


def parse_capture_path(stdout: str, stderr: str) -> str:
    text = (stdout or "") + "\n" + (stderr or "")
    match = re.search(r"\[capture\]\s+(.+?)(?:\r?\n|$)", text)
    if not match:
        return ""
    raw = match.group(1).strip()
    path = Path(raw)
    if not path.is_absolute():
        path = KB_HOME / path
    if path.exists():
        try:
            return path.relative_to(KB_HOME).as_posix()
        except ValueError:
            return str(path)
    return raw


def parse_imported_path(stdout: str, stderr: str) -> str:
    text = (stdout or "") + "\n" + (stderr or "")
    match = re.search(r"imported to\s+(.+?)(?:\s|$)", text, re.IGNORECASE)
    return match.group(1).strip() if match else ""


def load_capture_fields(result: dict[str, Any]) -> None:
    cap = result.get("capture_json_path") or ""
    if not cap:
        return
    path = KB_HOME / cap
    if not path.exists():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return
    result["title"] = data.get("title", "") or result.get("title", "")
    result["source_url"] = data.get("source_url", "") or result.get("source_url", "")


def status_from_single_exit(proc: subprocess.CompletedProcess[str], dry_run: bool) -> tuple[str, str]:
    text = (proc.stdout or "") + "\n" + (proc.stderr or "")
    if proc.returncode == 0:
        return (STATUS_DRY_RUN_OK if dry_run else STATUS_IMPORTED), ""
    if proc.returncode == 1:
        lowered = text.lower()
        if any(token in lowered for token in ("network error", "non-200", "fetch", "file not found", "--url must")):
            return STATUS_BLOCKED_FETCH_FAILED, text[-500:]
        return STATUS_BLOCKED_INCOMPLETE_TEXT, text[-500:]
    if proc.returncode == 2:
        return STATUS_BLOCKED_FETCH_FAILED, text[-500:]
    return STATUS_FAILED_IMPORT, text[-500:]


def run_single_wechat(item: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    result = base_result(item)
    cmd = [sys.executable, str(WECHAT_SINGLE_SCRIPT), item["route_flag"], item["input"]]
    cmd.append("--dry-run" if dry_run else "--import")
    proc = run_command(cmd)
    result["capture_json_path"] = parse_capture_path(proc.stdout, proc.stderr)
    result["status"], result["failure_reason"] = status_from_single_exit(proc, dry_run)
    load_capture_fields(result)
    if result["status"] == STATUS_IMPORTED:
        kb_path = parse_imported_path(proc.stdout, proc.stderr)
        result["kb_article_path"] = kb_path
        if kb_path:
            slug = kb_path.rstrip("/").split("/")[-1]
            result["docs_item_path"] = f"docs/items/{slug}/index.html"
            result["site_item_path"] = f"site/items/{slug}/index.html"
    return result


def parse_batch_report_paths(stdout: str, stderr: str) -> tuple[str, str]:
    text = (stdout or "") + "\n" + (stderr or "")
    paths = re.findall(r"\[batch\]\s+manifest:\s+(.+?)(?:\r?\n|$)", text)
    md_path = ""
    json_path = ""
    for raw in paths:
        raw = raw.strip()
        if raw.endswith(".md"):
            md_path = raw
        elif raw.endswith(".json"):
            json_path = raw
    return md_path, json_path


def relpath_or_raw(path_text: str) -> str:
    if not path_text:
        return ""
    path = Path(path_text)
    try:
        if path.is_absolute():
            return path.relative_to(KB_HOME).as_posix()
    except ValueError:
        pass
    return path_text


def run_batch_wechat(items: list[dict[str, Any]], dry_run: bool) -> list[dict[str, Any]]:
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", suffix=".txt", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        for item in items:
            tmp.write(item["input"] + "\n")
    try:
        cmd = [sys.executable, str(WECHAT_BATCH_SCRIPT), "--input", str(tmp_path)]
        cmd.append("--dry-run" if dry_run else "--import")
        if not dry_run:
            cmd.append("--no-gates")
        proc = run_command(cmd)
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass

    md_report, json_report = parse_batch_report_paths(proc.stdout, proc.stderr)
    route_report = relpath_or_raw(md_report)
    report_items: list[dict[str, Any]] = []
    if json_report and Path(json_report).exists():
        try:
            manifest = json.loads(Path(json_report).read_text(encoding="utf-8"))
            report_items = manifest.get("items", [])
        except Exception:
            report_items = []

    results: list[dict[str, Any]] = []
    for item, batch_item in zip(items, report_items):
        result = base_result(item)
        result["route"] = "wechat_batch_import.py input-list mode"
        result["route_report_path"] = route_report
        result["status"] = normalize_status(batch_item.get("status", ""), dry_run)
        result["title"] = batch_item.get("title", "")
        result["source_url"] = batch_item.get("source_url", "")
        result["capture_json_path"] = batch_item.get("capture_json_path", "")
        result["kb_article_path"] = batch_item.get("kb_article_path", "")
        result["docs_item_path"] = batch_item.get("docs_item_path", "")
        result["site_item_path"] = batch_item.get("site_item_path", "")
        result["failure_reason"] = batch_item.get("failure_reason", "")
        results.append(result)

    if len(results) < len(items):
        text = ((proc.stdout or "") + "\n" + (proc.stderr or ""))[-500:]
        for item in items[len(results):]:
            result = base_result(item, STATUS_FAILED_IMPORT)
            result["route"] = "wechat_batch_import.py input-list mode"
            result["route_report_path"] = route_report
            result["failure_reason"] = text or "wechat_batch_import.py did not emit parseable results"
            results.append(result)
    return results


def localize_imported_images(results: list[dict[str, Any]]) -> None:
    for result in results:
        if result.get("status") != STATUS_IMPORTED or not result.get("kb_article_path"):
            continue
        cmd = [sys.executable, str(LOCALIZE_SCRIPT), "--article-path", result["kb_article_path"]]
        proc = run_command(cmd)
        if proc.returncode != 0:
            result["status"] = STATUS_FAILED_IMPORT
            result["failure_reason"] = "localize_article_images.py failed: " + ((proc.stderr or proc.stdout or "")[-300:])


GATE_SCRIPTS = [
    ("check_kb.py", "scripts/check_kb.py"),
    ("update_site.py", "scripts/update_site.py"),
    ("audit_kb_state.py", "scripts/audit_kb_state.py"),
    ("check_pages_sync.py", "scripts/check_pages_sync.py"),
]


def run_import_gates() -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    for name, rel in GATE_SCRIPTS:
        proc = run_command([sys.executable, str(KB_HOME / rel)])
        gates.append({
            "name": name,
            "exit": proc.returncode,
            "status": "PASS" if proc.returncode == 0 else "FAIL",
            "stdout_tail": (proc.stdout or "")[-500:],
            "stderr_tail": (proc.stderr or "")[-300:],
        })
    return gates


def summarize(results: list[dict[str, Any]]) -> dict[str, int]:
    summary = {
        "total": len(results),
        "imported": 0,
        "dry_run_ok": 0,
        "skipped_duplicate": 0,
        "blocked_unsupported": 0,
        "blocked_fetch_failed": 0,
        "blocked_incomplete_text": 0,
        "failed_import": 0,
        "failed_gate": 0,
    }
    for result in results:
        key = SUMMARY_KEYS.get(result.get("status", ""))
        if key:
            summary[key] += 1
    return summary


def write_reports(results: list[dict[str, Any]], gates: list[dict[str, Any]], dry_run: bool) -> tuple[Path, Path]:
    stamp, iso = now_stamp()
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    md_path = REPORTS_DIR / f"material_import_{stamp}.md"
    json_path = REPORTS_DIR / f"material_import_{stamp}.json"
    summary = summarize(results)
    payload = {
        "generated_at": iso,
        "mode": "dry-run" if dry_run else "import",
        "summary": summary,
        "gate_results": gates,
        "items": results,
    }
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Material Import Report {stamp}",
        "",
        f"- generated_at: `{iso}`",
        f"- mode: `{'dry-run' if dry_run else 'import'}`",
        "",
        "## Summary",
        "",
        "| Metric | Count |",
        "|---|---:|",
    ]
    for key in ["total", "imported", "dry_run_ok", "skipped_duplicate", "blocked_unsupported",
                "blocked_fetch_failed", "blocked_incomplete_text", "failed_import", "failed_gate"]:
        lines.append(f"| {key} | {summary[key]} |")
    lines.extend([
        "",
        "## Inputs",
        "",
        "| # | Input | Inferred type | Route | Status | Title | KB path | Failure reason |",
        "|---:|---|---|---|---|---|---|---|",
    ])
    for idx, result in enumerate(results, 1):
        lines.append(
            "| {idx} | {input} | {itype} | {route} | {status} | {title} | {kb} | {reason} |".format(
                idx=idx,
                input=(result.get("input", "")[:80]).replace("|", "\\|"),
                itype=result.get("inferred_type", ""),
                route=(result.get("route", "")[:45]).replace("|", "\\|"),
                status=result.get("status", ""),
                title=(result.get("title", "")[:40]).replace("|", "\\|"),
                kb=(result.get("kb_article_path", "")[:45]).replace("|", "\\|"),
                reason=(result.get("failure_reason", "")[:80]).replace("\n", " ").replace("|", "\\|"),
            )
        )
    if gates:
        lines.extend(["", "## Gates", "", "| Gate | Exit | Status |", "|---|---:|---|"])
        for gate in gates:
            lines.append(f"| {gate['name']} | {gate['exit']} | {gate['status']} |")
    lines.extend(["", "## JSON", "", f"`{json_path.name}`", ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path, json_path


def route_inputs(values: list[str], dry_run: bool) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    inferred = [infer_input(value, index=i) for i, value in enumerate(values)]
    results_by_index: dict[int, dict[str, Any]] = {}

    supported = [item for item in inferred if item["supported"]]
    unsupported = [item for item in inferred if not item["supported"]]
    for item in unsupported:
        results_by_index[item["index"]] = base_result(item, STATUS_BLOCKED_UNSUPPORTED)

    if len(supported) > 1:
        for result, item in zip(run_batch_wechat(supported, dry_run=dry_run), supported):
            results_by_index[item["index"]] = result
    elif len(supported) == 1:
        item = supported[0]
        results_by_index[item["index"]] = run_single_wechat(item, dry_run=dry_run)

    results = [results_by_index[i] for i in sorted(results_by_index)]
    gates: list[dict[str, Any]] = []
    if not dry_run and any(r["status"] == STATUS_IMPORTED for r in results):
        localize_imported_images(results)
        if any(r["status"] == STATUS_IMPORTED for r in results):
            gates = run_import_gates()
            if any(g["exit"] != 0 for g in gates):
                for result in results:
                    if result["status"] == STATUS_IMPORTED:
                        result["status"] = STATUS_FAILED_GATE
                        result["failure_reason"] = "one or more post-import gates failed"
    return results, gates


def main() -> int:
    args = build_arg_parser().parse_args()
    dry_run = not args.do_import
    try:
        values = read_inputs(args)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if not values:
        print("ERROR: no inputs found", file=sys.stderr)
        return 1

    results, gates = route_inputs(values, dry_run=dry_run)
    md_path, json_path = write_reports(results, gates, dry_run=dry_run)
    summary = summarize(results)
    output = {
        "status": "FAILED_GATE" if summary["failed_gate"] else "PASS",
        "mode": "dry-run" if dry_run else "import",
        "summary": summary,
        "report_markdown": md_path.relative_to(KB_HOME).as_posix(),
        "report_json": json_path.relative_to(KB_HOME).as_posix(),
        "items": results,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    print(f"[material] report: {md_path}", file=sys.stderr)
    print(f"[material] report: {json_path}", file=sys.stderr)
    return 2 if summary["failed_gate"] else 0


if __name__ == "__main__":
    sys.exit(main())
