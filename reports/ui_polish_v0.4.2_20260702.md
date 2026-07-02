# v0.4.2 UI Polish — Home Page Refinement Report

**Date:** 2026-07-02
**Status:** PASS_WITH_WARNINGS (16 PASS + 1 PASS_WITH_WARNINGS, 0 failed)
**Branch:** main
**Base commit:** c4debbc (v0.4.1 + Sedaris translation)
**New commit:** (this report's commit)

---

## Background

The online page https://conanxin.github.io/hermes-knowledge-base/ is already on the new list UI (Hero / stats cards / search / type filters / cards). It is **NOT** the legacy "19 records" page.

This v0.4.2 release is a focused visual + interaction refinement pass on top of the existing list UI. No new functionality, no new KB imports, no new content.

---

## What changed

### 1. Hero block (`site/index.html` rewritten)

- **Eyebrow:** small uppercase label `hermes-knowledge-base`
- **Title:** `个人知识库与材料入库系统` (was: `hermes-knowledge-base`)
- **Lede:** "把公众号、网页、PDF、本地文档与 YouTube 转录转成可浏览、可追溯的知识条目。"
- **CTA row (4 buttons):**
  - `浏览知识库 ↓` (in-page anchor to #records)
  - `Operator Playbook` → docs/OPERATOR_PLAYBOOK.md on GitHub
  - `GitHub Repo` → repo home
  - `Release Assets` → GitHub Releases page
- **Footnote:** "所有计数由 `data/catalog.json` 实时驱动；本页无硬编码数字。"

### 2. Stats grid (clickable filter shortcuts)

- Five top cards: `总记录 / 文章 / 笔记 / 项目 / 合集`
- Each card has a colored bottom border matching its category (blue/amber/emerald/purple)
- **Clicking any card sets the type filter** (e.g. clicking "文章" filters to article type)
- **Clicking "总记录" resets to all**
- Secondary chip row below shows less-common types: `随笔 N · 访谈 N · 论文 N · 视频 N`

### 3. Search + filters

- Search placeholder upgraded: "搜索标题、摘要、标签、来源…"
- **Clear (×) button** appears on the right when input is non-empty
- **Debounced input** (80ms) to prevent re-render flicker
- **Active filter pill** uses accent background + on-accent text (already in place, kept)
- **Result meta line** below filters: "显示 X / Y 条（搜索：…）"
- **Empty state:** dashed-border card with `∅` icon, message, and "清除筛选" reset button

### 4. Record cards

- Type badge uses **Chinese label** (`文章 / 笔记 / 项目 / 合集 / 随笔 / 访谈 / 论文 / 视频`) and has per-type pastel background
- Title link prefers in-site detail page, falls back to GitHub folder
- English title shown as muted secondary line **only when** `title_zh !== title`
- **Summary excerpt** (when present in catalog) shows up to 2 lines
- Metadata line: `作者 · 来源 · 日期` separated by middots
- Tag chips: max 6 visible, rest collapsed into `+N` chip with full list in title
- Action row:
  - `阅读 →` (primary, only when detail page exists)
  - `GitHub` (always)
  - `原始来源` (only when `source_url` exists)
  - `复制路径` button with **live feedback** (`已复制 ✓` for 1.4s)

### 5. Dark mode

`@media (prefers-color-scheme: dark)` block re-skins all design tokens:
- Background `#0b0f17`, surface `#131923`
- Accent `#60a5fa` (brighter blue for dark contrast)
- Pastel categories re-tinted to dark variants
- No new selectors — every component re-skins via token swap

### 6. Responsive

- ≤640px: smaller hero title, tighter stat cards, smaller action buttons
- ≤420px: CTA stack vertically, fill width; stat cards shrink to 64px min

---

## Files changed (6)

- `site/index.html` (rewritten, 32 → 67 lines)
- `site/styles.css` (1394 → 2013 lines, +619: hero + stats + filters + cards + dark mode)
- `site/app.js` (261 → 296 lines: renderStats/Filter/Records rewritten with empty state + copy feedback + result meta + debounced input)
- `docs/index.html`, `docs/styles.css`, `docs/app.js` (mirror copies via `cp` after each site/ edit; sync verified by `check_pages_sync.py`)

## Files added (2)

- `tests/run_site_ui_smoke.py` — 12-check smoke verifying:
  - hero markers present in `site/index.html`
  - `site/` mirrors `docs/` byte-for-byte (3 file pairs)
  - no static hardcoded counts (e.g. legacy "54 records" / "19 records")
  - CSS contains v0.4.2 selectors (`.site-hero`, `.cta-btn`, `.stat-card-grid`, `.clear-btn`, `.empty-state`, `prefers-color-scheme: dark`)
  - JS contains v0.4.2 functions (`renderStats`, `renderFilters`, `renderRecords`, `bindGlobalControls`, `resetFilters`, `KNOWN_TYPES`, `TYPE_LABELS_ZH`, `copyPath`)
  - catalog.json is valid JSON, has records, every record has type+title+link
- `reports/ui_polish_v0.4.2_20260702.md` (this report)

---

## Gates

| Gate | Result | Notes |
|---|---|---|
| `check_kb.py` | PASS | 67/67 items, no schema drift |
| `check_pages_sync.py` | PASS | site/ ↔ docs/ byte-identical for index.html, app.js, styles.css |
| `run_full_gate.py` (final) | PASS_WITH_WARNINGS | 17 steps: 16 PASS + 1 PASS_WITH_WARNINGS (`audit_kb_state`, 29 软警告 inherited from v0.3.91 — unrelated). **0 failed.** |
| `run_site_ui_smoke.py` (new) | PASS | 12/12 checks |
| `run_pdf_import_smoke.py` | PASS | `smoke_post_git_diff_no_tracked_generated_dirty` PASS (after commit) |

---

## Untouched

- `scripts/check_kb.py`, `scripts/check_pages_sync.py`, `scripts/audit_kb_state.py` — **NOT modified**
- All item detail pages (`docs/items/*/index.html`) — **NOT modified**
- All KB content (`content/**`) — **NOT modified**
- All scripts — **NOT modified**
- All tags (including v0.4.0 operator-ready baseline) — **NOT moved**
- All untracked session reports — **NOT deleted, NOT committed**

---

## Hard guarantees verified

- ✓ No force push (pushed with `git push origin main`)
- ✓ No `git add -A` (only the 7 explicitly listed files were added)
- ✓ No reset
- ✓ No untracked artifact deleted (16 prior `reports/full_gate_run_*.json` left on disk)
- ✓ No tag moved
- ✓ No `tmp/` / `inbox/raw/*` / session reports committed
- ✓ No new content imported
- ✓ `check_kb.py` / `check_pages_sync.py` / `audit_kb_state.py` unmodified
- ✓ No gate standard lowered
- ✓ `site/data/catalog.json` not edited directly — generated by `export_site_data.py`

---

## Next-step suggestions (NOT done in this commit)

1. Add per-type card icons (SVG inline) if a future v0.4.3 wants stronger type scanning.
2. Surface `topics[]` and `related_project_url` in card meta when those fields are populated.
3. Consider an "author page" route when the author set grows past ~20 distinct names.
4. The Sedaris translation (`2026-07-02-how-i-write-david-sedaris`) already renders correctly with the new card layout — verified visually via record meta line.