# Generic Web Real Regression Retry v0.3.78b

- STATUS: PASS
- Task: `v0.3.78b-generic-web-real-regression-retry`
- Date: 2026-07-01
- Branch: `main`
- Base HEAD / origin/main at start: `2ec5b04acc089dc58c95d2d8faa6366ade6887c5`

## Previous v0.3.78 Blocked Result

The previous v0.3.78 regression used:

- `https://holo.substack.com/p/the-development-of-mind-and-society`
- `https://theconvivialsociety.substack.com/p/your-ai-is-not-a-tool`
- `https://www.chinatalk.media/p/ken-liu-on-ai-and-freedom`

All three were correctly recognized as `generic_web_url` and routed to `web_article_to_kb.py`, but all three were blocked because `robots.txt` disallowed fetch. No import was attempted and no half-entry was written.

## This Run Inputs

Input file:

```text
tmp/web_real_regression_urls_20260701_retry.txt
```

URLs:

- `https://www.paulgraham.com/read.html`
- `https://www.nngroup.com/articles/ten-usability-heuristics/`
- `https://martinfowler.com/articles/is-quality-worth-cost.html`
- `https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/`

## Robots Check

All four selected URLs were checked before the router dry-run.

| URL | robots result | HTTP status | content type |
|---|---|---:|---|
| `https://www.paulgraham.com/read.html` | allowed | 200 | `text/html` |
| `https://www.nngroup.com/articles/ten-usability-heuristics/` | allowed | 200 | `text/html; charset=utf-8` |
| `https://martinfowler.com/articles/is-quality-worth-cost.html` | allowed | 200 | `text/html` |
| `https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/` | allowed | 200 | `text/html; charset=UTF-8` |

Rejected during candidate selection:

- `https://blog.codinghorror.com/the-magpie-developer/`: robots disallowed.
- `https://fs.blog/circle-of-competence/`: robots disallowed.
- `https://www.aaronsw.com/weblog/productivity`: robots fetch failed due TLS handshake error, so it was not used.

## Dry-Run Result

Command:

```bash
python scripts/material_to_kb.py --input-list tmp/web_real_regression_urls_20260701_retry.txt --dry-run
```

Router reports:

- Markdown: `reports/material_import_20260701_154742.md`
- JSON: `reports/material_import_20260701_154742.json`

Summary:

- total: 4
- dry_run_ok: 4
- skipped_duplicate: 0
- blocked_unsupported: 0
- blocked_fetch_failed: 0
- blocked_incomplete_text: 0
- failed_import: 0
- failed_gate: 0

## Import Result

Command:

```bash
python scripts/material_to_kb.py --input-list tmp/web_real_regression_urls_20260701_retry.txt --import
```

Router reports:

- Markdown: `reports/material_import_20260701_154809.md`
- JSON: `reports/material_import_20260701_154809.json`

Summary:

- total: 4
- imported: 4
- skipped_duplicate: 0
- blocked_unsupported: 0
- blocked_fetch_failed: 0
- blocked_incomplete_text: 0
- failed_import: 0
- failed_gate: 0

Note: the router JSON's `docs_item_path` / `site_item_path` fields include an awkward absolute-path fragment inherited from the downstream output parser. The actual generated pages were checked by slug and are correct in both `docs/items/` and `site/items/`.

## Per-Article Results

| input | inferred_type | route | status | title | source_site | author | published_date | source_url | canonical_url | kb_article_path | docs_item_path | site_item_path | duplicate_of | failure_reason |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `https://www.paulgraham.com/read.html` | `generic_web_url` | `web_article_to_kb.py` | `IMPORTED` | The Need to Read | www.paulgraham.com | Unknown |  | `https://www.paulgraham.com/read.html` | `https://www.paulgraham.com/read.html` | `content/articles/2026/2026-07-01-web-wwwpaulgrahamcom-the-need-to-read` | `docs/items/2026-07-01-web-wwwpaulgrahamcom-the-need-to-read/index.html` | `site/items/2026-07-01-web-wwwpaulgrahamcom-the-need-to-read/index.html` |  |  |
| `https://www.nngroup.com/articles/ten-usability-heuristics/` | `generic_web_url` | `web_article_to_kb.py` | `IMPORTED` | 10 Usability Heuristics for User Interface Design | Nielsen Norman Group | Jakob Nielsen | 1994-04-24 | `https://www.nngroup.com/articles/ten-usability-heuristics/` | `https://www.nngroup.com/articles/ten-usability-heuristics/` | `content/articles/1994/1994-04-24-web-nielsen-norman-group-10-usability-heuristics-for-user-interface-design` | `docs/items/1994-04-24-web-nielsen-norman-group-10-usability-heuristics-for-user-interface-design/index.html` | `site/items/1994-04-24-web-nielsen-norman-group-10-usability-heuristics-for-user-interface-design/index.html` |  |  |
| `https://martinfowler.com/articles/is-quality-worth-cost.html` | `generic_web_url` | `web_article_to_kb.py` | `IMPORTED` | Is High Quality Software Worth the Cost? | martinfowler.com | Unknown |  | `https://martinfowler.com/articles/is-quality-worth-cost.html` | `https://martinfowler.com/articles/is-quality-worth-cost.html` | `content/articles/2026/2026-07-01-web-martinfowlercom-is-high-quality-software-worth-the-cost` | `docs/items/2026-07-01-web-martinfowlercom-is-high-quality-software-worth-the-cost/index.html` | `site/items/2026-07-01-web-martinfowlercom-is-high-quality-software-worth-the-cost/index.html` |  |  |
| `https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/` | `generic_web_url` | `web_article_to_kb.py` | `IMPORTED` | Things You Should Never Do, Part I | Joel on Software | Unknown | 2000-04-06 | `https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/` | `https://www.joelonsoftware.com/2000/04/06/things-you-should-never-do-part-i/` | `content/articles/2000/2000-04-06-web-joel-on-software-things-you-should-never-do-part-i` | `docs/items/2000-04-06-web-joel-on-software-things-you-should-never-do-part-i/index.html` | `site/items/2000-04-06-web-joel-on-software-things-you-should-never-do-part-i/index.html` |  |  |

## Imported Articles

- `content/articles/2026/2026-07-01-web-wwwpaulgrahamcom-the-need-to-read`
- `content/articles/1994/1994-04-24-web-nielsen-norman-group-10-usability-heuristics-for-user-interface-design`
- `content/articles/2026/2026-07-01-web-martinfowlercom-is-high-quality-software-worth-the-cost`
- `content/articles/2000/2000-04-06-web-joel-on-software-things-you-should-never-do-part-i`

Each imported article has:

- `metadata.yaml`
- `source.md`
- `translation.zh-CN.md`
- `summary.md`
- `notes.md`
- `raw_payload.json`

All four are English source articles, so `translation.zh-CN.md` is an explicit placeholder / needs-review draft, and `metadata.yaml` uses `status: "needs_translation_review"` with `is_translation_mirror: false`. The `summary.md` and `notes.md` files were manually completed enough for this regression and are not empty scaffolds.

## Blocked Articles

None in the selected retry input list.

## Duplicate Verification

Command:

```bash
python scripts/material_to_kb.py --input "https://www.paulgraham.com/read.html" --dry-run
```

Reports:

- Markdown: `reports/material_import_20260701_154854.md`
- JSON: `reports/material_import_20260701_154854.json`

Result:

- status: `SKIPPED_DUPLICATE`
- duplicate_of: `content/articles/2026/2026-07-01-web-wwwpaulgrahamcom-the-need-to-read`

## Page Render Check

Checked all four imported slugs in both `docs/items/` and `site/items/`.

- docs pages exist: 4/4
- site pages exist: 4/4
- raw Markdown image syntax in generated HTML: 0
- source/canonical URL trace visible in generated pages: 4/4
- docs/site byte sync: PASS

## Counts

- `content/articles` metadata count: 47
- total content metadata count: 65
- `docs/items`: 65
- `site/items`: 65
- synced slugs: 65

## Gates

- `python -m py_compile scripts/*.py`: PASS
- `python tests/run_smoke_tests.py`: PASS
- `python tests/run_wechat_batch_smoke.py`: PASS
- `python tests/run_item_render_smoke.py`: PASS
- `python tests/run_image_localization_smoke.py`: PASS
- `python tests/run_material_router_smoke.py`: PASS
- `python tests/run_web_article_smoke.py`: PASS
- `python scripts/check_kb.py`: PASS, 65/65
- `python scripts/update_site.py`: PASS
- `python scripts/audit_kb_state.py`: PASS_WITH_WARNINGS, 0 hard failures, 36 soft tag/topic warnings
- `python scripts/check_pages_sync.py`: PASS, 65 slugs

## Git Diff Summary

Expected staged scope:

- four new KB article directories under `content/articles/`
- four new item pages under `site/items/`
- four matching item pages under `docs/items/`
- updated `site/data/catalog.json`
- updated `docs/data/catalog.json`
- relevant `inbox/raw/web/*-2.json` capture payloads for the real imports
- v0.3.78 blocked report
- v0.3.78b retry report
- material import reports for blocked, dry-run, import, and duplicate verification

Existing unrelated untracked smoke artifacts are preserved and should not be staged.

## Commit And Push

- Commit hash: pending
- Push result: pending

## Next Steps

- Fix the cosmetic `docs_item_path` / `site_item_path` formatting in material reports in a separate small router cleanup.
- Consider a later translation pass for the four `needs_translation_review` English web articles.
