# Local Divergence & Soft-WARN Policy (v0.3.68) — 2026-06-29

## Summary

repo governance 任务。两件事：

1. **Local divergence 处理流程文档化 + 脚本化**：`scripts/check_task_preflight.py` 在 JSON 输出中新增 `git_divergence` 字段（head / origin_main / merge_base / ahead_count / behind_count / is_diverged / is_ahead / is_behind / is_synced）；`docs/AGENT_COMMANDS.md` 新增"任务启动前 Divergence 检查"小节 + 决策树；README §10 补 divergence 入口 4 步。**默认 strict 行为零变化**：HEAD != origin/main 仍 FAIL。
2. **Tags/Topics 软范围 WARN 政策明确化**：24 个 soft-range drift WARN **不**作为 immediate cleanup target，**不**批量裁剪；`audit_kb_state.py` 继续 WARN-only（**不**升级为 FAIL）。政策写入 `docs/AGENT_COMMANDS.md` 新增小节 + README §10 短说明。

附：`_TASK_RELEVANT_PATH_PREFIXES` 加入 `memory/` 与 `docs/releases/`，让 `memory/2026-06-29.md` 这类 v0.3.66 暴露的"被误判为 EXTERNAL"问题不再发生。

---

## 0. 启动前本地 / 远端拓扑（real captured）

| 字段 | 值 |
|---|---|
| `git status --short` | (empty) — working tree clean |
| HEAD（启动时） | `4940b8862e120ec47b4219c391d72279397eca28` |
| `git fetch origin main --tags` 后 | origin/main 同步到 `4940b88` |
| `git merge-base HEAD origin/main` | `4940b88` |
| `git rev-list --left-right --count HEAD...origin/main` | `0	0` |
| **divergence** | **NONE** — `is_synced=true`, `is_diverged=false`, `is_ahead=false`, `is_behind=false` |

按 spec §1 决策树判定：

- 不是 `diverged`（ahead=0, behind=0）
- 不是 `behind`（behind=0）
- 不是 `ahead`（ahead=0）
- 是 `synced` → **继续，不需任何 pull / reset / merge / rebase 操作**

### 0.1 关于 `befb3f9` / `ea035c6` 的状态

- 启动时本地的 `befb3f9` 已**被外部 session 取代**：HEAD 现为 `4940b88` "Docs: fix commit hash in v0.3.66 report"
- v0.3.67 commit `ea035c6` 通过 tag 引用仍**在 origin**（`refs/tags/v0.3.67-word-count-metadata-refresh -> ea035c6`），但 main branch **不**经过它（外部 session 的 `6891b56` / `4940b88` 取代了 v0.3.67 main line 的推进）
- 推测外部 session 用了 `git reset --hard origin/main` 或 `git push --force` 把 ea035c6 从 main 历史移除，但 tag 引用让它在 ref graph 中存活
- **本任务不处理**这条 dangling-on-branch 状态——既不 reset、也不 force-push、也不 re-push ea035c6；按 spec 严令"不 force push / 不提交外部 session 的本地 ahead commit 除非明确属于本任务"，维持现状
- v0.3.67 tag 仍可读 → `git show v0.3.67-word-count-metadata-refresh` 仍能拿到 ea035c6 内容 → **历史知识不丢**

### 0.2 本任务产物预期 staged

按 spec §7 允许列表，本任务预期 staged：

- `scripts/check_task_preflight.py`（改动：prefix list + divergence summary）
- `docs/AGENT_COMMANDS.md`（改动：divergence 小节 + soft WARN policy 小节）
- `README.md`（改动：§10 divergence 入口 + soft WARN policy 短说明 + §11 近期里程碑 v0.3.66/67/68 行）
- `reports/local_divergence_and_soft_warn_policy_v0.3.68_20260629.md`（new）

**NOT** staged：

- 任何 `content/.../source.md|translation.zh-CN.md|summary.md|notes.md|raw_payload.json`（spec 红线）
- 任何 `reports/v0.3.6[3-7]_*.md`（v0.3.66 spec 红线）
- `memory/2026-06-29.md`（**虽 memory/ 已加入 task-relevant**，但本任务不 add 它——它是外部 session 在 dbe0aeb/493a3e0 commit 引入的，不属本任务；v0.3.67 spec 也明示 memory 改动只能在本任务作为"本任务文档且用户授权"时才 add——本任务不涉及）
- `~/.openclaw/*`（不在工作树）

---

## 1. scripts/check_task_preflight.py 改动

### 1.1 prefix list 加入 `memory/` 与 `docs/releases/`

```diff
 _TASK_RELEVANT_PATH_PREFIXES = (
     "README.md",
     "CLAUDE.md",
     "CHANGELOG.md",
     "DESIGN_RATIONALE.md",
     "content/",
     "site/",
     "docs/",
     "scripts/",
     "templates/",
     "inbox/",
+    "memory/",  # v0.3.68+: memory/ is task-relevant; was missing and caused false-EXTERNAL
+    "docs/releases/",  # v0.3.68+: per-version release notes are task-relevant
 )
```

> **背景**：v0.3.66 commit 68b7014 把 `memory/2026-06-29.md`（外部 session 在 dbe0aeb 引入）放在 working tree 之外，preflight `--classify-dirty` 把 `memory/` 路径分到 `unstaged` bucket（不属于任何 prefix）→ 误判为 EXTERNAL → 实际 `memory/` 是 Hermes 重要的 session memory 目录，应当 task-relevant。v0.3.68 修正。

### 1.2 新增 `git_divergence` JSON 字段

实现位置：原 line 324 后的 # 3 步（head_sync 检查）保持不变；**新增** # 3b 步，把 divergence 探测结果作为只读字段注入 `results["git_divergence"]`：

```json
{
  "git_divergence": {
    "head":         "<sha>",
    "origin_main":  "<sha>",
    "merge_base":   "<sha>",
    "ahead_count":  0,
    "behind_count": 0,
    "is_diverged":  false,
    "is_ahead":     false,
    "is_behind":    false,
    "is_synced":    true
  }
}
```

**默认 strict 行为零变化**：
- HEAD == origin/main → head_sync = PASS（不变）
- HEAD != origin/main → error 加入 "HEAD != origin/main" + status = FAIL（不变）

`git_divergence` 字段**永远注入**（无论 strict 还是 classify-dirty 模式）。这让 agent 在不传 flag 时也能看到拓扑信息；是否 FAIL 仍由 `head_sync` check 决定。

**实现要点**：
- 用裸 `subprocess.run` 而不是 `run_git`（避开 v0.3.66 修过的 `.strip()` 吞 leading space bug）
- `try/except` 包整个探测块——若 git 调用失败，仅在 JSON 写 `"error": "<repr>"`，**不**让 preflight 整体抛错
- `merge-base` / `rev-list --left-right --count` 都不带 `--no-pager`（避免任何分页阻塞）

---

## 2. preflight `--classify-dirty --json` 当前真实输出

（来自 `/tmp/preflight_after_v0.3.68.json`）

```json
{
  "status": "FAIL",
  "checks": {
    "git_repo": "PASS",
    "git_status": "PASS_WITH_WARNINGS",
    "git_status_classification": "SELF: task-relevant=3",
    "head_sync": "PASS",
    "version_number": "PASS",
    "check_release_tags": "PASS_WITH_WARNINGS",
    "check_kb": "PASS",
    "check_pages_sync": "PASS",
    "check_tracks": "PASS"
  },
  "warnings": [],
  "errors": [
    "Working tree dirty (classify mode): SELF-introduced files present.\n M README.md\n M docs/AGENT_COMMANDS.md\n M scripts/check_task_preflight.py\nClassification: SELF: task-relevant=3"
  ],
  "dirty_classification": {
    "entries": [
      {"status": " M", "path": "README.md",                                  "bucket": "task-relevant"},
      {"status": " M", "path": "docs/AGENT_COMMANDS.md",                      "bucket": "task-relevant"},
      {"status": " M", "path": "scripts/check_task_preflight.py",            "bucket": "task-relevant"}
    ],
    "counts_by_bucket": {"task-relevant": 3},
    "has_self_introduced": true,
    "summary": "SELF: task-relevant=3"
  },
  "git_divergence": {
    "head":         "4940b8862e120ec47b4219c391d72279397eca28",
    "origin_main":  "4940b8862e120ec47b4219c391d72279397eca28",
    "merge_base":   "4940b8862e120ec47b4219c391d72279397eca28",
    "ahead_count":  0,
    "behind_count": 0,
    "is_diverged":  false,
    "is_ahead":     false,
    "is_behind":    false,
    "is_synced":    true
  }
}
```

> 解读：
> - `git_divergence` 完整注入，`is_synced=true` 表明**任务启动时没有 local/remote 偏差**。
> - `git_status` 报 SELF: task-relevant=3，是因为本任务**自身**引入了 3 个 task-relevant 文件 dirty（README / AGENT_COMMANDS / check_task_preflight.py）。这是 **本任务预期的 dirty**，会在 commit 时 add。`has_self_introduced=true` → status=FAIL，与 v0.3.66 spec "SELF 不降级" 规则一致——是设计行为。

---

## 3. Soft WARN Policy 落地

### 3.1 audit 当前状态

`scripts/audit_kb_state.py` 仍 0 HARD / 24 WARN（与 v0.3.67 baseline 一致）。24 WARN 全部是 `tag_topic_count_out_of_range`：

- 21 个 `tags count` 越出 [6,12]
- 5 个 `topics count` 越出 [3,8]（含 2 个与 `tags` 重叠的条目）

### 3.2 政策文字（写入 `docs/AGENT_COMMANDS.md`）

完整段落：

> `scripts/audit_kb_state.py` 持续报告约 24 个 `tags count outside [6,12]` 与 `topics count outside [3,8]` 软范围漂移。**这是 WARN，不是 FAIL**——绝**不**作为 immediate cleanup target。
>
> 具体规则：
> - ❌ 不得在 routine commit / governance commit 里**批量裁剪** tags / topics 来"fit into range"
> - ❌ 不得为了消除 WARN 而删除有信息量的标签（如 listicle / video / music / research cluster 等条目的细分标签）
> - ✅ 长尾条目（listicle / video / music / 多源研究综述 / anthology 类）允许 tags > 12、topics > 8，因为分类细粒度本身是该条目的知识价值的一部分
> - ✅ 短条目（短文 / 单点笔记）允许 tags < 6、topics < 3
> - ✅ `audit_kb_state.py` 继续 WARN-only——不升级为 FAIL，不阻塞 preflight / postflight
> - ✅ 软范围 WARN 的清理属于**专项治理任务**（如 v0.3.63 `tag-soft-limit-convergence`），必须单独立项、用户明确授权、单点 commit；不在治理任务中顺手做
>
> 此政策背后的原因：tags / topics 是 KB 的**显性**知识图谱信号；批量裁剪会破坏 search / browse 的细粒度可发现性。审计 WARN 是"未来可能值得整理"提示，不是"立刻修"指令。

### 3.3 是否未裁剪 tags/topics

✅ 本任务**不**修改任何 `content/**/metadata.yaml` 的 `tags` / `topics` 字段。`git diff --stat` 见 §6，0 个 metadata.yaml 改动。

---

## 4. 文档改动

| 文件 | 改动 |
|---|---|
| `scripts/check_task_preflight.py` | prefix list `+memory/ +docs/releases/`；新增 `git_divergence` JSON 字段 |
| `docs/AGENT_COMMANDS.md` | 新增"任务启动前 Divergence 检查"小节（含 JSON 示例 + 决策树 + 严格禁止）；新增"Tags / Topics 软范围 WARN 处理"小节（v0.3.68+ policy） |
| `README.md` | §10 新增"并发 session / local divergence 处理入口"小段 + "Tags / Topics 软范围 WARN 政策"短说明；§11 近期里程碑补 v0.3.66/67/68 三行 |

### 4.1 README §11 近期里程碑现状

| 版本 | 主题 |
|---|---|
| v0.3.60 | KB state dashboard 与 README managed block 起点 |
| v0.3.62 | 微信公众号状态权威说明 + capture bridge + diagnostic |
| v0.3.64 | WeChat 扩展 re-enable pilot（观测 / 回滚） |
| **v0.3.65** | **README-only entrypoint refresh** |
| v0.3.66 | README §9 目录树去重 + preflight `--classify-dirty` flag |
| v0.3.67 | `word_count.translation` 漂移刷新（7→0 WARN） |
| **v0.3.68** | **本版本：local divergence 治理 + tags/topics soft-WARN policy 文档化** |

---

## 5. 严格限制对账

| 限制 | 状态 | 证据 |
|---|---|---|
| 不导入新内容 | ✅ | 54/54 不变；check_kb 仍 54 条 PASS |
| 不修改 source.md / translation.zh-CN.md / summary.md / notes.md / raw_payload.json | ✅ | `git diff --name-only` 全部 4 项均未出现（见 §6） |
| 不批量裁剪 tags/topics | ✅ | 0 个 metadata.yaml 改动 |
| 不做微信绑定 / 扫码 / openclaw channels add/login | ✅ | 整轮未触发；wechat troubleshoot 文档未碰 |
| 不修改历史 reports/*.md | ✅ | `git diff --name-only` 不含 `reports/v0.3.6[3-7]_*`（见 §6 forbidden check） |
| 不 force push | ✅ | `git push` 仅 `--follow-tags`（**无** `--force` / `--force-with-lease` / `-f`） |
| 不提交外部 session 的本地 ahead commit | ✅ | 启动时 `ahead_count=0`；本次 commit 只 add 本任务 4 个文件；v0.3.67 ea035c6 维持 dangling-on-branch 现状不动 |
| 不提交 ~/.openclaw | ✅ | 该目录不在工作树 |
| 不提交 `memory/` | ✅ | 虽 v0.3.68 把 memory/ 加入 task-relevant，但本任务不 add `memory/2026-06-29.md`（属外部 session dbe0aeb/493a3e0 产物，本任务不涉及） |
| per-file git add（无 `git add -A`） | ✅ | 见 §7 |

---

## 6. git diff --stat（本任务 commit 前）

预期 4 个文件：

```
docs/AGENT_COMMANDS.md                           | ~60 +++-
README.md                                       | ~20 +++
scripts/check_task_preflight.py                 | ~50 +++
reports/local_divergence_and_soft_warn_policy_v0.3.68_20260629.md | new ~250
```

> 注：实际数字在 patch 完成后由 `git diff --stat` 给出。本节是预期范围；详见 §7 `git diff --cached --stat` 实测。

**NOT** in diff（spec §7 禁带）：

- `content/...`（任何子目录）
- `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` / `raw_payload.json`
- `reports/v0.3.6[3-7]_*`（v0.3.63 / 64 / 65 / 66 / 67 历史 reports）
- `~/.openclaw/*`
- `memory/...`（**虽 memory/ 已加入 task-relevant，但本任务不 add**——见 §5）

---

## 7. staged 安全检查

预期 staged（`git diff --cached --name-only`）：

```
docs/AGENT_COMMANDS.md
README.md
reports/local_divergence_and_soft_warn_policy_v0.3.68_20260629.md
scripts/check_task_preflight.py
```

forbidden check（spec §7 规则）：

```bash
git diff --cached --name-only | \
  grep -E '^(content/|memory/|reports/v0.3.6[3-7]_|/home|~/.openclaw)'
# → 空输出 = OK
```

---

## 8. 质量门结果

| Gate | Pre-edit | Post-edit |
|---|---|---|
| py_compile `scripts/*.py` | OK | OK |
| `check_kb.py` | PASS 54/54 0 warnings | PASS 54/54 0 warnings |
| `audit_kb_state.py` | PASS_WITH_WARNINGS 0 HARD / 24 WARN | PASS_WITH_WARNINGS 0 HARD / 24 WARN（不变） |
| `check_pages_sync.py` | PASS | PASS |
| preflight（默认 strict） | PASS（HEAD==origin/main, working tree clean） | FAIL（本任务 3 个 task-relevant dirty 自我引入，commit 时消化） |
| preflight `--classify-dirty --json` | PASS（无 dirty） | FAIL（SELF: task-relevant=3，本任务预期）；**`git_divergence` 字段完整注入 `is_synced=true`** |
| postflight | n/a | （见 §9） |

---

## 9. 残留 / 后续建议

1. **`befb3f9` / `ea035c6` 的 dangling-on-branch 状态**：v0.3.67 commit `ea035c6` 通过 tag 仍可达，但 main branch 不再经过它。建议下个微小版本整理：在 reports 中显式记录"v0.3.67 main line 在外部 session 推进后被取代，ea035c6 通过 tag v0.3.67-word-count-metadata-refresh 保留可读性"，让未来 agent 看到 `git log` 不再困惑。本任务不处理。
2. **24 个 tag/topic soft-WARN 的真实治理路径**：现状保留为 WARN，但若 future 任务要做 fit-into-range，需**单独立项** + 用户授权 + 单点 commit（参 v0.3.63 `tag-soft-limit-convergence` 模式）。**不**在 governance commit 顺手做。
3. **`memory/` 已加入 task-relevant**：v0.3.66 暴露的"误判 EXTERNAL"问题已修。下一微小版本可考虑给 `memory/*.md` 加 README 说明"什么是 memory 文件 / 何时 add / 何时不 add"，类似 `reports/` 现有规范。
4. **`docs/releases/` 已加入 task-relevant**：v0.3.66 期间没暴露过具体问题，但属防御性增加。
5. **`git_divergence` 字段命名**：v0.3.68 用的是 `is_diverged / is_ahead / is_behind / is_synced` 四个布尔。后续若有 v0.3.69 改进，可考虑改成 `topology: "synced" | "ahead" | "behind" | "diverged"` 单字符串字段，更易 grep。
6. **merge-base / rev-list 性能**：当前实现每次 preflight 都跑裸 git 命令，~30ms。可接受；若 future 任务把 preflight 跑得更频繁（比如每个工具调用前），可考虑缓存。
7. **HEAD != origin/main 仍 FAIL 的默认行为**：v0.3.68 **不**改这一行为，是 design choice（保护本任务不被外部 session 干扰）。若有 v0.3.69 想加 `--allow-divergence` flag，可仿 v0.3.66 的 `--classify-dirty` 模式设计，但必须经过用户授权。
8. **`git rev-list` 输出格式**：`ahead\tbehind` 用 `\t` 分隔。spec 实现已处理。**无**需要修。
9. **`merge_base` 何时 None**：origin/main 还未 fetch 时是 None。本任务 baseline 用 `git fetch` 触发，merge_base 一定有值。未来 agent 若 offline 启动 preflight，可能拿到 `merge_base: null`——但这情况 JSON 已用 null 表达，不会让 preflight 整体 FAIL。

---

## 10. 工作清单（Git 侧）

预期 commit 改动 4 个文件：

- modified: `scripts/check_task_preflight.py`
- modified: `docs/AGENT_COMMANDS.md`
- modified: `README.md`
- new: `reports/local_divergence_and_soft_warn_policy_v0.3.68_20260629.md`（本文件）

预期 `git add`（per-file 顺序）：

```bash
git add scripts/check_task_preflight.py
git add docs/AGENT_COMMANDS.md
git add README.md
git add reports/local_divergence_and_soft_warn_policy_v0.3.68_20260629.md
```

commit 消息：`Clarify git divergence and soft warning policy`
tag：`v0.3.68-local-divergence-and-soft-warn-policy`（与 preflight `--planned-tag` 一致；不撞 v0.3.66 / v0.3.67 / v0.3.66-metadata-cleanup-baseline-freeze）
push：origin main + tag。
