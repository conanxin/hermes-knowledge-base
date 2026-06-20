# 知识库标签体系指南

## 标签设计原则

1. **具体优先**: 使用具体标签而非宽泛标签。例如 `Transformer` 优于 `AI`，`Hacker-News` 优于 `tech`。
2. **大小写统一**: 专有名词首字母大写（如 `Karpathy`, `ArXiv`），普通概念小写（如 `knowledge-management`, `long-context`）。
3. **语言一致**: 同一标签不使用中英文混用。优先使用英文标签，中文内容使用中文标签。
4. **避免重复**: 不使用近义标签。例如有 `knowledge-management` 就不再用 `knowledge-architecture`。
5. **控制数量**: 每篇内容 6-12 个标签，避免过度标签化。

## 标签分类

### 技术领域

| 标签 | 说明 | 示例内容 |
|------|------|----------|
| `llm` | 大语言模型 | LLM 相关论文、资源 |
| `transformer` | Transformer 架构 | 解码机制、注意力机制 |
| `rag` | 检索增强生成 | Wiki vs RAG 分析 |
| `knowledge-management` | 知识管理 | Second Brain, LLM Wiki |
| `agent` | AI Agent | Agent 自进化、Agent 训练 |
| `reinforcement-learning` | 强化学习 | 目标条件 RL |
| `federated-learning` | 联邦学习 | 移动自主系统 |
| `long-context` | 长上下文 | 长上下文 LLM 资源 |

### 来源平台

| 标签 | 说明 | 示例内容 |
|------|------|----------|
| `arxiv` | ArXiv 论文 | 论文列表 |
| `hacker-news` | Hacker News | 热门链接 |
| `github` | GitHub | 开源项目、awesome 列表 |
| `twitter` | Twitter/X | 推文、讨论 |

### 内容类型

| 标签 | 说明 | 示例内容 |
|------|------|----------|
| `awesome-list` | 精选资源列表 | awesome-llm-long-context |
| `tutorial` | 教程 | 机器学习基础教学 |
| `paper` | 学术论文 | ArXiv 论文 |
| `tool` | 工具 | 可视化工具、框架 |
| `news` | 新闻 | HN 热门、行业动态 |

### 人物/组织

| 标签 | 说明 | 示例内容 |
|------|------|----------|
| `karpathy` | Andrej Karpathy | Second Brain, LLM Wiki |
| `erik-hoel` | Erik Hoel | 意识研究 |
| `steven-spielberg` | Steven Spielberg | 口述史 |
| `nousresearch` | NousResearch | Hermes Agent |

## 标签使用建议

### 推荐标签组合

- **技术文章**: `llm` + `transformer` + `attention` + `architecture` + `tutorial`
- **资源列表**: `awesome-list` + `github` + `llm` + `resources` + `research`
- **HN 热门**: `hacker-news` + `news` + `machine-learning` + `community`
- **论文列表**: `arxiv` + `papers` + `ai-agents` + `research`

### 避免使用的标签

| 不建议 | 原因 | 替代方案 |
|--------|------|----------|
| `ai` | 过于宽泛 | 使用具体技术标签 |
| `tech` | 过于宽泛 | 使用具体领域标签 |
| `research` | 过于宽泛 | 使用具体研究方向 |
| `ai意识` | 中英文混用 | `consciousness` 或 `ai-consciousness` |
| `ai 产品` | 含空格 | `ai-product` |

## 标签维护

- 定期审查标签使用情况
- 合并重复标签
- 删除未使用的标签
- 更新标签指南

## 当前标签统计

- 总标签数: 107
- 标签分布: 技术领域 40%, 来源平台 15%, 内容类型 20%, 人物/组织 15%, 其他 10%
- 建议标签数: 每篇 6-12 个

## 标签修复记录

| 日期 | 修复内容 | 状态 |
|------|----------|------|
| 2026-06-20 | 识别重复标签和近义标签 | 已记录，未强制修复 |
| 2026-06-20 | 统一 resource_collection source_site 规则 | 已修复 |
| 2026-06-20 | 更新 COLLECTIONS.md 文档 | 已修复 |

## 注意事项

- 不要强行大规模重命名标签
- 只对明显重复或错误的标签做最小修复
- 标签体系应随知识库扩展逐步优化
- 保持标签的灵活性和可扩展性
