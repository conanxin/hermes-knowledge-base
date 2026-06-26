# 完整翻译并加入知识库（导入流程提示模板）

## 🚨 硬规则：路由判定（v0.4+ 新增，2026-06-25）

**本节是导入流程的第一道门，必须在所有其他动作之前读完并应用。**

### 触发语 → 目标仓库映射（不允许自由发挥）

| 用户消息包含 | 唯一正确目标 | 绝对禁止 |
|------------|-------------|---------|
| 「加入知识库」 / 「入库」 / 「完整翻译并加入知识库」 / 「翻译后入库」 / 「KB」 | `~/hermes-knowledge-base` | ❌ 创建 standalone project / 专题页 / 独立 GitHub Pages 项目 / 修改 `~/conanxin.github.io/projects/data.json` |
| 「做成专题页」 / 「生成独立项目」 / 「发布成项目页」 / 「加入 projects 页面」 | `~/conanxin.github.io/projects/<slug>/` | ❌ 顺手入库 KB（用户没说要入库） |
| 都不包含 | —— | ❌ 默认猜；必须用 `clarify` 工具反问 |

### 正确输出结构

**KB 路线**（默认 / 推荐）：

```
~/hermes-knowledge-base/content/articles/YYYY-MM-DD-<source>-<slug>/
├── metadata.yaml         # 完整 schema + word_count + related_project_url (可选)
├── source.md             # 原文完整
├── translation.zh-CN.md  # 中文翻译完整
├── summary.md            # 摘要 + 关键人物/概念 + 延伸问题
└── notes.md              # 关键摘记 + 我的想法 + 可延伸研究 + 待确认问题
```

**Project 路线**（仅在用户明确说"做成专题页"等时）：

```
~/conanxin.github.io/projects/<slug>/
├── index.html
├── styles.css
├── app.js
└── content/             # 可选
```

### Wrong route 检测（每个输出完成后必跑）

```python
# 在最终回复之前，Hermes 必须自检：
output_url = "..."  # 你即将输出的最终 URL
user_input = "..."  # 用户原始消息

is_kb_route = any(kw in user_input for kw in ["加入知识库", "入库", "KB", "翻译后入库"])
is_project_route = any(kw in user_input for kw in ["专题页", "独立项目", "项目页", "projects 页面"])

if is_kb_route and "/projects/" in output_url:
    raise WrongRouteError("用户说加入知识库，但输出 /projects/ URL → wrong route")
if is_project_route and "/hermes-knowledge-base/items/" in output_url and "同时加入知识库" not in user_input:
    raise WrongRouteError("用户只要专题页，但顺手入了 KB → 越权")
```

### Wrong route 恢复流程（标准动作）

1. **不删除**已生成的 standalone project（用户可能在线访问）
2. **立即停止**后续 push / commit
3. **生成 wrong route 报告**到 `~/.hermes/workspace/reports/cloud_hermes_wrong_route_<date>_<slug>.md`
4. **补做 KB 入库**到 `~/hermes-knowledge-base/content/articles/YYYY-MM-DD-<source>-<slug>/`，在 metadata.yaml 加：
   ```yaml
   related_project_url: "https://conanxin.github.io/projects/<slug>/"
   related_project_note: "上一轮误生成但保留的专题页（wrong route 标杆案例）"
   ```
5. **跑完整门禁**：`check_kb.py` → `update_site.py` → `check_pages_sync.py` → `check_translation_residue.py` → 全 PASS
6. **commit + push 两条路线**，commit message 注明 "wrong route" / "after wrong route recovery"
7. **不修改** `~/conanxin.github.io/projects/data.json`（standalone project 不属于 projects grid）
8. **最终回复**：显式说明上一轮是 wrong route + 已补做 KB 入库 + 输出正确的 KB 详情页 URL

### 历史案例（防止再犯）

- ❌ 2026-06-24 Yarvin 文章：用户说"加入知识库"，却生成了 `~/conanxin.github.io/projects/yarvin-moldbug-cn/` standalone project + 修改了 `projects/data.json`。本节硬规则就是为防止再犯而设。

---

## 触发条件

用户说以下任意表达时执行：

- "把这篇文章完整翻译并加入知识库：URL"
- "入库并完整翻译：URL"
- "加入知识库：URL"
- "翻译后入库：URL"

## 默认行为

| 参数 | 默认值 |
|------|--------|
| content_type | article |
| 翻译语言 | zh-CN |
| 目录名格式 | YYYY-MM-DD-来源-slug |
| tags/topics | 由 Hermes 根据内容自动判断 |
| commit & push | 自动执行（除非用户说"先不要 push"） |

## 执行流程

### 0. Preflight（v0.3.38+ 强制）

**所有导入任务开始前必须先运行 preflight：**

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
python3 scripts/check_task_preflight.py
```

**如果是 versioned task：**

```bash
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name
```

**Preflight 结果处理：**

| 结果 | 处理方式 |
|------|----------|
| **PASS** | 继续执行导入 |
| **PASS_WITH_WARNINGS** | 仅当 warning 为已知非阻断项（如 v0.3.36 known duplicate）时可继续 |
| **FAIL** | **立即停止**，不得进入抓取/翻译阶段 |

### 1. 抓取正文（web_extract → browser 降级）

- 如果 URL 抓取失败 / paywall / ACL / 正文不完整 → **hard stop**，记录失败原因
- 长名单文章必须使用完整 source.md（不得基于截断版 web_extract）

### 2. 创建目录结构
### 3. 保存 source.md
### 4. 完整翻译为 translation.zh-CN.md
### 5. 生成 metadata.yaml（含 title_zh, source_site, word_count 等完整字段）
### 6. 生成 summary.md
### 7. 生成 notes.md（使用统一模板）
### 8. 处理 assets/
### 9. 更新索引（build_index.py）
### 10. 更新在线浏览页（update_site.py）
### 11. 运行质量检查（check_kb.py + check_translation_residue.py）
### 12. Commit & Push
### 13. 生成导入报告

## 强制停止条件

以下情况 Hermes 必须停止导入，向用户报告，不要强行入库：

- URL 无法访问或返回 404/403/500
- 正文抓取不完整（明显截断、缺少关键章节）
- 文章需要登录或付费才能阅读完整内容
- 内容类型不明确（无法判断是文章、论文、评论等）
- 翻译后英文残留严重（suspicious_count ≥ 20）—— **长名单文章例外**：residue 可能因专名密度天然高，详细规则见下方「长名单文章特殊规则」与 [docs/LISTICLE_IMPORT_RULES.md](../../docs/LISTICLE_IMPORT_RULES.md)
- metadata 关键字段无法确定（如作者、标题缺失）

## 📋 长名单文章（listicle）特殊规则

**触发条件**：文章标题或结构包含「Top N / Best N / Greatest N / 排名 / listicle / 编号型列表」。

**完整规范**：[docs/LISTICLE_IMPORT_RULES.md](../../docs/LISTICLE_IMPORT_RULES.md)（v1.0, 2026-06-26 固化）

**7 条核心约束（精简版）**：

1. **必须先完整解析 source.md** — 不得基于截断版 web_extract 开始翻译。长名单文章 fallback chain 必须包含 `curl + HTML 解析` 这一步,不要止步于 web_extract。

2. **翻译前结构预检**（必跑）:
   - 统计 H2 数量（应有 N 个,N=文章声称的列表长度）
   - 检查编号连续性（无 gap: #100, #99, #98, … #51）
   - 检查重复（同一编号不应出现两次）
   - 如果原文分页（如「page 3 of 3」），**只记录当前页覆盖范围,不得假装已覆盖全部分页**

3. **翻译后结构对齐 hard-stop**:
   - `source.md` 的编号标题 ↔ `translation.zh-CN.md` 的编号标题必须一一对应
   - 错位 / 缺号 / 重复 / 凭空捏造 → **禁止 commit/push,必须修复**

4. **metadata.yaml 必填字段**（长名单额外要求）:
   ```yaml
   coverage_scope: "rank_100_to_51_only"   # 当前覆盖范围
   is_partial_series: true                 # 是否系列文章的一部分
   series_info:                            # 完整系列信息
     total_parts: 3
     this_part: 1
     covered_range: "rank_100_to_51"
   translation_notes: |
     check_translation_residue.py 返回 suspicious_count=N
     这是音乐/影视/书单类文章的专名残留,不是漏译
   ```

5. **summary.md 必填段**: 「覆盖范围」章节,明确说明本次覆盖与未涵盖部分

6. **residue warning 解读**: 长名单文章 residue 可能天然高（50 首歌 × 歌名/艺人名/专辑名 = 80-150 项）。判定流程:
   - 抽样 10 个 residue 字符串
   - 80%+ 是已知专名 → ACCEPT
   - < 50% 是专名 → 真正漏译,hard-stop

7. **状态标记**: 长名单文章推荐用 `PASS_WITH_WARNINGS` 而非简单 `PASS`(若 residue 警告),commit message 应包含状态标记

**历史案例**：2026-06-26 Paste「100 greatest songs of the 1960s」(commit `725b7a9`) 因 web_extract 截断导致 11 首歌 H2 错位 + #75 缺失 + #74 凭空捏造,后续通过 source 重提取修复,教训固化到 LISTICLE_IMPORT_RULES.md。

## 🎵 音乐/影视/书目 listicle 的 track/film/book links（v0.3.19+）

当 listicle 每条目对应可播放/可定位实体（歌曲、影片、书目），需要给条目挂链接时，**优先级**：

1. **数据与翻译分离** — 链接元数据放 `<article-slug>/tracks.yaml`（或 `films.yaml` / `books.yaml`），**不要**硬编码进 `translation.zh-CN.md`。
2. **yaml schema 必填字段** — `rank`（与 H2 编号对齐）/ `artist` / `title` / `year` / `youtube_url` / `youtube_embed_url` / `spotify_url` / `apple_music_url` / `search_url` / `confidence` / `note`。
3. **confidence 字段值**：
   - `verified` — 高置信可播放（YouTube embed / Spotify URI 已人工核对）
   - `needs_verification` — metadata 已抓但 URL 未人工核对
   - `search_only` — 无可信 URL，只给 search 链接
4. **禁用** — 任何未经验证的 YouTube embed / Spotify URI（防 cover、live、reaction video 误填）。
5. **generator 集成** — `scripts/generate_item_pages.py` 检测 `<article-slug>/tracks.yaml` 存在时自动在每个对应 H2 后插入 track-card（50 卡片懒加载）。无需手写 HTML。
6. **不存音频** — KB 仓库只放元数据 + 嵌入 URL，不下载 mp3 / m4a / flac。
7. **质量门禁** — 跑 `python3 scripts/check_tracks.py` 校验 yaml 结构和 confidence 字段。

**历史案例**：2026-06-26 Paste「100 greatest songs of the 1960s」实施 v0.3.19-music-track-links，50 首全部 `confidence=needs_verification` + Google site-restricted search_url，0 个假 embed，0 个需要重翻 translation。

## 禁止事项

- 不要修改 Hermes 源码
- 不要重启 hermes-gateway.service
- 不要安装新依赖（使用现有工具）
- 不要推送 GitHub 除非用户授权
- 不要发送 Telegram 消息
- 不要暴露 API key、token、secret
- **不要生成残缺入库结果（缺少文件、字段为 0、翻译不完整）**

## 质量门禁（硬性规则）

1. `update_site.py` 已在最前面内置 `check_kb.py` 硬停止。如果 `check_kb.py` 返回 FAIL，`update_site.py` 立即返回非 0，**不会**运行 build / export / generate / sync，**不会**触碰 `site/data/catalog.json` 或 `docs/`。在 check 修复前**严禁**执行 commit / push。
2. `word_count` 字段必须是 YAML 对象，**不允许**用带引号的字符串或裸数字。规范格式：

   ```yaml
   word_count:
     source: 4434        # 整数（source.md 实际词数）
     translation: 7079   # 整数（translation.zh-CN.md 实际 CJK 字数）
   ```

   不允许：`word_count: 4500`、`word_count: "4500"`、`word_count: "~4500"`、`word_count: 约4500`。

3. 发现 `content/` 下存在半成品条目时，必须先修复或隔离到 `inbox/quarantine/`，再继续执行 `update_site.py`。
4. 除非用户明确说"先不要 commit/push"，否则完整导入流程应自动运行到 check → update_site → commit → push；但当 check 失败时必须立即停止并报告。

## 完整流水线顺序（更新于 v0.3.8+）

```
check_kb.py            ← 质量门禁，FAIL 立即停止
build_index.py
export_site_data.py
generate_item_pages.py
sync_pages_docs.py
```

---

## 长名单文章专用字段模板（LISTICLE）

长名单文章必须在 `metadata.yaml` 中包含以下字段。**完整规范**：`docs/LISTICLE_IMPORT_RULES.md`

```yaml
# 覆盖范围（长名单文章必填）
coverage_scope: "rank_100_to_51_only"      # 当前导入的覆盖范围
is_partial_series: true                     # 是否是系列文章的一部分

# 系列信息（如果是分页型 listicle）
series_info:
  total_parts: 3
  this_part: 1
  covered_range: "rank_100_to_51"
  remaining_parts:
    - part: 2
      url: "https://..."
      covered_range: "rank_50_to_11"
    - part: 3
      url: "https://..."
      covered_range: "rank_10_to_1"

# 翻译备注（说明 residue warning 性质）
translation_notes: |
  check_translation_residue.py returned suspicious_count=N.
  This is expected for a music/film/book listicle article
  containing N song/film/book titles + artist/director/author names
  (all preserved as proper nouns). No genuine untranslated paragraphs.
```

**长名单文章的 summary.md 必填段**：明确说明本次覆盖与未涵盖部分（详见 LISTICLE_IMPORT_RULES.md §5.2）

**长名单文章的 commit message 约定**：
```
Add [Source] [topic] list [N items] ([subtitle]) — [STATUS]
例: Add Paste Magazine 1960s top 100 songs list #100-#51 (zh-CN, 50 songs) — PASS_WITH_WARNINGS (residue=85 proper nouns)
```

**长名单文章的报告必填段**：
- `## Coverage scope` 表格
- `## Translation residue analysis` 段（专名类型 + 占比 + ACCEPT 判定）
