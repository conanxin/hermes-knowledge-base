# v0.3.32-final-candidate-sweep-and-coverage-sync Report

**Date**: 2026-06-27
**Branch**: main
**Working tree status at start**: clean (HEAD = `8c59e3c`, after v0.3.31 + Palantir fix)
**Final HEAD**: see commit hash section below
**Tag**: `v0.3.32-final-candidate-sweep-and-coverage-sync` (annotated, pushed)

---

## STATUS: **PASS** ✅

All v0.3.32 hard gates passed. 1 track promoted from `candidate` to `verified`, 1 track downgraded from `candidate` to `defer`. Candidate pool is now **empty**. Metadata and summary synchronized to real counts.

---

## 1. Starting point (from v0.3.31)

| Metric | Value |
|---|---|
| Total tracks | 50 |
| Verified | 37 |
| Needs verification | 13 |
| Play buttons | 37 |
| Search links | 13 |
| Candidate pool | 2 |
| Defer | 6 |
| Spotify/Apple preferred | 4 |
| Needs manual research | 1 |

---

## 2. Final candidate processing

### #73 Charles Mingus — Track B-Duet Solo Dancers → **VERIFIED** ✅

- **YouTube Video ID**: `f9FzSSGTufQ`
- **Topic Channel**: `Charles Mingus - Topic`
- **Label**: The Verve Music Group (UMG)
- **Album**: *The Black Saint and the Sinner Lady* (1963)
- **oEmbed author_name**: `Charles Mingus - Topic`
- **Description**: "Provided to YouTube by Universal Music Group... ℗ 1963 The Verve Music Group"
- **Excluded**: `chris chris` (fan upload), vinyl rips
- **Verification date**: 2026-06-27

### #61 Captain Beefheart — Moonlight on Vermont → **DEFER** ❌

- **Reason**: No high-confidence studio-version source found for 1969 *Trout Mask Replica* original
- **Available sources**:
  - `yqS-c_euzeM` — `Captain Beefheart & His Magic Band - Topic` (Rhino/Warner) — **but 1978 live version**, not 1969 studio
  - `NZFG1yAxjdQ` — `Revanlation` (fan channel)
  - `Wdx_Dv9MfLE` — `Dusty Records` (fan/vinyl rip)
- **Original label**: Reprise Records / Straight Records (1969) — no active Topic channel
- **Decision**: Downgrade to `defer` per rule "live version unless原文明确是 live"
- **Audit reason**: "No studio-version Topic channel found; only 1978 live and fan uploads available. Original 1969 Reprise/Straight label has no active YouTube presence for this track."
- **Next action**: "permanent defer — no viable official source for 1969 studio version"

---

## 3. Final state

| Metric | Before | After | Change |
|---|---|---|---|
| Total tracks | 50 | 50 | 0 |
| Verified | 37 | **38** | **+1** ✅ |
| Needs verification | 13 | **12** | **-1** ✅ |
| Play buttons | 37 | **38** | **+1** ✅ |
| Search links | 13 | **12** | **-1** ✅ |
| Candidate pool | 2 | **0** | **-2** ✅ |
| Defer | 6 | **7** | +1 (Beefheart) |
| Spotify/Apple preferred | 4 | 4 | 0 ✅ |
| Needs manual research | 1 | 1 | 0 ✅ |
| Verified rate | 74% | **76%** | **+2%** ✅ |

---

## 4. Audit field retention

For the newly verified Mingus (#73):
- `audit_status`: `candidate` → `verified`
- `audit_reason`: Updated to "oEmbed verified as label-authorized Topic channel auto-generated upload (UMG/The Verve Music Group)"
- `next_action`: "complete — verified in v0.3.32"

For the deferred Beefheart (#61):
- `audit_status`: `candidate` → `defer`
- `audit_reason`: "No studio-version Topic channel found; only 1978 live and fan uploads available. Original 1969 Reprise/Straight label has no active YouTube presence for this track."
- `next_action`: "permanent defer — no viable official source for 1969 studio version"

---

## 5. Metadata synchronization

### metadata.yaml

Updated from v0.3.29 values (33/17/66%) to real v0.3.32 values:

```yaml
music_enrichment:
  enabled: true
  total_tracks: 50
  verified_tracks: 38
  pending_tracks: 12
  verified_rate: "76%"
  playable_filter: true
  last_verified_version: "v0.3.32-final-candidate-sweep-and-coverage-sync"
  status: "partial_verified"
```

### summary.md

Updated "播放增强状态" section:
- 版本引用: v0.3.29 → v0.3.32
- 可直接播放: 33 → 38
- 待验证链接: 17 → 12
- 可播放率: 66% → 76%
- 报告引用: 新增 v0.3.30/v0.3.31/v0.3.32 报告链接
- last_verified_version: v0.3.32-final-candidate-sweep-and-coverage-sync

---

## 6. Check script results

| Script | Result |
|---|---|
| `python3 scripts/check_kb.py` | **PASS** (40/40, 3 non-blocking warnings on conan-harvard / jr-logo / dario-amodei — pre-existing word_count drift) |
| `python3 scripts/check_tracks.py` | **PASS** (50 tracks, 38 verified, 12 needs_verification, 38 youtube_embed_url, 50 search_url) |
| `python3 scripts/update_site.py` | **PASS** (5/5 steps; regenerated detail pages + catalog + index) |
| `python3 scripts/check_pages_sync.py` | **PASS** (site/ ↔ docs/ byte-identical) |
| `python3 scripts/check_translation_residue.py` | **WARNING** (jasmi article 1 obfuscated email; pre-existing) |

---

## 7. Files modified

**Content (v0.3.32 scope):**
- `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml` — 20 lines (11 insertions, 9 deletions): Mingus verified, Beefheart defer
- `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/metadata.yaml` — 8 lines: 33→38, 17→12, 66%→76%, version update
- `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/summary.md` — 14 lines: 播放增强状态数字同步

**Regenerated (update_site.py):**
- `site/items/2026-06-26-paste-greatest-songs-1960s/index.html` — 1 new play button, 1 fewer search link, coverage text updated
- `docs/items/2026-06-26-paste-greatest-songs-1960s/index.html` — mirror
- `site/data/catalog.json` — music_enrichment fields updated
- `docs/data/catalog.json` — mirror
- `index/catalog.jsonl` — music_enrichment fields updated

**Not modified (per task constraints):**
- `source.md` / `translation.zh-CN.md` / `notes.md` — untouched
- `README.md` — untouched
- `docs/MUSIC_ARTICLE_RULES.md` — untouched
- `docs/YOUTUBE_CAPABILITIES.md` — untouched
- `site/styles.css` / `docs/styles.css` — untouched
- `site/app.js` / `docs/app.js` — untouched

**Out of scope (not add'd):**
- `reports/palantir_translation_render_fix_tag_20260626.md` — untracked, user background work

---

## 8. Local smoke test results

Puppeteer verified:
- ✅ Paste page HTTP 200
- ✅ `track-card` count = 50
- ✅ Play buttons = 38 (was 37)
- ✅ Search links = 12 (was 13)
- ✅ Verified cards = 38
- ✅ Needs-verification cards = 12
- ✅ `track-coverage-summary` text: "38 / 50 首可播放 · 12 首待验证 · 可播放率 76%"
- ✅ `track-filter-bar` = 1
- ✅ Filter "全部曲目" = 50 visible
- ✅ Filter "仅可播放" = 38 visible
- ✅ Filter "仅待验证" = 12 visible
- ✅ Rank 73 (Charles Mingus) play button lazy-loads iframe with `src=https://www.youtube.com/embed/f9FzSSGTufQ`
- ✅ Rank 61 (Captain Beefheart) shows search link, no play button (correct — defer)
- ✅ Emily Campbell page: 0 coverage, 0 track-card (isolation correct)
- ✅ Home page: 0 coverage (isolation correct)

---

## 9. Online smoke test results

Post-push CDN verification:
- ✅ `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/` HTTP 200
- ✅ Coverage summary: "38 / 50 首可播放 · 12 首待验证 · 可播放率 76%"
- ✅ Filter counts correct
- ✅ Rank 73 Mingus iframe loads
- ✅ Rank 61 Beefheart no iframe, search link present
- ✅ 1 page error: favicon 404 (pre-existing)

---

## 10. Constraints honored

- ✅ No `git reset --hard`
- ✅ No `--force` push
- ✅ No `--amend`
- ✅ `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` — only summary.md modified (required by task)
- ✅ `tracks.yaml` verified track notes / URLs preserved verbatim (surgical edit)
- ✅ No defer / spotify_or_apple_preferred / needs_manual_research tracks accidentally modified (only Beefheart intentionally changed)
- ✅ No standalone project created
- ✅ per-file `git add` (no `git add -A` or `git add .`)
- ✅ README.md untouched
- ✅ All 5 hard-stop checks pass
- ✅ Candidate pool is empty (0)
- ✅ Metadata and summary synchronized to real counts

---

## 11. Tag

`v0.3.32-final-candidate-sweep-and-coverage-sync` (annotated, pushed to `origin`).

Tag message:

```
Finalize Paste 1960s candidate sweep and sync music coverage.

Promotes 1 track from v0.3.31 candidate pool to verified:
* #73 Charles Mingus - Track B-Duet Solo Dancers (Charles Mingus - Topic, UMG/Verve)

Downgrades 1 track from candidate to defer:
* #61 Captain Beefheart - Moonlight on Vermont (no studio-version Topic channel; only 1978 live and fan sources)

Candidate pool is now empty.
Play buttons: 37 -> 38. Search links: 13 -> 12. Verified rate: 74% -> 76%.
Metadata and summary synchronized to real counts.
```

---

## 12. Remaining work after v0.3.32

The only remaining `needs_verification` tracks (12 total):

| audit_status | Count | Tracks | Path forward |
|---|---|---|---|
| `defer` | 7 | #94, #91, #81, #77, #64, #54, #61 | Permanent — no viable official sources |
| `spotify_or_apple_preferred` | 4 | #87, #72, #69, #55 | Spotify/Apple Music URL injection (future sub-task) |
| `needs_manual_research` | 1 | #71 Albert Ayler | Human follow-up required |

**No more candidate tracks remain.** The Paste 1960s music embed enrichment is complete for the YouTube/Topic channel path.

---

## 13. Links

- **Commit**: https://github.com/conanxin/hermes-knowledge-base/commit/[COMMIT_HASH]
- **Tag**: https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.32-final-candidate-sweep-and-coverage-sync
- **GitHub Pages Detail Page**: https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/
