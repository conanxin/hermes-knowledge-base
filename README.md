# Hermes Knowledge Base

个人知识库，由 Hermes agent 自动维护。

## 用途

保存文章、书籍、论文、视频、项目的完整中文翻译、摘要、背景资料和个人笔记。

## 目录结构

| 目录 | 说明 |
|------|------|
| `inbox/raw/` | 原始素材（未处理的网页、PDF、截图等） |
| `content/articles/` | 外部文章（有 source_url，需翻译） |
| `content/books/` | 书籍 |
| `content/papers/` | 论文 |
| `content/videos/` | 视频 |
| `content/projects/` | 项目文档（有 source_url，无翻译） |
| `content/legacy-knowledge/` | 旧知识库迁移内容（中文笔记，无翻译） |
| `index/` | 索引和目录 |
| `scripts/` | 自动化脚本 |
| `templates/` | 模板 |
| `reports/` | 运行报告 |

## 当前内容类型

<!-- KB_STATE_START — auto-updated by scripts/audit_kb_state.py -->
<!-- Run `python3 scripts/audit_kb_state.py` to refresh; do not edit manually. -->
<!-- Real total = 54 items. Last refreshed: 2026-06-29 (v0.3.60). -->

| 类型 | 数量 | 说明 | 目录 |
|------|------|------|------|
| article | 25 | 外部文章（含 wechat 子集），有 source_url，需翻译 | `content/articles/` |
| essay | 8 | 散文 / 自传性长文，与 article 同等需要翻译 | `content/articles/` |
| note | 9 | 中文笔记，无翻译，来源 `legacy-knowledge` 或 `notes` | `content/legacy-knowledge/`, `content/notes/` |
| resource_collection | 5 | 资源集合（结构化列表，无翻译） | `content/resource_collections/` + `content/collections/`（遗留目录，请勿新建条目） |
| project | 4 | 项目文档（有 source_url，无翻译） | `content/projects/` |
| video | 1 | YouTube 视频知识包（transcript + cards + analysis） | `content/articles/` |
| academic_paper | 1 | 学术论文（tandfonline 等） | `content/papers/` |
| interview | 1 | 长访谈（视频/播客转录） | `content/articles/` |
| **总计** | **54** | — | — |

<!-- KB_STATE_END -->

## 质量检查命令

```bash
python3 scripts/check_kb.py
python3 scripts/check_translation_residue.py
python3 scripts/build_index.py
python3 scripts/check_pages_sync.py
```

**任务启动前 preflight（v0.3.38+）：**

```bash
python3 scripts/check_task_preflight.py              # 普通任务
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name  # versioned task
```

| 脚本 | 用途 | 预期结果 |
|------|------|----------|
| `check_kb.py` | 检查 metadata 完整性 | PASS（详见 `audit_kb_state.py` 输出的"真实条目总数"） |
| `check_translation_residue.py` | 检查翻译残留 | WARNING 可接受 |
| `build_index.py` | 重建索引 | 与 `audit_kb_state.py` 输出的"真实条目总数"一致 |
| `check_pages_sync.py` | 检查 site/ 与 docs/ 发布文件一致 | PASS |
| `check_task_preflight.py` | 任务启动前检查 | PASS / PASS_WITH_WARNINGS |
| `audit_kb_state.py` *(v0.3.60+)* | 状态审计：检查 README 数字漂移、目录漂移、类型漂移、catalog 同步 | PASS_WITH_WARNINGS（历史 drift 不阻塞，仅 WARN） |

## 本地浏览知识库

```bash
# 1. 导出站点数据
python3 scripts/export_site_data.py

# 2. 启动本地服务器
python3 -m http.server 8000 -d site

# 3. 浏览器打开
# http://localhost:8000
```

## 维护方式

- Hermes agent 自动抓取、翻译、归档
- `scripts/build_index.py` 自动更新索引
- `scripts/check_kb.py` 检查内容完整性
- 所有内容通过 metadata.yaml 管理元数据

## 状态标记

- `captured` — 已捕获，待处理
- `translated` — 已翻译
- `summarized` — 已摘要
- `reviewed` — 已审阅
- `archived` — 已归档

## 导入文章

### 短命令（推荐）

直接对 Hermes 说：

- "把这篇文章完整翻译并加入知识库：https://example.com/article"
- "入库并完整翻译：https://example.com/article"
- "加入知识库：https://example.com/article"
- "翻译后入库：https://example.com/article"

Hermes 会自动执行完整导入流程，无需追问（除非遇到付费墙、无法访问、多个 URL 等特殊情况）。

默认行为：
- `content_type` = `article`
- 翻译语言 = `zh-CN`
- 目录名自动使用 `YYYY-MM-DD-来源-slug`
- tags/topics 由 Hermes 根据内容自动判断
- 自动 commit 并 push

### 导入后自动执行的质量检查

每篇文章导入完成后，Hermes 会自动运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/check_translation_residue.py
```

**check_kb.py** 必须 PASS，否则修复问题后再继续。  
**update_site.py** 必须 PASS，确保 site/ 和 docs/ 同步完成。  
**check_translation_residue.py** 可以有 warning，但严重残留必须修复。

### 质量门禁规则

| 检查项 | 要求 | 失败处理 |
|--------|------|----------|
| metadata.yaml 字段完整 | 必须包含 title, title_zh, source_url, source_site, author, published_date, captured_date, language, translation_language, status, type, topics, tags, word_count | 修复后重新检查 |
| title_zh | 非空，不得为 PLACEHOLDER | 补充中文标题 |
| word_count | source > 0, translation > 0 | 重新计算并写入 |
| tags | 6-12 个 *(soft guideline，audit_kb_state.py 仅 WARN，不阻断；细粒度可发现性的条目如 listicle 视频/音乐可超出)* | 调整数量 |
| topics | 3-8 个 *(soft guideline，audit_kb_state.py 仅 WARN，不阻断)* | 调整数量 |
| 翻译完整性 | 无大段英文残留、无漏译、无乱码 | 修复翻译 |
| notes.md | 使用统一模板 | 替换为 templates/notes.md |
| 在线浏览页同步 | update_site.py PASS | 修复同步问题 |

### 强制停止条件

以下情况 Hermes 必须停止导入，向用户报告，不要强行入库：

- URL 无法访问或返回 404/403/500
- 正文抓取不完整（明显截断、缺少关键章节）
- 文章需要登录或付费才能阅读完整内容
- 内容类型不明确
- 翻译后英文残留严重（suspicious_count ≥ 20）
- metadata 关键字段无法确定

### 模板化 Prompt（高级）

如需自定义导入流程，使用模板：

```bash
cp templates/prompts/import_article_prompt.md /tmp/my_import.md
# 替换占位符后发送给 Hermes
```

详见 `templates/prompts/import_article_prompt.md` 和 `docs/AGENT_COMMANDS.md`。

## 微信公众号文章入库

Hermes Knowledge Base 支持将微信公众号文章全文入库保存。

### 能力说明

将微信公众号文章（通过 OpenClaw @tencent-weixin/openclaw-weixin 读取全文）转换为：
- `metadata` — 文章元数据（含 content_kind, source_platform, dedupe_key, wechat, capture 字段）
- `source.md` — 原文全文
- `translation.zh-CN.md` — 清洗后的中文正文（V1 可与 source.md 一致）
- `summary.md` — 文章摘要
- `notes.md` — 结构化笔记
- `raw_payload.json` — 原始 JSON 捕获包备份
- `KB 条目` — 知识库正式条目
- `GitHub Pages 站点更新` — 自动发布到浏览站点

### 最短命令

在微信中直接对 Hermes 说：

```
把这篇公众号文章加入 Hermes 知识库
```

或：

```
入库这篇公众号文章
```

或：

```
保存这篇公众号全文到知识库
```

### 输出目录

```
content/articles/YYYY/YYYY-MM-DD-wechat-<account-slug>-<title-slug>/
```

### 输出文件

| 文件 | 说明 |
|------|------|
| `metadata.yaml` | 知识库元数据（含 wechat / capture 字段） |
| `source.md` | 原文全文 |
| `translation.zh-CN.md` | 清洗后的中文正文 |
| `summary.md` | 文章摘要 |
| `notes.md` | 结构化笔记 |
| `raw_payload.json` | 原始 JSON 捕获包 |

### 质量检查命令

```bash
cd ~/hermes-knowledge-base
python3 scripts/check_task_preflight.py
python3 -m py_compile scripts/import_wechat_article_capture.py
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/check_translation_residue.py
git status
```

| 检查项 | 要求 | 失败处理 |
|--------|------|----------|
| content_markdown 完整性 | 非空、非截断、非仅摘要 | 拒绝入库，报告原因 |
| word_count | source > 0, translation > 0，整数 | 重新计算 |
| metadata.yaml 字段 | 含 content_kind, source_platform, dedupe_key | 补充缺失字段 |
| tags | 6-12 个 | 调整数量 |
| topics | 3-8 个 | 调整数量 |

### 强制停止条件

以下情况 Hermes 必须停止导入，向用户报告，不要强行入库：

- content_markdown 为空或明显截断
- 文章只有摘要，没有正文主体
- 内容需要登录或付费才能阅读完整内容
- 文章已删除或违规无法查看
- metadata 关键字段无法确定（如 title、source_url 缺失）

### 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 导入工作流 | `docs/workflows/wechat-article-kb-import-workflow.md` | 完整入库流程 |
| 导入命令 | `docs/commands/wechat-article-kb-import-command.md` | 快捷命令说明 |
| 导入 Prompt | `templates/prompts/import_wechat_article_prompt.md` | Agent 处理规则 |
| 导入脚本 | `scripts/import_wechat_article_capture.py` | 自动化脚本 |

## YouTube 视频知识包

Hermes Knowledge Base 支持将 YouTube 视频转换为完整的中文知识包。

### 能力说明

将 YouTube 视频（含字幕）转换为：
- `metadata` — 视频元数据
- `transcript.original` — 原始字幕（英文）
- `transcript.zh` — 中文字幕
- `transcript.bilingual` — 双语对照字幕
- `analysis.zh` — 深度解读
- `summary-post.zh` — 分享文章
- `notes` — 永久笔记
- `cards` — 知识卡片
- `preflight-failure-archive` — 失败预检归档（如视频不可访问）
- `KB 条目` — 知识库正式条目
- `GitHub Pages 站点更新` — 自动发布到浏览站点

### 最短命令

```
预检这个 YouTube 视频：<YOUTUBE_URL>
解读这个 YouTube 视频并加入 Hermes 知识库：<YOUTUBE_URL>
```

### 预检命令

在正式解读前，先判断视频是否可处理：

```
预检这个 YouTube 视频：<YOUTUBE_URL>
```

预检结果：
- **PASS**：视频可访问且有字幕 → 继续解读和入库
- **BLOCKED**：视频不可访问或无字幕 → 停止并归档失败

### 输出结构

**成功视频**：
```
content/articles/YYYY/YYYY-MM-DD-video-slug/
├── metadata.yaml
├── summary.md
├── notes.md
├── source.md
├── translation.zh-CN.md
├── cards.md
└── ...
```

**失败预检**：
```
data/youtube-preflight-failures/YYYY/YYYY-MM-DD-video-id.json
data/youtube-preflight-failures/YYYY/YYYY-MM-DD-video-id.md
```

### 安全边界

- 不登录 YouTube 账号
- 不读取浏览器 Cookie
- 不下载完整视频（只提取字幕和元数据）
- 不绕过地区限制或私密限制
- 不处理私密视频
- 不伪造字幕或元数据
- 不可访问视频直接 BLOCKED 并归档，不继续处理

### 相关文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 视频解读工作流 | `docs/workflows/youtube-video-brief-workflow.md` | 从 URL 到知识包的完整流程 |
| 一键入库工作流 | `docs/workflows/youtube-video-kb-import-workflow.md` | 将知识包导入知识库 |
| 链接预检工作流 | `docs/workflows/youtube-link-preflight-workflow.md` | 入库前的预检判断 |
| 视频解读命令 | `docs/commands/youtube-brief-command.md` | 视频解读快捷命令 |
| 一键入库命令 | `docs/commands/youtube-kb-import-command.md` | 入库快捷命令 |
| 预检命令 | `docs/commands/youtube-preflight-command.md` | 预检快捷命令 |

### 版本演进

| 版本 | 内容 |
|------|------|
| v0.3.18 | 视频解读成功案例（Conan O'Brien 毕业演讲） |
| v0.3.19 | 一键视频入库命令能力建设 |
| v0.3.20 | 真实视频入库试运行（Dario Amodei 采访） |
| v0.3.21 | 链接预检与失败归档机制 |

---

## 浏览知识库

### 在线访问

GitHub Pages: https://conanxin.github.io/hermes-knowledge-base/

### 更新在线浏览页

新增知识库内容后，同步更新线上浏览页：

```bash
python3 scripts/build_index.py
python3 scripts/export_site_data.py
python3 scripts/sync_pages_docs.py
git status
```

或一键运行：

```bash
python3 scripts/update_site.py
```

### 本地运行

```bash
python3 scripts/export_site_data.py
python3 scripts/generate_item_pages.py
python3 -m http.server 8000 -d site
```

浏览器打开 http://localhost:8000

功能：
- 按类型筛选（article / note / project / resource_collection）
- 关键词搜索（标题、标签、主题）
- 按日期倒序排列
- **每张卡片标题和"阅读 →"按钮进入站内详情页**（`/items/<slug>/`）
- 卡片右侧 **GitHub 文件夹** 按钮仍可打开 GitHub 原始目录
- 一键复制 path

### 站内详情页（v0.3.8+）

每条记录除了 GitHub 原始目录外，还在 GitHub Pages 内部生成独立阅读页：

```
https://conanxin.github.io/hermes-knowledge-base/items/<slug>/
```

例如：<https://conanxin.github.io/hermes-knowledge-base/items/2026-06-22-your-ai-is-not-a-tool/>

详情页结构（v0.3.9 起为每种类型提供差异化的默认展开/折叠）：

| 区域 | 内容 |
|------|------|
| 顶部 | 返回首页链接 |
| 标题 | `title_zh` + 英文副标题 `title` |
| 目录 TOC | 来自正文主体的 h2/h3 标题（带编号 + 平滑滚动到锚点） |
| 元数据 | 类型、作者、来源、发布日期、采集日期、迁移日期、标签、主题 |
| 摘要 summary.md | 默认展开（所有类型） |
| 主体正文 | 文章=中文翻译 / 资源集合=collection / 笔记·项目=source。默认展开 |
| 原文 / 笔记 | 默认折叠，长文不会撑爆页面 |
| 底部 | 原文链接（如有）+ GitHub 文件夹 + 复制 path |
| 浮窗 | 滚动 400px 后右下角出现"↑ 返回顶部" |

可选文件缺失时，详情页显示"暂无该部分"，不会崩溃。

类型差异化默认展开/折叠（v0.3.9+）：

| 类型 | summary | translation / collection / source | source (次要) | notes |
|------|---------|------------------------------------|----------------|-------|
| article | 展开 | 展开（translation） | 折叠 | 折叠 |
| resource_collection | 展开 | 展开（collection） | — | 折叠 |
| note | 展开 | 展开（source） | — | 折叠 |
| project | 展开 | 展开（source） | — | 折叠 |

> 用户随时可以点击 section 标题手动展开/折叠，状态**不**持久化。

`update_site.py` 一键重建并同步：

```bash
python3 scripts/update_site.py
# 硬性执行顺序：
#   0. check_kb.py            ← 质量门禁，FAIL 立即停止
#   1. build_index.py
#   2. export_site_data.py
#   3. generate_item_pages.py
#   4. sync_pages_docs.py
```

## Releases

See [CHANGELOG.md](CHANGELOG.md) and [docs/RELEASES.md](docs/RELEASES.md) for version history and release notes.

- **Latest YouTube capability entry**: [`v0.3.24-youtube-public-entry-qa`](https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.24-youtube-public-entry-qa)
- **Music player fix**: [`v0.3.22-music-player-js-loader-fix`](https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.22-music-player-js-loader-fix)

---

## 质量门禁（硬性规则）

`update_site.py` 已在最前面内置 `check_kb.py` 硬停止：

1. `check_kb.py` 失败 → `update_site.py` 立即返回非 0，**不会**运行 build / export / generate / sync，**不会**触碰 `site/data/catalog.json` 或 `docs/`。
2. `check_kb.py` 失败时**严禁** commit / push。
3. `word_count` 字段必须是 YAML 对象，**不允许**用带引号的字符串或裸数字。规范格式：

   ```yaml
   word_count:
     source: 4434        # 整数（source.md 实际词数）
     translation: 7079   # 整数（translation.zh-CN.md 实际 CJK 字数）
   ```

   不允许：`word_count: 4500`、`word_count: "4500"`、`word_count: "~4500"`、`word_count: 约4500`。
4. 半成品条目（缺文件、字段为 0、翻译不完整）必须先修复或隔离到 `inbox/quarantine/`，再继续执行 `update_site.py`。
5. 除非用户明确说"先不要 commit/push"，否则完整导入流程应自动运行到 check → update_site → commit → push；但当 check 失败时必须立即停止并报告。
