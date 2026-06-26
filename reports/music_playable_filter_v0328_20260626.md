# Playable Track Filter — v0.3.28

**STATUS: PASS**

## Overview

This batch adds an in-page **playable track filter** to the Paste 1960s music
long-list article (`content/articles/2026-06-26-paste-greatest-songs-1960s/`).
It does NOT add new verified embeds, NOT modify source/translation/summary
content, NOT change tracks.yaml, and NOT touch any unrelated detail page.

The motivation is to make the playable-vs-pending split discoverable without
scanning all 50 track-cards. Before this change, the page silently mixed 33
playable YouTube embeds with 17 search links and the user had no way to
quickly filter to one set. The filter solves this with a top-of-section
summary + three filter buttons.

## What Was Added

### Page-side (CSS + HTML + JS)

- **Summary bar** above the first track-card showing:
  - 总曲目: 50
  - 可播放: 33
  - 待验证: 17
  - 可播放比例: 66%
- **Three filter buttons** with count badges:
  - 全部曲目 (50)
  - 仅可播放 (33)
  - 仅待验证 (17)
- **Status classes** on every `.track-card`:
  - `.is-playable` + `data-track-status="verified"`
  - `.needs-verification` + `data-track-status="needs_verification"`
- **Hide via** `.is-hidden { display: none; }` so cards can be re-shown
  without re-rendering.

### Generator-side (Python)

- `generate_item_pages.py`:
  - New `_build_track_filter_bar(tracks)` helper returns the filter bar
    HTML with embedded counts; returns empty string when no tracks.
  - `_build_track_cards()` now emits `data-track-status` + the
    matching status class on each card.
  - The `track_filter_bar` is inserted between the metadata grid and
    the first body section so it sits at the top of the music content.
  - No source.md / translation.zh-CN.md / summary.md / notes.md / tracks.yaml
    modifications.

### Client-side (app.js)

- New `initTrackFilter()` function:
  - **Safety no-op** when `#track-filter-bar` is absent (the function
    returns early without binding any listeners).
  - Scoped to the closest `.detail-article` so cross-section track
    cards are not affected.
  - Click handler toggles `is-hidden` on cards based on
    `data-track-status`.
  - Updates button `.active` and `aria-pressed` state on click.
  - Coexists with `initTrackPlayers()` — the lazy-load iframe handler
    is still attached to every `.track-play-button` regardless of
    current filter state, and works whether the card is visible or
    later shown again.
- DOMContentLoaded handler now invokes both `initTrackPlayers()` and
  `initTrackFilter()`.

### CSS additions

- `.track-filter-bar` — flexbox container with summary + buttons, surfaces
  to the design tokens (`--color-surface`, `--color-border`,
  `--radius-button`).
- `.track-filter-summary` + `.track-filter-playable-pct` — text layout
  for the counts.
- `.track-filter-buttons` + `.track-filter-button` + `.track-filter-button.active` —
  button styles respecting the design system (uses accent token for active).
- `.track-card.is-playable` — subtle border-left accent (verified green).
- `.track-card.needs-verification` — slight opacity dim to visually
  de-emphasize.
- `.track-card.is-hidden` — `display: none` to fully hide filtered-out
  cards (preserves their DOM so toggling back re-shows them instantly).
- Mobile breakpoint (`@media (max-width: 480px)`) — stack bar vertically
  on narrow screens.

## Statistics

| Metric | v0.3.27 → v0.3.28 |
|---|---|
| Total tracks | 50 (unchanged) |
| Verified | 33 (unchanged) |
| Needs verification | 17 (unchanged) |
| Play buttons | 33 (unchanged) |
| Search links | 17 (unchanged) |
| Playable % | 66% (new) |
| New verified embeds added | **0** (filter is UI-only) |
| Detail pages with filter bar | **1** (only Paste 1960s) |
| Detail pages without filter bar (no-op) | 37 (all other items) |

## Smoke Test Results

### Local (http://127.0.0.1:8765)

- HTTP 200 on Paste page ✅
- 50 track-cards ✅
- 33 play buttons ✅
- 17 search links ✅
- 1 filter bar with 3 buttons ✅
- 33 cards carry `data-track-status="verified"` ✅
- 17 cards carry `data-track-status="needs_verification"` ✅
- All other 37 detail pages: `track-filter-bar` count = 0 (no-op) ✅
- Homepage: `track-filter-bar` count = 0 (no-op) ✅
- styles/ + app.js + index.html byte-identical between `site/` and `docs/`

#### Puppeteer E2E (9/9 PASS)

| Step | Result |
|---|---|
| Initial load | 50 visible / 0 hidden / active="all" ✅ |
| Click "仅可播放" | 17 hidden / 33 verified visible / active="playable" ✅ |
| Click "仅待验证" | 33 hidden / 17 pending visible / active="pending" ✅ |
| Click "全部曲目" | 0 hidden / active="all" ✅ |
| Click "仅可播放" then click play on #75 (Led Zeppelin) | iframe src = `https://www.youtube.com/embed/WnMiXsRtsfc` ✅ |
| Click "仅待验证" then check #75 | hidden=true ✅ |
| Navigate to jasmi non-music page | `hasFilterBar=false / trackCardCount=0` ✅ |
| 0 page errors aside from favicon 404 | ✅ |

### Online (https://conanxin.github.io)

- HTTP 200 on Paste page ✅
- 50 track-cards / 33 play / 17 search ✅
- 1 filter bar with 3 buttons ✅
- 33 + 17 cards with `data-track-status` ✅

#### Puppeteer E2E (8/8 PASS)

| Step | Result |
|---|---|
| Initial load | 50 visible / 0 hidden / active="all" ✅ |
| Click "仅可播放" | 17 hidden / 33 verified visible / active="playable" ✅ |
| Click "仅待验证" | 33 hidden / 17 pending visible / active="pending" ✅ |
| Click "全部曲目" | 0 hidden / active="all" ✅ |
| Click "仅可播放" then click play on #75 | iframe src = `https://www.youtube.com/embed/WnMiXsRtsfc` ✅ |
| Navigate to jasmi non-music page | `hasFilterBar=false / trackCardCount=0` ✅ |
| 0 page errors aside from favicon 404 | ✅ |

## Check Scripts

| Script | Result |
|---|---|
| `check_kb.py` | PASS (38/38) |
| `check_tracks.py` | PASS (33 verified, 50 total) |
| `update_site.py` | PASS (5/5 steps) |
| `check_pages_sync.py` | PASS (site/ ↔ docs/ byte-identical) |
| `check_translation_residue.py` | WARNING (jasmi article 1 email, **unrelated**) |

## Files Modified

- `scripts/generate_item_pages.py` — added `_build_track_filter_bar`,
  added `data-track-status` + status class to `_build_track_cards`,
  inserted filter bar between metadata grid and body sections.
- `site/styles.css` + `docs/styles.css` — added `.track-filter-bar`,
  `.track-filter-button`, `.track-filter-button.active`,
  `.track-card.is-playable`, `.track-card.needs-verification`,
  `.track-card.is-hidden`, plus mobile breakpoint.
- `site/app.js` + `docs/app.js` — added `initTrackFilter()` with safe
  no-op, scoped to `.detail-article`, click handler that toggles
  `is-hidden` and button `.active` / `aria-pressed` state.
- `site/items/2026-06-26-paste-greatest-songs-1960s/index.html` +
  `docs/items/2026-06-26-paste-greatest-songs-1960s/index.html` —
  regenerated via `update_site.py` to include the new filter bar and
  status classes.

## Constraint Compliance

- ✅ Did not modify `source.md`
- ✅ Did not modify `translation.zh-CN.md`
- ✅ Did not modify `summary.md` (no need to add any explanation; the
  filter is self-explanatory in the UI summary bar)
- ✅ Did not modify `notes.md`
- ✅ Did not modify `tracks.yaml` (verified count remains 33/50)
- ✅ Did not add new verified embed
- ✅ Did not create standalone project
- ✅ Did not modify README.md
- ✅ Did not modify unrelated reports
- ✅ Per-file `git add` (no `-A` / `.`)
- ✅ Did not force push or amend or hard reset
- ✅ Did not break homepage search/filter
- ✅ Did not break existing `.track-play-button` lazy-load iframe
  behavior
- ✅ All non-Paste detail pages: `track-filter-bar` count = 0
  (no DOM pollution, no JS listener, fully safe)

## Git

- **Commit**: `b2afd982c8abef89983e3ff9fc660ee63b537f06`
- **Tag**: `v0.3.28-playable-track-filter` → to be created next
- **Working tree**: clean
- **Branch**: `main`, up to date with `origin/main`

## UX Notes

- The filter **hides** cards (display: none) rather than collapsing or
  removing them from the DOM. This preserves lazy-loaded iframe state:
  if the user has played track #75, then filtered to "pending",
  then back to "all", the existing iframe in #75 is still there (it
  is preserved in the DOM by the `initTrackPlayers` no-replace
  guard that checks `btn.dataset.replaced === '1'`).
- The summary numbers in the bar (`50 / 33 / 17`) are computed at
  build time by `_build_track_filter_bar()` from the same tracks
  data used to render the cards, so the summary can never go out
  of sync with the actual card set.
- The active button has `aria-pressed="true"` and others `false` to
  preserve accessibility for screen readers.
- The `is-playable` class gives verified cards a subtle green
  border-left accent, complementing the existing confidence badge.
- The `needs-verification` class applies a 0.92 opacity dim so the
  user can still see the unfiltered set has a visual differentiation,
  but it's intentionally subtle (not aggressive) to avoid looking
  like an error state.
