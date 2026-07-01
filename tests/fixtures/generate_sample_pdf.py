#!/usr/bin/env python3
"""Generate a tiny text-layer PDF fixture for pdf_to_kb.py smoke tests.

Pure-local: uses pymupdf only, no network calls. The output is deterministic
enough that the smoke test can also assert extracted text contents.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import fitz  # type: ignore
except ImportError as exc:
    raise SystemExit(
        "pymupdf required: pip install --user pymupdf"
    ) from exc


SAMPLE_TITLE = "Hermes Knowledge Base — Routing & Capture Layer (Sample PDF)"
SAMPLE_AUTHOR = "Hermes Smoke Fixture"
SAMPLE_BODY_PARAGRAPHS = [
    "The Hermes knowledge base routes incoming materials through a thin adapter layer.",
    "Inputs are classified by URL scheme and file extension. Unknown routes are hard-stopped.",
    "When a route is supported, the importer writes a uniform 6-file entry to content/articles/.",
    "Dedup keys vary by route. Web uses canonical URL and content hash; PDFs use sha256 and (title, author, page_count).",
    "Imported items are regenerated into docs/items/ and site/items/ by update_site.py.",
    "All gate runners must be green before a fetch_result.json may be promoted to the handoff layer.",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True, help="output PDF path")
    args = parser.parse_args()

    out = Path(args.out).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4 in points
    # Title (bold-ish via large fontsize)
    page.insert_text((72, 64), SAMPLE_TITLE, fontsize=18)
    # Body: each paragraph as a textbox so they wrap + break.
    # Use insert_textbox with width and a Y offset per paragraph.
    body_y = 110
    for para in SAMPLE_BODY_PARAGRAPHS:
        rect = fitz.Rect(72, body_y, 523, body_y + 60)
        page.insert_textbox(rect, para, fontsize=11)
        body_y += 64
    page.insert_text((72, body_y + 16), f"_Author: {SAMPLE_AUTHOR}_", fontsize=10)
    doc.set_metadata(
        {
            "title": SAMPLE_TITLE,
            "author": SAMPLE_AUTHOR,
            "subject": "Smoke fixture",
            "producer": "pymupdf-fixture",
        }
    )
    doc.save(str(out))
    doc.close()
    print(f"wrote {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
