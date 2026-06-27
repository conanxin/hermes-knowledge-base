# v0.3.52-online-smoke-and-anthology-extraction-regression Report

**Date**: 2026-06-27
**Branch**: main
**Starting HEAD**: `0ca2ccd`
**Origin/main at start**: `0ca2ccd`
**Planned tag**: `v0.3.52-online-smoke-and-anthology-extraction-regression`
**Recommended next minor before task**: v0.3.52
**Git status at start**: clean

---

## 1. STATUS

* **STATUS**: PASS
* **Result type**: PASS
* **Summary**: Online smoke and anthology extraction regression after Emerson Self-Reliance import.

---

## 2. Version / Git

* **commit**: pending until commit
* **commit hash**: pending until commit
* **tag**: `v0.3.52-online-smoke-and-anthology-extraction-regression`
* **tag object**: pending until tag creation
* **tag deref**: pending until tag creation
* **tag deref commit**: pending until tag creation
* **HEAD**: `0ca2ccd`
* **origin/main**: `0ca2ccd`
* **git status**: clean at task start
* **git status –short**: clean at task start

---

## 3. Scope

* **task name**: v0.3.52-online-smoke-and-anthology-extraction-regression
* **task type**: online smoke + import workflow rule hardening
* **allowed files**:
    * templates/prompts/import_article_prompt.md
    * docs/AGENT_COMMANDS.md
    * docs/CLOUD_HERMES_INTEGRATION.md
    * docs/REPORTING_TEMPLATE.md
    * generated index/site data files, only if update_site.py produces justified diff (none this round)
    * reports/online_smoke_and_anthology_extraction_regression_v0352_20260627.md
* **forbidden files**:
    * content/articles/**
    * translation.zh-CN.md
    * source.md
    * metadata.yaml
    * summary.md
    * notes.md
    * tracks.yaml
    * unrelated reports
* **modified files**:
    * templates/prompts/import_article_prompt.md
    * docs/AGENT_COMMANDS.md
    * docs/CLOUD_HERMES_INTEGRATION.md
    * docs/REPORTING_TEMPLATE.md
    * reports/online_smoke_and_anthology_extraction_regression_v0352_20260627.md (new)

---

## 4. Inputs

### For import tasks:

* **source URL**: N/A — no new import in this task
* **short command**: N/A — regression task
* **content directory**: `content/articles/2026/2026-06-27-emerson-self-reliance/` (read-only verification only)
* **duplicate check**: N/A — no new import attempted
* **blocked check**: N/A — no external import attempted
* **GitHub Pages URL**: https://conanxin.github.io/hermes-knowledge-base/items/2026-06-27-emerson-self-reliance/
* **extraction scope**: II. SELF-RELIANCE only
* **extraction start**: `<h2 id="link2H_4_0002">II. SELF-RELIANCE</h2>` (HTML position 52,118)
* **extraction end**: just before `<h2 id="link2H_4_0003">III. COMPENSATION</h2>` (HTML position 109,195)
* **anthology / collection boundary check**: PASS — HTML positions 52,118–109,195; 57,077 chars extracted; 11 other chapters excluded

### For feature tasks:

* **feature target**: anthology extraction rules and online smoke
* **modified scripts/docs**:
    * templates/prompts/import_article_prompt.md (added §"Anthology / Collection Page 单篇抽取规则")
    * docs/AGENT_COMMANDS.md (added §2a Anthology / Collection 页面抽取)
    * docs/CLOUD_HERMES_INTEGRATION.md (added §5a Anthology / Collection Page 导入)
    * docs/REPORTING_TEMPLATE.md (added §14 Anthology / Collection Page 导入报告必填字段)
* **generated files**: none (docs-only changes; update_site.py produced no diff)

---

## 5. Checks

| Script | Result |
|---|---|
| `check_task_preflight.py` | **FAIL** (expected: dirty tree from staged changes during task) |
| `check_release_tags.py` | **PASS_WITH_WARNINGS** (v0.3.36 known exception) |
| `check_kb.py` | **PASS** (48/48) |
| `check_tracks.py` | **PASS** (38 verified, 12 needs) |
| `update_site.py` | **PASS** (5/5, no diff — docs changes don't affect site generation) |
| `check_pages_sync.py` | **PASS** |
| `check_translation_residue.py` | **WARNING** (Emerson 8 suspicious — all proper_noun_ok/citation_or_url_ok by policy) |

---

## 6. Smoke Tests

### Local Smoke (Boundary Checks on Local Files)

| File | Field | Status | Evidence |
|---|---|---|---|
| `content/articles/2026/2026-06-27-emerson-self-reliance/source.md` | extraction scope 说明 | ✅ | Line 6: "Extraction scope: Only II. SELF-RELIANCE chapter" |
| `content/articles/2026/2026-06-27-emerson-self-reliance/source.md` | "II. SELF-RELIANCE" header | ✅ | Line 35: "## SELF-RELIANCE" |
| `content/articles/2026/2026-06-27-emerson-self-reliance/source.md` | no other chapter headers | ✅ | No "I. HISTORY" or "Spiritual Laws" chapter headers in body |
| `content/articles/2026/2026-06-27-emerson-self-reliance/metadata.yaml` | extraction_scope field | ✅ | "extraction_scope: Only II. SELF-RELIANCE from Essays, First Series" |
| `content/articles/2026/2026-06-27-emerson-self-reliance/metadata.yaml` | source_collection field | ✅ | "source_collection: Essays, First Series" |
| `content/articles/2026/2026-06-27-emerson-self-reliance/notes.md` | records Essays, First Series | ✅ | "Source: Project Gutenberg eBook #2944 (Essays, First Series, 1841)" |
| `content/articles/2026/2026-06-27-emerson-self-reliance/notes.md` | records boundary II.→III. | ✅ | "Boundaries: Start: II. SELF-RELIANCE ... End: Just before III. COMPENSATION" |
| `content/articles/2026/2026-06-27-emerson-self-reliance/translation.zh-CN.md` | no other chapters | ✅ | 10060 chars; no "Spiritual Laws" or "I. HISTORY" headers |
| `content/articles/2026/2026-06-27-emerson-self-reliance/translation.zh-CN.md` | no Compensation as body | ✅ | "Compensation" not present as chapter header |

### Online Smoke (GitHub Pages)

| URL | Expected | Result | Evidence |
|---|---|---|---|
| Homepage | 200 | ✅ HTTP 200 | https://conanxin.github.io/hermes-knowledge-base/ |
| Emerson detail | 200 | ✅ HTTP 200 | https://conanxin.github.io/hermes-knowledge-base/items/2026-06-27-emerson-self-reliance/ (98,207 bytes) |
| Thoreau detail | 200 | ✅ HTTP 200 | https://conanxin.github.io/hermes-knowledge-base/items/2026-06-27-thoreau-civil-disobedience/ (30,001 bytes) |
| Swift detail | 200 | ✅ HTTP 200 | https://conanxin.github.io/hermes-knowledge-base/items/2026-06-27-swift-modest-proposal/ (49,422 bytes) |
| Paste 1960s detail | 200 | ✅ HTTP 200 | https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/ (213,644 bytes) |

### Online Content Verification (Emerson detail page)

| Check | Expected | Result |
|---|---|---|
| Contains "Self-Reliance" | yes | ✅ |
| Contains "论自立" | yes | ✅ |
| Contains "Ralph Waldo Emerson" | yes | ✅ |
| Contains "summary" section | yes | ✅ |
| Contains "translation" content | yes | ✅ |
| No "track-card" | yes | ✅ (non-music) |
| No "track-filter-bar" | yes | ✅ |
| No "Spotify" | yes | ✅ |
| No "Apple Music" | yes | ✅ |
| No "I. HISTORY" chapter | yes | ✅ (only as Excluded list) |
| No "Spiritual Laws" chapter | yes | ✅ (only as Excluded list) |
| No "Compensation" chapter body | yes | ✅ (only as boundary marker in source.md top + Excluded list) |

### Online Content Verification (Paste 1960s music page)

| Check | Expected | Result |
|---|---|---|
| Contains "track-card" | yes | ✅ |
| Contains "Spotify" | yes | ✅ |
| Contains "Apple Music" | yes | ✅ |

### Online Content Verification (Thoreau / Swift non-music pages)

| Check | Expected | Result |
|---|---|---|
| No "track-card" | yes | ✅ |
| No "Spotify" | yes | ✅ |

### Live Catalog Verification

| Check | Result |
|---|---|
| `https://conanxin.github.io/hermes-knowledge-base/data/catalog.json` | 48 records ✅ |
| Emerson record present | yes (`Self-Reliance / 论自立 / slug: 2026-06-27-emerson-self-reliance`) ✅ |

---

## 7. Postflight

To be run after commit/tag:

```bash
python3 scripts/check_task_postflight.py \
    --report reports/online_smoke_and_anthology_extraction_regression_v0352_20260627.md \
    --tag v0.3.52-online-smoke-and-anthology-extraction-regression \
    --expect-clean --expect-head-origin
```

**Expected**:
* **check_task_postflight.py**: PASS
* **postflight status**: PASS
* **warnings**: 0
* **tag deref**: final v0.3.52 commit
* **tag deref commit**: final v0.3.52 commit
* **git status**: clean

---

## 8. Links

* **GitHub commit**: pending until push
* **GitHub tag**: pending until tag push
* **GitHub Pages**: https://conanxin.github.io/hermes-knowledge-base/
* **Emerson detail**: https://conanxin.github.io/hermes-knowledge-base/items/2026-06-27-emerson-self-reliance/

---

## 9. Warnings / Known Non-blockers

* **known warning**: `check_release_tags.py` may report PASS_WITH_WARNINGS for known v0.3.36 duplicate minor exception
* **reason**: historical tag exception documented in docs/RELEASES.md and docs/VERSIONING.md
* **action**: no action required
* **known warning**: `check_translation_residue.py` may still report proper_noun_ok / citation_or_url_ok warnings under current policy
* **reason**: Emerson article contains 8 residue samples (Ralph Waldo Emerson, original English quotations) — all proper_noun_ok / citation_or_url_ok per policy
* **action**: no action required; documented in docs/TRANSLATION_RESIDUE_POLICY.md

---

## 10. Next Version

* **recommended next minor**: expected v0.3.53 after tag creation
* **next suggested task**: normal article import or anthology extraction blocked-case regression

---

## 11. Online Smoke Details

| URL | Expected | Result | Evidence |
|---|---|---|---|
| Homepage | HTTP 200 | ✅ HTTP 200 (728 bytes) | https://conanxin.github.io/hermes-knowledge-base/ |
| Emerson detail | HTTP 200 + content | ✅ HTTP 200 (98,207 bytes) | Title "论自立 · hermes-knowledge-base"; contains "Self-Reliance", "论自立", "Ralph Waldo Emerson", "summary", "translation"; no music UI |
| Thoreau detail | HTTP 200 + non-music | ✅ HTTP 200 (30,001 bytes) | No track-card, no Spotify |
| Swift detail | HTTP 200 + non-music | ✅ HTTP 200 (49,422 bytes) | No track-card, no Spotify |
| Paste 1960s detail | HTTP 200 + music UI | ✅ HTTP 200 (213,644 bytes) | Contains track-card, Spotify, Apple Music |
| Live catalog | 48 records | ✅ 48 records | Emerson present (Self-Reliance / 论自立 / 2026-06-27-emerson-self-reliance) |

---

## 12. Anthology Extraction Regression

* **source page type**: Project Gutenberg anthology / book page (Essays, First Series, 12 essays)
* **imported scope**: II. SELF-RELIANCE only
* **boundary start**: `<h2 id="link2H_4_0002">II. SELF-RELIANCE</h2>` (HTML position 52,118)
* **boundary end**: just before `<h2 id="link2H_4_0003">III. COMPENSATION</h2>` (HTML position 109,195)
* **evidence source.md**: contains "II. SELF-RELIANCE" header; "Extraction scope" documented at top; "Compensation" appears only as boundary marker (HTML anchor ID), not body
* **evidence metadata.yaml**: `extraction_scope: "Only II. SELF-RELIANCE from Essays, First Series"`; `source_collection: "Essays, First Series"`
* **evidence notes.md**: "Boundaries" section records start/end; "Excluded" lists 11 other essays
* **evidence translation.zh-CN.md**: 10060 chars; no "Spiritual Laws" or "I. HISTORY" or "Compensation" chapter content
* **other chapters excluded**:
    * History
    * Compensation
    * Spiritual Laws
    * Love
    * Friendship
    * Prudence
    * Heroism
    * The Over-Soul
    * Circles
    * Intellect
    * Art
* **result**: PASS — anthology boundary check successful; only II. SELF-RELIANCE imported; all 11 other essays excluded

---

## 13. Documentation Changes

### templates/prompts/import_article_prompt.md

- **Added**: §"📚 Anthology / Collection Page 单篇抽取规则（v0.3.52+）"
- **Content**: 6 core rules (明确范围优先, 必须抽取指定边界, 必须记录 extraction scope, 边界无法稳定识别 → hard-stop, 不得混入其他章节, collection URL ≠ 整本书)
- **Example**: full block including short command and execution breakdown
- **metadata.yaml 必填字段**: extraction_scope + source_collection
- **notes.md 必填段**: Extraction Scope with boundaries + excluded list
- **历史案例**: 2026-06-27 Emerson《Self-Reliance》导入 (v0.3.51)

### docs/AGENT_COMMANDS.md

- **Added**: §2a "Anthology / Collection 页面抽取（v0.3.52+）"
- **Content**: example short command + 6 rules summary + link to import_article_prompt.md

### docs/CLOUD_HERMES_INTEGRATION.md

- **Added**: §5a "Anthology / Collection Page 导入（v0.3.52+）"
- **Content**: 3 requirements (写明 extraction scope, 无法确认边界时 hard-stop, 报告必填字段); links to import_article_prompt.md + AGENT_COMMANDS.md

### docs/REPORTING_TEMPLATE.md

- **Added**: §14 "Anthology / Collection Page 导入报告必填字段（v0.3.52+）"
- **Content**: 5 required fields (source URL, extraction scope, extraction start, extraction end, anthology/collection boundary check); postflight WARN if missing
- **Example**: PASS evidence "HTML positions 52,118–109,195; 57,077 chars extracted; 11 other chapters excluded"

---

*Report generated: 2026-06-27*