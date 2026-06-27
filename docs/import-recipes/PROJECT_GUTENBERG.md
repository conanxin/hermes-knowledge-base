# Project Gutenberg Import Recipe

> **Status**: Active since v0.3.55
> **Audience**: AI agents and human reviewers importing articles from Project Gutenberg
> **Related scripts**: `scripts/check_kb.py`, `scripts/check_pages_sync.py`, `scripts/check_translation_residue.py`, `scripts/update_site.py`
> **Related docs**: `docs/AGENT_COMMANDS.md`, `docs/CLOUD_HERMES_INTEGRATION.md`, `docs/REPORTING_TEMPLATE.md`, `docs/TRANSLATION_RESIDUE_POLICY.md`, `templates/prompts/import_article_prompt.md`

---

## 1. Purpose

This document codifies the **Project Gutenberg import recipe** for the hermes-knowledge-base, derived from successful imports of Swift, Thoreau (×2), and Emerson across v0.3.39–v0.3.54.

It covers:

* **Single essay page imports** — URLs that point directly to one essay.
* **Anthology / collection / book page imports** — URLs that point to a multi-essay or multi-chapter collection, with user-specified extraction scope.
* **Duplicate detection** — preventing accidental re-imports.
* **Blocked detection** — preventing half-finished imports when fetch fails or HTML is incomplete.
* **Extraction boundary rules** — anthology extraction with hard-stop fallback.
* **Gutenberg noise removal** — header, footer, license boilerplate, transcriber notes.
* **Translation residue policy** — applying `docs/TRANSLATION_RESIDUE_POLICY.md`.

---

## 2. Preflight (run before every Gutenberg import)

```bash
cd ~/hermes-knowledge-base
git status --short                            # must be clean
git fetch origin                              # proxy: socks5://127.0.0.1:7898
git pull --ff-only origin main
git rev-parse --short HEAD                    # must equal origin/main
git rev-parse --short origin/main
python3 scripts/check_release_tags.py         # recommended_next_minor = next available
python3 scripts/check_task_preflight.py --planned-tag <planned-tag>
git tag --list '<planned-tag>'                # must not exist locally
git -c http.proxy=socks5://127.0.0.1:7898 ls-remote --tags origin '<planned-tag>*'  # must not exist remotely
```

### Hard-stop conditions

* `git status` is dirty — stop, do not proceed.
* `HEAD != origin/main` — stop, do not proceed.
* `planned-tag` already exists locally or remotely — stop, do not reuse minor.
* `check_task_preflight.py` exits non-PASS / non-PASS_WITH_WARNINGS with non-known warnings — stop.
* `check_release_tags.py` `recommended_next_minor` is not the planned minor — stop, do not skip.

### Why this matters

* **Dirty tree** = an unfinished state from a previous task; merging new content risks loss.
* **Tag reuse** = violates v0.3.37+ rule against reusing minor numbers (v0.3.36 is the documented exception).
* **HEAD ≠ origin/main** = unmerged or unpushed commits that may be lost on push.

---

## 3. Duplicate Check

Before any import, check the catalog and content directories for an existing entry.

### Check dimensions

| Dimension | Where to check | Example |
|---|---|---|
| `source_url` | `index/catalog.jsonl`, `content/articles/**/metadata.yaml` | `https://www.gutenberg.org/files/1022/1022-h/1022-h.htm` |
| `title` (English) | `index/catalog.jsonl`, `index/timeline.md`, `metadata.yaml` | `Walking`, `On the Duty of Civil Disobedience` |
| `title_zh` (Chinese) | `index/catalog.jsonl`, `index/timeline.md`, `metadata.yaml` | `步行`, `论公民不服从` |
| `author` | `index/authors.md`, `index/catalog.jsonl`, `metadata.yaml` | `Henry David Thoreau` |
| `slug` pattern | `index/catalog.jsonl`, `content/articles/**/` | `thoreau-walking`, `thoreau-civil-disobedience` |
| `catalog record` | `index/catalog.jsonl` | Full record match |

### Hard-stop if duplicate

* Source URL already imported.
* English title already imported.
* Chinese title already imported.
* Slug already exists.

**Do not**:

* Overwrite the old content directory.
* Create a duplicate entry.
* Re-import an anthology sub-extraction when the same range is already present.
* "Update" an existing entry via re-import — produce a new minor version instead.

### Known existing entries (do not re-import)

| Author | Title | Title (zh) | Slug | Version |
|---|---|---|---|---|
| Jonathan Swift | A Modest Proposal | 一个温和的建议 | `swift-a-modest-proposal` | v0.3.39 |
| Henry David Thoreau | On the Duty of Civil Disobedience | 论公民不服从 | `2026-06-27-thoreau-civil-disobedience` | v0.3.45 |
| Ralph Waldo Emerson | Self-Reliance (anthology extraction from *Essays, First Series*) | 论自立 | `2026-06-27-emerson-self-reliance` | v0.3.51 |
| Henry David Thoreau | Walking | 步行 | `2026-06-27-thoreau-walking` | v0.3.54 |

---

## 4. Blocked Check

Project Gutenberg is generally open access, but every import must still confirm the page is **fetchable, complete, and importable**.

### Confirm

* HTTP 200.
* Body is non-empty.
* Content is the actual essay, not a directory listing or error page.
* HTML is complete (no truncation, no character-encoding artifacts).
* Single-essay pages have exactly **one** `<h1>` containing the title.
* Anthology pages have clear `<h2>` / `<h3>` chapter markers.

### Hard-stop if blocked / incomplete

* HTTP non-200 (redirect, 404, 403, 5xx).
* Empty body.
* Directory page (e.g., `/files/1022/` instead of `/files/1022/1022-h/1022-h.htm`).
* Truncated HTML (missing closing tags, half a paragraph, character corruption).
* Single-essay page has zero or more-than-one `<h1>`.
* Anthology page lacks stable chapter markers (`<h2 id="...">` with stable IDs).
* ACL / paywall / login wall — although rare on Gutenberg, possible on derivative sites.

### On hard-stop

* **Do not create** a content directory.
* **Do not write** a half-finished `source.md` or `translation.zh-CN.md`.
* **Do not run** `update_site.py`.
* **Generate** a `BLOCKED` report describing the failure mode.
* **Do not proceed** to commit / tag.

---

## 5. Single Essay Page Import

### When applicable

* URL directly resolves to a single essay.
* Example: `https://www.gutenberg.org/files/1022/1022-h/1022-h.htm` → Thoreau, *Walking*.

### Rules

* `source.md` preserves the body structure of the essay.
* `source.md` does **not** include Gutenberg navigation, license footer, transcriber notes, or related-book links.
* `metadata.yaml.source_url` points to the Gutenberg HTML page.
* `metadata.yaml.source_site` = `"Project Gutenberg"`.
* `metadata.yaml.type` = `"essay"`.
* `metadata.yaml.published_date` set to the original publication date (not the Gutenberg file date).
* `notes.md` records the open-access / single-essay judgment.
* `translation.zh-CN.md` is a complete translation.

### Example: v0.3.54 Thoreau Walking

* `source.md`: 67,231 chars (1 h1 + 1 h2 + 179 paragraphs + horizontal rule).
* `translation.zh-CN.md`: 19,659 Chinese characters across 8 sub-sections.
* `metadata.yaml`: `slug = "2026-06-27-thoreau-walking"`, `import_version = "v0.3.54-normal-article-import-production"`.
* No `extraction_scope` / `source_collection` fields (single essay, not anthology extraction).

---

## 6. Anthology / Collection Page Import

### When applicable

* URL is a collection / anthology / book page with multiple essays or chapters.
* User has explicitly specified the chapter / essay / section to extract.
* Example: `https://www.gutenberg.org/files/2944/2944-h/2944-h.htm` → Emerson, *Essays, First Series*, with user specifying **II. SELF-RELIANCE**.

### Rules

* The collection URL **does not** mean importing the entire book.
* When the user specifies a single chapter / essay, **only that range** is extracted.
* `source.md` must **not** include text from other chapters.
* `translation.zh-CN.md` must **not** include translations from other chapters.
* `metadata.yaml` must include both:
  * `source_collection`: the collection / book title (e.g., `"Essays, First Series"`).
  * `extraction_scope`: the user-specified scope (e.g., `"II. SELF-RELIANCE"`).
* `metadata.yaml` may also include:
  * `extraction_start`: the HTML marker for the start (e.g., `"<h2 id=\"link2H_4_0002\">II. SELF-RELIANCE</h2>" at HTML position 52118`).
  * `extraction_end`: the HTML marker for the end (e.g., `"Just before <h2 id=\"link2H_4_0003\">III. COMPENSATION</h2> at HTML position 109195"`).
  * `anthology_boundary_check`: explicit pass/fail of the boundary check.
  * `excluded_sections`: list of sections explicitly excluded from the import.
* `notes.md` must include a **Boundaries** section recording the start / end HTML positions and the excluded sections.

### Example: v0.3.51 Emerson Self-Reliance

* Source URL: `https://www.gutenberg.org/files/2944/2944-h/2944-h.htm` (*Essays, First Series* — 12 essays).
* User specified scope: **II. SELF-RELIANCE** (single essay).
* `source.md`: 55,635 chars, extracted from HTML position 52,118 to 109,195 (just before III. COMPENSATION).
* `metadata.yaml` includes:
  * `source_collection: "Essays, First Series"`
  * `extraction_scope: "II. SELF-RELIANCE"`
  * `extraction_start: "..."` and `extraction_end: "..."`
  * `anthology_boundary_check: PASS`
  * `excluded_sections: ["I. HISTORY", "III. COMPENSATION", "IV. SPIRITUAL LAWS", ..., "XII. ART"]`
* `notes.md` includes a **Boundaries** section documenting the start / end HTML positions.
* **11 other essays** explicitly excluded.

---

## 7. Anthology Hard-Stop Cases

The following situations **must hard-stop**, with no fallback to the full book or to a neighboring chapter.

### Hard-stop triggers

* User provides only the collection URL with **no specific chapter** specified.
  * Reason: ambiguous scope → risk of importing the entire book or wrong chapter.
  * Blocked reason: `AMBIGUOUS_ANTHOLOGY_SCOPE`.
* User specifies a chapter / section that **does not exist** in the collection.
  * Reason: nonexistent boundary → cannot extract reliably.
  * Blocked reason: `EXTRACTION_BOUNDARY_NOT_FOUND`.
* Start or end marker **cannot be stably located** (no `<h2 id="...">`, position drifts across fetches).
  * Reason: extraction would be fragile; future re-imports would silently drift.
* Boundary can only be **guessed** (e.g., nearest paragraph break, prose heuristics).
  * Reason: violates the "stable, reproducible extraction" principle.
* Would require **fallback to the entire book** because no chapter matches.
  * Reason: anthology URL ≠ import whole book.
* Would require **fallback to a neighboring chapter** because the target is missing.
  * Reason: violates the user-specified scope.

### Examples (v0.3.53)

| Case | Short command | Blocked reason |
|---|---|---|
| Ambiguous scope | "把这篇文章完整翻译并加入知识库： https://www.gutenberg.org/files/2944/2944-h/2944-h.htm" | `AMBIGUOUS_ANTHOLOGY_SCOPE` |
| Nonexistent boundary | "把这篇文章完整翻译并加入知识库： https://www.gutenberg.org/files/2944/2944-h/2944-h.htm — 限定范围：只导入 XIII. NONEXISTENT ESSAY FOR BOUNDARY REGRESSION" | `EXTRACTION_BOUNDARY_NOT_FOUND` |

### On hard-stop

* **Do not create** a content directory.
* **Do not write** a half-finished `source.md`.
* **Do not run** `update_site.py`.
* **Generate** a `BLOCKED` report describing the failure mode and the canonical fix (ask the user for clarification).
* **Do not proceed** to commit / tag.

---

## 8. Gutenberg Noise Removal

### Exclude from `source.md`

* Gutenberg navigation bars (top / bottom).
* Project Gutenberg boilerplate ("This eBook is for the use of anyone anywhere at no cost...").
* License footer (full START / END headers, transcriber's notes that are unrelated to the text).
* File encoding notes (UTF-8, ASCII, etc.) outside the body.
* "More books by this author" links.
* "Similar books" recommendations.
* Related book download links.
* Unrelated chapter text (for anthology extraction — see §6, §7).

### Retain in `source.md`

* Minimal source attribution (title + author line).
* `# Walking` / `## by Henry David Thoreau` style heading at the top.
* Horizontal rule between metadata and body.
* Chapter / section headings within the body.
* Inline `<i>` / `<em>` emphasis (convert to Markdown `*...*`).
* Inline `<b>` / `<strong>` emphasis (convert to Markdown `**...**`).
* HTML entities (`&mdash;` → `—`, `&ldquo;` → `"`, etc.) — convert to Unicode.

### Retain in `notes.md` only (not `source.md`)

* HTML byte positions for start / end markers (for anthology extraction reproducibility).
* Gutenberg eBook number (`#1022`, `#2944`, etc.).
* Copyright / public domain statement.
* Original publication date and venue (e.g., *The Atlantic Monthly*, June 1862).

---

## 9. Metadata Requirements

`metadata.yaml` for any Gutenberg import must include at least:

```yaml
title: "<English title>"
title_zh: "<Chinese title>"
author: "<Author full name>"
source_url: "<Gutenberg HTML URL>"
source_site: "Project Gutenberg"
type: "essay"  # or other documented type
language: "en"
translation_language: "zh-CN"
publication_year: "<year>"  # original publication, not Gutenberg file date
tags: ["...", "..."]
topics: ["...", "..."]
word_count:
  source: <int>
  translation: <int>
captured_date: "<YYYY-MM-DD>"  # date of import
status: "published"
summary: "<English summary>"
summary_zh: "<Chinese summary>"
import_date: "<YYYY-MM-DD>"
import_version: "<vX.Y.Z-task-name>"
kb_entry_id: "<YYYY-MM-DD-slug>"
slug: "<slug>"
```

### For anthology extraction, additionally include:

```yaml
source_collection: "<Collection / book title>"
extraction_scope: "<User-specified scope>"
extraction_start: "<HTML marker>"
extraction_end: "<HTML marker>"
anthology_boundary_check: "PASS"
excluded_sections: ["...", "..."]
```

### Word count

* `word_count.source`: whitespace-separated English word count of `source.md` body.
* `word_count.translation`: character count of `translation.zh-CN.md` body (Chinese does not separate by spaces, so character count is the standard).

---

## 10. Translation Requirements

### Mandatory

* **Complete translation** — no paragraph omitted.
* **Structure preserved** — headings, sections, paragraph breaks.
* **No whole-sentence English residue** in the body translation.
* **Quotes** — translated; if a famous line is preserved for recognition, use `中文（English）` format.

### Accepted by policy

* **Proper nouns** — author names, historical figures, place names, publication names may stay in English.
* **Citations** — short citation fragments are allowed when they reference canonical English titles.
* **URLs** — never translated; preserved as-is.
* **Emails** — preserved as-is (with explicit allowlist per `docs/TRANSLATION_RESIDUE_POLICY.md`).

### Apply

* `docs/TRANSLATION_RESIDUE_POLICY.md` — categorize all `check_translation_residue.py` warnings into one of: `proper_noun_ok`, `citation_or_url_ok`, `needs_translation_fix`, `script_false_positive`, `allowlisted_known_non_blocker`.
* **P0 / P1** — must fix before commit.
* **P2** — should fix in batch with next residue round.
* **proper_noun_ok / citation_or_url_ok** — no action needed; document if recurring.
* **script_false_positive** — fix the script rule, not the article.

---

## 11. Quality Gates

After every Gutenberg import, run all quality gates in order:

```bash
python3 scripts/check_kb.py              # integrity — items +1, PASS
python3 scripts/check_tracks.py          # tracks unchanged unless Paste 1960s touched
python3 scripts/update_site.py           # 5/5 steps; regenerates site/ and docs/
python3 scripts/check_pages_sync.py      # site/ ↔ docs/ byte-identical
python3 scripts/check_translation_residue.py  # WARNING acceptable per policy
```

### Required to commit

* `check_kb.py` PASS, items count +1.
* `update_site.py` PASS, all 5 steps.
* `check_pages_sync.py` PASS, slugs byte-identical.
* `check_translation_residue.py` either PASS or WARNING with no new `needs_translation_fix` entries introduced by this import.

### Smoke tests

* **Local smoke**: `python3 -m http.server 8765 -d site`, then `curl` homepage / detail / catalog. Detail page must:
  * Return HTTP 200.
  * Contain `<h1>` with the Chinese title.
  * Contain translation key phrases.
  * NOT contain music UI (`track-card`, `track-filter-bar`, `spotify`, `apple music`, `youtube embed`) for non-music imports.
* **Online smoke** (after push): `curl` GitHub Pages URL with the same checks.

---

## 12. Reporting

Every Gutenberg import must produce a `reports/<slug>_v<X.Y.Z>_<YYYYMMDD>.md` file using `docs/REPORTING_TEMPLATE.md`.

### Mandatory sections

* **STATUS**: PASS or BLOCKED.
* **Version / Git**: commit hash, tag name, tag object, tag deref, HEAD, origin/main, git status.
* **Scope**: allowed files (this import only) and forbidden files (none of: other articles, tracks.yaml, unrelated reports).
* **Inputs**: source URL, short command, content directory, duplicate check result, blocked check result, extraction scope (if anthology), GitHub Pages URL.
* **Checks**: preflight, release tags, kb, tracks, update_site, pages_sync, translation_residue — all with results.
* **Smoke tests**: local + online, with curl outputs.
* **Postflight**: run `check_task_postflight.py` after commit/tag.
* **Links**: GitHub commit URL, GitHub tag URL, GitHub Pages URL.
* **Warnings / Known non-blockers**: explicit list, with reason and action.
* **Next version**: `recommended_next_minor` from `check_release_tags.py`.

### Self postflight target

* `check_task_postflight.py` PASS.
* 0 warnings.
* Tag deref to commit.
* `git status --short` empty.

---

## 13. Known Good Examples

| Version | Entry | URL pattern | Type | Lessons |
|---|---|---|---|---|
| v0.3.39 | Swift — *A Modest Proposal* / 一个温和的建议 | gutenberg.org/files/... | single essay (template validation) | First import; established 5-file layout |
| v0.3.45 | Thoreau — *On the Duty of Civil Disobedience* / 论公民不服从 | gutenberg.org/files/71/71-h/71-h.htm | single essay (real import) | Template validated on a second source |
| v0.3.51 | Emerson — *Self-Reliance* / 论自立 | gutenberg.org/files/2944/2944-h/2944-h.htm | anthology extraction (12 essays → 1) | First anthology extraction; established `extraction_scope` field |
| v0.3.54 | Thoreau — *Walking* / 步行 | gutenberg.org/files/1022/1022-h/1022-h.htm | single essay (12,110 words) | Largest single-essay translation to date; full prose translation |

---

## 14. Known Regression Tests

| Version | Test | Outcome |
|---|---|---|
| v0.3.40 | duplicate / blocked hard-stop | Confirmed that pre-flight duplicate and blocked checks prevent accidental re-imports and half-finished imports |
| v0.3.52 | anthology online smoke | Verified that anthology-extracted entries render correctly on GitHub Pages with proper boundary markers |
| v0.3.53 | anthology blocked-boundary regression | Confirmed that ambiguous scope (no chapter specified) and nonexistent boundaries (chapter not in collection) both trigger hard-stop without creating half-finished content |

---

## 15. Cross-references

* `docs/AGENT_COMMANDS.md` — agent commands reference this recipe for Project Gutenberg imports.
* `templates/prompts/import_article_prompt.md` — agent prompt loads this recipe when source_url matches `gutenberg.org`.
* `docs/CLOUD_HERMES_INTEGRATION.md` — cloud Hermes integration paths reference this recipe for Project Gutenberg cloud imports.
* `docs/REPORTING_TEMPLATE.md` — report template referenced for §12.
* `docs/TRANSLATION_RESIDUE_POLICY.md` — translation residue policy referenced for §10.
* `docs/VERSIONING.md` — version conventions referenced for tag naming.

---

## 16. Maintenance

* Update this recipe when:
  * A new Gutenberg-specific edge case emerges.
  * A new anthology extraction pattern is validated.
  * A new regression test is added.
* Bump the recipe's `Status` line when superseded.
* Do not delete recipes — they are durable operational memory.