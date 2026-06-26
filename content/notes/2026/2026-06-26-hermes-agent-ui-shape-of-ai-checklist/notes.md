# Hermes Agent UI 自检表

> **基础**：The Shape of AI 的 37 个 AI 交互模式（6 大类 × 6 + 1 UILibrary）
> **目的**：把共享模式名转化为可勾选 checklist，盘点 Hermes Agent 当前覆盖度
> **状态约定**：未评估 / 已具备 / 需改进 / 不适用
> **优先级约定**：P0 = 不达不让上线 / P1 = 半年内推进 / P2 = 长期观察

---

## 如何使用这张表

1. **新功能设计前**：先对照相关类别的 checklist，遗漏 P0 模式则不进入开发
2. **发布前 review**：过一遍"Trust builders"和"Identifiers"两类的全量 P0/P1 项
3. **每月复盘**：扫一遍所有"需改进"项，决定当月是否推进
4. **跨 agent 协作时**：用本表统一 Hermes / OpenClaw / ConPort 对 UI 能力的描述

**打勾方式**（建议）：在每行后面追加 `- [x]` 或 `- [ ]`（GitHub 友好），或复制到 Notion / 飞书表格。

**优先级重新评估**：当某条 P2 项 3 个月未推进时，应主动降级或删除，避免自检表本身变成噪声。

---

## 一、Wayfinders（导航指引）— 6 个模式

帮助用户理解 AI 能做什么、当前处于什么状态。

### 1.1 Example gallery
- **自检问题**：用户首次使用时，是否能看到 Hermes 能做什么的具体示例？
- **Agent 场景**：OpenClaw 启动时是否推送 3-5 个 `/skill` 例子？
- **状态**：未评估
- **优先级**：P1

### 1.2 Follow up
- **自检问题**：AI 回复后是否提供后续问题建议？
- **Agent 场景**：Hermes 完成任务后是否提示"继续"或"展开"按钮？
- **状态**：已具备（chat 中已有延续上下文）
- **优先级**：P0

### 1.3 Chained action
- **自检问题**：多步骤任务是否能串联执行并展示进度？
- **Agent 场景**：`/research` 触发 search → extract → summarize 三步流水线
- **状态**：已具备（多步任务编排已实现）
- **优先级**：P0

### 1.4 Inline Action
- **自检问题**：在 AI 回复中是否能直接执行下一步操作？
- **Agent 场景**：MEDIA 协议、消息中可点击按钮
- **状态**：已具备（MEDIA / button 已部分支持）
- **优先级**：P0

### 1.5 Connectors
- **自检问题**：是否能连接外部工具或 AI 功能？
- **Agent 场景**：terminal / browser / web_search / code_exec / delegate_task / cronjob
- **状态**：已具备
- **优先级**：P0

### 1.6 Workspaces
- **自检问题**：是否有为复杂任务提供的专用工作空间？
- **Agent 场景**：sub-agent 隔离目录（ConPort、hermes-agent-spawning）
- **状态**：需改进（用户视角的 workspace 概念未明示）
- **优先级**：P1

---

## 二、Inputs（输入方式）— 6 个模式

让用户以自然、高效的方式向 AI 提供信息。

### 2.1 Voice input
- **自检问题**：是否支持语音作为主要输入？
- **Agent 场景**：Telegram / 飞书语音消息转文本后作为 prompt
- **状态**：未评估
- **优先级**：P2

### 2.2 Camera input
- **自检问题**：是否支持摄像头捕获视觉信息？
- **Agent 场景**：vision_analyze 工具已具备
- **状态**：已具备（工具层支持，但 UX 流不显式）
- **优先级**：P1

### 2.3 Drag and drop
- **自检问题**：用户能否拖拽文件到对话窗口？
- **Agent 场景**：Telegram 拖拽文件 → 自动上传 → 提取为 prompt 上下文
- **状态**：未评估
- **优先级**：P2

### 2.4 @ mention
- **自检问题**：是否能通过 @ 激活特定 AI 功能或上下文？
- **Agent 场景**：`/skill` 命令、@ 子 agent 路由
- **状态**：已具备
- **优先级**：P0

### 2.5 Slash command
- **自检问题**：是否能通过 / 命令快速调用功能？
- **Agent 场景**：`/research`、`/book`、`/mode`
- **状态**：已具备
- **优先级**：P0

### 2.6 Prompt library
- **自检问题**：是否提供预设提示词模板供用户选择？
- **Agent 场景**：常用工作流模板（研究、复盘、翻译）一键加载
- **状态**：未评估
- **优先级**：P1

---

## 三、Tuners（调节器）— 6 个模式

让用户控制 AI 输出的风格、长度、语气等参数。

### 3.1 Temperature slider
- **自检问题**：用户能否调节输出的创造性/确定性？
- **Agent 场景**：用户切换"严谨模式" vs "创意模式"
- **状态**：未评估
- **优先级**：P1

### 3.2 Length control
- **自检问题**：用户能否控制输出长度？
- **Agent 场景**：`/brief`、`/detail`、`/long`
- **状态**：未评估
- **优先级**：P1

### 3.3 Tone selector
- **自检问题**：用户能否选择回复语气？
- **Agent 场景**：在"正式 / 随意 / 学术 / 口语"之间切换
- **状态**：未评估
- **优先级**：P2

### 3.4 Persona picker
- **自检问题**：用户能否选择 AI 扮演的角色？
- **Agent 场景**：律师 / 工程师 / 设计师等 persona 预设
- **状态**：未评估
- **优先级**：P2

### 3.5 Format selector
- **自检问题**：用户能否选择输出格式？
- **Agent 场景**：列表 / 段落 / 表格 / Markdown 之间切换
- **状态**：未评估
- **优先级**：P1

### 3.6 Regenerate
- **自检问题**：不满意时能否重新生成？
- **Agent 场景**：用户按"重新生成"按钮得到不同版本
- **状态**：未评估
- **优先级**：P1

---

## 四、Governors（控制机制）— 6 个模式

确保 AI 行为符合用户预期和安全边界。

### 4.1 Stop button
- **自检问题**：用户能否随时中断 AI 生成？
- **Agent 场景**：长任务时显示"停止"按钮
- **状态**：已具备（`/stop`、Telegram cancel）
- **优先级**：P0

### 4.2 Undo
- **自检问题**：用户能否撤销 AI 的最近操作？
- **Agent 场景**：删除刚刚生成的文件、撤回刚刚发出的消息
- **状态**：未评估
- **优先级**：P1

### 4.3 Edit prompt
- **自检问题**：用户能否修改已发送的提示词？
- **Agent 场景**：在任务执行中修改 prompt，AI 重新规划
- **状态**：未评估
- **优先级**：P1

### 4.4 Branching
- **自检问题**：是否能从某个节点分叉探索不同路径？
- **Agent 场景**：从 A 回复分叉到 A1 / A2 / A3 平行实验
- **状态**：未评估
- **优先级**：P2

### 4.5 Version history
- **自检问题**：是否保存和回溯 AI 交互的不同版本？
- **Agent 场景**：所有回复 / 文件操作可回看和回退
- **状态**：部分具备（session DB 但 UX 不显式）
- **优先级**：P1

### 4.6 Feedback loop
- **自检问题**：用户能否反馈以改进后续结果？
- **Agent 场景**：👍 / 👎 反馈、显式"更短 / 更详细"指令
- **状态**：未评估
- **优先级**：P1

---

## 五、Trust builders（信任构建）— 6 个模式

增强用户对 AI 系统的信任感。

### 5.1 Confidence score
- **自检问题**：是否显示 AI 对输出的置信度？
- **Agent 场景**：在事实类回答旁显示"置信度：85%"
- **状态**：未评估
- **优先级**：P0

### 5.2 Source citation
- **自检问题**：是否标注信息来源便于验证？
- **Agent 场景**：`web_search` 结果自动带 URL
- **状态**：部分具备（工具层有，UX 不一致）
- **优先级**：P0

### 5.3 Explanation
- **自检问题**：AI 是否解释为什么给出某个答案？
- **Agent 场景**：推理路径可展开 / 折叠
- **状态**：需改进（隐式推理存在，无显式 toggle）
- **优先级**：P1

### 5.4 Human review
- **自检问题**：是否标记需要人工审核的内容？
- **Agent 场景**：自动邮件、支付类操作需二次确认
- **状态**：未评估
- **优先级**：P0

### 5.5 Transparency toggle
- **自检问题**：用户能否切换显示 AI 推理过程？
- **Agent 场景**："详细模式"展示 token-by-token 推理
- **状态**：未评估
- **优先级**：P2

### 5.6 Error handling
- **自检问题**：失败时是否优雅处理？
- **Agent 场景**：工具调用失败时回退、重试、提示替代路径
- **状态**：已具备
- **优先级**：P0

---

## 六、Identifiers（标识符）— 6 个模式

帮助用户识别和区分不同的 AI 实体或内容。

### 6.1 AI avatar
- **自检问题**：是否有可识别的 AI 视觉形象？
- **Agent 场景**：跨平台一致的 Hermes logo / 头像
- **状态**：已具备
- **优先级**：P1

### 6.2 Content labeling
- **自检问题**：是否明确标注 AI 生成的内容？
- **Agent 场景**：所有 AI 输出在 Telegram 端带"AI"标签
- **状态**：已具备（消息源标识）
- **优先级**：P0

### 6.3 Status indicator
- **自检问题**：是否显示 AI 当前状态（思考 / 完成 / 错误）？
- **Agent 场景**：Typing bubble + "正在执行 search..."文字
- **状态**：已具备
- **优先级**：P0

### 6.4 Typing indicator
- **自检问题**：是否显示 AI 正在输入的动画？
- **Agent 场景**：Telegram typing action
- **状态**：已具备
- **优先级**：P1

### 6.5 Sound cue
- **自检问题**：是否用声音提示状态变化？
- **Agent 场景**：任务完成时一声轻响
- **状态**：未评估
- **优先级**：P2

### 6.6 Progress bar
- **自检问题**：长时间任务是否显示进度？
- **Agent 场景**：多步任务时显示"步骤 2/5"
- **状态**：已具备
- **优先级**：P0

---

## 七、UILibrary（UI 组件库）— 1 个模式

Shape of AI 还提供可复用的 UI 组件参考。

### 7.1 UI Components
- **自检问题**：是否有可复用的 AI 交互界面组件库？
- **Agent 场景**：按钮、卡片、引用块、表单等组件的跨 agent 共享
- **状态**：部分具备（Telegram 端组件散落，无统一库）
- **优先级**：P1

---

## 对 Hermes 的第一轮建议（10 条，按优先级排序）

1. **P0 - Agent 状态要更可见**：Status indicator 应区分"思考中 / 执行中 / 已完成"三态，目前是二态。
2. **P0 - 中断 / 撤销 / 回退必须级联**：Stop button 触发的停止应当级联到所有 sub-agent，不能只停止主 agent。
3. **P0 - 自动结果要带来源 / 状态 / 证据**：Source citation 必须包含链接、置信度、最后验证时间，缺一不可。
4. **P0 - 长任务必须有进度与阶段**：Progress bar 必须显示阶段名（如"提取 → 翻译 → 校对"），不能只显示百分比。
5. **P0 - 区分草稿 / 建议 / 已执行动作**：所有 Inline Action 必须有"预览 / 已生效"标签，已执行动作不可静默发生。
6. **P1 - 默认透明推理可关**：Transparency toggle 应当默认开启推理可见，由用户决定是否隐藏。
7. **P1 - 失败兜底要显式**：Error handling 必须有可重试、可降级、可放弃三个选项，不能只显示错误。
8. **P1 - 输入多模态要显眼**：Voice / Camera / Drag and drop 应当有 UI 入口，不能只通过工具间接使用。
9. **P1 - 输出调节常驻可达**：Temperature / Length / Format 应当放在设置里，不应当让用户每次写 prompt。
10. **P2 - 跨 agent 标识稳定**：AI avatar / Content labeling 跨 Hermes / OpenClaw / ConPort 必须一致，不能每个 agent 长得不一样。

---

## 与 6 层 AI Experience 的对应关系

The Layers of AI Experience 提出 AI 体验的 6 层模型：Model / Prompt / Interface / Workflow / System / Emergence。下表把 37 个模式映射到这 6 层。

> 注：Shape of AI 原文使用 Interface / Interaction / Conversation / Collaboration / Delegation / Companionship 6 层。本表使用更面向个人 agent 项目的 Model / Prompt / Interface / Workflow / System / Emergence 6 层（与 Hermes Agent 自身架构对齐），但映射逻辑相同。

| 6 层 | 含义 | 对应的 Shape of AI 模式（37） | 覆盖度 |
|---|---|---|---|
| **Model** | 模型本身的理解与生成能力 | （不直接对应 UX 模式） | — |
| **Prompt** | 用户输入和上下文 | Prompt library、Persona picker、Temperature slider、Length control、Tone selector、Format selector | 部分覆盖（5/37 = 14%） |
| **Interface** | 用户直接看到的界面 | Wayfinders（6）、Inputs（5 减去 Prompt library）、Identifiers（6）、Transparency toggle | 高覆盖（18/37 = 49%） |
| **Workflow** | 任务的执行流程 | Chained action、Workspaces、Progress bar、Stop button、Branching、Version history、Regenerate、Feedback loop | 部分覆盖（8/37 = 22%） |
| **System** | 系统级保障与可观测性 | Source citation、Confidence score、Explanation、Human review、Error handling、Undo、Edit prompt、Connectors、@ mention、Slash command | 部分覆盖（10/37 = 27%） |
| **Emergence** | 跨会话的涌现能力 | Content labeling、AI avatar、Sound cue、Drag and drop、Camera input、Voice input、Example gallery、Follow up、Inline Action、UI Components | 弱覆盖（10/37 = 27%） |

**最大空白**：

- **Emergence 层**（跨会话、跨 agent 涌现能力）最弱，缺少长期记忆、companionship、delegation 的 UX 模式
- **Prompt 层**几乎完全依赖用户自己写，缺少主动引导（Prompt library / Persona picker 都是 P1-P2）
- **System 层**的 Trust builders 大部分缺失，Hermes Agent 在"信任建立"上投入不足

---

## 与 Shape of AI 条目的差异

| 维度 | Shape of AI 资源条目 | 本表 |
|---|---|---|
| 形式 | 资源清单 + 链接 | 可勾选 checklist |
| 视角 | 通用 AI 产品 | 专门针对 Hermes Agent |
| 内容 | 模式名 + 说明 + 链接 | 模式名 + 自检问题 + Agent 场景 + 状态 + 优先级 |
| 分类 | 6 大类（横向） | 6 大类（横向）+ 6 层（纵向） |
| 更新频率 | Shape of AI 站点 | 跟随 Hermes Agent 实际能力 |
| 派生关系 | 原始 | 派生自 `2026-06-26-shape-of-ai-ux-patterns` |

---

## 变更日志

- **2026-06-26**：初版。基于 Shape of AI 37 个模式 + Layers of AI Experience 6 层模型
