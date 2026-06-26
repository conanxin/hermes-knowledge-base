# Hermes Agent UI 自检表：来源与参考

## 派生来源

本条目是**派生内容（derived）**，不是原始翻译。核心源材料：

| 源 | URL | 用途 |
|---|---|---|
| The Shape of AI | https://www.shapeof.ai/ | 37 个 AI 交互模式的事实清单（6 大类 × 6 + 1 UILibrary） |
| The Layers of AI Experience | https://emilycampbell.co/writing/layers-of-ai-experience | 6 层 AI 体验模型，用于纵向映射 |
| Shape of AI 知识库条目 | `content/resource_collections/2026-06-26-shape-of-ai-ux-patterns/` | 本仓库内已导入的同源条目（中文版 collection / summary / notes / source） |

## 基于本仓库已有条目

```
2026-06-26-shape-of-ai-ux-patterns          (resource_collection)
2026-06-26-emilycampbell-layers-of-ai-experience  (article)
```

自检表中的 37 个模式名、说明和分类直接来自这两个条目；本表的价值在于把它们**结构化为可勾选 checklist**，并叠加 6 层模型作为纵向参照。

## 自检表的工程背景

Hermes Agent 是一个常驻、跨会话、可调用多种工具（terminal、browser、web_search、code_exec、delegate_task、cronjob、media 等）的 AI 助手。它不是单一产品而是一组 agent、subagent、sidecar 的集合（Hermes Agent、OpenClaw、ConPort 等）。这张自检表针对的是**用户能直接看到的交互层**——任何 agent 暴露给用户的命令、消息、UI 元素都应通过本表审视。

## 派生（derived）类型的设计取舍

| 候选类型 | 优点 | 缺点 | 结论 |
|---|---|---|---|
| `type: note` | 已有 4 文件结构；接受 summary + source + notes；最轻量 | 没有专门的"checklist"概念 | ✅ **采用** |
| `type: article` | 流量更大、容易被检索到 | 需要 `translation.zh-CN.md`，但本表本身就是中文原生，不是翻译 | ❌ 会与翻译语义混淆 |
| `type: project` | 适合有独立代码/产物 | 本表无独立代码，只是文档 | ❌ 类别不符 |
| `type: resource_collection` | 支持 `item_count`、支持 `collection.md` 表格 | 是资源清单类型，不是设计自检表 | ❌ 类别不符 |

**结论**：`type: note` 是最兼容的最小类型。完整 checklist 放在 `notes.md`，因为 `checklist.md` 不在 `note` 的合法 body 列表中（见 `scripts/generate_item_pages.py: BODY_FILES_BY_TYPE`）。

## 不复制的内容

- 不复制 Shape of AI 的 37 个模式的原始英文说明
- 不复制 The Layers of AI Experience 的全文翻译
- 每个模式用 1-2 句中文概括 + 1 条自检问题 + 1 个 Agent 场景 + 1 个状态/优先级
- 总字数控制在 2400-3000 中文字

## 维护约定

- **每月复盘**：根据 Hermes Agent 实际状态更新"已具备 / 需改进"项
- **新增模式**：当 Shape of AI 站点新增模式时，本表同步更新（保持 37 模式总量或更新计数）
- **跨 agent 共享**：OpenClaw、ConPort 的 UI 改进可引用本表 slug
- **优先级变更**：当某条 "P2 需改进" 项连续 3 个月未推进时，应评估是否降级或删除
