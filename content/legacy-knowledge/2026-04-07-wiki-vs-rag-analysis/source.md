# 知识架构对比分析：Wiki 代替 RAG 的可行性评估

```
name: wiki-vs-rag-analysis
description: 当前知识架构与 Karpathy LLM Wiki 方案的对比分析
version: 1.0.0
tags: [analysis, wiki, rag, architecture]
hall: discoveries
```

## 当前架构概览

### 1. Wiki Navigator (新增)
- **存储**: Markdown 文件 (1758 行)
- **分类**: infrastructure / system-patterns / decisions / research
- **检索**: 元数据路由 + 关键词匹配
- **操作**: 手动维护，无自动化

### 2. Layered Memory System
- **存储**: JSON 文件 (semantic layer: 279 条)
- **架构**: 4 层 (Working/Episodic/Semantic/Reflection)
- **特点**: 认知科学启发的分层结构
- **状态**: 部分实现，semantic 层有数据

### 3. State.db (主数据库)
- **内容**: 会话、待办、工具调用记录
- **用途**: 运行状态管理

---

## Karpathy Wiki 核心要素 vs 当前实现

| 维度 | Karpathy Wiki 要求 | 当前实现 | 差距评估 |
|------|-------------------|----------|----------|
| **Raw Sources 层** | 原始资料不可变，仅 LLM 读取 | ❌ 无专门存储 | 需要新增 |
| **Wiki 层** | LLM 维护的 markdown 互相链接 | ⚠️ Wiki 目录存在 | 部分实现 |
| **Schema 层** | CLAUDE.md/AGENTS.md 定义规则 | ⚠️ AGENTS.md 存在 | 需增强 |
| **Ingest 操作** | LLM 读取资料 → 提取 → 整合进 wiki | ❌ 无自动化 | 需要实现 |
| **Query 操作** | 向 wiki 提问，LLM 综合回答 | ⚠️ 基本检索 | 需增强 |
| **Lint 操作** | 定期体检找矛盾/过时/孤立 | ❌ 无自动化 | 需要实现 |
| **Index/Log** | index.md 索引 + log.md 时间线 | ⚠️ index.md 存在 | 需完善 |

---

## 能力矩阵评估

### ✅ 已具备

| 能力 | 现状 |
|------|------|
| Markdown 存储 | ~/.hermes/wiki/ 1758 行 |
| 分类体系 | 4 个分类目录 |
| 元数据路由 | index.md 索引 |
| 知识条目结构 | semantic layer JSON |
| AGENTS.md 配置 | 存在 system prompt |

### ⚠️ 部分具备

| 能力 | 问题 |
|------|------|
| Wiki 页面互联 | 未实现跨页面链接 |
| index.md 摘要 | 仅包含顶层索引，缺少页面级摘要 |
| Schema 规则 | AGENTS.md 未定义 wiki 维护规范 |
| 持续积累 | 手动维护，无自动化 |

### ❌ 缺失

| 能力 | 影响 |
|------|------|
| Raw Sources 存储 | 无法区分原始资料和 LLM 产出 |
| Ingest 自动化 | 无法自动摄入新资料并整合 |
| Lint 自动化 | 无法自动检查一致性/过时 |
| Query 综合回答 | 简单检索，非语义理解 |
| Log 时间线 | 无法追踪知识演化 |

---

## 核心差距分析

### 1. 缺少 Raw Sources 层

**Karpathy 要求**: 原始资料单独存储，不可变，LLM 只读不写。

**当前状态**: 所有内容混在一起，无法回溯某个 wiki 页面来自哪个原始资料。

**影响**: 
- 无法验证知识来源
- 无法在原始资料更新后触发 wiki 刷新

**建议**: 创建 `~/.hermes/wiki/sources/` 目录，存放原始资料。

### 2. 缺少 Ingest 自动化

**Karpathy 要求**: 
- 丢资料进 raw 目录 → LLM 处理 → 写摘要 → 更新索引/实体/概念页面
- 一个资料来源可能触及 10-15 个 wiki 页面
- 人在回路，全程参与

**当前状态**: 手动写 wiki 页面，无自动化流程。

**影响**: 
- 无法实现"持续维护"而"每次查询重新推导"
- 知识无法真正"复合累积"

**建议**: 开发 ingest workflow skill。

### 3. 缺少 Lint 自动化

**Karpathy 要求**: 定期让 LLM 做体检 — 找矛盾、过时信息、孤立页面、缺失交叉引用。

**当前状态**: 无定期检查机制。

**影响**: 
- 知识一致性无法保证
- 页面可能变得混乱

**建议**: 开发 lint workflow skill + cronjob。

### 4. Schema 不完整

**Karpathy 要求**: 配置文件告诉 LLM wiki 结构、约定、操作流程。

**当前状态**: AGENTS.md 是通用配置，未定义 wiki 维护规范。

**影响**: LLM 每次按自己理解组织信息，结果混乱。

**建议**: 创建 `~/.hermes/wiki/schema.md` 定义 wiki 维护规范。

### 5. Query 能力不足

**Karpathy 要求**: 向 wiki 提问 → LLM 搜索相关页面 → 综合回答 (markdown/表格/图表)。

**当前状态**: 简单关键词检索。

**影响**: 无法实现"综合回答"，知识无法有效提取。

**建议**: 增强 query workflow skill。

---

## 结论：Wiki 代替 RAG 的可行性

### 当前阶段：基础具备，自动化缺失

| 维度 | 评分 | 说明 |
|------|------|------|
| 存储架构 | 6/10 | Wiki 结构存在，缺少 Raw Sources 层 |
| 分类体系 | 7/10 | 4 类分类，元数据路由 |
| 自动化 | 2/10 | 无 Ingest/Lint/Log 自动化 |
| Schema | 4/10 | AGENTS.md 存在但未定义 wiki 规范 |
| 操作闭环 | 3/10 | 缺 Ingest/Query/Lint/Log 完整流程 |

### 实现路径

**Phase 1: 补齐基础设施**
1. 创建 `wiki/sources/` 目录
2. 创建 `wiki/schema.md` 定义规范
3. 完善 `wiki/index.md` 页面级摘要

**Phase 2: 实现核心操作**
4. 开发 Ingest workflow skill
5. 开发 Lint workflow skill  
6. 实现 Query 综合回答能力
7. 实现 Log 时间线追踪

**Phase 3: 自动化闭环**
8. 设置 cronjob 定期 lint
9. 实现人在回路的 ingest 流程

### 评估

**能否实现 Wiki 代替 RAG?** — **技术上可行，需要工程实现。**

当前架构已有 60% 基础 (存储、分类、索引)，缺失的是自动化操作和 Schema 规范。实现 Karpathy 方案需要大约 3-5 个 skill + 配置的工程工作量。

---
*分析日期: 2026-04-07*
*对比: Karpathy LLM Wiki vs 当前 Hermes 知识架构*