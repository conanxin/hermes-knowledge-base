# Workflows Index

Available workflows in Hermes Knowledge Base.

---

## Unified Import Workflows

### material-kb-import-workflow

**Purpose**: Infer the material type and route it to an existing stable KB importer.

**Input**: One URL/local file, or an input-list with one URL/path per line
**Output**: Material import markdown + JSON report; KB entry when the routed importer supports it

**Relationship**: Called by `material-kb-import` command. Reuses WeChat import scripts and returns `BLOCKED_UNSUPPORTED` for routes not yet implemented.

**Documentation**: `docs/workflows/material-kb-import-workflow.md`

---

## YouTube Workflows

### youtube-video-brief-workflow

**Purpose**: End-to-end video processing from URL to knowledge package.

**Input**: YouTube URL
**Output**: 11 files (metadata, subtitles, analysis, notes, cards, report)

**Relationship**: Called by `youtube-brief` command. Preceded by `youtube-link-preflight-workflow`.

**Documentation**: `docs/workflows/youtube-video-brief-workflow.md`

---

### youtube-video-kb-import-workflow

**Purpose**: Import existing knowledge package into Hermes KB.

**Input**: Video knowledge package directory
**Output**: KB entry + index + site update

**Relationship**: Called by `youtube-kb-import` command. Requires `youtube-link-preflight-workflow` PASS.

**Documentation**: `docs/workflows/youtube-video-kb-import-workflow.md`

---

### youtube-link-preflight-workflow

**Purpose**: Check video accessibility before processing.

**Input**: YouTube URL
**Output**: PASS / BLOCKED with failure classification

**Relationship**: Must be called before `youtube-video-brief-workflow` and `youtube-video-kb-import-workflow`.

**Documentation**: `docs/workflows/youtube-link-preflight-workflow.md`

---

## Article Workflows

### article-import-workflow

**Purpose**: Import and translate articles into the knowledge base.

**Input**: Article URL
**Output**: KB entry with translation, summary, notes

**Documentation**: See `docs/AGENT_COMMANDS.md`

---

### wechat-article-kb-import-workflow

**Purpose**: Import a WeChat Official Account article into Hermes KB.

**Input**: JSON capture package from OpenClaw @tencent-weixin/openclaw-weixin
**Output**: KB entry + index + site update

**Relationship**: Called by `wechat-article-kb-import` command.

**Documentation**: `docs/workflows/wechat-article-kb-import-workflow.md`

---

## PDF Workflows

### pdf-ocr-kb-import-workflow

**Purpose**: End-to-end local PDF import: OCR (if scanned), translate, build KB entry, push, live smoke.

**Input**: Absolute path to a local PDF file on the user's machine
**Output**: KB entry (6 files) + OCR report + catalog/index/site update + commit + push
**Relationship**: Called by `pdf-ocr-kb-import` command. Loads `docs/import-recipes/PDF_OCR_LOCAL.md` (MUST).

**Documentation**: `docs/workflows/pdf-ocr-kb-import-workflow.md`

---

## How to Add New Workflows

1. Create workflow documentation in `docs/workflows/<workflow-name>-workflow.md`
2. Update this README
3. Update `docs/commands/README.md` if new commands are introduced
4. Update `docs/import-recipes/` if the new workflow is a source-specific import path
5. Run `python3 scripts/check_kb.py` to verify

---

*Last updated: 2026-07-01*
