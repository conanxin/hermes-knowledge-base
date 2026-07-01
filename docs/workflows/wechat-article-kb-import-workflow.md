# WeChat Official Account Article KB Import — OpenClaw Workflow

> **版本**: 1.2（v1.0 = OpenClaw 捕获包；v1.1 = 公开 URL 直抓 + 本地文件兜底，`v0.3.69`；v1.2 = 批量入库 + 三层去重，`v0.3.71`）
> **创建时间**: 2026-06-29
> **最近更新**: 2026-07-01
> **来源**: 基于 OpenClaw @tencent-weixin/openclaw-weixin 能力 + `scripts/wechat_url_to_kb.py` 公开抓取通道 + `scripts/wechat_batch_import.py` 批量通道
> **基线脚本**: `scripts/import_wechat_article_capture.py`（捕获包 → KB 条目）
> **单篇入口**: `scripts/wechat_url_to_kb.py`（URL/本地文件 → 捕获包 → 调用基线脚本）
> **批量入口**: `scripts/wechat_batch_import.py`（多 URL/本地文件 → 逐篇调用单篇入口 → 三层去重 → manifest 报告）

---

## 工作流名称

**WeChat Article KB Import** — 一键把微信公众号文章全文加入 Hermes Knowledge Base

## 一句话描述

两条入口，同一个落点：
1. **OpenClaw 通道**（v1.0）：基于 OpenClaw 读取的微信公众号文章全文捕获包，自动完成知识库入库、索引更新和站点发布。
2. **公开 URL / 本地文件通道**（v1.1，本节新增）：只给一个 `mp.weixin.qq.com` 链接或本地另存的 HTML/Markdown/TXT，`scripts/wechat_url_to_kb.py` 抓取公开页面、解析正文、生成标准 capture JSON，再交给同一条基线入库流程。**不登录、不扫码、不读 cookie、不绕过微信访问限制。**

---

## v1.1 新增：公开 URL 直抓 + 本地文件兜底

### 最短命令（WorkBuddy 里直接说）

```
解读并入库这篇公众号文章：
<mp.weixin.qq.com 链接>
```

WorkBuddy 翻译为：

```bash
python3 scripts/wechat_url_to_kb.py --url "<mp.weixin.qq.com 链接>" --import
```

### 本地文件兜底命令

链接抓不到全文时，浏览器另存为 HTML/Markdown/TXT，然后说：

```
解读并入库这个公众号文章本地文件：
<本地 html/md/txt 路径>
```

WorkBuddy 翻译为四选一：

```bash
python3 scripts/wechat_url_to_kb.py --html-file  <path> --import
python3 scripts/wechat_url_to_kb.py --markdown-file <path> --import
python3 scripts/wechat_url_to_kb.py --text-file <path> --import
```

### URL 通道执行步骤（替代 Step 0 ~ Step 2）

```bash
# Step A: 抓取 + 生成 capture JSON + 跑 import 脚本 dry-run（不写条目）
python3 scripts/wechat_url_to_kb.py --url "<链接>" --dry-run

# Step B: 真的入库
python3 scripts/wechat_url_to_kb.py --url "<链接>" --import
```

`--import` 内部会：抓取 → 解析 → 写 `inbox/raw/wechat/YYYY-MM-DD-<slug>.json` → 调用 `scripts/import_wechat_article_capture.py`（无 `--dry-run`，写 KB 条目）。

### 硬停止条件（HARD STOP，不写半成品）

`wechat_url_to_kb.py` 在以下情况退出码 1，只生成报告，不写 KB 条目：

- 获取不到完整正文 / 页面要求登录 / 页面只返回摘要
- 正文明显截断（命中 `... / 阅读全文 / 前往阅读` 等标记）
- 只有标题没有正文
- 微信拦截公开访问（命中"请在微信客户端打开"等阻断短语）
- 无法确认标题和正文对应
- `import_wechat_article_capture.py` 校验失败（exit 1）

遇到硬停止时脚本提示：

> 这个链接无法直接抓全文，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。

详见 [`docs/commands/wechat-url-kb-import-command.md`](../commands/wechat-url-kb-import-command.md)。

---

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `JSON 捕获包` | OpenClaw 通道必填 | — | OpenClaw 读取到的公众号文章全文，包含 title、source_url、account_name、author、published_date、captured_at、content_markdown |
| `公众号 URL` | URL 通道必填 | — | `mp.weixin.qq.com` 公开链接，由 `wechat_url_to_kb.py --url` 抓取 |
| `本地文件` | 本地通道必填 | — | HTML / Markdown / TXT，由 `wechat_url_to_kb.py --html-file/--markdown-file/--text-file` 解析 |
| `目标仓库` | ❌ | `~/hermes-knowledge-base` | Hermes Knowledge Base 本地路径 |

> 三种入口最终都汇聚到同一条基线：`scripts/import_wechat_article_capture.py`。

---

## 前置条件

1. **OpenClaw 已接入 @tencent-weixin/openclaw-weixin**（仅 OpenClaw 通道需要；URL/本地文件通道不需要）
2. **Hermes Knowledge Base 仓库已 clone** — 本地有 `~/hermes-knowledge-base` 且 remote 指向 `conanxin/hermes-knowledge-base`
3. **仓库状态 clean** — 无未提交的修改（本任务除外）
4. **Python 环境**：URL/HTML 通道需要 `requests` + `beautifulsoup4`；Markdown/TXT 通道只需标准库

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

### v1.1 URL 直抓（推荐，不需要 OpenClaw）

```
解读并入库这篇公众号文章：
<mp.weixin.qq.com 链接>
```

### v1.1 本地文件兜底

```
解读并入库这个公众号文章本地文件：
<本地 html/md/txt 路径>
```

### v1.0 OpenClaw 通道

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
| 导入命令（OpenClaw 通道） | `docs/commands/wechat-article-kb-import-command.md` | v1.0 快捷命令 |
| 导入命令（URL/本地文件通道） | `docs/commands/wechat-url-kb-import-command.md` | v1.1 单篇快捷命令 |
| 导入命令（批量通道） | `docs/commands/wechat-batch-kb-import-command.md` | v1.2 批量快捷命令 |
| 导入 Prompt | `templates/prompts/import_wechat_article_prompt.md` | Agent 处理规则 |
| 单篇入口脚本 | `scripts/wechat_url_to_kb.py` | URL/本地文件 → capture JSON → 入库 |
| 批量入口脚本 | `scripts/wechat_batch_import.py` | 多 URL/本地文件 → 三层去重 → manifest 报告 |
| 基线脚本 | `scripts/import_wechat_article_capture.py` | capture JSON → KB 条目 |
| 测试 fixture | `tests/fixtures/wechat_sample_article.html` | 离线测试用公众号 HTML |
| 测试 fixture（徒步 + /AI/ 陷阱） | `tests/fixtures/wechat_sample_hiking_article.html` | v0.3.70 回归 guard |
| 批量测试 fixture | `tests/fixtures/wechat_batch_urls.txt` 等 | v0.3.71 批量 smoke |
| 单篇 smoke | `tests/run_smoke_tests.py` | v0.3.70 smoke 套件 |
| 批量 smoke | `tests/run_wechat_batch_smoke.py` | v0.3.71 批量 smoke 套件 |

---

## v1.2 新增：批量入库 + 三层去重

### 最短命令（WorkBuddy 里直接说）

```
批量解读并入库这些公众号文章：
<urls.txt 或多行 URL>
```

本地文件批量：

```
批量解读并入库这些公众号本地文件：
<files.txt 或多行 .html/.md/.txt 路径>
```

### 底层调用

```bash
python3 scripts/wechat_batch_import.py --input urls.txt --dry-run
python3 scripts/wechat_batch_import.py --input urls.txt --import
python3 scripts/wechat_batch_import.py --url "<u1>" --url "<u2>" --import
```

### 三层去重

| 层 | 键 | 说明 |
|----|----|------|
| Layer 1 | `source_url` | URL 归一化后比对 `content/**/metadata.yaml` |
| Layer 2 | `title + account_name + published_date` | 三元组完全一致 |
| Layer 3 | `sha256(visible_text)` | 清洗后正文内容哈希 |

重复输入标记 `SKIPPED_DUPLICATE` / `DRY_RUN_DUPLICATE`，`duplicate_of` 写明已存在的 KB 路径。同一批次内也会去重。

### 失败隔离

单篇失败（`BLOCKED_FETCH_FAILED` / `BLOCKED_INCOMPLETE_TEXT` / `FAILED_IMPORT`）不中断整批。所有文章处理完后，若 `--import` 且 ≥1 篇 IMPORTED，自动运行四项质量门禁；门禁失败 → 退出码 2，manifest 标 `FAILED_GATE`，不 commit / 不 push。

### manifest

```
reports/wechat_batch_import_YYYYMMDD_HHMMSS.md
reports/wechat_batch_import_YYYYMMDD_HHMMSS.json
```

详见 [`docs/commands/wechat-batch-kb-import-command.md`](../commands/wechat-batch-kb-import-command.md)。

------

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
