# CLAUDE.md — Agent Operating Rules

> **Audience**: Any AI agent (Claude Code, Cursor, Hermes subagent) editing files in this repo.
> **Read first**: `DESIGN_RATIONALE.md` (the *why*). This file is the *what to do / what not to do*.

---

## Project: hermes-knowledge-base

A static, content-first knowledge base. 23 records (article / note / project / collection).
Generated site lives in `site/`, GitHub Pages deploy lives in `docs/`. Both are byte-identical
for the published surface.

## Hard rules (DO NOT violate)

### Quality gate (MUST run before any commit that touches `content/` or `site/`)
```bash
python3 scripts/check_kb.py        # integrity gate — exit 0 required
python3 scripts/check_pages_sync.py # post-sync gate — site/ ↔ docs/ must match
```
If either fails, **do not commit**. Fix the failure; do not bypass.

### site/ ↔ docs/ invariant
`site/styles.css` and `docs/styles.css` MUST be byte-identical. After editing either, sync the
other with `cp site/styles.css docs/styles.css` and re-run `check_pages_sync.py`.

### Per-file `git add`
Never `git add -A` or `git add .`. Always:
```bash
git add DESIGN_RATIONALE.md
git add CLAUDE.md
git add site/styles.css docs/styles.css
git add .cursor/rules/hermes-kb-taste.mdc
```

---

## Hermes KB Taste Rules (CSS / component edits)

> **Full rationale**: `DESIGN_RATIONALE.md`. **Cursor auto-load**: `.cursor/rules/hermes-kb-taste.mdc`.

### Color tokens (the only literal hex values live in `:root`)
- `--color-bg`, `--color-surface`, `--color-text-primary`, `--color-text-secondary`,
  `--color-text-meta`, `--color-border`, `--color-accent`, `--color-on-accent`, `--color-accent-bg`,
  `--color-tag-bg`, `--color-tag-text`
- Category pastels: `--color-category-a/b/c/d` + matching `--color-category-X-text`
- Code blocks: `--color-code-bg`, `--color-code-fg`

### Accent rationing (single most important rule)
`var(--color-accent)` appears ONLY on:
- `<a>` links
- `<button>` primary / `[role="button"]`
- `:focus-visible` outlines
- Exactly one active filter pill at a time

Forbidden on: section headers, dividers, category labels, card decorations, banner backgrounds,
stat numbers, type badges.

### Spacing scale (only these values)
`[4, 8, 12, 16, 24, 32, 40, 64, 96]`. No `13px`, no `105px`.

### Radius tokens
- `--radius-button: 6px` (chips, action buttons)
- `--radius-card: 8px` (record cards, detail article, code blocks)
- `--radius-pill: 12px` (filter buttons, chip pills)
- `--radius-banner: 20px` (banner element)

### Card surface
- Border-style shadow: `box-shadow: var(--shadow-card)` (= `0 0 0 1px rgba(0,0,0,0.08)`)
- Hover: border-color shift only. NO shadow change, NO lift, NO scale.

### Typography
- System font only (`-apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`)
- Weights: 400 and 600 only
- No negative letter-spacing anywhere
- Single H1 per page; no H2–H6 outside `.markdown-body`

### Anti-patterns
- Gradients (except existing banner)
- Multi-layer shadows, `filter: drop-shadow()`, glow effects
- Hover scale/translate/opacity
- Decorative icons in empty states / category labels
- SaaS-hero layout (big headline + subhead + CTA)
- "Oops!" / "Try a different search!" empty-state copy
- Exclamation marks in user-facing strings
- Hardcoded hex outside `:root`
- New web fonts (Inter / Geist / IBM Plex / JetBrains Mono)
- H2–H6 elements

---

## Standard commands

| Task | Command |
|---|---|
| Run integrity gate | `python3 scripts/check_kb.py` |
| Run post-sync gate | `python3 scripts/check_pages_sync.py` |
| Rebuild site | `python3 scripts/update_site.py` |
| Re-export only | `python3 scripts/build_index.py` |

## Standard file-edit checklist (CSS only)

1. Edit `site/styles.css`
2. `cp site/styles.css docs/styles.css`
3. `python3 scripts/check_pages_sync.py` → must exit 0
4. `git diff --stat` → confirm only intended files changed
5. `git add <files>` (one per file, no `git add .`)
6. Commit with `Design:` prefix

## When in doubt

- Read `DESIGN_RATIONALE.md` (principles) + `outputs/taste-1b-hermes-kb/HERMES_KB_DESIGN_AUDIT.md` (the audit)
- If a change doesn't fit any of the 4 principles (Readability / System Font / Pastel Categories /
  Structural Flatness), propose it as a separate design review — not a silent code change.
