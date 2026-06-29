# WeChat Official Account Article KB Import — OpenClaw Workflow

> **版本**: 1.0
> **创建时间**: 2026-06-29
> **来源**: 基于 OpenClaw @tencent-weixin/openclaw-weixin 能力
> **基线脚本**: `scripts/import_wechat_article_capture.py`

---

## 工作流名称

**WeChat Article KB Import** — 一键把微信公众号文章全文加入 Hermes Knowledge Base

## 一句话描述

基于 OpenClaw 读取的微信公众号文章全文捕获包，自动完成知识库入库、索引更新和站点发布。

---

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `JSON 捕获包` | ✅ | — | OpenClaw 读取到的公众号文章全文，包含 title、source_url、account_name、author、published_date、captured_at、content_markdown |
| `目标仓库` | ✅ | `~/hermes-knowledge-base` | Hermes Knowledge Base 本地路径 |

---

## 前置条件

1. **OpenClaw 已接入 @tencent-weixin/openclaw-weixin** — 能够读取公众号文章全文
2. **Hermes Knowledge Base 仓库已 clone** — 本地有 `~/hermes-knowledge-base` 且 remote 指向 `conanxin/hermes-knowledge-base`
3. **仓库状态 clean** — 无未提交的修改（本任务除外）

---

## 标准执行步骤

### Step 0: 微信中转发文章

在微信中直接对 Hermes 说：

> "把这篇公众号文章加入 Hermes 知识库"

Hermes（通过 OpenClaw）会：
1. 读取文章全文
2. 生成 JSON 捕获包
3. 运行导入脚本

### Step 1: 检查仓库

进入知识库仓库，确认：
- `git remote -v` 指向 `conanxin/hermes-knowledge-base`
- 当前分支为 `main`
- `git status` 无未提交修改（允许未跟踪文件，但不得有已修改未提交文件）
- 目录结构：`content/articles/`、`scripts/` 存在

**如果存在非本任务相关的未提交改动 → BLOCKED**

### Step 2: 运行导入脚本

```bash
python3 scripts/import_wechat_article_capture.py <path-to-capture.json>
```

**脚本自动执行：**
- 验证 JSON 字段完整性
- 验证 content_markdown 是否完整（非空、非截断、非仅摘要）
- 生成目录名：`content/articles/YYYY/YYYY-MM-DD-wechat-<account-slug>-<title-slug>/`
- 生成 6 个文件：metadata.yaml、source.md、translation.zh-CN.md、summary.md、notes.md、raw_payload.json
- 计算 word_count（source 和 translation 均为整数）
- 生成 dedupe_key

**验证失败 → HARD STOP，不写入任何文件**

### Step 3: 执行知识库检查脚本

按顺序执行：

1. `python3 scripts/check_kb.py` — 检查知识库 schema 和完整性
2. `python3 scripts/check_translation_residue.py` — 检查翻译残留
3. `python3 scripts/update_site.py` — 更新站点（GitHub Pages）

**任何一步失败 → BLOCKED，不 commit**

### Step 4: 生成入库报告

创建报告：`reports/wechat_article_kb_import_YYYYMMDD.md`

报告必须包含：
- 任务名称
- 执行状态（PASS / BLOCKED）
- 导入的文章标题和来源
- 新增知识库条目路径
- 执行过的检查脚本及结果
- git diff 摘要
- commit hash
- push 结果
- 后续建议

### Step 5: 提交和推送

确认 `git diff` 只包含本任务相关文件后：

```bash
git add <本任务相关文件>
git commit -m "Add WeChat article KB import: <article-title>"
git push origin HEAD
```

**不要 force push。不要创建 tag（除非仓库现有流程明确要求）。**

---

## 成功判定

| 检查项 | 要求 |
|--------|------|
| 文章全文已捕获 | content_markdown 包含完整正文，非截断 |
| KB 条目已创建 | `content/articles/YYYY/YYYY-MM-DD-wechat-slug/` 存在且文件完整 |
| check_kb.py PASS | 检查脚本通过 |
| 索引/站点更新成功 | update_site.py 成功 |
| commit 成功 | 本地 commit 成功 |
| push 成功 | 远程同步成功 |

---

## 失败处理

### 内容不完整（content_markdown 为空、截断、仅摘要）
- **HARD STOP**
- 在报告中记录失败原因
- 建议：确认文章是否已删除、是否在付费墙后、是否只在微信客户端内可见

### 仓库 dirty（存在非本任务相关的未提交改动）
- **BLOCKED**
- 在报告中列出未提交文件清单
- 建议：先 stash 或提交其他改动，再重新执行本任务

### 检查脚本失败
- **BLOCKED**
- 在报告中记录失败脚本和错误信息
- 建议：修复脚本问题后重新执行

### 远程 push 失败
- **BLOCKED**
- 在报告中记录错误信息
- 建议：检查网络、权限，或手动 push

---

## 最短调用提示词

```
把这篇公众号文章加入 Hermes 知识库
```

或在微信中直接转发文章链接并说：

```
入库这篇公众号文章
```

---

## 完整调用提示词

```
请执行一个 Hermes Knowledge Base 入库任务。

任务名称：WECHAT_ARTICLE_TO_HERMES_KB_V1

目标：把这篇微信公众号文章全文加入到 GitHub 知识库。

JSON 捕获包路径：<path-to-capture.json>

已有 OpenClaw workflow：docs/workflows/wechat-article-kb-import-workflow.md
已有快捷命令文档：docs/commands/wechat-article-kb-import-command.md

Hermes Knowledge Base 仓库目录：~/hermes-knowledge-base
GitHub repo：https://github.com/conanxin/hermes-knowledge-base

硬约束：
1. 不要把公众号文章做成 standalone project。
2. 不要创建独立项目页。
3. 不要修改 conanxin.github.io/projects。
4. 内容不完整时 hard stop，不得写入半成品。
5. 只基于已有 JSON 捕获包做导入、整理、校验、提交、推送。
6. 不要 force push。
7. 如果仓库存在非本任务相关的未提交改动，先 BLOCKED 并报告。
8. 公共展示文章里不要暴露 /home/ubuntu 这类本机绝对路径。

执行步骤：
一、检查仓库（git remote、分支、status、结构）
二、运行导入脚本（import_wechat_article_capture.py）
三、执行检查脚本（check_kb.py → check_translation_residue.py → update_site.py）
四、生成报告
五、提交和推送

最终回复：
OPENCLAW_STATUS: PASS 或 BLOCKED
KB_REPO: ~/hermes-knowledge-base
ARTICLE_ENTRY: <文章知识库条目路径>
REPORT_PATH: <报告绝对路径>
COMMIT: <commit hash>
PUSH: success 或 failed
```

---

## 关联文档

| 文档 | 路径 | 说明 |
|------|------|------|
| 本 Workflow | `docs/workflows/wechat-article-kb-import-workflow.md` | 本文档 |
| 导入命令 | `docs/commands/wechat-article-kb-import-command.md` | 快捷命令 |
| 导入 Prompt | `templates/prompts/import_wechat_article_prompt.md` | Agent 处理规则 |

---

## 后续可扩展方向

### 1. 自动去重
- 基于 dedupe_key 检测重复文章
- 同一文章多次转发时自动识别并提示

### 2. 多文章批量入库
- 一次转发多个公众号文章链接
- 批量处理、批量 commit

### 3. 语义关联自动建立
- 基于文章内容自动提取关键词
- 与知识库已有条目建立双向链接
- 生成相关文章推荐列表

---

## 维护说明

- 每次执行成功后，更新报告中的 `commit` 和 `push` 字段
- 如遇到新类型的失败，更新"失败处理"章节
- 新增扩展方向时，在"后续可扩展方向"追加
- 版本升级时，更新版本号并记录变更日志

---

*Workflow 固化完成。可直接复制"最短调用提示词"或"完整调用提示词"使用。*
