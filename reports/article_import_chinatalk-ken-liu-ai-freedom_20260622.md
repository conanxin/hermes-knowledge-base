# Article import: Ken Liu on AI and Freedom

**Import date:** 2026-06-22
**Source:** <https://www.chinatalk.media/p/ken-liu-on-ai-and-freedom>
**Hosts:** Jordan Schneider, Irene Zhang, Phoebe Chow
**Guest:** Ken Liu
**Published:** May 6, 2026
**Captured:** 2026-06-22
**Pipeline tag:** post-`v0.3.12-short-command-e2e-regression`

## Source extraction

| Field | Value |
|-------|-------|
| Extraction method | `web_extract` |
| Body completeness | 100% — full intro blurb, all 7 sections (Technology as Human Expression / The Age of Slop / Everything Not Said / The Real Danger of AI / Mythology vs. Ideology / Daoism and Freedom / The Inadequacy of Language), embedded book-excerpt passage, full Q&A dialogue markers, all three hosts' and Ken's lines |
| Paywall / login | None — Substack, public |
| Truncation | None |
| Article length | ~8,302 words (source) → ~12,139 CJK characters (translation) |
| Format | Podcast transcript / interview dialogue — multiple speakers, bold thesis statements, embedded book excerpts |

## Files generated

```
content/articles/2026/2026-06-22-chinatalk-ken-liu-ai-freedom/
├── metadata.yaml                (977 bytes)
├── source.md                    (49,914 bytes)
├── translation.zh-CN.md         (43,160 bytes)
├── summary.md                   (8,887 bytes)
└── notes.md                     (9,659 bytes)

site/items/2026-06-22-chinatalk-ken-liu-ai-freedom/index.html    (generated)
docs/items/2026-06-22-chinatalk-ken-liu-ai-freedom/index.html    (synced)
```

## `word_count` schema (object form, per v0.3.8+ requirement)

```yaml
word_count:
  source: 8302
  translation: 12139
```

This is the longest article in the knowledge base so far (previous max was the 2026-06-22-your-ai-is-not-a-tool article at 2651 source / 4194 translation). Both counts reflect real content (not placeholders), as required by `check_kb.py`.

## Pipeline results

| Step | Command | Result |
|------|---------|--------|
| 1 | `python3 scripts/check_kb.py` | **PASS** — Total items: 22, PASS: 22, FAIL: 0 (was 21/21 → 22/22, +1) |
| 2 | `python3 scripts/update_site.py` | **PASS** — Steps 1/5 → 5/5 all OK (build_index, export_site_data, generate_item_pages, sync_pages_docs, **check_pages_sync**) |
| 3 | `python3 scripts/check_pages_sync.py` | **PASS** — 22/22 slugs in both `site/items/` and `docs/items/`, all 4 top-level files byte-identical |
| 4 | `python3 scripts/check_translation_residue.py` | **WARNING** (pre-existing) — **2 intentional proper-noun retentions** on the new article (book title *All That We See or Seem*, hardware *Game Boy Advance*); matches established baseline for proper nouns |
| 5 | `diff site/data/catalog.json docs/data/catalog.json` | **byte-identical** |

## Catalog counts

```
total records: 22
by type: Counter({'article': 9, 'note': 5, 'resource_collection': 4, 'project': 4})
```

Article count went 8 → 9. All other type counts unchanged.

## Notable per-file decisions

- **Multi-speaker Q&A preserved**: the source is a podcast transcript with three hosts (Jordan, Irene, Phoebe) and one guest (Ken). All speaker markers preserved in both `source.md` (`**Jordan Schneider:**`) and `translation.zh-CN.md` (`**Jordan Schneider：**`). Chinese punctuation rules applied (full-width `：` not `:`).
- **Embedded book excerpt**: the long block-quoted passage from *All That We See or Seem* describing "Homo sapiens had always externalized their minds" was kept as a single indented blockquote in both files. Proper-noun coinages ("Talos", "codemonkey", "datajinn", "egolets", "fiscjinns", "memoelves", "codedaemons", "bug-genies", "patchsprites", "scriptpixies", "cogitrons", "electrons", "logons") were kept in English with brief contextual Chinese inline where useful.
- **Proper nouns kept in English (per skill baseline)**: *Dandelion Dynasty*, *Pantheon*, *Three-Body Problem*, *Dao De Jing*, *All That We See or Seem*, *Pluribus*, *Frankenstein*, *1984*, *Lord of the Rings*, *Dao De Jing*, *Pantheon*, individual characters like Talos / Julia Z / Jane Whitefield / Clarice Starling / Roland Barthes / Walter Benjamin / Ayn Rand / Steve Jobs / Arthur Waley / Tolkien / Le Guin / Orwell / Mary Shelley / Laozi / Zhuangzi — all kept in original.
- **Laozi/Zhuangzi 翻译约定**: following Ken Liu's own translation choices, used "老子/庄子" in body text with English in parentheses on first mention ("老子(Laozi)"), then Chinese-only thereafter.
- **Direct quotation of the Dao De Jing**: "The way that can be stated is not the way. The path that can be laid out is not the path." — translated as "可以言说之道，不是恒常之道。可以指出之路，不是恒常之路。" This mirrors how Chinese readers would naturally quote the original 道德经 (道可道，非常道；名可名，非常名).
- **Bold thesis statements preserved**: in `summary.md` the section "核心论点" mirrors the original's bold-thesis structure 1:1 so future readers can navigate by the same headings Ken used.

## Translation residue hits on new article (2 — both legitimate)

| Original | Why kept |
|----------|----------|
| *All That We See or Seem* | Ken Liu's book title — proper noun retention per skill baseline |
| *Game Boy Advance* | Nintendo hardware product name — proper noun retention per skill baseline |

Per `kb-article-import` skill, these are well-known false-positive patterns matching the established baseline (e.g. *Dandelion Dynasty*, *Pantheon*, *Three-Body Problem* in the source — all kept similarly). No "fix" needed.

## Cross-references in `notes.md`

- *你的 AI 不是一个工具*（L. M. Sacasas, 2026-06-22）：两文都拒绝"AI 是工具"的简化叙事。
- *Superlinear Returns* / *How to Earn a Billion Dollars*（Paul Graham, 2026-06-22）：本文在"增长"叙事上提供"同理心与创作动机"的补充视角。
- 老子《道德经》——Ken Liu 译本（the book referenced and quoted from throughout）。
- 庄子寓言——尤其"得意忘言"那段，是 Ken 关于"语言之不足"的论点的原始依据。
- Walter Benjamin《机械复制时代的艺术作品》(1935)——aura 概念被 Ken 借用以反对"AI 取代艺术"的论点。
- Roland Barthes《作者之死亡》(1967)——本文用来类比 LLM 是"全部过去写作的字典"的具体落实。

## Summary of pipeline changes (counted)

| Direction | Delta |
|-----------|-------|
| `content/articles/2026/` total | +1 directory |
| `site/items/` total | 21 → 22 |
| `docs/items/` total | 21 → 22 |
| `site/data/catalog.json` records | 21 → 22 |
| `docs/data/catalog.json` records | 21 → 22 |
| `index/{authors,tags,timeline}.md` | each updated with new record |
| `index/catalog.jsonl` | +1 line |

No drift between `site/` and `docs/` after the post-sync integrity check ran.

## Verification commands (for re-run)

```bash
cd ~/projects/hermes-knowledge-base
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/check_pages_sync.py
python3 scripts/check_translation_residue.py
diff site/data/catalog.json docs/data/catalog.json
ls site/items/2026-06-22-chinatalk-ken-liu-ai-freedom/
ls docs/items/2026-06-22-chinatalk-ken-liu-ai-freedom/
```