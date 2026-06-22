# Site Item Detail Pages — v0.3.8

**Date**: 2026-06-22
**Scope**: `hermes-knowledge-base` GitHub Pages site
**Version**: v0.3.8

## Goal

When a user clicks an article card on
<https://conanxin.github.io/hermes-knowledge-base/>, the link used to go
to the GitHub folder view
(`https://github.com/conanxin/.../tree/main/content/articles/...`) which
shows raw `.md` / `.yaml` files. This change adds in-site detail pages
under `items/<slug>/` so users see the actual rendered content.

## Files Created

| Path | Purpose |
|------|---------|
| `scripts/generate_item_pages.py` | Build `site/items/<slug>/index.html` from catalog + content (zero external deps; stdlib-only Markdown renderer) |
| `site/items/<slug>/index.html` | One static detail page per record (19 pages) |
| `docs/items/<slug>/index.html` | Mirror of above, deployed to GitHub Pages |

## Files Modified

| Path | Change |
|------|--------|
| `scripts/export_site_data.py` | Add per-record `slug`, `detail_url`, `github_url` |
| `scripts/sync_pages_docs.py` | New `MIRROR_DIRS` mode syncs `site/items/` → `docs/items/` without touching any other doc files |
| `scripts/update_site.py` | Insert `generate_item_pages.py` between export and sync |
| `site/app.js` | Card title links to in-site `detail_url`; added "阅读 →" and "GitHub 文件夹" buttons; added `escapeHtml` / `escapeAttr` for safety; dynamic footer count |
| `site/styles.css` | New detail-page styles (article container, metadata grid, markdown body, back link, reading width, mobile breakpoints) |
| `site/index.html` | Footer record count updated 17 → 19 (also dynamically refreshed by JS) |
| `site/data/catalog.json` | Regenerated; now includes `slug`, `detail_url`, `github_url` per record |
| `docs/index.html` / `docs/app.js` / `docs/styles.css` / `docs/data/catalog.json` | Synced from `site/` |
| `README.md` | New "站内详情页（v0.3.8+）" section + record count + script chain update |

## Pipeline order (post-change)

```
scripts/build_index.py
scripts/export_site_data.py
scripts/generate_item_pages.py
scripts/sync_pages_docs.py
```

## Validation

| Check | Result |
|-------|--------|
| `python3 scripts/check_kb.py` | PASS 18/19 (1 pre-existing FAIL on 2026-03-25 article `word_count` legacy string form, not from this change) |
| `python3 scripts/update_site.py` | All 4 steps green: 19 records, 19 detail pages, 19 mirrors |
| `python3 scripts/check_translation_residue.py` | WARNING (pre-existing, not from this change) |

## Local smoke test (port 8765 — 8000 occupied by SurrealDB on this host)

| # | Check | Result |
|---|-------|--------|
| 1 | GET `/` → 200 | OK |
| 2 | `catalog.json` has 19 records, all with `detail_url` | OK |
| 3 | Article detail page returns 200, contains "中文翻译" + "原文 / 源文本" + 返回首页 + GitHub 文件夹 + 复制 path | OK |
| 4 | Collection detail page returns 200, contains "资源集合" + "摘要" | OK |
| 5 | `GitHub 文件夹` button on detail page points to `github.com/conanxin/.../tree/main/content/...` | OK |
| 6 | All 19 `items/<slug>/` URLs serve 200 | OK (19/19) |
| 7 | Detail page references stylesheet at `../../styles.css` | OK |
| 8 | `docs/` files preserved (AGENT_COMMANDS.md, COLLECTIONS.md, LEGACY_MIGRATION.md, TAXONOMY.md) | OK |

## Type-specific body loading

| Type | Files rendered |
|------|---------------|
| `article` | `translation.zh-CN.md` → `source.md` |
| `resource_collection` | `collection.md` → `summary.md` |
| `note` | `source.md` → `summary.md` |
| `project` | `source.md` → `summary.md` |
| (all) | `notes.md` if present |

Missing files render "暂无该部分" — no crashes.

## Design decisions

1. **No external dependencies.** The Markdown renderer uses `re` + `html.escape` only. Covers headings, lists, tables, code, blockquotes, links, footnotes, hr.
2. **No new build tools.** Pages are static HTML + the same `styles.css` already used by the homepage.
3. **Sync safety.** `docs/items/` is the only subtree `sync_pages_docs.py` may prune; hand-authored files like `docs/AGENT_COMMANDS.md` are explicitly protected by a file-list sync model — the script cannot `rmtree` `docs/`.
4. **Slug from path tail.** `content/legacy-knowledge/2026-04-07-transformer-decoding` → slug `2026-04-07-transformer-decoding`. Stable, deterministic, no collisions today.
5. **HTML safety.** Card rendering now uses `escapeHtml` / `escapeAttr` so future record fields with `<`, `>`, `&`, quotes, or backticks cannot break the page.
6. **Footer count dynamic.** `app.js#renderStats` updates `footer p` text on every load, so the static `19 records` in `index.html` is only initial-render fallback.

## URLs

- Homepage: <https://conanxin.github.io/hermes-knowledge-base/>
- Article example: <https://conanxin.github.io/hermes-knowledge-base/items/2026-06-22-your-ai-is-not-a-tool/>
- Collection example: <https://conanxin.github.io/hermes-knowledge-base/items/2026-05-06-arxiv-ai-agents/>
- Note example: <https://conanxin.github.io/hermes-knowledge-base/items/2026-04-07-transformer-decoding/>

## Known limitations

- Markdown renderer does not handle nested lists (1 level deep is fine, multi-level not). The 19 current records have at most 1 level of nesting, so this is a known-acceptable gap.
- Markdown renderer does not handle pipe characters inside table cells (real Markdown limitation; none of the 19 records use this).
- No image embedding yet (records don't reference images in body files).
- No TOC / anchor links. Footnote text bodies are rendered as `<sup>[n]</sup>` and the corresponding `[n]: ...` definitions appear as plain paragraphs at the bottom.

## Follow-ups (not blocking)

- [ ] Add a real TOC sidebar once record count exceeds ~30.
- [ ] Add sitemap.xml and RSS feed under `docs/`.
- [ ] Add per-record search highlight on detail page (read query from URL).
- [ ] Fix the pre-existing `2026-03-25-reverse-game-theory-housing-shortage` `word_count` legacy string form (separate cleanup).
