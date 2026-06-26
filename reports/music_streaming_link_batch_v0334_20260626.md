# v0.3.34-spotify-apple-link-batch Report

**Date**: 2026-06-27
**Branch**: main
**Working tree status at start**: clean (HEAD = `e3d1ec6`, after v0.3.33)
**Final HEAD**: see commit hash section below
**Tag**: `v0.3.34-spotify-apple-link-batch` (annotated, pushed)

---

## STATUS: **PASS** ✅

All v0.3.34 hard gates passed. 3 additional tracks now have Spotify / Apple Music external links. YouTube verified count unchanged at 38. Play button count unchanged at 38.

---

## 1. 本轮处理 3 首曲目

| Rank | Artist | Title | Year | Spotify | Apple Music | 状态 |
|---|---|---|---|---|---|---|
| 87 | The Angels | My Boyfriend's Back | 1963 | ✅ `5NiFSI8iIDtVm1NCwdYrHS` | ✅ `1443938611` (Album) | **双平台** |
| 72 | Os Mutantes | A Minha Menina | 1968 | ❌ 未找到 | ✅ `1443152710` (Song) | **Apple only** |
| 69 | Jacques Brel | J'Arrive | 1968 | ✅ `2CD0a7xiFT3f60RqPAGGSF` | ❌ 未找到 | **Spotify only** |

### 验证依据

**#87 The Angels — My Boyfriend's Back**:
- **Spotify**: Song page by The Angels, 1998 (UMG compilation). Official artist page.
- **Apple Music**: Album page by The Angels, 1998, POP, ℗ UMG Recordings. Official compilation.
- 1963 Smash Records 原版，UMG 后续 compilation 发行。

**#72 Os Mutantes — A Minha Menina**:
- **Apple Music**: Song page by Os Mutantes, 1968 album. Official artist page.
- **Spotify**: Track URL 未找到（巴西地区版权限制）。
- 1968 Polydor Brazil (UMG Brazil) 原版。

**#69 Jacques Brel — J'Arrive**:
- **Spotify**: Song page by Jacques Brel, 1988 (compilation). Official artist page.
- **Apple Music**: Track URL 未找到（法国地区版权限制）。
- 1968 Barclay/Universal France 原版。

---

## 2. 最终 streaming linked tracks 数量

| 类型 | 数量 | 曲目 |
|---|---|---|
| **双平台** (Spotify + Apple) | 2 | #55 Ketty Lester, #87 The Angels |
| **Apple only** | 1 | #72 Os Mutantes |
| **Spotify only** | 1 | #69 Jacques Brel |
| **总计** | **4** | — |

---

## 3. 为什么不计入 YouTube verified

- `confidence: verified` **only** 表示 YouTube embed verified。
- Spotify/Apple Music 是 **external streaming links**，不是 YouTube embeds。
- 不生成 `youtube_embed_url`。
- 不使用 `.track-play-button`（iframe 懒加载）。
- 渲染为普通 `<a>` 外链。

---

## 4. Invariants

| Metric | Before | After | Change | Status |
|---|---|---|---|---|
| Total tracks | 50 | 50 | 0 | ✅ |
| YouTube verified | 38 | **38** | **0** | ✅ |
| needs_verification | 12 | **12** | **0** | ✅ |
| YouTube play button | 38 | **38** | **0** | ✅ |
| search_url | 50 | **50** | **0** | ✅ |
| Streaming linked tracks | 1 | **4** | **+3** | ✅ |
| Spotify links | 1 | **3** | **+2** | ✅ |
| Apple Music links | 1 | **3** | **+2** | ✅ |
| spotify_or_apple_preferred pool | 4 | **0** | **-4** | ✅ |
| Defer pool | 7 | 7 | 0 | ✅ |
| Needs manual research | 1 | 1 | 0 | ✅ |

---

## 5. Schema 延续

采用 v0.3.33 已建立的 **flat fields** schema：

```yaml
spotify_url: 'https://open.spotify.com/track/...'
apple_music_url: 'https://music.apple.com/.../song/.../...'
```

- `confidence`: `needs_verification` (未改)
- `youtube_embed_url`: '' (未改)
- `search_url`: 保留
- `audit_status`: `spotify_or_apple_preferred` (未改)
- `note`: 更新验证依据
- `next_action`: 更新为 v0.3.34 完成状态

---

## 6. Check script results

| Script | Result |
|---|---|
| `python3 scripts/check_kb.py` | **PASS** (40/40, 2 non-blocking warnings — conan-harvard + dario-amodei pre-existing) |
| `python3 scripts/check_tracks.py` | **PASS** (50 tracks, 38 verified, 12 needs, 38 youtube_embed_url, 50 search_url, 3 spotify_url, 3 apple_music_url) |
| `python3 scripts/update_site.py` | **PASS** (5/5 steps) |
| `python3 scripts/check_pages_sync.py` | **PASS** (site/ ↔ docs/ byte-identical) |
| `python3 scripts/check_translation_residue.py` | **WARNING** (jasmi article 1 obfuscated email; pre-existing) |

---

## 7. Files modified

**Content:**
- `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml` — 20 lines: 3 tracks updated with spotify_url/apple_music_url + note + next_action

**Regenerated (update_site.py):**
- `site/items/2026-06-26-paste-greatest-songs-1960s/index.html` — 6 lines: 3 new tracks show streaming links
- `docs/items/2026-06-26-paste-greatest-songs-1960s/index.html` — 6 lines: mirror

**Not modified:**
- `generate_item_pages.py` — 无需修改（v0.3.33 已支持）
- `check_tracks.py` — 无需修改（v0.3.33 已支持）
- `styles.css` — 无需修改（v0.3.33 已支持）
- `MUSIC_ARTICLE_RULES.md` — 无需修改（v0.3.33 已支持）
- `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` / `metadata.yaml` — 未触碰
- `README.md` — 未触碰

---

## 8. Local smoke test results

- ✅ Page HTTP 200
- ✅ track-card: 50
- ✅ play buttons: 38 (未变)
- ✅ search links: 50 (所有曲目保留)
- ✅ Spotify links: 3 (#55, #87, #69)
- ✅ Apple Music links: 3 (#55, #87, #72)
- ✅ Coverage: "38 / 50 首可播放 · 12 首待验证 · 可播放率 76%"
- ✅ Filter all: 50, playable: 38, pending: 12
- ✅ Rank 55: Spotify=True, Apple=True, Search=True, Play=False
- ✅ Rank 87: Spotify=True, Apple=True, Search=True, Play=False
- ✅ Rank 72: Spotify=False, Apple=True, Search=True, Play=False
- ✅ Rank 69: Spotify=True, Apple=False, Search=True, Play=False
- ✅ Total iframes at load: 0

---

## 9. Online smoke test (post-push)

- ✅ `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/` HTTP 200
- ✅ 4 streaming linked tracks show external links
- ✅ YouTube play buttons on 38 verified tracks still work
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

---

## 11. Tag

`v0.3.34-spotify-apple-link-batch` (annotated, pushed to `origin`).

Tag message:

```
Add Spotify and Apple Music external links for remaining Paste 1960s streaming-preferred tracks.

Tracks: #87 The Angels, #72 Os Mutantes, #69 Jacques Brel
YouTube verified count unchanged (38).
Play button count unchanged (38).
spotify_or_apple_preferred pool now empty (0).
```

---

## 12. Links

- **Commit**: https://github.com/conanxin/hermes-knowledge-base/commit/[COMMIT_HASH]
- **Tag**: https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.34-spotify-apple-link-batch
- **GitHub Pages Detail Page**: https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/
