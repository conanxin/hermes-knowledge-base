# v0.3.49-translation-residue-script-false-positive-cleanup Report

**Date**: 2026-06-27
**Branch**: main
**Starting HEAD**: `707a96d`
**Origin/main at start**: `707a96d`
**Planned tag**: `v0.3.49-translation-residue-script-false-positive-cleanup`
**Recommended next minor before task**: v0.3.49
**Git status at start**: clean

---

## 1. STATUS

* **STATUS**: PASS
* **Result type**: PASS
* **Summary**: Minimal script cleanup for HTML comment false positives in translation residue checks.

---

## 2. Version / Git

* **commit**: pending until commit
* **commit hash**: pending until commit
* **tag**: `v0.3.49-translation-residue-script-false-positive-cleanup`
* **tag object**: pending until tag creation
* **tag deref**: pending until tag creation
* **tag deref commit**: pending until tag creation
* **HEAD**: `707a96d`
* **origin/main**: `707a96d`
* **git status**: clean at task start
* **git status –short**: clean at task start

---

## 3. Scope

* **task name**: v0.3.49-translation-residue-script-false-positive-cleanup
* **task type**: quality-gate script false-positive cleanup
* **allowed files**:
    * scripts/check_translation_residue.py
    * reports/translation_residue_script_false_positive_cleanup_v0349_20260627.md
* **forbidden files**:
    * content/articles/**
    * translation.zh-CN.md
    * source.md
    * metadata.yaml
    * summary.md
    * notes.md
    * tracks.yaml
    * config/translation_residue_allowlist.yaml
    * unrelated reports
* **modified files**:
    * scripts/check_translation_residue.py
    * reports/translation_residue_script_false_positive_cleanup_v0349_20260627.md

---

## 4. Inputs

### For import tasks:

* **source URL**: N/A — not an import task
* **short command**: N/A — not an import task
* **content directory**: N/A — no content directory created
* **duplicate check**: N/A — no import attempted
* **blocked check**: N/A — no external fetch attempted
* **GitHub Pages URL**: https://conanxin.github.io/hermes-knowledge-base/

### For feature tasks:

* **feature target**: HTML comment false-positive cleanup for translation residue checker
* **modified scripts/docs**:
    * scripts/check_translation_residue.py
* **generated files**: none
* **modified files**:
    * scripts/check_translation_residue.py
    * reports/translation_residue_script_false_positive_cleanup_v0349_20260627.md

---

## 5. Checks

| Script | Result |
|---|---|
| `check_task_preflight.py` | **FAIL** (expected: dirty tree from staged changes during task) |
| `check_release_tags.py` | **PASS_WITH_WARNINGS** (v0.3.36 known exception) |
| `check_kb.py` | **PASS** (47/47) |
| `check_tracks.py` | **PASS** (38 verified, 12 needs) |
| `update_site.py` | **PASS** (5/5, no diff) |
| `check_pages_sync.py` | **PASS** |
| `check_translation_residue.py` | **WARNING** (false positives reduced; proper_noun_ok/citation_or_url_ok remain) |

---

## 6. Smoke Tests

* **local smoke**: N/A — no site UI changes
* **online smoke**: N/A — no site UI changes
* **pages URL**: https://conanxin.github.io/hermes-knowledge-base/
* **GitHub Pages URL**: https://conanxin.github.io/hermes-knowledge-base/

---

## 7. Postflight

To be run after commit/tag:

```bash
python3 scripts/check_task_postflight.py \
    --report reports/translation_residue_script_false_positive_cleanup_v0349_20260627.md \
    --tag v0.3.49-translation-residue-script-false-positive-cleanup \
    --expect-clean --expect-head-origin
```

**Expected**:
* **check_task_postflight.py**: PASS
* **postflight status**: PASS
* **warnings**: 0
* **tag deref**: final v0.3.49 commit
* **tag deref commit**: final v0.3.49 commit
* **git status**: clean

---

## 8. Links

* **GitHub commit**: pending until push
* **GitHub tag**: pending until tag push
* **GitHub Pages**: https://conanxin.github.io/hermes-knowledge-base/

---

## 9. Warnings / Known Non-blockers

* **known warning**: `check_release_tags.py` may report PASS_WITH_WARNINGS for known v0.3.36 duplicate minor exception
* **reason**: historical tag exception documented in docs/RELEASES.md and docs/VERSIONING.md
* **action**: no action required
* **known warning**: `check_translation_residue.py` still reports WARNING because this task only removes HTML comment false positives
* **reason**: proper_noun_ok, citation_or_url_ok entries remain by design (legitimate book titles, author names, journal names, etc.)
* **action**: no action for this round; future tasks may address residue policy

---

## 10. Next Version

* **recommended next minor**: expected v0.3.50 after tag creation
* **next suggested task**: proper noun / citation residue policy summary or final translation residue state report

---

## 11. Script False Positive Cleanup Details

### Source Report

* **v0.3.47 triage report**: `reports/translation_residue_triage_v0347_20260627.md`
* **v0.3.47 classification**: script_false_positive (4 items per report count, 3 explicitly listed)

### HTML Comment False-Positive Samples Before

| # | Path | Token | In HTML Comment |
|---|---|---|---|
| 1 | chatgptpro-tyler-cowen-infovore | `shares his chats` | `<!-- Translation: An "infovore" shares his chats → ... -->` |
| 2 | chatgptpro-tyler-cowen-infovore | `ChatGPT Pro Community` | `<!-- 撰稿：ChatGPT Pro Community；主角：Tyler Cowen -->` |
| 3 | paste-greatest-songs-1960s | `greatest songs of the` | `<!-- Translation: The 100 greatest songs of the 1960s → ... -->` |
| 4+ | noema-how-ai-will-change-us | `How AI Will Change Us`, `Houda Nait El Barj researcher at OpenAI`, `Thrownness Meets Abundance` | Multiple HTML comments (translation notes, author info) |

### Exact Script Change

Added a `strip_html_comments()` function and called it before the Markdown stripping step:

```python
def strip_html_comments(text):
    """剥离 HTML 注释块（<!-- ... -->），包括单行和多行。
    HTML comments are source/build annotations, not user-visible translation text.
    它们包含 import metadata、translation notes、build hints 等，不应被当作翻译残留。
    """
    return re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)
```

In the `check_translation_residue()` main loop, before the `clean = re.sub(...)` Markdown stripping:

```python
# 剥离 HTML 注释（v0.3.49）：注释内是 source/build metadata，不是用户可见译文
content = strip_html_comments(content)
```

The change is minimal: 1 new function (8 lines) + 2-line insertion point. No other logic affected.

### Before/After Comparison

| File | Before suspicious_count | After suspicious_count | Reduction |
|---|---|---|---|
| chatgptpro-tyler-cowen-infovore | 5 | 2 | -3 ✅ |
| paste-greatest-songs-1960s | 85 | 84 | -1 ✅ |
| noema-how-ai-will-change-us | 4 | 1 | -3 ✅ |
| **Total false positives removed** | | | **-7** ✅ |
| **Files with warnings** | 25 | 25 | 0 (all 3 files still have legitimate proper_noun_ok) |

### Confirmation

* **content/articles were NOT modified**: ✅ (verified via `git diff --stat`)
* **allowlist was NOT modified**: ✅ (config/translation_residue_allowlist.yaml unchanged)
* **jasmi allowlist still works**: ✅ (`allowlisted_count: 1 (known non-blocker)` still shown)
* **Real visible English residue is still detected**: ✅ (e.g., Thoreau `Henry David Thoreau`, paste `Second That Emotion`, ai-unconscious `manner of speaking` still detected)
* **proper_noun_ok still detected**: ✅ (~72 proper noun items still flagged)
* **citation_or_url_ok still detected**: ✅ (publisher names in footnotes still flagged)
* **No new warnings introduced**: ✅ (warning count reduced, not increased)
* **No blanket ignore of English**: ✅ (only HTML comment blocks are stripped, regex `<!--.*?-->` with DOTALL flag)
* **Allowlist mechanism preserved**: ✅ (`is_allowlisted()` still called after content stripping)
* **Markdown stripping preserved**: ✅ (Markdown syntax still removed after HTML comment stripping)

### Remaining Warning Categories

After this cleanup, the remaining warnings are by design:
- **proper_noun_ok** (~65 items): book titles, author names, brand names, etc. (legitimate English in translation)
- **citation_or_url_ok** (~2 items): publisher names in footnotes
- **1 allowlisted item** (jasmi email): known non-blocker

No remaining `script_false_positive` items from HTML comments.

---

*Report generated: 2026-06-27*