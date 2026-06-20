# Agent Commands

## 短命令：导入文章到知识库

当用户说以下任意一种表达时，Hermes 默认执行完整导入流程：

- "把这篇文章完整翻译并加入知识库：【URL】"
- "入库并完整翻译：【URL】"
- "加入知识库：【URL】"
- "翻译后入库：【URL】"
- "把这篇文章完整翻译并加入知识库：URL"

### 默认行为

| 参数 | 默认值 |
|------|--------|
| content_type | article |
| 翻译语言 | zh-CN |
| 目录名格式 | YYYY-MM-DD-来源-slug |
| tags/topics | 由 Hermes 根据内容自动判断 |
| commit & push | 自动执行 |

### 执行流程

1. 抓取正文（web_extract → browser 降级）
2. 创建目录结构
3. 保存 source.md
4. 完整翻译为 translation.zh-CN.md
5. 生成 metadata.yaml（含 title_zh, source_site, word_count 等完整字段）
6. 生成 summary.md
7. 生成 notes.md（使用统一模板）
8. 处理 assets/
9. 更新索引（build_index.py）
10. 运行质量检查（check_kb.py + check_translation_residue.py）
11. Commit & Push
12. 生成导入报告

### 质量门禁

导入完成后必须满足：

- check_kb.py PASS（0 issues）
- check_translation_residue.py 无严重残留（suspicious_count < 20）
- metadata.yaml 字段完整（含 title_zh, source_site, language, translation_language, word_count）
- word_count.source > 0 且 word_count.translation > 0
- notes.md 使用统一模板

### 强制停止条件

以下情况 Hermes 必须停止导入，向用户报告，不要强行入库：

- URL 无法访问或返回 404/403/500
- 正文抓取不完整（明显截断、缺少关键章节）
- 文章需要登录或付费才能阅读完整内容
- 内容类型不明确（无法判断是文章、论文、评论等）
- 翻译后英文残留严重（suspicious_count ≥ 20）
- metadata 关键字段无法确定（如作者、标题缺失）

### 追问场景

如果用户只说"把这篇文章加入知识库"但没有提供 URL，Hermes 应该追问：
"请提供文章 URL。"

如果用户提供多个 URL 且没有明确说明，Hermes 应该追问：
"您想导入哪一篇文章？请提供具体 URL。"

### 模板位置

完整导入流程模板：`templates/prompts/import_article_prompt.md`

metadata 模板：`templates/metadata.yaml`

notes 模板：`templates/notes.md`
