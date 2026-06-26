# Music Embed Enrichment Batch 5 — v0.3.25

**STATUS: PASS**

## Overview

Fifth batch of verified YouTube embed enrichment for the Paste 1960s music long-list
article (`content/articles/2026/2026-06-26-paste-greatest-songs-1960s/`).

This batch addresses 5 previously-deferred tracks that the v0.3.22 / v0.3.23 / v0.3.24
batches could not resolve with high-confidence sources. All 5 new embeds were verified
via YouTube oEmbed API + cross-checked against official label/CID metadata. Notably, 4
of 5 came from `Topic` channels (UMG/Epic/Legacy/Rhino Content ID auto-generation) and
1 came from an artist-operated VEVO channel.

## Statistics

| Metric | v0.3.24 → v0.3.25 |
|---|---|
| Total tracks | 50 (unchanged) |
| Verified | 22 → **27** (+5) |
| Needs verification | 28 → **23** (-5) |
| Play buttons | 22 → **27** |
| Search links | 28 → **23** |
| youtube_embed_url count | 22 → **27** |
| verified rate | 44% → **54%** |

## New Verified Tracks (5)

| Rank | Artist | Title | Year | YouTube ID | Channel | Label |
|---|---|---|---|---|---|---|
| 56 | Harry Nilsson | Everybody's Talkin' | 1968 | `BFKDyVPkonc` | HarryNilssonVEVO | RCA Victor (UMG-operated VEVO) |
| 63 | Loretta Lynn | Don't Come Home a Drinkin' (With Lovin' on Your Mind) | 1966/67 | `Y40H3OoY3Io` | Loretta Lynn - Topic | Decca (UMG Content ID) |
| 80 | Love | The Red Telephone | 1967 | `m_j0qicK9mc` | Love - Topic | Elektra/Asylum (Rhino Content ID) |
| 82 | Merle Haggard | Mama Tried | 1968 | `PTV9LGPlbic` | Merle Haggard - Topic | Capitol Records Nashville (UMG Content ID) |
| 92 | Donovan | Epistle to Dippy | 1966/67 | `aKmjym6FQeI` | Donovan - Topic | Epic/Legacy (Sony/BMG Content ID) |

### Notes on the 5 verifications

- **#56 Harry Nilsson — `HarryNilssonVEVO`**: UMG-operated VEVO channel (verified
  via oEmbed API returning author_url `https://www.youtube.com/@HarryNilssonVEVO`).
  Description confirms title "Harry Nilsson - Everybody's Talkin' (From 'Midnight
  Cowboy') (Audio)". 1968 RCA Victor canonical single from the Midnight Cowboy
  soundtrack (composed by Fred Neil, performed by Harry Nilsson). Note: VEVO is a
  label-operated channel managed by Sony/UMG/Warner, not an artist-operated channel,
  but the @HarryNilssonVEVO handle is the only official YouTube presence for this
  catalog, making it the highest-confidence source available.

- **#63 Loretta Lynn — `Loretta Lynn - Topic`**: UMG Content ID auto-generated
  Topic channel. Title is "Don't Come Home A-Drinkin' (With Lovin' On Your Mind)
  (Single Version)". 1966/67 Decca Records canonical single recording. The song was
  written by Loretta Lynn and her sister Peggy Sue, recorded at Bradley's Barn on
  5 October 1966, and released as a single in November 1966; it reached #1 on the
  Billboard Hot Country Singles chart in February 1967. Note: paste-headline year
  1967 is the year it hit #1, but the studio recording was 1966.

- **#80 Love — `Love - Topic`**: Rhino/Elektra Content ID auto-generated Topic
  channel. Description confirms: "Provided to YouTube by Rhino/Elektra The Red
  Telephone (2015 Remaster) · Love Forever Changes ℗ 1967 Elektra/Asylum Records
  Producer, Vocals: Arthur Lee Producer: Bruce Botnick". 1967 Elektra Records
  canonical recording from album Forever Changes. Note: 2015 Remaster is the same
  1967 mix, just remastered — the 2015 release is the highest-quality YouTube-offered
  version of the original 1967 canonical recording.

- **#82 Merle Haggard — `Merle Haggard - Topic`**: UMG Content ID auto-generated
  Topic channel. Description confirms: "Provided to YouTube by Universal Music
  Group Mama Tried · Merle Haggard & The Strangers The Very Best Of Merle Haggard
  ℗ 1968 Capitol Records Nashville". 1968 Capitol Records Nashville canonical single
  recording. Note: the canonical artist credit is "Merle Haggard & The Strangers"
  but the Topic channel is named "Merle Haggard - Topic" (no Strangers suffix) —
  this is a UMG Content ID auto-generation convention; the recording is identical.

- **#92 Donovan — `Donovan - Topic`**: Epic/Legacy Content ID auto-generated
  Topic channel (Sony/BMG). Description confirms: "Provided to YouTube by
  Epic/Legacy Epistle To Dippy (Single Version) · Donovan Donovan's Greatest Hits
  ℗ Originally Released 1967. All rights reserved by SONY BMG". 1966/67 Epic
  Records (Columbia/CBS group) canonical single recording produced by Mickie Most.
  Note: the song was released as a non-LP single in 1967, hence the paste-headline
  year 1966 refers to the studio recording period; the single release was 1967.

## Deferred Tracks (Not in This Batch)

- #54 The Sonics — Strychnine (deferred again per user instruction: Etiquette Records
  is a small Seattle garage rock label with no online YouTube channel; the only
  YouTube uploads are fan rip/aggregate accounts. Keep as `needs_verification`.)

## Channel Verification Methodology

For all 5 new embeds, channel authenticity was verified using two methods:

1. **YouTube oEmbed API** (no browser, no proxy required) — returns
   `author_name` + `author_url` for any public YouTube video. Used to confirm
   the channel handle/name matches the artist or label.

2. **Cross-check against YouTube description metadata** — the Topic-channel
   auto-generated audio tracks include a `Provided to YouTube by [Label]` line
   in the description, e.g. "Provided to YouTube by Universal Music Group Mama
   Tried · Merle Haggard & The Strangers ... ℗ 1968 Capitol Records Nashville".
   This metadata is Copyright-Content-ID-mediated, so it is reliable.

## Smoke Test Results

### Local (http://127.0.0.1:8765)

- HTTP 200 ✅
- 50 track-cards ✅
- 27 play buttons ✅
- 23 search links ✅
- 5 new embed IDs found via `data-embed-url` attribute ✅
- 5 new clicks all create correct iframe `src` ✅
- 1 existing click (#74 Johnny Cash) still works ✅
- 1 non-verified check (#53 Jorge Ben) shows search link only, no play button ✅
- Puppeteer E2E: **12/12 PASS** (0 page errors aside from favicon 404)

### Online (https://conanxin.github.io)

- HTTP 200 ✅
- 50 track-cards / 27 play / 23 search ✅
- 5 new embed IDs found via `data-embed-url` ✅
- 5 new clicks + 1 existing (#74) all create correct iframe `src` ✅
- Puppeteer E2E: **12/12 PASS** (0 page errors aside from favicon 404)

## Check Scripts

| Script | Result |
|---|---|
| `check_kb.py` | PASS (38/38) |
| `check_tracks.py` | PASS (27 verified, 50 total) |
| `update_site.py` | PASS (5/5 steps) |
| `check_pages_sync.py` | PASS (site/ ↔ docs/ byte-identical) |
| `check_translation_residue.py` | WARNING (jasmi article 1 email, **unrelated**) |

## Files Modified

- `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml` (+5 verified entries)
- `site/items/2026-06-26-paste-greatest-songs-1960s/index.html` (derived page, 5 new play buttons)
- `docs/items/2026-06-26-paste-greatest-songs-1960s/index.html` (mirror, byte-identical to site/)

## Constraint Compliance

- ✅ Did not modify `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md`
- ✅ Did not modify `README.md` or unrelated reports
- ✅ Did not create standalone project
- ✅ Did not force push or amend or hard reset
- ✅ Per-file `git add` (no `-A` / `.`)
- ✅ All 5 new embeds are Topic or VEVO channels (not fan uploads / covers / lives /
  reactions / karaoke)
- ✅ Reported source includes "Not a cover/live/reaction/karaoke" in every `note`
- ✅ All 5 `youtube_embed_url` use `https://www.youtube.com/embed/<VIDEO_ID>` format
- ✅ Channel name vs artist name mismatches are explained in `note` (e.g.
  "Merle Haggard & The Strangers" canonical credit vs "Merle Haggard - Topic"
  channel name)

## Git

- **Commit (fix)**: `a4ad475`
- **Tag**: `v0.3.25-music-embed-enrichment-batch-5` → to be created next
- **Working tree**: clean
- **Branch**: `main`, up to date with `origin/main`
