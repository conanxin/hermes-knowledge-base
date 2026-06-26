# Versioning Guide

## 版本命名规则

### 格式

```
v{major}.{minor}-{task-description}
```

- **major**: 重大架构变更 (e.g., v0, v1)
- **minor**: 增量任务编号 (e.g., v0.3.37)
- **task-description**: 简短英文描述，用连字符分隔 (e.g., `release-index-and-tag-hygiene`)

### 示例

- `v0.3.37-release-index-and-tag-hygiene`
- `v0.3.38-article-import-batch`
- `v0.3.39-design-system-update`

## Tag 命名规则

1. **Annotated tag 优先** — 使用 `git tag -a` 而非轻量 tag
2. **Tag message 必须包含**:
   - 任务简述
   - 关键变更摘要
   - 状态 (PASS / NOOP_CLEAN / 等)
3. **Tag 一旦创建，永不移动** — 不 delete, 不 force push, 不覆盖

## 什么时候创建 Annotated Tag

- 完成一个阶段性任务
- 通过所有 hard-stop checks
- 有明确的 commit 可指向
- 需要记录任务完成状态

## 为什么不移动旧 Tag

- Tag 是**不可变的历史标记**
- 移动 tag 会破坏远程协作的信任
- 如果 tag 指向错误 commit，创建新 tag 修正，保留旧 tag
- Force push tag 可能导致其他协作者仓库混乱

## 新任务如何选择下一个版本号

### 执行前检查

```bash
# 本地检查
git tag --list 'v0.3.N-*'

# 远程检查
git ls-remote --tags origin 'v0.3.N-*'
```

### 选择规则

1. **查看 docs/RELEASES.md** — 确认最新已用版本
2. **运行 scripts/check_release_tags.py** — 自动检测推荐版本
3. **选择下一个未使用的 minor number**
4. **如果 v0.3.N 已存在任何 tag，不要使用 v0.3.N**

### 示例

```bash
# 当前最新: v0.3.37
# 下一个可用: v0.3.38

# 不要这样做:
git tag v0.3.37-something-else  # ❌ v0.3.37 已存在

# 正确做法:
git tag v0.3.38-new-task  # ✅
```

## 已知例外

### v0.3.36 双 Tag 例外

**状态**: ⚠️ Known exception，不视为错误

**历史原因**:
- `v0.3.36-repo-health-final-verification` — 仓库健康验证
- `v0.3.36-repo-hygiene-and-report-cleanup` — 仓库卫生清理

这两个 tag 指向不同 commit，是**有意为之的阶段性标记**:
1. 先验证仓库健康 (repo-health-final-verification)
2. 再执行卫生清理 (repo-hygiene-and-report-cleanup)

**从 v0.3.37 开始，避免复用 minor number**。

### 历史并行开发模式

v0.3.18–v0.3.35 期间存在 **music enrichment** 和 **youtube capability** 双轨并行开发，导致同一 minor version 有多个 tag。这是**历史设计模式**，不视为错误。

**从 v0.3.37 开始，单轨单 tag**。

## Versioned Task 的 Mandatory Preflight

从 **v0.3.38** 开始，所有 versioned task 必须运行 preflight：

```bash
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name
```

### Preflight 检查内容

1. Git repo 有效性
2. Working tree clean
3. HEAD 与 origin/main 同步
4. Planned tag 不存在（本地和 remote）
5. Minor version 不冲突（不小于 recommended next minor）
6. 核心检查脚本通过（check_kb.py, check_pages_sync.py, check_tracks.py）

### Preflight 结果处理

| 结果 | 处理方式 |
|------|----------|
| **PASS** | 继续执行任务 |
| **PASS_WITH_WARNINGS** | 仅当 warning 为已知非阻断项（如 v0.3.36 known duplicate）时可继续 |
| **FAIL** | **立即停止**，不得继续 |

## Versioned Task 完整流程（v0.3.41+）

```
preflight → execution → checks → commit → tag → postflight
```

- **preflight**: `python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name`
- **postflight**: `python3 scripts/check_task_postflight.py --report reports/<task>.md --tag v0.3.N-task-name --expect-clean --expect-head-origin`

postflight 不移动旧 tag。tag deref commit 必须记录。

## 新任务版本号选择

1. **先运行** `python3 scripts/check_release_tags.py`
2. **以 `recommended_next_minor` 为准**
3. 不要复用已使用过的 minor number
4. 如果 planned minor > recommended，输出 WARNING（gap 可接受但需验证）

## Tag 创建前后验证

### 创建前

```bash
git tag --list 'v0.3.N-*'
git ls-remote --tags origin 'v0.3.N-*'
```

### 创建后

```bash
git rev-parse v0.3.N-task-name      # tag object
git rev-parse v0.3.N-task-name^{}    # deref commit
```

### 如果 tag 已存在

- **不删除**
- **不覆盖**
- **不 force push**
- 选择新的版本号

## Agent 执行前检查清单

- [ ] 运行 `python3 scripts/check_release_tags.py`
- [ ] 确认推荐版本号
- [ ] 运行 `python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name`
- [ ] 确认 preflight PASS
- [ ] 检查 `git tag --list 'v0.3.N-*'` 和 `git ls-remote --tags origin 'v0.3.N-*'`
- [ ] 确认 v0.3.N 未被使用
- [ ] 创建 annotated tag: `git tag -a v0.3.N-description -m "..."`
- [ ] 推送 tag: `git push origin v0.3.N-description`
- [ ] 验证 tag deref: `git rev-parse v0.3.N-description^{}`

## 相关文档

- [docs/RELEASES.md](RELEASES.md) — 完整 release index
- [docs/AGENT_COMMANDS.md](AGENT_COMMANDS.md) — Agent 命令与导入流程
- [docs/CLOUD_HERMES_INTEGRATION.md](CLOUD_HERMES_INTEGRATION.md) — 云端 Hermes 开工规则
- [scripts/check_release_tags.py](../scripts/check_release_tags.py) — 自动 tag 检查
- [scripts/check_task_preflight.py](../scripts/check_task_preflight.py) — 任务 preflight 检查
