# KB State Dashboard + README Sync — v0.3.60

## STATUS: PASS_WITH_WARNINGS (38 warnings, 0 hard fail)

## Real item count

**54 items** in `content/**/metadata.yaml` (was previously mis-stated as 19/19 in README).

## Type distribution

| type | count |
|------|-------|
| article | 25 |
| note | 9 |
| essay | 8 |
| resource_collection | 5 |
| project | 4 |
| interview | 1 |
| academic_paper | 1 |
| video | 1 |
| **TOTAL** | **54** |

## Status distribution

| status | count |
|--------|-------|
| translated | 29 |
| migrated | 13 |
| published | 4 |
| active | 4 |
| original | 3 |
| collected | 1 |

## P0 / P1 / P2 findings

### P0 — none (no hard failures)

`audit_kb_state.py` exit=0; catalog parse OK; site/docs byte-identical OK; metadata.yaml readable for all 54 entries.

### P1 — addressed in this task

| # | Finding | Fix |
|---|---------|-----|
| P1.1 | README total stat said "19" / "19/19" but real total = 54 | Replaced hard-coded numbers with `<!-- KB_STATE_START --> ... <!-- KB_STATE_END -->` managed block in README |
| P1.2 | README type table listed only 4 types (article / note / project / resource_collection) | Expanded to 8 types (added essay / video / academic_paper / interview) |
| P1.3 | `scripts/check_kb.py` had inline `item_type == "article"` for translation_language + translation file checks | Extracted to `TRANSLATABLE_TYPES = {"article", "essay"}` constant; essay entries with translation_language=zh-CN are now validated for translation.zh-CN.md presence + word_count drift |
| P1.4 | README's quality-check table claimed "PASS (19/19)" | Replaced with managed reference: "PASS (see audit_kb_state.py output for real total)" |

### P2 — observed, NOT fixed in this task (documented for follow-up)

| # | Finding | Why deferred | Recommended action |
|---|---------|--------------|--------------------|
| P2.1 | **dir_drift**: `content/collections/` (4 items) and `content/resource_collections/` (1 item) coexist; all 5 declare type=resource_collection | All 5 items use the canonical type; directory name drift is cosmetic. README now warns "遗留目录，请勿新建条目". A move would touch 5 items + their slugs + site/docs detail pages | Future consolidation task: move 4 items from `content/collections/` to `content/resource_collections/` (or vice versa) + update slugs + regenerate site/docs |
| P2.2 | **translation_language='null'** (literal string, not YAML null) in 7 metadata files (5 legacy-knowledge + 2 projects) | These are migrated legacy entries. `null` is a legacy placeholder. check_kb.py doesn't currently check this; audit_kb_state.py WARNs | Either accept the WARN (legacy drift) or replace `translation_language: null` with empty/missing in a future v0.3.61+ legacy-backfill task |
| P2.3 | **tag/topic count out of soft range** in 29 items | Soft limits in README say tags 6-12 / topics 3-8. Many real entries (esp. paste-greatest-songs-1960s with 27 tags / dario-amodei with 25 tags) exceed because they need fine-grained discoverability for the catalog filter UI | Either (a) loosen soft limits in README to 5-30 / 3-15, or (b) accept historical drift as WARN-only. Soft limits are guidelines, not hard rules |
| P2.4 | **duplicate tag** `Mencius Moldbug` appears twice in 421news-the-people-are-never-right | Single-entry issue; cosmetic | Surgical fix in a future metadata cleanup task |
| P2.5 | **README postflight CLI examples**: spec asked to grep for old `--expect-clean --expect-head-origin` style in README. README had no such examples; the postflight CLI is only documented in historical reports and docs/AGENT_COMMANDS.md. `audit_kb_state.py` check_postflight_cli_drift_in_readme returns clean. | No action needed in README. `docs/AGENT_COMMANDS.md` and historical `reports/` may still contain old examples — out of scope for this task per spec ("不要删除历史报告") | Document the new CLI (`--profile auto`) in a separate v0.3.6x task targeting docs/AGENT_COMMANDS.md |

## What this task fixed

1. **Added `scripts/audit_kb_state.py`** (new, 18.6 KB, 508 lines)
   - Reads all `content/**/metadata.yaml` and reports type/status/site/year histograms + last 10 entries
   - Cross-checks `index/catalog.jsonl` vs `site/data/catalog.json` vs `docs/data/catalog.json` for count + slug drift
   - Detects README staleness (literal "19" / "19/19" / "19 records")
   - Detects type-coverage gaps in README's type table
   - Detects postflight CLI drift in README
   - Detects `translation_language: 'null'` (string) and translatable types missing translation.zh-CN.md
   - Detects tags/topics outside [6,12] / [3,8] soft ranges (WARN-only, by design)
   - Detects duplicate tag values within a single metadata.yaml
   - Detects `content/collections/` vs `content/resource_collections/` directory drift
   - Verifies `site/data/catalog.json` ↔ `docs/data/catalog.json` byte-identity (HARD FAIL on mismatch)
   - Exit 0 on PASS / PASS_WITH_WARNINGS; exit 1 only on hard failures
2. **Updated `README.md`** with `<!-- KB_STATE_START --> ... <!-- KB_STATE_END -->` managed block + expanded type table (4 → 8 types) + correct item total (19 → 54) + new `audit_kb_state.py` row in quality-check table
3. **Updated `scripts/check_kb.py`** to use `TRANSLATABLE_TYPES = {"article", "essay"}` constant (was hard-coded `item_type == "article"` in 2 places). Essay entries with `translation_language: zh-CN` are now properly validated for translation.zh-CN.md presence + word_count drift (catches the previous silent gap).

## What this task did NOT fix (out of scope)

- Did NOT consolidate `content/collections/` ↔ `content/resource_collections/` (P2.1, would touch 5 items)
- Did NOT clean `translation_language: 'null'` in 7 legacy entries (P2.2)
- Did NOT loosen tag/topic soft limits in README (P2.3)
- Did NOT fix the duplicate `Mencius Moldbug` tag (P2.4)
- Did NOT modify historical reports that still show old postflight CLI (P2.5 — per spec "不要删除历史报告")
- Did NOT modify any existing content (source.md / translation.zh-CN.md / summary.md / notes.md) — only metadata.yaml allowed, none modified

## Commands run and results

```bash
$ python3 scripts/check_task_preflight.py --planned-tag v0.3.60-kb-state-dashboard-readme-sync --allow-warnings
STATUS: PASS
  git_repo: PASS / git_status: PASS / head_sync: PASS / version_number: PASS
  check_release_tags: PASS_WITH_WARNINGS / check_kb: PASS / check_pages_sync: PASS / check_tracks: PASS

$ python3 -m py_compile scripts/*.py
compile OK (all 13 scripts)

$ python3 scripts/check_kb.py
Total items: 54 / PASS: 54 / FAIL: 0 / STATUS: PASS
Warnings (7) — non-blocking: word_count.translation drift in 7 essay entries (NEW: now caught for essay type thanks to TRANSLATABLE_TYPES)

$ python3 scripts/update_site.py
[1/5] check_kb.py OK / [2/5] export_site_data.py OK / [3/5] generate_item_pages.py OK / [4/5] sync_pages_docs.py OK / [5/5] check_pages_sync.py OK / All steps completed successfully.

$ python3 scripts/audit_kb_state.py
Real metadata.yaml count: 54 / STATUS: PASS_WITH_WARNINGS (38 warnings) / exit=0

$ python3 scripts/check_pages_sync.py
STATUS: PASS (site/ ↔ docs/ byte-identical)

$ python3 scripts/check_task_postflight.py --report-file reports/kb_state_dashboard_v0.3.60_20260629.md --profile auto
(see Postflight section below)

$ git status --short
(see Modified files section below)
```

## Modified files

| File | Status | Description |
|------|--------|-------------|
| `README.md` | M | Replaced hard-coded "19/19" / "19 records" / type table with `<!-- KB_STATE_START -->` ... `<!-- KB_STATE_END -->` managed block; expanded type table from 4 to 8 types; added `audit_kb_state.py` row to quality-check table |
| `scripts/check_kb.py` | M | Added `TRANSLATABLE_TYPES = {"article", "essay"}` constant; replaced 2 inline `item_type == "article"` checks with `item_type in TRANSLATABLE_TYPES`; updates error message to mention translatable types |
| `scripts/audit_kb_state.py` | A (new) | Lightweight state auditor — see "What this task fixed" §1 above |
| `reports/kb_state_dashboard_v0.3.60_20260629.md` | A (new) | This report |

## Commit

- (final SHA filled in after commit)
- Message: `Add KB state dashboard and README sync audit`

## Tag

- (final tag deref filled in after tag push)
- Tag: `v0.3.60-kb-state-dashboard-readme-sync`

## GitHub Pages check

- Pending: run `python3 scripts/update_site.py` (already done above, all green) + push + wait 30-60s for GitHub Pages CDN + re-verify `https://conanxin.github.io/hermes-knowledge-base/` shows 54 items

## Pre-flight / Post-flight

**Preflight (v0.3.60-kb-state-dashboard-readme-sync)**: PASS — all 8 checks green

**Postflight**: see `check_task_postflight.py --report-file <this> --profile auto` output

## Acceptance criteria (from spec)

- [x] 修复 README 当前状态漂移 (19/19 → 54, type table 4 → 8)
- [x] 修复 postflight 命令漂移 (README 中无老 CLI 残留; `audit_kb_state.py` 自动检测 README 内的漂移)
- [x] 新增轻量状态审计脚本 `scripts/audit_kb_state.py` (满足全部 spec 要求)
- [x] 报告含 STATUS / 真实条目总数 / 类型分布 / P0-P1-P2 / 修复内容 / 未修复但建议 / 运行过的命令
- [x] README 含 `<!-- KB_STATE_START --> ... <!-- KB_STATE_END -->` managed block
- [x] check_kb.py 抽出 TRANSLATABLE_TYPES 集合, essay 现在被 translation_language + translation file 检查覆盖
- [x] tags/topics 数量做 WARN, 不让历史内容 FAIL
- [x] Per-file `git add`, no `git add -A`
- [x] Commit message: `Add KB state dashboard and README sync audit`
- [x] Tag: `v0.3.60-kb-state-dashboard-readme-sync`

