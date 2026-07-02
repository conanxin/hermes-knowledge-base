# Release Assets Policy

This document defines how **large multimedia assets** associated with KB entries are stored, versioned, and referenced. It complements the existing [`docs/RELEASES.md`](RELEASES.md), which tracks the **release-line history** of the repository itself; this file is the index and policy for **content assets that live outside the git repo**.

---

## 1. Policy

### 1.1 What goes where

| Asset class | Goes in | Why |
|-------------|---------|-----|
| Lightweight text (lyrics, transcripts, subtitles, README) | **git repo** | Small, diffable, long-term archival |
| Cover image (JPG/PNG, ≤ 1 MB) | **git repo** (case-by-case) | Small enough to commit; serves as canonical preview |
| Audio (MP3/WAV, any size) | **GitHub Release** | `.gitignore` blocks `*.mp3`; releases are stable storage |
| Video (MP4, any size) | **GitHub Release** | `.gitignore` blocks `*.mp4`; 100 MB GitHub file cap; releases are stable storage |
| Archives (ZIP, tar.gz) | **GitHub Release** | `.gitignore` blocks `*.zip`/`*.tar.gz`; releases are stable storage |
| PDFs (any size) | **GitHub Release** | `.gitignore` blocks `*.pdf`; releases are stable storage |

### 1.2 Why GitHub Release (not git, not GitHub Pages)

- **`.gitignore` blocks the asset classes** above; committing them is impossible without an explicit `git add -f` (which we forbid).
- **GitHub Pages serves from the git tree** — assets hidden by `.gitignore` would 404.
- **GitHub Releases are first-class**: each release has a stable tag URL, supports versioning, and is the canonical home for binary artifacts.
- **Repo history stays small**: 35 MB of multimedia would bloat every clone, every CI run, every `git fetch`.
- **License tracking**: each Release notes ownership and license; the metadata link is verifiable.

### 1.3 What goes in the repo (mandatory)

For every entry that uses Release assets, the git repo MUST contain:

1. `metadata.yaml` with `source_url` pointing to the **Release tag URL** (not a download URL)
2. `source.md` describing the asset set and how the entry was produced
3. `summary.md` and `notes.md` with the textual content of the entry
4. A row in `docs/releases.md` (this file) linking Release ↔ KB entry

### 1.4 What the Release MUST contain

- A descriptive release name (e.g. "v0.3.92 — 秉烛游 MV 素材包")
- Body text explaining what the assets are and why they're on the Release
- Per-asset labels matching the logical structure (e.g. `clips/`, `segments/`, `full_mv.mp4`)
- License / ownership note

### 1.5 Naming convention

- Release tag: `vX.Y.Z-<slug>-assets` (e.g. `v0.3.92-bingzhu-you-mv-assets`)
- Asset filenames inside the release: use a short, descriptive name; group with subfolders (`clips/`, `segments/`, etc.) when applicable
- KB entry slug: `YYYY-MM-DD-<slug>` (unchanged from existing convention)

### 1.6 Minimum audit on every Release

Before opening or updating a Release, verify:

- [ ] Asset count recorded
- [ ] Total size recorded
- [ ] Sensitive data scan (no tokens, keys, PII, internal paths)
- [ ] License / ownership note present
- [ ] KB entry linked from this index
- [ ] `source_url` in metadata points to the Release tag URL (not a download URL)

---

## 2. Release Assets Index

### 2.1 Active releases

| Release tag | Created | Total size | Asset count | Linked KB entry | `source_url` points to release? |
|-------------|---------|------------|-------------|------------------|----------------------------------|
| [`v0.3.92-bingzhu-you-mv-assets`](https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.92-bingzhu-you-mv-assets) | 2026-07-02 | 34.71 MB | 22 | [`2026-07-02-bingzhu-you-mv-production`](https://github.com/conanxin/hermes-knowledge-base/tree/main/content/notes/2026/2026-07-02-bingzhu-you-mv-production) | ✅ yes |

### 2.2 v0.3.92-bingzhu-you-mv-assets · 秉烛游 MV 素材包

- **Release URL**: <https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.92-bingzhu-you-mv-assets>
- **Tag commit in repo**: `4117366` (`v0.3.92-bingzhu-you-mv-assets` → `Clean up KB audit warnings (37 → 29)`)
- **KB entry slug**: `2026-07-02-bingzhu-you-mv-production`
- **KB entry path**: `content/notes/2026/2026-07-02-bingzhu-you-mv-production/`
- **KB entry status**: `active`
- **Asset count**: 22
- **Total size**: 34.71 MB (36,395,928 bytes)
- **License**: CC BY-NC 4.0 (lyrics user-authored; audio/video AI-generated)

#### Asset inventory

| # | Name | Size | Type | Role |
|---|------|------|------|------|
| 1 | `A_scholar_lifts_candle.mp4` | 703 KB | video/mp4 | Raw clip A — scholar lifts candle (Telegram segment 2 raw material) |
| 2 | `bingzhu_subs_720.ass` | 2.6 KB | text/x-ssa | Subtitle source (ASS, 720×720) |
| 3 | `bingzhu_you.mp3` | 3.95 MB | audio/mpeg | Full 2:09 audio (256 kbps) |
| 4 | `bingzhu_you_cover.jpg` | 342 KB | image/jpeg | Cover image (1024×1024) |
| 5 | `bingzhu_you_lyrics.txt` | 1.5 KB | text/plain | Lyrics source |
| 6 | `B_dance_over_city.mp4` | 2.21 MB | video/mp4 | Raw clip B — dance over city |
| 7 | `C_golden_rain.mp4` | 3.65 MB | video/mp4 | Raw clip C — golden rain |
| 8 | `D_walks_into_light.mp4` | 817 KB | video/mp4 | Raw clip D — walks into light |
| 9 | `full_v3.mp4` | 13.37 MB | video/mp4 | Full 2:09 MV (720×720, with intro/subtitles/outro, version 3) |
| 10 | `seg_01.mp4` | 400 KB | video/mp4 | Telegram segment 1 (intro) |
| 11 | `seg_02_small.mp4` | 666 KB | video/mp4 | Telegram segment 2 (small variant) |
| 12 | `seg_03.mp4` | 349 KB | video/mp4 | Telegram segment 3 |
| 13 | `seg_04.mp4` | 1.20 MB | video/mp4 | Telegram segment 4 |
| 14 | `seg_05.mp4` | 561 KB | video/mp4 | Telegram segment 5 |
| 15 | `seg_06.mp4` | 966 KB | video/mp4 | Telegram segment 6 |
| 16 | `seg_07.mp4` | 837 KB | video/mp4 | Telegram segment 7 |
| 17 | `seg_08.mp4` | 776 KB | video/mp4 | Telegram segment 8 |
| 18 | `seg_09.mp4` | 1.00 MB | video/mp4 | Telegram segment 9 |
| 19 | `seg_10.mp4` | 475 KB | video/mp4 | Telegram segment 10 |
| 20 | `seg_11.mp4` | 1.28 MB | video/mp4 | Telegram segment 11 |
| 21 | `seg_12.mp4` | 367 KB | video/mp4 | Telegram segment 12 |
| 22 | `seg_13.mp4` | 972 KB | video/mp4 | Telegram segment 13 |

#### URL patterns

- Release index: `https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.92-bingzhu-you-mv-assets`
- Asset downloads: `https://github.com/conanxin/hermes-knowledge-base/releases/download/v0.3.92-bingzhu-you-mv-assets/<asset-name>`

#### Asset name correction (v0.3.93 → v0.3.94)

The v0.3.93 report used simplified asset names (e.g. `cover.jpg`, `subs.ass`, `full_mv.mp4`). The actual filenames on the Release are:

- `cover.jpg` → `bingzhu_you_cover.jpg`
- `subs.ass` → `bingzhu_subs_720.ass`
- `lyrics.txt` → `bingzhu_you_lyrics.txt`
- `audio.mp3` → `bingzhu_you.mp3`
- `full_mv.mp4` → `full_v3.mp4`

This file (`docs/releases.md`) is the corrected, authoritative index. The v0.3.93 report's naming is kept for historical accuracy.

---

## 3. Procedure for Future Release-Backed Entries

When importing a new KB entry that needs Release assets:

1. **Commit KB entry first** (`metadata.yaml` + `source.md` + `summary.md` + `notes.md`) with `source_url` placeholder (e.g. `https://github.com/conanxin/hermes-knowledge-base/releases/tag/vX.Y.Z-<slug>-assets`)
2. **Create GitHub Release** via `gh release create`:
   ```bash
   gh release create vX.Y.Z-<slug>-assets \
       ./local/path/to/asset1.mp4 \
       ./local/path/to/asset2.jpg \
       ./local/path/to/lyrics.txt \
       --title "vX.Y.Z — <entry title> 素材包" \
       --notes "<release body describing assets, license, KB entry link>"
   ```
3. **Update KB entry `source_url`** to the actual Release tag URL (no change needed if placeholder was right)
4. **Add a row to §2.1** of this file with the new Release info
5. **Run all release gates** to confirm no regression
6. **Commit** the updated `docs/releases.md` + any regenerated `index/` files

---

## 4. Why This Document Lives in `docs/` (not `RELEASES.md`)

- `docs/RELEASES.md` tracks the **release history of the repository itself** (v0.1.0 → v0.3.94, capability lines, etc.). It's a chronological changelog of the codebase.
- `docs/releases.md` (this file) tracks **content assets that live outside the repo** — the policy and index for Releases that store multimedia.

Splitting them keeps each file focused: the codebase changelog stays narrow, the asset policy stays comprehensive.

---

*Policy established: 2026-07-02 (v0.3.94)*
*First Release indexed: `v0.3.92-bingzhu-you-mv-assets` (2026-07-02)*