# Changelog

All notable changes to the Hermes Knowledge Base project.

## v0.3.25 — Release and Changelog Consolidation

### Added

- Added consolidated release/changelog view for the YouTube capability line.
- Added release notes for v0.3.18 through v0.3.24.
- Added public version map for video brief, KB import, preflight, failure archive, OSS docs, and public entry QA.
- Added `CHANGELOG.md` and `docs/RELEASES.md` for version navigation.

### Version Line Summary

| Version | Tag | Theme |
|---------|-----|-------|
| v0.3.18 | `v0.3.18-youtube-video-brief-kb-import` | YouTube video brief KB import |
| v0.3.19 | `v0.3.19-youtube-one-click-kb-import` | One-click YouTube KB import command |
| v0.3.20 | `v0.3.20-youtube-kb-import-pilot` | YouTube KB import pilot (Dario Amodei) |
| v0.3.21 | `v0.3.21-youtube-preflight-failure-archive` | YouTube preflight and failure archive |
| v0.3.22 | `v0.3.22-music-player-js-loader-fix` | Music player JS loader fix |
| v0.3.23 | `v0.3.23-youtube-capability-oss-exposure` | YouTube capability OSS exposure |
| v0.3.24 | `v0.3.24-youtube-public-entry-qa` | YouTube public entry QA |

---

## v0.3.24 — YouTube Public Entry QA

### Summary

Verified that YouTube capability public entry points are discoverable, navigable, and reusable. Fixed local path leaks in workflow/command docs.

### What Changed

- Fixed internal output directory path leaks in workflow/command docs (replaced with placeholder paths).
- Updated version history table in `docs/YOUTUBE_CAPABILITIES.md`.
- Verified all public docs contain no local absolute paths.

### User-Facing Impact

- External users can now safely read workflow docs without seeing internal paths.
- README, docs, commands, workflows, and prompt templates form a complete navigation chain.

---

## v0.3.23 — YouTube Capability OSS Exposure

### Summary

Documented YouTube capabilities for open-source users, making the video-to-knowledge workflow publicly discoverable.

### What Changed

- Added `docs/YOUTUBE_CAPABILITIES.md` with full capability map.
- Added `docs/commands/README.md` and `docs/workflows/README.md` as indexes.
- Added `templates/prompts/youtube_kb_import_prompt.md` for reusable prompts.
- Added YouTube video knowledge package section to `README.md`.

### User-Facing Impact

- First-time visitors can understand what YouTube capabilities exist.
- Users can copy prompt templates directly.

---

## v0.3.22 — Music Player JS Loader Fix

### Summary

Fixed a bug where the music player detail page did not load `app.js`, causing the verified play button to be unresponsive.

### What Changed

- Fixed script loading order on item detail pages.
- Added music player JS loader fix report.

### User-Facing Impact

- Verified music play buttons now work on item detail pages.
- Paste 1960s greatest songs listicle entries can play embedded tracks.

---

## v0.3.21 — YouTube Preflight and Failure Archive

### Summary

Added preflight checks and failure archiving for YouTube videos to avoid wasted processing on inaccessible videos.

### What Changed

- Added `youtube-link-preflight` workflow.
- Added failure archive under `data/youtube-preflight-failures/`.
- Documented preflight command and workflow.

### User-Facing Impact

- Before processing any video, the system checks accessibility.
- Blocked videos are archived with reasons instead of failing silently.

---

## v0.3.20 — YouTube KB Import Pilot

### Summary

First real-world pilot of the YouTube video knowledge import workflow using the Dario Amodei Bloomberg interview.

### What Changed

- Added complete knowledge entry for Dario Amodei Bloomberg interview.
- Generated all 11 files: metadata, transcripts, analysis, notes, cards, report.
- Published to GitHub Pages.

### User-Facing Impact

- Demonstrated end-to-end video-to-knowledge workflow on a real video.
- Proved the workflow works for long-form interviews (24+ minutes).

---

## v0.3.19 — One-Click YouTube KB Import

### Summary

Built the one-click command capability for importing YouTube video knowledge packages into Hermes Knowledge Base.

### What Changed

- Added `youtube-kb-import` command documentation.
- Added workflow for importing existing video brief outputs.
- Connected `youtube-brief` output to KB entry creation.

### User-Facing Impact

- Users can now say "解读这个 YouTube 视频并加入 Hermes 知识库" as a single command.

---

## v0.3.18 — YouTube Video Brief KB Import

### Summary

First successful case of YouTube video brief and KB import, using Conan O'Brien's Harvard 2026 commencement speech.

### What Changed

- Generated complete video knowledge package from YouTube URL.
- Created KB entry with metadata, summary, notes, and source.
- Documented the workflow and command for reuse.

### User-Facing Impact

- Proved that a YouTube video can be converted into a structured Chinese knowledge package.
- Established the baseline for all subsequent YouTube capability development.

---

## Earlier Versions

See git tags for versions prior to v0.3.18:

- v0.3.0 to v0.3.17: Site infrastructure, browser, import workflows, quality gates.

---

*This changelog follows the principles at [docs/RELEASES.md](docs/RELEASES.md).*
