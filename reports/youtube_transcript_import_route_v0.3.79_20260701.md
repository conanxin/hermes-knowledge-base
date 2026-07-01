# YouTube Transcript Import Route v0.3.79

- STATUS: PASS
- Task: v0.3.79-youtube-transcript-kb-import-route
- Date: 2026-07-01
- Branch: main
- Base commit: 6f0d06e82ee44da22226ec0db670c9defd8eac19

## Scope

This task adds a minimal stable YouTube transcript import route and connects it to the unified material router.

New route:

- Input: `youtube.com/watch?v=...`, `youtu.be/...`, `youtube.com/shorts/...`
- Router inferred type: `youtube_url`
- Router route: `youtube_to_kb.py`
- Import script: `scripts/youtube_to_kb.py`
- Output kind: KB article with `content_kind: youtube_transcript`

The route does not download video files, does not use browser cookies, and does not fabricate content when no usable transcript is available.

## Current Support Matrix

- WeChat URL: supported via existing WeChat route
- Local HTML / Markdown / TXT: supported via existing local text route
- Generic web URL: supported via `scripts/web_article_to_kb.py`
- YouTube URL: supported when a usable caption/transcript track is available
- PDF: `BLOCKED_UNSUPPORTED`

## Existing Capability Inventory

Repository review found prior YouTube-related docs and KB entries, but no stable direct URL import script for transcripts:

- Existing docs: YouTube preflight/brief/import workflow documents.
- Existing KB examples: prior YouTube/speech transcript entries with older metadata conventions.
- Existing tools: no checked-in stable `youtube_to_kb.py` route before this task.

The new route therefore implements a narrow transcript-first importer and reuses existing KB helper functions from `import_wechat_article_capture.py` for slugging-compatible metadata, topics, tags, and mixed word counts.

## Metadata Extraction

For public YouTube pages, `scripts/youtube_to_kb.py`:

- Fetches the public watch page with a normal HTTP request.
- Extracts `ytInitialPlayerResponse` without using cookies or video downloads.
- Reads title, channel, channel URL, publish/upload date, duration, view count when available, description, thumbnail URL, video ID, source URL, and canonical URL.
- Hard-stops when the page is unavailable, private, unsupported, or lacks required metadata.

Offline smoke tests use fixture-only hidden hooks so tests do not depend on live YouTube.

## Transcript Extraction

Transcript extraction:

- Reads `captionTracks` from the public player response.
- Prefers manual captions by default.
- Falls back to automatic captions unless `--no-auto-captions` is set.
- Ranks preferred languages as requested by `--language`; default priority is zh/zh-CN first, then en.
- Fetches YouTube timedtext captions as VTT and parses VTT/XML transcript formats.
- Merges short timed captions into readable Markdown paragraphs with timestamps.

Hard stop conditions:

- No caption/transcript tracks.
- Only auto captions while `--no-auto-captions` is set.
- Caption endpoint empty or unparsable.
- Transcript too short.
- Missing title or other required metadata.
- Network or HTTP fetch failure.

No KB entry is written for these blocked states.

## KB Output

On successful import, the script writes the standard 6-file bundle under `content/articles/YYYY/<slug>/`:

- `metadata.yaml`
- `source.md`
- `translation.zh-CN.md`
- `summary.md`
- `notes.md`
- `raw_payload.json`

Schema fields include:

- `type: article`
- `content_kind: youtube_transcript`
- `source_platform: youtube`
- `source_site: YouTube`
- `source_url`
- `canonical_url`
- `title`
- `author` / `channel`
- `published_date`
- `captured_date`
- `source_language`
- `translation_language`
- `transcript_language`
- `transcript_kind`
- `video_id`
- `duration`
- `channel_url`
- `thumbnail_url`
- `topics`
- `tags`
- `word_count`

Chinese transcripts are mirrored with `is_translation_mirror: true`. English transcripts are marked `needs_translation_review` and receive an explicit placeholder translation file instead of pretending to be a complete human translation.

## Summary and Notes

Generated `summary.md` includes:

- One-sentence summary
- Video core question
- Main points
- Structure / timeline
- Key concepts
- Background notes
- Quotable transcript excerpts
- Possible KB links
- Personal viewing prompt

Generated `notes.md` includes:

- Accepted points
- Reflections
- Related materials
- Actions
- Key excerpts
- Concept cards
- Structure notes
- Rewatch reminder

## Dedup Strategy

Duplicate checks cover:

- `video_id`
- `source_url`
- `canonical_url`
- `title + channel + published_date`
- Transcript `content_hash`

Duplicates return `SKIPPED_DUPLICATE` for import mode or `DRY_RUN_DUPLICATE` at the script layer. The unified router normalizes duplicate dry-runs to `SKIPPED_DUPLICATE` in material reports.

## Router Integration

`scripts/material_to_kb.py` now:

- Infers YouTube inputs as `youtube_url`.
- Routes them to `scripts/youtube_to_kb.py`.
- Preserves dry-run/import mode.
- Keeps WeChat and generic web routes unchanged.
- Leaves PDF as `BLOCKED_UNSUPPORTED`.
- Runs each YouTube input independently so one blocked input does not stop a mixed batch.

## Tests Added or Updated

Added:

- `tests/run_youtube_import_smoke.py`
- `tests/fixtures/youtube_sample_metadata.json`
- `tests/fixtures/youtube_sample_transcript.vtt`
- `tests/fixtures/material_inputs_youtube_mixed.txt`

Updated:

- `tests/run_material_router_smoke.py`
- `tests/run_web_article_smoke.py`
- `tests/fixtures/material_inputs_mixed.txt`

Coverage:

- YouTube URL inference for watch/shorts URLs.
- Router route to `youtube_to_kb.py`.
- Fixture metadata + transcript capture generation.
- Non-empty transcript Markdown conversion.
- Missing transcript hard-stop as `BLOCKED_INCOMPLETE_TEXT`.
- Duplicate `video_id` detection against an existing KB entry.
- WeChat and generic web routes remain intact.
- PDF remains `BLOCKED_UNSUPPORTED`.
- `check_kb.py` and `check_pages_sync.py` remain PASS.

## Real Dry-Run

Command:

```bash
python scripts/material_to_kb.py --input "https://www.youtube.com/watch?v=F3fCktnkBbc" --dry-run
```

Result:

- Report markdown: `reports/material_import_20260701_162110.md`
- Report json: `reports/material_import_20260701_162110.json`
- Inferred type: `youtube_url`
- Route: `youtube_to_kb.py`
- Status: `BLOCKED_INCOMPLETE_TEXT`
- Reason: public YouTube metadata exposed caption tracks, but both manual and auto timedtext caption endpoints returned empty text from this environment.
- Real import: not attempted.
- KB writes: none.

This is the intended hard-stop behavior: no transcript means no article is imported.

## Gates

- `python -m py_compile scripts/*.py`: PASS
- `python tests/run_smoke_tests.py`: PASS
- `python tests/run_wechat_batch_smoke.py`: PASS
- `python tests/run_item_render_smoke.py`: PASS
- `python tests/run_image_localization_smoke.py`: PASS
- `python tests/run_material_router_smoke.py`: PASS
- `python tests/run_web_article_smoke.py`: PASS
- `python tests/run_youtube_import_smoke.py`: PASS
- `python scripts/check_kb.py`: PASS, 65/65
- `python scripts/update_site.py`: PASS
- `python scripts/audit_kb_state.py`: PASS_WITH_WARNINGS, 0 hard failures
- `python scripts/check_pages_sync.py`: PASS, 65 slugs

## Counts

- `content/articles` metadata count: 47
- Total KB metadata count: 65
- `docs/items`: 65
- `site/items`: 65
- Synced slugs: 65

## Dirty State Notes

At handoff, the workspace already contained many untracked reports, captures, and `tmp/` artifacts from prior v0.3.76-v0.3.78 work and smoke tests. These were preserved and not deleted.

The task commit should include only the v0.3.79 implementation, tests, docs, fixtures, and this report. It should not use `git add -A`.

## Git Diff Summary

Main tracked changes before staging:

- New YouTube importer script.
- Material router now supports YouTube URLs.
- New YouTube import smoke test and fixtures.
- Existing material/web router smoke tests updated for the new supported YouTube route.
- Documentation updated to list YouTube transcript route support and PDF unsupported status.

## Commit / Push

- Commit hash: pending at report creation; final response records the actual commit.
- Push result: pending at report creation; final response records the actual push result.

## Next Steps

- Consider adding an optional external transcript backend such as `yt-dlp` only if it can be used without video downloads, cookies, or paywall/login bypassing.
- Add a later real import regression with a video whose caption endpoint returns non-empty transcript text in the execution environment.
- Keep PDF as `BLOCKED_UNSUPPORTED` until a stable OCR/text route exists.
