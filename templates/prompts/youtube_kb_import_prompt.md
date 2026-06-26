# YouTube Video Knowledge Base Import Prompt

## Purpose

This is a copy-paste prompt template for importing YouTube videos into Hermes Knowledge Base.

## Prompt Template

```markdown
请按照 youtube-video-kb-import-workflow.md 处理这个 YouTube 视频，并加入 Hermes Knowledge Base：

VIDEO_URL:
<YOUTUBE_URL>

要求：
- 先执行 youtube-link-preflight
- 如果 PASS，提取字幕、翻译、解读、生成笔记和卡片
- 导入 Hermes Knowledge Base
- 更新索引和站点
- commit 并 push
- 如果 BLOCKED，生成 failure archive，不继续处理

最终回复：
OPENCLAW_STATUS
PREFLIGHT_STATUS
OUTPUT_DIR
VIDEO_ENTRY
FAILURE_ARCHIVE
REPORT_PATH
COMMIT
PUSH
```

## Example Usage

### Example 1: Successful Import

```markdown
请按照 youtube-video-kb-import-workflow.md 处理这个 YouTube 视频，并加入 Hermes Knowledge Base：

VIDEO_URL:
https://youtu.be/x2VHFgyawPE

要求：
- 先执行 youtube-link-preflight
- 如果 PASS，提取字幕、翻译、解读、生成笔记和卡片
- 导入 Hermes Knowledge Base
- 更新索引和站点
- commit 并 push
- 如果 BLOCKED，生成 failure archive，不继续处理

最终回复：
OPENCLAW_STATUS
PREFLIGHT_STATUS
OUTPUT_DIR
VIDEO_ENTRY
FAILURE_ARCHIVE
REPORT_PATH
COMMIT
PUSH
```

### Example 2: Preflight Only

```markdown
请按照 youtube-link-preflight-workflow.md 预检这个 YouTube 视频：

VIDEO_URL:
https://www.youtube.com/watch?v=U9Im71aNhYu

要求：
- 不登录
- 不读取 Cookie
- 不下载完整视频
- 检查视频是否可访问
- 检查字幕是否可用
- 如果失败，生成 failure archive

最终回复：
PREFLIGHT_STATUS
VIDEO_ID
FAILURE_TYPE
FAILURE_ARCHIVE
NEXT_ACTION
```

## Safety Boundaries

- No login
- No cookie reading
- No full video download
- No bypassing restrictions
- Blocked videos must be archived, not processed

## Related Documents

- `docs/workflows/youtube-video-kb-import-workflow.md`
- `docs/workflows/youtube-link-preflight-workflow.md`
- `docs/commands/youtube-kb-import-command.md`
- `docs/commands/youtube-preflight-command.md`
