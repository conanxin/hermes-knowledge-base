# v0.3.30-remaining-track-audit Report

**Date**: 2026-06-26
**Branch**: main
**Working tree status at start**: clean (HEAD = `4a759a0`, after v0.3.29 report commit)
**Final HEAD**: see commit hash section below
**Tag**: `v0.3.30-remaining-track-audit` (annotated, pushed)

---

## STATUS: **PASS** ✅

All v0.3.30 hard gates passed, no verified links changed, no source/translation touched.
17 needs_verification tracks each received `audit_status` / `audit_reason` / `next_action`
metadata; total working-tree diff is 118 insertions across 2 files (zero deletions).

---

## 1. The 17 audited tracks (full table)

All entries below are `confidence: needs_verification` tracks in
`content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml` (50 total, 33 verified,
17 needs_verification — unchanged from v0.3.29).

| Rank | Artist | Title | Year | audit_status | Reason (excerpt) | Next action |
|---|---|---|---|---|---|---|
| 100 | Wayne Shorter | Infant Eyes | 1966 | **candidate** | Blue Note 1964 recording; MusicBrainz ID 7530962f exists | v0.3.31: oEmbed 验证 Blue Note - Topic 或 Wayne Shorter - Topic |
| 97 | Laura Nyro | Stoned Soul Picnic | 1968 | **candidate** | Columbia/Sony 厂牌活跃 | v0.3.31: oEmbed 验证 Columbia Records - Topic 或 Laura Nyro - Topic |
| 94 | Blind Faith | Had to Cry Today | 1969 | **defer** | 仅有 Clapton 2010 Hyde Park live;无 studio 1969 官方 | 长期 defer;不硬填 live |
| 91 | Scott Walker | The Seventh Seal | 1969 | **defer** | Philips/4AD,Walker 2019 去世后官方松散;fan upload 主导 | 长期 defer;不硬填 fan / tribute |
| 87 | The Angels | My Boyfriend's Back | 1963 | **spotify_or_apple_preferred** | Smash/Motown;YouTube 官方少,UMG 曲库完整 | v0.3.31: 优先 Spotify / Apple Music 验证;YouTube 仅 fallback |
| 83 | Serge Gainsbourg & Brigitte Bardot | Bonnie and Clyde | 1968 | **candidate** | Philips/Universal France,法语区厂牌管理积极 | v0.3.31: oEmbed 验证 Serge Gainsbourg - Topic 或 Universal Music France - Topic |
| 81 | The Tammys | Egyptian Shumba | 1963 | **defer** | 极小厂牌 Scepter subsidiary;无官方 channel | 长期 defer |
| 77 | Buffy Sainte-Marie | Adam | 1967 | **defer** | Vanguard Records;Buffy 近年争议致官方管理保守 | 长期 defer;除非找到 Vanguard - Topic |
| 73 | Charles Mingus | Track B-Duet Solo Dancers | 1963 | **candidate** | Atlantic/Impulse!;经典曲 | v0.3.31: oEmbed 验证 Impulse Records - Topic 或 Charles Mingus - Topic |
| 72 | Os Mutantes | A Minha Menina | 1968 | **spotify_or_apple_preferred** | Polydor Brazil/UMG;oEmbed 验证 2 候选均为 fan (RioRecords/uaifree) | v0.3.31: 优先 Spotify / Apple Music 验证;YouTube 侧仅 fallback |
| 71 | Albert Ayler | Ghosts | 1964 | **needs_manual_research** | ESP-Disk 自由爵士;独立厂牌;受众小 | v0.3.31: 人工调研 ESP-Disk 官网 / Bandcamp / SoundCloud |
| 69 | Jacques Brel | J'Arrive | 1968 | **spotify_or_apple_preferred** | Barclay/Universal France;法语区经典 | v0.3.31: 优先 Spotify / Apple Music 验证;YouTube 侧仅 fallback |
| 65 | Vanilla Fudge | You Keep Me Hangin' On | 1967 | **candidate** | Atco/Atlantic | v0.3.31: oEmbed 验证 Atlantic Records - Topic 或 Vanilla Fudge - Topic |
| 64 | Midnight Movers | Medicated Goo | 1969 | **defer** | 极小厂牌 Eastbound;仅一张专辑 | 长期 defer |
| 61 | Captain Beefheart and His Magic Band | Moonlight on Vermont | 1969 | **candidate** | Straight/Reprise (Warner) | v0.3.31: oEmbed 验证 Reprise - Topic 或 Warner Records - Topic |
| 55 | Ketty Lester | Love Letters | 1961 | **spotify_or_apple_preferred** | Era/Dot;YouTube 官方少 | v0.3.31: 优先 Spotify / Apple Music 验证 |
| 54 | The Sonics | Strychnine | 1965 | **defer** | Etiquette Records (Seattle 小厂牌),1999 Norton reissue;无官方 channel;连续 4 轮 defer | 长期 defer;永久保留 search 链接 |

Full reason text (single-quote YAML strings) is stored in
`content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml` on each
needs_verification track as `audit_reason` field; full next-step text stored as `next_action`.

---

## 2. Audit distribution

| audit_status | Count | % of needs_verification |
|---|---|---|
| `candidate` | 6 | 35.3% |
| `spotify_or_apple_preferred` | 4 | 23.5% |
| `defer` | 6 | 35.3% |
| `needs_manual_research` | 1 | 5.9% |
| **Total** | **17** | **100%** |

---

## 3. Tracks suitable for v0.3.31 (candidate pool)

`candidate` 池(6 首,适合 v0.3.31 继续 oEmbed 验证):

1. **#100 Wayne Shorter — Infant Eyes** (Blue Note / Wayne Shorter - Topic)
2. **#97 Laura Nyro — Stoned Soul Picnic** (Columbia Records - Topic / Laura Nyro - Topic)
3. **#83 Serge Gainsbourg & Brigitte Bardot — Bonnie and Clyde** (Serge Gainsbourg - Topic / Universal Music France - Topic)
4. **#73 Charles Mingus — Track B-Duet Solo Dancers** (Impulse Records - Topic / Charles Mingus - Topic)
5. **#65 Vanilla Fudge — You Keep Me Hangin' On** (Atlantic Records - Topic / Vanilla Fudge - Topic)
6. **#61 Captain Beefheart and His Magic Band — Moonlight on Vermont** (Reprise Records - Topic / Warner Records - Topic)

These 6 are the highest-confidence next-shot list. Each has at least one well-known
label/Topic channel candidate and a clearly canonical song (not a deep cut, not a
live track, not a cover).

---

## 4. Tracks that may shift to spotify_or_apple_preferred in v0.3.31

`spotify_or_apple_preferred` 池(4 首,优先 Spotify / Apple Music 验证,YouTube 侧仅 fallback):

1. **#87 The Angels — My Boyfriend's Back** (UMG/Motown 完整曲库)
2. **#72 Os Mutantes — A Minha Menina** (UMG Brazil 完整曲库)
3. **#69 Jacques Brel — J'Arrive** (UMG France 完整曲库)
4. **#55 Ketty Lester — Love Letters** (UMG 完整曲库)

These are artists whose YouTube high-confidence sources are scarce but whose
streaming-platform presence (Spotify/Apple Music) is strong because their
publishing rights sit with major labels.

---

## 5. Tracks recommended for long-term defer

`defer` 池(6 首,长期 defer;不应再花 oEmbed 资源):

1. **#94 Blind Faith — Had to Cry Today** (Atco/Polydor;Studio 1969 无官方 channel)
2. **#91 Scott Walker — The Seventh Seal** (Philips/4AD;Walker 已故,官方松散)
3. **#81 The Tammys — Egyptian Shumba** (Scepter subsidiary,极小厂牌单曲)
4. **#77 Buffy Sainte-Marie — Adam** (Vanguard;近年身世争议,官方管理保守)
5. **#64 Midnight Movers — Medicated Goo** (Eastbound,极小厂牌,仅一张专辑)
6. **#54 The Sonics — Strychnine** (Etiquette Records / Norton reissue,Seattle 小厂牌,无 online 官方 channel;连续 4 轮已 defer)

---

## 6. Tracks needing manual research

`needs_manual_research` 池(1 首,需人工调研):

1. **#71 Albert Ayler — Ghosts** (ESP-Disk 自由爵士;独立厂牌;YouTube 高置信缺;建议人工调研 ESP-Disk 官网 / Bandcamp / SoundCloud;若无,降级 `defer`)

---

## 7. Verified count invariants

| Metric | Before v0.3.30 | After v0.3.30 | Change |
|---|---|---|---|
| Total tracks | 50 | 50 | 0 |
| `confidence: verified` | 33 | **33** | **0** ✅ |
| `confidence: needs_verification` | 17 | **17** | **0** ✅ |
| `youtube_embed_url` populated | 33 | **33** | **0** ✅ |
| `search_url` populated | 50 | **50** | **0** ✅ |
| play buttons on detail page | 33 | **33** | **0** ✅ |
| search links on detail page | 17 | **17** | **0** ✅ |
| `.track-card` count | 50 | **50** | **0** ✅ |

**No verified link was added, removed, or changed.** v0.3.30 is metadata-only.

---

## 8. Check script results

| Script | Result |
|---|---|
| `python3 scripts/check_kb.py` | **PASS** (40/40,3 non-blocking warnings on conan-harvard / jr-logo / dario-amodei — pre-existing word_count drift, unrelated to v0.3.30) |
| `python3 scripts/check_tracks.py` | **PASS** (50 tracks, 33 verified, 17 needs_verification, 33 youtube_embed_url, 50 search_url — invariants preserved) |
| `python3 scripts/update_site.py` | **PASS** (5/5 steps; no item-page re-render needed since tracks.yaml audit fields don't affect HTML output) |
| `python3 scripts/check_pages_sync.py` | **PASS** (site/ ↔ docs/ byte-identical for top-level + 40 item pages) |
| `python3 scripts/check_translation_residue.py` | **WARNING** (jasmi article 1 obfuscated email; pre-existing, unrelated to v0.3.30) |

---

## 9. Files modified (v0.3.30 scope, minimal & metadata-only)

**Content (audit metadata only, 51 insertions, 0 deletions):**
- `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml`
  - Added 3 fields × 17 tracks = 51 new lines
  - All `note:` fields preserved verbatim (verified tracks: 0 modifications)
  - All `youtube_url` / `youtube_embed_url` / `spotify_url` / `apple_music_url` / `search_url` /
    `confidence` values preserved verbatim

**Doc (taxonomy + 10.x subsection, 67 insertions, 0 deletions):**
- `docs/MUSIC_ARTICLE_RULES.md`
  - Added section 10: 剩余曲目审计分层 (v0.3.30+) — defines the 4 audit_status values
    (`candidate` / `spotify_or_apple_preferred` / `needs_manual_research` / `defer`),
    the 3 new tracks.yaml fields, prohibited behaviors, and the Paste audit distribution
    as a worked example

**Untouched (per task constraints):**
- `source.md` — not modified
- `translation.zh-CN.md` — not modified
- `summary.md` — not modified
- `notes.md` — not modified
- `README.md` — not modified
- `docs/YOUTUBE_CAPABILITIES.md` — not modified
- `docs/commands/README.md` — not modified
- `docs/workflows/README.md` — not modified
- `templates/prompts/youtube_kb_import_prompt.md` — not modified
- `site/styles.css` / `docs/styles.css` — not modified (no UI changes)
- `site/app.js` / `docs/app.js` — not modified (no JS changes)
- `site/items/*/index.html` / `docs/items/*/index.html` — not modified
  (audit fields are stored in tracks.yaml, not rendered in HTML)

**Not modified (out of v0.3.30 scope, user-managed):**
- All other 5 article/note/project/collection entries added by user in background
  (chatgptpro / noema / youtube-kb-import-command / youtube-link-preflight-failure-archive /
  youtube-video-brief-workflow) — all untracked content files exist but no v0.3.30 audit
  was applied to them

---

## 10. Tag

`v0.3.30-remaining-track-audit` (annotated, pushed to `origin`).

Tag message:

```
Remaining track audit for Paste 1960s listicle (v0.3.30).

Stratifies the 17 needs_verification tracks into 4 audit_status buckets
without adding any verified links:

* candidate: 6 tracks suitable for v0.3.31 oEmbed verification
* spotify_or_apple_preferred: 4 tracks better served by Spotify/Apple Music
* defer: 6 tracks with no realistic high-confidence YouTube source
* needs_manual_research: 1 track (Albert Ayler - Ghosts) for human follow-up

Adds 3 new tracks.yaml fields (audit_status, audit_reason, next_action)
on each needs_verification track. Verified tracks untouched (33/33).
Adds docs/MUSIC_ARTICLE_RULES.md section 10 to encode the taxonomy.
```

---

## 11. Constraints honored

- ✅ No `git reset --hard`
- ✅ No `--force` push
- ✅ No `--amend`
- ✅ `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` untouched
- ✅ `tracks.yaml` verified track notes / URLs preserved verbatim (51 insertions, 0 deletions)
- ✅ No new `youtube_embed_url` / `spotify_url` / `apple_music_url` added
- ✅ No track changed from `needs_verification` to `verified` (verified count remains 33)
- ✅ No standalone project created
- ✅ per-file `git add` (no `git add -A` or `git add .`)
- ✅ README.md untouched
- ✅ No new YouTube capability / commands / workflows files
- ✅ All 5 hard-stop checks pass (translation residue WARNING is pre-existing, jasmi)
- ✅ 17/17 needs_verification tracks have all 3 new audit fields
- ✅ 33/33 verified tracks do NOT have audit fields (correctly untouched)

---

## 12. Recommendation for v0.3.31

Based on this audit, the recommended v0.3.31 plan is:

1. **Pick N=3–5 from the `candidate` pool** and run oEmbed verification
2. **Pick 1–2 from the `spotify_or_apple_preferred` pool** to test the Spotify/Apple
   Music URL injection path (this requires adding `spotify_url` and/or `apple_music_url`
   rendering to the track card — a separate sub-task)
3. **Leave `defer` pool alone** — explicit decision to stop searching
4. **Leave `needs_manual_research` pool for human follow-up** (Albert Ayler)

A v0.3.31 sub-skill (`kb-music-audit-driven-embed`) should consume the new
`audit_status` field to know which tracks to attempt, rather than scanning all
17 needs_verification tracks blindly.
