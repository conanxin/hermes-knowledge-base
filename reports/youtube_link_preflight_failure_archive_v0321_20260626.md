# YouTube Link Preflight & Failure Archive 报告

**任务名称**: YOUTUBE_LINK_PREFLIGHT_FAILURE_ARCHIVE_V0321
**执行时间**: 2026-06-26
**基线版本**: v0.3.20-youtube-kb-import-pilot
**基线 commit**: ae1458c

---

## 执行状态

**状态**: PASS

---

## 新增文档

### Workflow 文档

| 文件 | 说明 |
|------|------|
| `docs/workflows/youtube-link-preflight-workflow.md` | YouTube 链接预检工作流 |

**内容要点**:
- 工作流目标：在正式处理 YouTube 视频前，先判断链接是否适合进入视频解读与知识库入库流程
- 标准预检步骤：解析 URL → 检查可访问性 → 检查字幕 → 分类失败 → 生成归档
- 失败分类：11 种失败类型（video_unavailable, private_video, deleted_video 等）
- 安全边界：不登录、不读 Cookie、不下载完整视频、不绕过限制

### Command 文档

| 文件 | 说明 |
|------|------|
| `docs/commands/youtube-preflight-command.md` | youtube-preflight 命令 |

**内容要点**:
- 命令名称：youtube-preflight
- 输出状态：PASS / BLOCKED / PARTIAL
- 失败归档规则：data/youtube-preflight-failures/YYYY/YYYY-MM-DD-<video-id>.json/.md
- 禁止行为：不登录、不读 Cookie、不下载完整视频、不绕过限制

### 更新的一键入库文档

| 文件 | 更新内容 |
|------|---------|
| `docs/workflows/youtube-video-kb-import-workflow.md` | 新增 Step 0: YouTube 链接预检 |
| `docs/commands/youtube-kb-import-command.md` | 新增预检前置要求和失败返回格式 |

---

## 失败归档

### 已知失败案例

| 属性 | 值 |
|------|-----|
| 视频 ID | U9Im71aNhYu |
| 失败类型 | video_unavailable |
| 预检时间 | 2026-06-26 |
| 尝试方法 | yt-dlp metadata-only, curl 标准 UA, curl 替代 UA |

### 归档文件

| 文件 | 路径 |
|------|------|
| JSON | `data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.json` |
| MD | `data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.md` |

---

## 新增知识库能力文章

| 文件 | 路径 |
|------|------|
| 能力文章目录 | `content/articles/2026/2026-06-26-youtube-link-preflight-failure-archive/` |

**文件清单**:
- `metadata.yaml` — 知识库元数据
- `summary.md` — 通俗文章，说明为什么需要预检、失败归档的价值
- `notes.md` — 结构化能力笔记，包含预检流程、失败分类、安全边界
- `source.md` — 能力来源和关联文档引用
- `translation.zh-CN.md` — 中文原文说明

---

## 检查脚本结果

| 脚本 | 状态 | 说明 |
|------|------|------|
| `check_kb.py` | PASS | 38 items, 0 failures |
| `build_index.py` | PASS | 38 records, 411 tags, 29 authors |
| `update_site.py` | PASS | 5/5 steps OK, pages sync PASS |

---

## 索引状态

| 指标 | 数值 |
|------|------|
| Records | 38 |
| Tags | 411 |
| Authors | 29 |
| Months | 4 |

---

## git diff 摘要

**新增文件**:
- `docs/workflows/youtube-link-preflight-workflow.md`
- `docs/commands/youtube-preflight-command.md`
- `content/articles/2026/2026-06-26-youtube-link-preflight-failure-archive/` (5 files)
- `data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.json`
- `data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.md`
- `docs/items/2026-06-26-youtube-link-preflight-failure-archive/` (1 file)
- `site/items/2026-06-26-youtube-link-preflight-failure-archive/` (1 file)

**修改文件**:
- `docs/workflows/youtube-video-kb-import-workflow.md` (新增 Step 0)
- `docs/commands/youtube-kb-import-command.md` (新增预检要求)
- 索引更新产物（catalog.jsonl, tags.md, authors.md, timeline.md, catalog.json）

---

## 提交信息

| 字段 | 值 |
|------|-----|
| Commit | 900e9c2 |
| Message | Add YouTube preflight and failure archive |
| Push | success |

---

## 后续建议

1. **v0.3.21 tag**: 建议创建 tag 标记本次预检能力建设完成
2. **实战验证**: 用新的 youtube-preflight 处理几个 YouTube 链接，验证预检逻辑
3. **失败模式分析**: 定期分析 failure archive，发现常见失败模式
4. **多平台扩展**: 将预检能力扩展到 Vimeo、Bilibili 等平台

---

*报告生成时间: 2026-06-26*
