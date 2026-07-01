# v0.3.83 YouTube Provider Env Real Import

> **Task tag:** `v0.3.83-youtube-provider-env-real-import`
> **Date:** 2026-07-01 (Asia/Shanghai)
> **Repo:** `~/projects/hermes-knowledge-base`
> **Baseline commit:** `f6729a46324abee5f9229507e774cfe293732012` (dev handoff checkpoint)
> **Final local HEAD:** `f6729a46324abee5f9229507e774cfe293732012` = `origin/main`
> **Decided result:** No real YouTube KB import; environment + report + docs only

---

## STATUS

`BLOCKED_NO_FULL_TRANSCRIPT_AVAILABLE`

The YouTube provider chain returns `metadata_only` for every dry-run in this environment:
direct `captionTracks` endpoints, `yt-dlp`, and `youtube-transcript-api` all return empty text.
An in-process fetch for one URL temporarily succeeded via `yt-dlp` (12 671 chars en manual) but
the project-wide `material_to_kb.py` subprocess call that writes the canonical capture file hit
`HTTP 429: Too Many Requests` and downgraded that result to `metadata_only` for the file on disk.
Per task rules, no half-baked KB entry is written; only docs + report + `.gitignore` are changed.

---

## SUMMARY

- `yt-dlp 2026.3.17` was already installed and works on the CLI; `youtube-transcript-api 1.2.4`
  was missing and has now been installed (PEP 668 required `--user --break-system-packages`).
- Both providers degraded gracefully: missing both falls back to `metadata_only`. Installing only
  `yt-dlp` lets it occasionally return a `full` transcript for the first URL per rate-limit
  window, but does not survive the in-process + subprocess double-call pattern in
  `material_to_kb.py`.
- 3 public YouTube URLs were exercised (Steve Jobs Stanford, Ken Robinson TED, Tim Urban TED).
  All 3 capture files were written under `inbox/raw/youtube/` but **none is committed** —
  they are `metadata_only`, which the task explicitly bans as a half-baked KB entry.
- Public-web, WeChat, and existing KB routes are unchanged. All gates still pass:
  `py_compile`, all 8 smoke groups (3+5+6+8+4+5+14+5 = 50 assertions), `check_kb.py 65/65`,
  `update_site.py`, `audit_kb_state.py` (`0 HARD`, 36 WARN), `check_pages_sync.py`.

---

## PROVIDER_ENV

- **python:** `Python 3.12.3` (`python3 --version`)
- **pip:** `pip 24.3.1 from /usr/lib/python3.12/site-packages/pip (python 3.12)`
- **yt_dlp:** `2026.3.17` (already installed at
  `/home/conanxin/.local/lib/python3.12/site-packages/yt_dlp`; CLI in `PATH` as `yt-dlp`)
- **youtube_transcript_api:** `1.2.4` (just installed today, same user-site path) — `defusedxml
  0.7.1` installed as a dependency
- **install_performed:** `python -m pip install --user --break-system-packages --upgrade
  youtube-transcript-api` (PEP 668 marker blocked the unflagged install; switched to per-user
  site-packages). No virtualenv used.
- **CLI smoke:** `yt-dlp --version` → `2026.3.17` ✅
- **Module smoke:** `python3 -c "import yt_dlp, youtube_transcript_api"` → OK ✅

---

## REAL_REGRESSION

- **dry_runs:** 3 URLs, all `BLOCKED_NO_FULL_TRANSCRIPT_AVAILABLE`
  - `https://www.youtube.com/watch?v=UF8uR6Z6KLc` — Steve Jobs 2005 Stanford Commencement (v0.3.82
    failure case reused)
  - `https://www.youtube.com/watch?v=iG9CE55wbtY` — Ken Robinson "Do Schools Kill Creativity?" TED
    (likely manual English subs)
  - `https://www.youtube.com/watch?v=arj7oStGLkU` — Tim Urban "Inside the Mind of a Master
    Procrastinator" TED (v0.3.82 timeout case reused)
- **full_transcript_found:** False on disk for all 3 capture files. The in-process fetch for Tim
  Urban DID return `fetch_quality: full` with `transcript_kind: manual` (zh-CN, 4 244 chars), but
  the follow-up `youtube_to_kb.py` subprocess call (which writes the canonical
  `inbox/raw/youtube/<slug>.json`) returned `metadata_only` because of `HTTP 429` rate limiting.
- **imported:** False
- **imported_article:** N/A
- **blocked_reason:** `metadata-only YouTube fetch has no transcript body` for all 3 capture
  files written by the project's canonical `youtube_to_kb.py` subprocess

---

## PROVIDER_ATTEMPTS

`inbox/raw/youtube/<slug>.json` (committed: none — these are dry-run artifacts and were kept
untracked per the "don't delete untracked artifact" rule).

### 1) Steve Jobs 2005 — `UF8uR6Z6KLc`

- direct_captionTracks: 40 attempts; 0 ok; all `empty` ("caption endpoint returned empty text",
  HTTP 200 with empty body) across 8 languages × manual/auto × 5 formats
- yt-dlp: 1 attempt; status `empty`; reason `HTTP 429` (Too Many Requests) + impersonation
  warning ("no impersonate target is available")
- youtube-transcript-api: 1 attempt; status `empty`; reason "transcript-api returned no text"
- metadata-only fallback: 1 attempt; status `ok`, char_count = 549 (title + description only)
- capture `fetch_quality: metadata_only`; `transcript_kind: none`; `transcript_char_count: 0`
- Side note: a direct `yt-dlp --skip-download --list-subs` call (after a 30 s wait) listed 8
  manual subtitle tracks for this video, confirming the video itself is public and has captions —
  the bot detection is at the runtime HTTP layer, not at the catalog layer.

### 2) Ken Robinson — `iG9CE55wbtY`

- direct_captionTracks: 40 attempts; 0 ok; same empty-body pattern across 7 languages
- yt-dlp: 1 attempt; status `empty`; reason `HTTP 429` + impersonation warning
- youtube-transcript-api: 1 attempt; status `empty`; reason "transcript-api returned no text"
- metadata-only fallback: 1 attempt; status `ok`, char_count = 1 383
- capture `fetch_quality: metadata_only`; `transcript_kind: none`; `transcript_char_count: 0`

### 3) Tim Urban — `arj7oStGLkU`  ✅ *only this one briefly passed an in-process fetch*

- direct_captionTracks: 40 attempts; 0 ok; same empty-body pattern across 7 languages
- yt-dlp: 1 attempt; status `empty`; reason `HTTP 429` (subprocess call after in-process call)
- youtube-transcript-api: 1 attempt; status `empty`; reason "transcript-api returned no text"
- metadata-only fallback: 1 attempt; status `ok`, char_count = 1 725
- capture on disk: `fetch_quality: metadata_only`
- **However**, the in-process `material_to_kb.py` fetch (one run earlier in the same process)
  recorded `fetch_quality: full` with three `yt-dlp` `provider_attempts: ok` rows:
  - `en / manual / vtt` — 12 671 chars
  - `zh-CN / manual / vtt` — 4 244 chars
  - `zh-Hans / auto / vtt` — 10 645 chars

The `material_to_kb.py` material-level report (`reports/material_import_20260701_213421.json`)
shows the `full` quality, but the canonical capture file ends up `metadata_only` because the
project always re-runs `youtube_to_kb.py` as a subprocess for the same URL, and that second
hit on `yt-dlp`'s timedtext endpoints triggers `HTTP 429`. This is consistent with the v0.3.82
baseline; the new providers made a one-shot in-process win possible but did not change the
capture-file behaviour under the current rate-limit window.

---

## DUPLICATE_CHECK

- **status:** not run (no import happened; nothing to dedupe against)
- **duplicate_of:** N/A
- Existing KB already contains `F3fCktnkBbc` (Conan O'Brien Harvard Commencement, 2026-06-25) and
  `zYKJdzyAviE` (Ali Abdaal "Financial Freedom is Easy", 2026-07-01), neither of which was
  re-touched.

---

## COUNTS

- **content/articles:** 65 metadata.yaml files across `content/articles/`,
  `content/legacy-knowledge/`, `content/notes/`, `content/projects/`,
  `content/resource_collections/` (matches `check_kb.py` baseline)
- **docs/items:** 65
- **site/items:** 65
- **synced slugs:** 65 (site docs complete triple-match)

---

## FILES_CHANGED

- `.gitignore` — added two ignored paths:
  - `tmp/`
  - `tmp/youtube_subs/`
- `docs/commands/youtube-kb-import-command.md` — added `### v0.3.83 provider environment
  (optional install)` block with the install commands and 4 hard guarantees
- `docs/workflows/youtube-video-kb-import-workflow.md` — same provider-environment block under
  maintenance notes
- `docs/commands/material-kb-import-command.md` — added `## v0.3.83 YouTube provider environment`
  with cross-references to the YouTube docs
- `docs/workflows/material-kb-import-workflow.md` — appended the provider-environment block
  after the v0.3.82 block
- `README.md` — added `### YouTube provider environment (v0.3.83)` section + a new changelog row
- `reports/youtube_provider_env_real_import_v0.3.83_20260701.md` — this report

NOT changed / NOT committed (kept as untracked dry-run evidence; the task bans deleting
untracked artifacts):

- `inbox/raw/youtube/2008-03-07-steve-jobs-2005-stanford-commencement-address.json`
- `inbox/raw/youtube/2007-01-06-do-schools-kill-creativity-sir-ken-robinson-ted.json`
- `inbox/raw/youtube/2016-04-06-inside-the-mind-of-a-master-procrastinator-tim-urban-ted.json`
- `reports/material_import_20260701_212600.{json,md}`
- `reports/material_import_20260701_212904.{json,md}`
- `reports/material_import_20260701_213421.{json,md}`
- `tmp/youtube_subs/*` (downloaded .vtt files; ignored by .gitignore but kept on disk)
- `reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629_finalcheck.json` (historical
  untracked from v0.3.63, not touched)

NOT touched:

- `python -m pip` site packages at `~/.local/lib/python3.12/site-packages/yt_dlp/` and
  `~/youtube_transcript_api/` (not in repo)
- No `.venv`, no `site-packages` in-repo, no video files, no cookies / login state, no
  impersonation bypass
- No public-web / wechat / existing KB entry content rewritten
- No `summary.md` / `notes.md` of any existing article overwritten
- No force push, no `git reset`, no `git add -A`

---

## COMMANDS_RUN

```bash
# Phase A — sync
git status --short
git status -sb
git branch --show-current
git fetch origin main --tags
git log --oneline -8
git pull --ff-only origin main
git rev-parse HEAD
git rev-parse origin/main
git merge-base --is-ancestor f6729a46324abee5f9229507e774cfe293732012 origin/main
python3 scripts/check_task_preflight.py \
    --planned-tag v0.3.83-youtube-provider-env-real-import \
    --classify-dirty --allow-warnings --json

# Phase B — providers
python3 --version
python3 -m pip --version
python3 -c "import importlib; ..."           # provider check (pre-install)
yt-dlp --version
python3 -m pip install --user --break-system-packages --upgrade youtube-transcript-api
python3 -c "import yt_dlp, youtube_transcript_api; ..."  # provider check (post-install)

# Phase D — three real dry-runs
mkdir -p tmp
python3 scripts/material_to_kb.py --input "https://www.youtube.com/watch?v=UF8uR6Z6KLc" --dry-run
python3 scripts/material_to_kb.py --input "https://www.youtube.com/watch?v=iG9CE55wbtY" --dry-run
python3 scripts/material_to_kb.py --input "https://www.youtube.com/watch?v=arj7oStGLkU" --dry-run
yt-dlp --skip-download --list-subs --no-update "https://www.youtube.com/watch?v=UF8uR6Z6KLc"

# Phase H — full gates
python3 -m py_compile scripts/*.py
python3 tests/run_smoke_tests.py
python3 tests/run_wechat_batch_smoke.py
python3 tests/run_item_render_smoke.py
python3 tests/run_image_localization_smoke.py
python3 tests/run_material_router_smoke.py
python3 tests/run_web_article_smoke.py
python3 tests/run_youtube_import_smoke.py
python3 tests/run_fetch_layer_smoke.py
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

---

## GATES

| gate | result |
| --- | --- |
| `py_compile scripts/*.py` | PASS |
| `tests/run_smoke_tests.py` | PASS (3/3) |
| `tests/run_wechat_batch_smoke.py` | PASS (5/5) |
| `tests/run_item_render_smoke.py` | PASS (6/6) |
| `tests/run_image_localization_smoke.py` | PASS (8/8) |
| `tests/run_material_router_smoke.py` | PASS (4/4) |
| `tests/run_web_article_smoke.py` | PASS (5/5) |
| `tests/run_youtube_import_smoke.py` | PASS (14/14) |
| `tests/run_fetch_layer_smoke.py` | PASS (5/5) |
| `scripts/check_kb.py` | PASS (65/65) |
| `scripts/update_site.py` | PASS |
| `scripts/audit_kb_state.py` | PASS_WITH_WARNINGS (HARD FAILURES: 0, WARNINGS: 36 — only pre-existing tag/topic soft-range observations, none introduced by v0.3.83) |
| `scripts/check_pages_sync.py` | PASS (site 65 == docs 65 == content 65) |

---

## REPORT

`reports/youtube_provider_env_real_import_v0.3.83_20260701.md` (this file)

---

## NEXT STEPS

1. **Rate-limit aware fetch path.** Today `material_to_kb.py` calls `youtube_to_kb.py` both
   in-process (for the preview) and as a subprocess (for the canonical capture). Two near-
   simultaneous `yt-dlp --write-subs` calls against the same video can trip YouTube's bot
   detector even when the first one succeeds. A future task could:
   - either skip the in-process `fetch_material` for `youtube_url` (let the subprocess be the
     single source of truth), or
   - cache the in-process result onto the item record and let `apply_fetch_result` always win
     over the stale subprocess `import_block_reason` (`metadata_only YouTube fetch has no
     transcript body`).
2. **`yt-dlp` impersonation target.** The `no impersonate target is available` warning is a
   separate signal that YouTube's anti-bot has tightened. Installing `curl-cffi` would let
   `yt-dlp` rotate through more browser fingerprints. This is a research task, not a v0.3.83
   concern (would change the chain's footprint and shouldn't be done silently).
3. **`--caption-provider yt-dlp --one-lang` short-circuit.** When the project knows the
   caller wants only English manual subs, a shorter `sub-langs` list reduces the surface area
   the rate limiter sees. This is a behaviour change so it should wait until we have a
   reproducible green in a less restricted network.
4. **Real-import retry.** A second `v0.3.84` (or live re-run of `v0.3.83`) from a fresh
   machine, or after waiting out the per-IP rate-limit window, has a reasonable chance of
   producing a clean `full` capture for Tim Urban (whose 3 successful `yt-dlp` rows were
   captured at 21:34 and prove the provider can pass the gate). Same hard constraints:
   no cookies, no video downloads, no fabricated subtitles.

---

*Last refreshed 2026-07-01 22:06 Asia/Shanghai. Hard rules observed throughout: no videos
downloaded, no cookies / login state, no impersonation bypass, no half-baked KB entry, no reset,
no force push, no `git add -A`, no overwrite of existing `summary.md` / `notes.md`, no delete of
untracked artifacts.*
