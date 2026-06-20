# Nia Docs — 把整个 Web 变成文件系统

```
name: nia-docs-filesystem
description: 用文件系统抽象解决 AI Agent 代码幻觉问题
version: 1.0.0
tags: [agent, documentation, filesystem, rag, mcp]
date: 2026-04-07
source: @arlanr (Nozomio Labs CEO)
source_url: https://x.com/arlanr/status/2041215978957389908
hall: discoveries
```

## 核心观点

**代码幻觉是数据问题，不是模型问题。**

- 每天 API 都在发布破坏性变更、弃用端点、重命名参数
- 模型训练数据是几个月甚至几年后的
- Agent 写出的代码看起来完美、编译通过，但运行时失败

## 现有方案局限

### RAG (检索增强) — 标准解法

- 分块文档 → 向量化 → 检索 top-K 片段
- 能解决 80% 问题
- **失效场景**：
  - 答案跨三页
  - 需要精确的函数签名（chunking 过程中丢失）
  - 检索给的是碎片，但 agent 需要完整图景

### MCP 的问题

- 每个工具需要 JSON schema、描述、参数构建
- 吃上下文空间
- 引入滥用风险

## Nia Docs 方案

> "What if every documentation site on the web was a directory you could `cd` into?"

### 核心洞察

1. **Agent 天生懂文件系统** — 数十亿 token 已嵌入模型权重
   - `tree`, `grep`, `find`, `cat README.md`, `grep -r "auth" .`

2. **文件系统 vs MCP**:
   - 130+ MCP 工具 → 每个都要配置、学习
   - 文件系统工具 → agent 先天就会

> @jerryjliu0: "an agent with filesystem tools and a code interpreter is just as general, if not more general, than an agent with 100+ MCP tools."

### 技术实现

#### 1. Index (索引)
- 首次访问 URL 时爬取站点
- 尊重 `llms.txt`，检测 OpenAPI specs，处理重定向
- URL → 文件路径 (例如 `docs.stripe.com/api/charges/create` → `/api/charges/create.md`)
- 自动检测共同路径前缀，解决 URL 结构不一致问题

#### 2. Serve (服务)
```
GET  /shell-docs/load?url=...       # 状态 + 完整 dump
GET  /shell-docs/{namespace}/read?path=...  # 单文件
POST /shell-docs/{namespace}/grep  # 正则搜索
GET  /shell-docs/{namespace}/ls?path=...   # 目录
GET  /shell-docs/{namespace}/tree  # 完整树
```
- gzip 压缩，一次请求获取所有文件
- 缓存 (Cache-Control: max-age=300) + 磁盘缓存 `~/.cache/nia-docs/`
- Namespace 共享 — 一人索引，大家受益

#### 3. Shell (客户端)
- 使用 **just-bash** — TypeScript 实现的 bash
- 整个文件系统是 in-memory JavaScript object
- 500 页文档的 `grep -r "webhook" .` 毫秒级完成

### 为什么不用真实沙箱？

| 指标 | Nia Docs | 真实沙箱 |
|------|----------|----------|
| 启动时间 | ~100ms (缓存) / ~2s (已索引) | 更慢 |
| 每会话计算 | 零 (客户端执行) | 需要资源 |
| 成本 | 低 (只读静态文本) | 高 |

> "A documentation shell doesn't need process isolation, writable storage, or a kernel. It needs string matching over a known set of files."

## 观测数据

Agent 收敛到一致工作流：
1. `tree` — 定向
2. `grep -rl` — 找相关文件
3. `cat` — 阅读

这正是人类开发者的操作方式。文件系统抽象是 agent 自然默认的行为。

## 更大愿景

> "The entire web should be navigable the same way a codebase is."

- API reference → 目录
- Changelog → 文件
- OpenAPI spec → JSON (直接 cat)

## 关键洞察

1. **抽象层级演进**:
   - Unix (1970s): 设备/进程/套接字 → 文件
   - DevOps (2010s): 代码制品 → 文件
   - Agentic AI (2020s): 上下文/记忆 → 文件

2. **知识 vs 工具**: 
   - MCP 是"给 agent 一堆工具"
   - 文件系统是"给 agent 一个它本来就理解的界面"

3. **端到端 vs 检索**: 
   - RAG 是"搜到什么返回什么"
   - 文件系统是"让 agent 自己逛"

4. **共享经济**: 
   - Namespace 共享 — 类似 CDN 的知识分发模型

## 关联

- [[arxiv-llm-systems]] — LLM 推理优化相关
- [[wiki-vs-rag-analysis]] — Wiki vs RAG 对比
- [[karpathy-llm-wiki]] — Karpathy Wiki 模式

---
*摄入日期: 2026-04-07*