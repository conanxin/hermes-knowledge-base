# Shape of AI 笔记

## 与 Hermes Agent 的关联

Hermes Agent 作为 AI 助手产品，可以从 Shape of AI 的模式库中直接借鉴以下设计：

### 已实现的模式

| 模式 | Hermes 中的体现 |
|------|----------------|
| **Follow up** | 对话中的上下文延续和建议 |
| **Chained action** | 多步骤任务执行（如：搜索→提取→总结） |
| **Inline Action** | 消息中的可点击操作（如：MEDIA 链接、代码执行） |
| **Connectors** | 与外部工具集成（terminal、browser、web_search） |
| **@ mention** | 技能调用（如 `/skill` 命令） |
| **Slash command** | 斜杠命令系统 |
| **Typing indicator** | 生成回复时的状态提示 |
| **Progress bar** | 长时间任务的状态反馈 |

### 可改进的模式

| 模式 | 改进机会 |
|------|---------|
| **Example gallery** | 在首次使用时展示 Hermes 的能力示例 |
| **Temperature slider** | 允许用户调节回复的创造性/确定性 |
| **Persona picker** | 切换不同专业领域的回复风格 |
| **Confidence score** | 对不确定的信息标注置信度 |
| **Source citation** | 对 web_search 结果标注来源 |
| **Explanation** | 解释为什么给出某个建议 |
| **Version history** | 保存和回溯对话的不同版本 |
| **Branching** | 从某个回复分叉探索不同路径 |

---

## 与 6 层 AI Experience 模型的对照

| 6 层模型 | Shape of AI 模式 | Hermes 现状 |
|---------|------------------|-------------|
| Interface | Wayfinders, Inputs | ✅ 基本覆盖 |
| Interaction | Tuners, Governors | ⚠️ 部分覆盖 |
| Conversation | Trust builders | ⚠️ 可加强 |
| Collaboration | Identifiers | ✅ 基本覆盖 |
| Delegation | — | 需设计委托边界 |
| Companionship | — | 长期记忆和个性化 |

---

## 产品自检表

基于 Shape of AI 的 37 个模式，可以构建一个 AI 产品交互设计自检表：

### Wayfinders 检查
- [ ] 用户首次使用时是否知道 AI 能做什么？
- [ ] 是否提供了示例展示能力边界？
- [ ] 复杂任务是否有步骤引导？

### Inputs 检查
- [ ] 是否支持多种输入方式（文本、语音、文件）？
- [ ] 是否有快捷指令或命令系统？
- [ ] 是否提供提示词模板？

### Tuners 检查
- [ ] 用户能否控制输出风格？
- [ ] 用户能否控制输出长度？
- [ ] 不满意时能否重新生成？

### Governors 检查
- [ ] 用户能否随时中断 AI？
- [ ] 能否撤销操作？
- [ ] 是否有版本历史？

### Trust builders 检查
- [ ] 是否标注信息来源？
- [ ] 是否解释推理过程？
- [ ] 是否显示置信度？

### Identifiers 检查
- [ ] AI 状态是否清晰？
- [ ] 内容是否标注 AI 生成？
- [ ] 进度是否可见？

---

## 后续行动

1. **定期回顾**：每季度对照 Shape of AI 检查 Hermes 的交互设计覆盖度
2. **模式实验**：选择 2-3 个高价值模式（如 Confidence score、Source citation）进行原型实验
3. **团队对齐**：在 AI 产品设计讨论中引入 Shape of AI 的术语体系
4. **跟踪更新**：关注 shapeof.ai 的新模式发布，及时更新本条目
