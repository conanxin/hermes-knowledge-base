# Audit Warnings Inventory
## v0.3.92 · 2026-07-02

---

## Background

This inventory lists all 37 audit_kb_state.py warnings before any cleanup in v0.3.92, classified by category and proposed handling strategy.

**Source of truth**: `python3 scripts/audit_kb_state.py --json` `checks.tag_topic_count_out_of_range`

---

## Summary

| Metric | Count |
|--------|-------|
| Total warnings | **37** |
| Unique files affected | **25** |
| Distinct warning code | 1 (`[tag_topic_count_out_of_range]`) |
| Hard failures | 0 |

All warnings are the same code: **soft range violations** for `tags` (soft range `[6, 12]`) and `topics` (soft range `[3, 8]`). These are **soft warnings** by design per the **Tags / Topics 软范围 WARN 政策 (v0.3.68+)** — non-blocking.

---

## Distribution by sub-type

| Sub-type | Count | Files affected |
|----------|-------|----------------|
| `tags` count too few (< 6) | 7 | 7 |
| `tags` count too many (> 12) | 14 | 12 |
| `topics` count too few (< 3) | 4 | 4 |
| `topics` count too many (> 8) | 12 | 8 |
| **(sum)** | **37** | **(unique: 25)** |

Note: a single file can violate both tags and topics ranges (counted twice in findings, once in unique files).

---

## Triage Methodology

1. **auto_fix** — additive, low-risk: missing tags or topics where the article title/source clearly suggests the value. Trimming/deletion of tags is destructive and avoided.
2. **keep_as_exception** — over-ranged entries where the high tag/topic count legitimately reflects content density (long interviews, transcripts, listicles, multi-topic essays). These should NOT be trimmed because they encode structural content, not just classification.
3. **needs_user_decision** — borderline cases where the user's content judgment is needed.

---

## Full Inventory

### Tags — too few (< 6)

| Count | File | Path | Decision |
|-------|------|------|----------|
| 4 | content/articles/2026/2026-06-26-wechat-译林出版社-我生病了要去西湖玩玩才能好起来/metadata.yaml | wechat-noema-ylcbs-illness-westlake | auto_fix |
| 4 | content/articles/2026/2026-06-27-wechat-澎湃翻书党-从传统评点看金庸倚天篇张无忌为什么总是被骗/metadata.yaml | wechat-pengpai-jinyong-yitian-zhangwuji-deception | auto_fix |
| 5 | content/articles/1994/1994-04-24-web-nielsen-norman-group-10-usability-heuristics-for-user-interface-design/metadata.yaml | nielsen-norman-1994-10-usability-heuristics | auto_fix |
| 5 | content/articles/2000/2000-04-06-web-joel-on-software-things-you-should-never-do-part-i/metadata.yaml | joel-on-software-2000-things-you-should-never-do-i | auto_fix |
| 5 | content/articles/2026/2026-03-25-reverse-game-theory-housing-shortage/metadata.yaml | reverse-game-theory-housing-shortage | auto_fix |
| 5 | content/articles/2026/2026-07-01-web-martinfowlercom-is-high-quality-software-worth-the-cost/metadata.yaml | martinfowler-software-quality-cost | auto_fix |
| 5 | content/articles/2026/2026-07-01-web-wwwpaulgrahamcom-the-need-to-read/metadata.yaml | paulgraham-need-to-read | auto_fix |

### Topics — too few (< 3)

| Count | File | Path | Decision |
|-------|------|------|----------|
| 1 | content/articles/1994/1994-04-24-web-nielsen-norman-group-10-usability-heuristics-for-user-interface-design/metadata.yaml | nielsen-norman-1994-10-usability-heuristics | auto_fix |
| 1 | content/articles/2000/2000-04-06-web-joel-on-software-things-you-should-never-do-part-i/metadata.yaml | joel-on-software-2000-things-you-should-never-do-i | auto_fix |
| 1 | content/articles/2026/2026-07-01-web-martinfowlercom-is-high-quality-software-worth-the-cost/metadata.yaml | martinfowler-software-quality-cost | auto_fix |
| 1 | content/articles/2026/2026-07-01-web-wwwpaulgrahamcom-the-need-to-read/metadata.yaml | paulgraham-need-to-read | auto_fix |

### Tags — too many (> 12)

| Count | File | Path | Decision |
|-------|------|------|----------|
| 13 | content/articles/2026/2026-06-22-paulgraham-earn-billion/metadata.yaml | paulgraham-earn-billion | keep_as_exception |
| 14 | content/articles/2026/2026-06-22-your-ai-is-not-a-tool/metadata.yaml | your-ai-is-not-a-tool | keep_as_exception |
| 14 | content/articles/2026/2026-06-26-emilycampbell-layers-of-ai-experience/metadata.yaml | emilycampbell-layers-of-ai-experience | keep_as_exception |
| 15 | content/articles/2026/2026-06-24-421news-the-people-are-never-right/metadata.yaml | 421news-the-people-are-never-right | keep_as_exception |
| 15 | content/articles/2026/2026-06-24-how-i-write-andrew-stanton/metadata.yaml | how-i-write-andrew-stanton | keep_as_exception |
| 15 | content/articles/2026/2026-06-25-jasmi-the-old-world-is-dying/metadata.yaml | jasmi-the-old-world-is-dying | keep_as_exception |
| 15 | content/articles/2026/2026-06-25-tandf-us-structural-power/metadata.yaml | tandf-us-structural-power | keep_as_exception |
| 15 | content/articles/2026/2026-06-26-chatgptpro-tyler-cowen-infovore/metadata.yaml | chatgptpro-tyler-cowen-infovore | keep_as_exception |
| 17 | content/articles/2026/2026-06-24-how-i-write-andrew-hunter-murray/metadata.yaml | how-i-write-andrew-hunter-murray | keep_as_exception |
| 20 | content/articles/2026/2026-06-22-chinatalk-ken-liu-ai-freedom/metadata.yaml | chinatalk-ken-liu-ai-freedom | keep_as_exception |
| 21 | content/articles/2026/2026-06-23-second-axial-age-otto-scharmer/metadata.yaml | second-axial-age-otto-scharmer | keep_as_exception |
| 25 | content/articles/2026/2026-06-26-dario-amodei-bloomberg-interview/metadata.yaml | dario-amodei-bloomberg-interview | keep_as_exception |
| 25 | content/articles/2026/2026-07-01-ali-abdaal-financial-freedom-easy/metadata.yaml | ali-abdaal-financial-freedom-easy | keep_as_exception |
| 27 | content/articles/2026/2026-06-26-paste-greatest-songs-1960s/metadata.yaml | paste-greatest-songs-1960s | keep_as_exception |

### Topics — too many (> 8)

| Count | File | Path | Decision |
|-------|------|------|----------|
| 9 | content/articles/2026/2026-06-24-how-i-write-andrew-stanton/metadata.yaml | how-i-write-andrew-stanton | keep_as_exception |
| 9 | content/articles/2026/2026-06-26-chatgptpro-tyler-cowen-infovore/metadata.yaml | chatgptpro-tyler-cowen-infovore | keep_as_exception |
| 10 | content/articles/2026/2026-06-24-how-i-write-andrew-hunter-murray/metadata.yaml | how-i-write-andrew-hunter-murray | keep_as_exception |
| 10 | content/articles/2026/2026-06-25-conan-harvard-commencement-2026/metadata.yaml | conan-harvard-commencement-2026 | keep_as_exception |
| 10 | content/articles/2026/2026-06-25-jasmi-the-old-world-is-dying/metadata.yaml | jasmi-the-old-world-is-dying | keep_as_exception |
| 10 | content/articles/2026/2026-06-25-tandf-us-structural-power/metadata.yaml | tandf-us-structural-power | keep_as_exception |
| 10 | content/articles/2026/2026-06-26-paste-greatest-songs-1960s/metadata.yaml | paste-greatest-songs-1960s | keep_as_exception |
| 12 | content/articles/2026/2026-06-26-noema-how-ai-will-change-us/metadata.yaml | noema-how-ai-will-change-us | keep_as_exception |
| 12 | content/articles/2026/2026-06-26-palantir-philosophy-weigel-burton/metadata.yaml | palantir-philosophy-weigel-burton | keep_as_exception |
| 12 | content/articles/2026/2026-07-01-ali-abdaal-financial-freedom-easy/metadata.yaml | ali-abdaal-financial-freedom-easy | keep_as_exception |
| 12 | content/notes/2026/2026-07-02-bingzhu-you-mv-production/metadata.yaml | bingzhu-you-mv-production (new entry, content-draft) | keep_as_exception |
| 15 | content/articles/2026/2026-06-26-dario-amodei-bloomberg-interview/metadata.yaml | dario-amodei-bloomberg-interview | keep_as_exception |

---

## Decision Rationale

### Why auto_fix (additive only)

- **tags=4, tags=5** with non-trivial topic coverage: the entries are missing 1-2 tags that are obvious from title or source_site. Adding 1-2 specific tags is information-preserving and low-risk.
- **topics=1** ("阅读笔记" only): adding 1-2 topical categories based on article title is reasonable.
- **Reverse-game-theory**: tags=5 with already-rich topics=5; only need 1 more general-purpose tag.

### Why keep_as_exception (no trim)

- **Long-form interviews/transcripts** (Dario Amodei 25 tags, Ali Abdaal 25 tags, second axial age 21 tags, Ken Liu 20 tags): Each tag is a named entity/topic referenced in the source. Trimming would lose structured reference information.
- **Listicle entries** (Paste greatest songs 27 tags): 27 = number of distinct songs/topics covered; structural not arbitrary.
- **Multi-essay collections** (421news 15, jasmi 15, TandF 15, chatgptpro 15): Each essay has multiple subtopics; tags are structural.
- **Bingzhu You MV production note**: 12 topics cover distinct production-pipeline aspects (rap / MV / AI music / AI video / character consistency / multi-modal / etc.). Lossy to trim.
- **Trim operation is destructive**: removing tags/topics might lose meaningful index relations and could regress searchability / discoverability. Per v0.3.68+ policy, soft range is intentionally non-blocking precisely because trimming is high-risk.

### No `needs_user_decision` cases

All 37 warnings are clear-cut enough to classify without further user input:
- The 7+4 under-ranged entries have obvious add candidates from title/source context.
- The 26 over-ranged entries all encode structural information about long content.

---

## Risk Assessment

| Class | Risk | Mitigation |
|-------|------|------------|
| auto_fix (11 findings across 7 files) | low | additive; will not lose information; visible diff is small |
| keep_as_exception (26 findings across ~19 files) | none (no change) | explicit retention with documented reason |
| modification of audit_kb_state.py | forbidden | NOT modifying thresholds or check logic |

---

## Verification Strategy

After cleanup:

1. Re-run `python3 scripts/audit_kb_state.py`
2. Compare `tag_topic_count_out_of_range` array
3. Expect:
   - 11 auto_fix findings: gone
   - 26 keep_as_exception: still listed (now documented as intentional)
   - Total: 37 → ~26 (auto_fixed count + 1 from Bingzhu You which we don't fix)

---

*Inventory generated: 2026-07-02 09:45 GMT+8 (v0.3.92 stage B)*
*Audit rule: scripts/audit_kb_state.py lines 234-242, constants at lines 53-54 (TAGS_SOFT_MIN/MAX = 6/12; TOPICS_SOFT_MIN/MAX = 3/8)*
*Policy basis: v0.3.68+ Tags / Topics soft-range WARN 政策*