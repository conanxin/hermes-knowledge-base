# 笔记：Wiki 代替 RAG 的可行性评估

## 关键洞察

- **当前架构已有 60% 基础**：存储、分类、索引已具备，缺自动化
- **最大差距是自动化**：Ingest/Lint/Query 三个核心操作均无自动化
- **Schema 是隐性瓶颈**：没有规范导致 LLM 每次按自己理解组织信息
- **Raw Sources 层缺失**：无法区分原始资料和 LLM 产出，无法验证来源

## 个人思考

- 当前 hermes-knowledge-base 已经是"改进版 Wiki"：有 metadata.yaml、有索引、有检查脚本
- 但缺少 Karpathy 强调的"复合效应"：知识应该随时间自动积累
- 可以考虑将 check_kb.py 和 build_index.py 作为 Lint 的雏形

## 行动项

- [ ] 设计 Ingest workflow skill（自动摄入新资料）
- [ ] 设计 Lint workflow skill（定期检查一致性）
- [ ] 创建 wiki/schema.md 定义规范
- [ ] 评估是否需要 Raw Sources 层

## 关联

- [[karpathy-llm-wiki]] — Karpathy Wiki 原始概念
- [[karpathy-second-brain-guide]] — 具体实现指南
- [[nia-docs-filesystem]] — 另一种知识管理方案
