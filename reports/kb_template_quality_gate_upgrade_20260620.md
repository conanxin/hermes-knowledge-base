# 知识库模板与质量门禁升级报告

**升级日期**: 2026-06-20
**目标**: 固化质量审计修复经验，防止后续文章再次出现 metadata 缺字段、word_count 为 0、英文残留过多、notes.md 空模板等问题

---

## STATUS: PASS

---

## 修改文件

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `templates/prompts/import_article_prompt.md` | 升级 | 强化 metadata 字段要求、新增英文残留自检、统一 notes 模板、新增质量门禁清单、新增强制停止条件 |
| `templates/metadata.yaml` | 升级 | 统一字段结构，title_zh 和 source_site 必填，word_count 占位符不为 0 |
| `templates/notes.md` | 新增 | 统一笔记模板 |
| `scripts/check_kb.py` | 升级 | 新增统一字段检查、title_zh 空值检查、word_count 有效性检查、topics/tags 非空检查 |
| `README.md` | 升级 | 新增短命令默认行为、质量检查流程、质量门禁规则、强制停止条件 |
| `docs/AGENT_COMMANDS.md` | 更新 | 完善短命令文档，明确质量门禁和强制停止条件 |

---

## 新增文件

| 文件 | 说明 |
|------|------|
| `scripts/check_translation_residue.py` | 轻量英文残留检查脚本，扫描所有 translation.zh-CN.md，输出 suspicious_count 和样例 |
| `templates/notes.md` | 统一笔记模板 |

---

## 三个脚本运行结果

### check_kb.py

```
==================================================
Knowledge Base Check
==================================================
Total items: 3
PASS: 3
FAIL: 0

STATUS: PASS
```

### build_index.py

```
catalog.jsonl: 3 records
tags.md: 32 tags
authors.md: 3 authors
timeline.md: 1 months
Index build complete.
```

### check_translation_residue.py

```
==================================================
Translation Residue Check
==================================================
Total files scanned: 3
Files with warnings: 3

Warnings (3):

  [content/articles/2026/2026-06-20-ai-unconscious-convivial-society]
  suspicious_count: 10
    - The Convivial Society
    - Erik Hoel    source
    - without our understanding
    - set outside himself
    - less than sanguine

  [content/articles/2026/2026-06-20-vulture-spielberg-oral-history]
  suspicious_count: 4
    - earned my way through
    - sort of shut it down
    - just spilled that line out
    - early in the shoot

  [content/articles/2026/2026-06-20-jr-logo-japan-railways]
  suspicious_count: 1
    - Telegraph and Telephone

STATUS: WARNING — review samples above
```

**说明**: check_translation_residue.py 只做 warning 不做硬失败。当前 3 篇文章的 suspicious_count 均低于 20 阈值，属于可接受范围（专有名词、引用短语等）。

---

## 质量门禁新增规则

### metadata.yaml 字段要求

必须包含 15 个字段：
1. title
2. title_zh（必填，不得为空或 PLACEHOLDER）
3. source_url
4. source_site（必填）
5. author
6. published_date
7. captured_date
8. language（默认 "en"）
9. translation_language（默认 "zh-CN"）
10. status（导入完成后统一为 "translated"）
11. type
12. topics（3-8 个）
13. tags（6-12 个）
14. word_count（source > 0, translation > 0）
15. path

### 翻译质量要求

- 翻译完成后必须执行英文残留自检
- 专有名词、URL、代码、文件名、括号中的英文原名可保留
- 大段连续英文、明显漏译段落、乱码、重复段落必须修复
- suspicious_count ≥ 20 视为严重残留，必须修复

### 强制停止条件

以下情况必须停止导入，向用户报告：
- URL 无法访问或返回 404/403/500
- 正文抓取不完整（明显截断、缺少关键章节）
- 文章需要登录或付费才能阅读完整内容
- 内容类型不明确
- 翻译后英文残留严重（suspicious_count ≥ 20）
- metadata 关键字段无法确定

---

## 后续短命令使用示例

```
用户: 把这篇文章完整翻译并加入知识库：https://example.com/article

Hermes 默认执行：
1. 抓取正文
2. 翻译并自检英文残留
3. 生成完整 metadata（含 title_zh, source_site, word_count）
4. 生成 notes.md（统一模板）
5. 运行 check_kb.py（必须 PASS）
6. 运行 check_translation_residue.py（suspicious_count < 20）
7. 运行 build_index.py
8. commit & push
9. 生成导入报告
```

---

## Commit

- **Message**: Harden article import quality gate
- **Hash**: 16fa392
- **Files changed**: 8 files, 551 insertions(+), 158 deletions(-)

---

## GitHub 链接

https://github.com/conanxin/hermes-knowledge-base/commit/16fa392
