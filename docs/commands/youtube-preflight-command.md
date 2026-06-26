# youtube-preflight

> **命令名称**: `youtube-preflight`
> **用途**: 在解读和入库 YouTube 视频前，先判断链接是否可处理
> **Workflow**: `youtube-link-preflight-workflow.md`
> **基线版本**: v0.3.20-youtube-kb-import-pilot
> **创建时间**: 2026-06-26
> **版本**: 1.0

---

## 一句话说明

YouTube 视频入库前的预检命令，判断链接是否可访问、是否有字幕，避免无效流程。

---

## 最短调用方式

```
预检这个 YouTube 视频：https://www.youtube.com/watch?v=VIDEO_ID
```

---

## 标准调用方式

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

最终回复：
PREFLIGHT_STATUS
VIDEO_ID
FAILURE_TYPE
FAILURE_ARCHIVE
NEXT_ACTION
```

---

## 输入参数

| 参数 | 必填 | 说明 |
|------|------|------|
| `VIDEO_URL` | ✅ | YouTube 视频链接或 ID |
| `需要字幕` | ❌ | 默认 yes |
| `允许自动字幕` | ❌ | 默认 yes |
| `允许音频转写` | ❌ | 默认 no |
| `归档失败` | ❌ | 默认 yes |

---

## 输出状态

| 状态 | 说明 | 下一步 |
|------|------|--------|
| **PASS** | 视频可访问且有字幕 | 进入 `youtube-kb-import` |
| **BLOCKED** | 不可处理，已归档失败 | 提供可访问链接或手动处理 |
| **PARTIAL** | 可访问但缺少字幕 | 需要用户确认是否允许轻量转写，默认不继续 |

---

## 失败归档规则

**归档路径**：
```
data/youtube-preflight-failures/YYYY/YYYY-MM-DD-<video-id>.json
data/youtube-preflight-failures/YYYY/YYYY-MM-DD-<video-id>.md
```

**归档内容**：
- JSON：结构化失败信息（video_id, failure_type, attempted_methods, safety_boundary 等）
- MD：人类可读失败说明（失败原因、尝试方法、安全边界、后续建议）

---

## 内部调用链

```
youtube-preflight
  ├── yt-dlp --skip-download --print-json（检查可访问性）
  ├── yt-dlp --skip-download --list-subs（检查字幕）
  ├── 分类失败原因
  ├── 生成 preflight.json
  └── 如失败，生成 failure archive
```

---

## 禁止行为

| 行为 | 后果 |
|------|------|
| 登录 YouTube | BLOCKED |
| 读取浏览器 Cookie | BLOCKED |
| 下载完整视频 | BLOCKED |
| 绕过地区限制 | BLOCKED |
| 伪造元数据 | BLOCKED |
| 把失败链接写成正式视频知识条目 | BLOCKED |

---

## 失败分类

| failure_type | 说明 |
|-------------|------|
| video_unavailable | 视频不可访问 |
| private_video | 私密视频 |
| deleted_video | 已删除视频 |
| geo_restricted | 地区限制 |
| login_required | 需要登录 |
| age_restricted | 年龄限制 |
| live_not_started | 直播未开始 |
| no_subtitles | 无字幕 |
| unsupported_url | 不支持的 URL |
| metadata_fetch_failed | 元数据获取失败 |
| unknown_failure | 未知失败 |

---

## 成功案例

```
PREFLIGHT_STATUS: PASS
VIDEO_ID: x2VHFgyawPE
TITLE: Inside the Mind of Anthropic CEO Dario Amodei
CHANNEL: Bloomberg Originals
DURATION: 4204
SUBTITLES: [en]
NEXT_ACTION: run_youtube_kb_import
```

## 失败案例

```
PREFLIGHT_STATUS: BLOCKED
VIDEO_ID: U9Im71aNhYu
FAILURE_TYPE: video_unavailable
FAILURE_ARCHIVE: data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.json
NEXT_ACTION: provide_accessible_link
```

---

## 关联文档

| 文档 | 路径 |
|------|------|
| YouTube Link Preflight Workflow | `docs/workflows/youtube-link-preflight-workflow.md` |
| YouTube KB Import Workflow | `docs/workflows/youtube-video-kb-import-workflow.md` |
| youtube-kb-import Command | `docs/commands/youtube-kb-import-command.md` |

---

## 与 youtube-kb-import 的关系

```
youtube-preflight ──PASS──→ youtube-kb-import ──→ KB 入库
        │
        └──BLOCKED──→ failure archive ──→ 返回失败原因
```

**规则**：
- youtube-kb-import 必须先调用 youtube-preflight
- 只有 PASS 才允许进入入库流程

---

*命令文档固化完成。可直接复制调用示例使用。*
