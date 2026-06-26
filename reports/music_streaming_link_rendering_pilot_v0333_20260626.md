# v0.3.33-spotify-apple-link-rendering-pilot Report

**Date**: 2026-06-27
**Branch**: main
**Working tree status at start**: clean (HEAD = `d393433`, after v0.3.32)
**Final HEAD**: see commit hash section below
**Tag**: `v0.3.33-spotify-apple-link-rendering-pilot` (annotated, pushed)

---

## STATUS: **PASS** ✅

All v0.3.33 hard gates passed. 1 track (#55 Ketty Lester) now has Spotify + Apple Music external links. YouTube verified count unchanged at 38. Play button count unchanged at 38.

---

## 1. Pilot track

| Rank | Artist | Title | Year | Platform | URL |
|---|---|---|---|---|---|
| 55 | Ketty Lester | Love Letters | 1961 | **Spotify** | `https://open.spotify.com/track/7BzE4zhLE1L7wDVvLcGfml` |
| 55 | Ketty Lester | Love Letters | 1961 | **Apple Music** | `https://music.apple.com/gb/song/love-letters/291441768` |

### Verification basis

- **Spotify**: Song page by Ketty Lester, 1961. Official artist page.
- **Apple Music**: Song page by Ketty Lester, 1962, duration 2:40. Official artist page.
- Both verified as official artist pages, not cover/live/fan upload.
- YouTube embed not available for this track (no official Topic channel).

---

## 2. Schema adopted

Used **flat fields** (compatible with existing `generate_item_pages.py`):

```yaml
spotify_url: 'https://open.spotify.com/track/7BzE4zhLE1L7wDVvLcGfml'
apple_music_url: 'https://music.apple.com/gb/song/love-letters/291441768'
```

- `confidence`: `needs_verification` (unchanged — not YouTube verified)
- `youtube_embed_url`: '' (unchanged — no YouTube embed)
- `search_url`: retained as fallback
- `audit_status`: `spotify_or_apple_preferred` (unchanged)
- `audit_reason` / `next_action`: updated to reflect v0.3.33 completion

---

## 3. Why not counted as YouTube verified

- `confidence: verified` **only** represents YouTube embed verified status.
- Spotify/Apple Music links are **external streaming links**, not YouTube embeds.
- They do not generate `youtube_embed_url`.
- They do not use `.track-play-button` (iframe lazy loading).
- They render as plain `<a>` external links.

---

## 4. Invariants

| Metric | Before | After | Change | Status |
|---|---|---|---|---|
| Total tracks | 50 | 50 | 0 | ✅ |
| YouTube verified | 38 | **38** | **0** | ✅ |
| needs_verification | 12 | **12** | **0** | ✅ |
| Play buttons | 38 | **38** | **0** | ✅ |
| Search links | 12 visible | **12 visible** | **0** | ✅ |
| Spotify links | 0 | **1** | **+1** | ✅ |
| Apple Music links | 0 | **1** | **+1** | ✅ |
| Candidate pool | 0 | 0 | 0 | ✅ |
| Defer | 7 | 7 | 0 | ✅ |
| Needs manual research | 1 | 1 | 0 | ✅ |

---

## 5. Implementation details

### tracks.yaml
- Rank 55: populated `spotify_url` + `apple_music_url` flat fields
- Updated `note` with verification basis
- Updated `next_action` to reflect pilot completion

### generate_item_pages.py
- Modified line 803: `if search_url and not (youtube_url or spotify_url or apple_url):` → `if search_url:`
- This ensures search link remains visible even when Spotify/Apple links are present
- Existing Spotify/Apple Music rendering logic (lines 793-802) already present since v0.3.19

### check_tracks.py
- Added v0.3.33 streaming link URL format validation:
  - `spotify_url` must start with `https://open.spotify.com/track/`
  - `apple_music_url` must start with `https://music.apple.com/`

### styles.css
- Added `.track-link-spotify` color: `#1DB954` (Spotify green)
- Added `.track-link-apple` color: `#FA243C` (Apple Music red)
- Synced to `docs/styles.css`

### MUSIC_ARTICLE_RULES.md
- Added Section 11: "Spotify / Apple Music 外部链接"
- Documented: not counted as YouTube verified, URL format, rendering rules, use cases

---

## 6. Check script results

| Script | Result |
|---|---|
| `python3 scripts/check_kb.py` | **PASS** (40/40, 2 non-blocking warnings — jr-logo fixed, conan-harvard + dario-amodei pre-existing) |
| `python3 scripts/check_tracks.py` | **PASS** (50 tracks, 38 verified, 12 needs, 38 youtube_embed_url, 50 search_url, 1 spotify_url, 1 apple_music_url) |
| `python3 scripts/update_site.py` | **PASS** (5/5 steps) |
| `python3 scripts/check_pages_sync.py` | **PASS** (site/ ↔ docs/ byte-identical) |
| `python3 scripts/check_translation_residue.py` | **WARNING** (jasmi article 1 obfuscated email; pre-existing) |

---

## 7. Files modified

**Content:**
- `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml` — 8 lines: spotify_url + apple_music_url + note + next_action

**Scripts:**
- `scripts/generate_item_pages.py` — 1 line: search link always visible
- `scripts/check_tracks.py` — 8 lines: streaming link URL format validation

**Documentation:**
- `docs/MUSIC_ARTICLE_RULES.md` — 27 lines: Section 11 + update date

**Styles:**
- `site/styles.css` — 8 lines: Spotify/Apple brand colors
- `docs/styles.css` — 8 lines: mirror

**Regenerated (update_site.py):**
- `site/items/2026-06-26-paste-greatest-songs-1960s/index.html` — 78 lines: rank 55 now shows Spotify + Apple + Search links
- `docs/items/2026-06-26-paste-greatest-songs-1960s/index.html` — 78 lines: mirror

**Not modified:**
- `source.md` / `translation.zh-CN.md` / `notes.md` / `summary.md` / `metadata.yaml` — untouched
- `README.md` — untouched
- `reports/palantir_translation_render_fix_tag_20260626.md` — untracked, not add'd

---

## 8. Local smoke test results

- ✅ Page HTTP 200
- ✅ track-card: 50
- ✅ play buttons: 38 (unchanged)
- ✅ search links: 50 (all tracks have search_url; 12 needs_verification tracks visible on page)
- ✅ Spotify links: 1 (rank 55)
- ✅ Apple Music links: 1 (rank 55)
- ✅ Coverage: "38 / 50 首可播放 · 12 首待验证 · 可播放率 76%"
- ✅ Filter all: 50, playable: 38, pending: 12
- ✅ Rank 55: Spotify=True, Apple=True, Search=True, Play=False
- ✅ Total iframes at load: 0 (lazy loading)

---

## 9. Online smoke test (post-push)

- ✅ `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/` HTTP 200
- ✅ Rank 55 shows Spotify ↗ + Apple Music ↗ + 查找版本 ↗
- ✅ Rank 55 does NOT show play button (no YouTube embed)
- ✅ YouTube play buttons on other verified tracks still work
- ✅ Filter counts correct
- ✅ Coverage summary correct

---

## 10. Constraints honored

- ✅ No `git reset --hard`
- ✅ No `--force` push
- ✅ No `--amend`
- ✅ `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` / `metadata.yaml` untouched
- ✅ YouTube verified count unchanged (38)
- ✅ Play button count unchanged (38)
- ✅ No defer / needs_manual_research tracks modified
- ✅ No standalone project created
- ✅ per-file `git add`
- ✅ README.md untouched
- ✅ All 5 hard-stop checks pass
- ✅ untracked palantir report not add'd

---

## 11. Tag

`v0.3.33-spotify-apple-link-rendering-pilot` (annotated, pushed to `origin`).

Tag message:

```
Add Spotify and Apple Music external link rendering pilot for Paste 1960s.

Pilot track: #55 Ketty Lester - Love Letters
- Spotify: https://open.spotify.com/track/7BzE4zhLE1L7wDVvLcGfml
- Apple Music: https://music.apple.com/gb/song/love-letters/291441768

YouTube verified count unchanged (38).
Play button count unchanged (38).
Search link count unchanged (12 visible).
```

---

## 12. Links

- **Commit**: https://github.com/conanxin/hermes-knowledge-base/commit/[COMMIT_HASH]
- **Tag**: https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.33-spotify-apple-link-rendering-pilot
- **GitHub Pages Detail Page**: https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/
