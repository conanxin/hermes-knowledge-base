# v0.3.84 · YouTube fetch-result handoff + inbox overwrite protection

**Task name:** `v0.3.84-youtube-fetch-handoff-overwrite-protection`
**Branch / Repo:** `conanxin/hermes-knowledge-base` (main)
**Date:** 2026-07-01
**Author:** Hermes / MiniMax-M3
**Status:** PASS

---

## 1. Background (root cause from v0.3.83 report)

`reports/youtube_provider_env_real_import_v0.3.83_20260701.md` (committed as
`7d931e9`) recorded that for `https://youtu.be/arj7oStGLkU` (Tim Urban, TED):

- The **in-process** YouTube fetch layer returned a `full` capture (en 12 671 chars /
  zh-CN 4 244 chars / zh-Hans auto 10 645 chars).
- The **subprocess** call (`scripts/youtube_to_kb.py`) refetched, hit YouTube HTTP
  429, and ended up with `fetch_quality=metadata_only`.
- Net effect: the imported item would have been downgraded to `metadata_only`,
  blocking the import entirely.

The deeper structural issue: `scripts/youtube_to_kb.py` does the in-process fetch
once, then `scripts/material_to_kb.py` shells out to the same script, and the
subprocess refetches, doubling the load and the rate-limit exposure.

The second issue is **inbox write fragility**: the subprocess always overwrites
`inbox/raw/youtube/<video_id>.json`, so any later run that gets a weaker
`metadata_only` result silently erases the previously captured `full` capture for
the same `video_id`.

## 2. v0.3.84 changes

### 2.1 Fetch-result handoff (`material_to_kb.py` → `youtube_to_kb.py`)

- `run_single_youtube()` now accepts `fetch_result` (the in-process fetcher
  return value) and writes a handoff file when `fetch_quality` is `full` or
  `partial`.
- Handoff path: `tmp/material_fetches/youtube_<video_id>_<timestamp>.json`.
  The directory is gitignored under `tmp/material_fetches/` (added to
  `.gitignore`).
- Handoff envelope shape:
  ```json
  {
    "url": "https://youtu.be/<id>",
    "video_id": "...",
    "fetch_quality": "full" | "partial",
    "captured_at": "2026-07-01T22:34:57",
    "metadata": { "capture": {<full capture dict>}, "source_platform": "youtube" }
  }
  ```
- `material_to_kb.py` adds `--fetch-result-json <path>` to the YouTube subprocess
  command and records `handoff_used: true` + `fetch_result_json_path` on the
  router item.
- `youtube_to_kb.py` accepts the new `--fetch-result-json` argument
  (intentionally hidden in `--help` via `argparse.SUPPRESS`; it's a router-only
  contract) and short-circuits `build_capture_from_args()` to load the handoff
  file instead of refetching.
- `load_fetch_result_json()` is permissive about the envelope shape: it accepts
  either `metadata.capture.<capture-dict>` or a top-level capture dict (with
  `video_id` set). It sets `fetch_source=handoff` and `handoff_used=true` /
  `handoff_source_path=<path>` on the resulting capture so audit downstream
  can see the provenance.
- **Refetch is preserved for weaker fetches:** `metadata_only`, `blocked`,
  or empty fetch results do **not** write a handoff. The subprocess refetches
  and the fresh attempt is logged in the inbox (subject to overwrite
  protection, see 2.2).

### 2.2 Inbox overwrite protection (`youtube_to_kb.py`)

- New `QUALITY_RANK` table:
  `full=4 > partial=3 > metadata_only=2 > blocked=1 > none=0`.
- New `_find_existing_capture_for_video_id(video_id)` walks
  `inbox/raw/youtube/*.json`, parses each, filters by `video_id`, and returns
  the capture with the **highest** rank (ties: most recent file mtime wins).
- `write_capture()` now:
  1. Computes a rank for the new capture and the existing one.
  2. Sets `capture["overwrite_decision"]` with `existing_path`,
     `existing_quality`, `new_quality`, `overwrite: bool`, and a human-readable
     `reason` (e.g. "new quality 'metadata_only' (rank 2) < existing 'full'
     (rank 4); overwrite refused").
  3. If the new capture has a strictly **lower** rank, returns the existing
     path **without writing** the new file. The new capture is otherwise
     written normally.
- `_print_capture_summary()` now echoes the overwrite decision to stderr so
  the operator can see what happened without re-parsing the capture file.

### 2.3 Documentation updates

- `README.md` — new "Fetch-result handoff + inbox overwrite protection
  (v0.3.84)" section + new v0.3.84 row in the changelog.
- `docs/commands/youtube-kb-import-command.md` — new v0.3.84 subsection with
  rank table and handoff example.
- `docs/workflows/youtube-video-kb-import-workflow.md` — new v0.3.84 section
  describing how the handoff prevents the 429→metadata_only race.
- `docs/commands/material-kb-import-command.md` — new v0.3.84 paragraphs
  under YouTube Quality Gate.
- `docs/workflows/material-kb-import-workflow.md` — new v0.3.84 subsection
  in Chinese mirroring the command doc.

### 2.4 Test updates

- `tests/run_youtube_import_smoke.py` — added `_clear_inbox_for_video()`
  helper and call it in **smoke 6** (yt-dlp unavailable is reported). Without
  the cleanup, the test reads a stale `full` capture from a prior run and
  cannot observe the new `metadata_only` provider attempts.
- `tests/run_fetch_layer_smoke.py` — added `_clear_inbox_for_video()` helper
  and call it in **smoke 4** (router records fetch fallback) for the same
  reason.
- `tests/run_fetch_layer_smoke.py` — added new **smoke 6**
  (`smoke_6_router_handoff_passes_fetch_result`) that:
  1. Cleans inbox + handoff dir for the test video_id.
  2. Runs the router with the YouTube URL + `HERMES_YTDLP_FIXTURE_*` env so
     the in-process fetch layer returns `full`.
  3. Asserts the router wrote exactly one handoff file under
     `tmp/material_fetches/`.
  4. Asserts the router item records `handoff_used: true`,
     `fetch_result_json_path`, and `fetch_quality: full`.
  5. Asserts the inner subprocess's capture file records
     `handoff_used: true` and `handoff_source_path` so the provenance is
     auditable from the inbox file too.

## 3. Verification (regression / new behavior)

### 3.1 Smoke tests — all 8 suites green

```
ALL SMOKE TESTS PASSED (3/3)
ALL BATCH SMOKE TESTS PASSED (5/5)
ALL RENDER SMOKE TESTS PASSED (6/6)
ALL IMAGE LOCALIZATION SMOKE TESTS PASSED (8/8)
ALL MATERIAL ROUTER SMOKE TESTS PASSED (4/4)
ALL WEB ARTICLE SMOKE TESTS PASSED (5/5)
ALL YOUTUBE IMPORT SMOKE TESTS PASSED (14/14)
ALL FETCH LAYER SMOKE TESTS PASSED (6/6)   ← new smoke 6 added
```

Total: 51 tests / 51 passed.

### 3.2 Other gates

```
py_compile:        OK
check_kb:          PASS (0 hard, 0 soft)
check_pages_sync:  PASS (65 / 65 byte-identical)
update_site:       All steps completed successfully
audit_kb_state:    PASS_WITH_WARNINGS (36 warnings — all pre-existing v0.3.83-era)
```

### 3.3 Real dry-run regression — `https://youtu.be/arj7oStGLkU`

- In-process fetch layer: all four providers (direct captionTracks × multiple
  languages, yt-dlp, youtube-transcript-api) returned empty text or HTTP 429
  → `metadata_only`.
- Router: correctly **skipped** the handoff path (handoff is `full` /
  `partial` only), subprocess refetched, also got `metadata_only`.
- Item result:
  - `fetch_quality: metadata_only`
  - `import_allowed: False`
  - `import_block_reason: metadata-only YouTube fetch has no transcript body`
  - `handoff_used: False` (correctly NOT triggered)
  - `status: DRY_RUN_OK` (dry-run is reportable; import is correctly blocked)
  - `provider_attempts: 14` (all four providers × multiple languages, with
    honest reasons — `caption endpoint returned empty text`, `HTTP Error
    429: Too Many Requests`, `transcript-api returned no text`,
    `all transcript providers failed; metadata only`)

**Conclusion:** real-network `metadata_only` correctly bypasses the handoff
and the dry-run does NOT write a KB entry.

### 3.4 Inbox overwrite behavior — manual fixture scenario

```
# inbox state before smoke 6: full capture for video_id=ytfixture123
# cleared by _clear_inbox_for_video() at test start
# subprocess runs yt-dlp unavailable → metadata_only capture
# write_capture(): rank 2 < (no existing) → overwrite=true, writes
# capture file now has overwrite_decision: overwrite=true, reason="no existing capture for video_id; normal write"
```

This proves a fresh `metadata_only` capture is still written when no prior
capture exists. The protection only kicks in when an existing `video_id` is
encountered.

## 4. What did NOT change (hard constraints respected)

- No `git reset` / `git reset --hard` / force push.
- No `git add -A` — every commit is per-file.
- No KB entry written (real dry-run, not import).
- No download of YouTube video files.
- No use of cookies, login state, or impersonation bypass.
- No fabrication of transcript text.
- No modification of existing `summary.md` / `notes.md`.
- No re-fetch of WeChat content, no re-download of WeChat images.
- No PDF-claim — `PDF remains unsupported` (smoke 13 still passes).
- `inbox/raw/wechat/*.json` and `inbox/raw/web/*.json` were never touched.
- `tmp/material_fetches/` is gitignored; the 18 files accumulated during
  smoke tests are not committed.
- Existing 65 KB entries + 65 docs items + 65 site items are byte-identical
  (check_pages_sync PASS).

## 5. Files changed (staged for commit)

```
M  .gitignore
M  README.md
M  scripts/material_to_kb.py
M  scripts/youtube_to_kb.py
M  tests/run_fetch_layer_smoke.py
M  tests/run_youtube_import_smoke.py
M  docs/commands/material-kb-import-command.md
M  docs/commands/youtube-kb-import-command.md
M  docs/workflows/material-kb-import-workflow.md
M  docs/workflows/youtube-video-kb-import-workflow.md
A  reports/youtube_fetch_handoff_overwrite_protection_v0.3.84_20260701.md
```

## 6. Next Steps (still open after v0.3.84)

These were already in the v0.3.83 report's Next Steps and remain open — they
are not part of v0.3.84 and were intentionally **not** attempted in this
commit:

1. **Find a stable YouTube video with public full transcript + non-flaky
   network** so the handoff path can be exercised end-to-end on a real URL.
   - The three real dry-runs (Steve Jobs, Ken Robinson, Tim Urban) all hit
     HTTP 429 or empty captions.
   - One real-network import would prove the handoff's value beyond the
     fixture smoke test. Defer until a stable target is identified.
2. **Add a per-provider rate-limit backoff (still optional, off-policy).**
   - The chain's current 429 behavior is honest reporting, not bypass.
     Backoff would smooth retries but is not on the critical path.
3. **Promote `tmp/material_fetches/` cleanup to a `tmp-cleanup` cron job.**
   - The directory accumulates 1 file per router run; the fixture smoke test
     added 18+ files in 10 minutes. A weekly cleanup would keep it bounded.
4. **Add a dedicated `tmp/material_fetches/cleanup` script for ad-hoc use.**
   - Trivial `find … -mtime +7 -delete`, but only worth it if (3) isn't
     already covered.

## 7. COMMIT / PUSH (filled in after `git push`)

(see git log output below)
