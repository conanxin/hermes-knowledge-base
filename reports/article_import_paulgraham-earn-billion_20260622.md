# Article import: How to Earn a Billion Dollars

**Import date:** 2026-06-22
**Source:** <https://paulgraham.com/earn.html>
**Author:** Paul Graham
**Published:** June 2026 (based on a talk at the Oxford Union)
**Captured:** 2026-06-22
**Pipeline tag:** post-`v0.3.12-short-command-e2e-regression`

## Source extraction

| Field | Value |
|-------|-------|
| Extraction method | `web_extract` |
| Body completeness | 100% — full title, byline, "based on a talk" subtitle, all body paragraphs, "Thanks" line |
| Paywall / login | None — plain HTML, public, no JS-rendered content |
| Truncation | None |
| Article length | ~2,333 words (source) → ~3,303 CJK characters (translation) |

## Files generated

```
content/articles/2026/2026-06-22-paulgraham-earn-billion/
├── metadata.yaml                (767 bytes)
├── source.md                    (13,295 bytes)
├── translation.zh-CN.md         (11,651 bytes)
├── summary.md                   (5,233 bytes)
└── notes.md                     (5,281 bytes)

site/items/2026-06-22-paulgraham-earn-billion/index.html    (generated)
docs/items/2026-06-22-paulgraham-earn-billion/index.html    (synced)
```

## `word_count` schema (object form, per v0.3.8+ requirement)

```yaml
word_count:
  source: 2333
  translation: 3303
```

- `source`: regex `\b[A-Za-z][A-Za-z\-']*\b` over source.md with markdown link / code-block / heading / quote markers stripped.
- `translation`: regex `[\u4e00-\u9fff]` over translation.zh-CN.md.

## Pipeline results

| Step | Command | Result |
|------|---------|--------|
| 1 | `python3 scripts/check_kb.py` | **PASS** — Total items: 21, PASS: 21, FAIL: 0 (was 20/20 → 21/21, +1) |
| 2 | `python3 scripts/update_site.py` | **PASS** — Steps 1/5 → 5/5 all OK (build_index, export_site_data, generate_item_pages, sync_pages_docs, **check_pages_sync**) |
| 3 | `python3 scripts/check_pages_sync.py` | **PASS** — 21/21 slugs in both `site/items/` and `docs/items/`, all 4 top-level files byte-identical |
| 4 | `python3 scripts/check_translation_residue.py` | **WARNING** (pre-existing) — **0 suspicious hits** on the new article; WARNING only aggregates legacy article warnings |
| 5 | `diff site/data/catalog.json docs/data/catalog.json` | **byte-identical** |

## Catalog counts

```
total records: 21
by type: Counter({'article': 8, 'note': 5, 'resource_collection': 4, 'project': 4})
```

Article count went 7 → 8. All other type counts unchanged.

## Notable per-file decisions

- **Translation style**: Paul Graham's idiomatic English ("my ass off", "crap signal", "contrived", "lame") was rendered with **equivalent-register Chinese** (e.g. "拼命", "糟糕的信号", "刻意", "听起来很烂") rather than literal translation. This preserves the speaker's voice — a key requirement for a transcript-style piece.
- **Subtitle preserved**: "(This is based on a talk I gave at the Oxford Union.)" was kept italicized in both `source.md` and `translation.zh-CN.md` as a structural marker — the entire piece reads as transcribed speech, not a written essay.
- **Mathematical content kept literal**: `log(500, 1.93) ≈ 9.45` and `1.15^60 ≈ 4384` were kept as English expressions inside the Chinese translation, since they're computational syntax (calculators accept them as-is). Translating them would obscure the "do the math yourself" interactive intent.
- **Proper nouns kept in English**: Y Combinator, Oxford Union, Twitch, Justin.TV, Airbnb, Apple, Facebook, Google — all kept in original to match established convention across the knowledge base.
- **Linked X post**: `[impossible](https://x.com/MarcoFoster_/status/2052427151371047016)` was preserved verbatim. Per memory: do not fabricate handles; the X handle visible in the source is `@MarcoFoster_` and the status ID is preserved.

## Cross-references in `notes.md`

- *Superlinear Returns* (paulgraham-superlinear-returns): sister essay — provides the theoretical foundation; this article is the operationalization.
- *How to Get Startup Ideas* (in the broader Paul Graham essay canon, not yet imported): cited as the source of the "don't look for startup ideas" doctrine.
- *How to Do Great Work* (in the same canon): echoes "make what you want to use."
- Y Combinator cultural doctrine ("do things that don't scale"): the engineering version of the high-growth-rate argument.

## Summary of pipeline changes (counted)

| Direction | Delta |
|-----------|-------|
| `content/articles/2026/` total | +1 directory |
| `site/items/` total | 20 → 21 |
| `docs/items/` total | 20 → 21 |
| `site/data/catalog.json` records | 20 → 21 |
| `docs/data/catalog.json` records | 20 → 21 |
| `index/{authors,tags,timeline}.md` | each updated with new record |
| `index/catalog.jsonl` | +1 line |

No drift between `site/` and `docs/` after the post-sync integrity check ran — `check_pages_sync.py` STEP 5/5 in `update_site.py` confirmed this.

## Verification commands (for re-run)

```bash
cd ~/projects/hermes-knowledge-base
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/check_pages_sync.py
python3 scripts/check_translation_residue.py
diff site/data/catalog.json docs/data/catalog.json
ls site/items/2026-06-22-paulgraham-earn-billion/
ls docs/items/2026-06-22-paulgraham-earn-billion/
```