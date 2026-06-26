# 音乐文章专用规则（Music Article Rules）

> **状态**: v1.0 — 2026-06-26 固化
> **触发版本**: v0.3.19-music-track-links
> **来源案例**: Paste Magazine「The 100 greatest songs of the 1960s」(commit `725b7a9` + `34edf3d`)
> **适用范围**: 任何包含「音乐 / 专辑 / 歌曲榜单 / 艺人列表」的文章,以及用户要求「加入播放链接 / 播放按钮」的情况

## 为什么需要这些规则

KB 内一篇音乐长名单文章(Paste「The 100 greatest songs of the 1960s」)需要为每首歌提供音乐链接与播放入口。直接修改 `translation.zh-CN.md` 嵌入播放器会产生以下问题:

1. **可维护性差**: 翻译文本与播放地址耦合,后续要更新 URL 必须重新翻译
2. **页面膨胀**: 50 个 `<iframe>` 同时加载会拖慢页面、消耗第三方配额
3. **错误风险**: 自动抓取 YouTube/Spotify URL 容易抓错版本(cover、remaster、karaoke)
4. **污染翻译质量**: URL 嵌入正文会增加 translation residue,触发检查脚本误判

**解决方案**: 引入独立的 `tracks.yaml` 数据文件 + 详情页生成器自动注入卡片 + 播放器懒加载。

---

## 1. 数据结构 — tracks.yaml

每个有音乐内容的 KB 条目,可在其目录下新增 `tracks.yaml`:

```yaml
article_slug: "2026-06-26-paste-greatest-songs-1960s"
coverage_scope: "rank_100_to_51_only"
source_article_url: "https://..."
schema_version: 1
notes: |
  可选的元数据,说明 tracks 数据的来源、置信度规则、未涵盖部分等。

tracks:
  - rank: 100                              # 排名(必需,唯一)
    artist: "Wayne Shorter"                # 必需
    title: "Infant Eyes"                   # 必需
    year: 1966                              # 必需
    contributor: "Mariam Abdel-Razek"       # 撰稿人(可空)
    section_heading_source: "..."          # 原文 H2(可空,用于校验)
    section_heading_translation: "..."     # 译文 H2(可空,用于校验)
    youtube_url: ""                        # 直链(空 = 未验证)
    youtube_embed_url: ""                  # 嵌入 URL(youtube.com/embed/...)
    spotify_url: ""                        # Spotify 直链
    apple_music_url: ""                    # Apple Music 直链
    search_url: "https://www.google.com/search?q=..."   # 兜底搜索链接
    confidence: "needs_verification"       # verified / needs_verification / search_only
    note: ""                                # 自由备注
```

### 字段约束

| 字段 | 必需 | 类型 | 规则 |
|---|---|---|---|
| `rank` | ✅ | int >= 1 | 在文件内唯一 |
| `artist` | ✅ | non-empty str | — |
| `title` | ✅ | non-empty str | — |
| `year` | ❌ | int | 推荐填写(用于排序/搜索) |
| `confidence` | ✅ | enum | `verified` / `needs_verification` / `search_only` |
| `youtube_embed_url` | ❌ | URL | 若填写,必须匹配 `youtube.com/embed/<id>` 模式 |
| `search_url` | ❌ | URL | 若填写,必须以 `http://` 或 `https://` 开头 |

### confidence 三档

| 等级 | 含义 | 是否允许填具体 URL |
|---|---|---|
| `verified` | 已经人工核对 URL 指向原曲(非 cover / remaster / live) | ✅ 可填 |
| `needs_verification` | URL 待人工验证,search_url 仅作兜底 | ⚠️ 仅填 search_url |
| `search_only` | 找不到稳定 URL,只能靠 search_url 引导用户查找 | ⚠️ 仅填 search_url |

**硬性规则**: 不确定时必须选 `needs_verification`,**严禁伪造 URL**。

---

## 2. 不存音频,只存链接

**严禁**:

- ❌ 把 mp3 / m4a / wav 存入 `content/`、`site/`、`docs/`(会污染 git + 违反仓库资产策略)
- ❌ 试图用 `<audio>` 标签做自托管播放
- ❌ 用 iframe 内嵌第三方完整播放器(必须只挂按钮,懒加载)

**允许**:

- ✅ `youtube_embed_url` 填 `https://www.youtube.com/embed/<video_id>`
- ✅ `spotify_url` / `apple_music_url` 填官方直链(用户点击后跳第三方 app)
- ✅ `search_url` 填 Google / DuckDuckGo 搜索链接,作为 fallback

---

## 3. 校验脚本

`scripts/check_tracks.py` 自动验证:

- tracks 数量 > 0
- rank 不重复
- artist / title 非空
- confidence 在合法集合内
- youtube_embed_url 必须匹配 `youtube.com/embed/...`
- search_url 必须以 http(s):// 开头
- 对 Paste 1960s 这类 known canonical 条目,额外校验 tracks 数量 == 50、rank 范围 100..51、source.md / translation.zh-CN.md H2 数量 == 50

```bash
python3 scripts/check_tracks.py
```

退出码:

- `0`: PASS 或 WARNING(允许 `needs_verification` 全部留空)
- `1`: FAIL(结构性问题,如 rank 重复、URL 格式错、cross-check 失败)

---

## 4. 详情页注入逻辑

`scripts/generate_item_pages.py` 在生成详情页时:

1. 检查 record 目录下是否存在 `tracks.yaml`
2. 若存在,加载并构建 `rank -> HTML` 字典
3. 在渲染 `translation` 节段(对 article 类型)时,对每个 H2 检查 `#NNN. ...` 开头
4. 若 H2 编号命中 tracks.yaml 中的 rank,在该 H2 之后立即插入 track card HTML
5. 其他节段(notes / source / summary)不插入(避免重复)

---

## 5. 播放器懒加载

`site/app.js` 监听 `.track-play-button` 点击:

- 第一次点击 → 创建 `<iframe>` 并插入卡片(默认不预加载 iframe)
- 第二次点击 → 移除 iframe,折叠回按钮状态
- 没有 `data-embed-url` 的卡片**不显示**播放按钮(防伪造)

**性能约束**:

- 50 个 track card 同时存在页面,但 50 个 iframe **只有用户点击后才创建**
- 页面初次加载不触发任何 YouTube / Spotify 网络请求
- 移动端友好(480px 断点单独优化 card padding)

---

## 6. CSS 样式

`site/styles.css` 中新增样式类(2026-06-26 同步到 docs/styles.css):

- `.track-card` — 卡片容器
- `.track-title` / `.track-meta` / `.track-artist` / `.track-year`
- `.track-actions` — 操作区(播放按钮 + 链接)
- `.track-play-button` — 播放按钮(accent 色)
- `.track-embed` — iframe 容器(16:9 aspect-ratio)
- `.track-link` — 外链按钮
- `.track-link-search` — 兜底搜索链接(灰色弱化)
- `.track-confidence` / `.track-confidence-verified` / `.track-confidence-needs-verification`

**重要**: 修改 `site/styles.css` 后必须 `cp site/styles.css docs/styles.css` 同步(KB Hard Rule)。

---

## 7. 与 LISTICLE_IMPORT_RULES 的关系

音乐长名单文章**首先必须**符合 [docs/LISTICLE_IMPORT_RULES.md](LISTICLE_IMPORT_RULES.md):

- ✅ 长名单识别
- ✅ 先完整解析 source.md
- ✅ 翻译前结构预检
- ✅ 翻译后结构对齐
- ✅ metadata + summary 记录 coverage_scope
- ✅ residue 解读
- ✅ PASS_WITH_WARNINGS 状态

**额外**: 音乐长名单文章还需要:

- 创建 `tracks.yaml`
- 通过 `check_tracks.py` 校验
- 在 commit message 中包含 `tracks-link` 标识(如 `Add music track links for ...`)

---

## 8. 禁止事项

| 行为 | 原因 |
|---|---|
| 在 translation.zh-CN.md 嵌入 `<iframe>` / `<audio>` | 与翻译文本耦合,可维护性差 |
| 填 `confidence: "verified"` 但 URL 未人工核对 | 误导用户,违反"防止伪造"原则 |
| 把封面图/专辑图存入 git 仓库 | 增大仓库体积,KB 资产策略禁止 |
| 为同一首歌列出多个版本(live / cover / remaster) | 用户请求的是原曲榜单 |
| 用自动搜索 API 批量填 URL | 容易填错版本,必须人工确认 |
| 修改其他非音乐文章页面同时加 track-card | 该 feature 仅作用于有 tracks.yaml 的记录 |
| 创建 standalone project | 违反 KB Hard Rule,只维护 hermes-knowledge-base |

---

## 9. 历史案例

### 2026-06-26 Paste Magazine「The 100 greatest songs of the 1960s」(v0.3.19)

- 创建 `tracks.yaml`,50 条记录 (#100-#51)
- 全部 `confidence: "needs_verification"`(未离线验证)
- 全部填 `search_url`(Google site-restricted YouTube 搜索)
- `youtube_embed_url` / `spotify_url` / `apple_music_url` 全部留空
- commit: `Add music track links for Paste 1960s listicle`
- 详情页: 50 个 track-card,0 个 iframe,所有外链 + 搜索链接 + confidence badge
- 其他 36 个 detail page 完全不受影响

### 未来建议

- 如果后续用户填了 verified URLs,需要重新跑 `check_tracks.py` 与 `update_site.py`
- 当多个 KB 条目都有 tracks.yaml 时,可考虑加入跨条目的 `tracks_index.json`

---

**维护者**: Hermes Agent
**最后更新**: 2026-06-26
**关联文档**:
- [docs/LISTICLE_IMPORT_RULES.md](LISTICLE_IMPORT_RULES.md) — 长名单文章规则
- [docs/AGENT_COMMANDS.md](AGENT_COMMANDS.md) — 导入规则总览
- [templates/prompts/import_article_prompt.md](../templates/prompts/import_article_prompt.md) — 完整导入流程
- `scripts/check_tracks.py` — tracks 校验脚本
- `scripts/generate_item_pages.py` — 详情页生成器(包含 track card 注入)