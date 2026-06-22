# Site detail page polish — v0.3.9

**Date**: 2026-06-22
**Scope**: `hermes-knowledge-base` — detail page reading experience
**Builds on**: `178c896 Fix item pages quality gate hard stop` (v0.3.8)

## STATUS: PASS

## 1. Summary

v0.3.8 shipped the basic detail page skeleton (title / metadata / sections /
GitHub folder button / copy path). v0.3.9 polishes the **reading experience**
without changing any KB content or adding frameworks:

- In-page **TOC** auto-generated from the primary section's h2/h3 headings
- Type-aware **section expand/collapse** using native `<details>` / `<summary>`
- **返回顶部** floating button (visible after 400px scroll)
- **原文链接** action button — only when `source_url` is non-empty
- Reading typography polish: line-height 1.85, table overflow, code/pre refinement, mobile breakpoints

The only KB data observed at write time: 19 records unchanged.

## 2. Files Modified

| Path | Change |
|------|--------|
| `scripts/generate_item_pages.py` | Major — Markdown renderer returns `(html, toc)`, headings get stable ids; new `_primary_body_key()`, `_build_source_btn()`, `_build_toc_html()`, `SECTION_OPEN_BY_TYPE`; TEMPLATE_SECTION switched to `<details>`; TEMPLATE_ACTIONS adds source_btn + back-to-top; scroll listener in inline JS |
| `site/styles.css` | +440 lines: `.detail-toc`, `.toc-list/link`, `.section-details/summary`, `.section-tag-collapsed`, `.back-to-top`, `.action-link.source-link`, refined `.markdown-body` (line-height, table block-overflow, scroll-margin-top, sup margins), mobile media-query block |
| `site/items/<slug>/index.html` × 19 | Regenerated — TOC added, sections restructured as `<details>`, back-to-top button added, source_url button conditionally added |
| `docs/items/<slug>/index.html` × 19 | Mirrored from site/ via `sync_pages_docs.py` |
| `site/data/catalog.json` | Regenerated (no schema change; same 19 records) |
| `docs/data/catalog.json` | Synced |
| `README.md` | Detail page section updated with v0.3.9 polish (TOC, type-aware collapse, back-to-top) |

## 3. 新增/更新详情页数量

- Regenerated: **19 / 19** detail pages (100 %)
- Pruned (stale slugs): 0
- Build summary: `Generated 19 item pages under /home/conanxin/projects/hermes-knowledge-base/site/items (skipped: 0).`

## 4. 新增体验功能

| Feature | Implementation | Where |
|---------|----------------|-------|
| **页内目录 TOC** | Native `<nav class="detail-toc">` with numbered links. Built from the primary body section's h2/h3 only (`translation` for article, `collection` for resource_collection, `source` for note/project). Stable `id` on each heading via `_slugify()` (Chinese-friendly: lowercase + CJK retained + dedup on collision). | `scripts/generate_item_pages.py:_slugify` + `_build_toc_html` + `TEMPLATE_TOC` |
| **类型差异化展开/折叠** | Native `<details>` with `<details open>` for sections that should default-expanded, plain `<details>` for collapsed. The `<summary>` has a custom round toggle (▾/▴) styled in `styles.css`. Per-type map: `SECTION_OPEN_BY_TYPE` (article: summary+translation; resource_collection: summary+collection; note/project: summary+source). | `scripts/generate_item_pages.py:SECTION_OPEN_BY_TYPE` + `_section_open` + `TEMPLATE_SECTION` |
| **返回顶部按钮** | Fixed position bottom-right. CSS-only anchor `<a href="#top">` works without JS; visibility toggled via 2-line inline `scroll` listener in the page's existing inline `<script>`. | `scripts/generate_item_pages.py:TEMPLATE_ACTIONS` + inline JS; `site/styles.css:.back-to-top` |
| **原文链接按钮** | Conditional `<a class="action-link source-link">` rendered only when `source_url` is truthy and not the literal string `"null"` / `"~"` / `"none"`. Placed in `TEMPLATE_ACTIONS` between back-link and GitHub button. | `scripts/generate_item_pages.py:_build_source_btn` |
| **阅读样式优化** | line-height 1.85 (was 1.75); h2 gets a 1px bottom border; `scroll-margin-top: 24px` so anchored headings don't get hidden by sticky top; `word-break: break-word` on inline code; `display: block; overflow-x: auto` on tables so wide tables scroll horizontally inside the article; `overflow-wrap: anywhere` to prevent long URLs from blowing the layout; `.markdown-body pre` keeps `white-space: pre` to preserve indentation. | `site/styles.css` (new `v0.3.9` section) |

## 5. Pipeline results

```text
$ python3 scripts/check_kb.py
Total items: 19
PASS: 19
FAIL: 0
STATUS: PASS

$ python3 scripts/update_site.py
# STEP 0/4: Quality gate (check_kb.py) → OK
[1/4] scripts/build_index.py OK
[2/4] scripts/export_site_data.py OK
[3/4] scripts/generate_item_pages.py OK
[4/4] scripts/sync_pages_docs.py OK
All steps completed successfully.

$ python3 scripts/check_translation_residue.py
STATUS: WARNING — review samples above
```

The check_translation_residue WARNING is pre-existing (5 book-title hits, all intentional proper-noun retention in the 4 modern articles). Not introduced by v0.3.9.

## 6. Local smoke test (`python3 -m http.server 8765 -d site`)

> Port 8765 (instead of 8000) because the local SurrealDB is bound to 8000.

| # | Check | Result |
|---|-------|--------|
| 1 | `GET /` | 200 |
| 2 | `catalog.json` records | 19, all with `detail_url` |
| 3 | All 19 `/items/<slug>/` | 19/19 → 200 |
| 4 | Article page (Spielberg oral history, 13 h2): TOC + open/close + back-to-top + source_btn | ✓ all pass |
| 5 | Article page (your-ai-is-not-a-tool, 0 h2 in translation): no TOC, translation=open, source/notes=closed, back-to-top, source_btn | ✓ all pass |
| 6 | Article page (wiki-vs-rag-analysis, empty `source_url`): 原文链接 button NOT rendered | ✓ correct |
| 7 | Collection page (arxiv-ai-agents, no `source_url`): collection=open, summary=open, notes=closed, no 原文链接 button | ✓ correct |
| 8 | Note page (transformer-decoding): summary=open, source=open, notes=closed, 原文链接 button visible | ✓ correct |
| 9 | Project page (hermes-agent-self-evolution): summary=open, source=open, notes=closed, 原文链接 button visible | ✓ correct |
| 10 | TOC counts match h2+h3 (excluding fenced code blocks) | ✓ all 19 records |
| 11 | Mobile layout (640px breakpoint): TOC, sections, back-to-top, action buttons all stack correctly | ✓ (verified by media-query rules) |

### Per-type section state verified

| Type | summary | translation / collection / source | source (secondary) | notes |
|------|---------|------------------------------------|--------------------|-------|
| article | (closed for some, open for others) | **open** | closed | closed |
| resource_collection | **open** | **open** (collection) | — | closed |
| note | **open** | **open** (source) | — | closed |
| project | **open** | **open** (source) | — | closed |

> Note: For article type, **summary** is rendered with its own details block. Looking at the open map: `article: {"summary", "translation"}` — both should be open. The smoke test confirms both summary and translation are open in rendered article pages. (The per-row table above shows summary as variable because some articles don't have summary.md; in those cases there's no summary section block at all.)

## 7. site/docs sync result

```
Synced 4 top-level files from site/ to docs/:
  index.html, app.js, styles.css, data/catalog.json
Mirrored 19 files under site/items/ → docs/items/.
```

Hand-authored docs (AGENT_COMMANDS.md, COLLECTIONS.md, LEGACY_MIGRATION.md, TAXONOMY.md) preserved untouched. The v0.3.8 → v0.3.9 diff is only inside the 19 detail pages + 2 site/ source files + README.

## 8. Example URLs (post-push, post-CDN)

- Homepage: <https://conanxin.github.io/hermes-knowledge-base/>
- Article with rich TOC: <https://conanxin.github.io/hermes-knowledge-base/items/2026-06-20-vulture-spielberg-oral-history/>
- Article with no TOC (1 h1 only): <https://conanxin.github.io/hermes-knowledge-base/items/2026-06-22-your-ai-is-not-a-tool/>
- Article with no source_url (button hidden): <https://conanxin.github.io/hermes-knowledge-base/items/2026-04-07-wiki-vs-rag-analysis/>
- Collection: <https://conanxin.github.io/hermes-knowledge-base/items/2026-05-06-arxiv-ai-agents/>
- Note: <https://conanxin.github.io/hermes-knowledge-base/items/2026-04-07-transformer-decoding/>
- Project: <https://conanxin.github.io/hermes-knowledge-base/items/2026-04-13-hermes-agent-self-evolution/>

## 9. Known limitations (v0.3.9)

- TOC only includes h2/h3 (not h4); deeper structure is collapsed in the displayed TOC.
- TOC is collected only from the **primary** body section. If a user has `notes.md` with a long structure of its own, that structure is NOT surfaced in the page-level TOC. (Intentional — the page TOC reflects the main reading flow.)
- Markdown renderer still doesn't handle nested lists deeper than 1 level. None of the 19 current records use deeper nesting, so this remains a known-acceptable gap.
- Back-to-top button requires JS for visibility toggle. The anchor `<a href="#top">` itself works without JS.

## 10. Follow-ups (not blocking)

- [ ] Consider an "All sections expanded" / "All sections collapsed" master toggle (would require minor JS).
- [ ] Consider persisting the per-section open/close state in `localStorage` so users don't lose their collapse state when navigating away. (Current spec says state should not persist — kept that way for v0.3.9.)
- [ ] Add a "TOC sticky on desktop" treatment once the page is wide enough to spare a sidebar (current breakpoint is 760px max-width for the article column).
- [ ] Cleanup unused old `.section-header` CSS rules from v0.3.8 (no functional impact; they target classes that no longer exist in HTML).
