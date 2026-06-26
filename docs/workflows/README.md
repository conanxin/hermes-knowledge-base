# Workflows Index

Available workflows in Hermes Knowledge Base.

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

## How to Add New Workflows

1. Create workflow documentation in `docs/workflows/<workflow-name>-workflow.md`
2. Update this README
3. Update `docs/commands/README.md` if new commands are introduced
4. Run `python3 scripts/check_kb.py` to verify

---

*Last updated: 2026-06-26*
