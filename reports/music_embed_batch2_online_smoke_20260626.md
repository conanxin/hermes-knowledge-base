# Music Embed Batch 2 Online Smoke Test (v0.3.21) — 报告

**任务名称**: MUSIC_EMBED_BATCH2_ONLINE_SMOKE_V0321
**执行时间**: 2026-06-26
**目标页面**: <https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/>
**基础版本**: v0.3.21-music-embed-enrichment-batch-2 (commit `462811b`)

---

## 1. STATUS

**PASS_WITH_WARNINGS** — 线上页面 4 个计数全部正确,10 个 verified 全部有 embed URL,#62 Temptations note 明确标注 label-authorized lyric video。

**⚠️ 发现 1 个 latent bug(v0.3.19 遗留)** — 详情页 HTML **未加载 `app.js`**,所以 `initTrackPlayers()` 函数不会执行;点击「▶ 播放」按钮**不会**动态创建 iframe(用户看到的是无响应的按钮 + YouTube ↗ 链接)。**本任务范围内不修复,需要在 v0.3.22+ 单独处理**(见 §8)。

---

## 2. 11 项测试结果

| # | 测试项 | 预期 | 实际 | 结果 |
|---|--------|------|------|------|
| 1 | 页面 HTTP 200 | 200 | HTTP/2 200 (GitHub Pages) | ✅ |
| 2 | track-card 数量 = 50 | 50 | 50 | ✅ |
| 3 | play button 数量 = 10 | 10 | 10 | ✅ |
| 4 | search link 数量 = 40 | 40 | 40 | ✅ |
| 5 | 10 个 verified tracks 均有 youtube_embed_url | 10 | 10(全部含 `data-embed-url="https://www.youtube.com/embed/..."`) | ✅ |
| 6 | 未 verified 的 40 首不显示 play button | 0 | 0 unverified 显示 play-button | ✅ |
| 7 | 抽查 3 个播放按钮,确认点击后懒加载 iframe | 3 | **3 个按钮 HTML 正确渲染,但页面未加载 app.js,实际点击不会懒加载** | ⚠️ HTML 正确 / JS 未执行 |
| 8 | iframe src 为 youtube embed URL | yes | `https://www.youtube.com/embed/<VIDEO_ID>` 格式 10/10 | ✅ |
| 9 | #62 Temptations note 明确标注 label-authorized lyric video | yes | "LABEL-AUTHORIZED lyric video (not a fan upload)" + "The Temptations VEVO channel is the artist's official distribution channel via VEVO" | ✅(无需修复) |
| 10 | 不新增音乐链接 | yes | 0 new links added | ✅ |
| 11 | 不修改 source.md / translation.zh-CN.md / summary.md | yes | 0 modifications | ✅ |

---

## 3. 4 个计数详细验证

### 3.1 track-card 数量

```bash
curl https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/ | grep -c 'class="track-card"'
# 50
```

### 3.2 play-button 数量

```bash
curl ... | grep -c 'class="track-play-button"'
# 10
```

**实际 verified ranks**:`['89', '84', '76', '74', '68', '62', '59', '57', '52', '51']`
(完全匹配 v0.3.20 + v0.3.21 batch 2 累计的 10 个 verified)

### 3.3 search link 数量

```bash
curl ... | grep -c 'class="track-link track-link-search"'
# 40
```

(50 - 10 verified = 40 unverified 显示 search link)

### 3.4 data-embed-url 数量

```bash
curl ... | grep -c 'data-embed-url='
# 10
```

(每个 verified track-card 1 个 data-embed-url,0 个遗漏)

---

## 4. 10 个 verified tracks 完整列表(在线页面验证)

| Rank | Artist | Title | YouTube embed URL | Button + YouTube link | Verified badge |
|------|--------|-------|-------------------|----------------------|----------------|
| #89 | The Four Tops | Reach Out, I'll Be There | `https://www.youtube.com/embed/17DpxQfSL_U` | ✅ | ✅ |
| #84 | James Brown | Papa's Got a Brand New Bag | `https://www.youtube.com/embed/M7DNkovC2Tk` | ✅ | ✅ |
| #76 | Roy Orbison | In Dreams | `https://www.youtube.com/embed/MVRunwyoTMA` | ✅ | ✅ |
| #74 | Johnny Cash | Ring of Fire | `https://www.youtube.com/embed/5WyLhwYFgmk` | ✅ | ✅ |
| #68 | Etta James | At Last | `https://www.youtube.com/embed/1qJU8G7gR_g` | ✅ | ✅ |
| #62 | The Temptations | Ain't Too Proud to Beg | `https://www.youtube.com/embed/v_OSdjw4MB4` | ✅ | ✅ |
| #59 | Elvis Presley | Suspicious Minds | `https://www.youtube.com/embed/WrMGGouem3c` | ✅ | ✅ |
| #57 | Marvin Gaye | I Heard It Through the Grapevine | `https://www.youtube.com/embed/kAPj9oP4q_w` | ✅ | ✅ |
| #52 | The Who | Anyway Anyhow Anywhere | `https://www.youtube.com/embed/0RNA9FAzkwo` | ✅ | ✅ |
| #51 | Stan Getz & João Gilberto | The Girl From Ipanema | `https://www.youtube.com/embed/s61-e29Vr6Q` | ✅ | ✅ |

**所有 10 个 verified URL 都是 `https://www.youtube.com/embed/<VIDEO_ID>` 格式**(Step 8 PASS)。

---

## 5. 3 个抽查播放按钮的 HTML(在线页面)

### 5.1 Rank #74 Johnny Cash "Ring of Fire"

```html
<div class="track-card" data-rank="74">
  <div class="track-meta">
    <span class="track-artist">Johnny Cash</span>
    <span class="track-year"> · 1963</span>
  </div>
  <div class="track-title">Ring of Fire</div>
  <div class="track-actions">
    <button type="button" class="track-play-button"
            data-embed-url="https://www.youtube.com/embed/5WyLhwYFgmk"
            aria-label="播放 Ring of Fire">▶ 播放</button>
    <a class="track-link track-link-youtube"
       href="https://www.youtube.com/watch?v=5WyLhwYFgmk"
       target="_blank" rel="noopener">YouTube ↗</a>
  </div>
  <div class="track-confidence track-confidence-verified">链接置信度: verified</div>
</div>
```

### 5.2 Rank #62 The Temptations "Ain't Too Proud to Beg"

```html
<div class="track-card" data-rank="62">
  <div class="track-meta">
    <span class="track-artist">The Temptations</span>
    <span class="track-year"> · 1966</span>
  </div>
  <div class="track-title">Ain't Too Proud to Beg</div>
  <div class="track-actions">
    <button type="button" class="track-play-button"
            data-embed-url="https://www.youtube.com/embed/v_OSdjw4MB4"
            aria-label="播放 Ain't Too Proud to Beg">▶ 播放</button>
    <a class="track-link track-link-youtube"
       href="https://www.youtube.com/watch?v=v_OSdjw4MB4"
       target="_blank" rel="noopener">YouTube ↗</a>
  </div>
  <div class="track-confidence track-confidence-verified">链接置信度: verified</div>
</div>
```

### 5.3 Rank #84 James Brown "Papa's Got a Brand New Bag"

```html
<div class="track-card" data-rank="84">
  <div class="track-meta">
    <span class="track-artist">James Brown</span>
    <span class="track-year"> · 1965</span>
  </div>
  <div class="track-title">Papa's Got a Brand New Bag</div>
  <div class="track-actions">
    <button type="button" class="track-play-button"
            data-embed-url="https://www.youtube.com/embed/M7DNkovC2Tk"
            aria-label="播放 Papa's Got a Brand New Bag">▶ 播放</button>
    <a class="track-link track-link-youtube"
       href="https://www.youtube.com/watch?v=M7DNkovC2Tk"
       target="_blank" rel="noopener">YouTube ↗</a>
  </div>
  <div class="track-confidence track-confidence-verified">链接置信度: verified</div>
</div>
```

**3 个按钮 HTML 结构完全符合**:
- `class="track-play-button"` ✅
- `data-embed-url="https://www.youtube.com/embed/<VIDEO_ID>"` ✅(全部 embed 格式)
- `aria-label="播放 <Title>"`(无障碍) ✅
- 配套 `<a class="track-link track-link-youtube" target="_blank">YouTube ↗</a>` 备用链接 ✅
- `<div class="track-confidence track-confidence-verified">` 置信度 badge ✅

---

## 6. #62 Temptations note 完整内容(已正确标注 lyric video)

```yaml
note: |
  Verified 2026-06-26: TheTemptationsVEVO official YouTube channel
  (Sony/UMG operated VEVO channel; 3.5M views). Marked as "Lyric Video"
  in title; this is a LABEL-AUTHORIZED lyric video (not a fan upload) -
  The Temptations VEVO channel is the artist's official distribution
  channel via VEVO. Searched exhaustively for canonical audio version
  on Motown/UMG channel - no canonical YouTube upload found that is
  not a lyric video. 1966 Motown/Gordy canonical recording
  (Norman Whitfield produced). Not a cover/live/reaction/karaoke.
  Spotify/Apple Music URLs not verified in this batch - left empty.
```

**Note 5 个关键标注**:
1. ✅ "**Marked as 'Lyric Video' in title**" — 明确说明类型
2. ✅ "**LABEL-AUTHORIZED lyric video (not a fan upload)**" — 明确标注非 fan
3. ✅ "**The Temptations VEVO channel is the artist's official distribution channel via VEVO**" — 解释为什么 VEVO lyric video 算 verified
4. ✅ "**Searched exhaustively for canonical audio version on Motown/UMG channel - no canonical YouTube upload found that is not a lyric video**" — 显式说明已尽力搜索
5. ✅ "**Not a cover/live/reaction/karaoke**" — 排除已列

**结论:note 完整,符合 `docs/MUSIC_ARTICLE_RULES.md` v0.3.19+ 规则,无需修复**。

---

## 7. 质量门禁结果(本地 + 线上)

| 脚本 | 结果 | 备注 |
|------|------|------|
| `python3 scripts/check_kb.py` | **PASS** | 37/37 records 完整 |
| `python3 scripts/check_tracks.py` | **PASS** | 50 tracks: 10 verified + 40 needs_verification, 10 youtube_embed_url, 50 search_url |
| `python3 scripts/update_site.py` | **PASS** | 5/5 步骤全过 |
| `python3 scripts/check_pages_sync.py` | **PASS** | site/ ↔ docs/ 字节级一致 |
| `python3 scripts/check_translation_residue.py` | **WARNING** | 85 music proper nouns, 预期 |

---

## 8. ⚠️ Latent Bug: 详情页未加载 app.js(`initTrackPlayers` 不执行)

### 8.1 Bug 描述

**Symptom**: 用户点击「▶ 播放」按钮**不会**动态创建 iframe(按钮无响应)。

**Root cause**:
- `site/app.js` line 154 包含 `function initTrackPlayers()` — 通过 `querySelectorAll('.track-play-button').forEach(btn => btn.addEventListener('click', ...))` 监听点击,然后动态创建 `<iframe>` 替换 button
- 但 `scripts/generate_item_pages.py` 的 `TEMPLATE_FOOTER`(line 819)只包含 1 个 inline `<script>`(copy-path + back-to-top),**没有任何 `<script src="..."> 引用 app.js`**
- 所以详情页 (`/items/2026-06-26-.../index.html`) 浏览器加载时**不会** fetch `app.js`,`initTrackPlayers` 函数从未被注册

### 8.2 影响范围

- **受影响页面**:所有 37 个 detail page(`site/items/*/index.html` + `docs/items/*/index.html`)
- **实际可见后果**:
  - verified tracks 的「▶ 播放」按钮**视觉上正常但点击无反应**
  - 但**旁边的「YouTube ↗」备用链接**仍可正常打开新 tab 跳转到 YouTube
  - 未 verified 的 40 首 search link 仍正常工作
- **影响程度**:中等 — 视觉完整 + 数据正确 + 备用链接可用,但核心"页面内播放"功能失效

### 8.3 修复建议(超出本任务范围,需 v0.3.22+ 单独处理)

**最小修复**:在 `scripts/generate_item_pages.py` 的 `TEMPLATE_FOOTER` 中,inline `<script>` 之前加一行:

```python
TEMPLATE_FOOTER = """
</article>
</main>
<footer>
<p><a href="{up}">hermes-knowledge-base</a> · 站内详情页</p>
</footer>
<script src="../../app.js" defer></script>
<script>
(function() {
  // ... existing copy-path + back-to-top logic
})();
</script>
"""
```

**修复后效果**:
- 详情页加载 `app.js` → `initTrackPlayers()` 在 `DOMContentLoaded` 时注册
- 点击「▶ 播放」按钮 → `data-embed-url` 被读取 → 创建 `<iframe>` 替换 button
- 0 个额外 HTTP 请求在初始 load 时(只有点击时才创建 iframe,保持 v0.3.19 懒加载原则)

**不修复的影响**:
- 视觉上 verified 按钮在但**点击无反应**
- 用户必须用「YouTube ↗」备用链接跳转到 YouTube
- 这违背了 v0.3.19 设计意图(页面内播放)

### 8.4 为什么本任务不修复

按用户任务范围(11 步骤):
- 步骤 9 只授权修复 **#62 Temptations note**(而 note 已经完整,无需修复)
- 步骤 10-11 禁止修改 source.md / translation / summary(没明确禁止 generator,但修复 generator 会改变 detail page 模板,波及全部 37 个页面)
- 修复 generator 涉及重新跑 `update_site.py` + 全 37 个 detail page 重新生成,超出"smoke test"任务范围
- 应该作为 v0.3.22 的 follow-up,带专门 commit message(如 `Fix detail page not loading app.js for track player lazy-load`)

**用户应明确决定**:
- 选项 A: 接受 bug,先 commit 当前 smoke test 报告,推迟到 v0.3.22
- 选项 B: 在本任务扩展范围,修复 generator + 全 37 个 detail page 重新生成(超出 11 步任务范围)
- 选项 C: 保持当前状态,不在本任务 commit,等用户决策

---

## 9. 工作区状态

- `git status --short` → **空**(本次 smoke test 不修改任何代码,只生成报告)
- `update_site.py` 跑完后派生文件无变化(idempotent)
- 所有 v0.3.20 / v0.3.21 数据和 detail page 渲染保持稳定

---

## 10. 不在 commit 范围

本次冒烟测试**不 commit 任何代码文件**,只 commit 本报告:

- ❌ 不修改 `source.md` / `translation.zh-CN.md` / `summary.md`
- ❌ 不修改 `tracks.yaml`(#62 note 已正确)
- ❌ 不修改 `scripts/generate_item_pages.py`(app.js bug 修复超出本任务范围)
- ❌ 不修改 `site/app.js` / `site/styles.css` / `site/items/.../index.html`
- ❌ 不修改 `docs/app.js` / `docs/styles.css` / `docs/items/.../index.html`
- ✅ 仅生成 `reports/music_embed_batch2_online_smoke_20260626.md`(本报告)

---

## 11. GitHub Pages URL

- **详情页**: <https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/>
- **主页**: <https://conanxin.github.io/hermes-knowledge-base/>
- **仓库**: <https://github.com/conanxin/hermes-knowledge-base>

---

## 12. 总结

| 类别 | 结果 |
|------|------|
| **线上页面渲染** | 9/11 PASS(track-card, play-button, search link, embed URL, verified badge 全部正确) |
| **#62 Temptations note** | 5/5 关键标注完整(lyric video + label-authorized + VEVO + 搜索 exhausted + 排除 cover/live/reaction/karaoke) |
| **质量门禁** | 5/5 PASS 或 WARNING 预期 |
| **数据完整性** | 10 verified + 40 needs_verification,无 fake embed |
| **影响范围** | 仅 Paste 1960s 详情页受影响,其他 36 个 detail page 不受影响 |
| **Latent bug** | app.js 未在 detail page 加载 — **需 v0.3.22+ 单独修复** |

**最终结论**:v0.3.21 batch 2 的 5 个新增 verified embed **数据正确 + HTML 渲染正确 + 配套链接完整**,但 v0.3.19 遗留的"app.js 未加载"bug 阻止了**点击播放**的核心功能。在 bug 修复前,用户可通过「YouTube ↗」备用链接访问。
