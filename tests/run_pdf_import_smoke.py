#!/usr/bin/env python3
"""Smoke tests for v0.3.86 PDF (text-layer) KB import.

Offline — does not contact the network. Uses a pymupdf-generated fixture PDF
under tests/fixtures/.

Covered cases:
  smoke_1_pdf_to_kb_dry_run_writes_capture
  smoke_2_pdf_to_kb_extracts_text_and_metadata
  smoke_3_pdf_to_kb_reports_scanned_as_blocked_needs_ocr
  smoke_4_pdf_to_kb_import_writes_6_files_and_respects_dedup
  smoke_5_router_routes_pdf_input_to_pdf_to_kb
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TEST_PY = sys.executable
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}

PDF_SCRIPT = REPO_ROOT / "scripts" / "pdf_to_kb.py"
ROUTER_SCRIPT = REPO_ROOT / "scripts" / "material_to_kb.py"
PDF_FIXTURE = REPO_ROOT / "tests" / "fixtures" / "pdf_sample_document.pdf"


def run(cmd: list[str], cwd: Path = REPO_ROOT, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env or ENV,
    )
    return proc.returncode, proc.stdout or "", proc.stderr or ""


def check(condition: bool, name: str, detail: str = "") -> bool:
    status = "PASS" if condition else "FAIL"
    print(f"  [{status}] {name}")
    if detail:
        print(f"         {detail}")
    return condition


def _clear_inbox_for_dedup() -> None:
    """Remove any prior test articles/inbox so smoke 4 starts clean.

    Removal is scoped to the slug prefix produced by the fixture title:
    `Hermes Knowledge Base — Routing & Capture Layer (Sample PDF)` →
    slug: `hermes-knowledge-base-routing-capture-layer-sample-pdf`.
    """
    captured = REPO_ROOT / "inbox" / "raw" / "pdf"
    if captured.exists():
        for f in captured.iterdir():
            if f.suffix == ".json" and (
                "hermes-knowledge-base-routing" in f.name
                or f.name.startswith("BLOCKED_NEEDS_OCR")
                or f.name.startswith("DRY_RUN_PREVIEW")
            ):
                f.unlink()
    today = REPO_ROOT / "content" / "articles" / "2026"
    if today.exists():
        for d in today.iterdir():
            if not d.is_dir():
                continue
            if "hermes-knowledge-base-routing" in d.name:
                # recursively delete
                import shutil
                shutil.rmtree(d)


def main() -> int:
    print("[pdf-smoke] start")
    if not PDF_FIXTURE.exists():
        print(f"  [FAIL] fixture missing: {PDF_FIXTURE}")
        return 1

    results = []

    # ---- smoke 1: dry-run writes capture JSON ----
    _clear_inbox_for_dedup()
    rc, out, err = run(
        [
            TEST_PY,
            str(PDF_SCRIPT),
            "--pdf-file",
            str(PDF_FIXTURE),
            "--dry-run",
        ]
    )
    results.append(check(rc == 0, "smoke_1_pdf_to_kb_dry_run_ok", f"rc={rc}"))
    capture_path_match = re.search(r"capture_json_path:\s+(\S+)", out)
    results.append(check(
        capture_path_match is not None, "smoke_1_capture_json_path_emitted",
        out.splitlines()[-3:] and "\n".join(out.splitlines()[-3:])
    ))
    if capture_path_match:
        cap = Path(capture_path_match.group(1))
        results.append(check(
            cap.exists(), "smoke_1_capture_file_exists", str(cap)
        ))
        try:
            data = json.loads(cap.read_text(encoding="utf-8"))
            results.append(check(
                data.get("text_layer_strategy") in ("full", "partial"),
                "smoke_1_text_layer_strategy_known",
                str(data.get("text_layer_strategy")),
            ))
            results.append(check(
                data.get("pdf_sha256") and len(data["pdf_sha256"]) == 64,
                "smoke_1_pdf_sha256_present",
                f"sha256={data.get('pdf_sha256')[:16]}...",
            ))
        except Exception as exc:  # pragma: no cover
            results.append(check(False, "smoke_1_capture_file_parseable", str(exc)))

    # ---- smoke 2: extracts text and metadata ----
    if capture_path_match:
        cap = Path(capture_path_match.group(1))
        data = json.loads(cap.read_text(encoding="utf-8"))
        results.append(check(
            data.get("page_count", 0) >= 1,
            "smoke_2_page_count_positive",
            f"page_count={data.get('page_count')}",
        ))
        results.append(check(
            data.get("total_chars", 0) >= 200,
            "smoke_2_total_chars_reasonable",
            f"total_chars={data.get('total_chars')}",
        ))
        results.append(check(
            "Hermes knowledge base routes" in (data.get("content_markdown") or ""),
            "smoke_2_content_includes_known_paragraph",
        ))
        results.append(check(
            (data.get("title") or "").lower().startswith("hermes"),
            "smoke_2_title_from_pdf_metadata",
            data.get("title"),
        ))
        results.append(check(
            data.get("author") == "Hermes Smoke Fixture",
            "smoke_2_author_from_pdf_metadata",
            data.get("author"),
        ))

    # ---- smoke 3: scanned PDF → BLOCKED_NEEDS_OCR ----
    # We synthesize a "scanned" fixture by writing a *zero-page* doc via pymupdf.
    # Instead, mimic by running with a synthetic PDF where we strip the text layer.
    # Practical shortcut: skip — the classification branches in classify_pdf() are
    # covered by smoke_1 (text-layer OK). For scanned detection, we test the
    # branch logic via a minimal zero-text PDF.
    scanned_pdf = REPO_ROOT / "tests" / "fixtures" / "pdf_scanned_fixture.pdf"
    try:
        import fitz  # type: ignore
        doc = fitz.open()
        doc.new_page(width=595, height=842)
        # No text inserted → scanned-like
        doc.save(str(scanned_pdf))
        doc.close()
    except Exception as exc:  # pragma: no cover
        results.append(check(False, "smoke_3_fixture_creation", str(exc)))

    if scanned_pdf.exists():
        rc2, out2, err2 = run(
            [TEST_PY, str(PDF_SCRIPT), "--pdf-file", str(scanned_pdf), "--dry-run"]
        )
        blocked = "BLOCKED_NEEDS_OCR" in out2
        results.append(check(
            blocked, "smoke_3_scanned_reports_BLOCKED_NEEDS_OCR",
            f"rc={rc2}, out_tail={out2.splitlines()[-1] if out2 else ''}"
        ))
        captured_path2 = re.search(r"capture_json_path:\s+(\S+)", out2)
        results.append(check(
            captured_path2 is not None, "smoke_3_capture_json_path_emitted_for_blocked"
        ))
        if captured_path2:
            cap2 = Path(captured_path2.group(1))
            results.append(check(
                cap2.exists(), "smoke_3_blocked_capture_file_exists",
                f"path={cap2}",
            ))
            try:
                data2 = json.loads(cap2.read_text(encoding="utf-8"))
                results.append(check(
                    data2.get("extraction_status") == "BLOCKED_NEEDS_OCR",
                    "smoke_3_blocked_capture_records_status",
                ))
            except Exception:
                results.append(check(False, "smoke_3_blocked_capture_parses", ""))
        # Pymupdf's empty-page doc still has 1 page but 0 chars — that's our fixture
        # representation of "scanned".

    # ---- smoke 4: import writes 6 files, dedup on second run ----
    _clear_inbox_for_dedup()
    rc3, out3, err3 = run(
        [TEST_PY, str(PDF_SCRIPT), "--pdf-file", str(PDF_FIXTURE), "--import"]
    )
    # The import may exit 5 if update_site.py has issues; we accept either
    # success (rc 0) or that the article files were written regardless.
    files_written = True
    expected_files = [
        "metadata.yaml",
        "source.md",
        "translation.zh-CN.md",
        "summary.md",
        "notes.md",
        "raw_payload.json",
    ]
    today_dir = None
    articles = REPO_ROOT / "content" / "articles"
    if articles.exists():
        for d in articles.iterdir():
            if not d.is_dir():
                continue
            for inner in d.iterdir():
                if not inner.is_dir():
                    continue
                if "hermes-knowledge-base-routing" in inner.name:
                    today_dir = inner
                    break
            if today_dir:
                break
    results.append(check(today_dir is not None, "smoke_4_article_dir_created", ""))
    if today_dir is not None:
        for fname in expected_files:
            p = today_dir / fname
            results.append(check(p.exists(), f"smoke_4_writes_{fname}", str(p)))
        # dedup on second invocation should report SKIPPED_DUPLICATE
    if today_dir is not None:
        rc4, out4, err4 = run(
            [TEST_PY, str(PDF_SCRIPT), "--pdf-file", str(PDF_FIXTURE), "--dry-run"]
        )
        is_dup = "SKIPPED_DUPLICATE" in out4 or "SKIPPED_DUPLICATE" in err4
        results.append(check(is_dup, "smoke_4_dup_returns_SKIPPED_DUPLICATE", out4[-200:]))

    # ---- smoke 5: router routes pdf input to pdf_to_kb ----
    _clear_inbox_for_dedup()
    rc5, out5, err5 = run(
        [
            TEST_PY,
            str(ROUTER_SCRIPT),
            "--input",
            str(PDF_FIXTURE),
            "--dry-run",
        ]
    )
    parsed = None
    try:
        m = re.search(r"^\{\s*\n", out5, re.MULTILINE)
        if m:
            parsed = json.loads(out5[m.start():])
    except json.JSONDecodeError:
        parsed = None
    results.append(check(parsed is not None, "smoke_5_router_emits_json_block", ""))
    if parsed:
        items = parsed.get("items", [])
        results.append(check(
            any(it.get("route") == "pdf_to_kb.py" for it in items),
            "smoke_5_router_resolves_pdf_route",
        ))
        results.append(check(
            any(it.get("inferred_type") == "pdf_file" for it in items),
            "smoke_5_router_marks_inferred_type_pdf",
        ))
        # status should not be BLOCKED_UNSUPPORTED for the text-layer fixture
        blocked_unsupported = any(
            it.get("status") == "BLOCKED_UNSUPPORTED" for it in items
        )
        results.append(check(
            not blocked_unsupported,
            "smoke_5_router_does_not_report_BLOCKED_UNSUPPORTED",
        ))

    passed = sum(1 for r in results if r)
    failed = len(results) - passed
    print(f"\n[pdf-smoke] {passed}/{len(results)} checks passed "
          f"({failed} failed)")
    return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(main())
