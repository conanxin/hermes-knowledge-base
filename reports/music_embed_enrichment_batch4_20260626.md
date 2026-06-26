# v0.3.24-music-embed-enrichment-batch-4 — Fourth batch of verified music embeds for Paste 1960s

**Date**: 2026-06-26
**Status**: PASS
**Tag**: v0.3.24-music-embed-enrichment-batch-4
**Commit hash**: (to be filled after commit)
**Article slug**: `2026-06-26-paste-greatest-songs-1960s`

---

## 1. STATUS

**PASS** — All 5 candidate tracks verified via canonical YouTube channels. Local puppeteer end-to-end test 10/10 PASS. All four hard-stop check scripts PASS or expected WARNING.

## 2. Scope

v0.3.24 continues the Paste 1960s listicle enrichment from the v0.3.23 baseline of 17 verified / 33 needs_verification. This batch adds 5 more verified tracks (10 / 17 + 5 = 22 verified), reducing the needs_verification pool to 28. Total verified rate is now 22/50 = 44%.

**Batches so far**:
- v0.3.19 (commit `787b4b8`): Initial music track links schema + `initTrackPlayers` in app.js
- v0.3.20 (commit `ee973a1`): Pilot — 2 verified
- v0.3.21 (commit `462811b` + smoke `2363a12`): Batch 2 — 8 more verified (10 total)
- v0.3.22 (commit `e1e1740` + report `82fd039`): Fix item-page music player script loading bug
- v0.3.23 (commit `f826dbf` + report `09f485c`): Batch 3 — 7 more verified (17 total)
- **v0.3.24 (this batch)**: Batch 4 — 5 more verified (22 total)

## 3. New verified tracks (5)

| Rank | Artist | Title | Year | YouTube ID | Channel | Note |
|---|---|---|---|---|---|---|
| 58 | The Cannonball Adderley Quintet | Mercy, Mercy, Mercy | 1966 | `y7FFLYXEOqA` | Cannonball Adderley Sextet - Topic (Capitol) | 1966 Capitol Records; from album *Mercy, Mercy, Mercy! - Live At "The Club"*; written by Joe Zawinul; Topic channel name is "Sextet" (Cannonball's performing unit on this recording) while Wikipedia refers to the group as "Quintet" - both refer to the same Cannonball Adderley-led ensemble |
| 70 | Tommy James & The Shondells | Crimson and Clover | 1969 | `q65x6jddc88` | RHINO (@rhino) | 1968 Roulette Records; from album *Crimson & Clover*; "Tommy James & The Shondells - Crimson and Clover (Official Audio)"; RHINO currently administers the Roulette Records catalog (Tommy James' original label) |
| 79 | Archie Bell & The Drells | Tighten Up | 1968 | `Kk1RCfV4zNM` | Archie Bell - Topic (Atlantic) | 1968 Atlantic Records; from album *Tighten Up*; "Tighten Up (Remastered)" |
| 85 | The Zombies | Care of Cell 44 | 1968 | `BveNwHGOjdc` | THE ZOMBIES - Topic | 1967 CBS/Date Records; from album *Odessey and Oracle*; "Care of Cell 44 (Mono Remastered)" |
| 93 | Ike & Tina Turner | River Deep – Mountain High | 1969 | `pWK7v0gIHLo` | Ike & Tina Turner - Topic (UMG) | 1966 Philles Records (US) / London (Europe); produced by Phil Spector; "Provided to YouTube by Universal Music Group" + "℗ 1966 UMG Recordings, Inc" |

**Pattern**: 4 of 5 use "Artist - Topic" / label-authorized channel (Atlantic, Capitol, UMG, RHINO/Roulette catalog), 1 uses RHINO's official artist channel.

## 4. Candidates considered but deferred (5+)

| Rank | Artist | Title | Reason for deferral |
|---|---|---|---|
| 54 | The Sonics | Strychnine | Same as v0.3.23 — Etiquette Records has no canonical YouTube channel. Searched exhaustively; no Topic, no official, no VEVO. All available uploads are fan channels. Continue deferring. |
| 56 | Harry Nilsson | Everybody's Talkin' | RCA Victor 1968. Searched but did not find a "Harry Nilsson - Topic" or RCA-official YouTube auto-generated audio entry in this session. The article and Wikipedia both reference the song but the available YouTube IDs in search results were fan-uploaded tribute / cover channels. Defer to a later batch when more time is available. |
| 63 | Loretta Lynn | Don't Come Home a Drinkin' (With Lovin' on Your Mind) | Decca 1966. Searched but did not find a verified "Loretta Lynn - Topic" or VEVO audio entry in this session. Wikipedia has no audio link. Defer. |
| 80 | Love | The Red Telephone | Elektra 1967. Searched but only fan-uploaded versions (38K-523K views) appear; no Topic or Rhino-rerelease audio in this session. Defer. |
| 87 | The Angels | My Boyfriend's Back | Mercury/Smash 1963. Searched but only fan / tribute channels appear (1980s compilations, girl-group compilations); no Topic. Defer. |
| 92 | Donovan | Epistle to Dippy | Pye/Epic 1966. Searched but did not find a verified Topic in this session. Defer. |

These deferrals are conservative — we verified each candidate's oembed channel before accepting. The next batch (v0.3.25) can return to these with additional search time or accept them with a "label-authorized lyric video" status.

## 5. Files changed (this commit)

| File | Change | Purpose |
|---|---|---|
| `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml` | +5 verified entries | Added youtube_url, youtube_embed_url, confidence=verified, note for 5 candidate tracks |
| `site/items/2026-06-26-paste-greatest-songs-1960s/index.html` | regenerated | update_site.py converted 5 needs_verification track-cards from search-link-only to play-button + youtube-link, with verification badge |
| `docs/items/2026-06-26-paste-greatest-songs-1960s/index.html` | regenerated | Mirror of site/ (per CLAUDE.md site/ ↔ docs/ byte-identical invariant) |

**Total**: 3 files, +X/-Y lines.

## 6. Local check results

| Script | Result | Notes |
|---|---|---|
| `python3 scripts/check_kb.py` | **PASS** | 38/38 records |
| `python3 scripts/check_tracks.py` | **PASS** | 50 tracks (22 verified, 28 needs_verification), 22 youtube_embed_url, 50 search_url |
| `python3 scripts/update_site.py` | **PASS** | 5/5 steps; 1 detail page regenerated |
| `python3 scripts/check_pages_sync.py` | **PASS** | site/ ↔ docs/ byte-identical |
| `python3 scripts/check_translation_residue.py` | **WARNING** | 1 email residue in 2026-06-25-jasmi article (unrelated to this task) |

## 7. Local puppeteer end-to-end test (10/10 PASS)

Run against `http://localhost:8765/items/2026-06-26-paste-greatest-songs-1960s/` (local http.server, no proxy needed) via headless Chromium:

| # | Test | Expected | Actual | Pass |
|---|---|---|---|---|
| 1 | Detail page HTTP 200 | 200 | 200 | ✅ |
| 2 | track-card = 50 | 50 | 50 | ✅ |
| 3 | play button = 22 | 22 | 22 | ✅ |
| 4 | search link = 28 | 28 | 28 | ✅ |
| 5 | initial iframe = 0 (lazy) | 0 | 0 | ✅ |
| 6 | Click #79 Archie Bell → iframe src | `https://www.youtube.com/embed/Kk1RCfV4zNM` | match | ✅ |
| 7 | Click #85 The Zombies → iframe src | `https://www.youtube.com/embed/BveNwHGOjdc` | match | ✅ |
| 8 | Click #93 Ike & Tina Turner → iframe src | `https://www.youtube.com/embed/pWK7v0gIHLo` | match | ✅ |
| 9 | Total iframes after 3 NEW clicks = 3 | 3 | 3 | ✅ |
| 10 | Click #74 Johnny Cash (existing v0.3.21) → still works | `https://www.youtube.com/embed/5WyLhwYFgmk` | match | ✅ |

## 8. Channel verification methodology

All 5 verified URLs were channel-checked via the YouTube oEmbed API (`https://www.youtube.com/oembed?url=...&format=json`) which returns the canonical `author_name` for each video. All match one of the accepted patterns documented in v0.3.21 (note for #62 The Temptations — VEVO + label-authorized lyric video):

- **Artist - Topic** (UMG / Atlantic / Capitol Content ID auto-generated) — preferred for canonical audio
- **Official artist / catalog label channel** (RHINO administers Roulette Records' catalog for Tommy James) — accepted when Topic is not available
- All other fan / compilation / radio channels were rejected. No cover / live / reaction / karaoke versions.

## 9. What's NOT in this commit

- `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` — not modified (per task constraint)
- `tracks.yaml` — only the 5 candidate entries were updated; no schema changes
- No new checks were added; the existing `check_tracks.py` accepted the new entries with `verified` confidence
- `README.md` / `docs/YOUTUBE_CAPABILITIES.md` / v0.3.22 YouTube capability documentation files — not touched (out of scope)
- The Sonics (Strychnine) — deferred (no canonical YouTube channel exists)
- Harry Nilsson, Loretta Lynn, Love Red Telephone, The Angels, Donovan — deferred (no verified canonical YouTube ID found in this session)

## 10. Verification artefacts

- Fix commit: (to be filled after commit)
- Commit message: `Add fourth batch of verified music embeds for Paste 1960s`
- Tag: `v0.3.24-music-embed-enrichment-batch-4` (annotated)
- GitHub Pages detail: https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/
- Test script: `/tmp/local_puppeteer_v324.cjs` (puppeteer 25.1.0 + Chromium)
- Local server: `python3 -m http.server 8765 -d site` (stopped after test)

## 11. Next steps

After this batch lands, 28 tracks remain in needs_verification. The remaining 6 deferred candidates (Harry Nilsson, Loretta Lynn, Love Red Telephone, The Angels, Donovan Epistle to Dippy, The Sonics) are likely addressable in v0.3.25 with additional search time. After that, the remaining 22 tracks are mostly:

- Jazz (Wayne Shorter, Eric Dolphy, Charles Mingus, Herbie Hancock, Bill Evans, Albert Ayler) — may have limited official YouTube presence
- Non-English (Os Mutantes, Jacques Brel, Jorge Ben) — may need Portuguese / French canonical sources
- Psychedelic (Vanilla Fudge, Captain Beefheart, Scott Walker, Blind Faith, Donovan Epistle, Led Zeppelin) — Atco and other labels
- Misc (Buffy Sainte-Marie, The Tammys, Midnight Movers, Ketty Lester) — obscure recordings

Recommended next batch (v0.3.25): target the 6 deferred candidates above. If any still cannot be verified after additional search effort, accept them with a "label-authorized lyric video" status (similar to The Temptations pattern) or leave them as needs_verification.
