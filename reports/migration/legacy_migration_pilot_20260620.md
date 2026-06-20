# 旧知识库迁移试点报告

**日期**: 2026-06-20
**版本**: v0.2.0 legacy migration pilot
**目标**: 从旧 Hermes 知识库迁移 2 篇代表性内容到 hermes-knowledge-base

---

## STATUS: PASS

---

## 迁移内容

### 1. 知识型内容：Karpathy LLM Wiki

| 字段 | 值 |
|------|-----|
| 标题 | Karpathy 的 LLM Wiki：AI 知识管理新范式 |
| 旧库路径 | `~/.hermes/wiki/research/karpathy-llm-wiki.md` |
| 新库路径 | `content/legacy-knowledge/2026-04-07-karpathy-llm-wiki/` |
| 类型 | note |
| 来源 URL | https://x.com/elliotchen100/status/2040981753490477403 |
| 缺 source_url | 否 |
| 翻译 | 无（原文为中文笔记） |
| 字数 | 2062 |

**文件清单**:
- metadata.yaml
- source.md
- summary.md
- notes.md

### 2. 项目型内容：Hermes Agent Self-Evolution

| 字段 | 值 |
|------|-----|
| 标题 | Hermes Agent Self-Evolution |
| 旧库路径 | `~/.hermes/wiki/research/hermes-agent-self-evolution.md` |
| 新库路径 | `content/projects/2026-04-13-hermes-agent-self-evolution/` |
| 类型 | project |
| 来源 URL | https://github.com/NousResearch/hermes-agent-self-evolution |
| 缺 source_url | 否 |
| 翻译 | 无（原文为中文笔记） |
| 字数 | 1773 |

**文件清单**:
- metadata.yaml
- source.md
- summary.md
- notes.md

---

## 新增文件

| 文件 | 说明 |
|------|------|
| `docs/LEGACY_MIGRATION.md` | 迁移规范文档 |
| `templates/legacy_metadata.yaml` | 迁移 metadata 模板 |
| `content/legacy-knowledge/2026-04-07-karpathy-llm-wiki/metadata.yaml` | 知识型内容 metadata |
| `content/legacy-knowledge/2026-04-07-karpathy-llm-wiki/source.md` | 知识型内容原文 |
| `content/legacy-knowledge/2026-04-07-karpathy-llm-wiki/summary.md` | 知识型内容摘要 |
| `content/legacy-knowledge/2026-04-07-karpathy-llm-wiki/notes.md` | 知识型内容笔记 |
| `content/projects/2026-04-13-hermes-agent-self-evolution/metadata.yaml` | 项目型内容 metadata |
| `content/projects/2026-04-13-hermes-agent-self-evolution/source.md` | 项目型内容原文 |
| `content/projects/2026-04-13-hermes-agent-self-evolution/summary.md` | 项目型内容摘要 |
| `content/projects/2026-04-13-hermes-agent-self-evolution/notes.md` | 项目型内容笔记 |

## 修改文件

| 文件 | 修改 |
|------|------|
| `scripts/check_kb.py` | 兼容非 article 类型：不强制要求 translation.zh-CN.md 和 word_count.translation |

---

## 脚本运行结果

### check_kb.py

```
Total items: 6
PASS: 6
FAIL: 0
STATUS: PASS
```

### build_index.py

```
catalog.jsonl: 6 records (+2)
tags.md: 57 tags (+25)
authors.md: 6 authors (+2)
timeline.md: 2 months (+1)
Index build complete.
```

### check_translation_residue.py

```
Total files scanned: 4
Files with warnings: 4
STATUS: WARNING — review samples above
```

注意：check_translation_residue.py 只扫描了 4 个有 translation.zh-CN.md 的 article 类型文件，自动跳过了 2 个迁移条目（无 translation.zh-CN.md），符合预期。

---

## 发现的问题

| 问题 | 等级 | 状态 |
|------|------|------|
| check_kb.py 原逻辑强制所有类型都有 translation.zh-CN.md | P1 | 已修复 |
| check_kb.py 原逻辑强制所有类型都有 word_count.translation | P1 | 已修复 |
| metadata.yaml 中 null 值被 YAML 解析为 None，导致 check_kb.py 误判为缺失 | P2 | 已修复（用 "null" 字符串替代） |
| 迁移内容缺 translation.zh-CN.md，但 summary.md 需要说明为何无翻译 | P3 | 已处理 |

---

## 是否建议继续 Batch 1 剩余 5 篇

**建议：是，但需满足以下条件**

1. **确认每篇内容的价值**：确保内容有独立价值，不是临时笔记或过时信息
2. **确认来源 URL**：优先迁移有明确来源 URL 的内容
3. **确认无重复**：避免与已迁移内容或现有知识库内容重复
4. **分批进行**：每次迁移 2-3 篇，运行检查脚本后再继续

**Batch 1 剩余候选**（按优先级排序）：

| 优先级 | 内容 | 类型 | 说明 |
|--------|------|------|------|
| 高 | `karpathy-second-brain-guide.md` | note | 与已迁移的 LLM Wiki 直接相关 |
| 高 | `wiki-vs-rag-analysis.md` | note | 知识管理分析，有独立价值 |
| 中 | `transformer-decoding.md` | note | 技术笔记，但可能过时 |
| 中 | `nia-docs-filesystem.md` | project | 项目文档，但可能过时 |
| 低 | `awesome-llm-long-context.md` | note | 资源列表，维护成本高 |
| 低 | `awesome-ai-agents.md` | note | 资源列表，维护成本高 |

---

## 迁移规范验证

| 规范要求 | 状态 |
|----------|------|
| 不修改旧知识库任何文件 | 通过 |
| 不删除、不移动旧文件 | 通过 |
| 只从旧知识库复制内容 | 通过 |
| 每个迁移条目生成标准 metadata.yaml | 通过 |
| 保留 legacy_source_path | 通过 |
| source_url 缺失时标记 source_url_missing | 通过 |
| 非外部文章不伪装成 article | 通过 |
| 系统文档、配置、runbook、日志不迁移 | 通过 |
| 重复内容只迁移一份 | 通过 |
| 迁移后运行检查脚本 | 通过 |

---

## Git 信息

- **Commit**: 6a722b0
- **GitHub**: https://github.com/conanxin/hermes-knowledge-base/commit/6a722b0
- **Push**: 成功

---

## 下一步建议

1. **创建 v0.2.0 tag**: 标记 legacy migration pilot 完成
2. **继续 Batch 1**: 按优先级迁移剩余 5 篇内容
3. **监控索引质量**: 确保 build_index.py 正确索引迁移条目
4. **完善迁移规范**: 根据实际迁移经验更新 LEGACY_MIGRATION.md
