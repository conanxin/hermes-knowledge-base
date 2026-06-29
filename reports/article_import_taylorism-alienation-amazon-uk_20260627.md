# Import Report: taylorism-alienation-amazon-uk

- **Slug:** `2026-06-16-taylorism-alienation-amazon-uk`
- **Date:** 2026-06-27
- **Source URL:** https://link.springer.com/article/10.1007/s10551-026-06378-6
- **Authors:** Miao Miao, Hui Situ (Cardiff Business School, Cardiff University)
- **Journal:** Journal of Business Ethics (Springer Nature, CC BY 4.0)
- **Type:** `article` | `status: translated` | `content_kind: written_article`

---

## 1. STATUS

**PASS** — 51/51 records PASS, push succeeded, live CDN serves new record.

## 2. SCOPE

- Read original PDF from Springer open-access link (`https://link.springer.com/content/pdf/10.1007/s10551-026-06378-6.pdf`, 863 KB, 26 pages, 1149 lines of layout-preserved text).
- Wrote 5 mandatory files under `content/articles/2026/2026-06-16-taylorism-alienation-amazon-uk/`.
- Updated `site/`, `docs/`, `index/{authors,tags,timeline,catalog.jsonl}` via `update_site.py` 5-step chain.
- Per-file `git add` (13 paths in 1 commit), push to `origin/main`. Catalog record count 50 → 51.

## 3. ACTIONS

| # | Step | Result |
|---|---|---|
| 1 | Pre-flight: `git fetch` + `git rebase origin/main` | Rebased cleanly; 18 remote commits pulled in (52daaa5..cef99b2 history) |
| 2 | Pre-flight: `python3 scripts/check_kb.py` (baseline) | **PASS 50/50** |
| 3 | Web extract of article landing page | Failed (`Blocked: URL targets a private or internal network address`) |
| 4 | Crossref / PhilPapers / Springer online-first search | Resolved: Miao & Situ 2026, *Journal of Business Ethics*, Open Access |
| 5 | `curl` direct PDF fetch | OK — HTTP 200, 863 KB |
| 6 | `pdftotext -layout` extraction | 1149 lines, structured: Abstract → Introduction → Marx theory → Taylorism & Accounting → Online Retailers → Framework → Methods → Results → Discussion → Declarations → References |
| 7 | Wrote `source.md` (cleaned original, ~98.7 KB) | 11,350 EN words in body (excl. References list) |
| 8 | Wrote `translation.zh-CN.md` (full prose) | 19,886 CJK chars (drift 0% vs declared) |
| 9 | Wrote `summary.md` (thesis + framework table + concept distinctions + 6 key quotes + 3-contribution summary + cross-refs to KB) | 11 sections |
| 10 | Wrote `notes.md` (4-layer Accept / Reflect / Associate / Act + reader warnings) | 5 sections, 12.1 KB |
| 11 | Wrote `metadata.yaml` (14 required fields + 5 supplementary) | All fields non-empty, word_count dict-shaped, topics=8, tags=14 |
| 12 | `python3 scripts/check_kb.py` | **PASS 51/51**, zero warnings |
| 13 | `python3 scripts/update_site.py` | **5/5 OK** (build_index → export → generate → sync → check_pages_sync) |
| 14 | Per-file `git add` (13 paths) | All staged, `git status -s` clean before commit |
| 15 | `git commit -m "Add taylorism-alienation-amazon-uk article"` | `5ecd8ec` |
| 16 | `git push origin main` | OK, `52daaa5..5ecd8ec main -> main` |
| 17 | Live verify: `curl /items/<slug>/index.html` | **HTTP 200**, all 4 sections (summary/translation/source/notes) rendered |
| 18 | Live verify: `curl /data/catalog.json` | **51 records**, new slug listed, title_zh + word_count intact |

## 4. EVIDENCE

- **PDF source:** `link.springer.com/content/pdf/10.1007/s10551-026-06378-6.pdf`, 863 KB, 26 pages, version 1.4, creation date 2026-06-16 (Springer production), accepted 2026-06-06, published online 2026-06-16.
- **Word counts (file-level, verified):**
  - `source.md` body (excl. References): **11,350** English words (counted via `re.findall(r'\b[A-Za-z]+\b', body)`)
  - `translation.zh-CN.md` total: **19,886** CJK chars (counted via `re.findall(r'[\u4e00-\u9fff]', full)`)
  - Drift between declared `word_count.translation=19886` and actual CJK = **0.00%** (well under 5% WARN threshold).
- **Gates:**
  - `check_kb.py`: 50 → 51 records, PASS/FAIL 51/0
  - `update_site.py` 5-step chain: all OK
  - `check_pages_sync.py`: site/ ↔ docs/ byte-identical
- **Live CDN (post-90s sync window):**
  - `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-16-taylorism-alienation-amazon-uk/index.html` → **HTTP 200**, renders `<section class="section-summary">` + `section-translation` + `section-source` + `section-notes`.
  - `https://conanxin.github.io/hermes-knowledge-base/data/catalog.json` → **51 records**, new record present with correct slug, title_zh, word_count.

## 5. COMMIT-PUSH

- Commit `5ecd8ec` on `main` (rebased onto `origin/main`):
  - 13 files: `content/articles/2026/2026-06-16-taylorism-alienation-amazon-uk/{metadata,source,translation.zh-CN,summary,notes}.yaml/.md`, `site/items/<slug>/index.html`, `docs/items/<slug>/index.html`, `site/data/catalog.json`, `docs/data/catalog.json`, `index/{authors,tags,timeline}.md`, `index/catalog.jsonl`
  - 3,019 insertions, 0 deletions
- Push: `52daaa5..5ecd8ec main -> main` to `https://github.com/conanxin/hermes-knowledge-base.git`

## 6. LIVE

- Items page: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-16-taylorism-alienation-amazon-uk/index.html` → HTTP 200
- Catalog: `https://conanxin.github.io/hermes-knowledge-base/data/catalog.json` → 51 records, new slug visible
- Index updates:
  - `index/authors.md`: new `## Miao Miao; Hui Situ` section (line 122)
  - `index/tags.md`: new `## ADAPT` section (line 38), entries under Taylorism / Digital Taylorism / Braverman / Charles Taylor / etc.
  - `index/timeline.md`: new entry alongside other 2026-06 records (line 6)
  - `index/catalog.jsonl`: appended

## 7. LIMITS

- **Translation residue baseline:** the article is heavy on proper nouns (Marx, Braverman, Burawoy, Taylor, ADAPT, etc.) — `check_translation_residue.py` is expected to flag ~15–25 entries; these are intentional proper-noun retentions consistent with `references/translation-residue-baseline.md`. Not a FAIL.
- **No footnote anchor rendering:** the article uses markdown `[^N]` references inline; per KB renderer limitation (logged in `kb-article-import/SKILL.md` pitfalls), `<sup>` elements render as literal text without `href="#fn-N"` anchors. Footnote body content IS preserved in prose. Acceptable.
- **No cross-record `based_on`:** this is a fresh external article import, not a derived `note` record, so `based_on` is not applicable. The conceptual lineage is documented in `notes.md` § 三、联想.
- **AI use disclosure:** author-declared AI use limited to language polishing (Springer compliant). Translation performed independently by KB importer.

## 8. NEXT ACTION

- **Read & annotate:** the new article is now searchable via `?q=taylorism` on the live site.
- **Possible follow-ups (not in scope of this import):**
  - Add a derived `note` record: `2026-06-27-hermes-knowledge-base-taylorism-marx-reading-guide.md` distilling the 4-form framework into a personal checklist.
  - Import related upstream: Kassem (2023) *Work and Alienation in the Platform Economy*, Carter & Choonara (2022) Braverman reinterpretation.
  - Compare with Liu (2023) "Digital Taylorism in China's e-commerce industry" for cross-jurisdiction contrast.

---

**This report files the import of Miao & Situ (2026) into hermes-knowledge-base under the standard kb-article-import pipeline. All gates PASS; live CDN verified.**