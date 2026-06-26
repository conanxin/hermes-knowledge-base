# Hermes Agent Reporting Template

## 这是什么

**Hermes Agent Reporting Template** 是 [KB 条目 `2026-06-26-hermes-agent-task-report-template`](https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-hermes-agent-task-report-template/) 的**稳定文档版**,作为所有 agent 任务的标准报告格式。

**两者关系**:
- KB 条目 (note 类型) — 完整版,含设计理念、范例回填、对比分析、变更日志
- 本文档 (docs/) — 精简操作版,只保留"任务报告"的可执行定义

**何时使用**:任何"通过 agent 完成、可能影响远端状态"的任务,均应按本模板输出报告。报告输出位置:
- **完整报告**:`reports/<task_name>_<YYYYMMDD>.md`
- **关键段摘要**:chat reply(STATUS / Files / Evidence / Commit / Live)

---

## 1. 三类任务 × 三类模板

| 任务类型 | 模板 | 必填段数 | 例子 |
|---|---|---|---|
| **只读审计** | 模板 1 | 3 段 | `read` / `search` / `grep` / `analyze` |
| **写入不发布** | 模板 2 | 5 段 | `write_file` / `patch` / `build_index` |
| **写入并发布** | 模板 3 | 9 段(全部) | `git push` / `deploy` / `publish` / 跨 agent 共享 |

如果任务从"写入"升级为"发布",**必须改用模板 3** 并补全缺失段。

---

## 2. 状态词(STATUS)

| 状态 | 含义 | 出现条件 |
|---|---|---|
| `PASS` | 任务完成 + 所有检查通过 | 全部 gate PASS + report 齐全 |
| `WARN` | 任务完成但有缺项 | 启发式、CDN 暂未同步、Evidence 缺项、报告缺段 |
| `FAIL` | 任务未完成 | 关键缺失 / gate FAIL / push failed |
| `PENDING_CDN_SYNC` | git 成功,live 暂未同步 | 见 §6 CDN 延迟规则 |
| `RESOLVED` | 之前 PENDING_CDN_SYNC,现已同步 | 见 §6 CDN 延迟规则 |

**`PENDING_CDN_SYNC` 不判 FAIL**。

---

## 3. 动作标签(Actions)

每个动作必须属于以下 5 标签之一:

| 标签 | 含义 | 出现位置 |
|---|---|---|
| `[READ-ONLY]` | 只读操作,无副作用 | 抓取 / 扫描 / 分析 / 验证 |
| `[WRITE]` | 写本地文件,未推远端 | `write_file` / `patch` / `edit` |
| `[GENERATE]` | 生成派生文件(由源生成) | `build_index` / `update_site` 输出 |
| `[PUSH]` | push 到远端 git 仓库 | `git push` |
| `[LIVE]` | live CDN 验证可见 | `curl <live URL>` |

**生命周期对应**:

| 生命周期 | 含义 | 标签 |
|---|---|---|
| `proposed` | 建议/草稿,未执行 | 仅在 Actions 中作为注释 |
| `applied` | 已应用到本地 | `[WRITE]` / `[GENERATE]` |
| `pushed` | 已推到远端 git 仓库 | `[PUSH]` |
| `live` | 已在 live CDN 验证 | `[LIVE]` |

**关键区分**:`applied ≠ pushed ≠ live`。一个动作可能 `applied` 但未 `pushed`(写本地),或 `pushed` 但 `live` 暂未同步(标 PENDING_CDN_SYNC)。

---

## 4. 三个模板

### 4.1 模板 1:只读审计任务报告模板(3 段)

````markdown
## 任务报告: <任务简述>

### 1. STATUS
- 状态: PASS / WARN / FAIL
- 任务类型: 只读审计
- 耗时: <X 秒/分>

### 2. SCOPE
- 做了什么: <一句话>
- 没做什么: <明确不修改任何文件>
- 边界: 本任务只读,不影响任何状态

### 3. EVIDENCE
| 引用 | 置信度 | 验证时间 |
|------|--------|----------|
| <本地文件路径或 URL> | n/a (本地) / high / medium | <ISO 8601 或 "X 分钟前"> |

**Checks (若有)**:
- [READ-ONLY] <使用的工具>

**Known limitations**:
- <未覆盖范围 / 启发式判断>

**Next action**:
- <下一步建议>
````

### 4.2 模板 2:写入但不发布任务报告模板(5 段)

````markdown
## 任务报告: <任务简述>

### 1. STATUS
- 状态: PASS / WARN / FAIL
- 任务类型: 写入但不发布
- 耗时: <X 秒/分>

### 2. SCOPE
- 做了什么: <文件/路径列表>
- 没做什么: <明确不 push / 不改远端>
- 边界: 修改仅限本地仓库工作区

### 3. ACTIONS
- [WRITE] patch `<file>: <field>` <old> → <new>
- [WRITE] write `<new-file>` (<字节数>)
- [GENERATE] catalog.json 包含新条目 (N → N+1)

### 4. FILES CHANGED
| 路径 | 操作 | 行数 Δ |
|------|------|--------|
| `<path>` | [WRITE] | +X / -Y |
| `<path>` | [GENERATE] | +X / -Y |

**Files unchanged**: <没有碰的文件>

### 5. EVIDENCE
| 引用 | 置信度 | 验证时间 |
|------|--------|----------|
| <本地路径> | n/a | <刚才> |
| <script output> | high | <刚才> |

**Known limitations**:
- <本地检查通过 ≠ 远端会通过>
- <未跑某些 check>

**Next action**:
- <下一步建议 / 是否需要 push>
````

### 4.3 模板 3:写入并发布任务报告模板(9 段)

````markdown
## 任务报告: <任务简述>

### 1. STATUS
- 状态: PASS / WARN / FAIL / PENDING_CDN_SYNC
- 任务类型: 写入并发布
- 阶段: <当前阶段名, 如 "Step 3/5 — 同步 push">
- 耗时: <X 秒/分>

### 2. SCOPE
- 做了什么: <完整列表>
- 没做什么: <明确排除>
- 边界声明: <任务类型的免责声明>

### 3. ACTIONS (按阶段切分)
**阶段 1: 准备**
- [READ-ONLY] fetch origin
- [READ-ONLY] pull --rebase --autostash
- [READ-ONLY] verify 0/0 + git status -s empty

**阶段 2: 写入**
- [WRITE] create <files>

**阶段 3: 构建**
- [GENERATE] run update_site.py (5/5 OK)
- [GENERATE] catalog.json records N → N+1

**阶段 4: 检查**
- [READ-ONLY] check_kb.py: PASS N/N, warnings=0
- [READ-ONLY] check_pages_sync.py: PASS N/N

**阶段 5: 发布**
- [WRITE] per-file git add
- [PUSH] git commit -m "<message>"
- [PUSH] git push origin main (success)

**阶段 6: live 验证**
- [LIVE] curl live catalog → N+1 records
- [LIVE] curl live item page → HTTP 200
- [LIVE] sha256 byte-identical vs local
- 状态: synced / PENDING_CDN_SYNC

### 4. FILES CHANGED
| 路径 | 操作 | Δ |
|------|------|---|
| content/.../metadata.yaml | [WRITE] (new) | +X |
| site/data/catalog.json | [GENERATE] | +X |
| ... | ... | ... |

**Files unchanged** (明确没动): <重要>
**Diff stat**: X files changed, Y insertions(+), 0 deletions(-)

### 5. EVIDENCE
| 引用 | 置信度 | 验证时间 |
|------|--------|----------|
| commit <hash> | high | <刚才> |
| git show origin/main:docs/data/catalog.json | high | <刚才> |
| live <URL> → HTTP 200 | high | <刚才> |
| check_kb.py output | high | <刚才> |
| check_pages_sync.py output | high | <刚才> |

### 6. CHECKS
| 检查 | 结果 |
|------|------|
| KB integrity | PASS N/N, warnings=0 |
| Pages sync | PASS N/N |
| Build pipeline | 5/5 OK |
| Pre-push rebase | clean (0/0) |
| Live HTTP | 200 |
| Live byte-identity | identical |

### 7. COMMIT / PUSH / LIVE
- commit hash: <full SHA, 40 chars>
- push status: success / failed / pending
- rebase status: clean / conflicts
- 远端 ahead/behind: 0/0
- live CDN: synced (iteration N) / PENDING_CDN_SYNC (X min waited)
- live last-modified: <header value>

### 8. KNOWN LIMITATIONS
- 启发式判断: yes / no
- 未跑全流程: yes / no
- CDN 延迟: yes / no
- 其他: <具体限制>

### 9. NEXT ACTION
- 后续任务 / 用户反馈等待
- 二轮审计 / 复现实验
- v2 触发条件
````

---

## 5. 反模式(不要做)

- ❌ **"完成了" 一句话替代证据** — 必须有 §5 EVIDENCE 或 §3 Actions
- ❌ **混用生命周期标签** — `applied ≠ pushed`,不能标 "已 applied" 但其实只 proposed
- ❌ **"草稿"和"已执行"放同一行** — 必须用 [DRY-RUN] / [APPLIED] 或 [READ-ONLY] / [WRITE] 区分
- ❌ **git push 失败时仍标 PASS** — push rejected = FAIL
- ❌ **live 未同步时标 PASS** — 必须标 PASS + PENDING_CDN_SYNC(或 WARN + PENDING_CDN_SYNC)
- ❌ **check FAIL 时仍标 PASS** — check 失败 = FAIL

---

## 6. CDN 延迟处理规则

### 6.1 进入 PENDING_CDN_SYNC 的条件

**全部满足**:
- `git push origin main` 成功(exit 0)
- `git show origin/main:docs/data/catalog.json` 显示新记录(说明 push 真实成功)
- 但 `curl https://<user>.github.io/<repo>/data/catalog.json` 仍返回旧 records

**根因**:GitHub Pages 部署后,CDN 需要 5-10 min 同步(实测最近几次 ~30s-60s)。

### 6.2 处理流程

```
[Step 1] git push 成功
[Step 2] 立刻 curl live,验证是否已同步
[Step 3] 如果未同步,标 PENDING_CDN_SYNC
[Step 4] 每 30s 轮询一次,最多 8 min
[Step 5] 一旦同步,标 RESOLVED
[Step 6] 报告最终状态 = PASS + RESOLVED
```

### 6.3 关键原则

- **PENDING_CDN_SYNC 不判 FAIL** — git 成功 + live 暂时缓存是已知现象
- **git show origin/main 是权威** — 区分 "CDN 缓存" vs "push 真的失败"
- **8 min 是上限** — 超出后标 PENDING 等待人工介入,不无限轮询
- **轮询脚本**:
  ```bash
  for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
    live_count=$(curl -sL "<live-catalog>" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
    if [ "$live_count" = "<expected>" ]; then
      echo "CDN RESOLVED at iteration $i"
      break
    fi
    sleep 30
  done
  ```

### 6.4 状态转换

| 阶段 | 状态 |
|---|---|
| 刚 push 完,live 还未追上 | `PASS + PENDING_CDN_SYNC` |
| live 追上 | `PASS + RESOLVED` |
| 8 min 仍未追上 | `WARN + PENDING_CDN_SYNC (超时)` |
| 区分不清 (CDN vs push 失败) | `FAIL + 需调查` |

---

## 7. 多 agent 并发最小协议

完整 13 步协议见 [P0 Implementation Spec KB 条目](https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-hermes-agent-ui-p0-implementation-spec/) §8。本节是**最小可工作集**(5 步)。

### 7.1 最小协议 5 步

```
[CP-1] git fetch origin
       退出条件: 命令成功

[CP-2] git pull --rebase --autostash origin main
       退出条件: rebase 成功, ahead/behind = 0/0
       失败处理: reset-and-rebuild (见 §7.2)

[CP-3] python3 scripts/update_site.py
       退出条件: 5/5 OK
       内部已 hard-stop: check_kb.py FAIL 时不进 build/export/sync

[CP-4] re-run checks (check_kb.py + check_pages_sync.py)
       退出条件: 两个 gate 都 PASS
       目的: 二次确认 Step 3 的副作用没破坏 gate

[CP-5] per-file git add + git commit + git push origin main
       退出条件: push 成功
       注意: 不 git add . 或 git add -A
```

### 7.2 失败处理:reset-and-rebuild

当 CP-2 失败(rebase 冲突)或 CP-5 失败(push rejected)时:

```bash
# 保存本地新内容到 /tmp
cp -r content/<new-dir> /tmp/kb-stash/

# 丢弃本地 commit,回到 origin/main
git reset --hard origin/main

# 恢复新内容
cp -r /tmp/kb-stash/* content/

# 重新走完整流程
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/check_pages_sync.py
git add <per-file>
git commit -m "<message>"
git push origin main
```

**为什么不用 `git pull --rebase` 手动解冲突**:catalog JSON 文件的 UU 冲突不好手动解,reset-and-rebuild 让 `update_site.py` 从 `content/` 重新生成,一次解决。

### 7.3 push 前再次 rebase

CP-5 之前**必须再跑一次** `git pull --rebase --autostash origin main`,避免 push 冲突:

```
[CP-5a] git pull --rebase --autostash origin main
        退出条件: rebase 成功, 0/0

[CP-5b] python3 scripts/update_site.py + check_kb.py + check_pages_sync.py
        退出条件: 全部 PASS

[CP-5c] per-file git add + git commit + git push origin main
```

### 7.4 协议时间预算

| Step | 预期时长 | 超出则 |
|---|---|---|
| CP-1 (fetch) | < 10s | 检查网络 |
| CP-2 (pull) | < 30s | 可能冲突,转 reset-and-rebuild |
| CP-3 (update_site) | < 60s | 检查脚本权限 |
| CP-4 (re-run checks) | < 30s | 极少见,检查 commit 是否成功 |
| CP-5 (commit + push) | < 30s | 检查 commit msg / 远端权限 |
| **总预算** | **< 3 min** | 转完整协议 13 步 |

---

## 8. 何时使用

### 8.1 强制场景

| 场景 | 强制程度 | 模板 |
|---|---|---|
| 跨 agent 共享的写入 | 强制 | 模板 2 或 3 |
| `git push` / `deploy` / `publish` | 强制 | 模板 3 |
| 用户明确说"安全" / "可验证" | 强制 | 模板 3 |
| 长任务(> 5 步) | 强烈推荐 | 模板 3 |
| 纯只读 + 极简(ls / wc) | 可选 | 可不用 |
| 紧急任务 + 用户说"brief" | 最低要求 | 至少 3 段 |

### 8.2 必填段(任意模板)

无论用哪个模板,以下字段**不可省略**:

- **STATUS**(PASS / WARN / FAIL + 任务类型)
- **SCOPE**(做了什么 + 没做什么)
- **EVIDENCE**(Source citation 三件套或本地验证)

### 8.3 与现有 7 段约束报告的关系

仓库 `reports/` 现有 v0.3.36/37/38 报告使用**7 段约束报告格式**(`## STATUS` + `## 1-7. Constraints Honored`)。两种格式**不冲突,可共存**:

| 维度 | 7 段约束报告 | 9 段流程报告(本模板) |
|---|---|---|
| 关注 | 约束遵守 + 检查结果 | 任务执行过程 + 证据 + live |
| 读者 | 版本 tag / 维护者 | 跨 agent / 用户 |
| 典型场景 | versioned task 硬 gate 报告 | 任何 agent 任务 |

versioned task 可**同时产出 2 份报告**,或把 7 段约束报告作为 9 段流程报告的**子集**(`## 1-7` 嵌入 9 段中)。

---

## 10. Postflight 检查(`scripts/check_task_postflight.py`)

`scripts/check_task_postflight.py` 是本模板的**机器验证脚本**,用于在任务结束后检查报告文件是否对齐所选 profile。**当前是 WARN-only**,不阻断任务,只在传 `--strict` 时才返回非 0。

### 9.1 与 preflight 的边界

| 维度 | `check_task_preflight.py` | `check_task_postflight.py` |
|---|---|---|
| 触发时间 | 任务开始前 (T0) | 任务完成后 (T1) |
| 输入 | git 状态 / tag / check 脚本存在 | 报告文件 + profile |
| 关注 | "约束是否就绪" | "报告是否对齐" |
| 失败语义 | 阻止任务开始 | WARN-only(默认)或 FAIL(显式 `--strict`) |
| 默认行为 | 强制门禁 | 可选工具,默认不扫描 reports/ |

两者**不能混用**:preflight 不应承担报告检查(语义错位),postflight 不应承担仓库状态检查(超出其职责)。

### 9.2 CLI

```bash
# 最小用法
python3 scripts/check_task_postflight.py \
    --report-file reports/<task>.md \
    --profile publish

# 自动推断 profile
python3 scripts/check_task_postflight.py \
    --report-file reports/<task>.md \
    --profile auto

# JSON 输出(供 CI / agent 解析)
python3 scripts/check_task_postflight.py \
    --report-file reports/<task>.md \
    --profile auto --json

# 显式 --strict:缺失必填段返回非 0 (FAIL)
python3 scripts/check_task_postflight.py \
    --report-file reports/<task>.md \
    --profile publish --strict
```

### 9.3 Profile 选择

| Profile | 适用报告 | 必填段 |
|---|---|---|
| `readonly` | 模板 1 (3 段) | STATUS, Scope, Evidence |
| `write_local` | 模板 2 (5 段) | STATUS, Scope, Actions, Files changed, Evidence |
| `publish` | 模板 3 (9 段) | STATUS, Scope, Actions, Files changed, Evidence, Checks, Known limitations, Next action + commit/push/live 引用 |
| `article_import` | 旧 `article_import_*.md` | Summary, Pipeline execution, Files written, Quality checks, Final state (legacy 豁免) |
| `versioned` | 旧 v0.3.x 7-段约束报告 | STATUS 顶部行 + 起始状态 + Check 结果 + Constraints Honored (legacy 豁免) |
| `auto` | 启发式推断(从文件名 + 标题) | 同对应 profile |

**auto 启发式**:
- 文件名以 `article_import_` 开头 → `article_import`
- 文件名含 `_v0` / `_v03` → `versioned`
- 文本含 `live` + (`push` / `commit`) → `publish`
- 文本含 `files changed` / `files written` → `write_local`
- 其它 → `readonly`

### 9.4 当前行为(WARN-only)

**默认**:
- 缺失必填段 → `STATUS: PASS_WITH_WARNINGS` + exit 0(不阻断)
- 任何错误(文件不存在、profile 未知) → `STATUS: FAIL` + exit 1

**显式 `--strict`**:
- 缺失必填段 → `STATUS: FAIL` + exit 1

**legacy 豁免**(v0.3.36/37/38 历史 reports):
- `profile=article_import` / `profile=versioned` 即使配 `--strict` 也不会因缺段返回 FAIL(只 WARN)— 因为这些 profile 的"必填段"是软必填
- `profile=publish` 即使配 `--strict` 仍会 FAIL(因为 publish 9 段是硬必填)

### 9.5 不做的事

- **不**扫描 `reports/` 全目录 — 必须显式传 `--report-file`
- **不**接入 `update_site.py` hard-stop
- **不**接入 CI / GitHub Actions
- **不**接入 pre-push hook
- **不**修改历史 reports/
- **不**修改 `check_kb.py` / `check_task_preflight.py`

Postflight 是**可选检查工具**,不是强制门禁。未来如要升级为门禁,需先观察 3-5 个任务 WARN 比例再决定,详见 §11。

---

## 10. Postflight 检查（v0.3.41+）

每个 versioned task 在 commit/tag 后推荐运行 postflight：

```bash
python3 scripts/check_task_postflight.py \
    --report reports/<task>.md \
    --tag v0.3.N-task-name \
    --expect-clean \
    --expect-head-origin
```

**说明：**
- postflight 是 **WARN-only**，不作为 FAIL gate。
- 检查 report 是否包含关键字段、tag 是否正确、git 状态是否 clean。
- 有 warning 时必须在最终回复中说明。
- 推荐观察 3-5 个任务后再考虑是否升级 FAIL gate。

---

## 11. 相关文档

- **完整版**(KB 条目,含设计理念与范例回填):[2026-06-26-hermes-agent-task-report-template](https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-hermes-agent-task-report-template/)
- **理论依据**(P0 Implementation Spec):[2026-06-26-hermes-agent-ui-p0-implementation-spec](https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-hermes-agent-ui-p0-implementation-spec/)
- **评估来源**:[2026-06-26-hermes-agent-ui-self-audit-v1](https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-hermes-agent-ui-self-audit-v1/)
- **Agent 命令参考**:[docs/AGENT_COMMANDS.md](AGENT_COMMANDS.md)
- **导入 prompt**:[templates/prompts/import_article_prompt.md](../templates/prompts/import_article_prompt.md)
- **云端开工手册**:[docs/CLOUD_HERMES_INTEGRATION.md](CLOUD_HERMES_INTEGRATION.md)

## 12. 修订日志

- **2026-06-27**:v1 初版。基于 task-report-template KB 条目的精简操作版
- **2026-06-27**:v1.1 新增 §10 Postflight 检查章节(WARN-only 最小版)
- v2 触发:KB 条目出 v2 / 反模式新增 / 协议步骤变化
