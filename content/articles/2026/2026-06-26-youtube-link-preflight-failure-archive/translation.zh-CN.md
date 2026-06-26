# 中文原文

## 说明

本文为 OpenClaw 工作流说明文档，原文即为中文，无需翻译。

## 命令名称

先预检，再解读 YouTube 视频 — YouTube Link Preflight

## 核心流程

1. 解析 YouTube URL / video id
2. 使用 yt-dlp metadata-only 检查可访问性
3. 检查字幕可用性
4. 分类失败原因
5. 生成 preflight.json
6. 如失败，生成 failure archive
7. 返回 PASS 或 BLOCKED

## 输入

- YouTube URL 或 video id
- 可选参数：需要字幕、允许自动字幕、允许音频转写、归档失败

## 输出

- PASS：视频可访问且有字幕，可以进入 youtube-kb-import
- BLOCKED：视频不可访问或无字幕，已归档失败

## 失败分类

- video_unavailable
- private_video
- deleted_video
- geo_restricted
- login_required
- age_restricted
- live_not_started
- no_subtitles
- unsupported_url
- metadata_fetch_failed
- unknown_failure

## 安全边界

- 不登录账号
- 不读取 Cookie
- 不下载完整视频
- 不绕过地区限制
- 不处理私密视频
- 不伪造字幕
- 不伪造元数据
- 不把失败视频当作成功知识条目
- 不对同一失效链接反复重试

## 关联能力

- youtube-preflight：预检命令
- youtube-kb-import：一键入库命令
- Hermes Knowledge Base：知识存储和索引
