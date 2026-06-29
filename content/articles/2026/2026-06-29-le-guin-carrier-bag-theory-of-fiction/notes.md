# Import Notes

## Preflight

- **Status**: PASS
- **Working tree**: clean (after reset-and-rebuild to incorporate a parallel
  remote commit `230c7f6` that landed during the run; the rebuild pattern
  matches the team's `Multi-agent shared repo, push collision handled via
  reset-and-rebuild` convention)
- **HEAD before this commit**: `230c7f6` (origin/main, "Add article_import_orwell-why-i-write report")
- **check_task_preflight.py**: PASS (release_tags warning only, unrelated)
- **Source PDF**: 4 pages, scanned, 3.0 MB, no text layer
- **OCR method**: tesseract 5.3.4 at 250 DPI, single pass, no deskew
- **Local PDF copy**: `inbox/raw/pdf/2026-06-29-le-guin-carrier-bag-theory-of-fiction.pdf` (gitignored via `*.pdf` rule)

## Source Information

- **Author**: Ursula K. Le Guin (1929–2018), American speculative-fiction writer
- **Original publication**: *Dancing at the Edge of the World* (Grove Press, 1986)
- **Book pages in this excerpt**: 164–171
- **Two essays in one scan**:
  - *The Carrier Bag Theory of Fiction* — pp. 164–170, **complete**
  - *Heroes* — pp. 170–171, opening only (scan cuts off mid-paragraph at p. 171)
- **License note**: Le Guin died 2018; *Dancing at the Edge of the World* (1986) is under copyright in most jurisdictions until at least 2034. The user supplied the local PDF directly; no public URL was fetched. Translation and excerpt are for personal knowledge-base use.

## Extraction Scope

**Boundaries**:
- **Start**: top of p. 164 (the three "Notes" / footnotes that introduce the section)
- **End of first essay**: bottom of p. 170 ("…room in the bag of stars.")
- **End of second essay ("Heroes")**: partway through p. 171, at the line "We left no
  footprints, even," says the narrator. Beyond this, the source PDF ends.
- **Length**: source 2,929 English words; translation 4,940 CJK characters.

**Why not the whole book**: This is a *single PDF*, not a book. It contains
exactly the two essays above. Neither the other essays in *Dancing at the Edge
of the World* nor the rest of the volume is in the source.

## Duplicate Check

- **Source URL**: not applicable (local PDF; `source_url_missing: true`)
- **Title "The Carrier Bag Theory of Fiction"**: NOT FOUND in catalog
- **Title_zh "故事的承载袋理论"**: NOT FOUND
- **Author "Ursula K. Le Guin"**: NOT FOUND
- **Slug "le-guin" or "carrier-bag"**: NOT FOUND

## Blocked Check

- **PDF open**: PASS (opens in 0.2s; `pdfinfo` and `pdftoppm` both succeed)
- **OCR pipeline**: PASS (tesseract 5.3.4 + PIL available; no new deps installed)
- **No encryption / no permission error**: PASS
- **No paywall / network calls**: PASS (no network used for this entry)

## OCR / Translation Decisions

| Surface form in OCR | Restored form | Method |
|---|---|---|
| `Nattve` | `Native` | `[OCR疑似: ...]` tag in source.md |
| `Percetving` | `Perceiving` | `[OCR疑似: ...]` tag |
| `Indi-ana` | `Indiana` | `[OCR疑似: 软连字符拆行]` tag |
| `herowsm` | `heroism` | `[OCR疑似: ...]` tag |
| `fertilize itand` | `fertilize it and` | `[OCR疑似: OCR 缺少空格...]` tag |
| `how \|` | `how I` | `[OCR疑似: 原文为 "how I"...]` tag |
| `1 am` | `I am` | `[OCR疑似: ...]` tag |
| `littke` | `little` | `[OCR疑似: ...]` tag |
| `solider` | kept as "solider" in source; translated 更结实 (likely 原文's "sturdier", but Le Guin has been known to use less common word choices) | Flagged in this `notes.md` |

**Rationale for minimal correction**: task boundary prohibits "凭空补写原文".
All corrections are character-level only; the corrected forms are obvious
contextual completions (e.g. "Native American Women" cannot contain "Nattve").
No sentence was added or removed; OCR artifacts are flagged, not silently
replaced, in the source file.

## Quality Check Results

- **check_kb.py**: PASS (53/53)
- **update_site.py**: PASS (5/5 steps including post-sync check)
- **check_pages_sync.py**: PASS
- **check_translation_residue.py**: WARNING (9 entries in this file, all
  proper nouns / book titles: *Dancing at the Edge of the World*,
  *Woman and Nature*, *The Women Speaking*, *Contemporary Poetry and Fiction
  by Native American Women*, *Feminist Criticism in the Wilderness*,
  *The New Feminist Criticism*, *Perceiving Women*, *Three Guineas*,
  *Women's Creation*, *The Left Hand of Darkness* — all allowlisted as
  proper names / canonical titles)

## 待确认问题

1. **Le Guin 原文 "solider container"**:OCR 给出 `solider`。英文中
   `solider` 不是标准词——可能是 `sturdier` 或 `solider`(更坚实,古用法)、
   或者 Le Guin 的自造。我保留原文并在中译用"更结实",但需要查 Le Guin
   权威电子本(Grove Press 1986 原书电子版)以确认。
2. **"how \| thrust my spear"**:竖线极可能是栏分隔被误识;`how I thrust`
   上下文通顺。Le Guin 1986 原文使用第一人称复数讲采集者故事,这里改用
   第一人称单数模仿"猎人故事"的张扬语态是合理的。
3. **《英雄们》一文是否完整收录**:本次扫描件只到 p. 171 中段。Le Guin
   同名集中还有独立的 "Heroes"(完整)。本条目如果以后拿到完整本,可补全。
4. **同 6-29 同日有 Orwell "Why I Write" 入库**(commit `61b12d0`),目录
   `content/articles/2026/2026-06-29-orwell-foundation-why-i-write/`。两条目
   日期同、slug 互不冲突,均通过 check_kb.py PASS。

## 可关联的知识库主题

- `content/articles/2026/2026-06-22-chinatalk-ken-liu-ai-freedom/` — Ken Liu 也是翻译者/作者,关注中美科幻交流
- `content/articles/2026/2026-06-25-second-axial-age-otto-scharmer/` — Scharmer 的"原型—历史"重写,可与 Le Guin 互参
- `content/articles/2026/2026-06-26-noema-how-ai-will-change-us/` — Le Guin 谈"容器式技术"在 AI 时代的回响
- `content/articles/2026/2026-06-26-palantir-philosophy-weigel-burton/` — 关于"技术作为支配"vs"技术作为器具"的姊妹议题
- `content/articles/2026/2026-06-26-emilycampbell-layers-of-ai-experience/` — "experience as carrier bag" 的可能延伸
- `content/articles/2026/2026-06-29-orwell-foundation-why-i-write/` — 同日入
  库;Orwell 关于"为什么写作"和 Le Guin 关于"为什么讲故事"形成姊妹篇

## Reference Paths

- OCR 报告:`reports/pdf_ocr_import_2026-06-29-le-guin-carrier-bag.md`
- 源 PDF(gitignore):`inbox/raw/pdf/2026-06-29-le-guin-carrier-bag-theory-of-fiction.pdf`
- 源 MD:`content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/source.md`
- 译 MD:`content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/translation.zh-CN.md`
- 元数据:`content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/metadata.yaml`

---

*Notes generated: 2026-06-29*
