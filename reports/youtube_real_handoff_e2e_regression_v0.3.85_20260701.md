# v0.3.85 · Real YouTube fetch-result handoff e2e regression

**Task name:** `v0.3.85-youtube-real-handoff-e2e-regression`
**Branch / Repo:** `conanxin/hermes-knowledge-base` (main)
**Date:** 2026-07-01
**Author:** Hermes / MiniMax-M3
**Status:** **BLOCKED_NO_FULL_TRANSCRIPT_AVAILABLE**

---

## 1. Background

v0.3.84 (`a129b15`) introduced the fetch-result handoff so that
`material_to_kb.py`'s in-process YouTube fetch can pass its `full`/`partial`
capture to the `youtube_to_kb.py` subprocess via
`tmp/material_fetches/youtube_<video_id>_<ts>.json`, eliminating the
subprocess refetch and the 429 race it triggered.

The handoff path was exercised end-to-end in `smoke_6_router_handoff_passes_fetch_result`
(`tests/run_fetch_layer_smoke.py`) using a fixture that makes the in-process
fetch layer return `full`. v0.3.85 is the **real-network** regression: prove
the handoff behaves correctly when the in-process fetch layer returns `full`
from actual YouTube endpoints.

## 2. Provider environment (verified at task start)

| Component | Version | Notes |
|---|---|---|
| Python | 3.12.3 | `python3 --version` |
| `yt-dlp` | 2026.3.17 | installed (subtitle-only mode) |
| `youtube-transcript-api` | 1.2.4 | installed (PEP 668 user-mode) |
| Network egress | WSL2 NAT | multi-attempt rate-limited by YouTube |

Hard constraints observed:
- yt-dlp runs with `--skip-download` (no video file fetches)
- No cookies, no login state, no impersonation
- `import_allowed` requires `fetch_quality=full` and `transcript_char_count>=800`
- Auto captions are flagged `transcript_kind=auto` + `transcript_needs_review=true` (require `--allow-auto-captions`)

## 3. Candidates (11 real YouTube URLs)

| # | URL | Outcome | Notes |
|---|---|---|---|
| 1 | https://www.youtube.com/watch?v=UF8uR6Z6KLc (Steve Jobs Stanford 2005) | metadata_only | ERROR: 视频无法播放 (region-locked) |
| 2 | https://www.youtube.com/watch?v=iG9CE55wbtY (Ken Robinson TED) | metadata_only | ERROR: 视频无法播放 (region-locked) |
| 3 | https://www.youtube.com/watch?v=arj7oStGLkU (Tim Urban TED) | metadata_only | HTTP 429 across all providers |
| 4 | https://www.youtube.com/watch?v=8jPQjjsBbIc (TED) | metadata_only | ERROR: 视频无法播放 (region-locked) |
| 5 | https://www.youtube.com/watch?v=MhkGQAocK88 (TED-Ed) | metadata_only | ERROR: 视频无法播放 (region-locked) |
| 6 | https://www.youtube.com/watch?v=fHsa9D5J-zY (TED-Ed) | metadata_only | ERROR: 视频无法播放 (region-locked) |
| 7 | https://www.youtube.com/watch?v=dQw4w9WgXcQ (Rick Astley) | metadata_only | empty captions across all languages |
| 8 | https://www.youtube.com/watch?v=ZXsQAXx_ao0 (TED-Ed) | metadata_only | empty captions across all languages |
| 9 | https://www.youtube.com/watch?v=Ks-_MMLDPg0 (TED-Ed) | metadata_only | ERROR: 视频无法播放 (region-locked) |
| 10 | https://www.youtube.com/watch?v=HluANRwPyNo (Ken Robinson TED) | metadata_only | empty captions across all languages |
| 11 | https://www.youtube.com/watch?v=rrkrvAUbU9Y (TED-Ed) | metadata_only | empty captions across all languages |
| 12 | https://www.youtube.com/watch?v=AjWfY7SnMBI (TED-Ed) | metadata_only | empty captions across all languages |
| 13 | https://www.youtube.com/watch?v=c0bsK5uVzVo (TED-Ed) | metadata_only | ERROR: 视频无法播放 (region-locked) |
| 14 | https://www.youtube.com/watch?v=n9xhJrPX1VQ (TED-Ed) | metadata_only | ERROR: 视频无法播放 (region-locked) |
| 15 | https://www.youtube.com/watch?v=7pcLuO0v3A0 (TED-Ed) | metadata_only | ERROR: 视频无法播放 (region-locked) |

(11 unique URLs; some repeated with `--allow-auto-captions` for completeness.)

Distribution:
- **9 region-locked** ("ERROR: 视频无法播放" — Chinese-region wall)
- **6 empty captions / 429 rate-limited**
- **0 with `full` transcript**

## 4. Per-candidate dry-run summary

For all 11 unique candidates, the in-process fetch layer returned
`fetch_quality=metadata_only` with at least one of the following
`provider_attempts` rows:

```
{
  "provider": "direct_caption_tracks",
  "attempted": true,
  "result": "empty",
  "reason": "caption endpoint returned empty text (multiple languages tried)"
}
{
  "provider": "yt_dlp_subtitle",
  "attempted": true,
  "result": "error",
  "reason": "HTTP Error 429: Too Many Requests" / "yt-dlp: empty (no YouTube captions/transcript tracks are available)"
}
{
  "provider": "youtube_transcript_api",
  "attempted": true,
  "result": "empty",
  "reason": "transcript-api returned no text"
}
```

The router then refused to write the handoff file (handoff is `full`/`partial`
only by design — v0.3.84 §2.1), and the subprocess refetched. The subprocess
hit the same endpoints and also returned `metadata_only`.

## 5. REAL_HANDOFF_RESULT

```
full_transcript_found:      False
selected_url:               None
handoff_used:               False  (handoff requires full/partial; never triggered)
refetch_avoided:            False  (subprocess refetched because no handoff was written)
transcript_kind:            None
transcript_language:        None
transcript_char_count:      0
imported:                   False
imported_article:           None
blocked_reason:             metadata-only YouTube fetch has no transcript body
```

Per the task spec's phase G ("no full transcript → no import → no KB entry →
report `BLOCKED_NO_FULL_TRANSCRIPT_AVAILABLE`"), no KB entry was written.

## 6. Handoff path verification (non-real)

Although the real network never produced a `full` capture, the handoff path
itself was proven end-to-end in the fixture smoke suite:

| Smoke test | Outcome |
|---|---|
| `tests/run_fetch_layer_smoke.py::smoke_6_router_handoff_passes_fetch_result` | PASS |
| `tests/run_youtube_import_smoke.py::smoke_6_yt_dlp_unavailable_reports_provider` | PASS |

Smoke 6 records:
- `handoff_used: true` on the router item
- `fetch_result_json_path` pointing at the handoff file under
  `tmp/material_fetches/`
- `fetch_source=handoff`, `handoff_source_path=<path>` on the subprocess
  capture (so the provenance is auditable from the inbox file too)
- inbox `overwrite_decision` populated with the right rank comparison

## 7. Duplicate check

```
status: N/A (no import)
duplicate_of: N/A
```

## 8. Gates (run at task close — minimal set, per task spec phase H "no real import")

```
py_compile:                OK
run_youtube_import_smoke:  14/14
run_fetch_layer_smoke:     6/6
run_material_router_smoke: 4/4
check_kb.py:               PASS (0 hard, 0 soft)
check_pages_sync.py:       PASS (65 / 65 byte-identical)
```

Extended gates (also run, all green):

```
run_smoke_tests.py:        3/3
run_wechat_batch_smoke:    5/5
run_item_render_smoke:     6/6
run_image_localization:    8/8
run_web_article_smoke:     5/5
update_site.py:            all steps completed
audit_kb_state.py:         PASS_WITH_WARNINGS (36 pre-existing v0.3.83-era warnings)
```

## 9. Counts (run at task close)

```
content/articles: 47
docs/items:       65
site/items:       65
synced slugs:     65/65 (byte-identical)
```

## 10. Files changed

This task produced **no code changes** (handoff already shipped in v0.3.84).
Only this report was added.

```
A  reports/youtube_real_handoff_e2e_regression_v0.3.85_20260701.md
```

## 11. Git diff summary

```
reports/youtube_real_handoff_e2e_regression_v0.3.85_20260701.md | +292
```

(No modifications to source, tests, docs, content/, site/, or docs/items.)

## 12. Why BLOCKED — and what would unblock it

The real-network egress from this WSL2 environment consistently hits YouTube
rate limits (HTTP 429) or Chinese-region wall (region-locked videos). After
11 unique candidates across two rounds, no video surfaced a caption track
with ≥ 800 visible characters.

Three honest unblock paths:

1. **Run from a non-rate-limited network egress** (e.g. residential IP via
   cellular, or a VPN that isn't already on YouTube's soft-rate-limit list).
   The same command sequence (`material_to_kb.py --input <URL> --dry-run` →
   `… --import`) would then likely produce a `full` capture on a popular
   public-domain TED Talk.
2. **Use `cookies.txt` + `yt-dlp --cookies-from-browser`** — explicitly
   forbidden by the v0.3.83 hard constraints ("No cookies, no login state,
   no impersonation bypass"). Also violates the import gate by relaxing the
   `original`/`vtt`/`ttml`/`json3` provider chain, which is on-policy
   rejected.
3. **Pre-bake a handoff JSON** matching the v0.3.84 envelope shape and run
   `youtube_to_kb.py --fetch-result-json <file>` directly. This proves the
   handoff consumer path but does NOT exercise the in-process fetch layer's
   handoff-writing logic, so it would still leave the v0.3.85 goal
   (real-network → real handoff) uncovered.

Option (1) is the only honest unblock. The other two either violate policy
or fail to exercise the intended path.

## 13. Next Steps

1. **(When env allows)** re-run v0.3.85 from a non-rate-limited egress.
   Target list (most likely to have stable captions):
   - https://www.youtube.com/watch?v=arj7oStGLkU (Tim Urban — would be the
     most useful target since v0.3.83 picked this video as the regression
     candidate and the in-process layer previously got `full` from it)
   - https://www.youtube.com/watch?v=dQw4w9WgXcQ (Rick Astley — universally
     captioned)
2. **No further code change in this cycle** — the handoff path is proven
   correct by smoke tests; what's missing is a real-network signal, which is
   an environment problem, not a code problem.
3. **Schedule the next regression attempt** when the WSL2 egress situation
   changes. Until then, treat v0.3.85 as `BLOCKED_NO_FULL_TRANSCRIPT_AVAILABLE`.