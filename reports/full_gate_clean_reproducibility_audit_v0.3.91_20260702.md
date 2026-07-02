# Full Gate Clean + Reproducibility Audit
## v0.3.91 · 2026-07-02

---

## STATUS: PASS

---

## 当前 HEAD

| | 值 |
|---|---|
| local HEAD | `b045a70` |
| origin/main | `b045a70` (synced, 0 ahead / 0 behind) |

v0.3.90 三个 commit 已全部在 origin/main:
- `def5a7f` — pdf_to_kb.py fix (replace update_site.py with run_gates)
- `13d7d55` — Stage D regression check (7 new smoke_post checks)
- `b045a70` — Report update (Stage D documentation)

---

## Full Gate 结果

| Gate | 状态 | 详情 |
|------|------|------|
| `python -m py_compile scripts/*.py` | **PASS** | 全部 scripts/*.py 编译成功 |
| `python tests/run_smoke_tests.py` | **PASS** | 3/3 |
| `python tests/run_wechat_batch_smoke.py` | **PASS** | 5/5 |
| `python tests/run_item_render_smoke.py` | **PASS** | 6/6 |
| `python tests/run_image_localization_smoke.py` | **PASS** | 8/8 |
| `python tests/run_material_router_smoke.py` | **PASS** | 4/4 |
| `python tests/run_web_article_smoke.py` | **PASS** | 5/5 |
| `python tests/run_youtube_import_smoke.py` | **PASS** | 14/14 |
| `python tests/run_fetch_layer_smoke.py` | **PASS** | 6/6 |
| `python tests/run_pdf_import_smoke.py` | **PASS** | **33/33** |
| `python scripts/check_kb.py` | **PASS** | 65 items, FAIL: 0 |
| `python scripts/update_site.py` | **PASS** | all 5 steps OK |
| `python scripts/audit_kb_state.py` | **PASS_WITH_WARNINGS** | 36 warnings (non-blocking) |
| `python scripts/check_pages_sync.py` | **PASS** | site/docs synced |

---

## run_pdf_import_smoke.py 是否 33/33

**是。** smoke test 从 v0.3.90 的 26/26 升级到 33/33（+7 regression checks）。

新增的 7 个 smoke_post 检查：
- `smoke_post_no_smoke_slug_in__docs_data_catalog.json`
- `smoke_post_no_smoke_slug_in__site_data_catalog.json`
- `smoke_post_no_smoke_slug_in__index_catalog.jsonl`
- `smoke_post_no_smoke_slug_in__index_authors.md`
- `smoke_post_no_smoke_slug_in__index_tags.md`
- `smoke_post_no_smoke_slug_in__index_timeline.md`
- `smoke_post_git_diff_no_tracked_generated_dirty`

---

## Gate 后 Tracked Working Tree 是否 Clean

**是。**

```
git status --short:
?? reports/pdf_kb_import_v0.3.86_20260702.md
?? reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json

git diff --stat: (empty — 0 tracked dirty)
git diff --name-only: (empty — 0 tracked dirty)
```

仅有 2 个 untracked 报告文件（`reports/pdf_kb_import_v0.3.86_20260702.md`、`reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json`），均为 v0.3.86 遗留 formal reports，不在本次任务提交范围，符合 `.gitignore` 策略（v0.3.89 确立）。

---

## 是否出现 Smoke-Only Slug

**否。**

```
grep -r "hermes-knowledge-base-routing-capture" docs/data site/data index docs/items site/items content/articles
→ CLEAN (0 occurrences in all tracked + generated files)
```

---

## 是否出现 DRY_RUN_PREVIEW

**否。**

```
grep -r "DRY_RUN_PREVIEW" docs/data site/data index docs/items site/items content/articles
→ CLEAN (0 occurrences)
```

---

## 内容数量

| 维度 | 数量 |
|------|------|
| `content/articles/` 下的 metadata.yaml | 47 |
| `docs/items/` 数量 | 65 |
| `site/items/` 数量 | 65 |
| synced slugs（catalog.json records） | 65 |

---

## Audit Warnings

`audit_kb_state.py`: **PASS_WITH_WARNINGS（36 warnings）**

warnings 均为非阻塞性（如 article metadata 字段缺失可选属性、日期格式轻微偏差等），不影响 gate 通过。HARD FAIL = 0。

---

## Untracked Ignored Artifact 摘要

| 文件 | 来源 | 状态 |
|------|------|------|
| `reports/pdf_kb_import_v0.3.86_20260702.md` | v0.3.86 formal report | untracked, out of scope |
| `reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json` | v0.3.63 formal report | untracked, out of scope |

均不在本任务提交范围，符合 v0.3.89 `.gitignore` 策略。

---

## Git Diff 摘要

```
(empty — 0 tracked dirty after full gate)
```

---

## Commit Hash

N/A — 无代码变更，本次仅审计，未修改任何源码/测试/配置。

---

## Push 结果

N/A — 无代码变更，无需 push。

---

## 下一步建议

1. **v0.3.86 报告清理**：两个 v0.3.86 遗留 formal reports（`reports/pdf_kb_import_v0.3.86_20260702.md`、`reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json`）如已确认内容，可单独 commit 归档；如已过期，可 `.gitignore` 或删除。

2. **audit_kb_state 36 warnings 审查**：虽然是 non-blocking warnings，但 36 个积累量值得在下次维护窗口逐一分类处理，避免未来 HARD FAIL 淹没在大量非关键 warnings 中。

3. **v0.3.91 无代码变更**：本次审计确认了 v0.3.90 修复的完整性，无需合并或回退任何 commit。

---

*Audit generated: 2026-07-02 08:53 GMT+8*
*Auditor: OpenClaw agent (hermes-knowledge-base v0.3.91 task)*
*Local HEAD: b045a70 | origin/main: b045a70 | Synced: yes*