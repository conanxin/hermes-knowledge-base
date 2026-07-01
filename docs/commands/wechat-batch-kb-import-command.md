# wechat-batch-kb-import

> **命令名称**: `wechat-batch-kb-import`
> **用途**: 一次给多个公众号链接（或本地文件），自动批量完成"抓取 → 解析 → 去重 → 入库 → 详情页 → 报告"
> **Workflow**: [`docs/workflows/wechat-article-kb-import-workflow.md`](../workflows/wechat-article-kb-import-workflow.md)
> **入口脚本**: `scripts/wechat_batch_import.py`
> **单篇脚本**: `scripts/wechat_url_to_kb.py`（v0.3.69）
> **入库脚本**: `scripts/import_wechat_article_capture.py`
> **创建时间**: 2026-07-01
> **版本**: 1.0
> **任务标签**: `v0.3.71-wechat-batch-import-dedup-report`

---

## 一句话说明

输入一个 URL 列表文件（或多行 URL，或多个本地文件），脚本逐篇调用 `wechat_url_to_kb.py` 完成"抓取 → capture JSON → 入库"，三层去重防止重复导入，单篇失败不中断整批，最后生成 markdown + json 双格式 manifest 报告。

---

## 最短调用方式

### 批量 URL（推荐）

在 WorkBuddy 里直接说：

```
批量解读并入库这些公众号文章：
<urls.txt>
```

或粘贴多行 URL：

```
批量解读并入库这些公众号文章：
https://mp.weixin.qq.com/s/xxx
https://mp.weixin.qq.com/s/yyy
https://mp.weixin.qq.com/s/zzz
```

### 批量本地文件

链接抓不到时，把每篇另存为 HTML/MD/TXT，然后：

```
批量解读并入库这些公众号本地文件：
<files.txt>
```

WorkBuddy 把它翻译成：

```bash
python3 scripts/wechat_batch_import.py --input <urls.txt> --import
```

---

## 脚本支持的完整参数

```bash
python3 scripts/wechat_batch_import.py \
    (--input <file>) ... \
    (--url "<url>") ... \
    (--html-file <path>) ... \
    (--markdown-file <path>) ... \
    (--text-file <path>) ... \
    [--dry-run | --import] \
    [--no-gates]
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--input <file>` | 多选一 | 文件，每行一个 URL 或本地路径；空行和 `#` 开头跳过；可重复 |
| `--url "<url>"` | 多选一 | 单个 mp.weixin.qq.com URL；可重复 |
| `--html-file <path>` | 多选一 | 单个本地 HTML 文件；可重复 |
| `--markdown-file <path>` | 多选一 | 单个本地 Markdown 文件；可重复 |
| `--text-file <path>` | 多选一 | 单个本地纯文本文件；可重复 |
| `--dry-run` | 默认 | 每篇都跑 capture + 去重检查，但**不写 KB 条目** |
| `--import` | 可选 | 真的写入 KB 条目；末尾自动跑质量门禁 |
| `--no-gates` | 可选 | 跳过末尾的质量门禁（仅 `--import` 模式有效） |

> 既不传 `--dry-run` 也不传 `--import` 时，默认走 `--dry-run`（安全优先）。

### input 文件格式

- 每行一个 URL 或本地文件路径
- 空行跳过
- 以 `#` 开头的行跳过
- 支持 `mp.weixin.qq.com` URL
- 支持 `.html` / `.htm` / `.md` / `.markdown` / `.txt`

---

## 去重策略（三层）

去重在入库**之前**完成，重复的输入不会被再次写入。

| 层 | 键 | 说明 |
|----|----|------|
| Layer 1 | `source_url` | 扫 `content/**/metadata.yaml` 的 `source_url` 字段；URL 归一化（小写、去 fragment、去尾斜杠）后比对 |
| Layer 2 | `title + account_name + published_date` | 三元组完全一致即判重 |
| Layer 3 | `sha256(visible_text)` | 对 `source.md` 清洗后的可见正文算 sha256；正文一致即判重 |

- 重复输入标记为 `SKIPPED_DUPLICATE`（`--import` 模式）或 `DRY_RUN_DUPLICATE`（`--dry-run` 模式）
- manifest 里 `duplicate_of` 字段写明已存在的 KB 路径
- **同一批次内**也会去重：第 N 篇导入后，第 N+1 篇若命中相同键，也会被标记为重复

---

## 失败策略

单篇失败**绝不**中断整批：

| 失败类型 | 状态码 | 行为 |
|----------|--------|------|
| 抓取失败（网络/拦截） | `BLOCKED_FETCH_FAILED` | 记录，继续下一篇 |
| 正文不完整（截断/登录墙） | `BLOCKED_INCOMPLETE_TEXT` | 记录，继续下一篇 |
| 本地文件不存在 | `BLOCKED_FETCH_FAILED` | 记录，继续下一篇 |
| import 脚本失败 | `FAILED_IMPORT` | 记录，继续下一篇 |
| 质量门禁失败 | `FAILED_GATE` | 在 manifest 末尾记录，**不 commit / 不 push** |

所有文章处理完后，若 `--import` 模式且有 ≥1 篇 `IMPORTED`，自动运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

任一门禁失败 → 脚本退出码 2，manifest 标 `FAILED_GATE`，列出失败命令。

---

## manifest / 报告

每次批量运行生成两份 manifest：

```
reports/wechat_batch_import_YYYYMMDD_HHMMSS.md
reports/wechat_batch_import_YYYYMMDD_HHMMSS.json
```

每篇一行，字段：

- `input` / `input_type`
- `status`（IMPORTED / DRY_RUN_OK / DRY_RUN_DUPLICATE / SKIPPED_DUPLICATE / BLOCKED_FETCH_FAILED / BLOCKED_INCOMPLETE_TEXT / FAILED_IMPORT / FAILED_GATE）
- `title` / `account_name` / `published_date` / `source_url`
- `capture_json_path` / `kb_article_path` / `docs_item_path` / `site_item_path`
- `failure_reason` / `duplicate_of`

Markdown 报告含汇总表（total / imported / dry_run_ok / skipped_duplicate / blocked / failed）。

---

## 与既有命令的关系

| 命令 | 输入 | 适用场景 |
|------|------|----------|
| `wechat-url-kb-import`（v0.3.69） | 单个 URL / 本地文件 | 单篇 |
| **`wechat-batch-kb-import`（本命令，v0.3.71）** | URL 列表 / 多个本地文件 | 批量 + 去重 |
| `wechat-article-kb-import`（v1.0，OpenClaw） | capture JSON | OpenClaw 启用时 |

---

## 最小测试（无需网络）

```bash
# 1. 批量 dry-run 两个本地 fixture
python3 scripts/wechat_batch_import.py --input tests/fixtures/wechat_batch_urls.txt --dry-run

# 2. 重复检测（同一 fixture 出现两次 → 第二次 DRY_RUN_DUPLICATE）
python3 scripts/wechat_batch_import.py --input tests/fixtures/wechat_batch_duplicate_urls.txt --dry-run

# 3. 失败隔离（中间一个不存在的文件 → BLOCKED_FETCH_FAILED，其余正常）
python3 scripts/wechat_batch_import.py --input tests/fixtures/wechat_batch_failure_isolation.txt --dry-run

# 完整 smoke 套件
python3 tests/run_wechat_batch_smoke.py
```
