# 笔记：Nia Docs — 把整个 Web 变成文件系统

## 关键洞察

- **核心问题**：代码幻觉是数据问题，不是模型问题
- **核心方案**：文件系统抽象 — Agent 天生懂 tree/grep/cat
- **vs MCP**：文件系统更通用，不需要学习 130+ 个工具
- **vs RAG**：文件系统让 Agent 自己逛，而不是给碎片

## 个人思考

- 这个方案与 Karpathy 的 Wiki 理念一致：给 Agent 一个它本来就理解的界面
- Namespace 共享是聪明的 CDN 知识分发模型
- 可以借鉴到 hermes-knowledge-base 的文档系统设计

## 行动项

- [ ] 评估 hermes-knowledge-base 是否可以采用文件系统抽象
- [ ] 研究 just-bash 的实现细节
- [ ] 对比 Nia Docs 与当前知识库文档系统的优劣

## 关联

- [[karpathy-llm-wiki]] — 知识管理哲学
- [[wiki-vs-rag-analysis]] — RAG 对比分析
- [[karpathy-second-brain-guide]] — 知识积累方法
