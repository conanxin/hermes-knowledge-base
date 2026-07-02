# v0.3.98 — Tooling Stability Checkpoint

**STATUS:** PASS_WITH_WARNINGS

**DATE:** 2026-07-02
**TASK:** `v0.3.98-tooling-stability-checkpoint`
**REPORT_PATH:** `reports/tooling_stability_checkpoint_v0.3.98_20260702.md`

---

## HEAD

- **local:** `3d026f0` — Fix deterministic WeChat batch manifest selection (v0.3.97)
- **origin_main:** `3d026f0` — already up to date; no fetch drift
- **HEAD_distance_to_origin_main:** 0 commits

## PROTECTED_TAGS

| Tag                              | Object SHA                           | Dereferenced Commit                  | Kind         | Status |
|----------------------------------|--------------------------------------|--------------------------------------|--------------|--------|
| `v0.3.91-material-ingestion-stable-baseline` | `6b8e95b1f235d30dfb703f96e2c5aefc39a61a0a` | `56fe8482a8ce833baf52baa8429bdd17aac0d703` | annotated    | unchanged |
| `v0.3.92-bingzhu-you-mv-assets`  | `4117366a5cf5a6a6ce4b4d2de79fe0a2dba588d8` | `4117366a5cf5a6a6ce4b4d2de79fe0a2dba588d8` | lightweight  | unchanged |

- `tag_changed: false` — both tags held throughout v0.3.95/96/97/98
- v0.3.96 / v0.3.97 introduced **no** new tags (tooling changes); only v0.3.96's prior worker tag (`v0.3.96-full-gate-runner-and-tag-sanity`) was created then

## FULL_GATE

- **status:** `PASS_WITH_WARNINGS`
- **json_report:** `reports/full_gate_run_v0.3.98_20260702_1245.json`
- **steps_passed:** 16/17 PASS + 1 PASS_WITH_WARNINGS (audit_kb_state)
- **failed_steps:** 0
- **failed_step_names:** []
- **failed:** 0
- **exit_code:** 0
- **warnings:** 29 soft warnings, all `tag_topic_count_out_of_range` (audit_kb_state; unchanged since v0.3.91 — pre-existing metadata characteristics, not introduced by v0.3.98)
- **tracked_dirty_after_gate:** none (`working_tree.tracked_dirty_files: []`)
- **untracked_after_gate:** 16 (15 EXTERNAL prior-session gate JSONs + 1 new `v0.3.98` gate JSON to be committed)

### Per-step result

| Step                              | Result                  | Duration |
|-----------------------------------|-------------------------|----------|
| `py_compile`                      | PASS                    | 0.08s    |
| `run_smoke_tests`                 | PASS                    | 0.68s    |
| `run_wechat_batch_smoke`          | PASS (5/5)              | 2.41s    |
| `run_item_render_smoke`           | PASS                    | 0.12s    |
| `run_image_localization_smoke`    | PASS                    | 0.28s    |
| `run_material_router_smoke`       | PASS                    | 2.52s    |
| `run_web_article_smoke`           | PASS                    | 2.25s    |
| `run_youtube_import_smoke`        | PASS                    | 2.27s    |
| `run_fetch_layer_smoke`           | PASS                    | 0.66s    |
| `run_pdf_import_smoke`            | PASS                    | 1.54s    |
| `run_release_assets_smoke`        | PASS                    | 5.38s    |
| `check_release_assets`            | PASS (1 release-backed entry) | 2.51s |
| `check_release_tags`              | PASS (both tags OK)     | 1.36s    |
| `check_kb`                        | PASS (66/66)            | 0.25s    |
| `update_site`                     | PASS                    | 1.23s    |
| `audit_kb_state`                  | PASS_WITH_WARNINGS (29) | 0.22s    |
| `check_pages_sync`                | PASS                    | 0.07s    |

## MATERIAL_MATRIX

| Input type               | Status         | Backend                                | Notes |
|--------------------------|----------------|----------------------------------------|-------|
| `wechat_url` (mp.weixin.qq.com) | supported | `wechat_article_capture.py` + `import_wechat_article_capture.py` | 3-layer dedup; v0.3.71 stable |
| `generic_web_url`        | supported      | `web_article_to_kb.py`                 | Smoke-tested via `run_web_article_smoke` |
| `youtube_url`            | supported only with full transcript | `youtube_to_kb.py` | otherwise `BLOCKED_INCOMPLETE_TEXT` (no full auto-captions, too-short, low CJK, no manual track) |
| `local_html_md_txt`      | supported      | `material_to_kb.py --html-file / --markdown-file / --text-file` | All 3 local forms supported |
| `pdf_file` (extractable text) | supported | `pdf_to_kb.py` (pymupdf / fitz)        | v0.3.86 stable; respects gate `--import` mode |
| `scanned_pdf` (no text layer) | `BLOCKED_NEEDS_OCR` | `pdf_to_kb.py` refuses          | OCR is owned by `pdf-ocr-kb-import` workflow (`docs/import-recipes/PDF_OCR_LOCAL.md`); not called by this script |

Additional blocked categories (covered by `material_to_kb.py` exit states):

- `BLOCKED_FETCH_FAILED` — network error or non-2xx HTTP, or unreachable host
- `BLOCKED_INCOMPLETE_TEXT` — page returned but text unusable (< MIN_CHARS threshold)
- `BLOCKED_UNSUPPORTED` — host/source not recognized

## TOOLING_MATRIX

| Tool                                       | Status | Purpose |
|--------------------------------------------|--------|---------|
| `scripts/run_full_gate.py`                 | ✅ v0.3.96 stable | Standard unified gate runner — 17 steps full, 7 steps quick |
| `scripts/check_release_tags.py`            | ✅ v0.3.96 stable | Protected tag SHA sanity (annotated vs dereferenced); FAILs exit 1 on mismatch |
| `scripts/check_release_assets.py`          | ✅ v0.3.95 stable | Release-backed assets integrity — local metadata + docs index + gh CLI live validation |
| `tests/run_wechat_batch_smoke.py`          | ✅ v0.3.97 stable | Deterministic manifest selection via `--run-id` (no mtime flake) |
| `tests/run_pdf_import_smoke.py`            | ✅ v0.3.94 stable | No catalog/index pollution regression — guard asserts `SMOKE_SLUG_PREFIX` not in tracked `docs/data/catalog.json`, `site/data/catalog.json`, `index/*` |

### Auxiliary tools (kept in tree)

- `scripts/material_to_kb.py` — unified CLI entry over all input types
- `scripts/wechat_batch_import.py` — batch mode (3-layer dedup) with `--run-id` deterministic manifest
- `scripts/pdf_to_kb.py` — pymupdf text-layer extraction
- `scripts/youtube_to_kb.py` — transcript extraction with quality gating
- `scripts/web_article_to_kb.py` — generic web article import

## KNOWN_REMAINING_SOFT_WARNINGS

29 warnings, single category: `tag_topic_count_out_of_range` (audit_kb_state).

Soft ranges:
- topics: [3, 8]
- tags:   [6, 12]

Distribution of out-of-range entries (29 total):

- topics=2 (below):  2 entries  (older content from 1994, 2000)
- topics=9-12:       many 2026 entries (Chinese-language long-form)
- topics=15:         1 entry (Dario Amodei Bloomberg 2026)
- tags=13-27:        many 2026 entries (auto-inferred from long body text)

These are **pre-existing characteristics** of the KB corpus and are not introduced by v0.3.95/96/97/98. Same 29 were present at v0.3.91 baseline. They are warnings, not failures, and do not block the gate.

Future cleanup (out of v0.3.98 scope): a content-management task could tighten these by either:
1. Increasing the soft ranges (more permissive), or
2. Applying tag pruning / topic consolidation to current articles.

## NO_NEW_CONTENT_CONFIRMATION

- v0.3.98 introduced 0 new KB entries.
- v0.3.98 modified 0 tracked files except this report and the gate JSON artifact.
- `tmp/material_fetches`, `tmp/youtube_subs`, `inbox/` directories are working-state on disk; not committed.
- `tmp/`, `inbox/`, `raw/` (nonexistent) contents never staged.

## TRACKED_WORKING_TREE_CLEANLINESS

- Pre-task: HEAD `3d026f0`, working tree clean
- Mid-task: preflight classified 15 untracked files as `EXTERNAL` (`has_self_introduced: false`); 0 errors
- Post-full-gate: working tree has 0 modified tracked files (`git diff --stat` empty)
- Post-task commit (when applied): stage only `reports/tooling_stability_checkpoint_v0.3.98_20260702.md` + `reports/full_gate_run_v0.3.98_20260702_1245.json`

## NEXT_RECOMMENDATIONS

1. **v0.3.99+ candidates** (any of these would be appropriate next steps; pick one):
   - (a) Optional content-hygiene task: tighten `tag_topic_count_out_of_range` warnings by either adjusting soft ranges in `audit_kb_state.py` (allowed for this v0.3.x tooling) or pruning auto-inferred tags on long-form Chinese-language articles. NOT required for correctness — these are soft warnings only.
   - (b) Optional KB expansion: ingest one well-curated article batch (WeChat or generic) to validate end-to-end pipeline including `update_site.py`. NOT required — current 66/66 KB pipeline is stable.
   - (c) Optional observability: extend `run_full_gate.py` JSON to surface per-step stdout byte counts; helpful for trend analysis. NOT required.

2. **Standing directive** for v0.3.99+: every task should:
   - Run `python scripts/run_full_gate.py --quick` before claiming "task complete".
   - Run `python scripts/run_full_gate.py --json --output reports/full_gate_run_<task>_<ts>.json` at start and end for archival.
   - Use `--run-id` whenever invoking `scripts/wechat_batch_import.py` programmatically.

3. **Operational notes** (carry-over from prior tasks):
   - `next available minor: v0.3.97` per `scripts/check_release_tags.py` (already used; next is `v0.3.99` or higher).
   - The flake in `run_wechat_batch_smoke` is **fully fixed** by v0.3.97 (5/5 deterministic across 5+ consecutive runs post-commit).
   - The `audit_kb_state` `tag_topic_count_out_of_range` 29 warnings have been stable since v0.3.91 baseline; not regressions.

## CHECKPOINT_DECISION

✅ v0.3.98 is a green state.

- Tooling is stable (5 commits of gate runner / check_release_assets / check_release_tags / wechat_batch determinism / pdf_no_pollution).
- Content pipeline is stable (66/66 KB entries, 0 hard audit failures).
- Tags held through full v0.3.95/96/97/98 cycle (4 commits since last tag movement at v0.3.93).
- No new feature work is required for v0.3.99 unless user explicitly requests it.

---

**END OF REPORT**
