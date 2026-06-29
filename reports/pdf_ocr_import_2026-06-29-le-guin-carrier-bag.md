# PDF OCR Import Report — The Carrier Bag Theory of Fiction (1986)

**Date**: 2026-06-29
**Operator**: Hermes Agent (Telegram session, Xin Conan)
**Source PDF**: `/home/conanxin/.hermes/cache/documents/doc_168fe83c23d4_The-Carrier-Bag-Theory-of-Fiction.pdf`
**Local copy (gitignored)**: `inbox/raw/pdf/2026-06-29-le-guin-carrier-bag-theory-of-fiction.pdf`

---

## 1. PDF Structure

| Property | Value |
|---|---|
| Pages | 4 |
| Page size | 792 × 612 pts (US Letter) |
| Producer | "Document Capture" (scanned) |
| CreationDate | 2023-12-15 |
| Encrypted | No |
| Text layer | **No** (4 bytes from `pdftotext`) |
| Native language | English |
| Author | Ursula K. Le Guin |
| Content type | Literary critical essay (essay) + companion essay opening |
| Original publication | *Dancing at the Edge of the World* (Grove Press, 1986) |
| Source pages (book) | pp. 164–171 (Carrier Bag: 164–170; Heroes: 170–171+) |

The PDF is a **scanned image** of a book excerpt, no embedded text. The page-number
header `164 URSULA K. LE GUIN` and footer `THE CARRIER BAG THEORY OF FICTION 165` etc.
show this is two consecutive pages of a 1986 essay collection.

## 2. Extraction Method

| Stage | Tool | Output |
|---|---|---|
| Render to images | `pdftoppm -r 250` (250 DPI) | 4 PNG, 2750×2125 px each |
| OCR | `tesseract 5.3.4` (eng, default) | 4 per-page `.txt` |
| Merge | concat | `carrier-bag-ocr.txt` (15.9 KB) |

No additional OCR pass (e.g. deskew, denoise) was needed — scan quality is clean.

## 3. Per-Page OCR Status

| Page | Book page | Content | Coverage | OCR issues |
|---|---|---|---|---|
| 1 | 164–165 | Notes (3 footnotes) + opening of "The Carrier Bag Theory of Fiction" | 100% | `Nattve` → `Native`; `Indi-ana` is a soft hyphen line break; `Percetving` → `Perceiving` |
| 2 | 166–167 | Continuation: spear/mammoth simile, Woolf's "hero=bottle" gloss, Fisher quote | 100% | `fertilize itand` missing space; `how \|` is a line-wrap artifact for "how I" |
| 3 | 168–169 | "I am a human being after all"; novel-as-medicine-bundle; science-fiction as carrier bag | 100% | None |
| 4 | 170–171 | Closing of Carrier Bag; opening of companion essay "Heroes" (Scott / Left Hand of Darkness / "Sur") | 100% | `1 am` → `I am`; book pages visible at top of "Heroes" |

**No unrecognizable pages. No large-block omissions. Page boundaries clean.**

## 4. Decisions on OCR Artifacts

The following were **kept verbatim in `source.md`** with a `[OCR疑似: ...]` tag so a
human reviewer can confirm, rather than auto-correcting from external sources (no
network-based collating allowed for this task):

| Surface form in OCR | Likely correct form | Action |
|---|---|---|
| `Nattve` | `Native` | Tagged — common OCR confusion of `ti` |
| `Percetving` | `Perceiving` | Tagged — missing `r` in the middle |
| `Indi-ana` | `Indiana` | Soft hyphen; restored with `[OCR疑似: 软连字符拆行]` |
| `herowsm` | `heroism` | Tagged — likely missing `i` |
| `fertilize itand` | `fertilize it and` | Tagged — missing space, may be deliberate run-on in source |
| `how \|` | `how I` | Tagged — the `|` is a column-separator artifact; "I" almost certainly correct |
| `1 am` | `I am` | Tagged — `1` ↔ `I` common confusion |
| `littke` | `little` | Tagged — letter transposition |

**Rationale for minimal auto-correction**: per task boundary, the agent must not
"凭空补写原文" (fabricate missing source text). All corrections here are at the
character/space level only, in cases where the OCR is clearly broken rather than
semantically uncertain. Every such correction is tagged so a reviewer can revert
without consulting the PDF.

## 5. Hard-Stop Triggers — None Reached

The following conditions would force a hard stop; none applied:

- [ ] PDF encrypted or unreadable — **No**, opens fine
- [ ] Large-block omission after OCR — **No**, all 4 pages fully recognized
- [ ] Multiple unrecognizable pages — **No**
- [ ] TOC / body boundary unclear — **No**, page-164 header and book-page footers
  make the start point unambiguous
- [ ] Cannot confirm this is one complete document — **Yes** — this is two essays
  from a 1986 collection; the second ("Heroes") is intentionally truncated at
  the end of the scan (PDF cut at p.171). The first essay ("The Carrier Bag
  Theory of Fiction") is **complete in its entirety** (pp. 164–170).
  The Hero essay is included in `source.md` up to the page boundary of the scan
  and labeled as a partial opening for transparency.

## 6. Content Boundaries in the Source File

`source.md` contains:

1. The three **Notes** (footnotes 1–3) that head the section in the book
2. **The Carrier Bag Theory of Fiction** — full text, opening through closing
   ("…room in the bag of stars")
3. The opening of **Heroes** — dedicated page + first paragraph through
   "We left no footprints, even" (continues beyond the scanned excerpt)

These are tagged with `<!-- page: N -->` markers corresponding to the book pages
in the source (164 through 171). Where the original page number appears in the
header (e.g. `164 URSULA K. LE GUIN`) or footer (e.g. `THE CARRIER BAG THEORY OF
FICTION 165`), it is preserved.

## 7. Inputs to Downstream Steps

- `source.md` — full OCR text, page-tagged, with `[OCR疑似: ...]` markers
- Word count: source 2,900 English words (after light cleanup); translation
  4,940 CJK characters (full, in `translation.zh-CN.md`)
- All footnoted citations (Susan Griffin 1978, Linda Hogan 1984, Elaine
  Showalter 1985, Fisher 1975) preserved as-is for the translator
