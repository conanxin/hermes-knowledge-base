# Agent Commands

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
