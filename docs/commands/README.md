# Commands Index

Available commands in Hermes Knowledge Base.

---

## YouTube Commands

### youtube-preflight

**Purpose**: Check if a YouTube video is accessible before processing.

**Shortest call**: `预检这个 YouTube 视频：<YOUTUBE_URL>`

**When to use**: Before any video processing to avoid wasted effort.

**Output**: PASS / BLOCKED / PARTIAL

**Safety boundaries**: No login, no cookie, no full video download, no bypass.

**Documentation**: `docs/commands/youtube-preflight-command.md`

---

### youtube-brief

**Purpose**: Generate a complete Chinese knowledge package from a YouTube video.

**Shortest call**: `解读这个 YouTube 视频：<YOUTUBE_URL>`

**When to use**: When you want to deeply understand a video and create reusable knowledge.

**Output**: 11 files (metadata, subtitles, analysis, notes, cards, report)

**Documentation**: `docs/commands/youtube-brief-command.md`

---

### youtube-kb-import

**Purpose**: Import an existing video knowledge package into Hermes Knowledge Base.

**Shortest call**: `解读这个 YouTube 视频并加入 Hermes 知识库：<YOUTUBE_URL>`

**When to use**: When you have a complete knowledge package and want to archive it.

**Output**: KB entry + index update + site publish

**Documentation**: `docs/commands/youtube-kb-import-command.md`

---

## Article Commands

### import-article

**Purpose**: Import and translate an article into the knowledge base.

**Shortest call**: `把这篇文章完整翻译并加入知识库：<URL>`

**When to use**: When you find an article worth archiving.

**Output**: KB entry with translation, summary, notes

**Documentation**: `docs/AGENT_COMMANDS.md`

---

### wechat-article-kb-import

**Purpose**: Import a WeChat Official Account article into the knowledge base.

**Shortest call**: `把这篇公众号文章加入 Hermes 知识库`

**When to use**: When you read a WeChat article worth archiving.

**Output**: KB entry with metadata, source, summary, notes, raw_payload

**Documentation**: `docs/commands/wechat-article-kb-import-command.md`

---

## How to Add New Commands

1. Create command documentation in `docs/commands/<command-name>-command.md`
2. Update this README
3. Create prompt template in `templates/prompts/<command-name>_prompt.md` (optional)
4. Run `python3 scripts/check_kb.py` to verify

---

*Last updated: 2026-06-29*
