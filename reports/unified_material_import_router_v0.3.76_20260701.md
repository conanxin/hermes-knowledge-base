# Unified Material Import Router v0.3.76

- STATUS: PASS
- Task: `v0.3.76-unified-material-kb-import-router`
- Date: 2026-07-01
- Branch: `main`
- Base before v0.3.76 work: `490c34191f09c169b10704562be3901682fc8017`
- Origin before v0.3.76 work: `490c34191f09c169b10704562be3901682fc8017`

## Phase 0

- v0.3.75a report committed: yes
- Report file: `reports/wechat_summary_image_live_verification_v0.3.75a_20260701.md`
- Commit: `490c34191f09c169b10704562be3901682fc8017`
- Push: success

## Dirty / Artifact Handling

Preflight for v0.3.76 reported existing untracked artifacts. No tracked dirty changes were present before v0.3.76 edits.

Kept untracked and not committed:

- `AGENTS.md`
- `inbox/raw/wechat/2026-06-30-*.json` (17 files after smoke runs)
- `inbox/raw/wechat/2026-07-01-*.json` (11 files after smoke runs)
- `reports/wechat_batch_import_20260701_*.md/json` (14 JSON manifests plus matching markdown reports after smoke runs)
- `reports/material_import_20260701_150445.*`
- `reports/material_import_20260701_150446.*`
- `reports/material_import_20260701_150809.*`
- `reports/material_import_20260701_150810.*`

These are WorkBuddy/test artifacts or dry-run smoke reports and were intentionally left untracked.

## Existing Import Capability Inventory

| Material type | Repository evidence | v0.3.76 router status |
|---|---|---|
| WeChat Official Account URL | `scripts/wechat_url_to_kb.py`, `scripts/wechat_batch_import.py`, `docs/commands/wechat-url-kb-import-command.md`, `docs/commands/wechat-batch-kb-import-command.md` | supported |
| WeChat saved HTML / Markdown / TXT | `wechat_url_to_kb.py` local file mode and batch local file support | supported |
| YouTube URL | docs/workflows exist, but no stable URL import script under `scripts/` | `BLOCKED_UNSUPPORTED` |
| Generic web URL | no stable generic web article import script found | `BLOCKED_UNSUPPORTED` |
| Local PDF | docs/workflows exist, but no stable PDF/OCR import script under `scripts/` | `BLOCKED_UNSUPPORTED` |

## New Unified Entry

Added `scripts/material_to_kb.py`.

Supported commands:

```bash
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --dry-run
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --import
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --import
```

`--dry-run` is the default safe mode. Each run writes:

- `reports/material_import_YYYYMMDD_HHMMSS.md`
- `reports/material_import_YYYYMMDD_HHMMSS.json`

## Route Rules

| inferred_type | Match | Route | Notes |
|---|---|---|---|
| `wechat_url` | `mp.weixin.qq.com`, `weixin.qq.com` | single input: `wechat_url_to_kb.py`; multi input: `wechat_batch_import.py` | preserves dry-run/import, dedup, capture, manifest, and post-import localization/gates |
| `local_text_article` | `.html`, `.htm`, `.md`, `.markdown`, `.txt` | WeChat local file mode | report marks `route: wechat_url_to_kb.py local file mode` |
| `youtube_url` | `youtube.com`, `youtu.be` | unsupported | reason: `YouTube import route not implemented yet in unified router` |
| `generic_web_url` | other HTTP(S) URLs | unsupported | reason: `generic web article import route not implemented yet` |
| `pdf_file` | local `.pdf` | unsupported | reason: `PDF import/OCR route not implemented yet` |

## Tests

Added:

- `tests/run_material_router_smoke.py`
- `tests/fixtures/material_inputs_mixed.txt`

Coverage:

- WeChat URL inference.
- Local HTML inference.
- Local Markdown inference.
- YouTube unsupported status and reason.
- Generic web unsupported status and reason.
- PDF unsupported status and reason.
- input-list blank/comment skipping.
- dry-run keeps KB metadata count unchanged.
- mixed batch continues after `BLOCKED_UNSUPPORTED`.
- markdown and JSON material reports are generated.
- existing generated HTML has no remote `mmbiz.qpic.cn`.

Representative router dry-run reports:

- Markdown: `reports/material_import_20260701_150809.md`
- JSON: `reports/material_import_20260701_150809.json`

## Gates

| Gate | Result |
|---|---|
| `python -m py_compile scripts/*.py` | PASS |
| `python tests/run_smoke_tests.py` | PASS |
| `python tests/run_wechat_batch_smoke.py` | PASS |
| `python tests/run_item_render_smoke.py` | PASS |
| `python tests/run_image_localization_smoke.py` | PASS |
| `python tests/run_material_router_smoke.py` | PASS |
| `python scripts/check_kb.py` | PASS, 61/61 |
| `python scripts/update_site.py` | PASS |
| `python scripts/audit_kb_state.py` | PASS_WITH_WARNINGS, 28 existing tag/topic soft-range warnings, 0 hard failures |
| `python scripts/check_pages_sync.py` | PASS, 61 slugs |

## Counts

- `content/articles` metadata count: 43
- total `content/**/metadata.yaml` count: 61
- `docs/items` count: 61
- `site/items` count: 61
- synced slugs: 61

## Git Diff Summary

Tracked modified files before report:

- `README.md`: +3 / -1
- `docs/AGENT_COMMANDS.md`: +37 / -0
- `docs/commands/README.md`: +21 / -1
- `docs/workflows/README.md`: +16 / -1

New v0.3.76 files:

- `scripts/material_to_kb.py`: 468 lines
- `tests/run_material_router_smoke.py`: 204 lines
- `tests/fixtures/material_inputs_mixed.txt`: 7 lines
- `docs/commands/material-kb-import-command.md`: 94 lines
- `docs/workflows/material-kb-import-workflow.md`: 96 lines
- `reports/unified_material_import_router_v0.3.76_20260701.md`: this report

## Commit / Push

- Commit hash: pending; final response records the actual hash after commit.
- Push result: pending; final response records the actual push result.

## Next Steps

- Keep YouTube, generic web, and PDF routes blocked until stable scripts exist under `scripts/`.
- When adding a new stable importer, connect it through `material_to_kb.py` and extend `tests/run_material_router_smoke.py`.
- Consider ignoring or periodically cleaning dry-run smoke artifacts in a separate housekeeping task, with explicit approval.
