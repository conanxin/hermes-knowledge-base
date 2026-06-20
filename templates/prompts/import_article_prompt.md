# 文章导入任务

## 任务信息

- **来源 URL**: {{URL}}
- **内容类型**: {{CONTENT_TYPE}}
- **主题领域**: {{TOPICS}}
- **标签**: {{TAGS}}
- **特殊要求**: {{SPECIAL_REQUIREMENTS}}

---

## 执行步骤

### 1. 抓取正文

使用 web_extract 或 browser 工具抓取 {{URL}} 的完整正文内容。

- 优先使用 web_extract（更快、更便宜）
- 如果 web_extract 失败或内容不完整，降级到 browser_navigate + browser_snapshot
- 如果内容超过 5000 字符，web_extract 会返回摘要；此时必须切换到 browser 工具获取完整内容
- 对于超长文章（>40,000 字），使用 browser_console 执行 JavaScript 提取 article.innerText

### 2. 创建目录结构

在 `content/articles/YYYY/` 下创建文章目录：

```
content/articles/YYYY/YYYY-MM-DD-slugified-title/
├── metadata.yaml
├── source.md
├── translation.zh-CN.md
├── summary.md
├── notes.md
└── assets/          # 图片、附件等
```

目录名格式：`YYYY-MM-DD-` + 标题的 slug 化版本（小写、空格替换为连字符、去除特殊字符）。

### 3. 保存 source.md

将抓取的原始内容保存为 `source.md`，格式要求：

- 保留原文结构（标题、段落、列表）
- 清理广告、导航栏、页脚等无关内容
- 保留图片链接（后续可下载到 assets/）
- 在文件顶部添加来源注释：

```markdown
<!-- Source: {{URL}} -->
<!-- Captured: YYYY-MM-DD -->
```

### 4. 完整准确翻译

将 `source.md` 翻译为 `translation.zh-CN.md`：

- **必须完整翻译**，不允许摘要或节选
- 保留所有引用、数据、人名、地名
- 技术术语保留英文并附中文注释（如：blockchain（区块链））
- 长文章（>10,000 字）可分批次翻译，但输出必须是完整文件
- 翻译质量要求：准确 > 流畅 > 优雅
- **翻译完成后必须执行英文残留自检**：
  - 检查是否有大段连续英文未翻译
  - 检查是否有明显漏译段落、乱码、重复段落
  - 专有名词、URL、代码、文件名、括号中的英文原名可保留
  - 发现残留时修复后再继续下一步
- 在文件顶部添加：

```markdown
<!-- 原文来源: {{URL}} -->
<!-- 翻译日期: YYYY-MM-DD -->
```

### 5. 生成 metadata.yaml

```yaml
title: "文章标题"
title_zh: "中文标题"    # 必填，不得为空
source_url: "{{URL}}"
source_site: "来源站点名"  # 必填，如 Vulture、The Convivial Society
author: "作者名"
published_date: "YYYY-MM-DD"
captured_date: "YYYY-MM-DD"
language: "en"              # 原文语言
translation_language: "zh-CN"  # 翻译语言
status: "translated"        # 导入完成后统一为 translated
type: "{{CONTENT_TYPE}}"
topics:
  - "{{TOPICS}}"            # 建议 3-8 个
tags:
  - "{{TAGS}}"              # 建议 6-12 个
word_count:
  source: 0      # 必须根据 source.md 实际计算，不得为 0
  translation: 0  # 必须根据 translation.zh-CN.md 实际计算，不得为 0
```

**metadata 字段检查清单（导入完成后必须逐项确认）：**

- [ ] title 存在且非空
- [ ] title_zh 存在且非空（不得省略）
- [ ] source_url 存在且有效
- [ ] source_site 存在且非空
- [ ] author 存在且非空
- [ ] published_date 存在且格式为 YYYY-MM-DD
- [ ] captured_date 存在且格式为 YYYY-MM-DD
- [ ] language 存在（默认 "en"）
- [ ] translation_language 存在（默认 "zh-CN"）
- [ ] status 为 "translated"
- [ ] type 存在（如 "article"）
- [ ] topics 非空，建议 3-8 个
- [ ] tags 非空，建议 6-12 个
- [ ] word_count.source 为大于 0 的整数
- [ ] word_count.translation 为大于 0 的整数

### 6. 生成 summary.md

结构化摘要，包含：

```markdown
# 摘要：[文章标题]

## 一句话概括

## 详细摘要

## 关键人物

## 关键概念/作品/事件

## 背景信息

## 值得继续研究的问题

## 行动项
```

### 7. 生成 notes.md

使用统一模板（不得留空，使用占位符 `*`）：

```markdown
# 我的笔记

## 关键摘记

*

## 我的想法

*

## 可延伸研究

*

## 待确认问题

*
```

**禁止**：生成空模板后不做任何处理直接提交。如果用户尚未填写笔记，保留占位符即可。

### 8. 处理 assets/

- 如果文章包含图片，下载到 `assets/` 目录
- 图片命名：`image-001.jpg`, `image-002.png` 等
- 在 `source.md` 和 `translation.zh-CN.md` 中更新图片链接为相对路径
- 如果无法下载，保留原始 URL 并标注 `[图片未下载]`

### 9. 更新索引

运行：

```bash
cd ~/projects/hermes-knowledge-base
python3 scripts/build_index.py
```

### 10. 运行质量检查

```bash
cd ~/projects/hermes-knowledge-base
python3 scripts/check_kb.py
python3 scripts/check_translation_residue.py
```

**check_kb.py 必须 PASS**，否则修复问题后再继续。
**check_translation_residue.py 可以有 warning**，但严重残留必须修复。

**质量门禁清单：**
- [ ] check_kb.py: PASS — N items, 0 issues
- [ ] build_index.py: PASS — N records
- [ ] check_translation_residue.py: 无严重残留（suspicious_count < 10）
- [ ] metadata.yaml 字段完整（含 title_zh, source_site, language, translation_language, word_count）
- [ ] word_count.source > 0 且 word_count.translation > 0
- [ ] notes.md 使用统一模板

### 11. Commit

```bash
cd ~/projects/hermes-knowledge-base
git add -A
git status  # 确认变更
git commit -m "Add [文章标题] article"
```

### 12. Push

```bash
cd ~/projects/hermes-knowledge-base
git push origin main
```

### 13. 输出报告

创建报告文件 `reports/import_YYYYMMDD_slug.md`：

```markdown
# 导入报告：[文章标题]

**STATUS: PASS / PARTIAL / FAIL**

## 新增目录

`content/articles/YYYY/YYYY-MM-DD-slugified-title/`

## 新增文件

| 文件 | 大小 | 说明 |
|------|------|------|
| source.md | X KB | 原文 |
| translation.zh-CN.md | X KB | 中文翻译 |
| summary.md | X KB | 结构化摘要 |
| metadata.yaml | X B | 元数据 |
| notes.md | X B | 我的笔记 |

## 翻译字数

约 X 字符

## 索引更新结果

- catalog.jsonl: X 条记录
- tags.md: X 个标签
- authors.md: X 位作者
- timeline.md: X 个月份

## check_kb.py 结果

PASS / FAIL

## build_index.py 结果

PASS / FAIL

## Commit Hash

`XXXXXXX`

## GitHub 链接

https://github.com/conanxin/hermes-knowledge-base/commit/XXXXXXX

## 备注

- 特殊处理说明
- 遇到的问题和解决方案
```

---

## 质量标准

- [ ] 翻译完整，无遗漏段落
- [ ] 翻译完成后执行英文残留自检并修复
- [ ] metadata.yaml 字段完整（含 title_zh, source_site, language, translation_language, word_count）
- [ ] title_zh 非空
- [ ] word_count.source > 0 且 word_count.translation > 0
- [ ] notes.md 使用统一模板
- [ ] check_kb.py PASS
- [ ] check_translation_residue.py 无严重残留
- [ ] build_index.py 成功更新
- [ ] GitHub 上可访问
- [ ] 报告文件已生成

## 降级策略

如果某个步骤失败：

1. **web_extract 失败** → 使用 browser 工具
2. **browser 工具失败** → 使用 curl + 手动清理
3. **翻译过长** → 分批次处理，但输出必须合并为完整文件
4. **check_kb.py 失败** → 修复问题（通常是缺失文件或字段）
5. **check_translation_residue.py 严重残留** → 修复翻译后重新运行
6. **push 失败** → 检查网络，重试最多 3 次

## 强制停止条件

以下情况必须停止导入，向用户报告，不要强行入库：

- URL 无法访问或返回 404/403/500
- 正文抓取不完整（明显截断、缺少关键章节）
- 文章需要登录或付费才能阅读完整内容
- 内容类型不明确（无法判断是文章、论文、评论等）
- 翻译后英文残留严重（suspicious_count ≥ 20）
- metadata 关键字段无法确定（如作者、标题缺失）

## 禁止事项

- 不要修改 Hermes 源码
- 不要重启 hermes-gateway.service
- 不要安装新依赖（使用现有工具）
- 不要推送 GitHub 除非用户授权
- 不要发送 Telegram 消息
- 不要暴露 API key、token、secret
- **不要生成残缺入库结果（缺少文件、字段为 0、翻译不完整）**
