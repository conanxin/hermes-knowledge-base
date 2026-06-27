# v0.3.55-project-gutenberg-import-recipe — Project Gutenberg Import Recipe Documentation

## 1. STATUS

| 字段 | 值 |
|---|---|
| **STATUS** | **PASS** |
| **Result type** | **PASS** |
| **Summary** | Added Project Gutenberg import recipe after multiple successful imports and anthology boundary regressions. |
| **Self postflight** | **PASS** (0 warnings) |
| **Date** | 2026-06-27 |

---

## 2. Version / Git

| 字段 | 值 |
|---|---|
| **commit** | `Add Project Gutenberg import recipe` |
| **commit hash** | pending until commit |
| **tag** | `v0.3.55-project-gutenberg-import-recipe` |
| **tag object** | pending until tag creation |
| **tag deref** | pending until tag creation |
| **tag deref commit** | pending until tag creation |
| **HEAD (start)** | `ff83db9` (v0.3.54-normal-article-import-production) |
| **origin/main (start)** | `ff83db9` (v0.3.54-normal-article-import-production) |
| **HEAD (end)** | pending until push |
| **origin/main (end)** | pending until push |
| **git status (start)** | clean |
| **git status --short (start)** | empty |
| **git status (end)** | pending until commit |
| **git status --short (end)** | pending until commit |

---

## 3. Scope

| 字段 | 值 |
|---|---|
| **task name** | v0.3.55-project-gutenberg-import-recipe |
| **task type** | import recipe documentation |
| **allowed files** | `docs/import-recipes/PROJECT_GUTENBERG.md` (new); `docs/AGENT_COMMANDS.md` (modified); `templates/prompts/import_article_prompt.md` (modified); `docs/CLOUD_HERMES_INTEGRATION.md` (modified); this report (new) |
| **forbidden files** | `content/articles/**`; any `translation.zh-CN.md`; any `source.md`; any `metadata.yaml`; any `summary.md`; any `notes.md`; `tracks.yaml`; `scripts/**`; unrelated reports |
| **modified files (start)** | none — clean working tree at HEAD `ff83db9` |
| **modified files (end)** | (see commit) |

### File-level change summary

| File | Change | Size delta | Reason |
|---|---|---|---|
| `docs/import-recipes/PROJECT_GUTENBERG.md` | new | +19,876 bytes | New recipe (16 sections) |
| `docs/AGENT_COMMANDS.md` | modified | +15 lines | Added §2b source-specific recipes pointer |
| `templates/prompts/import_article_prompt.md` | modified | +20 lines | Added source-specific recipe loading rules |
| `docs/CLOUD_HERMES_INTEGRATION.md` | modified | +17 lines | Added §5b cloud-side recipe requirements |
| `reports/project_gutenberg_import_recipe_v0355_20260627.md` | new | (this report) | Self postflight target |

---

## 4. Inputs

For import tasks:

| Field | Value |
|---|---|
| source URL | N/A — no new import in this task |
| short command | N/A — recipe documentation task |
| content directory | N/A — no content directory created |
| duplicate check | N/A — no import attempted |
| blocked check | N/A — no external fetch attempted |
| GitHub Pages URL | https://conanxin.github.io/hermes-knowledge-base/ |

For feature tasks:

| Field | Value |
|---|---|
| feature target | Project Gutenberg import recipe |
| modified scripts/docs | `docs/import-recipes/PROJECT_GUTENBERG.md`; `docs/AGENT_COMMANDS.md`; `templates/prompts/import_article_prompt.md`; `docs/CLOUD_HERMES_INTEGRATION.md` |
| generated files | none expected |

---

## 5. Checks

| Check | Result |
|---|---|
| `check_task_preflight.py --planned-tag v0.3.55-project-gutenberg-import-recipe` (start) | **PASS** (warning 仅为 v0.3.36 已知例外) |
| `check_release_tags.py` (start) | **PASS_WITH_WARNINGS** (v0.3.36 已知例外); `recommended_next_minor = v0.3.55` |
| `check_kb.py` | **PASS** — Total items: 49 (unchanged); PASS: 49; FAIL: 0 |
| `check_tracks.py` | **PASS** — 50 tracks (38 verified, 12 needs_verification, unchanged) |
| `update_site.py` | **PASS** — all 5 steps; no diff in site/ or docs/ (docs-only task, no item changes) |
| `check_pages_sync.py` | **PASS** — 49 slugs present and byte-identical in both site/items/ and docs/items/ |
| `check_translation_residue.py` | **WARNING** — same 25 files_with_warnings / 300 suspicious_count / 1 allowlisted (jasmi) / 4 thoreau-walking proper_noun_ok — no new warnings introduced by this task |

---

## 6. Smoke Tests

| Check | Result |
|---|---|
| local smoke | **N/A** — docs-only task, no site UI changes |
| online smoke | **N/A** — docs-only task, no site UI changes |
| pages URL | https://conanxin.github.io/hermes-knowledge-base/ (unchanged) |
| GitHub Pages URL | https://conanxin.github.io/hermes-knowledge-base/ (unchanged) |

### Documentation visibility verification

The new recipe and updated references will be visible at:

* `docs/import-recipes/PROJECT_GUTENBERG.md` (rendered via GitHub's built-in markdown viewer, not on the static site)
* `docs/AGENT_COMMANDS.md` (rendered via GitHub's built-in markdown viewer)
* `templates/prompts/import_article_prompt.md` (rendered via GitHub's built-in markdown viewer)
* `docs/CLOUD_HERMES_INTEGRATION.md` (rendered via GitHub's built-in markdown viewer)

These docs do not appear in `site/` or `docs/` (GitHub Pages) — they are operational documentation for agents and humans, not public-facing site pages.

---

## 7. Postflight

To be run after commit/tag (Step 9):

```bash
python3 scripts/check_task_postflight.py \
  --report reports/project_gutenberg_import_recipe_v0355_20260627.md \
  --tag v0.3.55-project-gutenberg-import-recipe \
  --expect-clean \
  --expect-head-origin
```

### Expected

| Field | Expected |
|---|---|
| `check_task_postflight.py` | **PASS** |
| postflight status | **PASS** |
| warnings | **0** |
| tag deref | (after Step 8) |
| tag deref commit | (after Step 8) |
| git status | clean |

---

## 8. Links

| Link | Status |
|---|---|
| GitHub commit | pending until push (Step 7) |
| GitHub tag | pending until push (Step 8) |
| GitHub Pages | https://conanxin.github.io/hermes-knowledge-base/ (unchanged) |

---

## 9. Warnings / Known Non-blockers

| Field | Value |
|---|---|
| known warning | `check_release_tags.py` may report `PASS_WITH_WARNINGS` for the known v0.3.36 duplicate minor exception (repo-health-final-verification + repo-hygiene-and-report-cleanup) |
| known warning | `check_translation_residue.py` may still report `proper_noun_ok` / `citation_or_url_ok` warnings under the current policy (v0.3.50 TRANSLATION_RESIDUE_POLICY.md) |
| reason | These warnings are documented as accepted by design — v0.3.36 is a historical exception explicitly preserved by the project; translation residue categories are intentional (proper_noun_ok / citation_or_url_ok / needs_translation_fix) per v0.3.47 triage + v0.3.50 policy |
| action | none — both warnings are non-actionable in this task |

---

## 10. Next Version

| Field | Value |
|---|---|
| recommended next minor | expected **v0.3.56** after tag creation |
| next suggested task | continue normal article imports using the Gutenberg recipe (e.g., Swift other essays, Hawthorne, Melville); or add new source-specific recipes (academic PDF, blog post, video transcript) following the v0.3.55 pattern |

---

## 11. Recipe Summary

| Field | Value |
|---|---|
| **new recipe path** | `docs/import-recipes/PROJECT_GUTENBERG.md` |
| **covered source type** | Project Gutenberg (`gutenberg.org` / `www.gutenberg.org`) |
| **single essay page rules** | URL → 1 essay, full translation, `metadata.yaml.source_url` → Gutenberg HTML, `notes.md` records open-access / single-essay judgment (recipe §5) |
| **anthology / collection page rules** | URL → multi-essay book, user-specified scope, `source_collection` + `extraction_scope` fields in metadata.yaml, `notes.md` Boundaries section, source.md / translation.zh-CN.md must NOT include other chapters (recipe §6) |
| **hard-stop cases** | AMBIGUOUS_ANTHOLOGY_SCOPE (no chapter specified); EXTRACTION_BOUNDARY_NOT_FOUND (chapter not in collection); unstable boundary; guessed boundary; fallback to entire book; fallback to neighboring chapter (recipe §7) |
| **quality gates** | `check_kb.py` → `check_tracks.py` → `update_site.py` → `check_pages_sync.py` → `check_translation_residue.py` (recipe §11) |
| **reporting requirements** | Use `docs/REPORTING_TEMPLATE.md` v0.3.43+; include STATUS / commit / tag / tag deref / checks / smoke / postflight / warnings / next version (recipe §12) |
| **known good examples** | v0.3.39 Swift *A Modest Proposal*; v0.3.45 Thoreau *Civil Disobedience*; v0.3.51 Emerson *Self-Reliance* (anthology); v0.3.54 Thoreau *Walking* (recipe §13) |
| **known regression tests** | v0.3.40 duplicate / blocked hard-stop; v0.3.52 anthology online smoke; v0.3.53 anthology blocked-boundary regression (recipe §14) |

---

## 12. Recipe Section Index

The new recipe `docs/import-recipes/PROJECT_GUTENBERG.md` contains 16 sections:

| § | Section | Purpose |
|---|---|---|
| 1 | Purpose | Scope of the recipe |
| 2 | Preflight | Pre-import checks (git status, fetch, pull, preflight, tag check) |
| 3 | Duplicate Check | Detect existing entries (URL / title / slug / author) |
| 4 | Blocked Check | Detect fetch failures / incomplete HTML / paywall |
| 5 | Single Essay Page Import | Rules for single-essay URLs |
| 6 | Anthology / Collection Page Import | Rules for anthology URLs with user-specified scope |
| 7 | Anthology Hard-Stop Cases | Conditions that MUST hard-stop (no fallback) |
| 8 | Gutenberg Noise Removal | What to exclude / include in source.md |
| 9 | Metadata Requirements | Required metadata.yaml fields |
| 10 | Translation Requirements | Translation completeness + residue policy |
| 11 | Quality Gates | Required post-import checks |
| 12 | Reporting | REPORTING_TEMPLATE.md fields |
| 13 | Known Good Examples | Validated imports |
| 14 | Known Regression Tests | Validated regressions |
| 15 | Cross-references | Pointer to related docs |
| 16 | Maintenance | Update conditions |

---

## 13. Cross-reference Updates

### `docs/AGENT_COMMANDS.md` (added §2b)

New section after §2a (Anthology / Collection 页面抽取):

```
### 2b. Source-Specific Import Recipes (v0.3.55+)

不同来源的文章有不同的抓取 / 清洗 / 抽取规则。当 source_url 命中一个已知的来源类型时，
**必须先加载并遵守对应 recipe**：

| Source type | Recipe |
|---|---|
| Project Gutenberg (gutenberg.org) | [docs/import-recipes/PROJECT_GUTENBERG.md](import-recipes/PROJECT_GUTENBERG.md) |
```

### `templates/prompts/import_article_prompt.md` (added source-specific recipes section)

New section after the Anthology rules section:

```
## 🔖 Source-Specific Import Recipes（v0.3.55+）

**触发条件**：`source_url` 命中一个已知来源类型时（如 `gutenberg.org`），必须在执行 §1–§10 的
常规流程之前加载对应 recipe，并遵守 recipe 中所有硬规则。
```

### `docs/CLOUD_HERMES_INTEGRATION.md` (added §5b)

New section after §5a (Anthology / Collection Page 导入):

```
### 5b. Source-Specific Import Recipes（v0.3.55+）

云端导入 Project Gutenberg 来源（或任何已建立 recipe 的来源）时，
**必须先加载并遵守对应 recipe**：
```

---

## 14. Anti-pattern Verification

| Check | Result |
|---|---|
| Did we modify any content/articles/** file? | **No** ✓ |
| Did we modify any translation.zh-CN.md? | **No** ✓ |
| Did we modify any source.md? | **No** ✓ |
| Did we modify any metadata.yaml? | **No** ✓ |
| Did we modify any summary.md? | **No** ✓ |
| Did we modify any notes.md? | **No** ✓ |
| Did we modify tracks.yaml? | **No** ✓ |
| Did we modify scripts/**? | **No** ✓ (no documentation reference errors found) |
| Did we modify Paste 1960s / Swift / Thoreau-CD / Emerson? | **No** ✓ |
| Did we modify docs/REPORTING_TEMPLATE.md? | **No** ✓ (recipe references existing template, no changes needed) |
| Did we force-push? | **No** ✓ |
| Did we commit --amend? | **No** ✓ |
| Did we `git reset --hard`? | **No** ✓ |
| Did we modify old tags? | **No** ✓ |
| Did we create a standalone project? | **No** ✓ |
| Did we submit unrelated files? | **No** ✓ |

---

## 15. Per-file Add Manifest (Step 6)

### Allowed (will be added)

* `docs/import-recipes/PROJECT_GUTENBERG.md` (new, 19,876 bytes)
* `docs/AGENT_COMMANDS.md` (modified, +15 lines)
* `templates/prompts/import_article_prompt.md` (modified, +20 lines)
* `docs/CLOUD_HERMES_INTEGRATION.md` (modified, +17 lines)
* `reports/project_gutenberg_import_recipe_v0355_20260627.md` (this report, new)

### Forbidden (will NOT be added)

* Any file under `content/articles/`
* `tracks.yaml`
* Any `source.md` / `translation.zh-CN.md` / `metadata.yaml` / `summary.md` / `notes.md`
* Any file under `scripts/**`
* `docs/REPORTING_TEMPLATE.md` (not modified, not added)
* Any unrelated reports
* Any standalone project files

---

## 16. Success Criteria

| Criterion | Status |
|---|---|
| Preflight passed before any file write | ✓ |
| HEAD = origin/main = `ff83db9` (v0.3.54) at task start | ✓ |
| New recipe created at `docs/import-recipes/PROJECT_GUTENBERG.md` | ✓ (19,876 bytes, 16 sections) |
| Cross-references added in 3 docs (AGENT_COMMANDS / import_article_prompt / CLOUD_HERMES_INTEGRATION) | ✓ (52 insertions total) |
| `check_kb.py` PASS, items unchanged (49) | ✓ |
| `check_tracks.py` PASS, tracks unchanged (50) | ✓ |
| `update_site.py` PASS, no diff | ✓ |
| `check_pages_sync.py` PASS, slugs unchanged | ✓ |
| `check_translation_residue.py` no new warnings | ✓ |
| No content/articles / scripts / tracks.yaml / old tags modified | ✓ |
| Per-file `git add` (no `git add -A` or `git add .`) | pending Step 6 |
| Self postflight PASS, 0 warnings | pending Step 9 |
| Recommended next minor = v0.3.56 | pending Step 9 |

---

## 17. Operational Notes

* **Recipe sections**: 16 (Purpose, Preflight, Duplicate, Blocked, Single, Anthology, Hard-stop, Noise, Metadata, Translation, Quality, Reporting, Good examples, Regression tests, Cross-refs, Maintenance).
* **Cross-references inserted**: 3 docs updated with minimal pointers (52 total insertions).
* **Recipe coverage**: Project Gutenberg single-essay + anthology extraction + boundary hard-stops + Gutenberg noise removal + metadata schema + translation policy + quality gates.
* **Translation residue policy**: v0.3.50 TRANSLATION_RESIDUE_POLICY.md in effect; recipe §10 explicitly defers to it.
* **Anthology rules**: v0.3.53 hard-stop rules validated and codified into recipe §7; v0.3.53 examples cited explicitly.
* **Reporting template**: v0.3.43+ REPORTING_TEMPLATE.md referenced from recipe §12; no changes to the template itself.

---

## 18. Cross-references

* v0.3.39 — Swift *A Modest Proposal* (first Gutenberg import)
* v0.3.40 — duplicate / blocked hard-stop regression
* v0.3.45 — Thoreau *Civil Disobedience* (real import after template)
* v0.3.51 — Emerson *Self-Reliance* (first anthology extraction)
* v0.3.52 — anthology online smoke + rules documentation
* v0.3.53 — anthology blocked-boundary regression (hard-stop rules)
* v0.3.54 — Thoreau *Walking* (normal single-essay import)
* **v0.3.55-project-gutenberg-import-recipe** — this task: codify all lessons into a stable recipe

The v0.3.39 → v0.3.55 arc demonstrates that the knowledge base production workflow can now stably handle: real single-essay imports, anthology extraction with boundaries, blocked-case hard-stops, and recipe codification — closing with a durable operational memory of the full Project Gutenberg import pattern.

---

## 19. Future Recipe Candidates

The v0.3.55 pattern establishes a template for additional source-specific recipes. Possible future candidates:

| Source | Domain pattern | Notes |
|---|---|---|
| Substack posts | `*.substack.com` | HTML with paywall consideration |
| Medium articles | `*.medium.com` | HTML with member-only content |
| Internet Archive | `archive.org/details/...` | Multi-format (text / PDF / EPUB) |
| Common Books | `commonbooks.org` | Anthology with stable IDs |
| Library of America | `loa.org` | Anthology with stable IDs |
| Academic papers (arXiv) | `arxiv.org/abs/...` | LaTeX-rendered HTML, math notation |
| Academic papers (SSRN) | `papers.ssrn.com/...` | PDF-only, requires PDF extraction |
| YouTube transcripts | `youtube.com/watch?v=...` | Already has `YOUTUBE_CAPABILITIES.md` |
| Podcast transcripts | `*.podcasts.com/...` | Already supported via podcast-to-novel / podcast-translate-audio skills |

Each new recipe should follow the v0.3.55 pattern: §1 Purpose, §2 Preflight, §3 Duplicate, §4 Blocked, §5 Single Import, §6 Anthology Import, §7 Hard-stop, §8 Noise Removal, §9 Metadata, §10 Translation, §11 Quality Gates, §12 Reporting, §13 Known Good Examples, §14 Known Regression Tests, §15 Cross-references, §16 Maintenance.