# YouTube Video KB Import — OpenClaw Workflow

> **版本**: 1.0
> **创建时间**: 2026-06-26
> **来源**: 固化自 v0.3.18 成功案例（Conan O'Brien Harvard 2026）
> **基线 tag**: `v0.3.18-youtube-video-brief-kb-import`
> **基线 commit**: `87f5065`

---

## 工作流名称

**YouTube Video KB Import** — 一键把 YouTube 视频解读产物加入 Hermes Knowledge Base

## 一句话描述

基于已完成的 YouTube Video Brief 产物，自动完成知识库入库、能力说明补充、索引更新和站点发布。

---

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `视频解读产物目录` | ✅ | — | YouTube Video Brief 的输出目录，包含 metadata.json、analysis.zh.md、notes.md 等 |
| `目标仓库` | ✅ | `~/hermes-knowledge-base` | Hermes Knowledge Base 本地路径 |
| `文章日期` | ❌ | 当天日期 | 用于知识库条目命名，格式 `YYYY-MM-DD` |
| `文章 slug` | ❌ | 自动从视频标题生成 | 用于知识库条目目录名 |

---

## 前置条件

1. **YouTube Video Brief 已完成** — 必须已有完整的解读产物（至少包含 metadata.json、analysis.zh.md、notes.md）
2. **Hermes Knowledge Base 仓库已 clone** — 本地有 `~/hermes-knowledge-base` 且 remote 指向 `conanxin/hermes-knowledge-base`
3. **仓库状态 clean** — 无未提交的修改（本任务除外）

---

## 标准执行步骤

### Step 1: 检查仓库

进入知识库仓库，确认：
- `git remote -v` 指向 `conanxin/hermes-knowledge-base`
- 当前分支为 `main`
- `git status` 无未提交修改（允许未跟踪文件，但不得有已修改未提交文件）
- 目录结构：`content/articles/`、`docs/workflows/`、`docs/commands/`、`scripts/` 存在

**如果存在非本任务相关的未提交改动 → BLOCKED**

### Step 2: 创建知识库视频条目

在 `content/articles/YYYY/` 下创建目录：

```
content/articles/2026/2026-06-25-conan-harvard-commencement-2026/
├── metadata.yaml
├── summary.md
├── notes.md
└── source.md
```

**文件内容来源**：
- `metadata.yaml` — 从视频解读产物的 `metadata.json` 提取，补充知识库字段（type, category, tags, created, updated）
- `summary.md` — 从 `analysis.zh.md` 和 `summary-post.zh.md` 提炼，写成通俗文章
- `notes.md` — 从视频解读产物的 `notes.md` 整理，写成结构化能力笔记
- `source.md` — 引用 workflow 文档和 command 文档，不暴露本地绝对路径到公开正文

### Step 3: 同步 workflow / command 文档到知识库

将 OpenClaw 工作流文档复制到知识库 `docs/` 目录：

```
docs/workflows/youtube-video-brief-workflow.md
docs/commands/youtube-brief-command.md
```

如果 `docs/workflows` 或 `docs/commands` 不存在，则创建。

### Step 4: 新增知识库能力说明

创建新文章目录，说明"解读 YouTube 视频并生成中文知识包"的能力：

```
content/articles/2026/2026-06-25-youtube-video-brief-workflow/
├── metadata.yaml
├── summary.md
├── notes.md
└── source.md
```

**内容要点**：
- 这个能力是什么（端到端视频解读工作流）
- 输入是什么（YouTube URL）
- 输出是什么（11 个文件的知识包）
- 适合什么场景（学习、写作、研究、分享）
- 为什么适合进入知识库（可复用、标准化、累积、连接）
- 和 Hermes Knowledge Base 如何配合（直接存入、参与索引、自动发布）

### Step 5: 执行知识库检查脚本

按顺序执行（如果存在）：

1. `python3 scripts/check_kb.py` — 检查知识库 schema 和完整性
2. `python3 scripts/check_translation_residue.py` — 检查翻译残留
3. `python3 scripts/build_index.py` — 构建索引（catalog.jsonl、tags.md、authors.md、timeline.md）
4. `python3 scripts/update_site.py` — 更新站点（GitHub Pages）

**任何一步失败 → BLOCKED，不 commit**

### Step 6: 生成入库报告

创建报告：`reports/youtube_video_brief_kb_import_YYYYMMDD.md`

报告必须包含：
- 任务名称
- 执行状态（PASS / BLOCKED）
- 导入的视频知识包来源
- 新增视频知识库条目路径
- 新增能力说明条目路径
- 同步的 workflow / command 文档路径
- 执行过的检查脚本及结果
- git diff 摘要
- commit hash
- push 结果
- 后续建议

### Step 7: 提交和推送

确认 `git diff` 只包含本任务相关文件后：

```bash
git add <本任务相关文件>
git commit -m "Add YouTube video brief knowledge entry"
git push origin HEAD
```

**不要 force push。不要创建 tag（除非仓库现有流程明确要求）。**

---

## 成功判定

| 检查项 | 要求 |
|--------|------|
| 字幕已提取 | 视频产物包含 transcript.original.srt 或 .vtt |
| 中文稿已生成 | 视频产物包含 transcript.zh.md |
| analysis / notes / cards 已生成 | 视频产物包含对应文件 |
| KB 条目已创建 | `content/articles/YYYY/YYYY-MM-DD-slug/` 存在且文件完整 |
| check_kb.py PASS | 检查脚本通过 |
| 索引/站点更新成功 | build_index.py 和 update_site.py 成功（如果存在） |
| commit 成功 | 本地 commit 成功 |
| push 成功 | 远程同步成功 |

---

## 失败处理

### 仓库 dirty（存在非本任务相关的未提交改动）
- **BLOCKED**
- 在报告中列出未提交文件清单
- 建议：先 stash 或提交其他改动，再重新执行本任务

### 检查脚本失败
- **BLOCKED**
- 在报告中记录失败脚本和错误信息
- 建议：修复脚本问题后重新执行

### 缺少视频产物文件
- **BLOCKED**
- 在报告中记录缺失文件
- 建议：先执行 YouTube Video Brief 工作流，再执行本入库任务

### 远程 push 失败
- **BLOCKED**
- 在报告中记录错误信息
- 建议：检查网络、权限，或手动 push

### 索引/站点构建失败
- **BLOCKED**（如果仓库流程要求）
- 在报告中记录失败信息
- 建议：检查构建脚本依赖，或手动修复

---

## 最短调用提示词

```
请把这个 YouTube 视频解读产物加入知识库：
~/.openclaw/workspace/outputs/youtube-video-brief/20260625-conan-harvard-commencement-2026/
```

---

## 完整调用提示词

```
请执行一个 Hermes Knowledge Base 入库任务。

任务名称：YOUTUBE_BRIEF_TO_HERMES_KB_V1

目标：把已经解读完成的 YouTube 视频知识包加入到 GitHub 知识库。

视频解读产物目录：
~/.openclaw/workspace/outputs/youtube-video-brief/20260625-conan-harvard-commencement-2026/

已有 OpenClaw workflow：
~/.openclaw/workspace/docs/workflows/youtube-video-brief-workflow.md

已有快捷命令文档：
~/.openclaw/workspace/docs/commands/youtube-brief-command.md

Hermes Knowledge Base 仓库目录：~/hermes-knowledge-base
GitHub repo：https://github.com/conanxin/hermes-knowledge-base

硬约束：
1. 不要把知识库内容写到 standalone outputs 目录。
2. 不要重新下载视频。
3. 不要重新翻译字幕。
4. 不要重新生成解读内容。
5. 只基于已有产物做导入、整理、能力补充、校验、提交、推送。
6. 不要 force push。
7. 如果仓库存在非本任务相关的未提交改动，先 BLOCKED 并报告，不要覆盖。
8. 公共展示文章里不要暴露 /home/ubuntu 这类本机绝对路径；绝对路径只允许写在内部 report 里。

执行步骤：
一、检查仓库（git remote、分支、status、结构）
二、创建知识库视频条目（metadata.yaml + summary.md + notes.md + source.md）
三、同步 workflow / command 文档到知识库 docs/
四、新增知识库能力说明（YouTube Video Brief 能力文章）
五、执行检查脚本（check_kb.py → check_translation_residue.py → build_index.py → update_site.py）
六、生成报告
七、提交和推送

最终回复：
OPENCLAW_STATUS: PASS 或 BLOCKED
KB_REPO: /home/ubuntu/hermes-knowledge-base
VIDEO_ENTRY: <视频知识库条目路径>
WORKFLOW_ENTRY: <视频解读能力条目路径>
WORKFLOW_DOC: <知识库内 workflow 文档路径>
COMMAND_DOC: <知识库内 command 文档路径>
REPORT_PATH: <报告绝对路径>
COMMIT: <commit hash>
PUSH: success 或 failed
```

---

## 关联文档

| 文档 | 路径 | 说明 |
|------|------|------|
| YouTube Video Brief Workflow | `docs/workflows/youtube-video-brief-workflow.md` | 视频解读工作流 |
| youtube-brief Command | `docs/commands/youtube-brief-command.md` | 视频解读快捷命令 |
| YouTube KB Import Command | `docs/commands/youtube-kb-import-command.md` | 本工作流的快捷命令 |

---

## 后续可扩展方向

### 1. 自动检测最新产物
- 自动扫描 `~/.openclaw/workspace/outputs/youtube-video-brief/` 目录
- 检测尚未入库的新产物
- 批量入库或提示用户确认

### 2. 一键发布到多平台
- 从 `summary-post.zh.md` 提取内容
- 自动生成小红书、公众号、Twitter/X 格式
- 支持多平台并行发布

### 3. 语义关联自动建立
- 基于视频内容自动提取关键词
- 与知识库已有条目建立双向链接
- 生成相关视频推荐列表

### 4. 播客化
- 从 `analysis.zh.md` 生成播客提纲
- 自动生成 TTS 朗读稿
- 支持多语言播客版本

---

## 维护说明

- 每次执行成功后，更新报告中的 `commit` 和 `push` 字段
- 如遇到新类型的失败，更新"失败处理"章节
- 新增扩展方向时，在"后续可扩展方向"追加
- 版本升级时，更新版本号并记录变更日志

---

*Workflow 固化完成。可直接复制"最短调用提示词"或"完整调用提示词"使用。*
