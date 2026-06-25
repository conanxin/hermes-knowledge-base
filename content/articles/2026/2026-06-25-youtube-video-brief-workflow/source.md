# Source: YouTube Video Brief Workflow

## 能力来源

本工作流来源于对 Conan O'Brien 哈佛大学 2026 毕业演讲的完整解读实践。在处理该视频的过程中，沉淀出一套标准化的 YouTube 视频知识包生成流程。

## 关联文档

- **Workflow 文档**: `docs/workflows/youtube-video-brief-workflow.md`
- **命令文档**: `docs/commands/youtube-brief-command.md`

## 使用场景

当你想要：
- 深入理解一个 YouTube 视频的核心内容
- 将英文视频转化为可检索、可复用的中文知识
- 生成结构化的学习笔记和知识卡片
- 为写作、演讲、讨论准备素材

## 技术栈

- `baoyu-youtube-transcript` — 字幕提取
- OpenClaw subagent — 翻译和分析
- Hermes Knowledge Base — 知识存储和检索
