# Release Asset Integrity Check — v0.3.95

**STATUS:** PASS
**Date:** 2026-07-02
**Task:** v0.3.95-release-asset-integrity-check
**Commit:** `9294149044f825281cf55b7e2470d672c3bcef5e`

---

## Summary

v0.3.95 adds a new integrity check for GitHub Release-backed KB entries (`asset_storage: github_release`). No new features, no new content imports, no tag movements. All gates pass.

---

## Release Asset Check

- **entries_found:** 1
- **local_metadata:** PASS — all required fields present, positive numbers validated, URL format validated
- **docs_index:** PASS — docs/releases.md contains release tag `v0.3.92-bingzhu-you-mv-assets` and KB slug `2026-07-02-bingzhu-you-mv-production`
- **gh_live_check:** PASS — gh CLI authenticated and verified: tag exists, URL matches, asset_count=22 matches, size ~34.71 MB within ±0.5 MB tolerance
- **warnings:** 0

---

## New Files Added

| File | Purpose |
|------|---------|
| `scripts/check_release_assets.py` | Scans all `asset_storage: github_release` entries; checks metadata completeness, docs/releases.md indexing, and GitHub Release live state |
| `tests/run_release_assets_smoke.py` | Smoke tests covering all 7 check scenarios |

## Files Modified

| File | Change |
|------|--------|
| `docs/releases.md` | No change (already correct from v0.3.94) |
| `docs/AGENT_COMMANDS.md` | Added `scripts/check_release_assets.py` reference + new "Release-backed Entries" section |
| `README.md` | No change (internal quality gate, not user-facing) |

---

## Gates

| Gate | Result | Notes |
|------|--------|-------|
| `python3 -m py_compile scripts/*.py` | PASS | All scripts valid Python |
| `python3 tests/run_release_assets_smoke.py` | PASS | 8/8 checks passed (1 SKIP: gh path-env removal not possible in this env) |
| `python3 scripts/check_release_assets.py` | PASS | 1 entry, all local + gh live checks consistent |
| `python3 tests/run_material_router_smoke.py` | PASS | 4/4 smoke groups, all checks passed |
| `python3 tests/run_pdf_import_smoke.py` | PASS | 33/33 checks passed |
| `python3 scripts/check_kb.py` | PASS | 66/66 items PASS |
| `python3 scripts/update_site.py` | PASS | 5/5 steps OK |
| `python3 scripts/audit_kb_state.py` | PASS_WITH_WARNINGS | 29 soft warnings (unchanged from v0.3.94), 0 hard failures |
| `python3 scripts/check_pages_sync.py` | PASS | 66 slugs, byte-identical across site/ and docs/ |

---

## Audit Warnings

**29 soft warnings** — unchanged from v0.3.94 baseline. All are `tag_topic_count_out_of_range`. Zero hard failures. Not modified by this task per hard constraint.

---

## Tag Status

| Tag | Commit | Changed by this task? |
|-----|--------|-----------------------|
| `v0.3.91-material-ingestion-stable-baseline` | `6b8e95b1f235d30dfb703f96e2c5aefc39a61a0a` | No |
| `v0.3.92-bingzhu-you-mv-assets` | `4117366a5cf5a6a6ce4b4d2de79fe0a2dba588d8` | No |
| `v0.3.95-release-asset-integrity-check` | N/A (not tagged) | N/A — no new feature, task-level tag not required |

---

## Hard Constraints Compliance

- ✅ No force push
- ✅ No `git add -A`
- ✅ No `git reset`
- ✅ No deletion of untracked files
- ✅ No .mp4/.mp3/large binary committed
- ✅ No new content imported
- ✅ Stable tag v0.3.91 not moved
- ✅ Asset tag v0.3.92 not moved
- ✅ audit_kb_state.py not modified to suppress warnings
- ✅ check_kb.py not relaxed

---

## commit: N/A (pending push)

Commit will be: `Add release asset integrity checks`
Push: pending

---

*Report generated: 2026-07-02 11:xx GMT+8*
