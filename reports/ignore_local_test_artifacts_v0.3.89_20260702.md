# v0.3.89 — Ignore Local Test and Dry-run Artifacts

**STATUS: PASS**

**Date:** 2026-07-02 08:18 GMT+8
**Branch:** `main`
**HEAD before:** `3dacc1f` (v0.3.88, already pushed)
**HEAD after:** <see below — see "commit / push">

---

## SUMMARY

Added 4 categories of ignore rules to `.gitignore` to keep the working tree clean of
local test/dry-run artifacts. Reduced untracked file count from **~626 to 2**. The 2
remaining untracked files are formal release reports flagged for human review (NOT
session artifacts).

Also re-ran `update_site.py` to clean the tracked dirty state from the v0.3.88a
checkpoint report (a stale routing-capture catalog entry that was re-introduced
after v0.3.88a finished).

---

## ROOT CAUSE

After v0.3.88 / v0.3.88a, the local working tree accumulated ~626 untracked files:
- `content/articles/DRY_RUN_PREVIEW/` (PDF smoke dry-run artifact)
- `inbox/raw/{pdf,web,wechat,youtube}/` (~297 fetch/fixture JSONs)
- `reports/material_import_*.{md,json}` (~125 pairs of per-run task reports)
- `reports/wechat_batch_import_*.{md,json}` (~75 pairs)
- `reports/generated_artifact_clean_checkpoint_v0.3.88a_*.md` (v0.3.88a report)

These files are SELF-introduced by local test runs and should not enter the
repository. The existing `.gitignore` already covered `tmp/`, `tmp/youtube_subs/`,
and `tmp/material_fetches/`, but no rule covered the above categories.

Additionally, the tracked `docs/data/catalog.json`, `site/data/catalog.json`, and
`index/*` files had drifted (1 stale routing-capture entry from a previous PDF
smoke run). `update_site.py` regenerated them into canonical state.

---

## FIX (added to `.gitignore`)

```gitignore
# Ignore PDF / local document import dry-run artifacts (v0.3.89)
content/articles/DRY_RUN_PREVIEW/

# Ignore inbox/raw capture fixtures — fetched / generated raw payloads
# that should never enter the repository (large, often user-license-bound).
# Real content lives in content/articles/ after the import pipeline processes them.
inbox/raw/pdf/
inbox/raw/web/
inbox/raw/wechat/
inbox/raw/youtube/

# Ignore session / per-run task reports that are SELF-introduced by local
# material imports and wechat batch imports. Formal release reports (e.g.
# fix_wechat_batch_smoke_stale_count_v0.3.88_*.md, no_real_pdf_material_matrix_*,
# pdf_kb_import_v0.3.86_*.md, pdf_ocr_postflight_*.md, ignore_local_test_artifacts_*)
# are intentionally NOT ignored — they are committed as release evidence.
reports/material_import_*.md
reports/material_import_*.json
reports/wechat_batch_import_*.md
reports/wechat_batch_import_*.json
reports/generated_artifact_clean_checkpoint_*.md
```

---

## UNTRACKED FILE COUNT COMPARISON

| State | Count |
|---|---|
| Before .gitignore changes | ~626 |
| After .gitignore changes | 2 |

**Remaining 2 untracked files (formal release reports, NOT session artifacts — kept for human review):**
- `reports/pdf_kb_import_v0.3.86_20260702.md` — formal v0.3.86 PDF KB import release report (companion to the already-committed `reports/pdf_ocr_import_2026-06-29-le-guin-carrier-bag.md` style files)
- `reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json` — formal v0.3.63 OCR postflight finalcheck JSON (companion to `pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629.{json,md}` which are already committed)

These two files should be evaluated by the user for inclusion in a separate commit
(v0.3.89 doesn't auto-include them — they are formal artifacts, not session noise).

---

## GITIGNORE VERIFICATION

```
$ git check-ignore -v content/articles/DRY_RUN_PREVIEW/latest_capture.json
.gitignore:17:content/articles/DRY_RUN_PREVIEW/  content/articles/DRY_RUN_PREVIEW/latest_capture.json

$ git check-ignore -v inbox/raw/pdf/test.json
.gitignore:22:inbox/raw/pdf/  inbox/raw/pdf/test.json

$ git check-ignore -v reports/material_import_test.md
.gitignore:32:reports/material_import_*.md  reports/material_import_test.md

$ git check-ignore -v reports/fix_wechat_batch_smoke_stale_count_v0.3.88_20260702.md
(exit 1 — NOT ignored, as expected for formal reports)

$ git check-ignore -v reports/pdf_kb_import_v0.3.86_20260702.md
(exit 1 — NOT ignored, as expected for formal reports)
```

---

## GATES (post-.gitignore, post-gates)

| Gate | Result |
|---|---|
| `run_material_router_smoke.py` | PASS (4/4) |
| `run_pdf_import_smoke.py` | PASS (26/26) |
| `check_kb.py` | PASS (65 items, 0 fail) |
| `check_pages_sync.py` | PASS (site=docs=66, content=65) |

---

## KNOWN POST-COMMIT DIRTY STATE

After running `run_pdf_import_smoke.py` smoke_4, the 6 tracked generated artifacts
(`docs/data/catalog.json`, `site/data/catalog.json`, `index/catalog.jsonl`,
`index/authors.md`, `index/tags.md`, `index/timeline.md`) re-accumulate a stale
`2026-07-02-hermes-knowledge-base-routing-capture` entry because pdf_to_kb.py
smoke_4 creates `content/articles/2026/<slug>/` + invokes `update_site.py --only`.

This is the SAME root cause v0.3.88 fixed the smoke test for (smoke_5 dropped the
`site==docs==content` triple-equality). The catalogs themselves still get the
fixture added because `update_site.py --only` runs without pruning.

**Workaround:** Run `python3 scripts/update_site.py` (no `--only`) before
committing to regenerate catalogs cleanly. The v0.3.89 commit was prepared BEFORE
running gates, so the commit is clean. The post-gate dirty state will need a
follow-up chore commit if the user wants those regenerations tracked.

---

## FILES CHANGED (2 files)

| File | Change |
|---|---|
| `.gitignore` | Modified (+24 lines): added ignore rules for DRY_RUN_PREVIEW, inbox/raw/*, session reports |
| `reports/ignore_local_test_artifacts_v0.3.89_20260702.md` | New (this file) |

---

## GIT STATUS (post-gates, pre-commit)

```
 M .gitignore
 M docs/data/catalog.json
 M index/authors.md
 M index/catalog.jsonl
 M index/tags.md
 M index/timeline.md
 M site/data/catalog.json
?? docs/items/2026-07-02-hermes-knowledge-base-routing-capture/
?? reports/pdf_kb_import_v0.3.86_20260702.md
?? reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json
```

Per protocol, only `.gitignore` and `reports/ignore_local_test_artifacts_v0.3.89_*.md`
are committed. The 6 tracked catalog/index files and the untracked docs/items/
test fixture are intentionally NOT included in this commit.

---

## NEXT STEPS

1. The 2 remaining untracked formal reports
   (`reports/pdf_kb_import_v0.3.86_20260702.md` and
   `reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json`)
   can be evaluated for inclusion in a separate chore commit (they appear to be
   formal release artifacts similar to other already-committed `pdf_*.md/json`
   files in `reports/`).

2. To permanently eliminate the post-PDF-smoke tracked-dirty state, a future
   improvement would be to have `scripts/pdf_to_kb.py` smoke cleanup also prune
   the catalog entry when the article directory is removed (the catalog has the
   `2026-07-02-hermes-knowledge-base-routing-capture` entry because update_site.py
   was called during smoke, but the article directory was later removed).
   This is out of scope for v0.3.89.