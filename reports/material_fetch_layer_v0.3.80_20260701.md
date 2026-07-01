# Material Fetch Layer v0.3.80

- STATUS: PASS
- Task: v0.3.80-material-fetch-layer-unification
- Date: 2026-07-01
- Branch: main
- Base commit: 8d6f86cb736f3df788fc72993fb5b800c8c3c4c2

## Goal

Introduce a shared material fetch layer so supported source types pass through one normalized fetch contract before KB import:

```text
URL / file -> router -> fetch layer -> importer -> KB
```

The import scripts remain available as standalone commands for backward compatibility, but `material_to_kb.py` now performs fetch preflight first and records fetch quality in its reports.

## New Fetch Layer

Added `scripts/fetchers/`:

- `base_fetcher.py`
- `wechat_fetcher.py`
- `web_fetcher.py`
- `youtube_fetcher.py`
- `__init__.py`

`BaseFetcher.fetch(source)` returns:

```python
{
    "title": str,
    "text": str,
    "images": [],
    "metadata": {},
    "status": "ok | partial | blocked",
    "reason": "",
    "fetch_quality": "full | partial | metadata_only"
}
```

## Fetcher Behavior

### WeChatFetcher

- Reuses `wechat_url_to_kb.py` parsing/fetching helpers.
- Supports public WeChat URLs and local HTML/Markdown/TXT files.
- Returns `fetch_quality: full` when article text is present.
- Blocks when the public page is inaccessible, incomplete, or has no article body.

### WebFetcher

- Reuses `web_article_to_kb.py` extraction logic.
- Supports public web URLs and local HTML/Markdown/TXT article fixtures.
- Uses the existing extraction chain: article/main/schema/common containers/body fallback.
- Returns `fetch_quality: full` only after existing content validation passes.
- Blocks robots-disallowed, non-article, unsupported content type, paywall/login, or empty-body cases.

### YouTubeFetcher

YouTube is the main reliability fix.

Fallback chain:

1. `ytInitialPlayerResponse` metadata.
2. `captionTracks` timedtext VTT/XML transcript.
3. Metadata/description fallback when captions are missing, empty, or unparsable.

Result quality:

- `full`: usable transcript was fetched and parsed.
- `partial`: no transcript, but public description/metadata gives usable text.
- `metadata_only`: only title/channel/basic metadata is available.

The fetch layer no longer treats caption endpoint failure as immediate `BLOCKED_INCOMPLETE_TEXT`.

## YouTube Importer Fix

`scripts/youtube_to_kb.py` now mirrors the fetch layer fallback:

- Caption success still produces a normal transcript capture.
- Caption discovery/fetch/parse failure falls back to a partial capture.
- Partial captures include `fetch_quality` and `fetch_reason`.
- Dry-run/import can proceed from partial text instead of writing nothing.
- Only "no metadata text at all" remains blocked.

No video files are downloaded, no cookies are used, and unavailable transcripts are not fabricated.

## Router Integration

`scripts/material_to_kb.py` now:

- Routes input as before.
- Runs `fetch_material()` before importer execution.
- Retries fetch once for network-style fetch failures.
- Skips importer when fetch returns `blocked`.
- Allows importer execution when fetch returns `ok` or `partial`.
- Adds report fields:
  - `fetch_status`
  - `fetch_quality`
  - `fetch_reason`
  - `fetch_text_chars`

Markdown material reports now include Fetch and Quality columns.

## Unified Error Strategy

Rules implemented:

1. Network/fetch errors are retried once in the fetch layer.
2. Missing YouTube captions are fallback-allowed.
3. No text at all is blocked.
4. Partial text is allowed and marked with `fetch_quality`.

Still blocked:

- WeChat public pages requiring login/client access.
- Web pages blocked by robots, login walls, paywalls, unsupported content type, or empty extraction.
- YouTube pages with no accessible metadata text at all.
- PDF remains `BLOCKED_UNSUPPORTED`.

## Tests

Added:

- `tests/run_fetch_layer_smoke.py`

Updated:

- `tests/run_youtube_import_smoke.py`

Coverage:

- WeChat fetch returns text.
- Web fetch returns text.
- YouTube fetch returns `partial` when captions are unavailable.
- `material_to_kb.py` records fetch fallback fields.
- YouTube no-transcript fixture now dry-runs successfully with partial quality.
- Existing material router smoke remains PASS.

## Gates

- `python -m py_compile scripts/*.py`: PASS
- `python tests/run_smoke_tests.py`: PASS
- `python tests/run_fetch_layer_smoke.py`: PASS
- `python tests/run_material_router_smoke.py`: PASS
- `python tests/run_youtube_import_smoke.py`: PASS
- `python scripts/check_kb.py`: PASS, 65/65
- `python scripts/update_site.py`: PASS
- `python scripts/check_pages_sync.py`: PASS, 65 slugs

## Counts

- Total KB metadata count: 65
- `content/articles` metadata count: 47
- `docs/items`: 65
- `site/items`: 65
- Synced slugs: 65

## Git Diff Summary

Primary changes:

- Added shared fetcher package under `scripts/fetchers/`.
- Inserted fetch preflight into `material_to_kb.py`.
- Added YouTube partial/metadata-only fallback in `youtube_to_kb.py`.
- Added fetch layer smoke tests.
- Updated YouTube smoke to reflect partial fallback behavior.

## Commit / Push

- Commit hash: pending at report creation; final response records the actual commit.
- Push result: pending at report creation; final response records the actual push result.

## Next Steps

- Consider passing normalized fetch payloads directly into importers in a future refactor, so standalone importer compatibility and router-driven fetch can share one physical payload.
- Add real YouTube regression cases where timedtext returns non-empty captions and where only metadata/description is available.
- Keep PDF blocked until a real PDF/OCR fetcher exists.
