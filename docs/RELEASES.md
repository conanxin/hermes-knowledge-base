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

*Last updated: 2026-06-26*
