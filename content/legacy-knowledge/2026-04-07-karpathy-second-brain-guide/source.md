# Karpathy Second Brain — 完整实现指南

```
name: karpathy-second-brain-guide
description: 100K+ 收藏的 Karpathy Second Brain 实现指南，含 7 步流程和完整 prompts
version: 1.0.0
tags: [knowledge-management, llm, wiki, prompt, karpathy]
date: 2026-04-07
source: @godofprompt
source_url: https://x.com/godofprompt/status/2041265656893489419
hall: discoveries
```

## 核心理念

> "The human's job is to curate sources, direct the analysis, ask good questions, and think about what it all means. The LLM's job is everything else." — Andrej Karpathy

### vs 传统方式

| 传统方式 | Karpathy 方式 |
|----------|---------------|
| AI 每次从零搜索 raw 文件 | AI 读一次源，编译结构化 wiki |
| 每次上传文档、提问、获得答案 | AI 维护 wiki，每次直接读 wiki |
| 下一个 session 全部忘记 | 知识积累而非重置 |

### 结果
- ~100 篇文章，~400,000 字
- 无数据库、无 embedding、无向量存储
- 只有文件夹和文本文件

---

## 七步构建

### Step 1: 创建文件夹结构 (2 分钟)

```
my-knowledge-base/
├── raw/           # 源材料，AI 只读不修改
│   └── assets/    # 图片、截图、图表
├── wiki/          # AI 维护的 wiki
├── outputs/       # 报告、分析、查询答案
└── CLAUDE.md      # schema 文件
```

### Step 2: 写 Schema 文件 (关键步骤)

```markdown
# Knowledge Base Schema

## Identity
This is a personal knowledge base about [YOUR TOPIC].
Maintained by an LLM agent.

## Architecture
- raw/ contains immutable source documents. NEVER modify.
- wiki/ contains the compiled wiki. The LLM owns this entirely.
- outputs/ contains generated reports and query answers.

## Wiki Conventions
- Every topic gets its own .md file in wiki/
- Every wiki file starts with YAML frontmatter
- Use [[topic-name]] for internal links
- Every factual claim cites its source: [Source: filename.md]
- Flag contradictions explicitly

## Ingest Workflow
1. Read full source document
2. Discuss key takeaways with user
3. Create/update summary page in wiki/
4. Update wiki/index.md
5. Update ALL relevant entity and concept pages
6. Add backlinks
7. Flag any contradictions
8. Append entry to wiki/log.md
9. A single source should touch 10-15 wiki pages

## Query Workflow
1. Read wiki/index.md first
2. Read all relevant wiki pages
3. Synthesize answer with citations
4. If answer reveals new insights, offer to file it back
5. Save valuable answers to outputs/

## Lint Workflow (Monthly)
Check for contradictions, stale claims, orphan pages, missing cross-references.
```

### Step 3: 填充 Raw 文件夹 (10 分钟)

- 复制粘贴文章 → .md 或 .txt
- 导出其他应用的笔记
- 保存截图到 raw/assets/
- 粘贴研究报告、PDF、竞品分析
- **不要组织，不要重命名，不要清理** — 这是 AI 的工作

### Step 4: 首次 Ingest

**单个源 Ingest Prompt:**
```
"Read the schema in CLAUDE.md. Process [FILENAME] from raw/. Read it fully, discuss key takeaways with me, then: create summary page, update index, update all relevant pages, add backlinks, flag contradictions, log the ingest."
```

- 一次一个源，Karpathy 也是这样做的
- 5-10 个源后，wiki/ 有 index、log、15-30 个互联页面

### Step 5: 开始查询

**Query Prompt:**
```
"Read wiki/index.md. Answer: [QUESTION]. Cite wiki pages. If this answer is worth preserving, offer to file it as a new wiki page."
```

高价值问题：
- "这个知识库最大的三个缺口是什么？"
- "哪些来源互相不同意？为什么？"
- "基于现有内容，我下一步应该研究什么？"
- "写一个 500 字的 [主题] 简报"
- "[概念 A] 和 [概念 B] 之间有什么联系？"

**关键循环**: 好的答案应该存回 wiki

### Step 6: 月度健康检查

**Lint Prompt:**
```
"Run a full health check on wiki/ per the lint workflow in CLAUDE.md. Output to wiki/lint-report-[date].md with severity levels (🔴 errors, 🟡 warnings, 🔵 info). Suggest 3 articles to fill the biggest knowledge gaps."
```

- 防止系统慢慢腐烂
- AI 写的东西稍微错误，你保存后，下一个答案基于错误建造
- 两个月后，5 页强化同一个错误

### Step 7: 让它复合

4-6 周后，你不是在搜索笔记，而是在查询一个理解来源之间联系的结构化知识系统。

加速复合的方式：
- 文件探索输出存回 wiki/
- 添加可视化输出 (markdown tables, charts, Marp slides)
- 版本控制一切 (git repo)

---

## 系统会在哪里失效

### 1. Context Window 天花板
- ~100 篇文章和 ~400K 字可以工作
- 128K token 上下文只容纳 ~96K 字
- AI 通过 index 选择性读取，会遗漏东西
- "lost in the middle" 效应 — 长输入中间的信息被降低优先级

### 2. Error Compounding (最大风险)
- AI 写了一个微妙错误的 wiki 页面
- 你查询，错误进入你的答案
- 你把答案存回去
- 现在两页强化同一个错误
- Monthly linting 有帮助，但 linting 的 AI 和犯错的 AI 有同样的盲点

### 3. Hallucination 不会消失
- Wiki 方式减少 hallucination，因为 AI 基于你的来源 grounding 答案
- 但不消除它
- AI 仍然可能合成不存在的连接
- 而且 wiki 看起来权威 (干净的 markdown、交叉引用、引用)，你更容易信任错误信息

### 4. Cost 不是零
- 每个 ingest、query、lint 都消耗 token
- 一个源触及 10-15 页，用前沿模型可能花 $2-5
- 50 个源只是 ingestion 就要 $100-250

### 5. 不适用于 Enterprise
- Karpathy 说 index-file 方式在 ~100 篇文章可以无 RAG 工作
- 10,000+ 来源时这个模式失效
- index 太大，一致性不可能

### 6. 单模型盲点
- 整个 wiki 是一个模型对你来源的解释
- 模型有偏差和倾向
- 高风险决策，一个 gist 评论者建议独立跑 4+ 模型查询，然后比较一致性

---

## 应对措施

| 问题 | 解决方案 |
|------|----------|
| Error compounding | Monthly lint + 手动交叉检查关键 claims |
| Context limits | 每个 wiki 专注一个领域，多领域用多个知识库 |
| Cost | 前沿模型用于 ingest 和复杂查询，便宜模型用于简单更新 |
| Hallucination | Schema 要求每个 claim 有 source citation，没有则 lint flag |
| Scale | 接受这是个人工具，不是企业基础设施 |

---

## 为什么这仍然重要

> "Humans abandon wikis because maintenance grows faster than value."

- 你开始组织，感觉很棒两周，然后维护杀死动力
- LLM 不会无聊
- LLM 不会忘记更新交叉引用
- LLM 可以一次触碰 15 个文件而不抱怨

Lex Fridman 运行类似设置，生成交互式 HTML 可视化，创建"mini-knowledge-bases"加载到语音模式跑步时使用。

多个开源实现 48 小时内出现。这不再是实验，正在成为认真做研究的人的标准实践。

---

## 完整 Prompt 库

### Schema
复制 Step 2 的完整 CLAUDE.md 模板

### Ingest (单个源)
```
"Read the schema in CLAUDE.md. Process [FILENAME] from raw/. Read it fully, discuss key takeaways with me, then: create summary page, update index, update relevant pages, add backlinks, flag contradictions, log the ingest."
```

### Ingest (批量，少监督)
```
"Read CLAUDE.md. Process all unprocessed files in raw/ sequentially. For each: create summary, update index, update relevant pages, log the ingest. Proceed automatically."
```

### Query
```
"Read wiki/index.md. Answer: [QUESTION]. Cite wiki pages. If this answer is worth preserving, offer to file it as a new wiki page."
```

### Lint
```
"Run a full health check on wiki/ per the lint workflow in CLAUDE.md. Output to wiki/lint-report-[date].md with severity levels. Suggest 3 articles to fill gaps."
```

### Explore
```
"Read wiki/index.md and identify the 5 most interesting unexplored connections between existing topics. For each, explain what insight it might reveal and what source would help confirm it."
```

### Brief
```
"Based on everything in wiki/, write a 500-word executive briefing on [TOPIC]. Cite sources. Structure it as: current state, key tensions, open questions, recommended next steps."
```

---

## 关联

- [[karpathy-llm-wiki]] — Karpathy Wiki 原始概念
- [[wiki-vs-rag-analysis]] — Wiki vs RAG 对比
- [[wiki-navigator]] — Hermes Wiki 实现
- [[nia-docs-filesystem]] — Nia Docs 文件系统方案

---
*摄入日期: 2026-04-07*
