#!/usr/bin/env python3
"""
wechat_inbound_to_capture.py — Minimal bridge from existing capture JSON → import-ready next step.

v0.3.62 — Read-mostly bridge. Does NOT enable any OpenClaw extension. Does NOT log in to WeChat.
Does NOT touch live inbound.

What it does:
  - Reads the most recent capture JSON in inbox/raw/wechat/
  - Validates the schema matches what scripts/import_wechat_article_capture.py expects
  - In dry-run mode (default): prints the next-step command(s) without invoking them
  - In --import mode: invokes scripts/import_wechat_article_capture.py (still respecting
    that script's own --dry-run default; user must explicitly add --import there)

Why this exists:
  OpenClaw @tencent-weixin/openclaw-weixin is currently disabled
  (extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122), so live inbound is
  impossible right now. This bridge lets us still consume the manually-cached capture
  JSONs (e.g. 2026-06-29-isls-2026-cached.json) without flipping the gateway extension
  state.

Exit codes:
  0  - Bridge succeeded (dry-run or import both)
  2  - No capture JSON found in inbox/raw/wechat/
  3  - Capture JSON schema invalid (missing required fields)
  4  - Import invocation failed
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

KB_HOME = Path(__file__).parent.parent
INBOX_WECHAT = KB_HOME / "inbox" / "raw" / "wechat"
IMPORT_SCRIPT = KB_HOME / "scripts" / "import_wechat_article_capture.py"

REQUIRED_FIELDS = ["title", "source_url", "content_markdown", "captured_at"]


def find_latest_capture() -> Path | None:
    if not INBOX_WECHAT.exists():
        return None
    files = sorted(INBOX_WECHAT.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def validate_capture(path: Path) -> tuple[bool, list[str]]:
    try:
        data = json.loads(path.read_text())
    except Exception as e:
        return False, [f"JSON parse error: {e}"]
    missing = [k for k in REQUIRED_FIELDS if not data.get(k)]
    if missing:
        return False, [f"missing required field: {k}" for k in missing]
    content_len = len(data.get("content_markdown", ""))
    if content_len < 200:
        return False, [f"content_markdown too short ({content_len} chars, need >=200)"]
    return True, []


def render_dry_run(capture_path: Path) -> dict:
    data = json.loads(capture_path.read_text())
    rel = capture_path.relative_to(KB_HOME)
    return {
        "capture_path": str(capture_path),
        "capture_rel": str(rel),
        "title": data.get("title"),
        "source_url": data.get("source_url"),
        "account_name": data.get("account_name"),
        "author": data.get("author"),
        "published_date": data.get("published_date"),
        "captured_at": data.get("captured_at"),
        "content_chars": len(data.get("content_markdown", "")),
        "next_step_dry_run": f"python3 scripts/import_wechat_article_capture.py --dry-run {rel}",
        "next_step_import": f"python3 scripts/import_wechat_article_capture.py --import {rel}",
        "warning": (
            "OpenClaw weixin extension is currently disabled; this is consuming a "
            "manually-cached capture, not a live inbound."
        ),
    }


def invoke_import(capture_path: Path, dry_run: bool) -> int:
    rel = capture_path.relative_to(KB_HOME)
    cmd = ["python3", str(IMPORT_SCRIPT.relative_to(KB_HOME))]
    if dry_run:
        cmd.append("--dry-run")
    cmd.append(str(rel))
    print(f"[bridge] running: {' '.join(cmd)}", file=sys.stderr)
    result = subprocess.run(cmd, cwd=str(KB_HOME))
    return result.returncode


def main():
    parser = argparse.ArgumentParser(description="WeChat capture → import bridge")
    parser.add_argument("--dry-run", action="store_true", default=True,
                        help="Print next-step commands without invoking import (DEFAULT)")
    parser.add_argument("--import", dest="do_import", action="store_true",
                        help="Invoke scripts/import_wechat_article_capture.py")
    parser.add_argument("--no-import-dry-run", action="store_true",
                        help="When --import is set, pass --dry-run to the import script too (double-safe)")
    parser.add_argument("--json", action="store_true", help="Emit JSON output")
    parser.add_argument("--path", type=str, default=None,
                        help="Override the capture JSON path (default: most recent in inbox/raw/wechat/)")
    args = parser.parse_args()

    # Resolve capture path
    if args.path:
        capture = Path(args.path)
        if not capture.is_absolute():
            capture = KB_HOME / args.path
    else:
        capture = find_latest_capture()
    if capture is None or not capture.exists():
        msg = f"No capture JSON found at {capture or INBOX_WECHAT}"
        if args.json:
            print(json.dumps({"error": msg}, ensure_ascii=False))
        else:
            print(f"ERROR: {msg}", file=sys.stderr)
        sys.exit(2)

    # Validate
    ok, errors = validate_capture(capture)
    if not ok:
        if args.json:
            print(json.dumps({"error": "schema_invalid", "details": errors,
                              "path": str(capture)}, ensure_ascii=False))
        else:
            print(f"ERROR: capture schema invalid: {errors}", file=sys.stderr)
        sys.exit(3)

    # Render
    out = render_dry_run(capture)

    if args.json and not args.do_import:
        print(json.dumps(out, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.json and args.do_import:
        # json + import: print a one-line JSON before invoking
        print(json.dumps({"bridge": "invoking_import", **out}, ensure_ascii=False))

    if not args.json:
        print("=" * 70)
        print("WeChat capture → import bridge (v0.3.62)")
        print("=" * 70)
        for k in ("capture_rel", "title", "source_url", "account_name", "author",
                  "published_date", "captured_at", "content_chars"):
            print(f"  {k:20s}: {out.get(k)}")
        print()
        print("Next steps:")
        print(f"  dry-run : {out['next_step_dry_run']}")
        print(f"  real    : {out['next_step_import']}")
        print()
        print(f"WARNING: {out['warning']}")
        print()

    if args.do_import:
        # Import invocation; respects --no-import-dry-run as double-safety
        rc = invoke_import(capture, dry_run=args.no_import_dry_run)
        sys.exit(rc if rc == 0 else 4)

    sys.exit(0)


if __name__ == "__main__":
    main()