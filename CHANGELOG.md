# Changelog

All notable changes to the Hermes Knowledge Base project.

## v0.3.86 — PDF / Local Document KB Import Route

### Summary

本地 PDF（可提取文本层）接入统一材料入口，由 `scripts/pdf_to_kb.py` 用 PyMuPDF 本地提取。扫描版 PDF 不再被静默当作"文本路径"处理，而是返回 `BLOCKED_NEEDS_OCR` 并硬停，不写半成品 KB 条目。

### Added

- `scripts/pdf_to_kb.py`（869 行）— PDF text-layer 路线，支持 dry-run / import / `--allow-partial-text`。
- `tests/run_pdf_import_smoke.py`（291 行）— 26/26 checks PASS，覆盖 fixture / dedup / scanned / router。
- `tests/fixtures/generate_sample_pdf.py` + `tests/fixtures/pdf_sample_document.pdf` + `tests/fixtures/pdf_scanned_fixture.pdf`。
- `docs/commands/pdf-kb-import-command.md` + `docs/workflows/pdf-kb-import-workflow.md` — 完整命令与工作流文档。
- `tests/run_material_router_smoke.py` 增加 PDF 路由端到端断言。

### Changed

- `scripts/material_to_kb.py` — `.pdf` 路由从 `BLOCKED_UNSUPPORTED` 改为 `pdf_file` → `pdf_to_kb.py`。
- `docs/commands/material-kb-import-command.md` — 增加 v0.3.86 PDF 路线段落。
- `docs/AGENT_COMMANDS.md` — 顶部状态表更新 PDF 行；`README.md` 增加 PDF 文本层路线行。
- `scripts/pdf_to_kb.py` — 在 5 个 `[pdf] status: ...` 行后追加大写 `STATUS:` 行，方便统一入口 `parse_status_line` 解析。

### Hard Guarantees

- **不下载 PDF**：必须用户已下载到本地。
- **不读 cookie / 登录态 / 网络凭据**：纯本地 PyMuPDF 调用。
- **不内置 OCR**：扫描版（`total_chars == 0` 或空页比例 ≥0.6 且 `total_chars < page_count×10`）返回 `BLOCKED_NEEDS_OCR`，不写半成品。
- **不伪造文本**：`--allow-partial-text` 仅放宽硬阈值，仍是基于真实提取的文本。
- **去重三键**：pdf_sha256 + (title, author, page_count) + content_hash（嵌入 `raw_payload.json`）。
- **统一状态行**：5 个退出路径都打印 `STATUS: {STATE}` 大写行，与 youtube / web / wechat 子脚本一致。

### Status Constants

`DRY_RUN_OK` / `IMPORTED` / `SKIPPED_DUPLICATE` / `BLOCKED_NEEDS_OCR` / `BLOCKED_INCOMPLETE_TEXT` / `BLOCKED_UNSUPPORTED` / `FAILED_IMPORT` / `FAILED_GATE`。

### Commits

- (final hash written by Stage L)

### Related

- 扫描版 PDF 暂未接 OCR（`docs/commands/pdf-ocr-kb-import-command.md` 是占位文档）。
- v0.3.85 YouTube real handoff e2e 报告（`reports/youtube_real_handoff_e2e_regression_v0.3.85_20260701.md`）记录环境拿不到 full transcript 的状况，本版不动 YouTube。

---

## v0.3.85 — YouTube Real Handoff E2E Regression

### Summary

YouTube 11 个候选 URL（Steve Jobs / Ken Robinson / Tim Urban / Rick Astley 等）全失败：9 个 region-locked + 6 个 empty captions / 429，0 个 `full` transcript → 0 imports。

### Status

`BLOCKED_NO_FULL_TRANSCRIPT_AVAILABLE`。Handoff 链路本身已由 `smoke_6_router_handoff_passes_fetch_result` 覆盖。

### Files Changed

- 仅 `reports/youtube_real_handoff_e2e_regression_v0.3.85_20260701.md` + `CHANGELOG.md`。
- 无 KB / docs / site / source 改动。

### Commit / Push

- `d1f2351` pushed.

---

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
