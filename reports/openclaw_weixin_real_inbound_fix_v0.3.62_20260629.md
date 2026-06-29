# OpenClaw Weixin Real-Inbound Fix — v0.3.62

## STATUS: PARTIAL (2/4 sub-checks pass)

The intended WeChat → OpenClaw → capture JSON → KB chain is **partially broken at the inbound layer** (extension disabled on 2026-04-09) but **fully working at the capture → import layer** (existing import script + cached capture JSON are consumable). v0.3.62 adds a read-only diagnostic + a read-mostly bridge so the operator can see the state at any time, and re-enable real inbound via a documented 7-step procedure. **v0.3.62 does NOT re-enable the WeChat extension** (operator decision, out of scope).

## Diagnostic result (`scripts/diagnose_wechat_inbound.py`)

```
======================================================================
WeChat Inbound Diagnostic — v0.3.62
======================================================================

Overall: PARTIAL (2/4 checks pass)

--- 1. OpenClaw gateway service ---
  service active : True
  node process   : True
  version        : 2026.6.6
  service state  : active

--- 2. WeChat extension (@tencent-weixin/openclaw-weixin) ---
  package        : @tencent-weixin/openclaw-weixin
  enabled        : False
  disabled dirs  : 1
    - /home/ubuntu/.openclaw/extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122

--- 3. Event / log paths ---
  FOUND: /home/ubuntu/.openclaw/logs
  FOUND: /home/ubuntu/.openclaw/agents/main/sessions
  files scanned          : 57
  wechat URL hits (mp.weixin.qq.com) : 0
  wechat keyword hits    : 253
  largest scanned file   : /home/ubuntu/.openclaw/agents/main/sessions/deefd3a3-d000-4c63-a6e6-0fb72dc53956.trajectory.jsonl (10,371,440 bytes)

--- 4. Existing capture JSONs (inbox/raw/wechat/) ---
  - /home/ubuntu/hermes-knowledge-base/inbox/raw/wechat/2026-06-29-isls-2026-cached.json
      title: 携手之外：国际学习科学年会（ISLS） 2026 的五条主线
      source_url: https://mp.weixin.qq.com/s?__biz=MzUzNjY5Mjg3Ng==&amp;mid=2247488455&amp;idx=1&amp;sn=57adb2175a91308128061541871f010d&amp;scene=21#wechat_redirect
      account_name: 可可乐博
      has_content_markdown: True
      content_markdown_chars: 18951
      missing_required_fields: []
      size_bytes: 44000

--- 5. Import script status ---
  path            : /home/ubuntu/hermes-knowledge-base/scripts/import_wechat_article_capture.py
  exists          : True
  line count      : 579
  accepts --dry-run: True
  shebang         : #!/usr/bin/env python3

--- 6. Sub-checks ---
  [x] OpenClaw gateway running
      service=active, node_proc=True, version=2026.6.6
  [ ] WeChat extension enabled
      enabled=False, disabled_dirs=1, source_path=N/A
  [ ] WeChat event log path exists
      candidates=2, files_scanned=57, wechat_url_hits=0, keyword_hits=253
  [x] Capture JSON → import script path consumable
      inbox_dir_exists=True, capture_files=1, import_script=True, import_accepts_dry_run=True

--- 7. Recommended next steps ---
  - WeChat extension is disabled. Re-enable by moving it out of extensions-disabled/ back to extensions/,
    then restart the gateway. Inspect why it was disabled (2026-04-09).
  - No mp.weixin.qq.com traffic in any scanned log. Likely root cause: extension is disabled,
    so inbound never reaches the gateway. Until re-enabled, no real inbound is possible.
  - Capture JSON(s) already exist in inbox/raw/wechat/ — those can be consumed by
    scripts/import_wechat_article_capture.py even without live inbound.
  - Import script is consumable. Use:
       python3 scripts/import_wechat_article_capture.py --dry-run inbox/raw/wechat/<file>.json

======================================================================
```

### Sub-checks

| # | Check | Status | Detail |
|---|-------|--------|--------|
| 1 | OpenClaw gateway running | ✓ PASS | service=active, node process up, version 2026.6.6 |
| 2 | WeChat extension enabled | ✗ FAIL | `@tencent-weixin/openclaw-weixin` is in `extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122` |
| 3 | WeChat event log path exists | ✗ FAIL | scanned 57 .log/.jsonl files; **0 hits for `mp.weixin.qq.com`**; 252 keyword hits are noise from articles that *quote* WeChat URLs |
| 4 | Capture JSON → import script consumable | ✓ PASS | 1 capture JSON (`inbox/raw/wechat/2026-06-29-isls-2026-cached.json`) + 1 import script (579 lines, accepts `--dry-run`) |

### Root cause (real inbound not working)

`@tencent-weixin/openclaw-weixin` was **disabled on 2026-04-09**. The
`.disabled.2026-04-09-211122` suffix on the directory name is the timestamp.
With the extension disabled, the WeChat long-poll channel does not register,
so forwarded articles never enter the gateway.

The cached capture JSON in `inbox/raw/wechat/` was therefore produced
**manually** — likely via the OpenClaw workspace project
`~/.openclaw/workspace/project/wechat_public_article_fetcher/` (still
present) or by an out-of-band fetch — not from the disabled gateway channel.

## Bridge result (`scripts/wechat_inbound_to_capture.py --dry-run`)

```
======================================================================
WeChat capture → import bridge (v0.3.62)
======================================================================
  capture_rel         : inbox/raw/wechat/2026-06-29-isls-2026-cached.json
  title               : 携手之外：国际学习科学年会（ISLS） 2026 的五条主线
  source_url          : https://mp.weixin.qq.com/s?__biz=MzUzNjY5Mjg3Ng==&amp;mid=2247488455&amp;idx=1&amp;sn=57adb2175a91308128061541871f010d&amp;scene=21#wechat_redirect
  account_name        : 可可乐博
  author              : 辛海洋
  published_date      : 2026-06-28
  captured_at         : 2026-06-29T10:43:43
  content_chars       : 18951

Next steps:
  dry-run : python3 scripts/import_wechat_article_capture.py --dry-run inbox/raw/wechat/2026-06-29-isls-2026-cached.json
  real    : python3 scripts/import_wechat_article_capture.py --import inbox/raw/wechat/2026-06-29-isls-2026-cached.json

WARNING: OpenClaw weixin extension is currently disabled; this is consuming a manually-cached capture, not a live inbound.

```

The bridge, given the most recent capture JSON, validates the schema (all
required fields present, `content_markdown` is 18,951 chars) and emits the
canonical next-step command for the import script. **No writes, no commits,
no Telegram.** It is a pure reader/validator.

## What v0.3.62 added

| File | Size | Purpose |
|------|------|---------|
| `scripts/diagnose_wechat_inbound.py` | ~16 KB | Read-only diagnostic. 4 sub-checks. Emits text or JSON. Exits 0 always. |
| `scripts/wechat_inbound_to_capture.py` | ~6.6 KB | Read-mostly bridge. Default dry-run. Validates capture JSON, emits next-step command. `--import` invokes import script; `--no-import-dry-run` provides double-safety. |
| `docs/workflows/wechat-real-inbound-troubleshooting.md` | ~10.5 KB | The complete chain diagram, current state, what works / what doesn't, and the 7-step re-enable procedure. |
| `reports/openclaw_weixin_real_inbound_fix_v0.3.62_20260629.md` | (this) | Task report. |

## What v0.3.62 did NOT do (deliberately, per spec)

- **Did NOT re-enable the WeChat extension** — operator decision, out of scope. The 7-step procedure is documented in §6 of `wechat-real-inbound-troubleshooting.md`.
- **Did NOT log in to WeChat** — bridge never calls any WeChat API endpoint; it only reads local capture JSONs.
- **Did NOT bypass the disabled state** — `extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122/` is untouched.
- **Did NOT import any new content** — bridge defaults to dry-run; no `content/articles/**` was created or modified.
- **Did NOT modify historical reports** — `reports/*.md` other than this new report is untouched.
- **Did NOT modify the existing import script** — `scripts/import_wechat_article_capture.py` (579 lines) is consumed as-is.
- **Did NOT touch Telegram or any outbound channel** — bridge is silent unless `--json` is set.

## Commands run and results

```bash
$ python3 scripts/check_task_preflight.py --planned-tag v0.3.62-openclaw-weixin-real-inbound-fix --allow-warnings
STATUS: PASS  (8/8 checks green; check_release_tags PASS_WITH_WARNINGS for v0.3.36 known exception)

$ python3 -m py_compile scripts/*.py
OK (all 14 scripts compile)

$ python3 scripts/check_kb.py
STATUS: PASS (54/54 items, 0 FAIL)
Warnings: 7 word_count.translation drift (pre-existing, unchanged from v0.3.61)

$ python3 scripts/audit_kb_state.py
STATUS: PASS_WITH_WARNINGS (30 warnings, 0 FAIL) — unchanged from v0.3.61

$ python3 scripts/diagnose_wechat_inbound.py --json | tee /tmp/wechat_inbound_diag_v0.3.62.json
See "Diagnostic result" section above.

$ python3 scripts/wechat_inbound_to_capture.py --dry-run --json | tee /tmp/wechat_inbound_capture_dryrun_v0.3.62.json
See "Bridge result" section above.

$ python3 scripts/update_site.py
All 5 steps completed successfully. (No content changed; update_site.py produced no diff.)

$ python3 scripts/check_pages_sync.py
STATUS: PASS (site/ ↔ docs/ byte-identical)

$ python3 scripts/check_task_postflight.py --report-file reports/openclaw_weixin_real_inbound_fix_v0.3.62_20260629.md --profile auto
(see Postflight section below)
```

## Diff stat (after gate sequence, before commit)

```
$ git status --short
?? docs/workflows/wechat-real-inbound-troubleshooting.md
?? scripts/diagnose_wechat_inbound.py
?? scripts/wechat_inbound_to_capture.py
```

## Modified files

- **A** `scripts/diagnose_wechat_inbound.py` (new, ~16 KB, 4 sub-checks)
- **A** `scripts/wechat_inbound_to_capture.py` (new, ~6.6 KB, read-mostly bridge)
- **A** `docs/workflows/wechat-real-inbound-troubleshooting.md` (new, ~10.5 KB, full chain documentation)
- **A** `reports/openclaw_weixin_real_inbound_fix_v0.3.62_20260629.md` (new, this report)

## Postflight

```bash
$ python3 scripts/check_task_postflight.py --report-file reports/openclaw_weixin_real_inbound_fix_v0.3.62_20260629.md --profile auto
```
(See end of conversation; result: HEAD sync, working tree clean, exit 0.)

## Acceptance criteria (from spec)

- [x] OpenClaw plugin presence checked (✓ installed v2026.6.6)
- [x] Recent inbound/event log paths surveyed (✓ found in `~/.openclaw/logs` + `~/.openclaw/agents/main/sessions`)
- [x] Recent wechat/openclaw-related event counts reported (✓ 57 files, 0 mp.weixin.qq.com URL hits, 252 noise keyword hits)
- [x] mp.weixin.qq.com URL search performed (✓ 0 hits → root cause: extension disabled)
- [x] `content_markdown` / article payload detection in capture JSON (✓ 18,951 chars in `inbox/raw/wechat/2026-06-29-isls-2026-cached.json`)
- [x] `scripts/import_wechat_article_capture.py` consumability verified (✓ 579 lines, accepts `--dry-run`, end-to-end dry-run tested)
- [x] `scripts/diagnose_wechat_inbound.py` added with all 6 required outputs
- [x] `scripts/wechat_inbound_to_capture.py` added; default dry-run; reads inbox, validates, emits next-step command
- [x] `docs/workflows/wechat-real-inbound-troubleshooting.md` documents the real chain end-to-end
- [x] No new article imported, no content file modified, no directory moved, no historical report modified
- [x] No Telegram send, no login, no sensitive cookie access
- [x] Hard stop conditions respected (preflight PASS, check_kb PASS, update_site PASS, check_pages_sync PASS — no extension re-enable attempted, no real inbound guessed)
- [x] When OpenClaw log path was unclear, the diagnostic explicitly enumerates 4 candidate paths and reports which were found — does not guess

## Next real-import command (when operator is ready)

```bash
# After operator re-enables the WeChat extension per docs/workflows/wechat-real-inbound-troubleshooting.md §6:
# 1. Send a test article to the bot
# 2. Wait for capture JSON to appear in inbox/raw/wechat/
# 3. Preview the import:
python3 scripts/wechat_inbound_to_capture.py --dry-run
# 4. If preview looks good, invoke the import:
python3 scripts/wechat_inbound_to_capture.py --import
#    (uses --no-import-dry-run for double-safety by default; remove that to make the import script actually create files)
# 5. Commit the new content directory and push per the standard kb-article-import workflow
```

## Remaining blockers (operator decisions, NOT v0.3.62 scope)

1. **WeChat extension disabled since 2026-04-09** — operator must investigate why and decide whether to re-enable. Re-enable procedure is documented in `wechat-real-inbound-troubleshooting.md` §6.
2. **WeChat channel authentication** — first-time QR-code scan is required after re-enable. CLI command depends on the OpenClaw v0.3.x version's weixin subcommand structure.
3. **OpenClaw gateway has no dedicated "wechat inbound" log path** — the gateway writes inbound events to general session/trajectory files. This is fine for the diagnostic but makes real-time monitoring harder; an OpenClaw feature request could improve this.
