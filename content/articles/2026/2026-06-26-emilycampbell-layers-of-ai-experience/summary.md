# 摘要：AI 体验的层次

## 核心论点

生成式 AI 让数字产品从"决定论式"的设计范式跃迁为"概率论式"——设计师无法再为每一种输出状态预先规定 UI 路径，而是要像系统设计者那样，理解并操作**界面之下**的多个相互依赖的层次。本文是 Emily Campbell 提出的 **AIUX 6 层模型**的一次完整阐述，作者将其与 Jesse James Garrett（2000）的 *Elements of User Experience* 以及 Jamie Mill（2021）的 *Elements of Product Design* 接续成"决定论 → 预期式 → 概率式"的三阶段设计史脉络。

**一句话总结**：AI 产品是"多层次概率系统"，设计师的职责从控制单层 UI 扩展到对模型 / 驾驭层 / 上下文 / 治理 / 涌现的"全栈式影响力"。

## 6 层模型一览

| 层级 | 英文 | 设计者关心的问题 | 关键张力 |
|------|------|------------------|----------|
| 用户界面层 | User Interface | 何时从"指令"过渡到"监督" | 渐进式自主 vs. 用户掌控感 |
| 上下文层 | Context | 显式输入 vs. 推断输入；保留 vs. 丢弃 | Context rot vs. 个性化深度 |
| 驾驭层 | Harness | 连接器 / 工具 / 技能 / 智能体的权限与编排 | 自主性 vs. 风险；粒度 vs. 信任 |
| 模型层 | Model | 训练、能力、行为三维度 | 推理深度 vs. 延迟；通用 vs. 垂直 |
| 治理层 | Governance | 规则 / 标准 / 偏好三类外部约束 | 合规 vs. 品牌个性；Anthropic vs. OpenAI 的可见差异 |
| 涌现 | Emergence | 可观测性 / 可解释性 / 来源追溯 | 不可消除的变异性是特征而非 bug |

## 历史脉络（关键对比表）

| 阶段 | 代表人物 / 文献 | 设计关注范围 | 核心隐喻 |
|------|-----------------|----------------|----------|
| 决定论式设计 | Jesse James Garrett, *The Elements of User Experience* (2000) | 5 个相互依存的层面（产品策略 → 视觉设计） | 设计师是"意图编排者" |
| 预期式设计 | Jamie Mill, *The Elements of Product Design* (2021) | 解空间 + 问题空间 + 真实世界 | 设计师是"结果促成者" |
| 概率式设计 | Emily Campbell, 本文 | 6 层 AIUX + 模型 + 治理 + 涌现 | 设计师是"杠杆点操作者"（Donella Meadows） |

## 三个关键概念区分

1. **方向（direction） vs. 监督（oversight）** — 同一界面在不同生命周期阶段承担不同职能。早期需要用户"指挥"模型，后期界面退化为"监督面板"。
2. **显式上下文 vs. 推断上下文** — 显式由用户主动提供（目标、顾虑、导入数据），推断由系统从行为模式、集成系统、历史交互中自动生成。地图揭示式类比。
3. **连接器 / 工具 / 技能 / 智能体** — 驾驭层内部的四要素层级，定义数据访问（连接器）→ 动作权限（工具）→ 知识注入（技能）→ 自主编排（智能体）的递进结构。

## 关键引文

> "The user experience development process is all about ensuring that no aspect of the user's experience with your site happens without your conscious, explicit intent."
> — Jesse James Garrett, *The Elements of User Experience*

> "Spare me the 'design is dead' takes. Design is more important than ever."

> "AI asks designers to go one layer deeper again: into the model, the harness, the context, the policies, and the emergent behaviors that produce the experience before it ever reaches the interface."

> "随机性是这些体验的必要组成部分，事实上是特性而非 bug：不确定性正是生成式系统价值的一部分。"

> "That makes emergence distinct from the other layers. It is not something designers configure directly. It is something they design around, monitor for, and respond to as the system encounters conditions the team could not fully predict."

## 一句话总结

> AI 产品是概率性多层次系统；设计师的角色正在从"控制表层 UI"演化为"对 6 层全栈拥有足够语言能力去影响、缓解与接受其影响"——既非"设计已死"，也非"设计师必须变 ML 工程师"，而是需要**多语境的"全栈式设计语言能力"**。

## 延伸阅读

- **Jesse James Garrett**, *The Elements of User Experience* (2000) — http://www.jjg.net/elements/
- **Jamie Mill**, *The Elements of Product Design* (2021) — https://jamiemill.com/blog/2021-07-10-elements-of-product-design/
- **Donella Meadows**, *Leverage Points: Places to Intervene in a System* — https://donellameadows.org/archives/leverage-points-places-to-intervene-in-a-system/
- **John Maeda**, *2017 Design in Tech Report* — https://designintech.report/wp-content/uploads/2017/03/dit-2017-1-0-7-compressed.pdf
- **Liu et al.**, *Lost in the Middle: How Language Models Use Long Contexts* (Stanford, 2023) — https://cs.stanford.edu/~nfliu/papers/lost-in-the-middle.arxiv2023.pdf
- **Understanding AI**, *Context Rot: The Emerging Challenge* — https://www.understandingai.org/p/context-rot-the-emerging-challenge
- **OpenAI**, *Where the Goblins Came From* (goblins / GPT-5.5 incident) — https://openai.com/index/where-the-goblins-came-from/
- **Emily Campbell** 维护的 **Shape of AI**（AI 交互模式库）— https://www.shapeof.ai/
