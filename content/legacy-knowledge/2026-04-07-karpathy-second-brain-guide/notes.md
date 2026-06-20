# 笔记：Karpathy Second Brain 实现指南

## 关键洞察

- **分工理念**：人类策展 + LLM 执行，这是知识管理的新范式
- **无数据库方案**：纯文本 + 文件夹，降低技术门槛
- **复合效应**：4-6 周后从"搜索笔记"变成"查询知识系统"
- **Error Compounding 是最大的隐性风险**：AI 错误会自我强化

## 个人思考

- 当前 hermes-knowledge-base 已经是类似结构，但缺少自动化 Ingest/Lint
- 可以考虑将 Karpathy 的 Prompt 模板整合到知识库导入流程中
- Monthly lint 可以作为 cronjob 实现

## 行动项

- [ ] 测试 Karpathy 的 Ingest Prompt 模板
- [ ] 设计月度 lint 工作流
- [ ] 评估当前知识库是否已达到"复合"阶段

## 关联

- [[karpathy-llm-wiki]] — 同一作者的另一篇高价值内容
- [[wiki-vs-rag-analysis]] — 技术架构对比
- [[nia-docs-filesystem]] — 另一种知识管理方案
