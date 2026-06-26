# Hermes Agent UI 自检表：摘要

## 这是什么

**Hermes Agent UI 自检表**是一份面向个人项目 Hermes Agent 的产品设计自检表，源自 [The Shape of AI](https://www.shapeof.ai/) 的 37 个 AI 交互模式（6 大类 × 6 + 1 个 UILibrary）以及 [The Layers of AI Experience](https://emilycampbell.co/writing/layers-of-ai-experience) 的 6 层 AI 体验模型。

它的目标是把两个外部参考库**翻译成可在 Hermes Agent 上直接打勾的 checklist**：每个 Shape of AI 模式对应一条自检问题、一个 Agent 场景示例、一个当前状态（未评估 / 已具备 / 需改进 / 不适用）、一个优先级（P0 / P1 / P2）。

## 为什么需要它

- **AI 产品交互设计仍处于早期**：没有统一的设计语言，团队和个人都靠"感觉"。
- **Shape of AI 提供了 37 个共享模式名**：当说"我们需要一个 Temperature slider"时，团队和外部引用者指向的是同一个定义。
- **Hermes Agent 已经实现了其中一部分**（Follow up、Slash command、Connectors、Progress bar 等），但**没有系统盘点过**。自检表让"已具备 / 需改进 / 不适用"三类状态可比较、可追踪。
- **6 层 AI Experience 模型**（Interface / Interaction / Conversation / Collaboration / Delegation / Companionship）给 Hermes Agent 一个**纵向**视角：Shape of AI 主要覆盖前两层，自检表暴露了高层（Delegation / Companionship）的设计空白。

## 与现有 Hermes 工具的关联

| 工具 / 能力 | 涉及的 Shape of AI 模式 |
|---|---|
| Slash command（`/skill`） | Slash command、@ mention |
| MEDIA 协议、Inline Action | Inline Action、Follow up |
| 多步任务编排 | Chained action、Progress bar、Stop button |
| OpenClaw 状态消息 | Status indicator、Typing indicator |
| 长期记忆 / 复盘 | Version history、Branching、Feedback loop |
| ConPort / sub-agent | Connectors、Workspaces |

## 怎么用（4 个使用时机）

1. **新功能设计前**：对照对应类别的 checklist 评估；遗漏 P0 模式则不进入开发。
2. **发布前 review**：过一遍"Trust builders"和"Identifiers"两类的全量 P0/P1 项。
3. **每月复盘**：扫一遍所有"需改进"项，决定当月是否推进。
4. **跨 agent 协作时**：用本表统一不同 agent（Hermes、OpenClaw、ConPort）对 UI 能力的描述。

## 主要建议（10 条，详见 notes.md）

1. Agent 正在做什么要更可见（Status indicator、Typing indicator 应当区分"思考中 / 执行中 / 已完成"三态）。
2. 用户可中断、撤销、回退（Stop button、Undo、Edit prompt 必须级联支持）。
3. 每个自动化结果要有来源、状态、证据（Source citation、Confidence score、Human review 缺一不可）。
4. 长任务需要进度与阶段提示（Progress bar、Chained action、Workspaces）。
5. 需要区分草稿、建议、已执行动作（Inline Action、Regenerate、Feedback loop 应当带"预览 / 已生效"标签）。
6. 默认开启透明推理（Transparency toggle），让用户决定是否隐藏。
7. 失败处理要有兜底（Error handling、Status indicator、Confidence score 一起工作）。
8. 输入方式要支持多模态（Voice、Camera、Drag and drop、Slash command、@ mention）。
9. 输出调节器应该常驻可达（Tone selector、Length control、Temperature slider）。
10. 标识符要稳定（AI avatar、Content labeling、Status indicator 跨会话一致）。

## 已知空白（6 层模型中尚未覆盖）

| 6 层 | 覆盖情况 | 主要缺口 |
|---|---|---|
| Model | 不适用 | 业务模型层，UX 模式不直接对应 |
| Prompt | 部分覆盖 | 缺少 Prompt library、Persona picker |
| Interface | 高覆盖 | Wayfinders、Inputs、Identifiers 大部分具备 |
| Workflow | 部分覆盖 | Chained action 强、Workspaces 弱 |
| System | 部分覆盖 | Trust builders 大部分具备、Confidence score 缺 |
| Emergence | 弱覆盖 | 长期记忆、Companionship、Delegation 设计空白 |

## 基于

- **Shape of AI** (Emily Campbell, 2026) — 37 个 AI 交互模式，6 大类 + UILibrary
- **The Layers of AI Experience** (Emily Campbell, 2026) — 6 层 AI 体验模型
- **Hermes Agent** (Xin Conan, 2026-) — 本知识库对应的 agent 实现

## 不做什么

- **不复制 Shape of AI 网站内容**：每个模式用 1-2 句话概括，加上自检问题、Agent 场景和状态/优先级。
- **不实现任何模式**：本表是诊断工具，不是开发任务清单。`已具备`项指 Hermes Agent 当前代码中已经覆盖；`需改进`项需要单独 PR。
- **不评判 Shape of AI 模式的有效性**：37 个模式都同等对待，由使用者在打勾时按场景判断。
