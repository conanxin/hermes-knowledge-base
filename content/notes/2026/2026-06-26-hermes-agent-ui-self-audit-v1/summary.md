# Hermes Agent UI 第一轮自检审计：摘要

## 是什么

**Hermes Agent UI Self-Audit v1** 是对刚完成的 [Hermes Agent UI 自检表](2026-06-26-hermes-agent-ui-shape-of-ai-checklist) 的**第一轮审计应用**。本审计以启发式判断（heuristic audit）为主，基于：

- 仓库中已有的 Hermes Agent 工具记忆（MEDIA 协议、`/skill` 体系、sub-agent 模式）
- 自检表 v1 中已经标注的"已具备 / 部分具备 / 未评估"状态
- 项目维护者对系统行为的认知（Conan Xin）

**明确声明**：这不是一次实际运行的系统行为审计（heuristic ≠ empirical）。所有判断在源代码层未做穷举验证。所有"已具备"判断需要后续由实际复现实验 / 代码 grep / 用户访谈确认。

## 审计目标

1. **把 37 个模式按"现状 / 缺口 / 改进 / 优先级"4 列归类**，形成可执行的 v1 改进路线
2. **汇总 P0/P1/P2 行动项**，让维护者能直接据此开 PR
3. **输出一份"先做无代码流程规范 → 报告模板 → UI 增强"的三阶段路线**，避免过早做 UI 投入
4. **暴露 6 层 AI Experience 模型中的最大空白**，作为长期演进方向

## 关键发现概览

### 现状（基于自检表 v1 的状态统计）

| 状态 | 数量 | 比例 |
|---|---|---|
| 已具备 | 12 | 32% |
| 部分具备 | 4 | 11% |
| 需改进 | 1 | 3% |
| 未评估 | 20 | 54% |

> "未评估"占多数不是缺陷信号 — 它是诚实标签。本审计的另一个价值是把 20 个"未评估"项收敛到更明确的"待评估"清单。

### 7 类整体判断

| 类别 | 当前判断 | 整体优先级 |
|---|---|---|
| Wayfinders | 能力侧已具备（5/6 已具备），但"Workspaces"未对用户显式 | P1（Workspaces 显式化） |
| Inputs | 主路径（Slash / @ mention / Connectors）已具备，多模态（Voice / Camera / Drag）未做 UX | P1（Camera / Prompt library 入口） |
| Tuners | 全部 6 项"未评估" — 调节器是**最大空白** | P1（至少做 Format selector） |
| Governors | Stop / Error handling 已具备；Undo / Edit prompt / Branching / Version history / Feedback loop 大部分未做 | **P0（Undo / Edit prompt 是中断链路的关键）** |
| Trust builders | Confidence score / Source citation / Human review 大部分未做；这是**最大的 P0 风险面** | **P0** |
| Identifiers | 5/6 已具备（AI avatar、Content labeling、Status indicator、Typing indicator、Progress bar） | P2（仅 Sound cue 缺失） |
| UILibrary | 部分具备（无统一库） | P2 |

### P0 行动项（必须马上推进，5 条）

1. **Status indicator 三态化**：从"思考中 / 已完成"二态改为"思考中 / 执行中 / 已完成"三态
2. **Stop 链路口径明确**：用户 `/stop` 必须级联到所有 sub-agent；当前在主 agent 层中断，子 agent 不一定停
3. **Inline Action 加"预览 / 已生效"标签**：避免"建议"被误以为是"已执行"
4. **Source citation 三件套**：URL + 置信度 + 最后验证时间三者必须同时出现，缺一不可
5. **Long task 进度显式化**：所有 >2 步的任务必须在消息中显示阶段名（不是只显示百分比）

### 6 层模型中的最大空白

| 6 层 | 覆盖度判断 | 主要缺口 |
|---|---|---|
| Model | 不适用 | — |
| Prompt | **14%** | 调节器全部 6 项只有 1 项半具备 |
| Interface | 49%（高） | Wayfinders / Identifiers 主体已具备，Workspaces 缺 |
| Workflow | 22% | Stop 链路、Undo、Edit prompt、Version history 全缺 |
| System | 27% | Trust builders 大部分缺，Source citation 不规范 |
| Emergence | **27% 但弱** | 跨 agent 标识、长期记忆、delegation 全缺 |

**核心判断**：Hermes Agent 在"用户能看到什么"上做得不错（Interface 49%），但在"系统是否可信"（System 27%）、"任务能否精细控制"（Workflow 22%）、"输出能否精细调节"（Prompt 14%）三个层面都有显著空白。

## 三阶段实施路线

### 阶段 1：无代码流程规范（0-2 周）

- 输出"P0 行动项 5 条"对应的话术模板（在 prompt 阶段就显式包含三态进度 / Stop 提示 / Source 标注）
- 不写代码，只改 prompt / 工具描述 / 报告模板
- 目标是**让用户在不感知代码变化的情况下看到 UX 改进**

### 阶段 2：报告模板（2-6 周）

- 在 update_site / patch / push 类操作后强制产出"做了什么 / 证据是什么 / live 状态"三段式报告
- 报告作为回复消息的固定结构（不是隐藏在 logs 里）
- 目标是把"Trust builders"中"Source citation / Human review / Explanation"三个 P0 项**通过模板化降低边际成本**

### 阶段 3：UI / Dashboard（6 周以后）

- 真正的 UI 增强（按钮、进度条组件、撤销按钮等）
- 只有在阶段 1 + 2 的反馈证明 P0 项仍有 UX gap 时才投入
- 避免过早做 UI — 流程和模板先收敛需求

## 不做什么

- **不修改任何代码 / 脚本 / 模板**：本条目是诊断 + 路线，不带任何 patch
- **不修改自检表原条目**：`2026-06-26-hermes-agent-ui-shape-of-ai-checklist` 保持原状
- **不假装已实际跑过 Hermes**：所有"已具备"判断都标注为启发式，需要后续验证
- **不做 P0 项的具体实现**：每个 P0 项给出"应该做什么"，不给"具体怎么改代码"

## 派生关系

- 上游：`2026-06-26-hermes-agent-ui-shape-of-ai-checklist` (自检表 v1)
- 上游：`2026-06-26-shape-of-ai-ux-patterns` (Shape of AI 资源条目)
- 上游：`2026-06-26-emilycampbell-layers-of-ai-experience` (6 层 AI Experience 模型)
- 平行：未来 `v2 / v3` 审计轮次

## 何时做 v2

满足以下任一条件时做 v2:

1. v1 中 5 条 P0 全部落地完成
2. 阶段 1+2 完成后有了真实用户反馈
3. 自检表 v1 的 20 个"未评估"项中超过半数被评估
4. Shape of AI 站点新增 / 删减模式
