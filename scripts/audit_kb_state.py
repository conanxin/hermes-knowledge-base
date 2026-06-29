#!/usr/bin/env python3
"""
audit_kb_state.py — Lightweight state auditor for hermes-knowledge-base.

v0.3.60 — Reads content/**/metadata.yaml + cross-checks against index/
catalog and README. Surfaces drift between documented state and real state.

Design contract:
- Default: WARN-only (does not raise / non-zero exit on historical drift)
- FAIL only on: catalog parse failure, metadata unreadable, site/docs sync mismatch
- Reports via stdout (plain text + simple table)
- Exits 0 unless a FAIL is found

Usage:
    python3 scripts/audit_kb_state.py
    python3 scripts/audit_kb_state.py --json
    python3 scripts/audit_kb_state.py --strict   # also treat WARN as FAIL
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FATAL: PyYAML not installed. pip install pyyaml", file=sys.stderr)
    sys.exit(2)

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"
README_PATH = BASE_DIR / "README.md"
SITE_CATALOG = BASE_DIR / "site" / "data" / "catalog.json"
DOCS_CATALOG = BASE_DIR / "docs" / "data" / "catalog.json"
INDEX_CATALOG_JSONL = BASE_DIR / "index" / "catalog.jsonl"

# Types that should have a `translation.zh-CN.md` if `translation_language: zh-CN` is set.
TRANSLATABLE_TYPES = {"article", "essay"}
# Types that are allowed to have an empty `source_site` (legacy migration case).
EMPTY_SOURCE_SITE_ALLOWED = {
    "note", "project", "resource", "report", "prompt",
    "resource_collection", "video", "academic_paper", "interview",
    "essay",
}
# Tags / topics count soft limits from README.
TAGS_SOFT_MIN, TAGS_SOFT_MAX = 6, 12
TOPICS_SOFT_MIN, TOPICS_SOFT_MAX = 3, 8


# ---------- collectors ----------

def collect_metadata():
    """Return list of (rel_path, dict) tuples; failure → None appended for hard errors."""
    items = []
    hard_fails = []
    for mf in sorted(CONTENT_DIR.rglob("metadata.yaml")):
        try:
            data = yaml.safe_load(mf.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            hard_fails.append(f"YAML parse error: {mf.relative_to(BASE_DIR)}: {e}")
            continue
        except OSError as e:
            hard_fails.append(f"Read error: {mf.relative_to(BASE_DIR)}: {e}")
            continue
        if not isinstance(data, dict):
            hard_fails.append(f"Non-dict YAML root: {mf.relative_to(BASE_DIR)}")
            continue
        items.append((mf, data))
    return items, hard_fails


def index_recent(items, key, n=10):
    """Return the n most-recent items by captured_date / import_date / fallback mtime."""
    def sort_key(item):
        mf, data = item
        for k in (key, "captured_date", "import_date"):
            v = data.get(k)
            if v:
                return str(v)
        return mf.stat().st_mtime  # fallback: file mtime
    sorted_items = sorted(items, key=sort_key, reverse=True)
    return sorted_items[:n]


# ---------- audit checks ----------

def check_dir_drift():
    """Detect coexisting /content/collections and /content/resource_collections."""
    findings = []
    if (CONTENT_DIR / "collections").is_dir() and (CONTENT_DIR / "resource_collections").is_dir():
        findings.append(
            f"DIR DRIFT: both 'content/collections' and 'content/resource_collections' exist. "
            f"All items declare type=resource_collection, but directory name has diverged. "
            f"Recommend consolidating under one directory (probably 'resource_collections')."
        )
    return findings


def check_stale_readme_numbers(items):
    """Look for outdated counts like '19' / '19/19' / '19 records' in README."""
    findings = []
    if not README_PATH.exists():
        return ["README.md missing"]
    text = README_PATH.read_text(encoding="utf-8")
    real_total = len(items)
    # Look for any "19" claims that look like item counts.
    bad_patterns = [
        (re.compile(r"\b总计\b[^|]*\*\*\s*19\b"), "stale 总计=19 in content type table"),
        (re.compile(r"PASS\s*\(\s*19\s*/\s*19\s*\)"), "stale 19/19 expected PASS"),
        (re.compile(r"\b19\s+records\b"), "stale '19 records' literal"),
        (re.compile(r"\b19\s+items\b"), "stale '19 items' literal"),
    ]
    for pat, desc in bad_patterns:
        if pat.search(text):
            findings.append(
                f"README contains {desc}. Real total = {real_total}. "
                f"Replace with managed block or update manually."
            )
    return findings


def check_postflight_cli_drift():
    """README should not instruct agents to use the old --expect-clean --expect-head-origin CLI."""
    findings = []
    if not README_PATH.exists():
        return findings
    text = README_PATH.read_text(encoding="utf-8")
    # Allowed elsewhere (in historical reports), but README itself should use new CLI.
    if "--expect-clean" in text and "check_task_postflight" in text:
        findings.append(
            "README mentions --expect-clean (legacy CLI). Current script supports "
            "--expect-clean via --profile article_import/versioned + --expect-clean flags. "
            "Recommend updating README to use --profile auto as the canonical example."
        )
    return findings


def check_type_coverage(items):
    """Find types that exist in metadata but are not mentioned in README's type table."""
    findings = []
    if not README_PATH.exists():
        return findings
    readme = README_PATH.read_text(encoding="utf-8")
    # Extract types actually used in metadata
    used_types = {d.get("type") for _, d in items if d.get("type")}
    # Look for the type-coverage table in README (rows starting with type name + pipe)
    table_rows = re.findall(r"\|\s*([a-z_]+)\s*\|\s*\d+\s*\|", readme)
    documented_types = set(table_rows)
    new_types = used_types - documented_types
    if new_types:
        findings.append(
            f"README type table missing types found in KB: {sorted(new_types)}. "
            f"Documented types: {sorted(documented_types)}."
        )
    return findings


def check_translation_file_for_translatable(items):
    """For translatable types (article/essay) with translation_language=zh-CN,
    the translation.zh-CN.md must exist."""
    findings = []
    for mf, data in items:
        t = data.get("type", "")
        tl = data.get("translation_language", "")
        if t not in TRANSLATABLE_TYPES:
            continue
        if tl != "zh-CN":
            continue
        item_dir = mf.parent
        rel = item_dir.relative_to(BASE_DIR)
        trans = item_dir / "translation.zh-CN.md"
        if not trans.exists():
            findings.append(
                f"MISSING translation.zh-CN.md for translatable type={t!r} with "
                f"translation_language='{tl}': {rel}"
            )
    return findings


def check_empty_source_site(items):
    """Detect source_site empty/None for types that shouldn't allow it."""
    findings = []
    for mf, data in items:
        t = data.get("type", "")
        ss = data.get("source_site", "")
        if t in EMPTY_SOURCE_SITE_ALLOWED:
            continue
        # Otherwise, source_site should be a non-empty string.
        if ss is None or ss == "":
            rel = mf.relative_to(BASE_DIR)
            findings.append(
                f"EMPTY source_site for type={t!r} (not in allowlist): {rel}"
            )
    return findings


def check_translation_language_null(items):
    """Detect translation_language: 'null' (string) which is a YAML schema smell."""
    findings = []
    for mf, data in items:
        tl = data.get("translation_language", None)
        if isinstance(tl, str) and tl.lower() in ("null", "none", "~"):
            rel = mf.relative_to(BASE_DIR)
            findings.append(
                f"translation_language is the string {tl!r} (likely a YAML null placeholder): {rel}"
            )
        elif tl is None:
            # Missing is fine for non-translatable types; only WARN for translatable ones
            t = data.get("type", "")
            if t in TRANSLATABLE_TYPES:
                rel = mf.relative_to(BASE_DIR)
                findings.append(
                    f"translatable type={t!r} but translation_language is null/missing: {rel}"
                )
    return findings


def check_tag_topic_counts(items):
    """WARN on tags/topics outside soft limits declared in README."""
    findings = []
    for mf, data in items:
        rel = mf.relative_to(BASE_DIR)
        tags = data.get("tags", [])
        topics = data.get("topics", [])
        if isinstance(tags, list):
            n = len(tags)
            if n < TAGS_SOFT_MIN or n > TAGS_SOFT_MAX:
                findings.append(
                    f"tags count={n} outside soft range [{TAGS_SOFT_MIN},{TAGS_SOFT_MAX}]: {rel}"
                )
        if isinstance(topics, list):
            n = len(topics)
            if n < TOPICS_SOFT_MIN or n > TOPICS_SOFT_MAX:
                findings.append(
                    f"topics count={n} outside soft range [{TOPICS_SOFT_MIN},{TOPICS_SOFT_MAX}]: {rel}"
                )
    return findings


def check_duplicate_tags(items):
    """WARN on duplicate tag values within a single metadata.yaml."""
    findings = []
    for mf, data in items:
        rel = mf.relative_to(BASE_DIR)
        for field in ("tags", "topics"):
            values = data.get(field, [])
            if not isinstance(values, list):
                continue
            seen = {}
            for v in values:
                if not isinstance(v, str):
                    continue
                seen[v] = seen.get(v, 0) + 1
            dupes = {k: c for k, c in seen.items() if c > 1}
            if dupes:
                findings.append(
                    f"duplicate {field} values in {rel}: {dupes}"
                )
    return findings


def check_catalog_drift(items):
    """Cross-check index/catalog.jsonl vs site/data/catalog.json vs docs/data/catalog.json."""
    findings = []
    hard_fails = []

    # 1. Read each catalog
    catalogs = {}
    for name, path in [
        ("index_jsonl", INDEX_CATALOG_JSONL),
        ("site", SITE_CATALOG),
        ("docs", DOCS_CATALOG),
    ]:
        if not path.exists():
            findings.append(f"catalog missing: {path.relative_to(BASE_DIR)}")
            continue
        try:
            if name == "index_jsonl":
                records = []
                for line in path.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    records.append(json.loads(line))
                catalogs[name] = records
            else:
                catalogs[name] = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as e:
            hard_fails.append(f"catalog parse error: {path.relative_to(BASE_DIR)}: {e}")

    if hard_fails:
        return findings, hard_fails

    # 2. Count records
    counts = {name: len(records) for name, records in catalogs.items()}

    # 3. Compare totals to real metadata.yaml count
    real_total = len(items)
    for name, c in counts.items():
        if c != real_total:
            findings.append(
                f"catalog count drift: {name}={c} vs metadata.yaml count={real_total}. "
                f"Run `python3 scripts/update_site.py` to regenerate."
            )

    # 4. Compare site vs docs total (byte-identical requirement)
    if "site" in counts and "docs" in counts and counts["site"] != counts["docs"]:
        hard_fails.append(
            f"site/docs catalog count mismatch: site={counts['site']} vs docs={counts['docs']}. "
            f"Run `python3 scripts/sync_pages_docs.py` to resync."
        )

    # 5. Spot-check: pick first 3 records from each catalog and compare slug/source_url/title
    slugs = {}
    for name, records in catalogs.items():
        slugs[name] = {r.get("slug", r.get("path", "")) for r in records}

    if "site" in slugs and "docs" in slugs:
        only_site = slugs["site"] - slugs["docs"]
        only_docs = slugs["docs"] - slugs["site"]
        if only_site or only_docs:
            hard_fails.append(
                f"site/docs slug mismatch: only_in_site={sorted(only_site)[:5]}, "
                f"only_in_docs={sorted(only_docs)[:5]}"
            )

    return findings, hard_fails


def check_site_docs_byte_identity():
    """Compare site/ top-level files vs docs/ top-level files for byte-identity."""
    findings = []
    hard_fails = []

    pairs = [
        ("site/data/catalog.json", "docs/data/catalog.json"),
        ("site/index.html", "docs/index.html"),
        ("site/styles.css", "docs/styles.css"),
        ("site/app.js", "docs/app.js"),
    ]
    for site_rel, docs_rel in pairs:
        sp = BASE_DIR / site_rel
        dp = BASE_DIR / docs_rel
        if not sp.exists() or not dp.exists():
            continue
        if sp.read_bytes() != dp.read_bytes():
            hard_fails.append(
                f"byte-identity mismatch: {site_rel} != {docs_rel}. "
                f"Run `python3 scripts/sync_pages_docs.py`."
            )
    return findings, hard_fails


# ---------- report renderer ----------

def render_report(audit):
    """Render audit dict to plain text report."""
    lines = []
    lines.append("=" * 60)
    lines.append("KB State Audit Report (v0.3.60)")
    lines.append("=" * 60)
    lines.append("")

    items = audit["items"]
    lines.append(f"Real metadata.yaml count: {len(items)}")
    lines.append("")
    lines.append("Type distribution:")
    for t, c in sorted(audit["by_type"].items(), key=lambda x: -x[1]):
        lines.append(f"  {t:20s} {c:3d}")
    lines.append("")
    lines.append("Status distribution:")
    for s, c in sorted(audit["by_status"].items(), key=lambda x: -x[1]):
        lines.append(f"  {s:20s} {c:3d}")
    lines.append("")
    lines.append("Top 10 source_site:")
    for s, c in sorted(audit["by_site"].items(), key=lambda x: -x[1])[:10]:
        lines.append(f"  {(s or '(empty/None)')[:40]:40s} {c:3d}")
    lines.append("")
    lines.append(f"Captured year buckets: {dict(sorted(audit['by_year'].items()))}")
    lines.append("")
    lines.append(f"Last 10 captured/imported:")
    for mf, data in audit["recent_10"]:
        rel = mf.relative_to(BASE_DIR)
        date = (data.get("captured_date") or data.get("import_date") or "")[:10]
        title = data.get("title_zh") or data.get("title") or "(no title)"
        lines.append(f"  {date}  {rel}  {title}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("Findings")
    lines.append("-" * 60)

    n_warn = 0
    for category, findings in audit["checks"].items():
        if not findings:
            continue
        lines.append(f"\n[{category}] ({len(findings)} findings)")
        n_warn += len(findings)
        for f in findings[:30]:  # cap per category to avoid runaway output
            lines.append(f"  - {f}")
        if len(findings) > 30:
            lines.append(f"  ... and {len(findings) - 30} more")

    lines.append("")
    lines.append("-" * 60)
    lines.append(f"HARD FAILURES: {len(audit['hard_fails'])}")
    lines.append(f"WARNINGS: {n_warn}")
    if audit["hard_fails"]:
        lines.append("\nHARD FAIL DETAILS:")
        for f in audit["hard_fails"]:
            lines.append(f"  ! {f}")
    lines.append("")
    lines.append("=" * 60)
    if audit["hard_fails"]:
        lines.append("STATUS: FAIL")
    elif n_warn:
        lines.append(f"STATUS: PASS_WITH_WARNINGS ({n_warn} warnings)")
    else:
        lines.append("STATUS: PASS")
    lines.append("=" * 60)
    return "\n".join(lines)


# ---------- main ----------

def main():
    parser = argparse.ArgumentParser(description="KB state auditor")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as FAIL")
    args = parser.parse_args()

    items, hard_fails_meta = collect_metadata()
    if hard_fails_meta:
        for f in hard_fails_meta:
            print("HARD FAIL:", f, file=sys.stderr)
        if args.strict or True:  # metadata parse failure is always FAIL
            if not args.json:
                print(f"\nSTATUS: FAIL ({len(hard_fails_meta)} metadata parse errors)")
            sys.exit(1)

    # Build summary stats
    by_type = Counter(d.get("type", "?") for _, d in items)
    by_status = Counter(d.get("status", "?") for _, d in items)
    by_site = Counter(d.get("source_site") for _, d in items)
    by_year = Counter((d.get("captured_date") or "")[:4] for _, d in items)
    recent_10 = index_recent(items, key="captured_date", n=10)

    # Run all checks
    checks = {}
    checks["dir_drift"] = check_dir_drift()
    checks["stale_readme_numbers"] = check_stale_readme_numbers(items)
    checks["postflight_cli_drift_in_readme"] = check_postflight_cli_drift()
    checks["type_coverage_in_readme"] = check_type_coverage(items)
    checks["missing_translation_for_translatable"] = check_translation_file_for_translatable(items)
    checks["empty_source_site"] = check_empty_source_site(items)
    checks["translation_language_null"] = check_translation_language_null(items)
    checks["tag_topic_count_out_of_range"] = check_tag_topic_counts(items)
    checks["duplicate_tags"] = check_duplicate_tags(items)

    catalog_warn, catalog_hard = check_catalog_drift(items)
    sync_warn, sync_hard = check_site_docs_byte_identity()

    checks["catalog_drift"] = catalog_warn
    checks["site_docs_byte_identity"] = sync_warn

    hard_fails = hard_fails_meta + catalog_hard + sync_hard

    audit = {
        "items_count": len(items),
        "items": items,
        "by_type": dict(by_type),
        "by_status": dict(by_status),
        "by_site": dict(by_site),
        "by_year": dict(by_year),
        "recent_10": [(mf, data) for mf, data in recent_10],
        "checks": checks,
        "hard_fails": hard_fails,
    }

    if args.json:
        # JSON-serialize the recent_10 by extracting title+path
        audit["recent_10"] = [
            {"path": str(mf.relative_to(BASE_DIR)),
             "title_zh": data.get("title_zh"),
             "title": data.get("title"),
             "date": (data.get("captured_date") or data.get("import_date") or "")[:10]}
            for mf, data in recent_10
        ]
        print(json.dumps(audit, ensure_ascii=False, indent=2, default=str))
    else:
        print(render_report(audit))

    if hard_fails:
        sys.exit(1)
    if args.strict:
        any_warn = any(len(v) > 0 for v in checks.values())
        if any_warn:
            sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()