# YouTube Fetch Quality Gate v0.3.81

- STATUS: PASS
- Task: `v0.3.81-youtube-fetch-quality-gate-real-regression`
- Date: 2026-07-01
- Branch: `main`
- Base commit: `9792f18a851af5890828cdfc97d803c9eb1a8c49`

## Summary

v0.3.81 adds an explicit YouTube transcript import quality gate on top of the v0.3.80 fetch layer. The router can still dry-run weak YouTube fetches so reports are useful, but `youtube_to_kb.py --import` now blocks weak entries before writing `content/articles`.

No real YouTube URL in this run produced a `fetch_quality=full` transcript in the current environment: YouTube caption tracks were discoverable, but timedtext caption endpoints returned empty text. Therefore no real YouTube entry was imported. This is the intended safe outcome: no metadata-only or weak partial entry was written.

## Behavior Matrix

| fetch_quality | Dry-run | Import default | Import with `--allow-partial-transcript` | Risk |
|---|---|---|---|---|
| `full` | allowed | allowed when visible transcript text >= 800 chars | allowed | acceptable |
| `partial` | allowed with warning | blocked | allowed only when visible transcript text >= 800 chars | needs review |
| `metadata_only` | reportable | blocked | blocked | too weak for KB |
| blocked fetch | blocked | blocked | blocked | no usable text |

## Quality Gate

- Minimum transcript visible text: 800 characters.
- `full`: allowed for dry-run and import when the threshold is met.
- `partial`: dry-run reports `DRY_RUN_OK` with `warning`; import returns `BLOCKED_INCOMPLETE_TEXT` unless `--allow-partial-transcript` is set.
- `metadata_only`: dry-run can generate a report/capture, but import returns `BLOCKED_INCOMPLETE_TEXT`.
- `blocked`: never writes KB entries.
- Fallback title/description text is not counted as transcript body.

## CLI

- `python scripts/youtube_to_kb.py --url "<YOUTUBE_URL>" --dry-run`
- `python scripts/youtube_to_kb.py --url "<YOUTUBE_URL>" --import`
- `python scripts/youtube_to_kb.py --url "<YOUTUBE_URL>" --allow-partial-transcript --import`
- `python scripts/youtube_to_kb.py --url "<YOUTUBE_URL>" --transcript-file "<file.vtt|file.srt|file.txt>" --dry-run`
- `python scripts/material_to_kb.py --input "<YOUTUBE_URL>" --allow-partial-transcript --import`

## Report Fields

The YouTube capture JSON and material router JSON now preserve:

- `fetch_status`
- `fetch_quality`
- `fetch_reason`
- `transcript_language`
- `transcript_kind`
- `transcript_char_count`
- `import_allowed`
- `import_block_reason`
- `warning`

## Local Transcript Fallback

- Implemented: yes.
- Command: `python scripts/youtube_to_kb.py --url "<YOUTUBE_URL>" --transcript-file "<file.vtt|file.srt|file.txt>" --dry-run`
- Supported formats: `.vtt`, `.srt`, `.txt`.
- Behavior: fetches public YouTube metadata from the URL and uses the local transcript file as transcript body.
- Metadata: records `transcript_kind: local`.
- Validation result: `https://www.youtube.com/watch?v=F3fCktnkBbc` + `tests/fixtures/youtube_sample_transcript.vtt` dry-run produced `fetch_quality=full`, `transcript_kind=local`, `transcript_char_count=1441`, then skipped as duplicate of `content/articles/2026/2026-06-25-conan-harvard-commencement-2026`.

## Real Dry-Run Results

| URL | Status | Title | fetch_quality | transcript_char_count | import_allowed | Reason |
|---|---|---|---|---:|---|---|
| `https://www.youtube.com/watch?v=arj7oStGLkU` | `DRY_RUN_OK` | `Inside the Mind of a Master Procrastinator \| Tim Urban \| TED` | `partial` | 0 | false | caption tracks found, timedtext endpoints returned empty text |
| `https://www.youtube.com/watch?v=jNQXAC9IVRw` | `DRY_RUN_OK` | `Me at the zoo` | `partial` | 0 | false | caption endpoints returned empty text |
| `https://www.youtube.com/watch?v=F3fCktnkBbc` | `SKIPPED_DUPLICATE` | `Conan OBrien Delivers the Commencement Address \| Harvard Commencement 2026` | `partial` | 0 | false | caption endpoints returned empty text; duplicate existing KB entry |

Router reports:

- `reports/material_import_20260701_181158.md`
- `reports/material_import_20260701_181158.json`
- `reports/material_import_20260701_181211.md`
- `reports/material_import_20260701_181211.json`
- `reports/material_import_20260701_181225.md`
- `reports/material_import_20260701_181225.json`

## Real Import

- Imported: 0
- Blocked: 3 dry-run candidates were not importable because none produced a full transcript.
- Reason: current environment can discover caption tracks but receives empty caption endpoint bodies.
- Action: no real YouTube KB entry was written.

## Tests

- Added metadata-only fixture: `tests/fixtures/youtube_metadata_only.json`
- Added partial transcript fixture: `tests/fixtures/youtube_partial_transcript.vtt`
- Updated `tests/run_youtube_import_smoke.py` to cover:
  - full transcript dry-run
  - full transcript capture fields
  - metadata-only import blocked
  - partial import blocked by default
  - partial import with `--allow-partial-transcript` reaches duplicate/import flow
  - short transcript blocked
  - YouTube route does not affect WeChat/web/PDF routes
- Updated `tests/run_fetch_layer_smoke.py` to assert weak fallback reports `import_allowed=false`.
- Updated `tests/run_wechat_batch_smoke.py` and `scripts/check_pages_sync.py` output strings to avoid Windows console Unicode arrow failures.

## Gates

| Gate | Result |
|---|---|
| `python -m py_compile scripts/*.py` | Windows wildcard form failed; PowerShell-expanded equivalent PASS |
| `python tests/run_smoke_tests.py` | PASS |
| `python tests/run_wechat_batch_smoke.py` | PASS |
| `python tests/run_item_render_smoke.py` | PASS |
| `python tests/run_image_localization_smoke.py` | PASS |
| `python tests/run_material_router_smoke.py` | PASS |
| `python tests/run_web_article_smoke.py` | PASS |
| `python tests/run_youtube_import_smoke.py` | PASS |
| `python tests/run_fetch_layer_smoke.py` | PASS |
| `python scripts/check_kb.py` | PASS, 65/65 |
| `python scripts/update_site.py` | PASS |
| `python scripts/audit_kb_state.py` | PASS_WITH_WARNINGS, 0 hard failures, 36 existing warnings |
| `python scripts/check_pages_sync.py` | PASS, 65 synced slugs |

## Counts

- `content/**/metadata.yaml`: 65
- `content/articles/**/metadata.yaml`: 47
- `docs/items`: 65
- `site/items`: 65
- synced slugs: 65

## Git Diff Summary

Changed tracked files:

- `README.md`
- `docs/AGENT_COMMANDS.md`
- `docs/commands/material-kb-import-command.md`
- `docs/commands/youtube-kb-import-command.md`
- `docs/workflows/material-kb-import-workflow.md`
- `docs/workflows/youtube-video-kb-import-workflow.md`
- `scripts/check_pages_sync.py`
- `scripts/fetchers/youtube_fetcher.py`
- `scripts/material_to_kb.py`
- `scripts/youtube_to_kb.py`
- `tests/run_fetch_layer_smoke.py`
- `tests/run_wechat_batch_smoke.py`
- `tests/run_youtube_import_smoke.py`

New files:

- `tests/fixtures/youtube_metadata_only.json`
- `tests/fixtures/youtube_partial_transcript.vtt`
- this report

## Commit And Push

- Commit hash: pending at report creation; final response records the pushed commit hash.
- Push result: pending at report creation; final response records the push result.

## Next Steps

- For real YouTube imports in environments where timedtext returns empty captions, ask the user for a local `.vtt`, `.srt`, or `.txt` transcript and use `--transcript-file`.
- If stable full transcript fetching is required without local files, evaluate a dedicated transcript provider or yt-dlp subtitle listing in a future scoped task without downloading videos.
