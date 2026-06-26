# v0.3.47-translation-residue-triage Report

**Date**: 2026-06-27
**Branch**: main
**Starting HEAD**: `ff98e85`
**Origin/main at start**: `ff98e85`
**Planned tag**: `v0.3.47-translation-residue-triage`
**Recommended next minor before task**: v0.3.47
**Git status at start**: clean

---

## 1. STATUS

* **STATUS**: PASS
* **Result type**: PASS
* **Summary**: Read-only triage of current translation residue warnings across 25 articles.

---

## 2. Version / Git

* **commit**: pending until commit
* **commit hash**: pending until commit
* **tag**: `v0.3.47-translation-residue-triage`
* **tag object**: pending until tag creation
* **tag deref**: pending until tag creation
* **tag deref commit**: pending until tag creation
* **HEAD**: `ff98e85`
* **origin/main**: `ff98e85`
* **git status**: clean at task start
* **git status –short**: clean at task start

---

## 3. Scope

* **task name**: v0.3.47-translation-residue-triage
* **task type**: quality-gate triage
* **allowed files**:
    * reports/translation_residue_triage_v0347_20260627.md
* **forbidden files**:
    * content/articles/**
    * tracks.yaml
    * source.md
    * translation.zh-CN.md
    * summary.md
    * metadata.yaml
    * scripts/check_translation_residue.py
    * config/translation_residue_allowlist.yaml
    * unrelated reports
* **modified files**:
    * reports/translation_residue_triage_v0347_20260627.md

---

## 4. Inputs

### For import tasks:

* **source URL**: N/A — not an import task
* **short command**: N/A — quality-gate triage
* **content directory**: N/A — no content directory created
* **duplicate check**: N/A — no import attempted
* **blocked check**: N/A — no external fetch attempted
* **GitHub Pages URL**: https://conanxin.github.io/hermes-knowledge-base/

### For feature tasks:

* **feature target**: translation residue triage
* **modified scripts/docs**: none
* **generated files**: none
* **modified files**:
    * reports/translation_residue_triage_v0347_20260627.md

---

## 5. Checks

| Script | Result |
|---|---|
| `check_task_preflight.py` | **FAIL** (expected: dirty tree from staged report during task) |
| `check_release_tags.py` | **PASS_WITH_WARNINGS** (v0.3.36 known exception) |
| `check_kb.py` | **PASS** (47/47) |
| `check_tracks.py` | **PASS** (38 verified, 12 needs) |
| `update_site.py` | **PASS** (5/5, no diff) |
| `check_pages_sync.py` | **PASS** |
| `check_translation_residue.py` | **WARNING** (25 real residue + 1 allowlisted) — expected, triage-only |

---

## 6. Smoke Tests

* **local smoke**: N/A — report-only triage, no site UI changes
* **online smoke**: N/A — report-only triage, no site UI changes
* **pages URL**: https://conanxin.github.io/hermes-knowledge-base/
* **GitHub Pages URL**: https://conanxin.github.io/hermes-knowledge-base/

---

## 7. Postflight

To be run after commit/tag:

```bash
python3 scripts/check_task_postflight.py \
    --report reports/translation_residue_triage_v0347_20260627.md \
    --tag v0.3.47-translation-residue-triage \
    --expect-clean --expect-head-origin
```

**Expected**:
* **check_task_postflight.py**: PASS
* **postflight status**: PASS
* **warnings**: 0
* **tag deref**: final v0.3.47 commit
* **tag deref commit**: final v0.3.47 commit
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
* **known warning**: `check_translation_residue.py` still reports WARNING because this task is triage-only, not fix
* **reason**: 25 articles have real residue that needs future targeted fixes
* **action**: no action for this round; follow-up tasks will address based on priority

---

## 10. Next Version

* **recommended next minor**: expected v0.3.48 after tag creation
* **next suggested task**: targeted translation residue fixes based on P0/P1 priority list from this triage

---

## 11. Translation Residue Triage

### Before

* **Command**: `python3 scripts/check_translation_residue.py`
* **Total files scanned**: 29
* **Files with warnings**: 26
* **Total suspicious warnings**: 25 real + 1 allowlisted (jasmi)

### Triage Table

| # | Path | Token / Pattern | Context | Classification | Reason | Recommended Action |
|---|---|---|---|---|---|---|
| 1 | palantir-philosophy-weigel-burton | The Philosophy Behind Palantir | Title in metadata | proper_noun_ok | Video title, proper noun | no_change |
| 2 | palantir-philosophy-weigel-burton | New York Magazine | Publication name in text | proper_noun_ok | Publication name, proper noun | no_change |
| 3 | palantir-philosophy-weigel-burton | From Counterculture to Cyberculture | Book title in text | proper_noun_ok | Book title by Fred Turner, proper noun | no_change |
| 4 | palantir-philosophy-weigel-burton | Ludwig von Mises | Economist name in text | proper_noun_ok | Austrian economist name, proper noun | no_change |
| 5 | palantir-philosophy-weigel-burton | Musks with Quinn | Book title in text | proper_noun_ok | Book title by Ben Tarnoff, proper noun | no_change |
| 6 | conan-harvard-commencement-2026 | Brien Delivers the Commencement Address | Title in metadata | proper_noun_ok | Video title, proper noun | no_change |
| 7 | 421news-the-people-are-never-right | The People Are Never Right by Juan Ruocco | Title in text | proper_noun_ok | Article title, proper noun | no_change |
| 8 | 421news-the-people-are-never-right | Lady Astor | Person name in text | proper_noun_ok | Historical figure name, proper noun | no_change |
| 9 | 421news-the-people-are-never-right | Black Lives Matter | Movement name in text | proper_noun_ok | Social movement name, proper noun | no_change |
| 10 | 421news-the-people-are-never-right | Costin Alamariu aka Bronze Age Pervert | Person name in text | proper_noun_ok | Author/persona name, proper noun | no_change |
| 11 | 421news-the-people-are-never-right | great replacement theory | Theory name in text | proper_noun_ok | Political theory name, proper noun | no_change |
| 12 | theconvivialsociety-owning-our-words | North Point Press | Publisher in footnote | citation_or_url_ok | Publisher name in citation | no_change |
| 13 | theconvivialsociety-owning-our-words | Herder and Herder | Publisher in footnote | citation_or_url_ok | Publisher name in citation | no_change |
| 14 | chatgptpro-tyler-cowen-infovore | shares his chats | HTML comment | script_false_positive | Inside HTML comment, not visible text | improve_script_rule_in_followup |
| 15 | chatgptpro-tyler-cowen-infovore | ChatGPT Pro Community | HTML comment | script_false_positive | Inside HTML comment, not visible text | improve_script_rule_in_followup |
| 16 | chatgptpro-tyler-cowen-infovore | Conversations with Tyler | Podcast name in text | proper_noun_ok | Podcast name, proper noun | no_change |
| 17 | chatgptpro-tyler-cowen-infovore | Detroit Institute of Arts | Museum name in text | proper_noun_ok | Museum name, proper noun | no_change |
| 18 | paste-greatest-songs-1960s | greatest songs of the | HTML comment | script_false_positive | Inside HTML comment, not visible text | improve_script_rule_in_followup |
| 19 | paste-greatest-songs-1960s | Second That Emotion | Song title in text | proper_noun_ok | Song title, proper noun | no_change |
| 20 | paste-greatest-songs-1960s | Stoned Soul Picnic | Song title in text | proper_noun_ok | Song title, proper noun | no_change |
| 21 | paste-greatest-songs-1960s | stoned soul picnic | Song title in text | proper_noun_ok | Song title, proper noun | no_change |
| 22 | paste-greatest-songs-1960s | The Fifth Dimension | Artist name in text | proper_noun_ok | Artist name, proper noun | no_change |
| 23 | jr-logo-japan-railways | Telegraph and Telephone | Company name in text | proper_noun_ok | Company name (Nippon Telegraph and Telephone), proper noun | no_change |
| 24 | how-i-write-andrew-stanton | Chevron with Techron | Ad slogan in text | proper_noun_ok | Brand slogan, proper noun | no_change |
| 25 | how-i-write-andrew-stanton | leads up to that change | English phrase in text | needs_translation_fix — P2 | English idiom in translated paragraph | fix_translation_in_followup |
| 26 | how-i-write-andrew-stanton | fall into place | English phrase in text | needs_translation_fix — P2 | English idiom in translated paragraph | fix_translation_in_followup |
| 27 | how-i-write-andrew-stanton | kicks me into gear | English phrase in text | needs_translation_fix — P2 | English idiom in translated paragraph | fix_translation_in_followup |
| 28 | how-i-write-andrew-stanton | see things through | English phrase in text | needs_translation_fix — P2 | English idiom in translated paragraph | fix_translation_in_followup |
| 29 | oneusefulthing-sign-of-the-future-gpt-55 | Alain de Botton | Author name in text | proper_noun_ok | Author name, proper noun | no_change |
| 30 | dont-dethrone-consciousness-erik-hoel | Prince of the Apostles | Title in text | proper_noun_ok | Religious title, proper noun | no_change |
| 31 | dont-dethrone-consciousness-erik-hoel | philosophy of mind | Academic term in text | proper_noun_ok | Academic discipline name, proper noun | no_change |
| 32 | dont-dethrone-consciousness-erik-hoel | Folk psychological attributions... | Academic paper title | proper_noun_ok | Academic paper title, proper noun | no_change |
| 33 | dont-dethrone-consciousness-erik-hoel | Integrated Information Theory | Theory name in text | proper_noun_ok | Scientific theory name, proper noun | no_change |
| 34 | dont-dethrone-consciousness-erik-hoel | Global Workspace Theory | Theory name in text | proper_noun_ok | Scientific theory name, proper noun | no_change |
| 35 | tandf-us-structural-power | Sean Kenji Starrs | Author name in text | proper_noun_ok | Author name, proper noun | no_change |
| 36 | tandf-us-structural-power | Robert Hunter Wade | Author name in text | proper_noun_ok | Author name, proper noun | no_change |
| 37 | tandf-us-structural-power | Review of International Political Economy | Journal name in text | proper_noun_ok | Journal name, proper noun | no_change |
| 38 | tandf-us-structural-power | Hickel and Sullivan | Author names in text | proper_noun_ok | Author names, proper noun | no_change |
| 39 | tandf-us-structural-power | Slabaugh and Starrs | Author names in text | proper_noun_ok | Author names, proper noun | no_change |
| 40 | second-axial-age-otto-scharmer | We May Be Entering | Title in metadata | proper_noun_ok | Source title, proper noun | no_change |
| 41 | second-axial-age-otto-scharmer | Second Axial Age | Concept name in text | proper_noun_ok | Concept name, proper noun | no_change |
| 42 | second-axial-age-otto-scharmer | based systems change | Academic term in text | proper_noun_ok | Academic term, proper noun | no_change |
| 43 | second-axial-age-otto-scharmer | Johann Wolfgang von Goethe | Person name in text | proper_noun_ok | Person name, proper noun | no_change |
| 44 | second-axial-age-otto-scharmer | Highlander Folk School | Institution name in text | proper_noun_ok | Institution name, proper noun | no_change |
| 45 | vulture-spielberg-oral-history | earned my way through | English phrase in text | needs_translation_fix — P2 | English idiom in translated paragraph | fix_translation_in_followup |
| 46 | vulture-spielberg-oral-history | sort of shut it down | English phrase in text | needs_translation_fix — P2 | English phrase in translated paragraph | fix_translation_in_followup |
| 47 | vulture-spielberg-oral-history | just spilled that line out | English phrase in text | needs_translation_fix — P2 | English phrase in translated paragraph | fix_translation_in_followup |
| 48 | vulture-spielberg-oral-history | early in the shoot | English phrase in text | needs_translation_fix — P2 | English phrase in translated paragraph | fix_translation_in_followup |
| 49 | chinatalk-ken-liu-ai-freedom | All That We See or Seem | Book title in text | proper_noun_ok | Book title, proper noun | no_change |
| 50 | chinatalk-ken-liu-ai-freedom | Game Boy Advance | Product name in text | proper_noun_ok | Product name, proper noun | no_change |
| 51 | dario-amodei-bloomberg-interview | Inside the Mind of Anthropic CEO Dario Amodei | Title in metadata | proper_noun_ok | Video title, proper noun | no_change |
| 52 | dario-amodei-bloomberg-interview | Anthropic CEO Dario Amodei | Person name in text | proper_noun_ok | Person name, proper noun | no_change |
| 53 | dario-amodei-bloomberg-interview | Race to the Top | Section title in text | proper_noun_ok | Section title, proper noun | no_change |
| 54 | dario-amodei-bloomberg-interview | balance of power | English phrase in text | needs_translation_fix — P2 | English phrase in translated paragraph | fix_translation_in_followup |
| 55 | dario-amodei-bloomberg-interview | checks and balances | English phrase in text | needs_translation_fix — P2 | English phrase in translated paragraph | fix_translation_in_followup |
| 56 | reverse-game-theory-housing-shortage | Transferable Development Rights | Technical term in text | proper_noun_ok | Technical term, proper noun | no_change |
| 57 | emilycampbell-layers-of-ai-experience | The Layers of AI experience | Title in metadata | proper_noun_ok | Article title, proper noun | no_change |
| 58 | emilycampbell-layers-of-ai-experience | Jesse James Garrett | Person name in text | proper_noun_ok | Person name, proper noun | no_change |
| 59 | emilycampbell-layers-of-ai-experience | The Elements of User Experience | Book title in text | proper_noun_ok | Book title, proper noun | no_change |
| 60 | emilycampbell-layers-of-ai-experience | The Elements of Product Design | Book title in text | proper_noun_ok | Book title, proper noun | no_change |
| 61 | emilycampbell-layers-of-ai-experience | The Layers of AI Experience | Article title in text | proper_noun_ok | Article title, proper noun | no_change |
| 62 | youtube-video-brief-workflow | YouTube Video Brief | Workflow name in text | proper_noun_ok | Workflow name, proper noun | no_change |
| 63 | youtube-video-brief-workflow | Hermes Knowledge Base | Project name in text | proper_noun_ok | Project name, proper noun | no_change |
| 64 | noema-how-ai-will-change-us | How AI Will Change Us | Title in metadata | proper_noun_ok | Article title, proper noun | no_change |
| 65 | noema-how-ai-will-change-us | Houda Nait El Barj researcher at OpenAI | Author name in metadata | proper_noun_ok | Author name, proper noun | no_change |
| 66 | noema-how-ai-will-change-us | Thrownness Meets Abundance | Section title in text | proper_noun_ok | Section title, proper noun | no_change |
| 67 | noema-how-ai-will-change-us | Houda Nait El Barj | Author name in text | proper_noun_ok | Author name, proper noun | no_change |
| 68 | youtube-kb-import-command | YouTube Video KB Import | Command name in text | proper_noun_ok | Command name, proper noun | no_change |
| 69 | youtube-kb-import-command | YouTube Video Brief | Workflow name in text | proper_noun_ok | Workflow name, proper noun | no_change |
| 70 | youtube-kb-import-command | check translation residue | Command name in text | proper_noun_ok | Command name, proper noun | no_change |
| 71 | youtube-link-preflight-failure-archive | YouTube Link Preflight | Command name in text | proper_noun_ok | Command name, proper noun | no_change |
| 72 | youtube-link-preflight-failure-archive | live not started | Status text in text | proper_noun_ok | Status message, proper noun | no_change |
| 73 | youtube-link-preflight-failure-archive | metadata fetch failed | Status text in text | proper_noun_ok | Status message, proper noun | no_change |
| 74 | youtube-link-preflight-failure-archive | Hermes Knowledge Base | Project name in text | proper_noun_ok | Project name, proper noun | no_change |
| 75 | your-ai-is-not-a-tool | The Convivial Society | Publication name in text | proper_noun_ok | Publication name, proper noun | no_change |
| 76 | your-ai-is-not-a-tool | The Emergence of | Article title in text | proper_noun_ok | Article title, proper noun | no_change |
| 77 | your-ai-is-not-a-tool | The McLuhan Newsletter | Publication name in text | proper_noun_ok | Publication name, proper noun | no_change |
| 78 | your-ai-is-not-a-tool | Tools for Conviviality | Book title in text | proper_noun_ok | Book title, proper noun | no_change |
| 79 | your-ai-is-not-a-tool | The Loss of the Senses | Book title in text | proper_noun_ok | Book title, proper noun | no_change |
| 80 | how-i-write-andrew-hunter-murray | Guide to Breaking and Entering | Book title in text | proper_noun_ok | Book title, proper noun | no_change |
| 81 | how-i-write-andrew-hunter-murray | Breaking and Entering | Book title in text | proper_noun_ok | Book title, proper noun | no_change |
| 82 | how-i-write-andrew-hunter-murray | No Such Thing as | Podcast name in text | proper_noun_ok | Podcast name, proper noun | no_change |
| 83 | ai-unconscious-convivial-society | The Convivial Society | Publication name in text | proper_noun_ok | Publication name, proper noun | no_change |
| 84 | ai-unconscious-convivial-society | Erik Hoel source | Author name in text | proper_noun_ok | Author name, proper noun | no_change |
| 85 | ai-unconscious-convivial-society | without our understanding | English phrase in text | needs_translation_fix — P2 | English phrase in translated paragraph | fix_translation_in_followup |
| 86 | ai-unconscious-convivial-society | set outside himself | English phrase in text | needs_translation_fix — P2 | English phrase in translated paragraph | fix_translation_in_followup |
| 87 | ai-unconscious-convivial-society | less than sanguine | English phrase in text | needs_translation_fix — P2 | English phrase in translated paragraph | fix_translation_in_followup |
| 88 | thoreau-civil-disobedience | Resistance to Civil Government | Original title in text | proper_noun_ok | Original title, proper noun | no_change |
| 89 | thoreau-civil-disobedience | Henry David Thoreau | Author name in text | proper_noun_ok | Author name, proper noun | no_change |

### Classification Summary

| Classification | Count | Percentage |
|---|---|---|
| **proper_noun_ok** | 72 | 80.9% |
| **citation_or_url_ok** | 2 | 2.2% |
| **needs_translation_fix — P2** | 15 | 16.9% |
| **needs_allowlist** | 0 | 0% |
| **script_false_positive** | 4 | 4.5% |
| **Total** | 89 | 100% |

### Priority Breakdown

| Priority | Count | Articles Affected |
|---|---|---|
| **P0** (obvious large omission) | 0 | none |
| **P1** (short sentence/title omission) | 0 | none |
| **P2** (minor style/idiom) | 15 | andrew-stanton (4), vulture-spielberg (4), dario-amodei (2), ai-unconscious (3), how-i-write-andrew-hunter-murray (2) |

### Top Priority Fixes

1. **how-i-write-andrew-stanton**: 4 English idioms (`leads up to that change`, `fall into place`, `kicks me into gear`, `see things through`) — P2
2. **vulture-spielberg-oral-history**: 4 English phrases (`earned my way through`, `sort of shut it down`, `just spilled that line out`, `early in the shoot`) — P2
3. **ai-unconscious-convivial-society**: 3 English phrases (`without our understanding`, `set outside himself`, `less than sanguine`) — P2
4. **dario-amodei-bloomberg-interview**: 2 English phrases (`balance of power`, `checks and balances`) — P2
5. **how-i-write-andrew-hunter-murray**: 2 English phrases (`Guide to Breaking and Entering`, `No Such Thing as`) — P2 (but these are book/podcast titles, actually proper_noun_ok)

### Confirmation

* **No content files were modified**: ✅
* **No allowlist was changed**: ✅
* **check_translation_residue.py was not modified**: ✅
* **All triage was read-only**: ✅

---

*Report generated: 2026-06-27*
