# Hermes Agent UI P0 实施规范

> **基础**：[Hermes Agent UI Self-Audit v1](2026-06-26-hermes-agent-ui-self-audit-v1) 的 5 个 P0 行动项
> **性质**：给 agent 自己的 SOP + 报告模板，**不是**工程实现方案
> **范围**：所有"通过 agent 完成、可能影响远端状态"的任务
> **基线日期**：2026-06-26

---

## 规范使用概览

> **速查关键词** — 5 P0（Status 三态 / Long task 阶段名 / Stop 链路 / Inline Action 标签 / Source citation 三件套）+ 统一报告模板（PASS / WARN / FAIL 三态）+ 并发协议（13 步）。

**本规范的两大组成**：

1. **5 个 P0 逐条规范**（§1-§5）：每条 P0 包含问题定义 / 为什么重要 / 最小实施规则 / agent 输出格式 / PASS-WARN-FAIL 验收标准 / 示例报告片段
2. **统一任务报告模板**（§6）：所有任务结束时的 8 段式固定输出结构

**两个支撑章节**：

3. **三类任务差异化处理**（§7）：只读 / 写入 / 发布 三种任务类型的报告长度差异
4. **并发 agent 写仓库协议**（§8）：基于最近 3 次任务经验的多 agent 并发状态协议

**1 个使用章节**：

5. **如何在后续任务中使用本规范**（§9）：维护约定 + 升级触发条件

---

## §1 P0-1: Status indicator 三态化

### 问题定义

当前 Hermes Agent 的 Status 指示是**二态**："思考中 / 已完成"。缺"执行中"中间态，导致用户在 5 步任务中只看到"思考中"长时间不更新，会怀疑 agent 卡死。

### 为什么重要

- 状态不可见是 AI 产品**最普遍**的 UX 失败模式
- "执行中" vs "思考中" 在用户感知中是两个不同的事——前者说明 agent 在做事，后者说明 agent 在等
- 单步任务能容忍"思考中"，但多步任务**必须**显示阶段

### 最小实施规则

所有"执行步骤 ≥ 2 步"的任务，在每一步结束时输出：

```
[Status: 执行中] Step 2/5 — 提取翻译 → 下一步: 校对
```

不允许只显示"思考中"超过 30 秒（用户感知阈值）。

### Agent 输出格式

```
## 当前任务状态
- Status: 思考中 / 执行中 / 已完成
- Step: <当前步骤号> / <总步骤数>
- Phase: <当前阶段名，如 "提取翻译">
- Next: <下一步要做什么>
```

### 验收标准

| 级别 | 标准 |
|---|---|
| **PASS** | 每个阶段切换都明确标注三态之一 + Phase + Next |
| **WARN** | 二态也能接受，但需要解释为什么缺"执行中"（如任务确实只 1 步） |
| **FAIL** | 5 步任务从头到尾只显示"思考中"，无阶段切分 |

### 示例报告片段

```
## 当前任务状态
- Status: 执行中
- Step: 2/5
- Phase: 提取翻译（en → zh-CN）
- Next: Step 3 — 校对（CJK 字数对齐 + 专名一致性）

> 状态变更记录：
> 21:50:00 Status=思考中（收到任务）
> 21:50:05 Status=执行中 Step 1/5（开始：源文件扫描）
> 21:50:12 Status=执行中 Step 2/5（当前：提取翻译）
```

---

## §2 P0-2: Long task 阶段名显式化

### 问题定义

长任务（>2 步）只显示"百分比"或"思考中"是低信息量的。用户看到 "60%" 不知道 agent 在做"翻译"还是"校对"还是"查重"。

### 为什么重要

- 阶段名比百分比**信息密度高 5-10 倍**
- 阶段名让用户能**预测剩余时间**和**理解当前进度**
- 当 agent 卡在某阶段时，阶段名让用户能精确报告问题

### 最小实施规则

所有 ≥ 3 步的任务，**每一步必须显式命名**阶段（不是只显示百分比）。阶段名应当是**动词 + 对象**的格式，如"提取翻译"、"校对字"、"查链接"，而不是抽象的"处理中"。

### Agent 输出格式

```
## Long task 阶段
- Total: 5 阶段
- Current: 阶段 2（提取翻译）
- Completed: 阶段 1（源文件扫描）
- Remaining: 3 阶段（校对 / 查链接 / 写报告）
```

### 验收标准

| 级别 | 标准 |
|---|---|
| **PASS** | 所有阶段都有动词+对象命名，且阶段数 = 实际步骤数 |
| **WARN** | 部分阶段命名抽象（如"处理中"），但总数对 |
| **FAIL** | 只显示百分比 / 抽象 "处理中" / 阶段数与实际不符 |

### 示例报告片段

```
## Long task 阶段
- Total: 5 阶段
- Current: 阶段 2/5 — 提取翻译（en → zh-CN）
- Completed:
  - 阶段 1 — 源文件扫描（2 文件、135 行）
- Remaining:
  - 阶段 3 — 校对（CJK 字数 + 专名一致性）
  - 阶段 4 — 查链接（外部 URL 可达性）
  - 阶段 5 — 写报告
```

---

## §3 P0-3: Stop / pause / rollback 链路

### 问题定义

当前 `/stop` 在主 agent 层中断，**不一定级联到 sub-agent**。这导致：用户以为停了，结果 sub-agent 还在后台跑，事后才发现副作用（如文件被写、commit 被 push、远端被改）。

### 为什么重要

- "Stop" 是破坏性操作的**安全网**，失效一次 = 整个 agent 不可信
- 多 agent 协作是 Hermes Agent 的核心能力，Stop 链路必须级联
- 用户的"停止"是 final state，不应留半成品

### 最小实施规则

任何包含 sub-agent / delegate_task / cronjob / background 进程 的任务，**必须在 Status 字段中标注 Stop 链路**：

```
## Stop 链路
- 主 agent: 已停止（21:55:00）
- Sub-agent 1 (delegate_task): 已级联停止 ✓
- Sub-agent 2 (cronjob): 仍在 PENDING，需手动 kill
- 回滚路径: git reset HEAD~1 (未执行)
```

每个 sub-agent / 后台进程都需逐项标注，**不允许"应该停了"这种模糊表述**。

### Agent 输出格式

```
## Stop / Pause / Rollback 链路
- 主 agent 状态: 已停止 / 部分停止 / 未停止
- Sub-agent N 状态: 已停止 / 在跑 / 未知
- 后台进程: <PID 列表 + 状态>
- 回滚动作: 已执行 / 未执行 / 不需要
- 回滚命令: <具体命令 + 是否已验证>
```

### 验收标准

| 级别 | 标准 |
|---|---|
| **PASS** | 所有 sub-agent / 后台进程状态明确标注，主 agent 停止后 sub-agent 全部停止 |
| **WARN** | 部分进程状态未知（"应该停了"），但主 agent 已停 |
| **FAIL** | 主 agent 停后仍有 sub-agent 在跑且无标注 / 出现"应该停了"等模糊表述 |

### 示例报告片段

```
## Stop / Pause / Rollback 链路
- 主 agent 状态: 已停止（2026-06-27 04:32:15）
- Sub-agent 状态:
  - delegate_task #1 (extract): 已停止 ✓
  - delegate_task #2 (translate): 已停止 ✓
  - cronjob #3 (cleanup): 在跑（PID 12345，下次触发 04:45:00）
- 后台进程: 无
- 回滚动作: 不需要（未提交任何变更）
- 回滚命令: N/A
```

---

## §4 P0-4: Inline Action 加"预览 / 已生效"标签

### 问题定义

当前 agent 输出 Inline Action（如 patch 描述、push 命令、文件操作）时，**视觉上与"已执行"动作无区别**。用户容易把"草稿 / 建议"误以为是"已执行"，导致误判。

### 为什么重要

- 草稿和建议的**语义差异常被忽略**——一个未执行，一个已执行
- 用户在 Telegram 端看到"建议 patch 这 3 个文件"如果没标签，会以为已经 patch 了
- 误判 = 不信任。一次误判可能让用户**永久**不再相信 agent 输出

### 最小实施规则

所有"在消息中描述、但未实际执行"的动作，必须以 `[DRY-RUN]` 开头；所有"已实际执行"的动作必须以 `[APPLIED]` 开头。**禁止**任何无标签的"建议"或"已执行"动作。

### Agent 输出格式

```
## Actions taken
- [DRY-RUN] 建议 patch 3 个文件:
  - content/notes/2026/X/metadata.yaml
  - content/notes/2026/X/notes.md
  - content/notes/2026/X/source.md
- [APPLIED] 已 patch 上述 3 个文件（commit: 9aed075）
- [DRY-RUN] 建议 push 到 origin/main
- [APPLIED] 已 push 到 origin/main
```

### 验收标准

| 级别 | 标准 |
|---|---|
| **PASS** | 所有"建议"用 [DRY-RUN] 前缀；所有"已执行"用 [APPLIED] 前缀；无遗漏 |
| **WARN** | 80%+ 动作有正确前缀，但有 1-2 处遗漏 |
| **FAIL** | 多个动作无标签 / 标签混用（如把已执行标 [DRY-RUN]） |

### 示例报告片段

```
## Actions taken
- [DRY-RUN] 建议在 content/notes/2026/2026-06-26-Y/ 创建 4 文件
- [APPLIED] 已创建 metadata.yaml / summary.md / source.md / notes.md
- [DRY-RUN] 建议运行 python3 scripts/update_site.py
- [APPLIED] 已运行（exit 0，5/5 步 OK）
- [DRY-RUN] 建议 per-file git add
- [APPLIED] 已 git add（12 个文件，1605 insertions）
- [DRY-RUN] 建议 commit + push
- [APPLIED] 已 commit（dd833d5）+ push（origin/main updated）
```

---

## §5 P0-5: Source citation 三件套

### 问题定义

当前 agent 输出引用（web_search 结果、文件路径、commit hash、远端 URL）时，**只给"是什么"**（URL、路径、SHA），**不给"多可信"和"什么时候验证的"**。用户无法判断引用是否新鲜、是否经过验证。

### 为什么重要

- Trust builders 是 Self-Audit v1 识别的**最大 P0 风险面**
- 用户看到 URL 不知道是该点还是不点
- 用户看到 commit hash 不知道是不是已经 push
- "URL + 置信度 + 验证时间" 三件套缺一不可——任何单独一项都不够

### 最小实施规则

所有"引用 / 证据"类输出必须包含三件套：

1. **URL / 路径 / 标识**（必须）
2. **置信度**（0-100%，或定性 high/medium/low）
3. **验证时间**（ISO 8601 或 "5 分钟前" 等相对时间）

**允许简化的场景**：

- 100% 系统可验证的引用（如本地文件路径、刚 commit 的 SHA）可以省略置信度（标 "n/a"），但必须有验证时间
- 文档化引用（如官方文档）置信度可以标 "high"，但验证时间必填

### Agent 输出格式

```
## Evidence (Source citation 三件套)
| 引用 | 置信度 | 验证时间 |
|------|--------|----------|
| https://github.com/X/Y/commit/9aed075 | high | 2026-06-27 04:30:00 |
| /home/conan/projects/Z/file.md | n/a (本地) | 2026-06-27 04:25:00 |
| https://www.shapeof.ai/ | medium | 5 分钟前 |
```

### 验收标准

| 级别 | 标准 |
|---|---|
| **PASS** | 所有引用都有 3 件套（URL + 置信度 + 验证时间） |
| **WARN** | 80%+ 引用有 3 件套，但本地路径类引用缺验证时间（"刚刚"等模糊） |
| **FAIL** | 多个引用缺三件套中任一项 / 验证时间 > 1 小时前未刷新 |

### 示例报告片段

```
## Evidence (Source citation 三件套)
| 引用 | 置信度 | 验证时间 |
|------|--------|----------|
| https://github.com/conanxin/hermes-knowledge-base/commit/dd833d5 | high | 2026-06-27 04:32:00 |
| https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-X/ | high | 2026-06-27 04:32:30 (live HTTP 200) |
| python3 scripts/check_kb.py output | high | 2026-06-27 04:30:00 (just run) |
| https://www.shapeof.ai/patterns/example-gallery | medium | 2026-06-27 04:25:00 (5 min ago, page reachable) |
```

---

## §6 统一任务报告模板

所有"通过 agent 完成、可能影响远端状态"的任务，结束时必须按本模板输出报告。

### 模板结构（8 段）

```
## 任务报告

### 1. Status
- 思考中 / 执行中 / 已完成（三态）
- Step: <当前步骤号> / <总步骤数>
- Phase: <当前阶段名>

### 2. Scope
- 改了什么: <文件/路径列表>
- 没改什么: <明确排除的范围>
- 边界声明: <任务类型的免责声明>

### 3. Actions taken
- [DRY-RUN] <建议但未执行的动作>
- [APPLIED] <已实际执行的动作>
- 按阶段切分（参考 §2）

### 4. Evidence
- Source citation 三件套（参考 §5）
- 表格形式

### 5. Commit / Push
- commit hash: <hash>
- push 状态: <success / failed / pending>
- rebase 状态: <clean / conflicts>
- 远端 ahead/behind: <0/0 / N/M>

### 6. Live verification
- catalog records: <本地 N → 远端 N>
- HTTP 状态: <200 / 404 / pending>
- byte-identity: <yes / no / pending>
- CDN sync: <synced / PENDING_CDN_SYNC>
- PENDING_CDN_SYNC 不判 FAIL

### 7. Known limitations
- 启发式判断: <yes / no>
- 未跑全流程: <yes / no>
- CDN 延迟: <yes / no, 等待 N min>
- 其他: <具体限制>

### 8. Next action
- PR / 复现实验 / 二轮审计 / etc.
- 触发 v2 的条件（如有）
```

### 完整示例（真实任务回填）

下面是按本模板的**完整报告**，数据来自 item_count 修复任务 (`b42212d`)：

```
## 任务报告: Shape of AI item_count 修复

### 1. Status
- 已完成
- 5 步任务: 读 metadata / 改 4 文件 / update_site / check / push

### 2. Scope
- 改了什么:
  - content/resource_collections/2026-06-26-shape-of-ai-ux-patterns/metadata.yaml (item_count 42→37)
  - 同目录 collection.md / summary.md / notes.md / source.md 中的 "42" 文字统一改为 "37"
- 没改什么:
  - Shape of AI 原始网站
  - Emily Campbell / Dario Amodei / Conan Harvard 等其他记录
  - check_kb.py / app.js / generate_item_pages.py

### 3. Actions taken
- [APPLIED] patch metadata.yaml item_count 42→37
- [APPLIED] patch collection.md "总计:42"→"总计:37"
- [APPLIED] patch summary.md (2 处 "42" → "37")
- [APPLIED] patch notes.md "42 个模式" → "37"
- [APPLIED] patch source.md (2 处 "42" → "37")
- [APPLIED] run python3 scripts/update_site.py (5/5 OK)
- [APPLIED] run check_kb.py (PASS 42/42, warnings=0)
- [APPLIED] run check_pages_sync.py (PASS 42/42)
- [APPLIED] git add (10 个文件, per-file)
- [APPLIED] git commit b42212d
- [APPLIED] git push origin main (success)

### 4. Evidence
| 引用 | 置信度 | 验证时间 |
|------|--------|----------|
| commit b42212d | high | 2026-06-27 04:06:21 (just now) |
| site/data/catalog.json item_count=37 | high | 2026-06-27 04:08:00 (just verified) |
| https://conanxin.github.io/hermes-knowledge-base/data/catalog.json | high | 2026-06-27 04:10:00 (HTTP 200, byte-identical) |
| check_kb.py output: PASS 42/42 | high | 2026-06-27 04:08:00 |
| check_pages_sync.py output: PASS 42/42 | high | 2026-06-27 04:08:00 |

### 5. Commit / Push
- commit hash: b42212d78a549cefdb5e72e42e704031a1252814
- push 状态: success
- rebase 状态: clean (already up to date, 0/0)
- 远端 ahead/behind: 0/0

### 6. Live verification
- catalog records: 42 → 42 (无变化，仅 item_count 字段修改)
- HTTP 状态: 200
- byte-identity: yes (c9bbd0a3b263c6047ec4245e1fe22e379bc2b37f13dac573cab61a01e916ef24)
- CDN sync: synced (第二次轮询即追上，~30s)
- PENDING_CDN_SYNC: no

### 7. Known limitations
- 启发式判断: yes (item_count 来自实际 collection.md 计数，不是设计目标)
- 未跑全流程: no (gate 全过)
- CDN 延迟: yes (30s 同步窗口，但已追上)
- 其他: 无

### 8. Next action
- 等待后续任务或用户反馈
- 若用户希望 item_count 反映更新（如站点新增模式），重做计数
- P0 行动项 5 条的实施规范已记录在本规范（2026-06-26-hermes-agent-ui-p0-implementation-spec）
```

### 最小可接受报告

如果任务极简（如只修改 1 个文件的 1 个字段），可以**省略 §3 中按阶段切分**、**省略 §6 中 byte-identity**，但 §1 / §2 / §4 / §7 / §8 不可省略——这 5 段是报告的**最小可接受集**。

---

## §7 三类任务的差异化处理

### 7.1 任务分类

| 类型 | 定义 | 例子 |
|---|---|---|
| **只读任务** | 不修改任何文件、状态、远端 | read / search / grep / analyze / list |
| **写入任务** | 修改本地文件 / 状态，但不影响远端 | write / edit / patch / build_index |
| **发布任务** | 修改远端状态（push / deploy / publish） | push / deploy / send_message / publish |

### 7.2 报告 8 段是否全部要求

| 任务类型 | 必填段 | 可省略段 |
|---|---|---|
| **只读任务** | §1 Status, §2 Scope, §4 Evidence (3 段) | §3 Actions, §5 Commit/Push, §6 Live, §7 Limits, §8 Next |
| **写入任务** | §1 Status, §2 Scope, §3 Actions, §4 Evidence (4 段) | §5 Commit/Push, §6 Live, §7 Limits, §8 Next |
| **发布任务** | **全部 8 段** | 任何一段缺失 → WARN |

### 7.3 判定规则

agent 应当在任务开始时**显式声明任务类型**（在 Status 段）：

```
## 任务报告
- 类型: 发布任务（push 到 origin/main）
- 必填段: 全部 8 段
```

如果任务中途从"写入"升级为"发布"（如原本不打算 push 但发现需要 push），**必须更新任务类型声明**。

### 7.4 三类任务的差异化示例

**只读任务示例**（grep）：

```
## 任务报告: 检查所有 metadata.yaml 的 type 字段
- 类型: 只读任务
- 必填段: 3 段

### 1. Status: 已完成（1 步）
### 2. Scope: 扫描 content/**/*.yaml 的 type 字段分布
### 4. Evidence: 扫描结果表格（见下）
```

**写入任务示例**（patch 1 个文件）：

```
## 任务报告: 修复 shape-of-ai-ux-patterns item_count
- 类型: 写入任务
- 必填段: 4 段

### 1. Status: 已完成
### 2. Scope: 仅修改 metadata.yaml item_count 字段
### 3. Actions: [APPLIED] patch 1 处
### 4. Evidence: 验证 item_count = 37
```

**发布任务示例**（push 到 origin）：

```
## 任务报告: push 修复 commit
- 类型: 发布任务
- 必填段: 8 段 (全部)
...
### 5. Commit / Push
### 6. Live verification
### 7. Known limitations
### 8. Next action
```

---

## §8 并发 agent 写仓库时的状态协议

### 8.1 协议触发条件

满足以下任一条件时启动本协议：

- 多个 agent 共享同一仓库（多 sub-agent 并发）
- agent 在 push / deploy / publish 前
- agent 即将修改 `content/` 或 `site/` 或 `docs/`
- 用户明确要求"安全发布"

### 8.2 完整协议（13 步）

```
[CONCURRENT-PROTOCOL] 启动时间: <ISO 8601>

Step 1: git fetch origin
  退出条件: 命令成功，输出 FETCH_HEAD

Step 2: git pull --rebase --autostash origin main
  退出条件: 无冲突（如果冲突，转 reset-and-rebuild 模式，见 §8.3）
  检查: git rev-list --left-right --count origin/main...HEAD = 0/0

Step 3: git status -s
  退出条件: 输出为空（如果有输出，agent 评估是否 stash 已有改动）
  警告: 如果 status 非空，agent 不应继续，先 stash 自己的修改

Step 4: 写文件（4 文件 + metadata.yaml 等）
  退出条件: 文件实际写入成功（write_file 之后 read_file 验证）

Step 5: python3 scripts/check_kb.py
  退出条件: PASS, warnings=0, exit 0
  FAIL 处理: 不进 Step 6, 先修

Step 6: python3 scripts/check_pages_sync.py
  退出条件: PASS, site/ ↔ docs/ byte-identical

Step 7: python3 scripts/update_site.py
  退出条件: 5/5 步 OK
  内部已 hard-stop: 如果 check_kb.py FAIL, 不进 build/export/sync

Step 8: 再次运行 check_kb.py + check_pages_sync.py (独立 gate 二次确认)
  退出条件: 两次 gate 都 PASS

Step 9: per-file git add (不 git add . 或 git add -A)
  退出条件: git status -s 显示全部预期文件已 staged, 无未预期文件

Step 10: 再次 fetch + pull --rebase (pre-push concurrency safety)
  退出条件: rebase 成功, 0/0

Step 11: git commit + git push origin main
  退出条件: push 成功, origin/main = HEAD
  FAIL 处理: reset-and-rebuild 模式 (见 §8.3)

Step 12: 轮询 live CDN (最多 8 min, 每 30s 一次)
  退出条件: live records / HTTP / byte-identity 都匹配

Step 13: 报告 §6 Live verification 字段
  - PENDING_CDN_SYNC 不判 FAIL
  - git show origin/main:... 是权威 (用于区分 CDN-stale vs push-failed)

[CONCURRENT-PROTOCOL] 完成时间: <ISO 8601>
```

### 8.3 失败处理模式

#### 模式 A: reset-and-rebuild (rebase 冲突时)

适用于：多 agent 共享仓库，remote 已有新 commits 跟本地冲突。

```bash
# 保存本地新内容
cp -r content/<new-content-dir> /tmp/kb-stash/
# 丢弃本地 commit
git reset --hard origin/main
# 恢复内容 + 重新 build
cp -r /tmp/kb-stash/* content/
python3 scripts/check_kb.py
python3 scripts/update_site.py
# per-file git add + commit + push
```

**为什么不用 `git pull --rebase` 解决冲突**：catalog JSON 文件的 UU 冲突不好手动解,reset-and-rebuild 让 `update_site.py` 从 `content/` 重新生成,一次解决。

#### 模式 B: PENDING_CDN_SYNC (CDN 延迟时)

适用于：push 成功但 live 还在缓存旧 commit。

```bash
# 轮询 live, 不超过 8 min
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16; do
  live_count=$(curl -sL "<live-catalog>" | python3 -c "import json,sys; print(len(json.load(sys.stdin)))")
  if [ "$live_count" = "N+1" ]; then
    echo "CDN synced at iteration $i"
    break
  fi
  sleep 30
done
```

**关键**: 区分 `push failed` vs `CDN stale` —— 用 `git show origin/main:docs/data/catalog.json` 作为权威：

- 如果 `git show` 显示新 record → push 成功，CDN 缓存问题，**继续轮询**
- 如果 `git show` 不显示新 record → push 失败，**进 reset-and-rebuild**

#### 模式 C: 启发式判断未验证 (Self-Audit 限制)

适用于：所有 Self-Audit v1 识别的"未评估"项。

**在报告中标注**：

```
## 7. Known limitations
- 启发式判断: yes (item_count 基于 collection.md 实际计数)
- 启发式判断: yes (某些 "已具备" 项未跑复现实验)
```

不视为 FAIL，但明确标注。

### 8.4 协议执行时间盒

每步应有时长预算：

| Step | 预期时长 | 超出则 |
|---|---|---|
| Step 1-3 (git ops) | < 30s | 检查网络 |
| Step 5-7 (gate + build) | < 60s | 检查脚本权限 / Python 路径 |
| Step 8 (二次 gate) | < 30s | 检查 commit 前的修改 |
| Step 10 (pre-push rebase) | < 30s | 检查远端是否有新 commit |
| Step 11 (commit + push) | < 30s | 检查 commit msg / 远端权限 |
| Step 12 (CDN poll) | < 8 min | 标 PENDING_CDN_SYNC，不判 FAIL |
| **总预算** | **< 12 min** | 任何一步卡住，先标 WARN，再人工介入 |

### 8.5 协议输出要求

执行完本协议后，**报告 §6 Live verification 字段必须包含**：

```
### 6. Live verification
- catalog records: <本地 N → 远端 N+1 (CDN 追上后)>
- HTTP 状态: <200 / 404 / pending>
- byte-identity: <yes / no / pending>
- CDN sync: <synced (iteration N) / PENDING_CDN_SYNC (CDN 暂未同步)>
- PENDING_CDN_SYNC: <no / yes, 等待 N min>
- remote git tree authority: <git show origin/main:docs/data/catalog.json has N+1 records>
```

`PENDING_CDN_SYNC` 出现时**不视为 FAIL**——但要在 §7 Known limitations 中明确标注。

---

## §9 如何在后续任务中使用本规范

### 9.1 立即使用（每次任务结束）

每次 agent 完成"通过 agent 完成、可能影响远端状态"的任务时，**必须**按 §6 统一报告模板输出报告。

如果任务极简（纯只读），可省略部分段（见 §7.2）。如果任务复杂（含 sub-agent / 多平台 / CDN 同步），可在 8 段基础上**加段**（如"Sub-agent 状态"作为 §6.1）。

### 9.2 复盘使用（每月一次）

每月复盘时：

1. 抽取当月所有 agent 任务报告
2. 对照本规范的 5 P0，检查"本次报告是否满足规范"
3. 统计 WARN / FAIL 比例
4. 如果 FAIL > 5% 或某条 P0 多次触发 WARN，**升级本规范**

### 9.3 升级使用（触发 v1 → v2 时）

满足以下任一条件时升级本规范：

1. 5 P0 全部落地（按 Self-Audit v1 路线阶段 1+2 完成）
2. 30 天内应用 ≥ 10 次，WARN 比例 < 5%
3. Self-Audit 出 v2，本规范必须同步升级
4. 新增 agent 工作流工具（cronjob / delegate_task），并发协议章节需扩展

### 9.4 强制使用 vs 参考使用

| 场景 | 强制程度 |
|---|---|
| **发布任务** (push / deploy / publish) | **强制**——任何发布任务必须有 8 段完整报告，否则视作发布未完成 |
| **写入任务** (patch / write) | **强烈推荐**——4 段报告应在每次写入后输出 |
| **只读任务** (read / search) | **可选**——3 段简报即可 |
| **紧急任务** (用户显式说"快" / "brief") | **最低要求**——3 段简报，其他段可标注"省略" |

### 9.5 与项目记忆的关联

本规范的"已具备"判断依赖项目记忆（与 Self-Audit v1 共用）：

- Telegram typing action 对应 Status "思考中"
- MEDIA 协议可用于 Inline Action 的"已生效"标签
- sub-agent 隔离对应 Stop 链路的级联目标
- session DB 持久化对应 Evidence 的 last-validated 时间
- 多平台 home channel 对应 Live verification 的逐平台 curl

如果项目记忆本身有误（如某功能已下线），本规范相应章节需要修正。这正是 Self-Audit v1 推荐 v2 做"复现实验"的原因。

### 9.6 反馈循环

**本规范本身是 living document**。每次 agent 实际任务中遇到"本规范没说清楚"的场景，应当：

1. 在当次报告中标注"本规范需要补充 X"
2. 累积 3 次以上"同一类需要补充"后，正式修订本规范
3. 修订时同时更新 `summary.md` 和 `source.md` 的"何时更新"章节

---

## 附录 A: 报告模板速查卡

```
┌─ 任务报告 ────────────────────────────────┐
│ §1 Status (3 段必填)                      │
│ §2 Scope                                  │
│ §3 Actions [DRY-RUN]/[APPLIED]            │
│ §4 Evidence 三件套                        │
│ §5 Commit/Push (发布任务)                 │
│ §6 Live verification (发布任务)           │
│ §7 Known limitations                      │
│ §8 Next action                            │
└───────────────────────────────────────────┘

只读 → 3 段;写入 → 4 段;发布 → 8 段
WARN = 缺段 / 启发式 / CDN 未同步
FAIL = 关键缺失 / gate FAIL / push failed
PENDING_CDN_SYNC 不判 FAIL
```

## 附录 B: 并发协议速查卡

```
[CP-1]  fetch
[CP-2]  pull --rebase --autostash
[CP-3]  status -s 为空
[CP-4]  写文件
[CP-5]  check_kb.py PASS
[CP-6]  check_pages_sync.py PASS
[CP-7]  update_site.py OK
[CP-8]  二次 gate PASS
[CP-9]  per-file git add
[CP-10] pre-push 再次 rebase
[CP-11] commit + push
[CP-12] CDN poll (≤8 min)
[CP-13] 报告 §6 Live

失败模式:
- rebase 冲突 → reset-and-rebuild
- push 失败 → reset-and-rebuild
- CDN 慢 → PENDING_CDN_SYNC, 继续轮询
```

## 变更日志

- **2026-06-26**：v1 初版。基于 Self-Audit v1 的 5 P0 + 最近 3 次任务实证经验
- **v2 触发**：见 §9.3 4 个条件
