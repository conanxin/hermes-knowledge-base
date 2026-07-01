# Commands Index

Available commands in Hermes Knowledge Base.

---

## Unified Import Commands

### material-kb-import

**Purpose**: Route a URL or local file to an existing stable Hermes KB import path.

**Shortest call**: `解读并入库这个材料：<URL_OR_FILE>`

**Batch call**: `批量解读并入库这些材料：<materials.txt>`

**When to use**: First choice when the material may be a WeChat URL, saved WeChat HTML/Markdown/TXT, YouTube URL, generic web URL, or PDF.

**Output**: Material import markdown + JSON report; KB entry only when the routed stable importer supports the material.

**Safety boundaries**: Generic web URLs use `web_article_to_kb.py`; unsupported YouTube and PDF routes return `BLOCKED_UNSUPPORTED` instead of inventing a half-built importer.

**Documentation**: `docs/commands/material-kb-import-command.md`

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

### web-article-kb-import

**Purpose**: Import a publicly accessible ordinary web article into the knowledge base.

**Shortest call**: `解读并入库这个网页文章：<URL>`

**When to use**: When the material is a non-WeChat, non-YouTube HTTP(S) article page with publicly visible body text.

**Output**: KB article entry with metadata, source, translation mirror or placeholder, summary, notes, and raw payload.

**Safety boundaries**: No login, no cookie, no paywall bypass, no half-entry when full text cannot be verified.

**Documentation**: `docs/commands/web-article-kb-import-command.md`

---

### wechat-article-kb-import

**Purpose**: Import a WeChat Official Account article into the knowledge base.

**Shortest call**: `把这篇公众号文章加入 Hermes 知识库`

**When to use**: When you read a WeChat article worth archiving.

**Output**: KB entry with metadata, source, summary, notes, raw_payload

**Documentation**: `docs/commands/wechat-article-kb-import-command.md`

---

## PDF Commands

### pdf-ocr-kb-import

**Purpose**: OCR a local PDF (if scanned), translate the full text, and import it into the knowledge base.

**Shortest call**: `把这个本地 PDF OCR 识别、完整翻译并加入 Hermes 知识库：<PDF_PATH>`

**When to use**: When the user has a local PDF (already on disk) and wants it persisted in the KB — not just analyzed in chat.

**Output**: KB entry (6 files) + OCR report + catalog/index/site update + commit + push + live smoke

**Safety boundaries**:
- The user MUST supply an absolute PDF path; no guessing.
- "Analyze this PDF" without "入库" / "加入" is **read-only**; do not auto-import.
- No new system dependencies; only locally available tools (`pdfinfo`, `pdftotext`, `pdftoppm`, `tesseract`).
- PDF is gitignored; `source.local-ref.txt` keeps the local pointer.
- No standalone project, no `projects/data.json` modification, no Telegram.

**Documentation**: `docs/commands/pdf-ocr-kb-import-command.md`

---

## How to Add New Commands

1. Create command documentation in `docs/commands/<command-name>-command.md`
2. Update this README
3. Create prompt template in `templates/prompts/<command-name>_prompt.md` (optional)
4. Update `docs/workflows/README.md` if the command introduces a new workflow
5. Update `docs/import-recipes/` if the command is a source-specific import path
6. Run `python3 scripts/check_kb.py` to verify

---

*Last updated: 2026-07-01*
