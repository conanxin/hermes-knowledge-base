# Source: 先预检，再解读 YouTube 视频

## 能力来源

本能力基于 v0.3.20 实战试运行中的真实失败案例（U9Im71aNhYu 不可访问）沉淀而来。

在 v0.3.20 期间：
- Dario Amodei 视频成功入库（验证了一键入库命令的可行性）
- U9Im71aNhYu 视频不可访问（暴露了缺少预检机制的问题）

## 关联文档

- **YouTube Link Preflight Workflow**: `docs/workflows/youtube-link-preflight-workflow.md`
- **youtube-preflight Command**: `docs/commands/youtube-preflight-command.md`
- **YouTube KB Import Workflow**: `docs/workflows/youtube-video-kb-import-workflow.md`
- **youtube-kb-import Command**: `docs/commands/youtube-kb-import-command.md`

## 失败归档

- **JSON**: `data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.json`
- **MD**: `data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.md`

## 基线版本

- **v0.3.20**: `v0.3.20-youtube-kb-import-pilot`（ae1458c）— 首次实战试运行
- **v0.3.21**: 预检与失败归档能力建设

## 使用场景

当你想要：
- 解读一个 YouTube 视频前先确认它是否可访问
- 避免在不可处理的视频上浪费时间
- 自动归档失败案例供后续参考
- 强制执行安全边界（不登录、不绕过限制）

## 技术栈

- yt-dlp — 视频元数据和字幕预检
- OpenClaw — 执行预检步骤
- Hermes Knowledge Base — 失败归档存储
