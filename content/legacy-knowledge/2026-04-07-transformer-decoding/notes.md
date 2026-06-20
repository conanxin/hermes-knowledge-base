# 笔记：Transformer 解码机制解析

## 关键洞察

- **核心洞察**：Transformer 的复杂性来自组件堆叠，而非单个组件
- **RNN 两大问题**：遗忘 + 速度慢，Transformer 通过并行处理和 Attention 解决
- **tokens-in, tokens-out**：简洁的抽象，但实现细节复杂

## 个人思考

- 这是理解所有现代 LLM 的基础，值得反复阅读
- 原文是概述，需要配合代码实现才能真正理解
- 可以作为技术面试的核心复习材料

## 行动项

- [ ] 补充 PyTorch 实现代码
- [ ] 绘制架构图
- [ ] 对比 RNN/LSTM/Transformer/Mamba 的优缺点
- [ ] 理解 Multi-Head Attention 的数学推导

## 关联

- [[karpathy-llm-wiki]] — LLM 知识管理
- [[wiki-vs-rag-analysis]] — 知识架构对比
