# Translation Residue Policy

> **Status**: Active since v0.3.50
> **Audience**: AI agents and human reviewers editing `content/articles/**/translation.zh-CN.md`
> **Related scripts**: `scripts/check_translation_residue.py`

---

## Purpose

`check_translation_residue.py` exists to surface **疑似未翻译英文残留** in translated Chinese articles — not to eliminate every English token. Many articles legitimately retain English for clarity, recognition, and source traceability.

This policy explains how to interpret warnings and how to handle them.

---

## Categories

Each warning from `check_translation_residue.py` falls into one of these categories:

| Category | Meaning | Action |
|---|---|---|
| `suspicious residue` | Script flagged as potentially untranslated English | Investigate |
| `allowlisted known non-blocker` | Path + token explicitly approved by audit | No action; by design |
| `proper_noun_ok` | Book title, author name, brand, product name | Usually no action; document if recurring |
| `citation_or_url_ok` | Publisher in footnote, email, URL, copyright | No action |
| `needs_translation_fix — P0` | Obvious large omission (whole paragraph) | Must fix |
| `needs_translation_fix — P1` | Short sentence / title omission | Must fix |
| `needs_translation_fix — P2` | Minor idiom / phrase | Should fix in batch |
| `script_false_positive` | Script rule too coarse | Fix script rule, not the article |

---

## Current Policy (v0.3.50)

1. **专名、书名、机构名、产品名可保留英文**。 必要时使用"中文（English）"格式，避免让整句英文残留。
2. **URL、email、引用、版权信息可保留英文**，但长期反复触发的条目应建立精确 allowlist（path + token + reason）。
3. **明显英文句子 / 短语残留应修复**。 优先级 P0 > P1 > P2。P2 可在 batch 任务中处理。
4. **脚本误报应优先做规则优化**，而不是加大范围 allowlist。 例：v0.3.49 加入 `strip_html_comments()`。
5. **禁止 blanket ignore**。 不得用通配符或全局正则关闭真实残留检测。
6. **禁止关闭 residue 检查**。 `check_translation_residue.py` 永远以 WARNING 形式存在（不作为硬失败），但不得删除或禁用。
7. **allowlist 必须精确**：path + token + reason + introduced_before 版本号。 每个条目必须可审计、可回滚。
8. **新导入任务中出现 residue warning 时必须人工判断**，不得自动忽略。

---

## Known State After v0.3.50

### Allowed by Design

- **jasmi email** (`jaswsunny at gmail dot com`) is allowlisted as known non-blocker:
  - path: `content/articles/2026/2026-06-25-jasmi-the-old-world-is-dying/translation.zh-CN.md`
  - token: `jaswsunny at gmail dot com`
  - reason: Author contact email retained for citation traceability
  - introduced_before: v0.3.46

### Fixed in Earlier Versions

- **v0.3.47 triage** completed layer-by-layer audit of all residue warnings
- **v0.3.48** fixed all explicitly listed P2 needs_translation_fix items (13/13)
- **v0.3.49** stripped HTML comments from scanning (7 false positives removed)

### Expected Residual Warnings

After v0.3.50, the remaining warnings are **by design** and **not blockers**:

- **proper_noun_ok** (~65 items across 22 files): book titles, author names, brand names
- **citation_or_url_ok** (~2 items in 1 file): publisher names in footnotes
- **1 allowlisted item** (jasmi email): known non-blocker

No remaining `script_false_positive` items from HTML comments.

No P0/P1 needs_translation_fix items introduced or detected after v0.3.48.

---

## When to Fix Future Warnings

| New Warning Type | When to Fix |
|---|---|
| New obvious large omission (P0) | Immediately, in next task |
| New short omission (P1) | In next import task or cleanup batch |
| New P2 idiom / phrase | Batch with similar items, e.g., quarterly cleanup |
| New recurring proper noun | Evaluate: document, accept, or add to allowlist if needed |
| New HTML comment false positive | Improve script rule (extend `strip_html_comments()` or similar) |
| New citation / URL warning | Usually no action; document if recurring |

---

## How to Add a New Allowlist Entry

Only when the warning is a **legitimate, recurring, source-retained** residue:

1. Open `config/translation_residue_allowlist.yaml`
2. Add a new entry under `allowed_residues:`:

```yaml
- path: "content/articles/2026/YYYY-MM-DD-slug/translation.zh-CN.md"
  token: "exact token to allow"
  kind: "email" | "url" | "proper_noun" | "citation"
  reason: "Specific reason for retention"
  introduced_before: "vX.Y.Z"
```

3. Re-run `python3 scripts/check_translation_residue.py` to verify
4. Commit as a separate task (e.g., `vX.Y.Z-translation-residue-known-warning-cleanup`)

**Never** add an entry that hides real visible English residue.

---

## References

- v0.3.46: `reports/translation_residue_known_warning_cleanup_v0346_20260627.md`
- v0.3.47: `reports/translation_residue_triage_v0347_20260627.md`
- v0.3.48: `reports/translation_residue_p2_fix_batch_v0348_20260627.md`
- v0.3.49: `reports/translation_residue_script_false_positive_cleanup_v0349_20260627.md`
- v0.3.50: `reports/translation_residue_final_state_v0350_20260627.md`

---

*Last updated: 2026-06-27*