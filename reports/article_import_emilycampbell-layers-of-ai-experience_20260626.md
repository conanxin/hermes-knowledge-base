# Article Import Report: 2026-06-26-emilycampbell-layers-of-ai-experience

## Summary

- **Source**: emilycampbell.co — Emily Campbell, "The Layers of AI experience" (subtitle: "Designing beneath the surface")
- **URL**: https://emilycampbell.co/writing/layers-of-ai-experience
- **Published**: 2026-06-03
- **Captured**: 2026-06-26
- **Slug**: `2026-06-26-emilycampbell-layers-of-ai-experience`
- **Author**: Emily Campbell — VP of Design at HackerRank; runs Shape of AI (https://www.shapeof.ai/)
- **Type**: `article` (long-form design essay, ~5378 words / 21 min read)

## Pipeline execution

| # | Step | Tool | Result |
|---|------|------|--------|
| 1 | Pre-check | `check_kb.py` | 25 PASS / 0 FAIL (before import) |
| 2 | Schema discovery | Read 3 most recent `metadata.yaml` (theconvivialsociety / oneusefulthing / second-axial-age) | Confirmed: `word_count` must be `{source: int, translation: int}` dict; `path` field required |
| 3 | Duplicate check | `site/data/catalog.json` scan | URL not yet imported (no hit on `emilycampbell`) |
| 4 | Source extract | `browser_navigate` + `curl -A Mozilla` | `web_extract` falsely flagged URL as private/internal (Vercel-served); fell back to browser stack + curl HTML parse |
| 5 | HTML → markdown | Custom Python regex pass on `<div class="prose-article">` blocks | 12 prose blocks concatenated; 3 footnotes recovered from `<ol class="footnotes-list">` |
| 6 | Source write | `write_file source.md` | 5378 English words, 0 CJK contamination (sanitizer grep clean) |
| 7 | Translation write | Subagent → `write_file translation.zh-CN.md` | 8801 CJK characters, 256 lines; canonical 6-layer terms preserved (用户界面层 / 上下文层 / **驾驭层** / 模型层 / 治理层 / **涌现**); 3 footnotes translated; 14 `***emphasis***` markers preserved |
| 8 | Summary / Notes | `write_file` | Summary (5240 B) — 6-layer table + history table + 3 concept distinctions + key quotes + 1-sentence thesis; Notes (7802 B) — 接受/反思/联想/行动 4-layer structure + cross-references to Garrett / Mill / Meadows / Maeda / Sacasas / Shape of AI |
| 9 | Metadata write | `write_file metadata.yaml` | YAML lint OK, 14 tags, 7 topics, `word_count: {source: 5378, translation: 8640}`, `path: content/articles/2026/2026-06-26-emilycampbell-layers-of-ai-experience/` |
| 10 | Post-write `check_kb.py` | All gates | 26 PASS / 0 FAIL |
| 11 | `update_site.py` (5-step) | check_kb → build_index → export_site_data → generate_item_pages → sync_pages_docs → check_pages_sync | All 5 steps OK |
| 12 | `check_pages_sync.py` | Standalone run | 26/26 slugs byte-identical between `site/` and `docs/` |
| 13 | `check_translation_residue.py` | Standalone run | WARNING (15 hits, all baseline-acceptable: essay titles, author names, Meadows / Garrett / Mill proper nouns) |
| 14 | `git add` per file | 13 files staged | No `git add -A`, no blanket staging |
| 15 | First commit | `Add 2026-06-26-emilycampbell-layers-of-ai-experience article` | Local: `146b1d0` (initially), then `2b762d2` (after rebase) |
| 16 | Push | `git push origin main` | Required 2 reset+rebuild cycles due to concurrent remote commits (music / paste work). Final push: `b9b829a..2b762d2` |
| 17 | Live verification | curl to GitHub Pages | HTTP 200 on items page; catalog has 39 records including new slug |
| 18 | Report commit | (this file) | Separate commit for content / report split |

## Pipeline incidents

1. **`web_extract` false positive on Vercel URL.** Reported "Blocked: URL targets a private or internal network address" despite the site being publicly accessible via curl with `200 OK` and `server: Vercel`. Fell back to `browser_navigate` (full snapshot truncated, 8000-char limit) + raw `curl` + Python regex extraction of `<div class="prose-article">` blocks. The 1.5 MB Next.js page contains ~12 prose text blocks and 3 footnote `<li>` items once scripts/styles are stripped.
2. **Concurrent remote commits blocked the first push.** Remote `main` was 3 commits ahead by the time we tried to push (music / paste work from other agents). Strategy: save content → `git reset --hard origin/main` → restore content → `update_site.py` → re-commit → push. This worked on the second attempt; third attempt also raced. The winning run used the same reset strategy in a single tight shell chain.
3. **CDN cache served stale catalog for ~3 minutes.** Initial live `data/catalog.json` showed 38 records (old); `git show origin/main:docs/data/catalog.json` showed 39. After waiting ~3 min, live served 39 and the items page returned HTTP 200. This matches the known 5-10 min CDN-sync window flagged in `kb-article-import/SKILL.md` ("GitHub Pages root may 404 for 5-10 min after push").

## Files written

```
content/articles/2026/2026-06-26-emilycampbell-layers-of-ai-experience/
├── metadata.yaml              (932 B,  15 required fields)
├── source.md                  (34284 B, 5378 English words, 3 footnotes)
├── translation.zh-CN.md       (31642 B, 8801 CJK chars, 256 lines)
├── summary.md                 (5240 B, 6-layer table + history + concept distinctions + key quotes)
└── notes.md                   (7802 B, 4-layer personal annotation + cross-refs)
```

Plus 8 generated files in `site/`, `docs/`, and `index/` (catalog.json, item page HTML, timeline/authors/tags).

## Translation vocabulary decisions (the hard calls)

| Term | Decision | Why |
|------|----------|-----|
| User Interface layer | **用户界面层** | Canonical, matches Chinese UX literature |
| Context layer | **上下文层** | Canonical, distinguishes from "语境" (linguistic) |
| Harness layer | **驾驭层** (NOT 框架 / 架构) | Preserves the harness metaphor — "wearing the model" not "framing it" |
| Model layer | **模型层** | Canonical |
| Governance layer | **治理层** | Canonical, distinct from "管理层" (management) |
| Emergence | **涌现** (NOT 突现) | Established complex-systems term in mainland Chinese (Bertalanffy / Wu Tingjie lineage) |
| **Connectors** / **Tools** / **Skills** / **Agents** | **连接器 / 工具 / 技能 / 智能体** | Mainland AI vocabulary standard |
| **direction** / **oversight** | **方向** / **监督** (preserved as `***emphasis***`) | User's two-phase interaction model |
| **explicit** / **inferred** | **显式** / **推断** (preserved as `***emphasis***`) | Type distinction inside Context layer |
| Donella Meadows | **Donella Meadows** (English) | Established proper-noun form |
| leverage points | **杠杆点** (Chinese gloss) | First mention translated with English term in parens |

## Cross-references added to other KB articles

- `2026-06-24-theconvivialsociety-owning-our-words` — L. M. Sacasas on language machinery in the AI era; complementary critique of "language as material" (this article treats AI as material)
- (Implicit) Garrett (2000) and Mill (2021) are external refs, not yet KB entries

## Final state

- **Local**: `2b762d2` on `main`, working tree clean
- **Remote**: `2b762d2` on `origin/main`
- **Live**: https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-emilycampbell-layers-of-ai-experience/index.html (HTTP 200)
- **Catalog**: 39 records (was 38; +1)
