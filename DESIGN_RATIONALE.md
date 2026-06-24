# Hermes KB — Design Rationale

> **Why this file exists.** A future agent (or future-you) opening `styles.css` should be able to
> answer "why is it this way?" without re-running the audit. Every design choice below maps back
> to one of four principles captured in the TASTE-1B audit. If a new rule doesn't fit one of the
> four, propose it as a separate design review — don't add it as a silent code change.

**Primary reference**: [linear.app](https://linear.app)
**Secondary reference**: [vercel.com](https://vercel.com)
**Audit source**: `outputs/taste-1b-hermes-kb/HERMES_KB_DESIGN_AUDIT.md` (PASS, 2026-06-24)

---

## The four principles (Trigger → Decision → Reason → Evidence)

### 1 · Readability over density
**Trigger** — A user opens the KB to find one article, scan title/tags/metadata, then click
through. Time-to-decide is the bottleneck, not click-count.
**Decision** — Cards are 720px wide on a 1440px container. Body text is 15.2px / line-height 1.6.
Card padding is 16h × 18v; card-to-card gap is 16px.
**Reason** — Wide single-column lists read like a magazine, not a dashboard. They let the eye
catch title → tag → metadata in <1s per card. Cramped text (2-col card grids on the same
container) slows browse-decide-open because the eye has to track context-switches.
**Evidence** — TASTE-1B audit §"Strongest 5 design points" #4 (single-column list on 1408px
container; 2026-06-24).

### 2 · System font as invisible infrastructure
**Trigger** — A KB is browsed on a Mac, on Linux, on Windows, on iOS, on Android. Each OS already
ships with the best UI font for its size-class.
**Decision** — `font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif`.
Exactly two weights: 400 (body, meta) and 600 (titles). No web fonts. No Inter, Geist, IBM Plex,
or JetBrains Mono anywhere.
**Reason** — A web font adds 100–300KB and 200–600ms render-block for zero content value on a
text-first site. The system font loads zero bytes, renders crisply on the user's own OS, and
imposes no typographic personality that competes with the article content.
**Evidence** — TASTE-1B §"Strongest 5 design points" #1.

### 3 · Pastel category signals
**Trigger** — Users browse 19–25 records in mixed order. The type field (article / note / project
/ collection) is the strongest semantic axis, but it must NOT compete with title or metadata.
**Decision** — Four pastel left-stripes on type badges (`#EFF6FF` blue / `#FEF3C7` amber /
`#D1FAE5` emerald / `#F3E8FF` purple). Pastels are background only; text-on-pastel uses the
matching darker shade for ≥ 4.5:1 contrast.
**Reason** — Instant recognition without chromatic loudness. The four hues are
color-blind-accessible (blue/amber/green carry semantic meaning; purple is decorative-only).
None of the three reference sites (Linear / Vercel / Stripe) does this — it's the KB's
signature move.
**Evidence** — TASTE-1B §"Strongest 5 design points" #2.

### 4 · Structural flatness
**Trigger** — A knowledge base is read in varied lighting (daylight office, dim bedroom,
bright cafe). A floating depth treatment looks like an ad in low-contrast conditions.
**Decision** — Cards use border-style shadow: `box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.08)`. No
blur. Hover changes border color, NOT shadow. No scale, no translate, no glow.
**Reason** — Border-style shadow is two visual signals in one: the border defines the surface,
the shadow defines the offset. It renders identically across zoom levels and doesn't need
per-breakpoint blur tuning. Multi-layer shadows (Stripe) and 6%-opacity blur (legacy hermes-kb)
both feel less crisp at small sizes.
**Evidence** — TASTE-1B §"Strongest 5 design points" #5; Vercel comparison §"border-style
shadows".

---

## Accent rationing (the single most important rule)

`#2563EB` / `var(--color-accent)` may appear ONLY on:
- `<a>` links
- `<button>` primary and `[role="button"]`
- `:focus-visible` outlines
- Exactly one active filter pill at a time

Forbidden on: section headers, dividers, category labels, card decorations, banner backgrounds,
stat-card numbers, type badges. The accent is a signal, not a decoration.

If you add an accent-colored element, ask "is this actionable?" If no, use a text color.

---

## Spacing scale

All spacing uses the scale: `[4, 8, 12, 16, 24, 32, 40, 64, 96]` (8px base).

No `13px`, no `105px`, no random margin values. If a measurement needs a value not on the scale,
use the closest scale value and document the exception in the component's CSS comment.

---

## Container & layout

- Max-width: 1440px (Vercel reference). Cards sit at 720px (49% container width).
- Single-column list. No bento grid. No 2-col card layout.
- Section gaps ≤ 64px. Functional blocks (banner / filter / search / cards) deserve tight
  rhythm, not chapter spacing.

---

## Anti-patterns (always forbidden)

- Gradients (except existing banner element)
- Multi-layer shadows
- `filter: drop-shadow(...)`
- Glow effects
- Hover animations (scale, translate, opacity shifts beyond color)
- Decorative icons in empty states / headers / category labels
- SaaS-hero layout (big headline + subhead + CTA)
- "Oops!" / "Try adjusting your search!" empty-state copy
- Exclamation marks in user-facing strings
- Hardcoded hex values outside `:root` in `styles.css`
- Inline styles for color / spacing / radius
- New web fonts added to the repo
- Negative letter-spacing
- H2–H6 elements (single H1 per page only)

---

## Files affected by design changes

| File | Role |
|---|---|
| `site/styles.css` | Single source of design truth (1012 lines). Mirrored byte-identical to `docs/styles.css`. |
| `docs/styles.css` | GitHub Pages mirror. Must stay byte-identical to `site/styles.css`. |
| `CLAUDE.md` | Agent rules — what future agents must preserve. |
| `.cursor/rules/hermes-kb-taste.mdc` | Cursor editor auto-load rules. |
| `README.md` | Human-facing repo guide. |

---

## When in doubt

Read `outputs/taste-1b-hermes-kb/HERMES_KB_DESIGN_AUDIT.md`. If a change doesn't fit any of the
four principles, propose it as a separate design review — not a silent code change.
