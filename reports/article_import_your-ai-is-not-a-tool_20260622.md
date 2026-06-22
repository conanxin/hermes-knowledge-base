# Article Import Report: your-ai-is-not-a-tool

**Date**: 2026-06-22
**Source**: https://theconvivialsociety.substack.com/p/your-ai-is-not-a-tool
**Title**: Your AI Is Not a Tool / 你的 AI 不是一个工具
**Author**: L. M. Sacasas
**Slug**: 2026-06-22-your-ai-is-not-a-tool
**Path**: `content/articles/2026/2026-06-22-your-ai-is-not-a-tool/`

## Pipeline Results

| Step | Result | Notes |
|------|--------|-------|
| 1. Web extraction | OK | Full body + all 7 footnotes captured |
| 2. Source.md write | OK | 16,365 bytes; cleaned of Substack nav/share chrome |
| 3. Translation.zh-CN.md | OK | 15,793 bytes; 4,194 CJK characters; full prose + all 7 footnotes translated |
| 4. Summary.md | OK | Core thesis + 5-layer argument table + key concept distinctions + key quotes + one-sentence summary + extended reading list |
| 5. Notes.md | OK | "接受/反思/联想/行动" 4-layer personal annotation + 5 cross-references to other thinkers + action checklist |
| 6. Metadata.yaml | OK | 15 fields per skill spec, using current schema (`word_count: {source, translation}`) |
| 7. check_kb.py | OK | New article clean. 1 pre-existing FAIL on `2026-03-25-reverse-game-theory-housing-shortage` (legacy `word_count: "4500"` string form) — not blocking per skill guidance |
| 8. update_site.py | OK | build_index → export_site_data → sync_pages_docs all green; 19 records exported to site/data/catalog.json; 4 files synced to docs/ |
| 9. check_translation_residue.py | WARNING | 5 suspicious tokens — all intentional proper-noun book / newsletter / article titles: *The Convivial Society*, *The Emergence of a Hazardous Concept*, *The McLuhan Newsletter*, *Tools for Conviviality*, *The Loss of the Senses*. Consistent with the 2026-06-20 baseline |
| 10. Git commit | OK | `Add your-ai-is-not-a-tool article` (commit d97ee4b) |
| 11. Git push | OK | `main` → `origin/main` (f57a902..d97ee4b) |

## Word Counts

| File | Count |
|------|-------|
| source.md | 2,651 words |
| translation.zh-CN.md | 4,194 CJK characters (≈ 6,231 chars total) |

## Topics / Tags

- **Topics** (6): 人工智能, 技术哲学, 媒介理论, 伦理, 麦克卢汉, 伊凡·伊利奇
- **Tags** (14): AI, 工具, 环境, 系统, 技术中立性, 麦克卢汉, 伊利奇, 感知训练, 苦行, 认知投降, The Convivial Society, Antón Barba-Kay, 教皇利奥, Magnifica humanitas

## Translation Notes

- 文章的"austere / irenic / pugnacious"等高密度形容词都按中文语感逐一还原，未使用机器翻译常见的"果断的 / 友善的 / 好斗的"无差别套词。
- *Magnifica humanitas*、*Tools for Conviviality*、*The Loss of the Senses*、*The McLuhan Newsletter* 等书名 / 刊名均按惯例保留原名，首次出现时给出中文译名（如《欢愉工具》《感官的丧失》《麦克卢汉通讯》）。
- 全部 7 个脚注均已翻译，与正文一致。
- "asceticism" 在文中均译为"苦行"；"ascetical mode" 译为"苦行模式"。
- "McLuhan" 译为"麦克卢汉"（中文世界通用译名，未采用较生僻的"麦克鲁汉"等）。
- 标题"欢愉社会"为 *The Convivial Society* 的现行中译，与该通讯其他文章中已有译法一致。

## Article Highlights

> "你的 AI 不是一个工具。它是一个环境，而你身处其中。"

> "对友谊构成决定性障碍的技术"——这是 Illich 留给我们最锋利的标尺。

## Git Status

```
commit d97ee4b (HEAD -> main, origin/main)
Add your-ai-is-not-a-tool article
```

## Next Steps

- [ ] (Optional) Fix the pre-existing `2026-03-25-reverse-game-theory-housing-shortage` `word_count` legacy string form — separate cleanup task.
- [ ] (Optional) Watch for user feedback on the translation before considering "humanizer" pass.
