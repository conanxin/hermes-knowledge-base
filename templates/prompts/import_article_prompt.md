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
- 在文件顶部添加：

```markdown
<!-- 原文来源: {{URL}} -->
<!-- 翻译日期: YYYY-MM-DD -->
```

### 5. 生成 metadata.yaml

```yaml
title: "文章标题"
source_url: "{{URL}}"
author: "作者名"
published_date: "YYYY-MM-DD"
captured_date: "YYYY-MM-DD"
status: "imported"
type: "{{CONTENT_TYPE}}"
topics:
  - "{{TOPICS}}"
tags:
{{TAGS}}
word_count:
  source: 0      # 实际字数
  translation: 0  # 实际字数
```

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

```markdown
# 我的笔记

## 阅读日期
YYYY-MM-DD

## 第一印象

## 关键收获

## 与已有知识的联系

## 待深入研究的问题

## 行动项
```

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

### 10. 运行检查

```bash
cd ~/projects/hermes-knowledge-base
python3 scripts/check_kb.py
```

必须 PASS，否则修复问题后再继续。

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
- [ ] metadata.yaml 字段完整
- [ ] check_kb.py PASS
- [ ] build_index.py 成功更新
- [ ] GitHub 上可访问
- [ ] 报告文件已生成

## 降级策略

如果某个步骤失败：

1. **web_extract 失败** → 使用 browser 工具
2. **browser 工具失败** → 使用 curl + 手动清理
3. **翻译过长** → 分批次处理，但输出必须合并为完整文件
4. **check_kb.py 失败** → 修复问题（通常是缺失文件或字段）
5. **push 失败** → 检查网络，重试最多 3 次

## 禁止事项

- 不要修改 Hermes 源码
- 不要重启 hermes-gateway.service
- 不要安装新依赖（使用现有工具）
- 不要推送 GitHub 除非用户授权
- 不要发送 Telegram 消息
- 不要暴露 API key、token、secret
