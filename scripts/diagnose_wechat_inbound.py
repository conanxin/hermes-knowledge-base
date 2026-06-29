#!/usr/bin/env python3
"""
diagnose_wechat_inbound.py — Diagnose WeChat (mp.weixin.qq.com) inbound → OpenClaw → KB capture chain.

v0.3.62 — Read-only diagnostic. Surfaces the actual state of:
  1. OpenClaw gateway service + active extensions
  2. Whether @tencent-weixin/openclaw-weixin extension is enabled or disabled
  3. Recent OpenClaw event/log paths + counts
  4. Whether any wechat / mp.weixin.qq.com traffic has reached the gateway
  5. Existing capture JSON files in inbox/raw/wechat/
  6. Whether scripts/import_wechat_article_capture.py can consume them

This script NEVER makes changes. Default: print human-readable report + exit 0.
Use `--json` for machine-readable output.

Exit codes:
  0  - Diagnostic complete (output may show PASS / WARN / FAIL of the chain)
  2  - Hard error (Python missing dependency)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any


# --- Constants & canonical paths ---

HOME = Path.home()
OPENCLAW_HOME = HOME / ".openclaw"
EXTENSIONS_DIR = OPENCLAW_HOME / "extensions"
EXTENSIONS_DISABLED_DIR = OPENCLAW_HOME / "extensions-disabled"

# Possible log locations (canonical + observed)
LOG_CANDIDATES = [
    OPENCLAW_HOME / "logs",
    OPENCLAW_HOME / "log",
    OPENCLAW_HOME / "agents" / "main" / "sessions",
    Path("/var/log/openclaw"),
]

KB_HOME = HOME / "hermes-knowledge-base"
INBOX_WECHAT = KB_HOME / "inbox" / "raw" / "wechat"
IMPORT_SCRIPT = KB_HOME / "scripts" / "import_wechat_article_capture.py"

WECHAT_URL_RE = re.compile(r"mp\.weixin\.qq\.com")
WECHAT_KEYWORD_RE = re.compile(r"(wechat|weixin|公众号|tencent-weixin|openclaw-weixin)", re.I)

# Fields the import script demands (from its docstring + required-fields list)
REQUIRED_CAPTURE_FIELDS = ["title", "source_url", "content_markdown", "captured_at"]


# --- Diagnostic probes ---

def probe_openclaw_service() -> dict:
    """Check systemd user service + node process."""
    info = {
        "service": "unknown",
        "service_active": False,
        "node_process": False,
        "version": None,
    }
    try:
        out = subprocess.run(
            ["systemctl", "--user", "is-active", "openclaw-gateway"],
            capture_output=True, text=True, timeout=5
        )
        info["service_active"] = out.stdout.strip() == "active"
        info["service"] = out.stdout.strip()
    except Exception as e:
        info["service"] = f"error: {e}"

    try:
        out = subprocess.run(
            ["pgrep", "-f", "openclaw.*dist/index.js.*gateway"],
            capture_output=True, text=True, timeout=5
        )
        info["node_process"] = bool(out.stdout.strip())
    except Exception:
        pass

    # Try to find version
    pkg = Path("/home/ubuntu/.npm-global/lib/node_modules/openclaw/package.json")
    if pkg.exists():
        try:
            d = json.loads(pkg.read_text())
            info["version"] = d.get("version")
        except Exception:
            pass

    return info


def probe_weixin_extension() -> dict:
    """Check whether @tencent-weixin/openclaw-weixin is enabled or disabled."""
    info = {
        "package_name": "@tencent-weixin/openclaw-weixin",
        "enabled": False,
        "disabled_paths": [],
        "source_path": None,
    }

    if EXTENSIONS_DISABLED_DIR.exists():
        for p in EXTENSIONS_DISABLED_DIR.iterdir():
            if "weixin" in p.name.lower() or "wechat" in p.name.lower():
                info["disabled_paths"].append(str(p))

    # Search for the active source
    if EXTENSIONS_DIR.exists():
        for p in EXTENSIONS_DIR.rglob("package.json"):
            try:
                d = json.loads(p.read_text())
                if d.get("name") == "@tencent-weixin/openclaw-weixin":
                    info["enabled"] = True
                    info["source_path"] = str(p.parent)
                    break
            except Exception:
                continue

    # Also check the npm-global package
    npm_pkg = Path("/home/ubuntu/.npm-global/lib/node_modules/@tencent-weixin/openclaw-weixin/package.json")
    if npm_pkg.exists():
        try:
            d = json.loads(npm_pkg.read_text())
            info["npm_installed_version"] = d.get("version")
        except Exception:
            pass

    return info


def probe_event_logs() -> dict:
    """Survey potential event-log paths + count of wechat-related events."""
    info = {
        "candidate_paths": [],
        "wechat_url_count": 0,
        "wechat_keyword_count": 0,
        "files_scanned": 0,
        "largest_log_file": None,
    }
    for path in LOG_CANDIDATES:
        if path.exists():
            info["candidate_paths"].append(str(path))
            if path.is_dir():
                # Scan all .log / .jsonl files (cap to last 50 by mtime)
                files = sorted(
                    [f for f in path.rglob("*") if f.is_file() and f.suffix in (".log", ".jsonl")],
                    key=lambda f: f.stat().st_mtime,
                    reverse=True,
                )[:50]
                for f in files:
                    info["files_scanned"] += 1
                    try:
                        text = f.read_text(errors="ignore")
                    except Exception:
                        continue
                    if not info["largest_log_file"] or f.stat().st_size > info["largest_log_file"][1]:
                        info["largest_log_file"] = (str(f), f.stat().st_size)
                    url_hits = len(WECHAT_URL_RE.findall(text))
                    kw_hits = len(WECHAT_KEYWORD_RE.findall(text))
                    info["wechat_url_count"] += url_hits
                    info["wechat_keyword_count"] += kw_hits
    return info


def probe_existing_captures() -> dict:
    """Check what capture JSONs exist in inbox/raw/wechat/."""
    info = {
        "dir": str(INBOX_WECHAT),
        "exists": INBOX_WECHAT.exists(),
        "files": [],
    }
    if not INBOX_WECHAT.exists():
        return info
    for f in sorted(INBOX_WECHAT.glob("*.json")):
        try:
            d = json.loads(f.read_text())
        except Exception as e:
            info["files"].append({"path": str(f), "error": str(e)})
            continue
        fields_present = [k for k in REQUIRED_CAPTURE_FIELDS if k in d]
        info["files"].append({
            "path": str(f),
            "size_bytes": f.stat().st_size,
            "title": d.get("title"),
            "source_url": d.get("source_url"),
            "account_name": d.get("account_name"),
            "has_content_markdown": bool(d.get("content_markdown")),
            "content_markdown_chars": len(d.get("content_markdown", "")),
            "required_fields_present": fields_present,
            "missing_required_fields": [k for k in REQUIRED_CAPTURE_FIELDS if k not in d],
        })
    return info


def probe_import_script() -> dict:
    """Check whether the import script exists and is consumable."""
    info = {
        "path": str(IMPORT_SCRIPT),
        "exists": IMPORT_SCRIPT.exists(),
        "line_count": 0,
        "accepts_dry_run": False,
        "shebang": None,
    }
    if not IMPORT_SCRIPT.exists():
        return info
    try:
        text = IMPORT_SCRIPT.read_text()
    except Exception as e:
        info["error"] = str(e)
        return info
    info["line_count"] = text.count("\n")
    info["accepts_dry_run"] = "--dry-run" in text
    if text.startswith("#!"):
        info["shebang"] = text.splitlines()[0]
    return info


# --- Status summarizer ---

def summarize(diag: dict) -> dict:
    """Return a status summary based on the diagnostic findings."""
    s = diag["openclaw_service"]
    w = diag["weixin_extension"]
    c = diag["existing_captures"]
    im = diag["import_script"]

    # 4 sub-checks
    checks = []

    checks.append({
        "name": "OpenClaw gateway running",
        "pass": s.get("service_active", False) and s.get("node_process", False),
        "detail": f"service={s.get('service')}, node_proc={s.get('node_process')}, version={s.get('version')}",
    })

    checks.append({
        "name": "WeChat extension enabled",
        "pass": w.get("enabled", False),
        "detail": (
            f"enabled={w.get('enabled')}, "
            f"disabled_dirs={len(w.get('disabled_paths', []))}, "
            f"source_path={w.get('source_path') or 'N/A'}"
        ),
    })

    checks.append({
        "name": "WeChat event log path exists",
        "pass": len(diag["event_logs"].get("candidate_paths", [])) > 0
                and diag["event_logs"].get("wechat_url_count", 0) > 0,
        "detail": (
            f"candidates={len(diag['event_logs'].get('candidate_paths', []))}, "
            f"files_scanned={diag['event_logs'].get('files_scanned', 0)}, "
            f"wechat_url_hits={diag['event_logs'].get('wechat_url_count', 0)}, "
            f"keyword_hits={diag['event_logs'].get('wechat_keyword_count', 0)}"
        ),
    })

    checks.append({
        "name": "Capture JSON → import script path consumable",
        "pass": (
            c.get("exists", False)
            and len(c.get("files", [])) > 0
            and im.get("exists", False)
            and im.get("accepts_dry_run", False)
        ),
        "detail": (
            f"inbox_dir_exists={c.get('exists')}, "
            f"capture_files={len(c.get('files', []))}, "
            f"import_script={im.get('exists')}, "
            f"import_accepts_dry_run={im.get('accepts_dry_run')}"
        ),
    })

    n_pass = sum(1 for c in checks if c["pass"])
    n_total = len(checks)

    if n_pass == n_total:
        status = "PASS"
    elif n_pass == 0:
        status = "FAIL"
    else:
        status = "PARTIAL"

    return {
        "status": status,
        "n_pass": n_pass,
        "n_total": n_total,
        "checks": checks,
    }


# --- Report renderer ---

def render_text(diag: dict) -> str:
    s = diag["summary"]
    lines = []
    lines.append("=" * 70)
    lines.append("WeChat Inbound Diagnostic — v0.3.62")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Overall: {s['status']} ({s['n_pass']}/{s['n_total']} checks pass)")
    lines.append("")

    lines.append("--- 1. OpenClaw gateway service ---")
    info = diag["openclaw_service"]
    lines.append(f"  service active : {info.get('service_active')}")
    lines.append(f"  node process   : {info.get('node_process')}")
    lines.append(f"  version        : {info.get('version')}")
    lines.append(f"  service state  : {info.get('service')}")
    lines.append("")

    lines.append("--- 2. WeChat extension (@tencent-weixin/openclaw-weixin) ---")
    info = diag["weixin_extension"]
    lines.append(f"  package        : {info.get('package_name')}")
    lines.append(f"  enabled        : {info.get('enabled')}")
    if info.get("source_path"):
        lines.append(f"  active path    : {info.get('source_path')}")
    if info.get("npm_installed_version"):
        lines.append(f"  npm version    : {info.get('npm_installed_version')}")
    if info.get("disabled_paths"):
        lines.append(f"  disabled dirs  : {len(info['disabled_paths'])}")
        for p in info["disabled_paths"][:3]:
            lines.append(f"    - {p}")
    lines.append("")

    lines.append("--- 3. Event / log paths ---")
    info = diag["event_logs"]
    if info.get("candidate_paths"):
        for p in info["candidate_paths"]:
            lines.append(f"  FOUND: {p}")
    else:
        lines.append("  (no canonical log paths found)")
    lines.append(f"  files scanned          : {info.get('files_scanned')}")
    lines.append(f"  wechat URL hits (mp.weixin.qq.com) : {info.get('wechat_url_count')}")
    lines.append(f"  wechat keyword hits    : {info.get('wechat_keyword_count')}")
    if info.get("largest_log_file"):
        path, size = info["largest_log_file"]
        lines.append(f"  largest scanned file   : {path} ({size:,} bytes)")
    lines.append("")

    lines.append("--- 4. Existing capture JSONs (inbox/raw/wechat/) ---")
    info = diag["existing_captures"]
    if not info.get("exists"):
        lines.append(f"  directory not found: {info.get('dir')}")
    elif not info.get("files"):
        lines.append("  (no capture JSONs found)")
    else:
        for f in info["files"]:
            lines.append(f"  - {f['path']}")
            for k in ("title", "source_url", "account_name",
                      "has_content_markdown", "content_markdown_chars",
                      "missing_required_fields", "size_bytes"):
                v = f.get(k)
                if v is None:
                    continue
                if isinstance(v, list):
                    if v:
                        lines.append(f"      {k}: {v}")
                    else:
                        lines.append(f"      {k}: []")
                else:
                    lines.append(f"      {k}: {v}")
    lines.append("")

    lines.append("--- 5. Import script status ---")
    info = diag["import_script"]
    lines.append(f"  path            : {info.get('path')}")
    lines.append(f"  exists          : {info.get('exists')}")
    lines.append(f"  line count      : {info.get('line_count')}")
    lines.append(f"  accepts --dry-run: {info.get('accepts_dry_run')}")
    lines.append(f"  shebang         : {info.get('shebang')}")
    lines.append("")

    lines.append("--- 6. Sub-checks ---")
    for c in s["checks"]:
        mark = "[x]" if c["pass"] else "[ ]"
        lines.append(f"  {mark} {c['name']}")
        lines.append(f"      {c['detail']}")
    lines.append("")

    # Next-step recommendations
    lines.append("--- 7. Recommended next steps ---")
    if not diag["openclaw_service"].get("service_active"):
        lines.append("  - OpenClaw gateway is not running. Restart with: systemctl --user restart openclaw-gateway")
    if not diag["weixin_extension"].get("enabled"):
        lines.append("  - WeChat extension is disabled. Re-enable by moving it out of extensions-disabled/ back to extensions/,")
        lines.append("    then restart the gateway. Inspect why it was disabled (2026-04-09).")
    if diag["event_logs"].get("wechat_url_count", 0) == 0:
        lines.append("  - No mp.weixin.qq.com traffic in any scanned log. Likely root cause: extension is disabled,")
        lines.append("    so inbound never reaches the gateway. Until re-enabled, no real inbound is possible.")
    if diag["existing_captures"].get("files"):
        lines.append("  - Capture JSON(s) already exist in inbox/raw/wechat/ — those can be consumed by")
        lines.append("    scripts/import_wechat_article_capture.py even without live inbound.")
    if im_ok := diag["import_script"].get("exists") and diag["import_script"].get("accepts_dry_run"):
        lines.append("  - Import script is consumable. Use:")
        lines.append("       python3 scripts/import_wechat_article_capture.py --dry-run inbox/raw/wechat/<file>.json")

    lines.append("")
    lines.append("=" * 70)
    return "\n".join(lines)


# --- Main ---

def main():
    parser = argparse.ArgumentParser(description="WeChat inbound diagnostic")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    args = parser.parse_args()

    diag = {
        "openclaw_service": probe_openclaw_service(),
        "weixin_extension": probe_weixin_extension(),
        "event_logs": probe_event_logs(),
        "existing_captures": probe_existing_captures(),
        "import_script": probe_import_script(),
    }
    diag["summary"] = summarize(diag)

    if args.json:
        print(json.dumps(diag, indent=2, ensure_ascii=False, default=str))
    else:
        print(render_text(diag))

    sys.exit(0)


if __name__ == "__main__":
    main()