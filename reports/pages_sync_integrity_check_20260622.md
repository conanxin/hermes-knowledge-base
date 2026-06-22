# Pages sync integrity check — implementation report

**Date**: 2026-06-22
**Trigger**: v0.3.9 online smoke test discovered that `docs/styles.css` was
missing from the v0.3.9 commit (commit `98e1170`). The dev tree
(`site/styles.css`) had been updated and `sync_pages_docs.py` had copied
the new bytes to disk, but `git add` had skipped `docs/styles.css`. GitHub
Pages deployed from the commit, so users saw the v0.3.8 stylesheet while
the local tree looked correct. Fixed in commit `4adb6cc`
(`Smoke test v0.3.9 detail pages online`, tagged
`v0.3.10-detail-page-online-fix`).

## Goal

Add a lightweight, deterministic check that runs **after** `sync_pages_docs.py`
and asserts `site/` and `docs/` are byte-identical for every published file —
catching the failure mode above before the commit is made.

## New script — `scripts/check_pages_sync.py`

Pure stdlib (hashlib, pathlib), no dependencies, exits 0 / 1 / 2.

### Checks

1. **Top-level files** (must match byte-for-byte):
   - `site/index.html` ↔ `docs/index.html`
   - `site/app.js` ↔ `docs/app.js`
   - `site/styles.css` ↔ `docs/styles.css`
   - `site/data/catalog.json` ↔ `docs/data/catalog.json`

2. **Item pages**:
   - `site/items/<slug>/index.html` ↔ `docs/items/<slug>/index.html`
     for every shared slug.
   - Reports slugs present in `site/items/` but missing in `docs/items/`.
   - Reports stale slugs present in `docs/items/` but missing in `site/items/`.
   - Reports content mismatches inside shared slugs.

### Sample output (PASS)

```
============================================================
Pages sync integrity check
============================================================

[1/2] Top-level files (must be byte-identical)
  Path                           site/      docs/      Status
  ------------------------------ ---------- ---------- ----------
  index.html                     191b600202d6c507 191b600202d6c507 OK
  app.js                         e2692820624957bc e2692820624957bc OK
  styles.css                     8ad405052ca06029 8ad405052ca06029 OK
  data/catalog.json              085da5c1d2d9784d 085da5c1d2d9784d OK

[2/2] Item pages (site/items/ ↔ docs/items/)
  site slugs: 19
  docs slugs: 19
  all 19 slugs present and byte-identical.

============================================================
STATUS: PASS
============================================================
```

### Sample output (FAIL — synthetic drift)

Injected a trailing `/* drift */` comment into `docs/styles.css` while
testing, observed `STATUS: FAIL`, exit code `1`, with one row marked
`MISMATCH` and a remediation hint pointing back at `update_site.py` /
`git status`. Restored the file immediately after.

### Exit codes

| Code | Meaning |
|------|---------|
| 0 | site/ and docs/ are byte-identical for every published file |
| 1 | At least one mismatch, missing file, or stale file |
| 2 | Unexpected exception (uncaught) |

## Wiring — `scripts/update_site.py`

The build chain is now a 5-step pipeline:

```
STEP 0/5  check_kb.py            ← quality gate (existing)
STEP 1/5  build_index.py
STEP 2/5  export_site_data.py
STEP 3/5  generate_item_pages.py
STEP 4/5  sync_pages_docs.py
STEP 5/5  check_pages_sync.py    ← post-sync integrity check (NEW)
```

If `check_pages_sync.py` returns non-zero (after the build chain ran
successfully), `update_site.py` returns non-zero and prints a hard-stop
banner explaining that `site/` and `docs/` are out of sync — typically
because `sync_pages_docs.py` has a bug, or the next `git add` will skip a
synced `docs/` file.

This mirrors the existing pattern used for `check_kb.py`: a hard-stop
gate that turns silent drift into a noisy, structured failure before the
publish step completes.

## Documentation updates

- **`README.md`** — added `python3 scripts/check_pages_sync.py` to the
  quality-check commands block and a row in the per-script table.
- **`docs/AGENT_COMMANDS.md`** — added the check to the short-command
  import flow's "imports complete, run these checks" block.

## Run results

| Step | Command | Result |
|------|---------|--------|
| 1 | `python3 scripts/check_kb.py` | **PASS** (19/19) |
| 2 | `python3 scripts/update_site.py` | **PASS** (0/5 → 5/5) |
| 3 | `python3 scripts/check_pages_sync.py` | **PASS** |
| 4 | `python3 scripts/check_translation_residue.py` | **WARNING** (acceptable, pre-existing) |

`update_site.py` end-state:

```
[1/5] scripts/build_index.py OK
[2/5] scripts/export_site_data.py OK
[3/5] scripts/generate_item_pages.py OK
[4/5] scripts/sync_pages_docs.py OK
[5/5] scripts/check_pages_sync.py OK

All steps completed successfully.
```

`git status` after the full pipeline: only the 4 expected files
(`check_pages_sync.py` new, `update_site.py` / `README.md` /
`docs/AGENT_COMMANDS.md` modified) — no stray site/docs drift.

## Files changed

| File | Change |
|------|--------|
| `scripts/check_pages_sync.py` | **new** — post-sync integrity check |
| `scripts/update_site.py` | added STEP 5/5 (`check_pages_sync.py`) with hard-stop on FAIL |
| `README.md` | added check to quality-check commands + table |
| `docs/AGENT_COMMANDS.md` | added check to short-command import flow |

## What this prevents

| Failure mode | Caught by |
|--------------|-----------|
| `sync_pages_docs.py` deleted a synced file from `docs/` but not `site/` | ✅ extra-in-docs |
| `sync_pages_docs.py` failed to copy a new file into `docs/` | ✅ missing-in-docs |
| `git add` skipped a `docs/` file that had been synced on disk | ✅ detected **before** commit (the v0.3.9 case) |
| `generate_item_pages.py` regenerated `site/items/` but `sync_pages_docs.py` was skipped | ✅ content mismatch on every item page |
| Operator manually edited `docs/styles.css` and forgot `site/styles.css` | ✅ top-level MISMATCH |

## Followups considered, not implemented

- **Auto-amend on FAIL**: tempting, but the drift could be legitimate
  (someone editing `docs/` directly) and silent auto-fixes are hostile.
  Detection + a hard exit code is the safer contract.
- **Subset hash check on `data/catalog.json` only**: rejected — the whole
  point is that *any* publish file drift is a deploy hazard, not just
  the catalog.
- **CI hook** to run this on every push: out of scope. The check is
  cheap and runs locally as part of `update_site.py`.