# 中文原文

## 说明

本文为 OpenClaw 工作流说明文档，原文即为中文，无需翻译。

## 工作流名称

YouTube Video Brief — 把 YouTube 视频变成中文知识包

## 核心流程

1. 获取视频 Metadata（标题、频道、时长、发布日期）
2. 提取字幕（优先人工字幕，其次自动字幕）
3. 翻译字幕为中文（保留时间戳）
4. 生成双语对照稿
5. 生成深度解读（analysis.zh.md）
6. 生成分享文章（summary-post.zh.md）
7. 生成知识库入口（index.md）
8. 生成永久笔记（notes.md）
9. 生成知识卡片（cards.md）
10. 生成执行报告（report.md）

## 输出目录规则

```
outputs/youtube-video-brief/YYYYMMDD-video-title-slug/
```

## 失败处理原则

- 无字幕 → BLOCKED
- 需要音频转写 → BLOCKED（需用户授权）
- 视频不可访问 → BLOCKED

## 扩展方向

- 导入 Hermes Knowledge Base
- 导入 Open Notebook
- 生成小红书笔记
- 生成公众号文章
- 生成播客提纲
- 生成 Anki 卡片
