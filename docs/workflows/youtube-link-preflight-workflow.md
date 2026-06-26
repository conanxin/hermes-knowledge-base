# YouTube Link Preflight Workflow

> **版本**: 1.0
> **创建时间**: 2026-06-26
> **基线版本**: v0.3.20-youtube-kb-import-pilot
> **基线 commit**: ae1458c

---

## 工作流名称

**YouTube Link Preflight** — 在正式处理 YouTube 视频前，先判断链接是否适合进入视频解读与知识库入库流程

## 一句话描述

YouTube 视频入库前的预检工作流，判断链接是否可访问、是否有字幕，避免无效流程。

---

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `YouTube URL` 或 `video id` | ✅ | — | YouTube 视频链接或 ID |
| `目标语言` | ❌ | zh-CN | 期望的翻译目标语言 |
| `需要字幕` | ❌ | yes | 是否要求视频必须有字幕 |
| `允许自动字幕` | ❌ | yes | 是否接受 YouTube 自动生成的字幕 |
| `允许音频转写` | ❌ | no | 是否允许使用 Whisper 等工具进行音频转写 |
| `归档失败` | ❌ | yes | 是否将失败案例归档到 failure archive |

---

## 输出

### A. 成功预检输出

```json
{
  "preflight_status": "PASS",
  "video_id": "x2VHFgyawPE",
  "title": "Inside the Mind of Anthropic CEO Dario Amodei",
  "channel": "Bloomberg Originals",
  "duration": 4204,
  "availability": "public",
  "subtitle_languages": ["en"],
  "recommended_next_action": "run_youtube_kb_import"
}
```

### B. 失败预检输出

```json
{
  "preflight_status": "BLOCKED",
  "video_id": "U9Im71aNhYu",
  "url": "https://www.youtube.com/watch?v=U9Im71aNhYu",
  "failure_type": "video_unavailable",
  "failure_reason": "Video unavailable. This video is not available. The uploader may have removed it or set it to private.",
  "attempted_methods": [
    "yt-dlp metadata-only check",
    "curl with standard User-Agent",
    "curl with alternate User-Agent"
  ],
  "safety_boundary": {
    "no_login": true,
    "no_cookie": true,
    "no_full_video_download": true,
    "no_bypass": true
  },
  "recommended_next_action": "provide_accessible_link",
  "failure_archive_path": "data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.json"
}
```

---

## 标准预检步骤

### Step 1：解析 YouTube URL / video id

从用户输入中提取 video id。支持格式：
- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`
- `VIDEO_ID`（纯 ID）

### Step 2：标准化 URL

统一转换为标准格式：`https://www.youtube.com/watch?v=VIDEO_ID`

### Step 3：使用 yt-dlp metadata-only 检查可访问性

```bash
yt-dlp --skip-download --print-json "VIDEO_URL"
```

提取信息：title, channel, duration, upload_date, description, subtitle_languages

### Step 4：禁止登录、Cookie、完整下载

- **不**使用 `--cookies-from-browser`
- **不**使用 `--username` / `--password`
- **不**使用 `-f bestvideo+bestaudio`（完整下载）
- **只**使用 `--skip-download` 和 `--list-subs`

### Step 5：检查视频状态

| 状态 | 处理 |
|------|------|
| public | 继续 Step 6 |
| unlisted | 继续 Step 6（但记录为 unlisted） |
| private | BLOCKED，failure_type: private_video |
| deleted | BLOCKED，failure_type: deleted_video |
| unavailable | BLOCKED，failure_type: video_unavailable |
| age_restricted | BLOCKED，failure_type: age_restricted |
| live_not_started | BLOCKED，failure_type: live_not_started |

### Step 6：检查字幕可用性

```bash
yt-dlp --skip-download --list-subs "VIDEO_URL"
```

| 情况 | 处理 |
|------|------|
| 有手动字幕（en/zh 等） | PASS，记录可用语言 |
| 只有自动字幕 | PASS（如果允许自动字幕），记录 auto-generated |
| 无字幕 | BLOCKED（如果需要字幕），failure_type: no_subtitles |
| 字幕提取失败 | BLOCKED，failure_type: metadata_fetch_failed |

### Step 7：分类失败原因

如果 Step 5 或 Step 6 失败，按以下分类：

| failure_type | 说明 |
|-------------|------|
| video_unavailable | 视频不可访问（已删除/私密/地区限制） |
| private_video | 私密视频 |
| deleted_video | 已删除视频 |
| geo_restricted | 地区限制 |
| login_required | 需要登录 |
| age_restricted | 年龄限制 |
| live_not_started | 直播未开始 |
| no_subtitles | 无字幕 |
| unsupported_url | 不支持的 URL 格式 |
| metadata_fetch_failed | 元数据获取失败 |
| unknown_failure | 未知失败 |

### Step 8：生成 preflight.json

将预检结果写入 JSON 文件。

### Step 9：如失败，生成 failure archive

```
data/youtube-preflight-failures/YYYY/YYYY-MM-DD-<video-id>.json
data/youtube-preflight-failures/YYYY/YYYY-MM-DD-<video-id>.md
```

### Step 10：返回 PASS 或 BLOCKED

最终状态：
- **PASS**：视频可访问且有字幕，可以进入 youtube-kb-import 流程
- **BLOCKED**：视频不可访问或无字幕，停止流程并归档失败

### Step 11：只有 PASS 才允许进入 youtube-kb-import 流程

---

## 失败分类详解

### video_unavailable

**症状**：yt-dlp 返回 "Video unavailable"
**可能原因**：
- 视频已删除
- 视频设为私密
- 地区限制
- 版权移除
- 需要登录

**处理**：BLOCKED，建议用户提供可访问链接或字幕/文字稿

### private_video

**症状**：yt-dlp 返回 "Private video"
**处理**：BLOCKED，私密视频无法处理

### deleted_video

**症状**：yt-dlp 返回 "Video unavailable. This video has been removed by the uploader."
**处理**：BLOCKED，已删除视频无法处理

### geo_restricted

**症状**：yt-dlp 返回 "The uploader has not made this video available in your country"
**处理**：BLOCKED，不绕过地区限制

### login_required

**症状**：yt-dlp 返回 "Sign in to confirm you're not a bot" 或类似
**处理**：BLOCKED，不登录 YouTube

### age_restricted

**症状**：yt-dlp 返回 "Sign in to confirm your age"
**处理**：BLOCKED，年龄限制视频需要登录

### live_not_started

**症状**：视频是直播但尚未开始
**处理**：BLOCKED，建议直播结束后再尝试

### no_subtitles

**症状**：yt-dlp --list-subs 返回空列表
**处理**：BLOCKED（默认），除非用户明确允许音频转写

### unsupported_url

**症状**：无法解析 URL 格式
**处理**：BLOCKED，要求提供标准 YouTube URL

### metadata_fetch_failed

**症状**：yt-dlp 无法获取元数据（网络问题、API 限制等）
**处理**：BLOCKED，建议稍后重试

### unknown_failure

**症状**：不属于以上任何分类
**处理**：BLOCKED，记录详细错误信息

---

## 安全边界

| 边界 | 规则 | 违反后果 |
|------|------|---------|
| **不登录账号** | 不使用 --cookies-from-browser 或 --username | BLOCKED |
| **不读取 Cookie** | 不访问浏览器 Cookie 文件 | BLOCKED |
| **不下载完整视频** | 只使用 --skip-download | BLOCKED |
| **不绕过地区限制** | 不使用 VPN 或代理绕过 | BLOCKED |
| **不处理私密视频** | 不尝试访问私密视频 | BLOCKED |
| **不伪造字幕** | 不生成虚假字幕文件 | BLOCKED |
| **不伪造元数据** | 不编造视频信息 | BLOCKED |
| **不把失败视频当作成功知识条目** | 失败视频不入库 | BLOCKED |
| **不对同一失效链接反复重试** | 同一链接失败一次后归档 | BLOCKED |

---

## 与一键入库流程的关系

```
用户请求
  │
  ▼
youtube-link-preflight
  │
  ├── PASS ──→ youtube-kb-import ──→ 视频解读 ──→ KB 入库
  │
  └── BLOCKED ──→ failure archive ──→ 返回失败原因
```

**规则**：
- youtube-kb-import 必须先调用 youtube-link-preflight
- preflight PASS 才进入原有流程
- preflight BLOCKED 则停止，并输出 failure archive

---

## 最短调用命令

```
预检这个 YouTube 视频：https://www.youtube.com/watch?v=VIDEO_ID
```

---

## 标准调用命令

```
请预检这个 YouTube 视频链接：

VIDEO_URL:
https://www.youtube.com/watch?v=VIDEO_ID

要求：
- 只做可访问性和字幕预检
- 不下载完整视频
- 不登录
- 不读 Cookie
- 如果失败，生成 failure archive

最终回复：
PREFLIGHT_STATUS
VIDEO_ID
FAILURE_TYPE
FAILURE_ARCHIVE
NEXT_ACTION
```

---

## 失败返回格式

```
PREFLIGHT_STATUS: BLOCKED
VIDEO_ID: U9Im71aNhYu
FAILURE_TYPE: video_unavailable
FAILURE_ARCHIVE: data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.json
NEXT_ACTION: provide_accessible_link
```

---

## 关联文档

| 文档 | 路径 | 说明 |
|------|------|------|
| YouTube Link Preflight Workflow | `docs/workflows/youtube-link-preflight-workflow.md` | 本工作流 |
| youtube-preflight Command | `docs/commands/youtube-preflight-command.md` | 预检命令 |
| YouTube KB Import Workflow | `docs/workflows/youtube-video-kb-import-workflow.md` | 一键入库工作流 |
| youtube-kb-import Command | `docs/commands/youtube-kb-import-command.md` | 一键入库命令 |

---

## 后续可扩展方向

1. **自动重试机制**：对 metadata_fetch_failed 类型的失败，支持定时重试
2. **批量预检**：支持同时预检多个 YouTube 链接
3. **历史记录**：建立预检历史数据库，避免重复检查同一链接
4. **用户通知**：预检 BLOCKED 时，自动通知用户并提供替代方案
5. **字幕源扩展**：支持从其他平台（Vimeo、Bilibili 等）预检

---

## 维护说明

- 每次发现新的失败类型，更新"失败分类"章节
- yt-dlp 版本升级后，验证预检逻辑是否仍然有效
- 新增扩展方向时，在"后续可扩展方向"追加

---

*Workflow 固化完成。可直接复制"最短调用命令"或"标准调用命令"使用。*
