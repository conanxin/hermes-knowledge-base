# Hermes Agent UI 第一轮自检审计（v1）

> **基础**：[Hermes Agent UI 自检表 v1](2026-06-26-hermes-agent-ui-shape-of-ai-checklist)（37 个模式 + 6 层映射）
> **性质**：启发式审计（heuristic audit），非实证审计
> **数据来源**：项目记忆 + 自检表 v1 状态列 + 维护者认知
> **信任等级**：中。所有"已具备"判断需在 v2 用复现实验验证
> **基线日期**：2026-06-26

---

## 审计方法与边界

**本审计的 4 个边界**：

1. **不修改任何代码 / 脚本 / 模板** — 本条目是诊断 + 路线，不带 patch
2. **不修改自检表原条目** — checklist 保持原状
3. **不假装已实际跑过 Hermes** — 所有"已具备"判断都标注为启发式
4. **不做 P0 项的具体实现** — 每个 P0 项给"应该做什么"，不给"具体怎么改代码"

**审计循环**：每类 4 段式输出（**当前判断** / **主要缺口** / **推荐改进** / **优先级**），便于跳读。

---

## 一、Wayfinders（导航指引）审计

### 当前判断

Wayfinders 是 Hermes Agent **覆盖度最高**的类别之一。Source citation、Chained action、Inline Action、Connectors、@ mention 5 项已具备，仅 Example gallery / Workspaces 处于"未评估"或"需改进"。

> 数据基础：checklist v1 中 6/6 状态分布 = 已具备 5 / 需改进 1 / 未评估 0（实际 Example gallery 在 v1 标"未评估"，Workspaces 标"需改进"）

能力侧"做什么、当前在哪、怎么连外部"已成熟。问题是**首次使用引导（onboarding）**和**复杂任务的空间感（workspace 概念）**。

### 主要缺口

1. **缺少"第一次启动"案例展示** — 新用户面对 30+ skill 时不知道从哪里开始
2. **Workspaces 对用户不可见** — sub-agent 隔离目录在底层存在，但用户在主对话中看不到"我为你创建了 workspace X"
3. **Follow up 偏隐式** — chat 上下文延续是模型自发行为，没有显式"下一步"按钮

### 推荐改进

| 改进项 | 实施成本 | 价值 |
|---|---|---|
| 首次启动推送 3-5 个 `/skill` 例子 | 低（prompt 模板） | 高（onboarding 转化率） |
| sub-agent 创建时显式提示 "正在 workspace X 中执行..." | 中（sub-agent 模板改） | 中（信任建立） |
| Follow up 加 "继续 / 展开" 按钮 | 高（前端组件） | 中（依赖具体平台） |

### 优先级

**P1** — 整体不是阻断性问题，但 Example gallery 是 onboarding 漏斗的关键节点，建议先做。

---

## 二、Inputs（输入方式）审计

### 当前判断

主路径（Slash command / @ mention / Connectors）已具备，但**多模态（Voice / Camera / Drag and drop）和 Prompt library** 几乎全部未做 UX 化。工具层有（如 `vision_analyze`），但**用户入口不显眼**。

> 数据基础：checklist v1 中 6/6 状态 = 已具备 3（@ mention、Slash command、Camera input 工具层）/ 未评估 3（Voice / Drag and drop / Prompt library）

### 主要缺口

1. **Voice / Drag and drop 无 UX 入口** — 工具不支持，或支持但用户找不到
2. **Camera input 是"工具可达但 UX 不可达"** — `vision_analyze` 在，但用户不知道可以发图
3. **Prompt library 完全空白** — 没有"工作流模板"概念

### 推荐改进

| 改进项 | 实施成本 | 价值 |
|---|---|---|
| 在所有 home channel 入口处放"发图 / 发语音"提示 | 低 | 中 |
| Prompt library 起步版：3 个工作流模板（研究 / 复盘 / 翻译） | 中 | 高（复用率） |
| Drag and drop 文档化（Telegram / Slack 已有原生支持） | 低 | 中 |

### 优先级

**P1** — Camera / Prompt library 是 P1；Voice / Drag 推到 P2。

---

## 三、Tuners（调节器）审计

### 当前判断

**Tuners 是 Hermes Agent 当前最大的空白**。6/6 全部"未评估" — 既没有 Temperature slider、Length control，也没有 Tone selector、Persona picker、Format selector、Regenerate。

> 含义：用户对输出风格、长度、语气、格式的精细控制权基本为零，只能通过每次写 prompt 来"间接调节"。

### 主要缺口

1. **没有"模式切换"概念** — 用户无法在"严谨"和"创意"之间切换
2. **没有长度预设** — `/brief` / `/detail` 不存在
3. **没有格式预设** — 用户每次要重新指定"用表格 / 用列表 / 用 markdown"
4. **没有 regenerate** — 不满意只能"再发一次"，模型随机性导致结果不可预测

### 推荐改进

| 改进项 | 实施成本 | 价值 |
|---|---|---|
| Format selector 起步：3 个预设（list / paragraph / table） | 中 | 高（最高频调节需求） |
| Length control：`/brief` / `/detail` / `/long` 三个预设 | 低 | 高 |
| Regenerate：用户按 "↻ 重新生成" 按钮 | 中 | 中 |
| Temperature slider 推迟到 v2 | 高（需要 UI） | 中 |
| Tone / Persona 推迟到 v2 或更后 | 高 | 低（个人 agent 不强需要） |

### 优先级

**P1** — Format selector + Length control + Regenerate 是 P1 的核心（实施成本可控，价值高）。Temperature / Tone / Persona 推迟到 P2。

---

## 四、Governors（控制机制）审计

### 当前判断

**Governors 是 P0 风险面**。Stop button / Error handling 已具备，但 Undo / Edit prompt / Branching / Version history / Feedback loop 大部分未做。Version history 部分具备（session DB 有，但 UX 不显式）。

> 关键问题：用户**能停下但不能撤销**。这是中断链路的关键缺口。

### 主要缺口

1. **没有 Undo** — 写错文件 / 发错消息后无法回退
2. **没有 Edit prompt** — 任务执行中无法修改 prompt 重新规划
3. **没有 Version history UX** — session DB 有但用户不知道
4. **没有 Feedback loop** — 👍/👎 反馈没有 UX 入口
5. **没有 Branching** — 想从某个节点分叉探索但没工具

### 推荐改进

| 改进项 | 实施成本 | 价值 |
|---|---|---|
| Undo：每个生成动作后跟"↶ 撤销"按钮 | 中 | 极高（破坏性操作安全网） |
| Edit prompt：在任务执行中显示"修改 prompt"入口 | 中 | 高 |
| Version history 暴露给用户："查看本次 session 所有动作" | 中 | 高（debug + 信任） |
| Feedback loop：`👍 / 👎` 显式反馈 | 低 | 中 |
| Branching 推迟到 v3 | 高 | 中 |

### 优先级

**P0** — Undo 是 P0 的核心（破坏性操作安全网是上线前提）。Edit prompt 和 Version history 是 P1。Feedback loop 是 P1。Branching 是 P2。

---

## 五、Trust builders（信任构建）审计

### 当前判断

**Trust builders 是 P0 风险面的最大一块**。仅 Error handling 已具备；Confidence score / Source citation / Human review / Transparency toggle 全部未做或部分做；Explanation 部分具备（隐式推理存在，无显式 toggle）。

> 关键问题：用户**看到结果但无法判断结果可不可信**。这是 AI 产品最严重的 UX 失败模式之一。

### 主要缺口

1. **没有 Confidence score** — 用户无法知道 AI 的"把握度"
2. **Source citation 不规范** — 工具层有，但 UX 不一致
3. **没有 Human review 标记** — 自动化操作没有"请人工确认"环节
4. **Transparency toggle 缺失** — 推理过程不可见也不可隐藏
5. **Explanation 隐式** — 用户要主动问"为什么"才知道

### 推荐改进

| 改进项 | 实施成本 | 价值 |
|---|---|---|
| Source citation 三件套：URL + 置信度 + 最后验证时间 | 中 | 极高（事实类回答可信度） |
| Human review：自动邮件 / 支付类操作强制二次确认 | 中 | 极高（防止误操作） |
| Confidence score：在事实类回答旁显式标注 | 中 | 高 |
| Transparency toggle：默认开，可关 | 低 | 中 |
| Explanation：每个回复末尾加"推理依据" 1-2 句 | 低 | 中 |

### 优先级

**P0** — Source citation 三件套 + Human review 强制确认是 P0 的核心。Confidence score 是 P1（实施成本中等）。Transparency / Explanation 是 P1-P2。

---

## 六、Identifiers（标识符）审计

### 当前判断

**Identifiers 是 Hermes Agent 第二高覆盖度的类别**。5/6 已具备（AI avatar、Content labeling、Status indicator、Typing indicator、Progress bar），仅 Sound cue 缺失。

> 标识符已经做得不错，主要工作是把"三态 Status indicator"补全。

### 主要缺口

1. **Status indicator 是二态** — 当前"思考中 / 已完成"，缺"执行中"
2. **没有 Sound cue** — 任务完成时无声反馈
3. **AI avatar 跨平台一致性未验证** — 不同 home channel 可能不一致

### 推荐改进

| 改进项 | 实施成本 | 价值 |
|---|---|---|
| Status indicator 三态化：思考中 / 执行中 / 已完成 | 低 | 极高（长任务可观测性） |
| 跨平台 avatar 一致性验证 | 低 | 中 |
| Sound cue 推迟到 v2 | 中 | 低（个人 agent 场景不强需要） |

### 优先级

**P0（局部）** — Status indicator 三态化是 P0，因为它直接影响长任务可观测性。其他项 P2。

---

## 七、UILibrary（UI 组件库）审计

### 当前判断

UILibrary 在 Hermes Agent 中**部分具备** — Telegram / Discord / Slack 各自的 markdown 渲染存在，但没有跨平台统一组件库。

> 这是一个**长期投资**类项目，不在 P0/P1 范围。

### 主要缺口

1. **没有跨平台统一组件库** — 每个 home channel 各自实现
2. **按钮 / 卡片 / 引用块等组件不统一** — 同一概念在不同平台长相不同
3. **没有"组件文档"** — 设计者和实现者之间没有共同词汇

### 推荐改进

| 改进项 | 实施成本 | 价值 |
|---|---|---|
| 抽出"组件词汇表"文档：3-5 个核心组件 + 跨平台映射 | 中 | 中（长期价值） |
| 推迟实际 UI 组件库投入 | — | — |

### 优先级

**P2** — 长期增强，不在 v1 / v2 优先级。

---

## P0 / P1 / P2 行动项汇总

### P0（5 条，必须马上推进）

| # | 行动项 | 类别 | 实施成本 |
|---|---|---|---|
| 1 | Status indicator 三态化（思考中 / 执行中 / 已完成） | Identifiers | 低 |
| 2 | Stop 链路口径明确（级联到 sub-agent） | Governors | 中 |
| 3 | Inline Action 加"预览 / 已生效"标签 | Wayfinders | 中 |
| 4 | Source citation 三件套（URL + 置信度 + 验证时间） | Trust builders | 中 |
| 5 | Long task 阶段名显式化（不是只显示百分比） | Identifiers | 低 |

**P0 选择的 3 条原则**：

1. **对用户破坏性最大**（Stop 链路、Inline Action 误判、Source 不可信）
2. **实施成本低**（Status 三态、Long task 阶段名都是 prompt 层可改）
3. **不依赖 UI 改造**（避免过早做组件库投入）

### P1（7 条，下一轮推进）

| # | 行动项 | 类别 | 实施成本 |
|---|---|---|---|
| 1 | Undo（每个生成动作后跟"↶ 撤销"） | Governors | 中 |
| 2 | Edit prompt（任务执行中可修改 prompt） | Governors | 中 |
| 3 | Version history 暴露给用户 | Governors | 中 |
| 4 | Feedback loop（👍/👎 显式反馈） | Governors | 低 |
| 5 | Format selector 起步版（list / paragraph / table） | Tuners | 中 |
| 6 | Length control（`/brief` / `/detail` / `/long`） | Tuners | 低 |
| 7 | Human review（自动邮件 / 支付类操作强制确认） | Trust builders | 中 |
| 8 | Confidence score（事实类回答旁标注） | Trust builders | 中 |
| 9 | Example gallery 首次启动推送 | Wayfinders | 低 |
| 10 | Prompt library 起步版（3 个工作流模板） | Inputs | 中 |
| 11 | Workspaces 对用户显式化 | Wayfinders | 中 |
| 12 | Camera input UX 入口显眼化 | Inputs | 低 |

> P1 实际候选 12 条，按"实施成本 / 价值比"选了 7 条作为下一轮重点。其它 5 条可在 P1 末或 P2 初推进。

### P2（长期增强项，4 条）

| # | 行动项 | 类别 |
|---|---|---|
| 1 | Regenerate（↻ 重新生成） | Tuners |
| 2 | Temperature slider | Tuners |
| 3 | Transparency toggle（默认开可关） | Trust builders |
| 4 | Sound cue | Identifiers |
| 5 | UILibrary 跨平台统一组件库 | UILibrary |
| 6 | Branching（节点分叉探索） | Governors |
| 7 | Tone selector / Persona picker | Tuners |
| 8 | Voice / Drag and drop 入口 | Inputs |

> P2 候选 8 条，按"价值递减 / 成本递增"排序。

---

## 第一轮建议（5 个主题）

### 主题 1：Agent 当前状态可见性

- **核心问题**：用户不知道 AI 在做什么 / 做到哪了 / 还要多久
- **P0 行动项**：Status indicator 三态化（详见汇总表 #1）
- **P1 配套**：Long task 阶段名显式化
- **为什么优先**：状态不可见是 AI 产品**最普遍**的 UX 失败模式。Telegram typing bubble 解决"是否在线"，但解决不了"在做什么"。

### 主题 2：长任务进度和阶段提示

- **核心问题**：单步任务用户能容忍"思考中"，但 5 步任务只显示"思考中"会让人焦虑
- **P0 行动项**：Long task 阶段名显式化（详见汇总表 #5）
- **P1 配套**：Format selector 让用户控制进度显示格式
- **设计原则**：阶段名优于百分比。"提取 → 翻译 → 校对" 比 "进度 60%" 更有信息量

### 主题 3：用户中断 / 撤销 / 回退

- **核心问题**：用户能停下但不能撤销；这是破坏性操作的安全网缺口
- **P0 行动项**：Stop 链路口径明确（详见汇总表 #2）
- **P1 配套**：Undo、Edit prompt、Version history
- **设计原则**：所有"已执行"动作都要有"撤销"路径。所有"已发送"内容都要能"回看"。

### 主题 4：执行动作与建议草稿的区分

- **核心问题**：AI 输出"建议"和"已执行"语义模糊，用户容易把草稿当结果
- **P0 行动项**：Inline Action 加"预览 / 已生效"标签（详见汇总表 #3）
- **P1 配套**：Human review 强制确认
- **设计原则**：草稿和已执行必须**视觉上不同**。建议和动作必须**结构上分离**。

### 主题 5：证据、来源、日志、commit、live 状态的展示

- **核心问题**：用户看不到"为什么 AI 这样回答"、"这个改动是否真的应用了"、"现在 live 状态如何"
- **P0 行动项**：Source citation 三件套（详见汇总表 #4）
- **P1 配套**：Confidence score、Explanation
- **设计原则**：每次自动化输出都要带"证据" + "状态" + "可验证链接"。三件套缺一不可。

### 主题 6（额外）：多 agent 并发写入时的状态提示

- **核心问题**：sub-agent 并发时用户不知道谁在写、写了什么、会不会冲突
- **现状**：未做
- **P1 候选**：在 P1 末或 P2 初推进
- **设计原则**：sub-agent 写入应当有**显式前缀或 tag**，让用户能区分"哪个 agent 写了这行"。

---

## 与 6 层 AI Experience 的对应关系

> 复用 checklist v1 的 6 层映射（Model / Prompt / Interface / Workflow / System / Emergence），不重新做。

| 6 层 | 覆盖度（来自 checklist v1） | v1 审计判断 | 主要 P0 / P1 行动项 |
|---|---|---|---|
| **Model** | — | 不适用 | — |
| **Prompt** | 14%（5/37 = 14%） | Tuners 全部"未评估" — 调节器几乎为零 | P1: Format selector、Length control、Prompt library |
| **Interface** | 49%（18/37 = 49%） | 主体已具备，Workspaces 缺显式 | P1: Example gallery、Workspaces 显式化 |
| **Workflow** | 22%（8/37 = 22%） | Stop 链路、Undo、Edit prompt 全缺 | **P0: Stop 链路口径明确、Long task 阶段名；P1: Undo、Edit prompt、Version history、Feedback loop** |
| **System** | 27%（10/37 = 27%） | Trust builders 大部分缺，Source 不规范 | **P0: Source citation 三件套、Human review；P1: Confidence score** |
| **Emergence** | 27%（10/37 = 27%） | 跨 agent 标识、长期记忆、delegation 全缺 | P2: 跨平台 avatar 一致性、UILibrary 统一 |

### 6 层视角的判断

- **Interface 做得最好**（49%）— Wayfinders / Identifiers / 部分 Inputs 都已具备
- **Workflow 最弱**（22%）— 控制类功能（Undo / Edit / Branching / Version / Feedback）几乎全缺
- **System 第二弱**（27%）— Trust builders 是最大缺口
- **Prompt 形式上低**（14%）但**实质影响最大** — 因为用户每次都在用 prompt 调节

**v1 重点推进方向**：Workflow + System 是 P0 行动项的主要来源，Prompt 是 P1 重点。

---

## 下一步实施路线

### 阶段 1：无代码流程规范（0-2 周）

**目标**：在不写代码的情况下让用户感知到 UX 改进。

**做法**：

1. **Status indicator 三态化**：改 system prompt 让模型在长任务中显式输出"执行中: 提取 → 翻译 → 校对"阶段
2. **Long task 阶段名显式化**：同 1，作为 prompt 模板固化
3. **Source citation 三件套**：在 web_search / patch / push 类操作的 system prompt 中要求"每次回复带 URL + 置信度 + 验证时间"

**不做**：

- 不写新工具
- 不改 home channel 行为
- 不引入 UI 组件

**验证**：

- 跑 10 个长任务，记录是否能看到三态进度
- 跑 5 个 web_search 类任务，记录 Source citation 三件套是否齐全
- 用户反馈：阶段名是否更清晰

### 阶段 2：报告模板（2-6 周）

**目标**：把"做了什么 / 证据是什么 / live 状态"作为固定结构输出。

**做法**：

1. **设计"操作报告"标准模板**：
   - 标题：操作类型 + 目标
   - 中段：分步执行结果（每步：做了什么、结果、证据）
   - 末段：live 状态验证（链接、截图、curl 输出）
2. **在 update_site / patch / push 类工具后强制使用该模板**
3. **把"Trust builders"中"Source citation / Human review / Explanation"三项通过模板化降低边际成本**

**不做**：

- 不做 UI 组件
- 不引入新工具
- 不动 home channel 行为

**验证**：

- 抽样 20 个 patch / push 操作，看报告是否齐全
- 用户反馈：报告是否让"操作可验证"

### 阶段 3：UI / Dashboard（6 周以后）

**目标**：在前两阶段反馈证明 P0 仍有 UX gap 时才投入。

**做法**：

1. 真实按钮 / 进度条组件
2. 跨平台统一组件库（UILibrary）
3. Undo / Regenerate 等需要 UI 的 P1 项

**不做（除非必要）**：

- 不做"为做而做"的 UI 改造
- 不引入前端框架
- 不重写 home channel 集成

**启动条件**（任一满足才进入阶段 3）：

- 阶段 1 + 2 完成后用户反馈"P0 项仍有 UX gap"
- Tuners 调节器需要 UI 才有效（Temperature slider）
- 跨平台一致性出现严重问题

**反例警告**：

> 如果阶段 1 后用户已经满意，阶段 3 不应启动。流程和模板**永远优于** UI — UI 改起来贵，prompt 改起来便宜。

---

## 何时做 v2

满足以下任一条件时做 v2（本审计的下一轮）：

1. v1 中 5 条 P0 全部落地完成
2. 阶段 1+2 完成后有了真实用户反馈
3. 自检表 v1 的 20 个"未评估"项中超过半数被评估
4. Shape of AI 站点新增 / 删减模式

v1 → v2 之间不应有中间版本（避免审计口径漂移）。

---

## 变更日志

- **2026-06-26**：v1 初版。7 类审计 + P0/P1/P2 汇总 + 5 主题建议 + 6 层映射 + 3 阶段实施路线
- **v2 触发**：见上节 4 个条件
