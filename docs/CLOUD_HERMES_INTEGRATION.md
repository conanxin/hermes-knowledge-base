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
