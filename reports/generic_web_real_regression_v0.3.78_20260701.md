# Generic Web Real Regression v0.3.78

- STATUS: BLOCKED
- Task: `v0.3.78-generic-web-real-regression`
- Date: 2026-07-01
- Branch: `main`
- Base HEAD / origin/main: `2ec5b04acc089dc58c95d2d8faa6366ade6887c5`

## Summary

The real regression used the three user-provided ordinary web URLs. The unified router correctly recognized all three as `generic_web_url` and routed all three to `web_article_to_kb.py`.

All three were blocked by `robots.txt`, so no import was attempted. This is the expected safety behavior for v0.3.77/v0.3.78: the route must not bypass robots, login, paywall, cookie, or JS access restrictions and must not write half-complete KB entries.

## Input URLs

```text
https://holo.substack.com/p/the-development-of-mind-and-society
https://theconvivialsociety.substack.com/p/your-ai-is-not-a-tool
https://www.chinatalk.media/p/ken-liu-on-ai-and-freedom
```

Input list file:

```text
tmp/web_real_regression_urls_20260701.txt
```

## Dry-Run Result

Command:

```bash
python scripts/material_to_kb.py --input-list tmp/web_real_regression_urls_20260701.txt --dry-run
```

Router reports:

- Markdown: `reports/material_import_20260701_154223.md`
- JSON: `reports/material_import_20260701_154223.json`

Summary:

- total: 3
- imported: 0
- dry_run_ok: 0
- skipped_duplicate: 0
- blocked_unsupported: 3
- blocked_fetch_failed: 0
- blocked_incomplete_text: 0
- failed_import: 0
- failed_gate: 0

## Import Result

Import was skipped because dry-run produced 0 `DRY_RUN_OK` items.

No KB entries were created. No item pages were regenerated. No existing `summary.md` or `notes.md` files were touched.

## Per-Article Results

| input | inferred_type | route | status | title | source_site | author | published_date | source_url | canonical_url | kb_article_path | docs_item_path | site_item_path | duplicate_of | failure_reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `https://holo.substack.com/p/the-development-of-mind-and-society` | `generic_web_url` | `web_article_to_kb.py` | `BLOCKED_UNSUPPORTED` |  |  |  |  |  |  |  |  |  |  | `robots.txt disallows fetching https://holo.substack.com/p/the-development-of-mind-and-society` |
| `https://theconvivialsociety.substack.com/p/your-ai-is-not-a-tool` | `generic_web_url` | `web_article_to_kb.py` | `BLOCKED_UNSUPPORTED` |  |  |  |  |  |  |  |  |  |  | `robots.txt disallows fetching https://theconvivialsociety.substack.com/p/your-ai-is-not-a-tool` |
| `https://www.chinatalk.media/p/ken-liu-on-ai-and-freedom` | `generic_web_url` | `web_article_to_kb.py` | `BLOCKED_UNSUPPORTED` |  |  |  |  |  |  |  |  |  |  | `robots.txt disallows fetching https://www.chinatalk.media/p/ken-liu-on-ai-and-freedom` |

## Imported Articles

None.

## Blocked Articles

- `https://holo.substack.com/p/the-development-of-mind-and-society`: `robots.txt` disallowed fetch.
- `https://theconvivialsociety.substack.com/p/your-ai-is-not-a-tool`: `robots.txt` disallowed fetch.
- `https://www.chinatalk.media/p/ken-liu-on-ai-and-freedom`: `robots.txt` disallowed fetch.

## Duplicate Check

Skipped because no ordinary web article was imported in this regression run.

## Page Render Check

No new web article item pages were generated. Baseline checks still pass:

- `python scripts/check_kb.py`: PASS, 61/61
- `python scripts/check_pages_sync.py`: PASS, 61 slugs

No published item count decreased.

## Counts

- content metadata total: 61
- docs/items: 61
- site/items: 61
- synced slugs: 61

## Gates

Full import gates were not run because there were 0 real imports.

Read-only baseline checks run:

- `python scripts/check_kb.py`: PASS
- `python scripts/check_pages_sync.py`: PASS

Preflight note:

- `python scripts/check_task_preflight.py --planned-tag v0.3.78-generic-web-real-regression --classify-dirty --json` returned FAIL because the workspace contains pre-existing untracked smoke/report artifacts.
- No unrelated tracked dirty changes were present.
- HEAD and origin/main were synced at `2ec5b04acc089dc58c95d2d8faa6366ade6887c5`.

## Git Diff Summary

No tracked content/site/script changes were made.

Untracked files created by this regression:

- `tmp/web_real_regression_urls_20260701.txt`
- `reports/material_import_20260701_154223.md`
- `reports/material_import_20260701_154223.json`
- `reports/generic_web_real_regression_v0.3.78_20260701.md`

Existing untracked artifacts under `inbox/raw/` and `reports/` were preserved and not deleted.

## Commit And Push

- Commit hash: N/A
- Push result: N/A
- Reason: 0 articles imported, so no commit/push per task rule.

## Next Steps

- Choose 3-5 ordinary web URLs whose `robots.txt` permits public fetches for a true import regression.
- Keep these three URLs recorded as a useful negative test for robots-safe blocking behavior.
