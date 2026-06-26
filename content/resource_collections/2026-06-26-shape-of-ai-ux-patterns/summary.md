# Shape of AI 概述

## 这是什么

**Shape of AI**（https://www.shapeof.ai/）是 Emily Campbell 维护的一个 AI 产品交互模式分类库。它将当前 AI 产品界面中反复出现的设计模式归纳为 6 大类、37 个具体模式，为 AI 产品设计师和开发者提供参考词汇表。

与一次性文章不同，Shape of AI 是一个**持续维护的 living reference**，会随 AI 产品形态的演进而更新。

---

## 为什么重要

AI 产品的交互设计仍处于早期探索阶段。设计师和开发者经常面临以下问题：

- 用户不知道 AI 能做什么（能力边界模糊）
- AI 输出不可控，用户缺乏调节手段
- 用户不信任 AI 的结果（黑箱问题）
- 多步骤 AI 工作流缺乏清晰的进度反馈

Shape of AI 提供了一套**共享的设计语言**——当团队讨论"我们需要一个 Temperature slider"或"这里应该用 Chained action"时，大家指向的是同一个已定义的模式，而不是各自想象。

---

## 与 "The Layers of AI Experience" 的关系

Emily Campbell 在 [The Layers of AI Experience](https://emilycampbell.co/writing/layers-of-ai-experience) 中提出了 AI 体验的 6 层模型：

1. **Interface**（界面层）
2. **Interaction**（交互层）
3. **Conversation**（对话层）
4. **Collaboration**（协作层）
5. **Delegation**（委托层）
6. **Companionship**（陪伴层）

Shape of AI 的模式库主要服务于**第 1-2 层**（Interface + Interaction），解决的是"用户如何与 AI 产品进行具体交互"的问题。6 层模型提供了宏观框架，Shape of AI 提供了微观工具箱——两者互为补充。

在 Emily 的原文中，Shape of AI 被描述为"同一作者的 AI 交互模式库，6 层模型的具体应用示例"。

---

## 6 大类模式解决的问题

| 类别 | 核心问题 | 典型场景 |
|------|---------|---------|
| **Wayfinders** | 用户不知道 AI 能做什么 | 首次使用、探索新功能 |
| **Inputs** | 用户不知道如何高效地向 AI 表达需求 | 多模态输入、快捷指令 |
| **Tuners** | 用户对 AI 输出不满意但不知如何调整 | 语气、长度、风格控制 |
| **Governors** | 用户担心 AI 失控或犯错 | 中断、撤销、版本回溯 |
| **Trust builders** | 用户不信任 AI 的输出 | 来源标注、置信度、解释 |
| **Identifiers** | 用户无法区分 AI 状态或内容 | 状态指示、AI 身份标识 |

---

## 使用建议

- **产品自检**：在 AI 功能设计评审时，对照 37 个模式检查是否覆盖了关键交互场景
- **竞品分析**：分析其他 AI 产品使用了哪些模式，识别设计差距
- **团队对齐**：用模式名称统一团队内部对交互设计的讨论语言
- **渐进采用**：不需要一次性实现所有模式，按产品阶段优先解决当前最突出的交互问题
