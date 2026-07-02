# Material Ingestion Stable Baseline Release
## v0.3.91 · 2026-07-02

---

## STATUS: PASS

---

## baseline commit

| | 值 |
|---|---|
| Branch | `main` |
| Pre-tag commit | `f309cb6` (previous full-gate audit) |
| **Final tag commit** | **`56fe848`** (Document material ingestion stable baseline) |
| Tag | `v0.3.91-material-ingestion-stable-baseline` |
| Tag type | annotated |
| Pushed to origin | ✅ success (`f309cb6..56fe848  main -> main` + new tag push) |

> **Note on commit/tag split**: Per the task instruction "如果报告也要提交，请在 tag 前提交报告；如果 tag 已创建后才生成报告，则不要强行改 tag，报告可留待下一版本", we did the safer order: docs commit first (`56fe848`), then tag that final commit, then this report (left in tree but not required to commit before tag — task allows it can be left for next version).

---

## tag name

```
v0.3.91-material-ingestion-stable-baseline
```

Tag message:
> Material ingestion stable baseline: WeChat, web, YouTube transcript-gated, local files, PDF

---

## supported material matrix

| Material | 能力 | Status |
|----------|------|--------|
| 微信公众号 URL | 公开 URL 直抓 + 本地文件兜底（不登录、不扫码、不读 cookie） | ✅ supported |
| 普通网页 URL | material_to_kb.py → web_article_to_kb.py | ✅ supported |
| YouTube URL (有 transcript) | 字幕/转录稿入库 | ✅ supported |
| YouTube URL (无 transcript) | BLOCKED + archived | 🛑 BLOCKED |
| 本地 HTML / MD / TXT | material_to_kb.py 本地文件入口 | ✅ supported |
| 本地 PDF (文本层) | material_to_kb.py → pdf_to_kb.py (PyMuPDF) | ✅ supported |
| 本地 PDF (扫描版) | BLOCKED_NEEDS_OCR 不入库、不内置 OCR | 🛑 BLOCKED_NEEDS_OCR |
| 图片本地化 | 公众号 / 网页 / 本地 文件均支持 | ✅ supported |

---

## release gate results

| Gate | 状态 | 详情 |
|------|------|------|
| `tests/run_material_router_smoke.py` | **PASS** | 4/4 |
| `tests/run_pdf_import_smoke.py` | **PASS** | **33/33** |
| `tests/run_youtube_import_smoke.py` | **PASS** | 14/14 |
| `scripts/check_kb.py` | **PASS** | 65 items, FAIL: 0 |
| `scripts/check_pages_sync.py` | **PASS** | site ↔ docs synced |

---

## docs updated

| File | Change |
|------|--------|
| `CHANGELOG.md` | Added v0.3.91 entry at top with stable baseline info, material matrix, hard guarantees |
| `docs/RELEASES.md` | Added row in version map; added full release-line row; added new "Material Ingestion Stable Baseline" capability section; added "Use material ingestion on a new machine" entry in "How to Pick a Version" table |
| `README.md` | Added 4 milestone rows (v0.3.86, v0.3.89, v0.3.90, v0.3.91) under "近期里程碑"; updated "Last refreshed" footer to v0.3.91 |

---

## commit hash

| Commit | Description |
|--------|-------------|
| `56fe848` | **Document material ingestion stable baseline** (this task; staged) |
| `f309cb6` | v0.3.91 full-gate clean reproducibility audit (pre-task baseline) |
| `b045a70` | v0.3.90 Stage D documentation (prior task) |
| `13d7d55` | Stage D regression check (prior task) |
| `def5a7f` | v0.3.90 main fix (prior task) |

---

## tag push result

```
To https://github.com/conanxin/hermes-knowledge-base.git
 * [new tag]         v0.3.91-material-ingestion-stable-baseline -> v0.3.91-material-ingestion-stable-baseline
```

✅ success.

---

## next development recommendations

1. **Tag-based releases in CI/CD**: 此后每个 release 都应走相同的"docs commit → tag → push tag → report"流程，docs commit 必须在 tag 之前完成。

2. **Audit warnings 36 → 0**: `audit_kb_state.py` 累计 36 个 WARN，建议下个 maintenance 版本（v0.3.92+）将 warnings 分类归零，避免淹没 HARD FAIL。

3. **v0.3.86 untracked reports 清理**: `reports/pdf_kb_import_v0.3.86_20260702.md` 和 `reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json` 仍是 untracked out-of-scope；可在后续 archive 任务 commit 或 ignore。

4. **下一个 stable baseline**: 建议在 YouTube 长 transcript 模板、自定义 YouTube channel 抓取、PDF OCR 真实集成（v0.4+）之一实现后，再做 v0.3.92+ stable baseline。

5. **新机器/后续 agent 恢复命令**（关键）：
   ```bash
   git clone https://github.com/conanxin/hermes-knowledge-base.git
   cd hermes-knowledge-base
   git fetch origin tag v0.3.91-material-ingestion-stable-baseline
   git checkout v0.3.91-material-ingestion-stable-baseline
   pip install pymupdf yt-dlp youtube-transcript-api
   python3 -m py_compile scripts/*.py
   python3 tests/run_smoke_tests.py
   python3 tests/run_wechat_batch_smoke.py
   python3 tests/run_item_render_smoke.py
   python3 tests/run_image_localization_smoke.py
   python3 tests/run_material_router_smoke.py
   python3 tests/run_web_article_smoke.py
   python3 tests/run_youtube_import_smoke.py
   python3 tests/run_fetch_layer_smoke.py
   python3 tests/run_pdf_import_smoke.py
   python3 scripts/check_kb.py
   python3 scripts/update_site.py
   python3 scripts/audit_kb_state.py
   python3 scripts/check_pages_sync.py
   # 预期: 14 个 gate 全 PASS, 0 tracked dirty, 0 smoke-only slug
   ```

---

*Release report generated: 2026-07-02 09:13 GMT+8*
*Stable baseline: v0.3.91-material-ingestion-stable-baseline @ `56fe848`*