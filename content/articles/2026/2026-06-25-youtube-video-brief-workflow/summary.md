# 把 YouTube 视频变成中文知识包

## 这个能力是什么

**YouTube Video Brief** 是一个端到端的视频解读工作流。你只需提供一个 YouTube 链接，系统会自动完成字幕提取、中文翻译、深度解读、知识卡片生成和报告输出，最终生成一个结构化的中文知识包。

## 输入是什么

- **YouTube URL**（必填）
- 目标语言（可选，默认中文）
- 输出目录（可选，自动命名）

## 输出是什么

一个完整的知识包，包含 11 个文件：

| 文件 | 说明 |
|------|------|
| metadata.json | 视频元数据 |
| transcript.original.srt | 原始英文字幕 |
| transcript.zh.md | 中文翻译字幕 |
| transcript.bilingual.md | 双语对照 |
| analysis.zh.md | 深度解读 |
| summary-post.zh.md | 分享文章 |
| index.md | 知识库总入口 |
| notes.md | 永久笔记 |
| cards.md | 知识卡片 |
| cover.jpg | 视频封面 |
| report.md | 执行报告 |

## 适合什么场景

- **学习**: 把英文演讲、课程、访谈转化为可检索的中文笔记
- **写作**: 为文章、演讲、讨论准备素材
- **研究**: 追踪特定主题的视频内容，建立知识索引
- **分享**: 生成适合发布的中文总结文章

## 为什么适合进入知识库

1. **可复用**: 一次配置，永久使用
2. **标准化**: 输出格式统一，便于检索和比较
3. **累积**: 每次解读都增加知识库的厚度
4. **连接**: 通过标签和索引，视频内容与其他知识条目自然关联

## 和 Hermes Knowledge Base 如何配合

- 解读产物直接存入知识库的 `content/articles/` 目录
- 自动参与索引构建（catalog.jsonl、tags.md、authors.md、timeline.md）
- 通过站点生成器自动发布到 GitHub Pages
- 支持语义检索和标签检索
