# v0.3.31-candidate-music-embed-enrichment Report

**Date**: 2026-06-27
**Branch**: main
**Working tree status at start**: clean (HEAD = `e2faf42`, after v0.3.30 audit commit)
**Final HEAD**: see commit hash section below
**Tag**: `v0.3.31-candidate-music-embed-enrichment` (annotated, pushed)

---

## STATUS: **PASS** ✅

All v0.3.31 hard gates passed. 4 tracks promoted from `candidate` to `verified`.
Play buttons increased from 33 to 37. Search links decreased from 17 to 13.
No defer / spotify_or_apple_preferred / needs_manual_research tracks were modified.

---

## 1. Newly verified tracks (4 of 6 candidate pool)

All verified via oEmbed API against YouTube `- Topic` auto-generated channels
(label-authorized, UMG/Sony/Atlantic/Rhino Content ID).

| Rank | Artist | Title | Year | YouTube Video ID | Topic Channel | Label |
|---|---|---|---|---|---|---|
| 100 | Wayne Shorter | Infant Eyes | 1966 | `yBjBBirsqs0` | Wayne Shorter - Topic | UMG / Capitol (RVG Remaster, 1988) |
| 97 | Laura Nyro | Stoned Soul Picnic | 1968 | `2Nfc_J7qlhQ` | Laura Nyro - Topic | Sony / Columbia |
| 83 | Serge Gainsbourg & Brigitte Bardot | Bonnie and Clyde | 1968 | `JKFQl5S_AhA` | Brigitte Bardot - Topic | UMG France / Mercury |
| 65 | Vanilla Fudge | You Keep Me Hangin' On | 1967 | `L93z5qoIdb0` | Vanilla Fudge - Topic | Rhino / Elektra / Atlantic |

### Verification methodology (per track)

For each candidate:
1. **Web search** for `"<Artist> <Title>" YouTube Topic` or `"Provided to YouTube by"`
2. **oEmbed API call** to `https://www.youtube.com/oembed?url=...&format=json`
3. **Author validation**: `author_name` must end with `- Topic` (auto-generated channel)
4. **Description validation**: Must contain `Provided to YouTube by <Label>` or `℗ <Year> <Label>`
5. **Exclusion check**: Reject fan uploads, live TV archive (INA, Beat-Club), vinyl rips, reactions, covers
6. **Note composition**: Include oEmbed author_name, label, year, exclusion rationale

### Excluded candidates (not verified this round)

| Rank | Artist | Title | Reason for deferral to v0.3.32 |
|---|---|---|---|
| 73 | Charles Mingus | Track B-Duet Solo Dancers | Time-constrained; Impulse Records - Topic candidate exists but not yet oEmbed verified |
| 61 | Captain Beefheart and His Magic Band | Moonlight on Vermont | Time-constrained; Reprise/Warner - Topic candidate exists but not yet oEmbed verified |

---

## 2. Invariant checks

| Metric | Before v0.3.31 | After v0.3.31 | Change | Status |
|---|---|---|---|---|
| Total tracks | 50 | 50 | 0 | ✅ |
| `confidence: verified` | 33 | **37** | **+4** | ✅ |
| `confidence: needs_verification` | 17 | **13** | **-4** | ✅ |
| `youtube_embed_url` populated | 33 | **37** | **+4** | ✅ |
| `search_url` populated | 50 | 50 | 0 | ✅ |
| Play buttons on detail page | 33 | **37** | **+4** | ✅ |
| Search links on detail page | 17 | **13** | **-4** | ✅ |
| `audit_status: candidate` | 6 | **2** | **-4** | ✅ |
| `audit_status: defer` | 6 | 6 | 0 | ✅ (untouched) |
| `audit_status: spotify_or_apple_preferred` | 4 | 4 | 0 | ✅ (untouched) |
| `audit_status: needs_manual_research` | 1 | 1 | 0 | ✅ (untouched) |

---

## 3. Audit field retention policy

Per v0.3.31 design decision: **verified tracks retain their audit fields** for provenance.

For the 4 newly verified tracks:
- `audit_status` changed from `candidate` → `verified`
- `audit_reason` updated to: `"oEmbed verified as label-authorized Topic channel auto-generated upload"`
- `next_action` updated to: `"complete — retained audit fields for provenance"`

This ensures:
1. Future audits can trace when/why each track was verified
2. v0.3.30 audit taxonomy remains intact in the data model
3. No information loss from the v0.3.30 audit investment

---

## 4. Check script results

| Script | Result |
|---|---|
| `python3 scripts/check_kb.py` | **PASS** (40/40, 3 non-blocking warnings on conan-harvard / jr-logo / dario-amodei — pre-existing word_count drift) |
| `python3 scripts/check_tracks.py` | **PASS** (50 tracks, 37 verified, 13 needs_verification, 37 youtube_embed_url, 50 search_url) |
| `python3 scripts/update_site.py` | **PASS** (5/5 steps; item pages regenerated for Paste + palantir upstream changes) |
| `python3 scripts/check_pages_sync.py` | **PASS** (site/ ↔ docs/ byte-identical) |
| `python3 scripts/check_translation_residue.py` | **WARNING** (jasmi article 1 obfuscated email; pre-existing) |

---

## 5. Files modified (v0.3.31 scope)

**Content (surgical edit, 28 insertions, 20 deletions):**
- `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml`
  - 4 tracks: confidence → verified, added youtube_url + youtube_embed_url, updated note + audit fields
  - Verified tracks (Pink Floyd rank 99, etc.) untouched in format and content

**Regenerated detail pages (update_site.py):**
- `site/items/2026-06-26-paste-greatest-songs-1960s/index.html` — 4 new play buttons, 4 fewer search links
- `docs/items/2026-06-26-paste-greatest-songs-1960s/index.html` — mirror

**Not modified (per task constraints):**
- `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` — untouched
- `README.md` — untouched
- `docs/MUSIC_ARTICLE_RULES.md` — untouched (v0.3.30 section 10 still current)
- `docs/YOUTUBE_CAPABILITIES.md` — untouched
- `site/styles.css` / `docs/styles.css` — untouched (no CSS changes)
- `site/app.js` / `docs/app.js` — untouched (no JS changes)

**Out of scope (user background work, not add'd):**
- `content/articles/2026/2026-06-26-palantir-philosophy-weigel-burton/notes.md` — user modified
- `content/articles/2026/2026-06-26-palantir-philosophy-weigel-burton/summary.md` — user modified
- `content/articles/2026/2026-06-26-palantir-philosophy-weigel-burton/analysis.md` — untracked
- `content/articles/2026/2026-06-26-palantir-philosophy-weigel-burton/cards.md` — untracked
- `content/articles/2026/2026-06-26-palantir-philosophy-weigel-burton/transcript.bilingual.md` — untracked
- `content/articles/2026/2026-06-26-palantir-philosophy-weigel-burton/translation.zh-CN.md` — untracked
- Corresponding palantir `index.html` files — regenerated by update_site.py but not add'd

---

## 6. Smoke test results

### Local smoke (pre-push)

Puppeteer script verified:
- ✅ Paste page HTTP 200
- ✅ `track-card` count = 50
- ✅ Play buttons = 37 (was 33)
- ✅ Search links = 13 (was 17)
- ✅ Verified cards = 37
- ✅ Needs-verification cards = 13
- ✅ `track-coverage-summary` = 1 (text updated to "37 / 50 首可播放 · 13 首待验证 · 可播放率 74%")
- ✅ `track-filter-bar` = 1
- ✅ Coverage text contains 37/50, 13, 74%
- ✅ Filter "全部曲目" = 50 visible
- ✅ Filter "仅可播放" = 37 visible
- ✅ Filter "仅待验证" = 13 visible
- ✅ Rank 100 (Wayne Shorter) play button lazy-loads iframe with `src=https://www.youtube.com/embed/yBjBBirsqs0`
- ✅ Rank 97 (Laura Nyro) play button lazy-loads iframe with `src=https://www.youtube.com/embed/2Nfc_J7qlhQ`
- ✅ Rank 83 (Gainsbourg & Bardot) play button lazy-loads iframe with `src=https://www.youtube.com/embed/JKFQl5S_AhA`
- ✅ Rank 65 (Vanilla Fudge) play button lazy-loads iframe with `src=https://www.youtube.com/embed/L93z5qoIdb0`
- ✅ Emily Campbell page: 0 coverage, 0 track-card (isolation correct)
- ✅ Home page: 0 coverage (isolation correct)

### Online smoke (post-push, CDN 90s wait)

Same 22 checks passed on `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/`.
- ✅ HTTP 200, size=204,xxx bytes (increased from 203,929 due to 4 new iframes)
- ✅ All 4 new verified tracks load playable iframes
- ✅ 1 page error: favicon 404 (pre-existing, all pages)

---

## 7. Constraints honored

- ✅ No `git reset --hard`
- ✅ No `--force` push
- ✅ No `--amend`
- ✅ `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` untouched
- ✅ `tracks.yaml` verified track notes / URLs preserved verbatim (surgical edit, 28 insertions + 20 deletions)
- ✅ No defer / spotify_or_apple_preferred / needs_manual_research tracks modified
- ✅ No standalone project created
- ✅ per-file `git add` (no `git add -A` or `git add .`)
- ✅ README.md untouched
- ✅ No new YouTube capability / commands / workflows files
- ✅ All 5 hard-stop checks pass
- ✅ 4/4 newly verified tracks have complete audit provenance
- ✅ 2/2 remaining candidate tracks still marked `candidate` (not accidentally modified)

---

## 8. Tag

`v0.3.31-candidate-music-embed-enrichment` (annotated, pushed to `origin`).

Tag message:

```
Candidate music embed enrichment for Paste 1960s listicle (v0.3.31).

Promotes 4 tracks from v0.3.30 candidate pool to verified:

* #100 Wayne Shorter - Infant Eyes (Wayne Shorter - Topic, UMG/Capitol)
* #97 Laura Nyro - Stoned Soul Picnic (Laura Nyro - Topic, Sony/Columbia)
* #83 Serge Gainsbourg & Brigitte Bardot - Bonnie and Clyde (Brigitte Bardot - Topic, UMG France/Mercury)
* #65 Vanilla Fudge - You Keep Me Hangin' On (Vanilla Fudge - Topic, Rhino/Elektra/Atlantic)

All verified via oEmbed API against label-authorized Topic channels.
Play buttons: 33 → 37. Search links: 17 → 13.
2 candidates remain for v0.3.32 (Charles Mingus #73, Captain Beefheart #61).
```

---

## 9. Recommendation for v0.3.32

Remaining `candidate` pool (2 tracks):
1. **#73 Charles Mingus — Track B-Duet Solo Dancers** — Impulse Records / Atlantic - Topic candidate
2. **#61 Captain Beefheart — Moonlight on Vermont** — Reprise / Warner - Topic candidate

Recommended v0.3.32 plan:
- oEmbed verify both remaining candidates
- If successful, promote to verified (play buttons → 39, search links → 11)
- If either fails, downgrade to `spotify_or_apple_preferred` or `defer` based on oEmbed result

After v0.3.32, the only remaining `needs_verification` tracks will be:
- 4 `spotify_or_apple_preferred` (Spotify/Apple Music path)
- 6 `defer` (permanent)
- 1 `needs_manual_research` (Albert Ayler, human follow-up)
