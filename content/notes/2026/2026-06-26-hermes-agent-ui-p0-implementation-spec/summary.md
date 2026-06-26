# Hermes Agent UI P0 实施规范：摘要

## 是什么

**Hermes Agent UI P0 Implementation Spec** 是对 [Hermes Agent UI Self-Audit v1](2026-06-26-hermes-agent-ui-self-audit-v1) 中 5 个 P0 行动项的**可执行规范**——不是工程实现方案，而是**给 agent 自己的 SOP（标准作业流程）+ 报告模板**。

适用对象：所有"通过 agent 完成、可能影响远端状态"的任务（patch / push / deploy / 跨 agent 协作 / 用户能看到的 UI 调整等）。

不适用：纯一次性、只读、不可观察的任务（grep / read / search 等）。

## 5 个 P0 行动项的精确措辞

来自 Self-Audit v1 P0 汇总表，编号沿用：

| # | P0 行动项 | 类别 | 本规范的执行抓手 |
|---|---|---|---|
| 1 | Status indicator 三态化（思考中 / 执行中 / 已完成） | Identifiers | 报告模板的 "Status" 字段强制三态标注 |
| 2 | Stop 链路口径明确（级联到 sub-agent） | Governors | 并发 agent 写仓库协议（见 §并发协议） |
| 3 | Inline Action 加"预览 / 已生效"标签 | Wayfinders | 报告模板的 "Actions taken" 用 [DRY-RUN] / [APPLIED] 前缀 |
| 4 | Source citation 三件套（URL + 置信度 + 验证时间） | Trust builders | 报告模板的 "Evidence" 字段强制三件套 |
| 5 | Long task 阶段名显式化（不是只显示百分比） | Identifiers | 报告模板的 "Actions taken" 按阶段切分，每阶段单独报告 |

## 本规范的两大组成

### 1. 5 个 P0 的逐条规范（notes.md §1-§5）

每条 P0 包含 6 段：问题定义 / 为什么重要 / 最小实施规则 / agent 输出格式 / PASS-WARN-FAIL 验收标准 / 示例报告片段。

### 2. 统一任务报告模板（notes.md §6）

8 段式固定结构：

```
Status      — 思考中 / 执行中 / 已完成（三态）
Scope       — 任务边界（什么改了、什么没改）
Actions     — 实际动作（按阶段切分，Inline Action 带 [DRY-RUN]/[APPLIED]）
Evidence    — 证据（Source citation 三件套：URL + 置信度 + 验证时间）
Commit/Push — git 操作记录（commit hash、push 状态、rebase 状态）
Live        — live 状态验证（HTTP / sha256 / byte-identity）
Limits      — 已知限制（heuristic、CDN 延迟、未跑全流程等）
Next        — 下一步行动（PR / 复现实验 / 二轮审计等）
```

每条任务报告必须按这 8 段输出，缺一段视为 WARN（不阻断但报告不完整）。

## 三类任务的差异化处理（notes.md §7）

| 任务类型 | 报告 8 段是否全部要求 | 关键差异化 |
|---|---|---|
| **只读任务** (read / search / grep) | Status / Scope / Evidence (3 段) | 无 Commit/Push / Live，可省略 |
| **写入任务** (edit / write / patch) | Status / Scope / Actions / Evidence (4 段) | 必须有 Actions 详细分步 |
| **发布任务** (push / deploy / publish) | 全部 8 段 | Commit/Push + Live 必填，CDN 同步状态必填 |

## 并发 agent 写仓库时的状态协议（notes.md §8）

复用最近 3 次任务（item_count 修复、checklist 创建、self-audit 创建）的真实经验：

```
[CONCURRENT-PROTOCOL]
1. fetch + pull --rebase --autostash origin main
2. 确认 ahead/behind = 0/0
3. 确认 git status -s 为空
4. 写文件（per-file git add 在最后）
5. 跑 check_kb.py + check_pages_sync.py（必须 PASS, warnings=0）
6. 跑 update_site.py
7. 跑两个独立 gate（再确认）
8. per-file git add（不 git add . 或 git add -A）
9. pre-push 再次 fetch + pull --rebase
10. commit + push
11. 轮询 live CDN（最多 8 min，每 30s 一次）
12. 区分 CDN-stale vs push-failed（用 git show origin/main:... 作为权威）
13. PENDING_CDN_SYNC 不判 FAIL
```

每个 step 都有**退出条件（exit condition）**——前一步不通过就不进下一步。

## 验收标准：PASS / WARN / FAIL

| 级别 | 含义 | 行动 |
|---|---|---|
| **PASS** | 报告 8 段齐全、证据三件套、commit hash 有效、live byte-identical | 任务完成 |
| **WARN** | 报告有缺段 / 证据缺项 / CDN 暂未同步 / 启发式判断未经验证 | 标注后继续，下次补 |
| **FAIL** | 报告 8 段严重缺失 / 关键证据缺失 / 验收 gate FAIL / push 失败 | 不完成任务，标注 PENDING |

## 在后续任务中如何使用本规范

- **每次任务结束**输出一份按本规范模板的报告（即使是 brief reply）
- **复盘时**对比 Self-Audit v1 的 5 P0，检查"本次报告是否满足规范"
- **每月审计**时把当月所有报告合并统计，看 WARN 比例是否在下降
- **v2 触发**时把本规范纳入对比基线

## 不做什么

- **不修改 Self-Audit v1 原条目**——本规范基于它，但不动它
- **不修改 checklist 原条目**——三者是独立 KB 条目
- **不写新代码 / 脚本 / 工具**——本规范只是 SOP
- **不假装已经在所有 agent 中实施**——本规范发布后，agent 在每次任务中**应当**遵循，但不是"已强制"
- **不替代 Self-Audit v1**——审计是"现状评估"，本规范是"未来 SOP"

## 派生关系

```
2026-06-26-shape-of-ai-ux-patterns  (原始, 资源条目)
    └── 2026-06-26-hermes-agent-ui-shape-of-ai-checklist  (自检表 v1)
            └── 2026-06-26-hermes-agent-ui-self-audit-v1  (审计 v1)
                    └── 2026-06-26-hermes-agent-ui-p0-implementation-spec  (本条目)
```

本条目是 4 层派生的最下游，直接面向 agent SOP。

## 何时更新本规范

- 当 5 P0 全部落地（Status 三态、Long task 阶段、Stop 链路、Inline Action 标签、Source 三件套）后，做 v1 → v2 升级
- 当 Self-Audit 出 v2 时，本规范也必须更新
- 当 agent 工作流新增工具（cronjob / delegate_task / 跨 agent）时，扩展并发协议章节

## 与 Self-Audit v1 的差异

| 维度 | Self-Audit v1 | 本规范 |
|---|---|---|
| 性质 | 审计（评估现状） | 规范（定义未来） |
| 目标 | 知道该改什么 | 知道怎么改、按什么格式报告 |
| 输出 | 7 类审计 + P0/P1/P2 汇总 + 3 阶段路线 | 5 P0 逐条规范 + 报告模板 + 并发协议 |
| 读者 | 维护者（人） | agent 自身（也是维护者） |
| 时间 | 静态（v1 时点） | 动态（每次任务应用） |
| 派生 | 自检表 v1 | Self-Audit v1 |
