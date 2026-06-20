# Resource Collection Schema 规范报告

**日期**: 2026-06-20
**审查人**: Hermes Agent
**版本**: v0.2.2
**记录总数**: 11 (未新增 collection 内容)

---

## STATUS: PASS

---

## 1. 新增文件

| 文件 | 说明 |
|------|------|
| `content/collections/` | 新目录，用于存放 resource_collection 类型条目 |
| `docs/COLLECTIONS.md` | 资源集合规范文档：定义、适用/不适用内容、目录结构、metadata 特殊字段 |
| `templates/collection_metadata.yaml` | resource_collection 专用 metadata 模板，含 item_count 等字段 |
| `templates/collection.md` | 资源集合内容模板：简介、收录标准、条目列表、主题标签、维护建议 |

---

## 2. 修改文件

| 文件 | 修改内容 |
|------|----------|
| `scripts/check_kb.py` | 支持 resource_collection：不强制 translation.zh-CN.md；检查 item_count（必须为数字且 > 0）；文件检查改为 collection.md + summary.md + notes.md + metadata.yaml |
| `scripts/build_index.py` | 添加注释说明 item_count 会被保留到 catalog.jsonl |
| `README.md` | 增加 `content/collections/` 目录说明 |

---

## 3. 脚本运行结果

### check_kb.py

```
Total items: 11
PASS: 11
FAIL: 0
STATUS: PASS
```

**说明**: 当前 11 条记录无 resource_collection，脚本向后兼容，未触发新规则。

### build_index.py

```
catalog.jsonl: 11 records
tags.md: 85 tags
authors.md: 10 authors
timeline.md: 3 months
Index build complete.
```

### check_translation_residue.py

```
Total files scanned: 4
Files with warnings: 4
STATUS: WARNING — review samples above
```

---

## 4. resource_collection 规范摘要

### 适用内容

- ArXiv 论文列表（按主题聚合）
- Hacker News 热门链接汇总
- Awesome 资源列表
- 主题阅读清单
- 工具/项目资源库
- 数据集列表
- 课程/教程汇总

### 不适用内容

- 单篇文章（应放入 articles/）
- 系统日志或运行记录
- 配置文件或环境说明
- 临时 runbook 或操作手册
- 个人日记或碎片笔记

### 目录结构

```
content/collections/
├── YYYY-MM-DD-collection-slug/
│   ├── metadata.yaml
│   ├── collection.md      # 资源列表主体
│   ├── summary.md         # 摘要
│   └── notes.md           # 个人笔记
```

### metadata 特殊字段

| 字段 | 要求 |
|------|------|
| `type` | 必须为 `resource_collection` |
| `item_count` | 整数，> 0 |
| `collection_format` | 可选：jsonl / markdown_table / bullet_list |

### 检查规则

- `check_kb.py`：不强制 translation.zh-CN.md；强制检查 item_count
- `build_index.py`：保留 item_count 到 catalog.jsonl
- `check_translation_residue.py`：自动跳过（无 translation）

---

## 5. 是否建议立即迁移 Batch 2

**建议**: 暂不迁移。

当前已建立完整的 resource_collection 规范，但 Batch 2 内容（ArXiv 列表、HN 热门等）需要额外整理和补充 metadata。建议：

- **保持规范就绪**：当需要迁移 Batch 2 时，直接按此规范执行
- **优先新内容**：继续通过短命令导入高质量外部文章
- **Batch 2 按需启动**：当需要系统整理某类资源时，再启动对应 collection 的迁移

---

## 6. Tag 状态

| Tag | Commit | 状态 |
|-----|--------|------|
| v0.1.2-import-template | 34d6384 | 已存在，正确 |
| v0.1.5-short-command-regression | d5121a7 | 已存在，正确 |
| v0.2.0-legacy-migration-pilot | 4e392fc | 已存在，正确 |
| v0.2.1-batch1-legacy-migration | 2c836f0 | 已存在，正确 |
| v0.2.2-full-kb-review | 7f3b51a | 已存在，正确 |

---

## 7. Commit

- Message: `Add resource collection schema`
- Changes: 3 新文件 + 3 修改文件
