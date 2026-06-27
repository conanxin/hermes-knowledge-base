# Cloud Hermes Integration

## 云端 Hermes 开工规则

每次云端任务必须遵循以下规则：

### 1. 工作目录

- 每次任务必须从 `~/hermes-knowledge-base` 开始
- 不要从其他目录启动任务

### 2. 同步远程

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
```

### 3. 运行 Preflight

**所有任务必须运行 preflight：**

```bash
python3 scripts/check_task_preflight.py
```

**Versioned task 必须传 `--planned-tag`：**

```bash
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name
```

### 4. Preflight 结果处理

| 结果 | 处理方式 |
|------|----------|
| **PASS** | 继续执行任务 |
| **PASS_WITH_WARNINGS** | 仅当 warning 为已知非阻断项时可继续 |
| **FAIL** | **立即停止**，不得继续 |

### 云端 Hermes 收尾规则（v0.3.41+）

* commit + push + tag 后运行 postflight。
* 记录 postflight 输出。
* 如果 WARNING，最终回复必须说明。
* 不要因为 WARN-only 自行 force push / amend / reset。

**报告模板要求（v0.3.43+）**:
* 云端任务报告应遵循 [docs/REPORTING_TEMPLATE.md](REPORTING_TEMPLATE.md) §13 覆盖率审计字段清单。
* postflight warning 不得隐藏。
* report 缺字段时不要 amend 旧 commit，优先后续报告中记录。

### 5a. Anthology / Collection Page 导入（v0.3.52+）

如果云端任务涉及合集页 / 书籍页 / 多章节页抽取，必须：

- **写明 extraction scope**：报告中必须列出导入的章节边界（起点 + 终点 + 排除章节列表）。
- **无法确认边界时 hard-stop**：不得用整页正文替代指定单篇。
- **报告必填字段**：
  - `extraction_scope`
  - `extraction_start` / `extraction_end`
  - `anthology_boundary_check` (PASS / FAIL with evidence)

完整规则见 [templates/prompts/import_article_prompt.md § Anthology / Collection Page 单篇抽取规则](../templates/prompts/import_article_prompt.md) 和 [docs/AGENT_COMMANDS.md § 2a](AGENT_COMMANDS.md)。

### 5b. Source-Specific Import Recipes（v0.3.55+）

云端导入 Project Gutenberg 来源（或任何已建立 recipe 的来源）时，**必须先加载并遵守对应 recipe**：

| 来源 URL 域名 | Recipe 路径 |
|---|---|
| `gutenberg.org` / `www.gutenberg.org` | [docs/import-recipes/PROJECT_GUTENBERG.md](import-recipes/PROJECT_GUTENBERG.md) |

**云端 Gutenberg 导入要求**：

- 必须在报告中显式记录 **recipe 是否适用**（适用于 Project Gutenberg、不适用、命中但被 hard-stop）。
- 若触发 recipe §7 的 hard-stop cases（`AMBIGUOUS_ANTHOLOGY_SCOPE` / `EXTRACTION_BOUNDARY_NOT_FOUND`），报告中必须包含 `blocked_reason` 字段。
- 若为 anthology extraction，metadata.yaml 必须包含 `source_collection` + `extraction_scope` 字段。
- 云端导入与本地导入的差异：云端必须遵守 [§ 2 同步远程](#2-同步远程) 与 [§ 6 Versioned Task 流程](#6-versioned-task-流程)，不能在 dirty tree 上继续。

**不命中已知 recipe 时**：按通用流程处理，但报告中说明 `source_url` 域名 + 是否建议未来新增 recipe。

### 禁止操作

- **不得在 dirty tree 上执行** — 必须先 commit 或清理
- **不得在 tag 已存在时继续** — 必须选择新的版本号
- **不得复用 recommended next minor 之前的版本号** — 必须运行 `check_release_tags.py` 确认
- **不要 force push**
- **不要 commit --amend**
- **不要 git reset --hard**

### 6. Versioned Task 流程

```bash
# 1. Preflight
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name

# 2. 执行任务（导入、修改、生成等）
# ...

# 3. 质量检查
python3 scripts/check_kb.py
python3 scripts/check_pages_sync.py

# 4. 生成站点（如需要）
python3 scripts/update_site.py

# 5. Commit + Push
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name  # 再次确认
git add <相关文件>
git diff --cached --stat
git diff --cached --name-only
git commit -m "描述性提交信息"
git push origin main

# 6. Tag
git tag -a v0.3.N-task-name <commit> -m "Tag message"
git push origin v0.3.N-task-name
```

### 7. 任务报告

**所有云端 agent 任务完成后必须按 [docs/REPORTING_TEMPLATE.md](REPORTING_TEMPLATE.md) 输出报告。** 涉及 `git push` / `deploy` / `publish` / 跨 agent 共享写入的,必须使用"模板 3: 写入并发布任务报告模板"(9 段),并在报告中显式列出:

- **commit** — 完整 SHA hash
- **push range** — `git log origin/main..HEAD --oneline`(本次 push 含哪些 commit)
- **check_kb.py** — 完整输出 PASS 行
- **check_pages_sync.py** — 完整输出 PASS 行
- **live catalog** — `curl https://conanxin.github.io/hermes-knowledge-base/data/catalog.json` 的 records 数量
- **live item page** — `curl -I` 返回的 HTTP status
- **CDN 状态** — synced (RESOLVED) / PENDING_CDN_SYNC(详细规则见 [REPORTING_TEMPLATE.md §6](REPORTING_TEMPLATE.md))

`PENDING_CDN_SYNC` 不判 FAIL,但必须显式标注等待时间和轮询迭代。

### 8. 相关文档

- [docs/AGENT_COMMANDS.md](AGENT_COMMANDS.md) — Agent 命令参考
- [docs/VERSIONING.md](VERSIONING.md) — 版本命名规则
- [docs/REPORTING_TEMPLATE.md](REPORTING_TEMPLATE.md) — 任务报告模板(本规则的核心)
- [scripts/check_task_preflight.py](../scripts/check_task_preflight.py) — Preflight 检查脚本
- [scripts/check_release_tags.py](../scripts/check_release_tags.py) — Tag 卫生检查
