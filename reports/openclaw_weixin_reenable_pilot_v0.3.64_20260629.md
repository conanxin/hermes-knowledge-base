# OpenClaw Weixin Re-enable Pilot — v0.3.64

## STATUS: PARTIAL_AUTH_REQUIRED

The pilot performed a controlled re-enable → observe → **rollback** sequence and
discovered that the file-move approach alone is **insufficient** to activate
the WeChat channel in OpenClaw. Real inbound is not yet working because:

1. `openclaw channels list --all` reports the channel as `not installed,
   not configured, disabled` even after a clean Path A re-enable + restart.
2. The official catalog expects version **2.4.3**; the on-disk package is
   **1.0.2**. The catalog-correct path is `openclaw channels add openclaw-weixin`,
   which v0.3.64 did **not** run (operator decision; would change installed
   version).
3. The channel description in the catalog is "Personal WeChat messaging
   via **QR-code login**" — i.e. operator QR-code scanning is a prerequisite
   for any real inbound. v0.3.64 deliberately did **not** attempt login
   (would require human-in-the-loop action + persistent personal WeChat
   session + reading sensitive auth cookies).

The pilot was safely **rolled back** to the pre-pilot state (extension
disabled). Final diagnostic: 2/4 sub-checks pass (identical to v0.3.62
baseline).

## Before / after diagnostic

### BEFORE re-enable (pre-pilot baseline)

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
  wechat keyword hits    : 258
  largest scanned file   : /home/ubuntu/.openclaw/agents/main/sessions/deefd3a3-d000-4c63-a6e6-0fb72dc53956.trajectory.jsonl (10,371,440 bytes)

--- 4. Existing capture JSONs (inbox/raw/wechat/) ---
  - /home/ubuntu/hermes-knowledge-base/inbox/raw/wechat/2026-06-29-isls-2026-cached.json
      title: 携手之外：国际学习科学年会（ISLS） 2026 的五条主线
      source_url: https://mp.weixin.qq.co```
*(truncated; full output: `python3 scripts/diagnose_wechat_inbound.py`)*

| # | Check | Status |
|---|-------|--------|
| 1 | OpenClaw gateway running | ✓ PASS |
| 2 | WeChat extension enabled | ✗ FAIL |
| 3 | WeChat event log path exists | ✗ FAIL |
| 4 | Capture JSON → import script consumable | ✓ PASS |

**Result: PARTIAL (2/4)**

### AFTER re-enable (Path A: file-move only, no rollback yet)

| # | Check | Status |
|---|-------|--------|
| 1 | OpenClaw gateway running | ✓ PASS |
| 2 | WeChat extension enabled | ✓ PASS (file-move) |
| 3 | WeChat event log path exists | ✗ FAIL (no real inbound yet) |
| 4 | Capture JSON → import script consumable | ✓ PASS |

**Result: PARTIAL (3/4)** — sub-check #2 reports PASS, but
`openclaw channels list --all` still reports the channel as `not installed`.

### FINAL (post-rollback, current state)

| # | Check | Status |
|---|-------|--------|
| 1 | OpenClaw gateway running | ✓ PASS |
| 2 | WeChat extension enabled | ✗ FAIL (back to disabled) |
| 3 | WeChat event log path exists | ✗ FAIL (no real inbound) |
| 4 | Capture JSON → import script consumable | ✓ PASS |

**Result: PARTIAL (2/4)** — same as baseline.

## Why the file-move alone is insufficient — root cause

After `mv` + `systemctl --user restart openclaw-gateway`:

```
$ openclaw channels list --all | grep -A 1 weixin
- openclaw-weixin: not installed, not configured, disabled
```

The gateway journal still shows:
```
Jun 29 15:11:12 ... [gateway] http server listening (2 plugins: memory-core, telegram; 1.9s)
```
i.e. only 2 plugins loaded — `openclaw-weixin` is **not** among them.

The official catalog entry for the package is:

```json
{
  "name": "@tencent-weixin/openclaw-weixin",
  "openclaw": {
    "channel": { "id": "openclaw-weixin", "label": "Weixin", ... },
    "install": {
      "npmSpec": "@tencent-weixin/openclaw-weixin@2.4.3",
      "expectedIntegrity": "sha512-dPQbidUNWigC6V10vGW4i+GLH09x+6zUhafZRjuxkJ9GDu8o62WBsnUTojp4KqUH756hz+t2v9khiCRSi0dBDw==",
      "minHostVersion": ">=2026.3.22"
    }
  }
}
```

This says:
- The catalog expects version **2.4.3**, not 1.0.2 (which is on disk).
- A specific sha512 integrity hash is required.
- Host version >=2026.3.22 (we're on 2026.6.6 — OK).

The file-move puts the package on disk where the gateway can see it, but
the gateway's channel manager treats it as "not installed" because:

1. The version doesn't match what the catalog expects
2. The package wasn't installed via the catalog's integrity-checked channel
3. The channel config (`openclaw channels add openclaw-weixin`) was never run

The correct next step (which v0.3.64 **did not** perform) is:

```bash
openclaw channels add openclaw-weixin
# This will:
# 1. Verify integrity against sha512-dPQbid...
# 2. Install @tencent-weixin/openclaw-weixin@2.4.3
# 3. Register the channel
# Then:
openclaw channels login openclaw-weixin
# This will display a QR code for the operator to scan
# with their personal WeChat app to authenticate.
```

## Why disablement reason = not found

Searched the following for evidence of why the extension was disabled on
2026-04-09 21:15 (the timestamp in the directory suffix
`openclaw-weixin.disabled.2026-04-09-211122`):

- `~/.openclaw/logs/` — 10 files total; none from 2026-04-09
- `journalctl --user -u openclaw-gateway` for 2026-04-08 to 2026-04-10 —
  no entries (journal rolled over)
- `~/.openclaw/workspace/memory/` — 3 files from that range; only
  `2026-04-08-2249.md` exists, and it's a generic session-startup log
  (no weixin mention)
- `~/.openclaw/workspace/memory-indexed/` — `wechat-article-exporter-research.md`
  exists but is from 2026-03-21 and discusses the
  `wechat-article/wechat-article-exporter` open-source tool, not the
  OpenClaw channel extension
- `~/.openclaw/patches/` — only `apply-openclaw-telegram-send-gate-patch.sh`
  (telegram, not weixin)
- All `.openclaw` files dated 2026-04-08 to 2026-04-11 searched for
  `weixin` / `tencent-weixin` / `openclaw-weixin` — **0 hits**
- `find ~/.openclaw -name "*disabl*"` — only the `extensions-disabled/`
  directory itself

**Conclusion**: The disablement was performed out-of-band; the reason is
not in the local filesystem audit trail. The directory's child mtime
(2026-03-22) reflects the original install; the parent directory
(`extensions-disabled/`) was mtime 2026-04-09 21:15 until v0.3.64's
pilot, confirming the disable timestamp.

## Did the pilot move the extension directory?

**Yes, temporarily.** Sequence:

1. **15:09:35** — `mv ~/.openclaw/extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122 ~/.openclaw/extensions/openclaw-weixin` (Path A)
2. **15:10:29** — `systemctl --user restart openclaw-gateway` → active
3. **15:10:38** — diagnostic ran → PARTIAL (3/4)
4. **15:11:00** — observed `openclaw channels list --all` shows `not installed`; root cause identified
5. **15:12:46** — **rollback**: `mv ~/.openclaw/extensions/openclaw-weixin ~/.openclaw/extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122` + `systemctl --user restart openclaw-gateway`
6. **15:12:51** — final diagnostic: PARTIAL (2/4), same as baseline

## Gateway restart result

`systemctl --user status openclaw-gateway --no-pager` after each restart:

- **Pre-pilot (v0.3.62 baseline)**: `Active: active (running) since Wed 2026-06-24 15:36:36 CST; 4 days ago`, version 2026.4.9
- **After Path A restart (15:10:29)**: `Active: active (running) since Mon 2026-06-29 15:10:29 CST; 5s ago`, version 2026.4.9 — **HEALTHY**
- **After rollback restart (15:12:46)**: `Active: active (running) since Mon 2026-06-29 15:12:46 CST; 5s ago`, version 2026.4.9 — **HEALTHY**

The full pre-restart ExecStartPre patch hook (TG-SEND-GATE-2) succeeded
both times (`code=exited, status=0/SUCCESS`).

## Does the channel need QR / auth?

**Yes.** The catalog description is literally:

> "Personal WeChat messaging via QR-code login."

This is the same authentication model as `wechaty` and similar personal
WeChat gateway tools. The operator must scan a QR code with their
personal WeChat app once per (re-)activation to establish a long-poll
session token. The token is stored in `~/.openclaw/auth-profiles.json`
(which currently has no weixin entry, confirming no session exists).

v0.3.64 did **NOT** run `openclaw channels login openclaw-weixin` because:

- The user profile rule states "登录微信/绕过限制/读取敏感 cookie 时停止"
- The spec says "若需要扫码认证，停下并报告二维码/命令，不要假装已认证"
- A real inbound is impossible without it, so the entire pilot
  objective (smoke-test real inbound) cannot complete

## Did we receive real mp.weixin.qq.com inbound?

**No.** No `mp.weixin.qq.com` URL was found in any OpenClaw log/session
file at any point in the pilot. The 0 hit count is unchanged from
v0.3.62 / v0.3.63 baselines. This is expected: even if the channel
were activated, no test article was forwarded (we don't have the QR
session), and v0.3.64 explicitly did not attempt to forward anything.

## Did a new capture JSON appear?

**No.** `inbox/raw/wechat/` still contains only the one pre-existing
capture: `2026-06-29-isls-2026-cached.json` (44,000 bytes,
18,951 chars of `content_markdown`, all required fields present).
No new capture was generated by the pilot.

## Bridge dry-run result

`scripts/wechat_inbound_to_capture.py --dry-run --json` consumes the
pre-existing capture and emits the next-step command:

```json
{
  "capture_rel": "inbox/raw/wechat/2026-06-29-isls-2026-cached.json",
  "title": "携手之外：国际学习科学年会（ISLS） 2026 的五条主线",
  "source_url": "https://mp.weixin.qq.com/s?...",
  "account_name": "可可乐博",
  "author": "辛海洋",
  "published_date": "2026-06-28",
  "captured_at": "2026-06-29T10:43:43",
  "content_chars": 18951,
  "next_step_dry_run": "python3 scripts/import_wechat_article_capture.py --dry-run inbox/raw/wechat/2026-06-29-isls-2026-cached.json",
  "next_step_import": "python3 scripts/import_wechat_article_capture.py --import inbox/raw/wechat/2026-06-29-isls-2026-cached.json"
}
```

## Proof of no content import

`git status --short` after the pilot and after rollback:

```
 M docs/workflows/wechat-real-inbound-troubleshooting.md
```

`git diff --stat`:

```
 docs/workflows/wechat-real-inbound-troubleshooting.md | 92 +++++++++++++++++-----
 1 file changed, 73 insertions(+), 19 deletions(-)
```

**No `content/articles/**` file was created, modified, imported, or
moved. No capture JSON was generated or deleted. No KB slug was
introduced or changed. The bridge was only run in dry-run mode
(`--dry-run --json`); the `--import` flag was never used.**

## Was the real import command run?

**No.** v0.3.64 did **NOT** run:

- `python3 scripts/wechat_inbound_to_capture.py --import` (would invoke
  the import script, which would create a new KB directory)
- `python3 scripts/import_wechat_article_capture.py --import` (the
  underlying import command)

The bridge was run only in `--dry-run` mode. The import script was
exercised only by `python3 scripts/import_wechat_article_capture.py
--dry-run <file>` (also dry-run, no files created).

## Smoke test outcome

The pilot did not run a "10-minute wait" smoke watch because the
prerequisite (real channel activation + QR auth) was not met and is
explicitly out of scope. There is no point waiting for an inbound that
cannot arrive. The pilot was rolled back to leave the system in its
pre-pilot state.

## Commands run

```bash
$ python3 scripts/check_task_preflight.py --planned-tag v0.3.64-openclaw-weixin-reenable-pilot --allow-warnings
STATUS: PASS  (8/8 checks green; check_release_tags PASS_WITH_WARNINGS for v0.3.36 known exception)

$ python3 -m py_compile scripts/*.py
OK (all 14 scripts compile)

$ python3 scripts/check_kb.py
STATUS: PASS (54/54 items, 0 FAIL); 7 word_count drift WARNs (unchanged from v0.3.63)

$ python3 scripts/audit_kb_state.py
STATUS: PASS_WITH_WARNINGS (30 warnings, 0 FAIL) — unchanged from v0.3.63

$ python3 scripts/diagnose_wechat_inbound.py --json | tee /tmp/wechat_inbound_before_v0.3.64.json
STATUS: PARTIAL (2/4)  [BEFORE — disabled]

# search 2026-04-09 disablement evidence: not found

$ mv ~/.openclaw/extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122 \
     ~/.openclaw/extensions/openclaw-weixin
$ systemctl --user restart openclaw-gateway
$ sleep 5

$ python3 scripts/diagnose_wechat_inbound.py --json | tee /tmp/wechat_inbound_after_reenable_v0.3.64.json
STATUS: PARTIAL (3/4)  [file-move made sub-check #2 PASS, but gateway plugins list still 2 not 3]

$ openclaw channels list --all | grep weixin
- openclaw-weixin: not installed, not configured, disabled

# Decision: rollback (Path A is insufficient; Path B requires operator decision + QR auth)

$ mv ~/.openclaw/extensions/openclaw-weixin \
     ~/.openclaw/extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122
$ systemctl --user restart openclaw-gateway
$ sleep 5

$ python3 scripts/diagnose_wechat_inbound.py
STATUS: PARTIAL (2/4)  [POST-ROLLBACK — back to baseline]

$ python3 scripts/wechat_inbound_to_capture.py --dry-run --json
{"content_chars": 18951, ...}

$ python3 scripts/update_site.py
All 5 steps completed successfully. (No content changed; update_site.py produced no diff.)

$ python3 scripts/check_pages_sync.py
STATUS: PASS (site/ ↔ docs/ byte-identical)

$ python3 scripts/check_task_postflight.py --report-file reports/openclaw_weixin_reenable_pilot_v0.3.64_20260629.md --profile auto
(see Postflight section below)
```

## Diff stat

```
$ git diff --stat
 docs/workflows/wechat-real-inbound-troubleshooting.md | 92 +++++++++++++++++-----
 1 file changed, 73 insertions(+), 19 deletions(-)
```

## Modified files

- **M** `docs/workflows/wechat-real-inbound-troubleshooting.md` — §6 split
  into "Path A (file move)" vs "Path B (catalog install)", added §6.5
  v0.3.64 pilot findings. Updated step ordering (authenticate step
  correctly placed after install, not after file-move).

## Remaining blockers (operator decisions, NOT v0.3.64 scope)

1. **Run `openclaw channels add openclaw-weixin`** to install version 2.4.3
   (currently on-disk is 1.0.2). This is the catalog-correct path. Would
   require operator approval to change installed version.
2. **Run `openclaw channels login openclaw-weixin`** to authenticate
   the channel via QR-code scan. This is the human-in-the-loop step
   that v0.3.64 explicitly skipped. Requires operator's personal WeChat
   app to scan a QR code.
3. **Investigate why the extension was originally disabled on
   2026-04-09 21:15**. No local evidence found. The disable may have
   been intentional (e.g. compliance review, security concern, or
   upstream breaking change in the weixin protocol). Operator's
   judgment is required before re-enabling.

## Next real-import command (when operator is ready)

```bash
# Step 1: install via the catalog
openclaw channels add openclaw-weixin
# (Verifies sha512-dPQbidUNWigC6V10vGW4i+GLH09x+6zUhafZRjuxkJ9GDu8o62WBsnUTojp4KqUH756hz+t2v9khiCRSi0dBDw==
#  and installs @tencent-weixin/openclaw-weixin@2.4.3)

# Step 2: authenticate (operator scans QR code)
openclaw channels login openclaw-weixin

# Step 3: verify diagnostic
python3 scripts/diagnose_wechat_inbound.py
# All 4 sub-checks should now pass.

# Step 4: forward a test article to the bot
# Wait for capture JSON to appear in inbox/raw/wechat/

# Step 5: dry-run preview
python3 scripts/wechat_inbound_to_capture.py --dry-run

# Step 6: real import (if dry-run looks good)
python3 scripts/wechat_inbound_to_capture.py --import

# Step 7: commit the new content directory and push per standard kb-article-import workflow
```

## Acceptance criteria (from spec)

- [x] preflight PASS
- [x] check_kb.py PASS (54/54)
- [x] audit_kb_state.py PASS_WITH_WARNINGS (30, unchanged)
- [x] BEFORE diagnostic captured to `/tmp/wechat_inbound_before_v0.3.64.json`
- [x] AFTER re-enable diagnostic captured to `/tmp/wechat_inbound_after_reenable_v0.3.64.json`
- [x] POST-ROLLBACK diagnostic matches baseline (2/4)
- [x] Disabled reason search performed; explicitly reported as "not found"
- [x] Minimal re-enable (file move) was performed; gateway was restarted
- [x] Gateway status captured (active, healthy, 2 plugins)
- [x] No QR / auth bypass attempt
- [x] No 10-minute wait smoke test (correctly skipped — channel not actually active)
- [x] Real import command NOT executed; only dry-run
- [x] System rolled back to pre-pilot state
- [x] No `~/.openclaw` files committed to git (git status shows only the docs file)
- [x] No content file modified, no article imported
- [x] No Telegram sent
- [x] No browser cookies read
- [x] No WeChat API bypass

## Postflight

```bash
$ python3 scripts/check_task_postflight.py --report-file reports/openclaw_weixin_reenable_pilot_v0.3.64_20260629.md --profile auto
```
Result: PASS_WITH_WARNINGS (postflight profile auto only checks report fields; full verification requires `--tag` flag).
