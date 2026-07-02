# Hermes Knowledge Base — Operator Playbook

> **Audience:** anyone (human or agent) who needs to ingest external materials into this knowledge base.
> **Stable since:** v0.3.99 (this document) — built on top of v0.3.96 full gate runner, v0.3.97 deterministic WeChat manifests, v0.3.98 tooling checkpoint.
> **Status:** ✅ Live. Update on material-handling changes only; trivial per-record notes belong in CHANGELOG.md.

---

## 1. Current Stable Baseline

As of `v0.3.99`:

- **main HEAD:** last commit on `main` (run `git log -1 --oneline`)
- **Full gate status:** PASS_WITH_WARNINGS (0 hard failures; 29 soft `tag_topic_count_out_of_range` warnings in `audit_kb_state.py`, unchanged since v0.3.91 — these are content characteristics, not regression signals)
- **KB size:** 66 entries (target stable)
- **Material matrix:** see §3
- **Known warnings:** see §1.1

If the gate is anything other than PASS or PASS_WITH_WARNINGS, **stop and read** — do not push.

### 1.1 Known soft warnings (informational only)

- `audit_kb_state.py` → `[tag_topic_count_out_of_range] (29 findings)`: some 2026 long-form Chinese-language articles have topics/tags outside soft ranges (topics [3,8], tags [6,12]). These are kept-as-exception; do **not** "fix" by lowering ranges in `audit_kb_state.py` — ranges are project policy, not per-instance. Cleanup requires an additive tags/topics pass per entry.

---

## 2. Daily Import Entry Points

### 2.1 Single material

```bash
# Dry-run (default — recommended first step)
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --dry-run

# Real import (writes KB entry; needs gates to pass)
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --import
```

`scripts/material_to_kb.py` is the **unified router** — it auto-detects:
- WeChat URL (`mp.weixin.qq.com`)
- generic web URL
- YouTube URL
- local `.html` / `.md` / `.txt` file
- local `.pdf` file

For non-PDF files without an extension hint, pass `--input-list` with one path per line.

### 2.2 Batch import

```bash
# Build input list
cat > tmp/materials.txt <<'EOF'
https://mp.weixin.qq.com/s/abc123
https://example.com/post/2026/foo
./inbox/quarantine/cached_article.html
EOF

# Dry-run
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run

# Real import
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --import
```

For **WeChat batch** with multiple URLs, use the dedicated batch script (better deduplication reporting):

```bash
python3 scripts/wechat_batch_import.py --input wechat_urls.txt --dry-run --run-id batch_$(date +%Y%m%d_%H%M%S)
python3 scripts/wechat_batch_import.py --input wechat_urls.txt --import --run-id batch_$(date +%Y%m%d_%H%M%S)
```

**Always pass `--run-id <id>`** when calling `wechat_batch_import.py` programmatically. The script emits a single-line JSON summary on stdout with `json_report_path`; parse that line to find the deterministic manifest. Without `--run-id`, fallback to timestamp is racy when multiple invocations land in the same second (see v0.3.97 fix).

---

## 3. Supported Material Matrix

| Type | Command | Support condition | Hard stop | Common failure | Next step |
|---|---|---|---|---|---|
| WeChat URL | `material_to_kb.py --input "<weixin_url>"` | Article page reachable; HTML contains recognizable article block | `BLOCKED_FETCH_FAILED` (network), `BLOCKED_INCOMPLETE_TEXT` (article block not extracted) | Anti-bot blocking from WeChat servers | Use local HTML fallback (`--html-file`) |
| Local HTML/MD/TXT | `material_to_kb.py --input "<file>"` or `--input-list` | File exists and is readable; ≥ MIN_CHARS threshold | `BLOCKED_INCOMPLETE_TEXT` if file is empty / placeholder | File path wrong; MIME mismatch | Re-check path; verify file has actual content |
| Generic web URL | `material_to_kb.py --input "<url>"` | Publicly fetchable; `robots.txt` allows scraping; ≥ MIN_CHARS | `BLOCKED_FETCH_FAILED` (403/404/timeout), `BLOCKED_UNSUPPORTED` (robots.txt disallows), `BLOCKED_INCOMPLETE_TEXT` (paywall/loginwall rendered content) | Paywall, login required, JS-only rendering | Save page to `inbox/quarantine/` and use `--html-file` fallback |
| YouTube URL (full transcript) | `material_to_kb.py --input "<yt_url>"` | Manual or auto-transcript available; ≥ 800 visible chars ≥ 80 words ≥ 80 CJK chars | `BLOCKED_INCOMPLETE_TEXT` (no transcript, too short, low CJK) | No captions, captions disabled, transcripts unreliable | Provide `--input "<transcript.txt>"` instead (local transcript fallback supported) |
| Local PDF (text layer) | `pdf_to_kb.py --pdf "<file>"` or via `material_to_kb` | extractable text via pymupdf; ≥ MIN_CHARS | `BLOCKED_NEEDS_OCR` (no embedded text layer), `BLOCKED_INCOMPLETE_TEXT`, `BLOCKED_UNSUPPORTED` | Scanned PDF, image-only PDF | Use separate `pdf-ocr-kb-import` workflow (see `docs/import-recipes/PDF_OCR_LOCAL.md`) |
| Scanned PDF | — (no OCR here) | n/a — `pdf_to_kb.py` does not call Tesseract | `BLOCKED_NEEDS_OCR` | n/a | Switch to OCR workflow (`docs/import-recipes/PDF_OCR_LOCAL.md`); not handled by this KB's main import path |
| Release-backed assets (large files) | (metadata-only import) | Author large media → GitHub Release; link via `metadata.asset_*` fields | n/a | n/a | Read `docs/RELEASES.md`; do not commit `.mp4` / `.mp3` (`.gitignore` already covers them) |

---

## 4. WeChat Article Flow

### 4.1 Single article

```bash
python3 scripts/material_to_kb.py --input "https://mp.weixin.qq.com/s/abc123" --dry-run
# Review the dry-run output, check 3-layer dedup index, observe status
python3 scripts/material_to_kb.py --input "https://mp.weixin.qq.com/s/abc123" --import
```

### 4.2 Batch articles (recommended for ≥ 3 URLs)

```bash
python3 scripts/wechat_batch_import.py --input wechat_urls.txt --import \
    --run-id batch_2026MMDD_HHMMSS 2>&1 | tee logs/wechat_batch_$(date +%Y%m%d).log
```

The batch script:
- parses all URLs once,
- maintains a 3-layer dedup index (URL hash, title+account+date, content hash),
- writes a manifest at `reports/wechat_batch_import_<run_id>.{md,json}`,
- exits 2 if any post-import gate fails (do **not** commit/push until the manifest shows all PASS).

### 4.3 Local HTML fallback

If WeChat serves anti-bot HTML (HTTP 200 but JavaScript-only render), download the rendered page in a regular browser and save as `.html`:

```bash
python3 scripts/wechat_batch_import.py --html-file saved_article.html --import \
    --run-id fallback_$(date +%Y%m%d_%H%M%S)
```

### 4.4 Image localization

For WeChat-hosted images, the import path downloads them into `content/articles/<year>/<slug>/images/` and rewrites the markdown. **No manual intervention** required.

### 4.5 Deduplication

3 layers, all automatic:

1. **URL hash** — exact source-url match.
2. **Title + account + published_date** — catches re-shared articles.
3. **Content hash** — catches articles whose URLs differ but body is identical (re-hosted / re-translated duplicates).

Duplicate items are marked `SKIPPED_DUPLICATE` in import mode and `DRY_RUN_DUPLICATE` in dry-run mode.

### 4.6 Manifest reports

The batch script writes two files per run (with `--run-id`):

- `reports/wechat_batch_import_<run_id>.md` — human-readable markdown summary table
- `reports/wechat_batch_import_<run_id>.json` — machine-readable per-input detail

These manifests are **session artifacts** — never committed. They live in `reports/` until the next sweep (or are archived as task reports).

### 4.7 Hard rules

- **No login, no QR-code scan, no reading main-account cookies.** The import scripts never read `.env`, never call Telegram, never invoke browsers. If a WeChat article is paywall-locked, the user (human) is responsible for saving the rendered HTML locally first.
- WeChat anti-bot blocks this script fairly often. **Always plan for several BLOCKED_FETCH_FAILED results per batch and re-queue those manually.**

---

## 5. Generic Web Article Flow

```bash
python3 scripts/material_to_kb.py --input "https://example.com/post/2026/foo" --dry-run
python3 scripts/material_to_kb.py --input "https://example.com/post/2026/foo" --import
```

### 5.1 Robots.txt policy

- `scripts/web_article_to_kb.py` fetches `/robots.txt` first.
- If robots.txt disallows scraping the input path → `BLOCKED_UNSUPPORTED`.
- If robots.txt is unreachable or unparseable → **proceeds** (fail-open, log a notice).

### 5.2 Paywall / loginwall

HTTP 200 + JS-rendered paywall → `BLOCKED_INCOMPLETE_TEXT` (visible text below MIN_CHARS).

### 5.3 Local HTML fallback

Save the page with Ctrl-S "Webpage, Complete" in a browser, then:

```bash
python3 scripts/material_to_kb.py --input saved_page.html --import
```

### 5.4 Duplicate handling

Same 3-layer dedup as WeChat (URL, title+account+date, content hash).

---

## 6. YouTube Flow

**Policy:** only import videos with a **full transcript**. metadata-only fetches are not importable. Partial transcripts require `--allow-partial-transcript` and are tagged accordingly.

### 6.1 Why we gate by transcript

- KB quality bar: every entry should have substantive body content.
- metadata-only entries are link rot waiting to happen — they add nothing readable.

### 6.2 Current caveat

- `youtube_to_kb.py` uses `yt-dlp` against YouTube's transcript API. **Transcript availability is unreliable** in the current environment — many videos return no captions (disabled by uploader, region-locked, no auto-caption track).
- A failed transcript fetch is `BLOCKED_INCOMPLETE_TEXT` with the reason in the capture JSON. Re-trying the same video often returns the same error — **this is YouTube-side, not our bug**.

### 6.3 Local transcript fallback

If you have a `.txt` / `.vtt` / `.srt` transcript saved locally:

```bash
python3 scripts/material_to_kb.py --input transcript.txt --import
# or
python3 scripts/material_to_kb.py --input video_id --input-list transcript_paths.txt --import
```

The router detects `.txt` / `.vtt` / `.srt` extensions and pipes them through the YouTube text-quality gate.

### 6.4 What we never do

- **No video download.** No `.mp4` files in repo, ever.
- **No cookie use.** No reading browser cookies, no Telegram-bot, no auth flow.
- **No re-fetching auto-captions when manual track exists.** Manual > auto quality.

### 6.5 Operational guidance

- For important YouTube content you want in the KB, **first secure a transcript** (download with browser extension or yt-dlp CLI on your own machine), then import the local `.txt`. Do not rely on the live API.
- A video with no manual captions and only auto-captions is borderline — auto-caption quality varies wildly. Reject unless the speaker is clear and the auto-caption is accurate.

---

## 7. PDF Flow

### 7.1 Two workflows (do not confuse)

This KB has **two** PDF flows:

1. **`pdf_to_kb.py`** (main repo, this codebase) — handles **extractable-text** PDFs only.
2. **`pdf-ocr-kb-import` workflow** (`docs/import-recipes/PDF_OCR_LOCAL.md`) — handles scanned / image-only PDFs, runs Tesseract OCR.

They are **separate** by design: the main import path refuses to silently OCR (OCR is expensive, error-prone, and easy to misuse).

### 7.2 Main import (text PDFs only)

```bash
python3 scripts/pdf_to_kb.py --pdf path/to/file.pdf --dry-run
python3 scripts/pdf_to_kb.py --pdf path/to/file.pdf --import
```

Or via the unified router:

```bash
python3 scripts/material_to_kb.py --input path/to/file.pdf --dry-run
```

### 7.3 Hard rule — no original PDF in repo

Do **not** commit original user PDFs to the repo. The import path extracts the body and metadata into `content/notes/<year>/<slug>/{metadata.yaml,source.md,summary.md,notes.md}`; the source PDF itself stays on your disk.

### 7.4 Smoke vs real import

- `tests/run_pdf_import_smoke.py` runs offline against a pymupdf-generated synthetic PDF fixture. 5 smoke cases are validated.
- It includes `smoke_post_git_diff_no_tracked_generated_dirty`: after the import step, asserts the smoke slug is NOT present in `docs/data/catalog.json`, `site/data/catalog.json`, or `index/*`. This is the v0.3.94 regression guard.

If the smoke fixture persistently appears in tracked `docs/data/catalog.json` etc., the import path has regressed — open an issue.

---

## 8. Release-Backed Assets Flow

For large media (videos, audio, hi-res images), use **GitHub Releases** for binary storage and link via metadata fields. Repo holds **only** markdown content + metadata + small thumbnails.

### 8.1 Storage policy

- `.mp4`, `.mp3`, `.flac`, `.webm`, `.mov`, `.wav` → **GitHub Releases** (not in repo).
- Cover images, lyrics, subtitles, README → repo (e.g., `docs/assets/<name>/`).
- Manifest lives in `metadata.yaml`'s `asset_*` fields.

### 8.2 Verification

`scripts/check_release_assets.py` runs on every full gate:

- finds all entries whose metadata has release-backed asset fields,
- validates `gh release view` returns matching assets,
- validates `docs/data/...` index entries match.

If check_release_assets fails:
1. open `reports/check_release_assets_<ts>.log`,
2. identify the entry whose assets are missing or malformed,
3. re-upload via `gh release upload <tag> <files>` or correct the metadata.

---

## 9. Gates: When and How to Run Them

### 9.1 Pre-edit quick check (sub-minute)

```bash
python3 scripts/run_full_gate.py --quick
```

7 steps; ~10-15s on a warm machine. Catches regressions in:
- py_compile,
- material_router_smoke,
- pdf_import_smoke,
- release_assets_smoke,
- check_release_assets,
- check_kb,
- check_pages_sync.

Run before claiming "task complete" for any edit.

### 9.2 Pre-commit / pre-push full gate (~1-2 min)

```bash
python3 scripts/run_full_gate.py --json \
    --output reports/full_gate_run_$(date +%Y%m%d_%H%M%S).json
```

17 steps. Catches everything quick does, plus:
- run_smoke_tests (all `tests/run_*.py`),
- run_wechat_batch_smoke (5/5 deterministic since v0.3.97),
- run_youtube_import_smoke,
- run_fetch_layer_smoke,
- check_release_tags (SHA sanity on both protected tags),
- update_site,
- audit_kb_state.

### 9.3 Status meanings

| Status | Exit | Meaning | Action |
|---|---|---|---|
| `PASS` | 0 | All steps passed; no tracked dirty | Proceed with commit/push |
| `PASS_WITH_WARNINGS` | 0 | All steps passed but `audit_kb_state` reported soft warnings | Proceed; warnings are documented kept-as-exceptions |
| `FAILED_CLEANLINESS` | 1 | One or more tracked files are dirty (modified, not yet committed) | Commit your changes first; do not push |
| `FAILED_GATE` | 1 | One or more steps exited non-zero | Read the JSON `failed_step_names` and tail `stderr_tail`; fix and rerun |

The JSON report includes per-step `status`, `exit_code`, `duration_seconds`, `stdout_tail`, `stderr_tail`, and the working-tree summary. Save it under `reports/full_gate_run_<task>_<ts>.json` for archival.

---

## 10. BLOCKED / FAILED Status Reference

| Status | Meaning | Committable? | User next step |
|---|---|---|---|
| `BLOCKED_UNSUPPORTED` | Host/source not recognized, or `robots.txt` disallows | No | Local HTML fallback, or wait until support is added |
| `BLOCKED_FETCH_FAILED` | Network error, non-2xx HTTP, robots.txt unreachable / unparseable with strict policy | No | Retry; save page locally for fallback; check URL spelling |
| `BLOCKED_INCOMPLETE_TEXT` | Page fetched but text unusable (too short, paywall, JS-render-only, no transcript, low CJK) | No | Provide richer local content; for YouTube, supply local transcript |
| `BLOCKED_NEEDS_OCR` | PDF has no extractable text layer | No | Switch to `pdf-ocr-kb-import` workflow |
| `SKIPPED_DUPLICATE` | Item already in KB by 3-layer dedup | No (intentional) | Skip this item; check existing entry |
| `DRY_RUN_OK` / `DRY_RUN_DUPLICATE` | Dry-run results; nothing was written | n/a | Re-run with `--import` to commit |
| `FAILED_GATE` | Import ran but `check_kb` / `update_site` / `audit_kb_state` exited non-zero | No | Read JSON manifest gate_results; fix the underlying content / metadata |
| `FAILED_IMPORT` | Unhandled exception during a single input in a batch | (Batch continues) | Fix the offending input; batch does not abort |

A blocked item is **not a bug** — it is an explicit signal the importer refuses to write a low-quality entry. Take the suggested next step, or open the issue tracker.

---

## 11. Git Commit Discipline

### 11.1 Per-file add — never `git add -A`

```bash
git add <file1> <file2> ...
# NOT: git add -A
# NOT: git add .
```

`git add -A` would stage the 15+ untracked `reports/full_gate_run_*.json` files lying around; never want that.

### 11.2 No force push

`git push origin main` only. If push is rejected (no fast-forward), `git fetch && git pull --ff-only` and resolve locally.

### 11.3 Never commit

- `tmp/` — working state
- `inbox/` — quarantine / staging
- `tmp/material_fetches`, `tmp/youtube_subs` — fetch artifacts
- `*.mp4` / `*.mp3` / `*.flac` / `*.webm` / `*.wav` — `.gitignore` handles these
- `reports/wechat_batch_import_*.{md,json}` — session manifests
- `reports/full_gate_run_*.json` — gate runtime artifacts (only commit the one you intend to archive, with `--run-id`-style naming)
- `DRY_RUN_PREVIEW/` — never exists in repo; never create it

### 11.4 OK to commit

- `reports/<task>_vX.Y.Z_YYYYMMDD.md` — formal task reports
- `reports/full_gate_run_<task>_<ts>.json` — when archiving for a specific task
- Anything in `content/{articles,notes}/<year>/<slug>/` — that's the KB
- `docs/OPERATOR_PLAYBOOK.md`, `docs/AGENT_COMMANDS.md` — operator docs

### 11.5 Tag discipline

- **Do not move** any existing tag (e.g., `v0.3.91-material-ingestion-stable-baseline`, `v0.3.92-bingzhu-you-mv-assets`, `v0.3.96-full-gate-runner-and-tag-sanity`).
- Only a new stable baseline or feature tag gets a new tag. See `scripts/check_release_tags.py` for the current inventory.
- The full gate verifies tag SHAs each run; do not skip this gate.

---

## 12. New Machine Recovery

```bash
# 1. Clone
git clone https://github.com/conanxin/hermes-knowledge-base.git
cd hermes-knowledge-base

# 2. Sync
git checkout main
git fetch origin main --tags
git pull --ff-only origin main

# 3. Verify baseline health
python3 scripts/run_full_gate.py --quick
```

If the quick gate exits 0 with PASS or PASS_WITH_WARNINGS, you're ready. If it fails, you have a workspace / dependency issue — likely missing Python packages. Install requirements:

```bash
pip install -r requirements.txt   # if present
```

Common deps: `pymupdf` (fitz), `requests`, `beautifulsoup4`, `pyyaml`, `yt-dlp`. If a `pip install` OOM-kills or SIGKILLs, use a virtualenv:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

The first full gate after a clean install also runs `update_site.py`, which can take 30-60s.

---

**See also:**

- `docs/AGENT_COMMANDS.md` — detailed agent-only command reference (longer, more technical)
- `docs/RELEASES.md` — Release index (large media storage policy)
- `docs/import-recipes/PDF_OCR_LOCAL.md` — OCR fallback workflow for scanned PDFs
- `scripts/run_full_gate.py` — gate runner source (run `--list` for the full step plan)
- `reports/CHANGELOG.md` — release-by-release change log
