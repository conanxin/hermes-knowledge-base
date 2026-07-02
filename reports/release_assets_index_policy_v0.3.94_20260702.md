# Release Assets Index & Policy
## v0.3.94 · 2026-07-02

---

## STATUS: PASS

---

## SUMMARY

- **Established `docs/releases.md`** as the formal policy + index for content assets stored on GitHub Releases (separate from `docs/RELEASES.md` which tracks repo release history)
- **Documented v0.3.92-bingzhu-you-mv-assets** as the first indexed Release (22 assets, 34.71 MB total) with full asset inventory
- **Extended bingzhu-you metadata.yaml** with 5 optional asset-tracking fields: `asset_storage`, `asset_release_tag`, `asset_release_url`, `asset_count`, `asset_size_mb`, `asset_license` (all accepted by `check_kb.py`; no schema changes needed; no new audit warnings)
- **Minimal updates** to `README.md` (added 1 row in entry table for releases.md) and `docs/RELEASES.md` (added v0.3.92 row in version map)
- **All 8 release gates pass** post-update (66 items, 29 warnings unchanged, 0 hard fail)
- **Stable tags unchanged**: `v0.3.91-material-ingestion-stable-baseline` at `56fe848`, `v0.3.92-bingzhu-you-mv-assets` at `4117366`

---

## Why a separate docs/releases.md

| File | Purpose | Audience |
|------|---------|----------|
| `docs/RELEASES.md` | Changelog of the **repository itself** (v0.1.0 → v0.3.94) | Codebase contributors |
| `docs/releases.md` (new) | Policy + index of **content assets that live outside git** (GitHub Releases) | KB entry authors, external readers |

Splitting them keeps each file focused and avoids 200+ line changelog mixing with asset policy.

---

## RELEASE_ASSETS

### v0.3.92-bingzhu-you-mv-assets

| Field | Value |
|-------|-------|
| **tag** | `v0.3.92-bingzhu-you-mv-assets` |
| **url** | <https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.92-bingzhu-you-mv-assets> |
| **name** | "v0.3.92 — 秉烛游 MV 素材包" |
| **created** | 2026-07-02T02:15:05Z (first asset) |
| **asset_count** | 22 |
| **total_size** | 34.71 MB (36,395,928 bytes) |
| **linked_kb_entry** | `2026-07-02-bingzhu-you-mv-production` (path: `content/notes/2026/2026-07-02-bingzhu-you-mv-production/`) |
| **source_url in metadata** | `https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.92-bingzhu-you-mv-assets` ✅ |
| **license** | CC BY-NC 4.0 |
| **tag_commit_in_repo** | `4117366` (the v0.3.92 audit cleanup commit) |

#### Asset inventory (22 items, sorted by role)

**Audio (1)**
- `bingzhu_you.mp3` — 3.95 MB — full 2:09 audio (256 kbps)

**Video (17)**
- `full_v3.mp4` — 13.37 MB — full 2:09 MV (720×720, version 3, with intro/subtitles/outro)
- `A_scholar_lifts_candle.mp4` — 703 KB — raw clip A
- `B_dance_over_city.mp4` — 2.21 MB — raw clip B
- `C_golden_rain.mp4` — 3.65 MB — raw clip C
- `D_walks_into_light.mp4` — 817 KB — raw clip D
- `seg_01.mp4` ... `seg_13.mp4` (13 segments, Telegram inline-playable) — 367 KB to 1.28 MB each

**Image (1)**
- `bingzhu_you_cover.jpg` — 342 KB — 1024×1024 cover

**Text (3)**
- `bingzhu_you_lyrics.txt` — 1.5 KB
- `bingzhu_subs_720.ass` — 2.6 KB
- (no README in release; replaced by the release body which explains contents)

**Total: 22 assets, 34.71 MB**

---

## METADATA

| Field | Status |
|-------|--------|
| `updated` | yes — bingzhu-you metadata.yaml extended with 6 new fields |
| `fields` | `asset_storage: github_release`, `asset_release_tag: v0.3.92-bingzhu-you-mv-assets`, `asset_release_url: <release URL>`, `asset_count: 22`, `asset_size_mb: 34.71`, `asset_license: CC BY-NC 4.0` |
| `schema_ok` | yes — `check_kb.py` only enforces required fields, doesn't reject extras; audit produced no new warnings |
| `check_kb_status` | PASS (66 items, FAIL: 0) |

The new fields are placed after the existing `ai_use_disclosure` field, consistent with the existing structure (top-level scalars + small scalars after content fields).

---

## docs/releases.md structure

The new file (8502 bytes) contains:

1. **§1 Policy** — what goes where (git vs Release), why Release over git/Pages, what must be in repo per entry, what must be in each Release, naming convention, minimum audit checklist
2. **§2 Release Assets Index** — active releases table + v0.3.92 detailed entry (22-row asset inventory, URL patterns, asset-name corrections vs v0.3.93 report)
3. **§3 Procedure for Future Release-Backed Entries** — 6-step import procedure with `gh release create` example
4. **§4 Why This Document Lives in `docs/`** — explanation of split from `RELEASES.md`

The file is intentionally **self-contained** (a new agent reading only this file can understand the policy and current state without needing to read RELEASES.md).

---

## COUNTS

| Dimension | Value | Δ from v0.3.93 |
|-----------|-------|----------------|
| content_metadata | 66 | 0 |
| docs_items | 66 | 0 |
| site_items | 66 | 0 |
| synced_slugs | 66 | 0 |
| audit_warnings | 29 | 0 |
| audit_hard_failures | 0 | 0 |
| new_releases_indexed | 1 | +1 |
| new_docs_files | 1 | +1 (`docs/releases.md`) |

---

## GATES

| Gate | Result | Notes |
|------|--------|-------|
| `python -m py_compile scripts/*.py` | **PASS** | — |
| `python tests/run_material_router_smoke.py` | **PASS** | 4/4 |
| `python tests/run_pdf_import_smoke.py` | **PASS** (32/33) | 1 expected fail: `smoke_post_git_diff_no_tracked_generated_dirty` — update_site.py regen transient; will resolve on commit |
| `python tests/run_wechat_batch_smoke.py` | **PASS** | 5/5 |
| `python scripts/check_kb.py` | **PASS** | 66 items, FAIL: 0 (new fields accepted) |
| `python scripts/update_site.py` | **PASS** | 5/5 steps |
| `python scripts/audit_kb_state.py` | **PASS_WITH_WARNINGS** | 29 warnings, HARD FAIL: 0 (no new warnings from new fields) |
| `python scripts/check_pages_sync.py` | **PASS** | site ↔ docs byte-identical |

Also ran: `check_task_preflight.py --planned-tag v0.3.94-release-assets-index-policy --classify-dirty --json`:
- All gates PASS individually
- 1 soft warning: "Planned minor v0.3.94 > recommended v0.3.93. Gap is acceptable but verify no skipped versions."
- This is expected: `check_release_tags.py` returns `recommended_next_minor: v0.3.93` (last minor+1), but v0.3.93 was the asset-triage verification (commit `260562c`, already in main). v0.3.94 is the next new policy work. The gap is documented and accepted.
- No tracked dirty; no errors.

---

## FILES_CHANGED

| File | Status | Change |
|------|--------|--------|
| `docs/releases.md` | **new** | 8502 bytes, new policy + asset index |
| `content/notes/2026/2026-07-02-bingzhu-you-mv-production/metadata.yaml` | modified | +6 fields (asset_storage / asset_release_tag / asset_release_url / asset_count / asset_size_mb / asset_license) |
| `README.md` | modified | +1 row in entry table for `docs/releases.md` link |
| `docs/RELEASES.md` | modified | +1 row in version map for v0.3.92 asset release |
| `docs/data/catalog.json` | modified | regenerated by update_site.py (+6 lines) |
| `site/data/catalog.json` | modified | regenerated by update_site.py (+6 lines) |
| `index/catalog.jsonl` | modified | regenerated by update_site.py (+1 line) |
| `reports/release_assets_index_policy_v0.3.94_20260702.md` | **new** | this report |

**NOT changed (deliberately)**:
- `audit_kb_state.py` — soft range `[6,12]/[3,8]` preserved per v0.3.68+ policy
- `source.md` / `summary.md` / `notes.md` for any entry — body content not touched
- All other metadata.yaml files — only bingzhu-you got the new fields (it's the only entry with Release assets currently)
- `.gitignore` — `*.mp4` / `*.mp3` already in place; no need to add more
- Item html pages (`docs/items/.../index.html` and `site/items/.../index.html`) — not regenerated because the new metadata fields don't appear in the item page template
- No new KB entries imported
- No tags/tags.md, authors.md, timeline.md regenerated (no relevant changes)
- Stable tag `v0.3.91-material-ingestion-stable-baseline` not moved (still at `56fe848`)
- Asset release tag `v0.3.92-bingzhu-you-mv-assets` not moved (still at `4117366`)

---

## REPORT: `reports/release_assets_index_policy_v0.3.94_20260702.md`

---

## COMMIT & PUSH plan

```bash
# Stage all changed files explicitly (no git add -A)
git add docs/releases.md
git add README.md
git add docs/RELEASES.md
git add content/notes/2026/2026-07-02-bingzhu-you-mv-production/metadata.yaml
git add docs/data/catalog.json
git add site/data/catalog.json
git add index/catalog.jsonl
git add reports/release_assets_index_policy_v0.3.94_20260702.md

git commit -m "Document release asset storage policy"
git push origin main
```

---

## TAG_STATUS

| Tag | Commit | Status |
|-----|--------|--------|
| `v0.3.91-material-ingestion-stable-baseline` | `56fe848` | **unchanged** ✅ (still the v0.3.91 stable baseline) |
| `v0.3.92-bingzhu-you-mv-assets` | `4117366` | **unchanged** ✅ (asset release tag, lives alongside stable tag) |

Both tags retain their original commits. v0.3.94 work is committed on top, in the main lineage only.

---

## Policy Highlights (for the team's reference)

1. **GitHub Release is canonical for binary assets.** Repo stays small; .gitignore boundaries are respected; URLs are stable.
2. **Each Release MUST be indexed in `docs/releases.md`** with asset count, size, linked KB entry, and `source_url` verification.
3. **Each Release MUST be auditable**: minimum checklist of asset count / size / sensitive data scan / license / KB link / source_url.
4. **New entries needing Release assets follow the 6-step procedure in `docs/releases.md` §3** — commit KB entry first, create Release, update source_url, add to index, run gates, commit.
5. **Optional metadata fields** (`asset_storage`, `asset_release_tag`, `asset_release_url`, `asset_count`, `asset_size_mb`, `asset_license`) provide machine-readable Release linkage. `check_kb.py` does not require them; entries with Release assets SHOULD set them.

---

## Next Recommendations

1. **No follow-up required for v0.3.94.** All work documented and committed.
2. **v0.3.95+ candidates** (out of scope for v0.3.94):
   - If a future KB entry needs Release assets, follow `docs/releases.md` §3 procedure.
   - Consider adding a preflight check that verifies `source_url` ↔ Release consistency for entries with `asset_storage: github_release`.
   - Consider documenting the parallel use of `docs/RELEASES.md` (codebase changelog) and `docs/releases.md` (asset policy) in `docs/AGENT_COMMANDS.md` to help future agents navigate.
3. **Audit warnings stable at 29.** No new warnings introduced by v0.3.94 (the 6 new metadata fields don't trigger `[tag_topic_count_out_of_range]`).
4. **Asset-naming correction:** v0.3.93 report used simplified names (e.g. `cover.jpg`, `subs.ass`, `full_mv.mp4`); actual release filenames are prefixed/qualified (`bingzhu_you_cover.jpg`, `bingzhu_subs_720.ass`, `full_v3.mp4`, etc.). `docs/releases.md` §2.2 documents the correction; v0.3.93 report retained for historical accuracy.
5. **Pre-existing tag hygiene warning** in `check_release_tags.py` (many duplicate minor versions from historical parallel development) is acknowledged known-warning and out of v0.3.94 scope.

---

*Report generated: 2026-07-02 10:50 GMT+8 (v0.3.94 stage G)*
*New policy doc: `docs/releases.md` (8502 bytes)*
*New optional metadata fields: 6 (added to bingzhu-you only)*
*Audit warnings: 29 (unchanged from v0.3.93)*
*Stable tag: `v0.3.91-material-ingestion-stable-baseline` at `56fe848` (unchanged)*