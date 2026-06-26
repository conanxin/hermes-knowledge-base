# Music Track Links for Paste 1960s Listicle — 实施报告

**任务名称**: MUSIC_TRACK_LINKS_PASTE_1960S_V0319
**版本号**: v0.3.19-music-track-links
**执行时间**: 2026-06-26
**目标条目**: `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/`
**完整规范**: [docs/MUSIC_ARTICLE_RULES.md](../docs/MUSIC_ARTICLE_RULES.md)

---

## 1. STATUS

**PASS_WITH_WARNINGS** — 50 个 track-card 全部就位 + 50 个 search 链接可用 + 0 个假 embed；未验证 URL 需要后续人工补全。

---

## 2. 实施目标

为 Paste Magazine「The Greatest Songs of the 1960s」Top 100（#100–#51）中文译本详情页增加可维护的音乐播放链接架构。50 首歌曲的 track metadata 集中放 `tracks.yaml`，由 `generate_item_pages.py` 在 H2 后注入 track-card，前端点击后懒加载 iframe。

---

## 3. tracks.yaml 稳定性

- 文件位置: `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml`
- 文件大小: 28305 bytes（709 行）
- 验证步骤（每跑一个脚本后立即 check 文件存在）：
  - `check_kb.py` → ✅ 文件存在 28305 bytes
  - `build_index.py` → ✅ 文件存在 28305 bytes
  - `export_site_data.py` → ✅ 文件存在 28305 bytes
  - `generate_item_pages.py` → ✅ 文件存在 28305 bytes
  - `sync_pages_docs.py` → ✅ 文件存在 28305 bytes
  - `check_pages_sync.py` → ✅ 文件存在 28305 bytes
  - `update_site.py`（完整流水线）→ ✅ 文件存在 28305 bytes

**根因诊断**: 上一轮 tracks.yaml 反复消失不是脚本删除，而是 untracked 文件在 git stash 切换 working tree 时被丢弃。本轮先 `git stash pop` 恢复 v0.3.19 工作，再逐步验证每脚本对 tracks.yaml 无破坏。

---

## 4. tracks 数据

| 字段 | 值 |
|------|----|
| tracks 总数 | 50 |
| rank 范围 | 100 – 51（连续） |
| verified | 0 |
| needs_verification | 50 |
| search_only | 0 |
| youtube_embed_url（非空） | 0 |
| search_url（非空） | 50 |
| 实际播放按钮（`.track-play-button`） | 0 |
| search link（`.track-link-search`） | 50 |

**说明**: 50 个 track 全部 `confidence=needs_verification` + Google site-restricted search_url（`https://www.google.com/search?q=site:youtube.com+...`），无任何未经验证的 YouTube embed / Spotify URI。这是有意设计：云端 Hermes 没有可靠的离线途径验证 canonical streaming URLs（防 cover / live / reaction video 误填），URL 补全是后续人工 / 工具流的工作。

---

## 5. 质量门禁结果

| 脚本 | 结果 | 备注 |
|------|------|------|
| `python3 scripts/check_kb.py` | **PASS** | 37/37 records 完整 |
| `python3 scripts/check_tracks.py` | **WARNING** | 50 tracks PASS（所有 confidence=needs_verification）— WARNING 预期 |
| `python3 scripts/update_site.py` | **PASS** | 5/5 步骤全过 |
| `python3 scripts/check_pages_sync.py` | **PASS** | site/ ↔ docs/ 字节级一致 |
| `python3 scripts/check_translation_residue.py` | **WARNING** | 85 residue 音乐专名（artist + title），如预期 |
| `python3 scripts/build_index.py` | **PASS** | 37 records / 408 tags / 29 authors |
| `python3 scripts/export_site_data.py` | **PASS** | 37 records → site/data/catalog.json |
| `python3 scripts/generate_item_pages.py` | **PASS** | 37 item pages 生成（detail page 含 50 track-card） |
| `python3 scripts/sync_pages_docs.py` | **PASS** | site/items/ → docs/items/ 镜像 |

---

## 6. 本地冒烟测试

启动 `python3 -m http.server 8765 -d site`，按要求验证：

| # | 测试项 | 预期 | 实际 | 结果 |
|---|--------|------|------|------|
| 1 | 首页 200 | 200 | 200 | ✅ |
| 2 | Paste 1960s 详情页 200 | 200 | 200 | ✅ |
| 3 | 详情页 track-card 数 | 50 | 50 | ✅ |
| 4 | rank / artist / title / year / confidence 全显 | yes | yes | ✅ |
| 5 | youtube_embed_url 非空才显示「▶️ 播放」按钮 | 0 | 0 | ✅ |
| 6 | youtube_embed_url 空不显示假播放按钮 | 0 | 0 | ✅ |
| 7 | search_url 非空显示「查找版本 ↗」链接 | 50 | 50 | ✅ |
| 8 | 点击「▶️ 播放」才懒加载 iframe | 函数就绪 | `initTrackPlayers` x3 | ✅ |
| 9 | 其他 article 页面不受影响 | 0 | 4 个其他详情页 track-card = 0 | ✅ |
| 10 | 移动端布局不溢出 | media query | `.track-card { margin-left: -8px; margin-right: -8px }` @max-width: 480px | ✅ |

**冒烟测试 PASS**

---

## 7. 修改文件清单

### 新增（4）

| 文件 | 字节 | 说明 |
|------|------|------|
| `content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml` | 28305 | 50 tracks metadata, rank 100–51 |
| `scripts/check_tracks.py` | 12867 | tracks.yaml 结构 + confidence 校验 |
| `docs/MUSIC_ARTICLE_RULES.md` | 8776 | v0.3.19 音乐文章规范 |
| `reports/music_track_links_paste_1960s_20260626.md` | (本文件) | 本报告 |

### 修改（9）

| 文件 | 变化 | 说明 |
|------|------|------|
| `scripts/generate_item_pages.py` | +278 行 | 检测 `tracks.yaml` 存在时在 H2 后注入 track-card |
| `site/styles.css` | +127 行 | `.track-card` / `.track-meta` / `.track-actions` / `.track-link-search` / `.track-confidence-needs-verification` / 移动端响应式 |
| `docs/styles.css` | +127 行 | 同上（与 site/ 字节级同步） |
| `site/app.js` | +36 行 | `initTrackPlayers()` 懒加载 click handler |
| `docs/app.js` | +36 行 | 同上（与 site/ 字节级同步） |
| `site/items/2026-06-26-paste-greatest-songs-1960s/index.html` | +50 行 | 50 个 track-card 注入 |
| `docs/items/2026-06-26-paste-greatest-songs-1960s/index.html` | +50 行 | 同上（sync 后） |
| `docs/AGENT_COMMANDS.md` | +15 行 | 新增「🎵 音乐/影视/书目 listicle 的 track/film/book links（v0.3.19+）」规则段 |
| `templates/prompts/import_article_prompt.md` | +17 行 | 新增「🎵 音乐/影视/书目 listicle 的 track/film/book links（v0.3.19+）」规则段 |

### 派生文件（自动生成，不需单独 add）

- `site/data/catalog.json` — 37 records
- `docs/data/catalog.json` — 37 records
- `site/items/*/index.html` × 37 — 全部 detail page
- `docs/items/*/index.html` × 37 — 镜像
- `docs/index.html` — 728 bytes SPA 入口
- `site/index.html` — 728 bytes SPA 入口

---

## 8. 历史 stash 状态（事故复盘）

| stash | 消息 | 内容 | 处置 |
|-------|------|------|------|
| `stash@{0}` | "stash unrelated changes before v0.3.20 verify" | AGENT_COMMANDS / app.js / generate_item_pages / detail page / import_article_prompt + 3 untracked | 已 pop，应用到 working tree；AGENT_COMMANDS / app.js / import_article_prompt 的 v0.3.19 music 修改在 v0.3.20 阶段被覆盖丢失，**已在本轮重新打补丁** |
| `stash@{1}` | "stash unrelated css changes before v0.3.20 tag" | site/styles.css + docs/styles.css track-card 样式 | 已 pop，127 行 +127 行应用到 working tree |
| `stash@{2}` | "stash unrelated paste tracks before v0.3.20 tag" | generate_item_pages.py 集成 + detail page | 已 pop，278 行 + 50 行应用 |
| `stash@{3}` | "stash paste greatest songs article before v0.3.19 tagging" | （空） | 保留 |
| `stash@{4}` | "stash v0.3.18 tag report before v0.3.19 tagging" | （空） | 保留 |

**v0.3.19 music 部分恢复完整度**: 9/9 modify + 4/4 new（tracks.yaml / check_tracks.py / generate_item_pages.py 集成 / styles / app.js / AGENT_COMMANDS / import_article_prompt / MUSIC_ARTICLE_RULES.md / detail page）。

---

## 9. 不在 commit 范围（需用户确认）

`reports/dario_anthropic_video_kb_import_20260626.md` 是 v0.3.20 阶段 Dario Amodei 视频 KB 导入报告，与 v0.3.19 Paste 1960s 任务无关。**未**纳入本次 v0.3.19 commit。建议用户确认是否需要单独 commit 该文件。

---

## 10. GitHub Pages URL

- 详情页: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-paste-greatest-songs-1960s/`
- 主页: `https://conanxin.github.io/hermes-knowledge-base/`
- 仓库: `https://github.com/conanxin/hermes-knowledge-base`

---

## 11. 后续人工补全工作（TODO）

1. 跑 `python3 scripts/check_tracks.py` 找到 `needs_verification` 的 track
2. 用 `youtube_url` / `youtube_embed_url` 字段填入人工核对后的 canonical YouTube 链接
3. 改完后跑 `python3 scripts/update_site.py` 重生 detail page
4. 再次确认 `.track-play-button` 数量上升（每次 verified URL → 1 个按钮）
5. 跑 `check_pages_sync.py` + commit + push

**数据与翻译分离的好处**: 上述 4 步只动 `tracks.yaml` 与 `index.html`（派生），不动 `source.md` 与 `translation.zh-CN.md`。
