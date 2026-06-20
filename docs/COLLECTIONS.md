# Collections 规范

## 什么是 resource_collection

`resource_collection` 是一种特殊的知识库条目类型，用于存储**结构化资源列表**，而非单篇内容。

## 和 article/note/project 的区别

| 类型 | 内容 | 来源 | 翻译 | 典型文件 |
|------|------|------|------|----------|
| article | 单篇外部文章 | 有 source_url | 需要 translation.zh-CN.md | source.md + translation.zh-CN.md + summary.md + notes.md |
| note | 中文笔记/分析 | 可有 source_url | 无 | source.md + summary.md + notes.md |
| project | 项目文档 | 有 source_url | 无 | source.md + summary.md + notes.md |
| **resource_collection** | **结构化资源列表** | **可有 source_url** | **无** | **collection.md + summary.md + notes.md + metadata.yaml** |

## 适合放入 collections 的内容

- ArXiv 论文列表（按主题聚合）
- Hacker News 热门链接汇总
- Awesome 资源列表（如 awesome-llm, awesome-agent）
- 主题阅读清单（如 "AI 安全必读 20 篇"）
- 工具/项目资源库（如 "LLM 推理框架对比"）
- 数据集列表
- 课程/教程汇总

## 不适合放入 collections 的内容

- 单篇文章（应放入 articles/）
- 系统日志或运行记录
- 配置文件或环境说明
- 临时 runbook 或操作手册
- 个人日记或碎片笔记

## 目录结构

```
content/collections/
├── YYYY-MM-DD-collection-slug/
│   ├── metadata.yaml
│   ├── collection.md      # 资源列表主体
│   ├── summary.md         # 摘要
│   └── notes.md           # 个人笔记
```

## metadata.yaml 特殊字段

| 字段 | 说明 |
|------|------|
| `type` | 必须为 `resource_collection` |
| `item_count` | 列表中的条目数量，整数，> 0 |
| `collection_format` | 可选：jsonl / markdown_table / bullet_list |

## 收录标准

每个 resource_collection 必须说明：

1. **收录标准**：什么内容会被列入，什么不会
2. **更新频率**：静态快照还是持续维护
3. **质量门槛**：来源要求、最低信息量
4. **使用建议**：读者如何使用这个列表

## source_url 和 source_site 规则

- resource_collection 可以没有单一 source_url
- 如果没有明确外部来源 URL，使用：
  - `source_url: null`
  - `source_url_missing: true`
- resource_collection 可以没有单一 source_site
- 如果资源集合来自本地旧库或多来源整理，允许：
  - `source_site: null`

## item_count 规则

- `item_count` 必须大于 0
- `item_count` 必须与 `collection.md` 中表格条目数量一致
- 脚本会自动检查一致性

## 必需文件

- `metadata.yaml`
- `collection.md`
- `source.md`（保存原始内容或清理后的完整原始内容）
- `summary.md`
- `notes.md`

## 不创建的文件

- `translation.zh-CN.md`（resource_collection 不需要翻译）

## 检查规则

- `check_kb.py`：不强制 translation.zh-CN.md，但必须检查 item_count
- `build_index.py`：保留 item_count 字段
- `check_translation_residue.py`：跳过（无 translation）
