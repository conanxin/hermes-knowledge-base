# 摘要：Karpathy Second Brain 实现指南

## 原始内容讲什么

本文是 Andrej Karpathy 提出的 "Second Brain" 知识管理系统的完整实现指南。核心理念是：人类负责筛选来源、提出好问题、思考意义；LLM 负责其他一切。文章包含 7 步构建流程（创建文件夹、写 Schema、填充 Raw、首次 Ingest、开始查询、月度检查、让它复合），以及系统失效场景（Context Window 天花板、Error Compounding、Hallucination、Cost、Enterprise 不适用、单模型盲点）和应对措施。

## 为什么值得迁移

- **高价值方法论**：Karpathy 是 AI 领域最具影响力的教育者之一，他的知识管理方法论具有广泛参考价值
- **完整 Prompt 库**：包含 Ingest、Query、Lint、Explore、Brief 等完整 Prompt 模板，可直接复用
- **实践验证**：Lex Fridman 等人在实际使用类似方案，多个开源实现 48 小时内出现
- **与当前知识库关联**：与 Karpathy LLM Wiki、Wiki vs RAG 分析、Nia Docs 等条目形成知识网络

## 迁移后如何使用

- **作为知识管理参考**：当需要设计个人知识库时查阅
- **Prompt 模板复用**：直接复制 Ingest/Query/Lint Prompt 用于新项目
- **风险评估**：在决定是否采用 Wiki 方案时参考失效场景分析
- **对比分析**：与 RAG、MCP 等其他知识管理方案对比使用

## 缺失信息或后续补充建议

- **成本估算**：文章提到 $2-5/源，但实际成本随模型变化，建议补充当前模型成本
- **工具推荐**：可补充具体工具（如 Obsidian、Notion、Git）与 Karpathy 方案的对比
- **中文社区实践**：可补充中文社区的 Second Brain 实践案例
