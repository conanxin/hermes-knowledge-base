# WeChat Summary Image Cleanup v0.3.75

STATUS: PASS

## Scope

- Task: `v0.3.75-wechat-summary-image-cleanup-resume`
- Repo: `conanxin/hermes-knowledge-base`
- Branch: `main`
- Baseline HEAD at takeover: `c2c3fbe5e47bba5033c3bfecb67365709fbac83a`
- `origin/main` after fetch: `c2c3fbe5e47bba5033c3bfecb67365709fbac83a`
- Note: `python3` is not available in this Windows shell; gates were run with `python` / `sys.executable` and `PYTHONUTF8=1`, `PYTHONIOENCODING=utf-8` where needed.

## Takeover State

`git status --short` at takeover showed task-relevant WorkBuddy changes in:

- 3 `content/articles/**/summary.md` files
- 3 matching `site/items/**/index.html` files
- 3 matching `docs/items/**/index.html` files
- `scripts/localize_article_images.py`
- `scripts/import_wechat_article_capture.py`

It also showed pre-existing/untracked operating artifacts:

- `AGENTS.md`
- `inbox/raw/wechat/*.json`
- `reports/wechat_batch_import_20260701_*.md`
- `reports/wechat_batch_import_20260701_*.json`

WorkBuddy inheritance judgment: reused. The modified content/site/docs/script files were directly related to v0.3.75 and were preserved. The untracked raw/report artifacts were treated as prior smoke/batch-test artifacts, left untracked, and not staged.

Preflight:

- `git fetch origin main --tags`: PASS
- `origin/main` contains `c2c3fbe5e47bba5033c3bfecb67365709fbac83a`: PASS
- `check_task_preflight.py --planned-tag v0.3.75-wechat-summary-image-cleanup-resume --classify-dirty --json`: expected FAIL due dirty task-relevant WorkBuddy changes; `head_sync: PASS`, `tag_available: PASS`

## Remote mmbiz Residue

HEAD public-surface baseline before WorkBuddy cleanup:

- `content/articles/**/*.md`: 3
- `docs/items/**/*.html`: 3
- `site/items/**/*.html`: 3
- Total public-surface remote mmbiz refs: 9

Known content residues were all in `summary.md` under `## 附：首段原文（用于校对）`:

- `content/articles/2026/2026-06-26-wechat-新京报书评周刊-专访林小英接受教育最终是为了让我们把日子过得生动/summary.md`
- `content/articles/2026/2026-06-26-wechat-腾讯研究院-ai无法教会的三件事/summary.md`
- `content/articles/2026/2026-06-28-wechat-文汇读书周报-逆流而上的爱与勇气写在阿伦特诞辰120周年之际/summary.md`

At takeover, after WorkBuddy's uncommitted edits, the public-surface scan already reported:

- `content/articles/**/*.md`: 0
- `docs/items/**/*.html`: 0
- `site/items/**/*.html`: 0
- Total: 0

After completing this task and rebuilding:

- `content_remaining`: 0
- `docs_remaining`: 0
- `site_remaining`: 0
- Still has remote mmbiz residue on the public surface: no

Important boundary: `raw_payload.json` can still contain original remote WeChat URLs as archival capture payload. This task did not rewrite raw payloads and did not re-fetch WeChat articles.

## Implementation

`scripts/localize_article_images.py`:

- Extended default public Markdown processing from `source.md` / `translation.zh-CN.md` to:
  - `source.md`
  - `translation.zh-CN.md`
  - `summary.md`
  - `notes.md`
- Rewrites only Markdown image URLs.
- Skips already-local `assets/...` image URLs.
- Skips empty Markdown images such as `![]()`.
- Keeps failed remote URLs in place and reports failures.
- Preserves dry-run.
- Adds per-article and per-Markdown-file JSON results:
  - `image_total`
  - `image_localized`
  - `image_failed`
  - `file_changed`
- Avoids overwriting existing `assets/image-NNN.*` files by choosing the next available image index.

`scripts/import_wechat_article_capture.py`:

- Removed generation of the debug/proofreading `## 附：首段原文（用于校对）` section from new `summary.md` files.
- Left raw source payload preservation in `raw_payload.json`.
- Did not touch existing manual `summary.md` / `notes.md`.
- Did not relax `check_kb.py`.

`tests/run_image_localization_smoke.py`:

- Updated to v0.3.75.
- Confirms dry-run includes `summary.md` and `notes.md` file results.
- Adds a temp-article smoke covering `source.md`, `translation.zh-CN.md`, `summary.md`, and `notes.md`.
- Confirms already-local assets are not downloaded.
- Confirms empty `![]()` is not converted into a bad local link.
- Confirms generated item HTML has no remote `mmbiz.qpic.cn`.
- Confirms `check_pages_sync.py` still passes.

## Cleanup Results

- `summary.md` processed: yes
- `notes.md` processed: yes, via code path and smoke test; no live `notes.md` remote mmbiz refs existed in the current KB
- Public summary refs replaced in the committed diff: 3
- Current `localize_article_images.py --all-wechat` run:
  - articles processed: 7
  - image_total: 0
  - image_localized: 0
  - image_failed: 0
  - reason: WorkBuddy's inherited edits had already removed live remote refs before the handoff scan
- Download failures: 0
- Fallback remote URLs kept on public surface: 0

## Counts

- `content/articles` metadata count: 43
- Total `content/**/metadata.yaml` count: 61
- `docs/items` slug count: 61
- `site/items` slug count: 61
- Synced slugs: 61
- `check_kb.py`: 61/61 PASS

Note: the task prompt says `content/articles` should be 61, but this repo currently has 43 article records plus notes/projects/collections/legacy entries for a total content count of 61. No item pages or KB entries were deleted.

## Gates

All gates below were run after the final rebuild.

- `python -m py_compile scripts/*.py`: PASS
- `python tests/run_smoke_tests.py`: PASS
- `python tests/run_wechat_batch_smoke.py`: PASS
- `python tests/run_item_render_smoke.py`: PASS
- `python tests/run_image_localization_smoke.py`: PASS, 8/8
- `python scripts/check_kb.py`: PASS, 61/61
- `python scripts/update_site.py`: PASS
- `python scripts/audit_kb_state.py`: PASS_WITH_WARNINGS, HARD FAILURES 0, WARNINGS 28
- `python scripts/check_pages_sync.py`: PASS, 61 slugs

Environment note: `beautifulsoup4` was missing and was installed with `python -m pip install beautifulsoup4` so the existing WeChat smoke tests could run. No repo files were changed by that install.

## Diff Summary

`git diff --stat` before report:

```text
12 files changed, 205 insertions(+), 61 deletions(-)
```

Changed files intended for commit:

- `content/articles/2026/2026-06-26-wechat-新京报书评周刊-专访林小英接受教育最终是为了让我们把日子过得生动/summary.md`
- `content/articles/2026/2026-06-26-wechat-腾讯研究院-ai无法教会的三件事/summary.md`
- `content/articles/2026/2026-06-28-wechat-文汇读书周报-逆流而上的爱与勇气写在阿伦特诞辰120周年之际/summary.md`
- `docs/items/2026-06-26-wechat-新京报书评周刊-专访林小英接受教育最终是为了让我们把日子过得生动/index.html`
- `docs/items/2026-06-26-wechat-腾讯研究院-ai无法教会的三件事/index.html`
- `docs/items/2026-06-28-wechat-文汇读书周报-逆流而上的爱与勇气写在阿伦特诞辰120周年之际/index.html`
- `site/items/2026-06-26-wechat-新京报书评周刊-专访林小英接受教育最终是为了让我们把日子过得生动/index.html`
- `site/items/2026-06-26-wechat-腾讯研究院-ai无法教会的三件事/index.html`
- `site/items/2026-06-28-wechat-文汇读书周报-逆流而上的爱与勇气写在阿伦特诞辰120周年之际/index.html`
- `scripts/import_wechat_article_capture.py`
- `scripts/localize_article_images.py`
- `tests/run_image_localization_smoke.py`
- `reports/wechat_summary_image_cleanup_v0.3.75_20260701.md`

## Commit and Push

- Commit hash: pending at report-write time; final assistant response records the actual commit hash after commit.
- Push result: pending at report-write time; final assistant response records the actual push result.

Self-reference note: a committed report cannot contain its own final commit hash without changing that hash. The final response is the authoritative commit/push record.

## Next Steps

- Leave `raw_payload.json` untouched unless a separate archival-policy task decides to redact or mirror raw captures.
- Consider making `check_pages_sync.py` output ASCII-only arrows or setting UTF-8 mode internally for smoother Windows default-console runs.
