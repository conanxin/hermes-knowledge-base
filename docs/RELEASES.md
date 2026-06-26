# Releases

## Release Overview

The versions from **v0.3.18 to v0.3.24** form a coherent capability line: taking YouTube videos and turning them into structured Chinese knowledge packages, making the workflow publicly discoverable and verifiable.

**v0.3.22** is an orthogonal fix for the music player detail page and does not belong to the YouTube capability line.

---

## Version Map

| Version | Tag | Commit | Theme | What Changed | User-Facing Impact |
|---------|-----|--------|-------|--------------|-------------------|
| v0.3.18 | `v0.3.18-youtube-video-brief-kb-import` | `87f5065` | First success | Conan O'Brien video brief → KB entry | Proved YouTube → Chinese knowledge package works |
| v0.3.19 | `v0.3.19-youtube-one-click-kb-import` | `fd24d5c` | Command | One-click import command | Single command to import video knowledge |
| v0.3.20 | `v0.3.20-youtube-kb-import-pilot` | `ae1458c` | Real pilot | Dario Amodei Bloomberg interview | First real-world long-form video import |
| v0.3.21 | `v0.3.21-youtube-preflight-failure-archive` | `1b73df5` | Preflight | Link preflight + failure archive | No wasted effort on inaccessible videos |
| v0.3.22 | `v0.3.22-music-player-js-loader-fix` | `82fd039` | Music fix | app.js loader fix on detail pages | Verified play buttons work again |
| v0.3.23 | `v0.3.23-youtube-capability-oss-exposure` | `bbb693c` | OSS exposure | YouTube capability docs for public | External users can discover capabilities |
| v0.3.24 | `v0.3.24-youtube-public-entry-qa` | `9d0df38` | Public QA | Verified navigation + fixed path leaks | Safe, clean docs for external readers |

---

## YouTube Capability Line

```
v0.3.18  →  v0.3.19  →  v0.3.20  →  v0.3.21  →  v0.3.23  →  v0.3.24
(first     (one-click   (real       (preflight  (OSS        (public
 success)   command)     pilot)      + archive)  exposure)   entry QA)
```

### What each step added

- **v0.3.18**: Proved a single video can be turned into a knowledge package.
- **v0.3.19**: Made the import repeatable via a single command.
- **v0.3.20**: Validated the workflow on a real, long interview.
- **v0.3.21**: Added safety checks before processing.
- **v0.3.23**: Documented everything for external users.
- **v0.3.24**: Verified the docs are clean, linked, and navigable.

---

## Related Music Fix

### v0.3.22 — Music Player JS Loader Fix

- **Problem**: Detail pages were not loading `app.js`, so verified play buttons did not respond.
- **Fix**: Corrected script loading order on item detail pages.
- **Impact**: Paste 1960s greatest songs listicle entries can now play embedded tracks.
- **Tag**: `v0.3.22-music-player-js-loader-fix`

---

## How to Pick a Version

| What you want | Start here |
|---------------|------------|
| Understand YouTube capabilities | `v0.3.23` / `v0.3.24` |
| See a real video import | `v0.3.20` (Dario Amodei) |
| Understand failure handling | `v0.3.21` |
| Fix music player buttons | `v0.3.22` |
| See the first proof of concept | `v0.3.18` (Conan O'Brien) |

---

## Files

- [CHANGELOG.md](../CHANGELOG.md) — Full changelog with per-version details
- [docs/YOUTUBE_CAPABILITIES.md](YOUTUBE_CAPABILITIES.md) — YouTube capability documentation
- [docs/releases/](releases/) — Per-version release notes

---

## Current Policy

- **每个版本任务使用唯一 tag**。
- **新任务应使用新的 v0.3.N，不要复用已使用过的 minor number**。
- **annotated tag 优先**。
- **不移动旧 tag**。
- **不 force push tag**。
- **从 v0.3.37 开始，避免复用 minor number**。

---

## v0.3.x Release Line (Full)

| Version | Tag | Commit | Type | Status | Notes |
|---|---|---|---|---|---|
| v0.3.0 | `v0.3.0-static-kb-browser` | `5547205` | annotated | ✅ | 静态 KB 浏览器基础 |
| v0.3.1 | `v0.3.1-browser-polish` | `762fd38` | annotated | ✅ | 浏览器 polish |
| v0.3.2 | `v0.3.2-browser-smoke-tested` | `dc4cc20` | annotated | ✅ | 浏览器冒烟测试 |
| v0.3.3 | `v0.3.3-github-pages-publish` | `08ac3aa` | annotated | ✅ | GitHub Pages 发布 |
| v0.3.4 | `v0.3.4-pages-online-smoke-tested` | `45c85ea` | annotated | ✅ | 线上冒烟测试 |
| v0.3.5 | `v0.3.5-pages-sync-script` | `a508e4a` | annotated | ✅ | 同步脚本 |
| v0.3.6 | `v0.3.6-import-refreshes-site` | `ddfe8c2` | annotated | ✅ | 导入刷新站点 |
| v0.3.7 | `v0.3.7-quality-gate-hard-stop` | `fb32690` | commit | ✅ | 质量门硬停 |
| v0.3.8 | `v0.3.8-static-item-detail-pages` | `178c896` | annotated | ✅ | 静态详情页 |
| v0.3.9 | `v0.3.9-detail-page-polish` | `98e1170` | annotated | ✅ | 详情页 polish |
| v0.3.13 | `v0.3.13-cloud-hermes-integration` | `5ad0a4c` | annotated | ✅ | Cloud Hermes 集成 |
| v0.3.14 | `v0.3.14-cloud-hermes-e2e-import` | `a05ee25` | annotated | ✅ | E2E 导入验证 |
| v0.3.15 | `v0.3.15-deterministic-site-export` | `4c25078` | annotated | ✅ | 确定性导出 |
| v0.3.16 | `v0.3.16-cloud-short-command-repeatable` | `039d25b` | annotated | ✅ | 短命令可重复 |
| v0.3.17 | `v0.3.17-routing-hardening` | `a9a32c5` | annotated | ✅ | 路由加固 |
| v0.3.18 | `v0.3.18-listicle-import-rules` | `e95cf7e` | annotated | ✅ | 长名单导入规则 |
| v0.3.18 | `v0.3.18-youtube-video-brief-kb-import` | `87f5065` | annotated | ✅ | YouTube 视频简报导入 |
| v0.3.19 | `v0.3.19-music-track-links` | `787b4b8` | annotated | ✅ | 音乐 track-card 架构 |
| v0.3.19 | `v0.3.19-youtube-one-click-kb-import` | `fd24d5c` | annotated | ✅ | YouTube 一键导入 |
| v0.3.20 | `v0.3.20-music-embed-enrichment-pilot` | `ee973a1` | annotated | ✅ | 音乐 embed 增强 pilot |
| v0.3.20 | `v0.3.20-youtube-kb-import-pilot` | `ae1458c` | annotated | ✅ | YouTube KB 导入 pilot |
| v0.3.21 | `v0.3.21-music-embed-enrichment-batch-2` | `462811b` | annotated | ✅ | 音乐 embed batch 2 |
| v0.3.21 | `v0.3.21-youtube-preflight-failure-archive` | `1b73df5` | annotated | ✅ | YouTube 预检失败归档 |
| v0.3.22 | `v0.3.22-music-player-js-loader-fix` | `82fd039` | annotated | ✅ | 音乐播放器 JS 修复 |
| v0.3.23 | `v0.3.23-music-embed-enrichment-batch-3` | `09f485c` | annotated | ✅ | 音乐 embed batch 3 |
| v0.3.23 | `v0.3.23-youtube-capability-oss-exposure` | `bbb693c` | annotated | ✅ | YouTube 能力 OSS 暴露 |
| v0.3.24 | `v0.3.24-music-embed-enrichment-batch-4` | `0357505` | annotated | ✅ | 音乐 embed batch 4 |
| v0.3.24 | `v0.3.24-youtube-public-entry-qa` | `9d0df38` | annotated | ✅ | YouTube 公共入口 QA |
| v0.3.25 | `v0.3.25-music-embed-enrichment-batch-5` | `74bc42c` | annotated | ✅ | 音乐 embed batch 5 |
| v0.3.25 | `v0.3.25-release-changelog` | `4ca71b9` | annotated | ✅ | 发布日志 |
| v0.3.26 | `v0.3.26-music-embed-enrichment-batch-6` | `b3e0e9c` | annotated | ✅ | 音乐 embed batch 6 |
| v0.3.26 | `v0.3.26-palantir-translation-render-fix` | `8c59e3c` | annotated | ✅ | Palantir 翻译渲染修复 |
| v0.3.27 | `v0.3.27-music-embed-enrichment-batch-7` | `b9442c1` | annotated | ✅ | 音乐 embed batch 7 |
| v0.3.28 | `v0.3.28-playable-track-filter` | `b9b829a` | annotated | ✅ | 可播放筛选器 |
| v0.3.29 | `v0.3.29-music-coverage-summary` | `4a759a0` | annotated | ✅ | 音乐覆盖摘要 |
| v0.3.30 | `v0.3.30-remaining-track-audit` | `e2faf42` | annotated | ✅ | 剩余曲目审计 |
| v0.3.31 | `v0.3.31-candidate-music-embed-enrichment` | `586f2ea` | annotated | ✅ | 候选 embed 增强 |
| v0.3.32 | `v0.3.32-final-candidate-sweep-and-coverage-sync` | `d393433` | annotated | ✅ | 最终候选清理 |
| v0.3.33 | `v0.3.33-spotify-apple-link-rendering-pilot` | `e3d1ec6` | annotated | ✅ | Spotify/Apple 外链 pilot |
| v0.3.33 | `v0.3.33-paste-greatest-songs-streaming-links` | `e3d1ec6` | annotated | ✅ | Paste 流媒体链接 |
| v0.3.34 | `v0.3.34-spotify-apple-link-batch` | `01bb6fc` | annotated | ✅ | Spotify/Apple 外链 batch |
| v0.3.34 | `v0.3.34-stash-audit-repo-hygiene` | `08ee506` | annotated | ✅ | stash 审计 |
| v0.3.35 | `v0.3.35-music-enrichment-final-summary` | `d8c0850` | annotated | ✅ | 音乐增强最终总结 |
| v0.3.35 | `v0.3.35-obsolete-stash-cleanup` | `19db21a` | annotated | ✅ | 过时 stash 清理 |
| v0.3.36 | `v0.3.36-repo-health-final-verification` | `8b4f128` | annotated | ✅ | 仓库健康验证 |
| v0.3.36 | `v0.3.36-repo-hygiene-and-report-cleanup` | `942cab3` | annotated | ✅ | 仓库卫生清理 |
| v0.3.37 | `v0.3.37-release-index-and-tag-hygiene` | `TBD` | annotated | 🔄 | **本版本** — release index + tag 卫生 |

### Known Duplicate Minor-Version Exceptions

| Minor | Tags | Reason | Status |
|---|---|---|---|
| v0.3.18 | listicle-import-rules, youtube-video-brief-kb-import | 历史并行开发 (music + youtube 双轨) | ✅ 已知，不修复 |
| v0.3.19 | music-track-links, youtube-one-click-kb-import | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.20 | music-embed-enrichment-pilot, youtube-kb-import-pilot | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.21 | music-embed-enrichment-batch-2, youtube-preflight-failure-archive | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.23 | music-embed-enrichment-batch-3, youtube-capability-oss-exposure | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.24 | music-embed-enrichment-batch-4, youtube-public-entry-qa | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.25 | music-embed-enrichment-batch-5, release-changelog | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.26 | music-embed-enrichment-batch-6, palantir-translation-render-fix | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.33 | spotify-apple-link-rendering-pilot, paste-greatest-songs-streaming-links | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.34 | spotify-apple-link-batch, stash-audit-repo-hygiene | 历史并行开发 | ✅ 已知，不修复 |
| v0.3.35 | music-enrichment-final-summary, obsolete-stash-cleanup | 历史并行开发 | ✅ 已知，不修复 |
| **v0.3.36** | **repo-health-final-verification, repo-hygiene-and-report-cleanup** | **本版本明确标记的 known exception** | ⚠️ **特别标注，从 v0.3.37 起避免** |

---

## Recommended Next Version

**v0.3.38** (或更高)

> 从 v0.3.37 开始，每个 minor version 只对应一个 tag。v0.3.37 已用于 release index，因此下一个可用版本是 v0.3.38。

---

## Related Files

- [CHANGELOG.md](../CHANGELOG.md) — Full changelog with per-version details
- [docs/VERSIONING.md](VERSIONING.md) — Versioning guide and tag rules
- [scripts/check_release_tags.py](../scripts/check_release_tags.py) — Automated tag hygiene check
- [docs/YOUTUBE_CAPABILITIES.md](YOUTUBE_CAPABILITIES.md) — YouTube capability documentation
- [docs/releases/](releases/) — Per-version release notes

---

*Last updated: 2026-06-27*
