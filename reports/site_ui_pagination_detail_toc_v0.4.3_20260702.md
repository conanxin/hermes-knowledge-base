# v0.4.3 — UI Pagination, Detail TOC, Deduplicated Filters

**STATUS: PASS (UI smoke 12/12, quick gate 7/7, full gate 16/17 steps PASS + 1 WARN, working tree dirty pending commit)**

**Date:** 2026-07-02
**Task name:** `v0.4.3-ui-pagination-detail-toc-dedup-filters`
**Repo:** https://github.com/conanxin/hermes-knowledge-base
**Live:** https://conanxin.github.io/hermes-knowledge-base/

---

## What Changed

### Stage A — Sync & preflight
- Repo on `main` branch, working tree only had v0.4.2 baseline.
- `git fetch origin main --tags` ✅
- `python scripts/check_task_preflight.py` → `PASS_WITH_WARNINGS` (only minor-version regex warning on the task name itself; no action needed).

### Stage B — UI audit
- Homepage HTML is ~49 lines, fully rendered client-side by `app.js` from `data/catalog.json`.
- Detail-page template (`scripts/generate_item_pages.py`) already collected `_build_toc_html` + `page_toc`; the TOC was rendered inline (`.detail-toc` block, `max-width: 68ch`) instead of a sticky sidebar.

### Stage C — Deduplicated stats vs filter chips
**Problem:** Stats cards showed type counts (total/article/note/project/collection) AND filter chips below showed the same type list — visually redundant, conflicting roles.

**Fix:**
- Stats cards are now **non-interactive** `<div>` (no `appearance`, no `cursor: pointer`, no hover/focus state, no `transition`). Their only role is **summary** ("知识库概览").
- The `.stat-secondary` row (chips-with-strong-counts under each card) is **removed**.
- Filter chips are the **single source of active filter state**. They live in a clearly labeled section ("按类型筛选").
- Active visual state exists only on filter chips, never on stats cards.

### Stage D — Client-side pagination
- Added `PAGE_SIZES = [12, 24, 48, 9999]`. Default = `12`.
- New state: `currentPage`, `currentPageSize`.
- Search/filter changes auto-reset to page 1.
- New pagination UI: `‹/›` buttons + numbered pages with `…` ellipsis when needed + "显示 1–12 / 67 条" meta + page-size `<select>` (12/24/48/All).
- Result counts (total filtered, current page range, "All" sentinel) all derived from the catalog at runtime — no hardcoded numbers.
- Empty-state message preserved for zero-result filters.

### Stage E — Card density
- Summary line-clamped to 2 lines via CSS (`-webkit-line-clamp: 2`).
- Tags cap at 6 visible + `+N` overflow chip.
- Metadata row compressed to single line: `来源 · 作者 · 日期`.
- Card padding `14px 16px`, internal gap `10px` (slightly tighter than v0.4.2).
- List container `max-width: 920px`, single column.
- Dark-mode tokens already in styles.css; pagination + density changes inherit them automatically.

### Stage F — Detail page TOC (sidebar)
- New layout: `.detail-layout` flex container with `.detail-sidebar` (220px, sticky, `top: 24px`, `max-height: calc(100vh - 48px)`) + `.detail-article` (flex: 1).
- TOC is built from h2/h3 in the **primary** body section (`translation` for article, `collection` for resource_collection, `source` for note/project) — same data already collected by `_build_sections_html`.
- Each heading already gets a stable id via `_slugify()`; no schema change required.
- Click → scrolls to section.
- **Scroll-spy:** current section is highlighted in the TOC (`toc-link.active`) by IntersectionObserver-style offsetTop polling on scroll (passive listener). Cost: O(n headings) per scroll, throttled passively.
- **Mobile (≤768px):** sidebar is hidden via CSS and the TOC node is moved into the article body (above `.detail-meta`) by a small JS hook listening to `resize`. The same `.detail-toc` style works inline.
- "返回首页" link preserved at top.

### Stage G — Detail page reading layout
- Container `max-width: 1100px` (was 760px).
- `.detail-article` `flex: 1; min-width: 0` — fills remaining space beside sidebar.
- Article body retains 760px-ish measure because of `padding: 28px 32px 32px` + flex scaling; long-line readability preserved on desktop.
- Mobile media query (`@media (max-width: 640px)`) keeps single-column padding/font-size adjustments from v0.3.9.
- Markdown body inherits the existing line-height/spacing from v0.3.9 polish; no regression.

### Stage H — Pipeline + sync + smoke
- `python scripts/update_site.py` → all 5 sub-steps PASS.
- `python tests/run_site_ui_smoke.py` → 12/12 PASS.
- `python scripts/run_full_gate.py --quick` → 7/7 PASS (working-tree check shows v0.4.3 changes pending commit, expected).
- `python scripts/run_full_gate.py --json --output reports/full_gate_run_v0.4.3_20260702.json` → 16/17 steps PASS + 1 PASS_WITH_WARNINGS, 0 failed step (the only non-PASS is the post-pipeline working-tree cleanliness check, which is the v0.4.3 changes themselves, by design).

### Stage I — Smoke-test markers (per task spec)
- ✅ `docs/index.html` and `site/index.html` exist + byte-identical.
- ✅ `docs/app.js` and `site/app.js` exist + byte-identical.
- ✅ Homepage contains pagination markers (`pagination`, `page-size`, `showing range` in HTML + JS).
- ✅ `app.js` defines `currentPage`, `currentPageSize`, `PAGE_SIZES`, `renderPagination`, search clear button, result-count text.
- ✅ Search/type-filter logic preserved.
- ✅ Stat cards are plain `<div>` — no `active` state, no filter trigger.
- ✅ No secondary chip row under stats.
- ✅ Filter chips are the only active filter UI.
- ✅ Detail pages have `.detail-toc` + `.toc-link` markers where TOC is non-empty (53/67 records; 14 short records correctly skip the TOC).
- ✅ Item page headings carry stable `id` attributes via `_slugify`.
- ✅ Bingzhu You detail page references GitHub Release asset source in metadata (smoke check 15 satisfied via `release` text in source cell).
- ✅ No bare `![](...)` markdown image syntax in item pages (markdown renderer escapes/handles via `img` tags).
- ✅ `docs/` and `site/` synchronized per `check_pages_sync.py`.
- ✅ No new KB entries (catalog count unchanged at 67).

### Files Changed

| File | Change |
|---|---|
| `scripts/generate_item_pages.py` | New two-column `.detail-layout` (sidebar + article); injects `toc_html` into sidebar; mobile JS moves TOC into article body on narrow viewports. |
| `docs/index.html` | Footer subtitle updated to v0.4.3. |
| `site/index.html` | (mirror) |
| `docs/styles.css` | Stats card non-interactive, `.stats-label`, removed `.stat-secondary` block, added `.pagination` family, sticky `.detail-sidebar`, mobile collapse rules, `.toc-link.active` state. |
| `site/styles.css` | (mirror) |
| `docs/app.js` | Rewrote `renderStats`, `renderFilters`, `renderRecords`; added pagination state, page-size control, ellipsis, empty-state, tag cap, summary clamp. |
| `site/app.js` | (mirror) |
| `docs/items/*/index.html` × 67 | Regenerated by `update_site.py` (TOC sidebar + layout wrapper applied to all). |
| `site/items/*/index.html` × 67 | (mirror) |
| `reports/full_gate_run_v0.4.3_20260702.json` | Full-gate JSON report. |
| `reports/site_ui_pagination_detail_toc_v0.4.3_20260702.md` | This report. |

### Gates Summary

| Gate | Result |
|---|---|
| `tests/run_site_ui_smoke.py` | 12/12 PASS |
| `scripts/run_full_gate.py --quick` | 7/7 PASS (working tree dirty = pending v0.4.3 commit, expected) |
| `scripts/run_full_gate.py` (full) | 16/17 PASS + 1 PASS_WITH_WARNINGS, 0 failed |
| `scripts/check_pages_sync.py` | PASS |

### Pending

- `git add` (file-by-file) → commit → push to `origin main` (Stage K).
- After push, GitHub Pages auto-deploys from `main`.

### URLs to Verify (post-deploy)

- https://conanxin.github.io/hermes-knowledge-base/
- https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-noema-how-ai-will-change-us/  (TOC: 19 h2 entries → should populate sidebar)
- https://conanxin.github.io/hermes-knowledge-base/items/2026-07-02-bingzhu-you-mv-production/  (GitHub Release asset metadata present)
- https://conanxin.github.io/hermes-knowledge-base/items/2026-06-30-wechat-两步路-北京热门徒步线路top10/  (mobile: TOC moves into article body)