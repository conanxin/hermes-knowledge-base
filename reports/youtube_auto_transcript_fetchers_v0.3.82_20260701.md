# YouTube Automatic Transcript Fetchers - v0.3.82

- STATUS: BLOCKED_NO_FULL_TRANSCRIPT_AVAILABLE
- Task: `v0.3.82-youtube-auto-transcript-fetchers`
- Date: 2026-07-01
- Base commit: `54da7840dd0e20e1aa78eb56bae50e3f6e3145ce`
- Branch: `main`

## Summary

v0.3.82 adds an automatic multi-provider YouTube transcript chain so users do not need to provide local transcript files by default. The importer now tries direct captionTracks in multiple timedtext formats, then subtitle-only `yt-dlp` when available, then optional `youtube-transcript-api`, and finally records metadata-only diagnostics without treating descriptions as transcript text.

The code, tests, docs, and KB gates passed. Real YouTube dry-runs did not find a full transcript in this environment because direct caption endpoints returned HTTP 200 with empty text and both optional fallback providers were unavailable. No YouTube item was imported, and no partial or metadata-only KB entry was written.

## Provider Chain

1. `direct_captionTracks`
   - Reads `ytInitialPlayerResponse`.
   - Tries each selected caption track with:
     - original `baseUrl`
     - `fmt=vtt`
     - `fmt=srv3`
     - `fmt=ttml`
     - `fmt=json3`
   - Parses VTT, json3, srv3/XML, and TTML/XML.

2. `yt-dlp`
   - Optional subtitle-only fallback.
   - Requires either `yt-dlp` command or Python module availability.
   - Uses `--skip-download`, `--write-subs`, and `--write-auto-subs`.
   - Does not download video files.
   - Temporary subtitle files are written under `tmp/youtube_subs/` and are not committed.

3. `youtube-transcript-api`
   - Optional fallback if the Python package is already installed.
   - Not a hard dependency.

4. `metadata`
   - Diagnostic fallback only.
   - Produces `fetch_quality: metadata_only`.
   - Never importable.
   - Video description is not treated as transcript body.

## Provider Attempt Shape

Each attempt is recorded as:

```json
{
  "provider": "direct_captionTracks | yt-dlp | youtube-transcript-api | metadata",
  "status": "ok | empty | failed | unavailable",
  "language": "...",
  "kind": "manual | auto | local | metadata",
  "format": "vtt | srv3 | ttml | json3 | text",
  "char_count": 0,
  "reason": "..."
}
```

The attempts are propagated into YouTube capture JSON, `material_to_kb.py` JSON reports, and dry-run summaries.

## Provider Availability

- `yt-dlp`: unavailable in this environment.
  - Probe: `yt-dlp --version`
  - Result: command not found.
- `youtube-transcript-api`: unavailable in this environment.
  - Probe: `python -c "import importlib.util; ..."`
  - Result: unavailable.

## Auto Caption Policy

- Manual full transcript: import allowed.
- Auto full transcript: dry-run allowed; import requires `--allow-auto-captions`.
- Auto transcript metadata includes:
  - `transcript_kind: auto`
  - `transcript_needs_review: true`
  - warning: `automatic captions need review`
- Partial transcript: dry-run allowed; import requires `--allow-partial-transcript`.
- Metadata-only: dry-run reportable, import blocked.

## Quality Gate Result

- Minimum transcript length remains 800 visible characters.
- `fetch_quality=full` with sufficient transcript can import.
- `fetch_quality=partial` is blocked by default.
- `fetch_quality=metadata_only` is always blocked.
- No text / no transcript remains blocked.
- The implementation did not lower `check_kb.py` standards.

## CLI Changes

`scripts/youtube_to_kb.py` and `scripts/material_to_kb.py` now support:

```bash
python scripts/material_to_kb.py --input "<YouTube URL>" --dry-run
python scripts/material_to_kb.py --input "<YouTube URL>" --import
python scripts/material_to_kb.py --input "<YouTube URL>" --allow-auto-captions --import
python scripts/material_to_kb.py --input "<YouTube URL>" --caption-provider yt-dlp --dry-run
```

New flags:

- `--caption-provider auto|direct|yt-dlp|transcript-api`
- `--allow-auto-captions`
- `--allow-partial-transcript`

Existing local transcript fallback remains available:

```bash
python scripts/youtube_to_kb.py --url "<YouTube URL>" --transcript-file "<file.vtt|txt|srt>" --dry-run
```

## Real Dry-Run Results

| URL | Status | Title | fetch_quality | transcript_kind | transcript_char_count | Import allowed | Reason |
|---|---|---|---|---|---:|---|---|
| `https://www.youtube.com/watch?v=UF8uR6Z6KLc` | `DRY_RUN_OK` | `Steve Jobs' 2005 Stanford Commencement Address` | `metadata_only` | `none` | 0 | false | direct captions returned empty text; `yt-dlp` and transcript API unavailable |
| `https://www.youtube.com/watch?v=jNQXAC9IVRw` | `DRY_RUN_OK` | `Me at the zoo` | `metadata_only` | `none` | 0 | false | direct captions returned empty text; `yt-dlp` and transcript API unavailable |
| `https://www.youtube.com/watch?v=F3fCktnkBbc` | `SKIPPED_DUPLICATE` | `Conan O'Brien Delivers the Commencement Address` | `metadata_only` | `none` | 0 | false | duplicate of existing KB item; live fetch still metadata-only |
| `https://www.youtube.com/watch?v=arj7oStGLkU` | timed out | `Inside the Mind of a Master Procrastinator` candidate | n/a | n/a | 0 | false | live dry-run exceeded local timeout and was stopped; no import attempted |

Generated material reports used for evidence:

- `reports/material_import_20260701_184714.json`
- `reports/material_import_20260701_184714.md`
- `reports/material_import_20260701_185551.json`
- `reports/material_import_20260701_185551.md`
- `reports/material_import_20260701_185620.json`
- `reports/material_import_20260701_185620.md`

These generated material reports remain untracked and were not submitted with this task.

## Representative Provider Attempts

- Steve Jobs video:
  - `direct_captionTracks/en/manual/original`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/manual/vtt`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/manual/srv3`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/manual/ttml`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/manual/json3`: empty, HTTP 200, 0 chars
  - `yt-dlp`: unavailable, `provider_unavailable`
  - `youtube-transcript-api`: unavailable, `provider_unavailable`

- Me at the zoo:
  - `direct_captionTracks/en/manual/original`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/manual/vtt`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/manual/srv3`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/manual/ttml`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/manual/json3`: empty, HTTP 200, 0 chars
  - `yt-dlp`: unavailable, `provider_unavailable`
  - `youtube-transcript-api`: unavailable, `provider_unavailable`

- Conan duplicate candidate:
  - `direct_captionTracks/en/manual/original`: empty, HTTP 200, 0 chars
  - `direct_captionTracks/en/auto/vtt`: empty, HTTP 200, 0 chars
  - `yt-dlp`: unavailable, `provider_unavailable`
  - `youtube-transcript-api`: unavailable, `provider_unavailable`

## Tests

Updated or added smoke coverage for:

- direct captionTracks VTT parsing
- direct captionTracks json3 parsing
- direct captionTracks srv3/XML parsing
- direct empty caption fallback to `yt-dlp`
- `yt-dlp` unavailable without crash
- auto caption `transcript_kind=auto` and `transcript_needs_review=true`
- metadata-only import block
- partial transcript default import block
- full transcript import flow
- YouTube route not affecting WeChat or generic web routes
- PDF still `BLOCKED_UNSUPPORTED`
- `check_kb.py` and `check_pages_sync.py` still pass

## Gate Results

| Gate | Result | Notes |
|---|---|---|
| `python -m py_compile scripts/*.py` | PASS | PowerShell wildcard was expanded explicitly before invoking py_compile |
| `python tests/run_smoke_tests.py` | PASS | 3/3 |
| `python tests/run_wechat_batch_smoke.py` | PASS | 5/5 |
| `python tests/run_item_render_smoke.py` | PASS | 6/6 |
| `python tests/run_image_localization_smoke.py` | PASS | 8/8 |
| `python tests/run_material_router_smoke.py` | PASS | 4/4 |
| `python tests/run_web_article_smoke.py` | PASS | 5/5 |
| `python tests/run_youtube_import_smoke.py` | PASS | 14/14 |
| `python tests/run_fetch_layer_smoke.py` | PASS | 5/5 |
| `python scripts/check_kb.py` | PASS | 65/65 |
| `python scripts/update_site.py` | PASS | 65 item pages |
| `python scripts/audit_kb_state.py` | PASS_WITH_WARNINGS | 36 existing soft warnings, 0 hard failures |
| `python scripts/check_pages_sync.py` | PASS | 65 synced slugs |

## Counts

- `content/articles`: 47 article entries
- total content records: 65
- `docs/items`: 65
- `site/items`: 65
- synced slugs: 65

## Git Diff Summary

- Extended `scripts/youtube_to_kb.py` with multi-provider transcript fetching, provider attempts, format parsers, auto caption policy, and CLI flags.
- Extended `scripts/material_to_kb.py` to pass YouTube caption flags and preserve provider attempts in reports.
- Updated `scripts/fetchers/youtube_fetcher.py` to use the same provider and quality metadata.
- Updated YouTube and fetch layer smoke tests.
- Added synthetic caption fixtures for json3, srv3/XML, and `yt-dlp` subtitle fallback.
- Updated README and command/workflow docs for the v0.3.82 policy.

## Commit And Push

- Commit hash: pending at report creation; final response records the pushed commit hash.
- Push result: pending at report creation; final response records the push result.

## Next Steps

1. Install or vendor an approved subtitle-only provider such as `yt-dlp` in the runtime if real YouTube imports should work reliably without user-provided transcript files.
2. Retry the same real URLs after provider availability improves.
3. Keep metadata-only and partial-transcript blocks in place so weak YouTube entries are not written into the KB.
