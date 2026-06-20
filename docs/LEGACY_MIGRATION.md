# 旧知识库迁移规范

**版本**: v0.2.0 legacy migration pilot
**日期**: 2026-06-20
**目标**: 将旧 Hermes 知识库中的高价值内容迁移到 hermes-knowledge-base

---

## 哪些旧内容适合迁移

### 适合迁移的内容

| 类型 | 示例 | 判断标准 |
|------|------|----------|
| 知识型笔记 | Karpathy LLM Wiki 解析、技术概念分析 | 有独立价值、结构清晰、有学习意义 |
| 项目文档 | Hermes 自进化系统、Nia Docs 文件系统 | 有长期参考价值、记录重要决策 |
| 资源列表 | Awesome LLM 长上下文、AI Agents 资源 | 经过筛选、有结构化整理 |
| 研究报告 | Wiki vs RAG 分析、Transformer 解码 | 有深度分析、有结论 |

### 不适合迁移的内容

| 类型 | 示例 | 原因 |
|------|------|------|
| 系统文档 | schema.md、index.md、log.md | 属于系统维护，非知识积累 |
| 操作手册 | runbooks、操作步骤 | 属于系统运维，非知识库内容 |
| 系统配置 | config.yaml、auth.json | 敏感信息，不适合公开 |
| 运行日志 | session 记录、cron 输出 | 临时性，无长期价值 |
| 备份文件 | .mp3b-backup、.mp4c-backup | 临时备份 |
| 原始抓取 | 未清理的 HTML/XML | 需先清理，否则质量差 |
| 治理报告 | skill-catalog 维护报告 | 过时快，维护成本高 |
| 工作区报告 | 项目-specific 报告 | 属于项目知识库，非通用知识 |
| 审计报告 | hydro0x01 审计、session guard | 属于项目知识库 |
| 临时文件 | 媒体占位、缓存、日志 | 无价值 |

---

## 迁移后的目录放置规则

### 知识型内容

```
content/legacy-knowledge/
├── YYYY-MM-DD-title-slug/
│   ├── metadata.yaml
│   ├── source.md
│   ├── summary.md
│   └── notes.md
```

- 使用 `content/legacy-knowledge/` 目录
- 目录命名：`YYYY-MM-DD-title-slug`
- `type: note`

### 项目型内容

```
content/projects/
├── YYYY-MM-DD-project-name/
│   ├── metadata.yaml
│   ├── source.md
│   ├── summary.md
│   └── notes.md
```

- 使用 `content/projects/` 目录
- 目录命名：`YYYY-MM-DD-project-name`
- `type: project`

### 外部文章（有 source_url）

```
content/articles/YYYY/YYYY-MM-DD-title-slug/
```

- 使用标准文章目录结构
- `type: article`
- 必须有 translation.zh-CN.md

---

## metadata 字段扩展规则

### 新增字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `legacy_source_path` | string | 旧知识库中的原始路径，用于追溯 |
| `source_url_missing` | boolean | 是否缺少来源 URL（true = 缺失） |
| `migrated_date` | string | 迁移日期（YYYY-MM-DD） |
| `migration_note` | string | 迁移备注（如"从旧 Wiki 迁移"、"缺来源 URL"） |

### 字段调整

| 字段 | 规则 |
|------|------|
| `source_url` | 有则写，无则写 `null` |
| `source_url_missing` | 无 source_url 时写 `true` |
| `source_site` | 有则写，无则写 `null` |
| `author` | 有则写，无则写 `null` |
| `published_date` | 有则写，无则写 `null` |
| `captured_date` | 写旧内容的创建/摄入日期 |
| `migrated_date` | 写迁移日期 |
| `status` | 迁移内容写 `migrated` |
| `type` | `note` / `project` / `article` |
| `translation_language` | 无翻译时写 `null` |
| `word_count` | 根据 source.md 计算 |

---

## legacy_source_path 字段说明

- **必填**：所有迁移条目必须包含此字段
- **格式**：旧知识库中的绝对路径或相对路径
- **示例**：`~/.hermes/wiki/research/karpathy-llm-wiki.md`
- **用途**：方便追溯原始内容，未来需要更新时可定位

---

## source_url_missing 字段说明

- **条件**：当旧内容没有明确的来源 URL 时设置
- **值**：`true` 或 `false`
- **示例**：
  - 从 Twitter 解析的内容：有 URL，写 `false`
  - 从 Workshop 笔记整理的内容：无 URL，写 `true`
  - 从多来源综合的内容：无单一 URL，写 `true`
- **后续处理**：标记为 `true` 的内容，未来如果找到来源可补充更新

---

## Batch 定义

### Batch 1：高价值、结构清晰、可直接迁移

- 知识型笔记（Karpathy LLM Wiki、Second Brain、Wiki vs RAG）
- 项目文档（Hermes 自进化、Nia Docs）
- 资源列表（Awesome 系列）

**标准**：有独立价值、结构清晰、无需大量清理

### Batch 2：需要补 metadata 后迁移

- 有内容但缺来源 URL（ArXiv 论文列表、HN 热门）
- 有内容但格式需调整

**标准**：内容有价值，但需要人工补充来源或调整格式

### Batch 3：需要人工判断

- 治理报告（skill-catalog 维护报告）
- Workshop 笔记
- 项目报告

**标准**：内容可能过时，需要人工判断是否有长期价值

### Archive：只归档不迁移

- 系统文档、配置、日志
- 备份文件、临时文件
- 原始抓取（未清理）

**标准**：不属于知识积累范畴

---

## 迁移后必须运行的检查脚本

```bash
cd ~/projects/hermes-knowledge-base

# 1. 检查知识库完整性
python3 scripts/check_kb.py

# 2. 重建索引
python3 scripts/build_index.py

# 3. 检查英文残留（跳过无 translation.zh-CN.md 的条目）
python3 scripts/check_translation_residue.py
```

**预期结果**：
- check_kb.py: PASS
- build_index.py: 记录数增加
- check_translation_residue.py: 无崩溃，无 translation 的条目自动跳过

---

## 迁移流程

1. **选择内容**：从 Batch 1 中选择高价值内容
2. **创建目录**：按规则创建目录结构
3. **复制内容**：从旧知识库复制 source.md
4. **生成 metadata**：使用 legacy_metadata.yaml 模板
5. **生成 summary**：说明旧内容主要讲什么、为什么值得迁移
6. **生成 notes**：使用统一模板
7. **运行检查**：check_kb.py + build_index.py
8. **提交 commit**：`Start legacy knowledge migration pilot`
9. **push 到 GitHub**

---

## 注意事项

- 不修改旧知识库任何文件
- 不删除、不移动旧文件
- 只从旧知识库复制内容到 hermes-knowledge-base
- 如果旧内容没有完整翻译，不要伪造 translation.zh-CN.md
- 如果原内容是中文笔记，translation_language 可写 null
- 对重复内容只迁移质量更高的一份，并在报告中记录重复来源
- 系统文档、配置、runbook、日志、临时报告不要迁移
