# YouTube Capabilities

> **版本**: v0.3.23
> **创建时间**: 2026-06-26

---

## 1. Overview

Hermes Knowledge Base supports converting YouTube videos (with subtitles) into complete Chinese knowledge packages. This includes automatic subtitle extraction, translation, deep analysis, knowledge cards, and structured knowledge base entries.

The system also includes a preflight mechanism to check video accessibility before processing, with a failure archive for tracking blocked videos.

---

## 2. Capability Map

```
YouTube URL
    │
    ▼
youtube-preflight
    │
    ├── PASS ──→ youtube-video-brief ──→ youtube-kb-import ──→ KB Entry
    │
    └── BLOCKED ──→ Failure Archive
```

| Capability | Description | Status |
|-----------|-------------|--------|
| **Video Brief** | Extract subtitles, translate, generate analysis | ✅ Stable |
| **KB Import** | Import knowledge package into Hermes KB | ✅ Stable |
| **Preflight** | Check accessibility before processing | ✅ Stable |
| **Failure Archive** | Archive blocked videos with reasons | ✅ Stable |

---

## 3. Commands

### 3.1 youtube-preflight

**Purpose**: Check if a YouTube video is accessible and has subtitles before processing.

**Shortest call**:
```
预检这个 YouTube 视频：<YOUTUBE_URL>
```

**Output**: PASS / BLOCKED / PARTIAL

**When to use**: Before any video processing to avoid wasted effort.

**Safety boundaries**: No login, no cookie, no full video download, no bypass.

### 3.2 youtube-brief

**Purpose**: Generate a complete Chinese knowledge package from a YouTube video.

**Shortest call**:
```
解读这个 YouTube 视频：<YOUTUBE_URL>
```

**Output**: 11 files including metadata, subtitles, analysis, notes, cards.

**When to use**: When you want to deeply understand a video and create reusable knowledge.

### 3.3 youtube-kb-import

**Purpose**: Import an existing video knowledge package into Hermes Knowledge Base.

**Shortest call**:
```
解读这个 YouTube 视频并加入 Hermes 知识库：<YOUTUBE_URL>
```

**Output**: KB entry + index update + site publish.

**When to use**: When you have a complete knowledge package and want to archive it.

---

## 4. Workflows

### 4.1 youtube-video-brief-workflow

**Purpose**: End-to-end video processing from URL to knowledge package.

**Input**: YouTube URL
**Output**: 11 files (metadata, subtitles, analysis, notes, cards, report)

**Steps**:
1. Extract subtitles (yt-dlp)
2. Translate to Chinese
3. Generate bilingual transcript
4. Deep analysis
5. Summary article
6. Permanent notes
7. Knowledge cards
8. Report

**See**: `docs/workflows/youtube-video-brief-workflow.md`

### 4.2 youtube-video-kb-import-workflow

**Purpose**: Import existing knowledge package into Hermes KB.

**Input**: Video knowledge package directory
**Output**: KB entry + index + site update

**Steps**:
1. Check repository status
2. Create KB entry (metadata.yaml, summary.md, notes.md, source.md)
3. Sync workflow/command docs
4. Run check scripts
5. Build index
6. Update site
7. Commit and push

**See**: `docs/workflows/youtube-video-kb-import-workflow.md`

### 4.3 youtube-link-preflight-workflow

**Purpose**: Check video accessibility before processing.

**Input**: YouTube URL
**Output**: PASS / BLOCKED with failure classification

**Steps**:
1. Parse URL / video ID
2. Check accessibility (yt-dlp metadata-only)
3. Check subtitle availability
4. Classify failure if blocked
5. Generate failure archive if needed

**See**: `docs/workflows/youtube-link-preflight-workflow.md`

---

## 5. Success Path

```
User provides YouTube URL
    │
    ▼
[youtube-preflight] ──PASS──→
    │
    ▼
[youtube-video-brief] ──→ Knowledge Package (11 files)
    │
    ▼
[youtube-kb-import] ──→ KB Entry
    │
    ▼
[update_site.py] ──→ GitHub Pages
    │
    ▼
✅ Video available at https://conanxin.github.io/hermes-knowledge-base/
```

**Example success**:
- **Video**: Dario Amodei Bloomberg Interview
- **Tag**: v0.3.20-youtube-kb-import-pilot
- **KB Entry**: `content/articles/2026/2026-06-26-dario-amodei-bloomberg-interview/`

---

## 6. Failure Path

```
User provides YouTube URL
    │
    ▼
[youtube-preflight] ──BLOCKED──→
    │
    ▼
[Failure Archive]
    │
    ▼
❌ STOP: Report failure reason + suggestions
```

**Example failure**:
- **Video ID**: U9Im71aNhYu
- **Failure type**: video_unavailable
- **Archive**: `data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.json`
- **Reason**: Video may have been removed, set to private, or region-restricted

---

## 7. File Outputs

### Successful Video

| File | Description | Size (typical) |
|------|-------------|---------------|
| `metadata.json` | Video metadata (title, channel, duration, etc.) | ~1 KB |
| `transcript.original.srt` | Original English subtitles | ~100 KB |
| `transcript.zh.md` | Chinese translated subtitles | ~50 KB |
| `transcript.bilingual.md` | Bilingual side-by-side subtitles | ~150 KB |
| `analysis.zh.md` | Deep analysis and interpretation | ~50 KB |
| `summary-post.zh.md` | Shareable article | ~10 KB |
| `notes.md` | Permanent structured notes | ~25 KB |
| `cards.md` | Knowledge cards (10-15 cards) | ~15 KB |
| `index.md` | Knowledge base entry index | ~2 KB |
| `report.md` | Processing report | ~2 KB |
| `cover.jpg` | Video cover image (optional) | ~50 KB |

### Failure Archive

| File | Description |
|------|-------------|
| `YYYY-MM-DD-video-id.json` | Structured failure data |
| `YYYY-MM-DD-video-id.md` | Human-readable failure report |

---

## 8. Safety Boundaries

| Boundary | Rule | Violation Result |
|----------|------|-----------------|
| No login | Do not use YouTube account credentials | BLOCKED |
| No cookie | Do not read browser cookies | BLOCKED |
| No full download | Only extract subtitles and metadata | BLOCKED |
| No bypass | Do not use VPN/proxy to bypass restrictions | BLOCKED |
| No private videos | Do not process private videos | BLOCKED |
| No fake subtitles | Do not generate fake subtitle files | BLOCKED |
| No fake metadata | Do not fabricate video information | BLOCKED |
| Archive failures | Blocked videos must be archived, not disguised as successes | BLOCKED |

---

## 9. Version History

| Version | Tag | Description | Commit |
|---------|-----|-------------|--------|
| v0.3.18 | `v0.3.18-youtube-video-brief-kb-import` | First successful video brief case (Conan O'Brien) | 87f5065 |
| v0.3.19 | `v0.3.19-youtube-one-click-kb-import` | One-click KB import command capability | fd24d5c |
| v0.3.20 | `v0.3.20-youtube-kb-import-pilot` | First real-world video import pilot (Dario Amodei) | ae1458c |
| v0.3.21 | `v0.3.21-youtube-preflight-failure-archive` | Link preflight and failure archive | 1b73df5 |
| v0.3.22 | `v0.3.22-music-player-js-loader-fix` | Music player JS loader fix | 82fd039 |
| v0.3.23 | `v0.3.23-youtube-capability-oss-exposure` | OSS exposure and documentation | bbb693c |

---

## 10. Examples

### Example 1: Successful Video Import

```
User: 解读这个 YouTube 视频并加入 Hermes 知识库：https://youtu.be/x2VHFgyawPE

System:
  [youtube-preflight] PASS
  [youtube-video-brief] 11 files generated
  [youtube-kb-import] KB entry created
  [update_site.py] Site updated

Result: content/articles/2026/2026-06-26-dario-amodei-bloomberg-interview/
```

### Example 2: Blocked Video

```
User: 解读这个 YouTube 视频并加入 Hermes 知识库：https://www.youtube.com/watch?v=U9Im71aNhYu

System:
  [youtube-preflight] BLOCKED
  [failure archive] data/youtube-preflight-failures/2026/2026-06-26-U9Im71aNhYu.json

Result: Video unavailable. Please provide an accessible link.
```

---

## Related Documents

- `docs/workflows/youtube-video-brief-workflow.md`
- `docs/workflows/youtube-video-kb-import-workflow.md`
- `docs/workflows/youtube-link-preflight-workflow.md`
- `docs/commands/youtube-brief-command.md`
- `docs/commands/youtube-kb-import-command.md`
- `docs/commands/youtube-preflight-command.md`
