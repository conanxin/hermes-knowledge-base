# Source: 一键把 YouTube 视频加入知识库

## 能力来源

本能力基于 v0.3.18 成功案例（Conan O'Brien 哈佛大学 2026 毕业演讲解读入库）沉淀而来。在手动完成一次完整的"视频解读 → 知识库入库"流程后，将步骤固化成标准化工作流。

## 关联文档

- **YouTube Video Brief Workflow**: `docs/workflows/youtube-video-brief-workflow.md`
- **youtube-brief Command**: `docs/commands/youtube-brief-command.md`
- **YouTube KB Import Workflow**: `docs/workflows/youtube-video-kb-import-workflow.md`
- **youtube-kb-import Command**: `docs/commands/youtube-kb-import-command.md`

## 基线版本

- **Tag**: `v0.3.18-youtube-video-brief-kb-import`
- **Commit**: `87f5065`
- **日期**: 2026-06-25

## 使用场景

当你想要：
- 把已解读的 YouTube 视频产物加入长期知识库
- 让视频解读内容可检索、可关联、可发布
- 标准化入库流程，避免手工遗漏步骤
- 通过 GitHub Pages 与团队共享视频知识

## 技术栈

- OpenClaw subagent — 执行入库步骤
- Hermes Knowledge Base — 知识存储和索引
- GitHub — 版本控制和 Pages 发布
