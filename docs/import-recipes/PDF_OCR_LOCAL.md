# Local PDF OCR Import Recipe

> **Status**: Active since v0.3.62
> **Audience**: AI agents and human reviewers importing **local** PDF files into the knowledge base
> **Related scripts**: `scripts/check_kb.py`, `scripts/update_site.py`, `scripts/check_pages_sync.py`, `scripts/check_translation_residue.py`, `scripts/check_task_preflight.py`, `scripts/check_task_postflight.py`
> **Related docs**: `docs/AGENT_COMMANDS.md`, `docs/REPORTING_TEMPLATE.md`, `docs/TRANSLATION_RESIDUE_POLICY.md`, `templates/prompts/import_article_prompt.md`
> **Known good example**: `content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/` (commit `bdb1bc8`, v0.3.59 era)

This recipe is the **canonical workflow** for any task that begins with the
user supplying a local PDF and ends with a translated knowledge-base entry.
The 2026-06-29 Le Guin *The Carrier Bag Theory of Fiction* import is the
reference implementation. Any agent handling such a task **MUST** load this
recipe first.

---

## 1. Purpose

Codify the local-PDF OCR import path so that:

- A user message of the form "把这个本地 PDF OCR 识别、翻译并加入知识库：`<path>`"
  produces a **consistent, auditable, fully translated KB entry** with no
  free-form improvisation.
- Every PDF-derived entry in the catalog follows the same directory layout,
  metadata schema, and translation quality bar as URL-derived entries.
- Hard-stop failures are unambiguous and do not silently produce half-finished
  entries that pollute the catalog.
- The PDF (which is typically large, may be copyrighted, and is often
  scanned without a text layer) is handled with proper provenance
  tracking without forcing it into git.

## 2. Trigger conditions

Load this recipe when the user message **explicitly** contains:

- "OCR" / "识别" (combined with PDF)
- "本地 PDF" / "local PDF" / "把这个 PDF"
- "加入知识库" / "入库" / "完整翻译并加入"
- "扫描版" / "扫描件"
- Filename ending in `.pdf` and the user says "翻译" / "入库"

Do **not** load this recipe (or any other import recipe) when the user only
says "分析这个 PDF" / "summarize this PDF" / "read this PDF". In that case the
correct action is a read-only analysis; the result goes into a chat reply,
not into the knowledge base. Mis-routing analysis → import is a P0 violation.

## 3. Preflight (mandatory)

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
git rev-parse --short HEAD               # must equal origin/main
git rev-parse --short origin/main
python3 scripts/check_release_tags.py    # capture recommended_next_minor
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-<planned-suffix>
```

**Hard-stop on preflight FAIL**: do not touch any files, do not run OCR,
do not commit, do not push. Write a blocked report to
`reports/pdf_ocr_local_import_blocked_<YYYYMMDD>.md` and exit.

## 4. PDF inspection

```bash
PDF_PATH="<absolute path supplied by user>"
test -f "$PDF_PATH" || { echo "PDF not found"; exit 1; }

pdfinfo "$PDF_PATH" | head -25                # pages, producer, encrypted
pdftotext "$PDF_PATH" - | wc -c               # text layer size in bytes
file "$PDF_PATH"                              # format check
```

Capture the following into the OCR report (see §9):

- `Producer` (often reveals "Document Capture" or scanner name)
- `Pages` (1..N)
- `Page size` (Letter / A4)
- `Encrypted` (No = pass)
- `CreationDate` (provenance)
- `Text layer bytes` (0 = pure scan, >0 = has extractable text)

## 5. Text-layer detection

The branching decision:

| `pdftotext` byte count | Decision |
|---|---|
| ≥ 200 bytes per page on average | Treat as **text-layer PDF**. Skip OCR. Use `pdftotext -layout` output as `source.md` candidate. Validate page count and footnote/header hygiene before accepting. |
| 0 to a few hundred bytes total | Treat as **mixed / sparse**. Run `pdftotext` first, then OCR the pages with missing text. |
| ≈ 0 bytes | Treat as **scanned**. Run OCR (see §6). |

The Le Guin reference case is **scanned** (`Producer: Document Capture`,
`pdftotext` returned 4 bytes for 4 pages, no embedded text).

## 6. OCR fallback (scanned PDFs)

Use only locally available tools. **Do not** install new dependencies.

```bash
mkdir -p /tmp/pdf-ocr-pages
pdftoppm -r 250 "$PDF_PATH" /tmp/pdf-ocr-pages/page -png
for p in /tmp/pdf-ocr-pages/page-*.png; do
    tesseract "$p" "${p%.png}" 2>/dev/null
done
cat /tmp/pdf-ocr-pages/page-*.txt > /tmp/pdf-ocr-pages/all.txt
```

- DPI 250 is the reference value; do not exceed 300 unless image quality
  demands it (and document the deviation in the OCR report).
- If a page is blank in the OCR output, **rerun with `--psm 1` (auto with
  OSD)** and re-verify before flagging the page as unrecognizable.
- Keep the per-page text files in a temp dir; the canonical source lives
  in `content/articles/.../source.md`, not in `/tmp`.

## 7. Required OCR evidence

Every PDF-derived KB entry **must** include a report at
`reports/pdf_ocr_import_<YYYY-MM-DD>-<slug>.md` (alongside the entry
directory). The report must contain:

1. PDF absolute path
2. `pdfinfo` key-value output (pages, producer, encrypted, page size)
3. Text-layer detection result (bytes from `pdftotext`)
4. OCR toolchain and DPI used
5. Per-page OCR status table (page # | book page | content summary | coverage | issues)
6. List of OCR artifacts and their resolution method
7. Hard-stop trigger check (must be all clear)
8. Content boundary statement: which pages of the book / report / PDF
   are in scope, which are out of scope
9. Inputs to downstream steps (source.md structure, word counts, citations)

## 8. Entry directory selection

```bash
DATE=$(date -u +%Y-%m-%d)
SLUG="<author-or-title-slug>"
ITEM_DIR="content/articles/$DATE/$DATE-$SLUG"
mkdir -p "$ITEM_DIR"
```

Rules:

- Use `content/articles/YYYY/YYYY-MM-DD-<slug>/` for essays, critical
  reviews, and other long-form single-piece PDFs.
- Use `content/papers/YYYY/YYYY-MM-DD-<slug>/` for peer-reviewed papers
  (currently not a stable route — if `update_site.py` does not handle
  papers cleanly, fall back to `content/articles/...` and tag as `paper`
  in `metadata.yaml`).
- Use `content/books/YYYY/YYYY-MM-DD-<slug>/` for full-book PDFs (only
  when the entire book is in scope; multi-chapter partial imports must
  use `articles/`).
- **Hard-stop if the same `YYYY-MM-DD-<slug>` already exists** in the
  content tree. Choose a different slug or date.

## 9. Required file layout

```
content/articles/YYYY/YYYY-MM-DD-<slug>/
├── metadata.yaml          # schema-compliant
├── source.md              # OCR'd or extracted text, page-tagged
├── translation.zh-CN.md   # full Simplified Chinese translation
├── summary.md             # one-sentence + key quotes + extension questions
├── notes.md               # preflight/duplicate/blocked/OCR decisions
└── source.local-ref.txt   # only if PDF is gitignored (always for PDF > 1MB)
```

Plus, alongside the content tree:

```
reports/pdf_ocr_import_<YYYY-MM-DD>-<slug>.md   # OCR evidence report
```

## 10. metadata.yaml rules

Mandatory fields (from `check_kb.py`):

```yaml
title: "<English title from PDF, or romanized if no English>"
title_zh: "<中文标题>"
author: "<author from PDF, or 'unknown'>"
source: "<book / report / archive name, pp. X-Y>"
source_url: null                    # null because the PDF is local
source_url_missing: true            # REQUIRED when source_url is null
source_site: "local-pdf"            # REQUIRED — this is the canonical marker
local_pdf_path: "inbox/raw/pdf/YYYY-MM-DD-<slug>.pdf"   # see §15
source_pdf_sha256: null             # leave null unless user provides it
published_date: "<YYYY-MM-DD from PDF, or null>"
publication_year: <int>             # from PDF cover/copyright page
captured_date: "<YYYY-MM-DD today>"
type: "essay"                       # essay | paper | book-chapter | report
content_kind: "literary_criticism"  # free-form, document the genre
language: "en"                      # the source language
translation_language: "zh-CN"
extraction_method: "tesseract-5.3.4-ocr-250dpi"  # or pdftotext, etc.
ocr_report: "reports/pdf_ocr_import_YYYY-MM-DD-<slug>.md"
extraction_scope: "<what pages / chapters are in scope>"
status: "translated"                # translated | imported-no-translation
tags:                               # 6-12 entries, see docs/TAXONOMY.md
  - ursula-k-le-guin
  - narrative-theory
  - ...
topics:                             # 3-8 entries
  - ...
word_count:
  source: <int>                     # actual English word count of source.md
  translation: <int>                # actual CJK character count of translation.zh-CN.md
```

Author / published_date handling:

- If author is unrecoverable from the PDF → use `unknown` (string), not
  `null`. The schema requires `author` to be non-empty.
- If `published_date` is unrecoverable → use `null` for the field value
  but keep the key present. Do not write "PLACEHOLDER".
- `check_kb.py` validates these rules; do not bypass.

## 11. source.md rules

- **No summarization.** The file is the canonical OCR'd text.
- Preserve the original section structure with `##` / `###` headings
  as they appear in the PDF (or as reconstructed from the OCR
  page headers / footers).
- Insert `<!-- page: N -->` markers at every page boundary, where
  `N` is the **book / report page number** visible in the header /
  footer (not the PDF page number, which may differ).
- Where the original page header is preserved (e.g. `> 164 URSULA
  K. LE GUIN`), keep it in a blockquote.
- Tables, footnotes, image captions: keep verbatim. Footnote markers
  (¹ ² ³ or 1. 2. 3.) must stay.
- OCR artifacts must be **flagged, not silently fixed**. Use
  `[OCR疑似: ...]` inline annotation. Example:
  - OCR: `Nattve American Women`
  - Source: `[OCR疑似: OCR 写作 "Nattve"]American Women`
  - **Never** replace silently. A human reviewer must be able to
    revert from `source.md` alone.
- Hard-stop: if a full page is missing, garbled, or has fewer than
  ~50% of expected words, mark `[OCR疑似: 整页无法识别]` and **stop the
  import**. Do not push a half-empty entry.

## 12. translation.zh-CN.md rules

- Translate **every sentence** of `source.md`. No "TLDR" or summary-as-translation.
- Maintain the same heading hierarchy as `source.md`.
- Preserve `<!-- page: N -->` markers. Do not translate them.
- For proper nouns (people, books, places), use the **`中文（English）`**
  pattern on first appearance; English alone is fine on subsequent
  appearances if the Chinese already established the referent.
- For book titles, prefer `《中文书名》(*English Title*)` if the book has
  a conventional Chinese name; otherwise `《English Title》` or italicized
  English.
- Footnotes, captions, and image alt text must be translated.
- URLs, code, file names, dates, version numbers stay verbatim.
- OCR-flagged terms in `source.md` must be translated to the **most
  likely correct form** (the form flagged by `[OCR疑似: ...]`), not
  literally to the OCR'd nonsense. But **do not translate the flag
  itself** — keep `[OCR疑似: ...]` exactly as in the source.
- Long English sentences may be paraphrased into natural Chinese;
  literal word-order translations are not required, but content must
  be complete.

## 13. summary.md rules

Minimum sections:

- One-sentence summary in Chinese
- Core question the document addresses
- Main arguments (numbered list matching the document's structure)
- Key people / concepts / places
- Notable direct quotes (Chinese with English original in a table)
- 3–6 extension research questions
- Knowledge-base search keywords (mix of Chinese and English)

## 14. notes.md rules

Use the `templates/notes.md` style. Required sections:

- **Preflight**: status, planned tag, working tree, HEAD, recommended minor
- **Source information**: author, original publication, pages, license note
- **Extraction scope**: start / end / length, why-not-the-whole-book
- **Duplicate check**: title / title_zh / author / slug not found
- **Blocked check**: PDF open, OCR pipeline, no encryption, no paywall
- **OCR / translation decisions**: table of OCR artifacts and how each was
  resolved, with rationale for "minimal correction" policy
- **Quality check results**: paste the actual `check_kb.py` /
  `update_site.py` / `check_pages_sync.py` / `check_translation_residue.py`
  outputs (or at least their PASS/FAIL line and warnings).
- **待确认问题 (To-confirm)**: items the reviewer must double-check.
- **可关联的知识库主题 (Related KB topics)**: paths to existing entries
  that this one extends, contradicts, or complements.

## 15. source.local-ref.txt rules

When the PDF is **gitignored** (i.e. the repo's `.gitignore` rule `*.pdf`
or similar excludes it), the entry directory must contain
`source.local-ref.txt` with:

- Absolute path on the user's machine to the source PDF
- Path of the local working copy in the repo (e.g.
  `inbox/raw/pdf/YYYY-MM-DD-<slug>.pdf`)
- Format / size / page count / producer of the PDF
- A note that the file is intentionally not in git and the reason
  (typically: large file, copyrighted material, or both)

When the PDF **is** committed (rare; only for CC0 / public-domain
short documents), `source.local-ref.txt` is unnecessary; commit the
PDF as `source.pdf` instead.

## 16. PDF gitignore handling

The repo's `.gitignore` already includes `*.pdf`. Respect it. Do not
attempt to commit, force-add, or `git add -f` the PDF.

If the user explicitly asks to commit the PDF (unusual), document the
request in `notes.md` and use `git add -f <path>` after a separate
explicit confirmation. Default behavior: keep PDF local, point to it
via `source.local-ref.txt`.

## 17. Duplicate detection

Before creating the entry directory, run:

```bash
grep -l "<title or first 30 chars of title>" content/*/2026/*/source.md
grep -l "<author>" content/*/2026/*/metadata.yaml
```

If a duplicate is found, **stop** and ask the user whether to:

- Skip (no entry created)
- Replace (delete old, create new — only if the user owns both imports)
- Add a new entry with a different slug (e.g. date suffix)

## 18. Hard-stop cases (mandatory)

Any of the following **must** stop the import and produce a blocked
report. Do **not** commit, push, or update the catalog in any of these
cases.

| # | Hard-stop condition | Detection |
|---|---|---|
| 1 | PDF does not exist at the supplied path | `test -f "$PDF_PATH"` |
| 2 | PDF is encrypted or corrupted; `pdfinfo` fails or `pdftoppm` errors | `pdfinfo` exit code; `pdftoppm` stderr |
| 3 | OCR output is missing a page (page-N.txt absent or empty) | per-page file size check |
| 4 | Multiple pages unrecognizable (≥ 2 pages with empty / garbled OCR) | per-page word count threshold |
| 5 | Text layer / OCR garbled at the character level (e.g. ≥ 30% non-ASCII gibberish per page) | heuristic word/char ratio |
| 6 | TOC / body boundary cannot be determined (no clear page headers, no chapter markers, multi-section PDF with no clue where the body starts) | reviewer judgment, documented in OCR report |
| 7 | Cannot confirm document completeness (e.g. PDF cuts off mid-section, last page ends mid-sentence, signature page missing) | reviewer judgment |
| 8 | A required metadata field is unrecoverable and cannot be expressed with `source_url_missing: true` / `source_site: "local-pdf"` / `published_date: null` / `author: "unknown"` | `check_kb.py` will FAIL — fix forward or stop |
| 9 | `check_kb.py` FAILs after writing the entry | re-run after every fix; if still FAIL, stop |
| 10 | `check_pages_sync.py` FAILs after `update_site.py` | re-run `sync_pages_docs.py`; if still FAIL, stop |
| 11 | `check_translation_residue.py` reports residue that is **not** a proper noun / book title / URL / literature citation (i.e. real untranslated prose) | manual review of every residue; fix forward or stop |

When stopping, write a blocked report at
`reports/pdf_ocr_local_import_blocked_<YYYYMMDD>.md` with the failure
classification (§22), the steps already attempted, and the next
actionable item for the user.

## 19. Allowed-but-flagged cases

The following are **allowed** under this recipe, but the report must
document each one explicitly so a reviewer can audit:

- `source_url_missing: true` is set, and `source_url: null` — this is
  the canonical way to express "no public URL".
- `source_site: "local-pdf"` — the canonical marker for local-PDF
  imports. Distinguishes from `source_site: ""` (legacy note) and
  `source_site: <URL host>` (URL imports).
- PDF is `.gitignore`d; `source.local-ref.txt` keeps the local pointer.
- `check_translation_residue.py` WARNING with residue that is **all**
  book titles, proper nouns, URLs, or literature citations — these
  fall under `docs/TRANSLATION_RESIDUE_POLICY.md` and are acceptable.
  Paste the warning samples and the manual review verdict in
  `notes.md` and the final report.

## 20. Quality gates (run in this order)

```bash
python3 scripts/check_kb.py                  # integrity gate
python3 scripts/update_site.py               # build + sync (5/5 substeps)
python3 scripts/check_pages_sync.py          # post-sync gate
python3 scripts/check_translation_residue.py # WARNING-only
```

`check_kb.py` and `check_pages_sync.py` **must** exit 0. If either
exits non-zero, the import is **blocked**; do not commit, do not push.

`check_translation_residue.py` is WARN-only and is allowed to emit
warnings as long as every warning is a proper noun / book title /
URL / literature citation. Anything else requires a translation fix
or a hard-stop.

## 21. Commit / push / live smoke

Per-file `git add` only (no `git add -A` / `git add .`):

```bash
git add content/articles/YYYY/YYYY-MM-DD-<slug>/metadata.yaml
git add content/articles/YYYY/YYYY-MM-DD-<slug>/source.md
git add content/articles/YYYY/YYYY-MM-DD-<slug>/translation.zh-CN.md
git add content/articles/YYYY/YYYY-MM-DD-<slug>/summary.md
git add content/articles/YYYY/YYYY-MM-DD-<slug>/notes.md
git add content/articles/YYYY/YYYY-MM-DD-<slug>/source.local-ref.txt
git add reports/pdf_ocr_import_YYYY-MM-DD-<slug>.md
git add docs/data/catalog.json site/data/catalog.json index/*.md
git add docs/items/YYYY-MM-DD-<slug>/index.html
git add site/items/YYYY-MM-DD-<slug>/index.html

git diff --cached --stat
git diff --cached --name-only

git -c user.email="<>" -c user.name="<>" commit -m "Add OCR PDF knowledge entry: <title_zh> (zh-CN)"
git push origin main
```

For versioned tasks, additionally:

```bash
git tag -a v0.3.N-pdf-ocr-<rest> -m "<message>"
git push origin v0.3.N-pdf-ocr-<rest>
```

Live smoke:

```bash
curl -sI https://conanxin.github.io/hermes-knowledge-base/ | head -1
sleep 30  # typical CDN propagation
curl -s https://conanxin.github.io/hermes-knowledge-base/data/catalog.json \
  | python3 -c "import json, sys; d=json.load(sys.stdin); print(len(d), 'records')"
curl -sI "https://conanxin.github.io/hermes-knowledge-base/items/YYYY-MM-DD-<slug>/" | head -1
```

If the live catalog is still N (not N+1), the status is
`PENDING_CDN_SYNC`, which is **not** a FAIL. Document it in the report.

## 22. Reporting requirements

Use `docs/REPORTING_TEMPLATE.md` 模板 3 (9 sections) for any
`pdf-ocr-kb-import` task that pushes. Mandatory fields beyond the
template's defaults:

- `OCR 方法与页数` (OCR method + page count)
- `新条目目录` (entry directory path)
- `生成文件列表` (file list with sizes)
- `检查结果` (paste check_kb.py / update_site.py / check_pages_sync.py / check_translation_residue.py outputs)
- `commit hash`
- `push 状态` (success / rejected / error)
- `live URL 或 PENDING_CDN_SYNC`
- `已知 OCR/翻译限制` (every OCR artifact and its resolution, every
  un-translated phrase, every page that was below 100% coverage)

For blocked imports, use 模板 1 (3 sections) at
`reports/pdf_ocr_local_import_blocked_<YYYYMMDD>.md` with the
hard-stop classification filled in.

## 23. Maintenance rules

- This recipe is updated when a new local-PDF import case introduces
  a new OCR pipeline step, a new metadata field, or a new hard-stop
  case not already covered.
- The "known good example" line at the top must point to the most
  recent successful local-PDF import. Bump it after every successful
  import of this kind.
- Cross-references to `docs/AGENT_COMMANDS.md`, the workflow doc, and
  the command doc must be kept in sync. If you change the directory
  layout here, update all three downstream docs in the same commit.
- Tag suffix convention: `v0.3.N-pdf-ocr-local-import-recipe` for the
  recipe-hardening task itself; `v0.3.N-pdf-ocr-<source-slug>` for an
  individual import. The two are different tasks and must not share a
  tag.
- Do not add new dependencies to the OCR pipeline. If a new step
  requires a new tool, document the dependency in this recipe AND
  the OCR report, but do not auto-install.

---

## Appendix A. Reference: Le Guin import checklist (worked)

Used for `content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/`
(commit `bdb1bc8`):

1. Preflight: PASS, planned tag v0.3.59 (or any compatible minor)
2. `pdfinfo`: 4 pages, 792×612 pt, "Document Capture", 3.0 MB, not encrypted
3. `pdftotext` returned 4 bytes → scanned, OCR fallback
4. `pdftoppm -r 250` → 4 PNG @ 2750×2125 px
5. `tesseract 5.3.4` (eng, default) → 4 per-page txt, all 100% coverage
6. 8 character-level OCR artifacts (e.g. `Nattve` → `Native`),
   flagged in `source.md` with `[OCR疑似: ...]`
7. Entry: `content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/`
8. 6 files: metadata.yaml + source.md + translation.zh-CN.md + summary.md + notes.md + source.local-ref.txt
9. PDF gitignored; `inbox/raw/pdf/2026-06-29-le-guin-carrier-bag-theory-of-fiction.pdf`
   kept locally
10. Companion essay "Heroes" (pp. 170–171) only opening included;
    scan boundary documented in `extraction_scope` field
11. `check_kb.py` PASS 53/53 → 54/54 after entry
12. `update_site.py` PASS 5/5
13. `check_pages_sync.py` PASS
14. `check_translation_residue.py` WARNING (9 entries, all book titles
    and proper nouns; manually reviewed and approved)
15. Per-file `git add`, commit, push
16. `PENDING_CDN_SYNC` on live catalog (CDN lag)

## Appendix B. Quick command sequence

For an experienced agent, the full happy path is roughly:

```bash
PDF="$1"
cd ~/hermes-knowledge-base
git fetch origin && git pull --ff-only origin main
python3 scripts/check_release_tags.py
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-pdf-ocr-<slug>

pdfinfo "$PDF"
test -f "$PDF"
pdftotext "$PDF" - | wc -c   # 0 = scanned → OCR

mkdir -p /tmp/pdf-ocr-pages
pdftoppm -r 250 "$PDF" /tmp/pdf-ocr-pages/page -png
for p in /tmp/pdf-ocr-pages/page-*.png; do tesseract "$p" "${p%.png}"; done

# Read OCR, write source.md + translation.zh-CN.md + summary.md + notes.md
# + metadata.yaml + source.local-ref.txt + reports/pdf_ocr_import_*.md

python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/check_pages_sync.py
python3 scripts/check_translation_residue.py

# Per-file git add → commit → push
# python3 scripts/check_task_postflight.py ...
```
