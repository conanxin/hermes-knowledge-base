# Agent Commands

## 任务报告

**所有 agent 任务完成后必须按 [docs/REPORTING_TEMPLATE.md](REPORTING_TEMPLATE.md) 输出报告。** 三类任务对应三个模板:

| 任务类型 | 模板 | 必填段数 |
|---|---|---|
| 只读审计 (read / search / grep / analyze) | 模板 1 | 3 段 |
| 写入不发布 (write_file / patch / build_index) | 模板 2 | 5 段 |
| 写入并发布 (git push / deploy / publish / 跨 agent 共享) | 模板 3 | 9 段 |

**硬性规则**:
- 任务结束**不能只写"完成了"**,必须有 §2 Scope + §3 Actions + §5 EVIDENCE 三段最低证据
- 只读任务也要有 STATUS + Scope + EVIDENCE(模板 1)
- 写本地文件但未 push 的,标模板 2
- 涉及 `git push` / `deploy` / `publish` 的,标模板 3,且必须含 §7 Commit/Push/Live 段
- `PENDING_CDN_SYNC` 是合法 WARN,不判 FAIL
- 详细的状态词、动作标签、生命周期定义、CDN 延迟规则、并发协议见 [REPORTING_TEMPLATE.md](REPORTING_TEMPLATE.md)

---

## 任务启动前 Preflight

**所有任务开始前必须先运行 preflight 检查。**

### 普通导入 / 维护任务

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
python3 scripts/check_task_preflight.py
```

### 带版本 Tag 的 Versioned Task

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name
```

### Preflight 结果处理

| 结果 | 处理方式 |
|------|----------|
| **PASS** | 继续执行任务 |
| **PASS_WITH_WARNINGS** | 仅当 warning 为已知非阻断项（如 v0.3.36 known duplicate）时可继续，并在报告中记录 |
| **FAIL** | **立即停止**，不得继续导入、不得 update_site、不得 commit/push |

---

## 导入文章流程

### 1. Preflight

```bash
python3 scripts/check_task_preflight.py
```

### 2. 抓取与翻译

- 抓取 URL 内容
- 如果 URL 抓取失败 / paywall / ACL / 正文不完整 → **hard stop**，记录失败原因
- 完整翻译

### 3. 质量检查

```bash
python3 scripts/check_kb.py
python3 scripts/check_pages_sync.py
```

### 4. 生成站点

```bash
python3 scripts/update_site.py
```

### 5. 最终检查

```bash
python3 scripts/check_translation_residue.py
```

### 6. Commit + Push

```bash
git add <相关文件>
git diff --cached --stat
git diff --cached --name-only
git commit -m "描述性提交信息"
git push origin main
```

### 7. Tag（如果是 versioned task）

```bash
git tag -a v0.3.N-task-name <commit> -m "Tag message"
git push origin v0.3.N-task-name
```

---

## 版本号选择

1. 运行 `python3 scripts/check_release_tags.py`
2. 以 `recommended_next_minor` 为准
3. 不要复用已使用过的 minor number
4. 从 v0.3.37 开始，每个 minor 只对应一个 tag

---

## 相关文档

- [docs/VERSIONING.md](VERSIONING.md) — 版本命名规则与 tag 策略
- [scripts/check_task_preflight.py](../scripts/check_task_preflight.py) — Preflight 检查脚本
- [scripts/check_release_tags.py](../scripts/check_release_tags.py) — Tag 卫生检查
