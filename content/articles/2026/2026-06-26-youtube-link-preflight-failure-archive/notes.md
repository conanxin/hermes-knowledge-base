# 能力笔记：先预检，再解读 YouTube 视频

## 核心问题

如何在一键入库 YouTube 视频前，先判断视频是否可访问、是否有字幕，避免无效流程和安全边界违反？

## 预检命令

### 最短命令
```
预检这个 YouTube 视频：https://www.youtube.com/watch?v=VIDEO_ID
```

### 标准命令
```
请按照 youtube-link-preflight-workflow.md 预检这个 YouTube 视频：

VIDEO_URL:
https://www.youtube.com/watch?v=VIDEO_ID

要求：
- 不登录
- 不读取 Cookie
- 不下载完整视频
- 检查视频是否可访问
- 检查字幕是否可用
- 如果失败，生成失败归档
```

## 内部判断流程

```
1. 解析 YouTube URL / video id
2. 标准化 URL
3. 使用 yt-dlp metadata-only 检查可访问性
4. 禁止登录、Cookie、完整下载
5. 检查视频状态（public/private/deleted/unavailable）
6. 检查字幕可用性
7. 分类失败原因
8. 生成 preflight.json
9. 如失败，生成 failure archive
10. 返回 PASS 或 BLOCKED
```

## 失败分类

| failure_type | 说明 | 可恢复？ |
|-------------|------|---------|
| video_unavailable | 视频不可访问 | ❌ |
| private_video | 私密视频 | ❌ |
| deleted_video | 已删除 | ❌ |
| geo_restricted | 地区限制 | ⚠️ |
| login_required | 需要登录 | ❌ |
| age_restricted | 年龄限制 | ❌ |
| live_not_started | 直播未开始 | ⏰ |
| no_subtitles | 无字幕 | ⚠️ |
| unsupported_url | 不支持的 URL | ❌ |
| metadata_fetch_failed | 元数据获取失败 | ⚠️ |
| unknown_failure | 未知失败 | ⚠️ |

## 失败归档结构

```
data/youtube-preflight-failures/
└── YYYY/
    ├── YYYY-MM-DD-<video-id>.json
    └── YYYY-MM-DD-<video-id>.md
```

**JSON 文件**：结构化失败信息（video_id, failure_type, attempted_methods, safety_boundary）
**MD 文件**：人类可读失败说明（失败原因、尝试方法、安全边界、后续建议）

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

## 和一键入库命令的组合方式

```
youtube-preflight ──PASS──→ youtube-kb-import ──→ KB 入库
        │
        └──BLOCKED──→ failure archive ──→ 返回失败原因
```

**规则**：
- youtube-kb-import 必须先调用 youtube-preflight
- 只有 PASS 才允许进入入库流程

## 可继续扩展方向

1. **自动重试机制**：对 metadata_fetch_failed 支持定时重试
2. **批量预检**：同时预检多个 YouTube 链接
3. **历史记录**：建立预检历史数据库，避免重复检查
4. **用户通知**：BLOCKED 时自动通知用户并提供替代方案
5. **多平台扩展**：支持 Vimeo、Bilibili 等平台预检

## 关联能力

- **youtube-preflight**：预检命令（本能力）
- **youtube-kb-import**：一键入库命令（v0.3.19/20）
- **youtube-video-brief**：视频解读工作流
- **Hermes Knowledge Base**：知识存储和索引
