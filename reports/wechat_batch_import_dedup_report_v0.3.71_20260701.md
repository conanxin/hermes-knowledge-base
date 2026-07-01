# WeChat Batch Import + Dedup Report — v0.3.71

- **任务标签**: `v0.3.71-wechat-batch-import-dedup-report`
- **创建时间**: 2026-07-01
- **STATUS**: **PASS**
- **commit message**: `Add WeChat batch import with dedup reporting`

---

## §1 STATUS

**PASS**

新增微信公众号文章批量入库能力：一次给多个 URL 或本地文件，逐篇抓取/解析/入库，三层去重防止重复导入，单篇失败不中断整批，最后生成 markdown + json 双格式 manifest 报告。所有门禁通过。

---

## §2 新增能力说明

### 批量入口

`scripts/wechat_batch_import.py` 支持：

- `--input <file>`：URL/路径列表文件（每行一个，空行和 `#` 跳过）
- `--url "<url>"`：单个 URL，可重复
- `--html-file <path>` / `--markdown-file <path>` / `--text-file <path>`：单个本地文件，可重复
- `--dry-run`（默认）/ `--import`
- `--no-gates`：跳过末尾质量门禁

### 复用既有能力

脚本内部通过 `subprocess` 调用 `scripts/wechat_url_to_kb.py`（v0.3.69 单篇入口），后者再调用 `scripts/import_wechat_article_capture.py`（基线入库）。没有复制抓取/解析/入库逻辑。

### 批量输入格式

**input 文件**（每行一个）：
- `mp.weixin.qq.com` URL
- `.html` / `.htm` / `.md` / `.markdown` / `.txt` 本地路径
- 空行跳过
- `#` 开头跳过

**WorkBuddy 短命令**：

```
批量解读并入库这些公众号文章：
<urls.txt 或多行 URL>
```

```
批量解读并入库这些公众号本地文件：
<files.txt 或多行 .html/.md/.txt 路径>
```

---

## §3 去重策略（三层）

去重在入库**之前**完成，重复输入不会被再次写入。

| 层 | 键 | 说明 |
|----|----|------|
| Layer 1 | `source_url` | URL 归一化（小写、去 fragment、去尾斜杠）后比对 `content/**/metadata.yaml` 的 `source_url` |
| Layer 2 | `title + account_name + published_date` | 三元组完全一致 |
| Layer 3 | `sha256(visible_text)` | 对 capture 的 `content_markdown` 调 `extract_visible_text()` 清洗后算 sha256 |

- 重复输入标记 `SKIPPED_DUPLICATE`（`--import`）或 `DRY_RUN_DUPLICATE`（`--dry-run`）
- manifest 里 `duplicate_of` 写明已存在的 KB 路径
- **同一批次内**也去重：第 N 篇导入后，第 N+1 篇若命中相同键，也会被标记为重复（dry-run 模式用合成 marker `(dry-run batch item #N)`）

---

## §4 失败策略

单篇失败**绝不**中断整批：

| 失败类型 | 状态码 | 行为 |
|----------|--------|------|
| 抓取失败（网络/拦截/非 200） | `BLOCKED_FETCH_FAILED` | 记录，继续下一篇 |
| 正文不完整（截断/登录墙/仅摘要） | `BLOCKED_INCOMPLETE_TEXT` | 记录，继续下一篇 |
| 本地文件不存在 | `BLOCKED_FETCH_FAILED` | 记录，继续下一篇 |
| import 脚本失败 | `FAILED_IMPORT` | 记录，继续下一篇 |
| 质量门禁失败 | `FAILED_GATE` | manifest 末尾记录，**不 commit / 不 push** |

所有文章处理完后，若 `--import` 且 ≥1 篇 `IMPORTED`，自动运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

任一门禁失败 → 脚本退出码 2，manifest 标 `FAILED_GATE`。

---

## §5 修改文件列表

### 新增

| 文件 | 说明 |
|------|------|
| `scripts/wechat_batch_import.py` | 批量入口 + 三层去重 + manifest 报告 |
| `docs/commands/wechat-batch-kb-import-command.md` | 批量命令短档 |
| `tests/fixtures/wechat_batch_urls.txt` | 批量 smoke fixture（两个本地 fixture） |
| `tests/fixtures/wechat_batch_duplicate_urls.txt` | 重复检测 fixture（同一 fixture 两次） |
| `tests/fixtures/wechat_batch_failure_isolation.txt` | 失败隔离 fixture（中间一个不存在的文件） |
| `tests/run_wechat_batch_smoke.py` | 5 项批量 smoke 测试 |

### 修改

| 文件 | 说明 |
|------|------|
| `docs/AGENT_COMMANDS.md` | 新增 §2e「微信公众号批量入库流程（v0.3.71+）」 |
| `docs/workflows/wechat-article-kb-import-workflow.md` | 升级到 v1.2：版本号、批量入口脚本、关联文档表、v1.2 批量章节 |
| `README.md` | §6 表格加批量命令、§7 通道 A 加批量模式子节、changelog 加 v0.3.70/v0.3.71 行 |

---

## §6 新增测试说明

### `tests/run_wechat_batch_smoke.py`（5 项 smoke）

1. **多 fixture 批处理**：`--input wechat_batch_urls.txt --dry-run` → 2 项都 DRY_RUN_OK
2. **重复检测**：`--input wechat_batch_duplicate_urls.txt --dry-run` → 第 2 项 DRY_RUN_DUPLICATE，`duplicate_of` 非空
3. **/AI/ URL 陷阱回归**：hiking fixture（图片 URL 含 `/AI/`）→ topics 不含 人工智能，tags 不含 AI，含户外域
4. **失败隔离**：`--input wechat_batch_failure_isolation.txt --dry-run`（中间一个不存在的文件）→ 中间项 BLOCKED_FETCH_FAILED，其余 DRY_RUN_OK，整批不崩
5. **pages_sync 仍 55**：smoke 跑完后 `check_pages_sync.py` 仍报 55 slugs（dry-run 不写 KB 条目）

---

## §7 测试命令和结果

| 命令 | 结果 |
|------|------|
| `python3 -m py_compile scripts/*.py` | PASS |
| `python3 tests/run_smoke_tests.py` | ALL SMOKE TESTS PASSED (3/3) |
| `python3 tests/run_wechat_batch_smoke.py` | ALL BATCH SMOKE TESTS PASSED (5/5) |
| `python3 scripts/check_kb.py` | PASS (55/55) |
| `python3 scripts/update_site.py` | PASS（55 个 item 页面，无删除） |
| `python3 scripts/audit_kb_state.py` | PASS_WITH_WARNINGS (0 HARD FAIL, 24 WARN 均为既有) |
| `python3 scripts/check_pages_sync.py` | PASS（55 slugs + content→items 完整性） |

---

## §8 门禁结果

| 顺序 | 命令 | 结果 |
|------|------|------|
| 1 | `py_compile scripts/*.py` | PASS |
| 2 | `run_smoke_tests.py` | PASS (3/3) |
| 3 | `run_wechat_batch_smoke.py` | PASS (5/5) |
| 4 | `check_kb.py` | PASS (55/55, 0 FAIL) |
| 5 | `update_site.py` | PASS（生成 55 个 item 页面，无删除） |
| 6 | `audit_kb_state.py` | PASS_WITH_WARNINGS (0 HARD FAIL) |
| 7 | `check_pages_sync.py` | PASS（55 slugs + 完整性） |

---

## §9 数量统计

| 计数项 | 值 |
|--------|-----|
| content/articles | 55 |
| docs/items | 55 |
| site/items | 55 |
| synced slugs | 55 |

（本次为纯能力新增 + smoke 测试，没有真实导入文章，KB 条目数保持 55。）

---

## §10 git diff 摘要

```
9 files changed (3 modified + 6 new)
+ scripts/wechat_batch_import.py (新增, ~450 行)
+ docs/commands/wechat-batch-kb-import-command.md (新增)
+ tests/fixtures/wechat_batch_urls.txt (新增)
+ tests/fixtures/wechat_batch_duplicate_urls.txt (新增)
+ tests/fixtures/wechat_batch_failure_isolation.txt (新增)
+ tests/run_wechat_batch_smoke.py (新增)
M docs/AGENT_COMMANDS.md (§2e)
M docs/workflows/wechat-article-kb-import-workflow.md (v1.2)
M README.md (§6 表格 + §7 批量子节 + changelog)
```

---

## §11 Commit / Push

- **commit message**: `Add WeChat batch import with dedup reporting`
- **commit 方式**: 逐文件 `git add`（未用 `git add -A`）
- **commit hash**: 见最终回复 `COMMIT` 字段
- **push**: `git push origin main`，结果见最终回复 `PUSH` 字段
- **force push**: 无

---

## §12 Preflight

任务开始前：
- `git fetch origin main --tags`：成功
- 当前分支：main，与 origin/main 同步（HEAD = e01008e）
- `check_task_preflight.py --planned-tag v0.3.71-... --classify-dirty --json`：`git_divergence.is_synced = true`，工作树 clean，无分叉、无非本任务 dirty

---

## §13 下一步建议

1. **真实批量回归**：挑 2-3 篇公开可抓的公众号文章，用 `--input urls.txt --import` 做一次端到端真实批量入库，确认去重和 manifest 在真实数据下也正确。
2. **`--no-gates` 谨慎使用**：当前 `--no-gates` 跳过末尾门禁，仅建议在调试时用；生产入库应保留门禁。
3. **manifest 归档**：批量 manifest 会累积在 `reports/` 下，建议定期归档（按月打包）或加一个 `--manifest-dir` 参数。
4. **并行抓取**：当前是串行逐篇，URL 批量大时可考虑有限并行（如 3 并发），但需注意微信反爬可能因并发触发拦截。
5. **去重 Layer 3 的误判风险**：`sha256(visible_text)` 对"同一篇文章的不同排版"会判重，但对"不同文章恰好正文相同"也会判重（罕见但理论存在）；可考虑加一个长度容差或相似度阈值。
