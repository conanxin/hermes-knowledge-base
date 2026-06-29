# WeChat Real-Inbound Troubleshooting

> **v0.3.62 — read-only diagnostic + minimal bridge.**  
> Does not enable the WeChat extension. Does not log in to WeChat. Does not bypass
> the disabled state. Documents the real chain so the operator can decide whether
> to flip the extension on.

## 1. The intended chain (real inbound)

```
┌──────────────────┐    ┌──────────────────┐    ┌────────────────────┐
│ WeChat user      │ →  │ @tencent-weixin/ │ →  │ OpenClaw gateway   │
│ forwards article │    │ openclaw-weixin  │    │ (long-poll channel)│
│ to bot           │    │ channel (via     │    │                    │
│                  │    │  getUpdates)     │    │                    │
└──────────────────┘    └──────────────────┘    └─────────┬──────────┘
                                                         │
                                                         │ event/log written
                                                         ▼
                                              ┌────────────────────┐
                                              │ capture JSON in    │
                                              │ inbox/raw/wechat/  │
                                              │ (canonical schema) │
                                              └─────────┬──────────┘
                                                        │
                                                        ▼
                                              ┌────────────────────┐
                                              │ scripts/import_    │
                                              │ wechat_article_    │
                                              │ capture.py         │
                                              │ (consumes JSON →   │
                                              │  KB 5-file)        │
                                              └─────────┬──────────┘
                                                        │
                                                        ▼
                                              ┌────────────────────┐
                                              │ content/articles/  │
                                              │ YYYY/YYYY-MM-DD-   │
                                              │ wechat-<account>-  │
                                              │ <title>/           │
                                              └────────────────────┘
```

**Five steps, three of which depend on the WeChat extension being enabled.**

## 2. Current state (as of v0.3.62, 2026-06-29)

Re-run anytime with:

```bash
python3 scripts/diagnose_wechat_inbound.py
```

Last run result (v0.3.62):

| Sub-check | Status | Detail |
|---|---|---|
| OpenClaw gateway running | ✓ PASS | service=active, version=2026.6.6 |
| WeChat extension enabled | ✗ FAIL | `@tencent-weixin/openclaw-weixin` is in `extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122` (disabled on 2026-04-09) |
| WeChat event log path exists | ✗ FAIL | scanned 57 log/jsonl files; **0 hits for `mp.weixin.qq.com`** (only keyword noise from other articles that *quote* WeChat URLs) |
| Capture JSON → import script consumable | ✓ PASS | 1 capture JSON (`2026-06-29-isls-2026-cached.json`) + 1 import script (579 lines, accepts `--dry-run`) |

**Overall: PARTIAL (2/4 sub-checks pass).**

### Why "no real inbound" — root cause

`@tencent-weixin/openclaw-weixin` was disabled on **2026-04-09** (see the
`.disabled.2026-04-09-211122` suffix in the directory name). With the extension
disabled, the WeChat long-poll channel does not register, so forwarded WeChat
articles never enter the gateway. This explains why:

- No `mp.weixin.qq.com` URL appears in any scanned OpenClaw log/jsonl.
- The 252 "wechat keyword hits" are noise from other articles that *quote*
  WeChat URLs in their content (e.g. references list), not real inbound.

The cached capture JSON (`inbox/raw/wechat/2026-06-29-isls-2026-cached.json`)
was therefore produced **manually** (presumably via the OpenClaw workspace
project `wechat_public_article_fetcher`, which is still present in
`~/.openclaw/workspace/project/`), not from the disabled gateway channel.

## 3. What works today (without flipping the extension)

| Workflow | How | Status |
|---|---|---|
| Manually cache a capture JSON | Drop JSON into `inbox/raw/wechat/<slug>.json` matching the schema | ✓ working |
| Validate schema + dry-run import | `python3 scripts/import_wechat_article_capture.py --dry-run inbox/raw/wechat/<file>.json` | ✓ working |
| Run the new bridge (read-only) | `python3 scripts/wechat_inbound_to_capture.py --dry-run` | ✓ working |
| Run the new diagnostic | `python3 scripts/diagnose_wechat_inbound.py` | ✓ working |

## 4. What does NOT work today (until extension is re-enabled)

- Real-time WeChat forwarded articles → OpenClaw gateway
- Auto-generation of capture JSON from inbound events
- Any "you forward it once and it lands in KB" promise

## 5. The minimal bridge script

`scripts/wechat_inbound_to_capture.py` is a **read-mostly bridge**:

- **Default (`--dry-run`)**: prints the next-step command(s) without invoking
  the real import. **No writes, no commits, no Telegram send.**
- **`--import`**: invokes `scripts/import_wechat_article_capture.py` against
  the most recent (or `--path`-specified) capture JSON.
- **`--import --no-import-dry-run`**: double-safety — the import script's own
  `--dry-run` is also passed, so even if `--import` is set the import is still
  a dry run.

The bridge never:

- Reads WeChat session cookies
- Calls any WeChat API endpoint
- Modifies the extension-disabled directory
- Sends to Telegram or any other outbound channel

The bridge consumes only:

- Files already in `inbox/raw/wechat/`
- The local import script

## 6. Re-enabling real inbound (operator action, NOT a v0.3.62 task)

This section describes the action, but **v0.3.62 does NOT perform it** —
re-enabling the extension is an operator decision (the extension was disabled
on 2026-04-09, presumably for a reason, and re-enabling is not a "lite fix").

If the operator decides to proceed:

1. **Inspect why the extension was disabled** on 2026-04-09. Check
   `~/.openclaw/logs/` for entries from that day; check any related patches
   in `~/.openclaw/patches/`. *(v0.3.64 pilot: no direct evidence of the
   reason was found in local logs / memory / patches; the directory name's
   `2026-04-09-211122` suffix is the only timestamp evidence. The directory
   contents themselves have mtime 2026-03-22 — the original install time.
   The 2026-04-09 timestamp reflects the disable/rename action, not
   anything in the directory itself.)*

2. **Re-enable the extension — two distinct paths**, choose based on
   what's actually intended:

   **Path A (minimal file move, what v0.3.62 docs originally described)**:
   ```bash
   mv ~/.openclaw/extensions-disabled/openclaw-weixin.disabled.2026-04-09-211122 \
      ~/.openclaw/extensions/openclaw-weixin
   systemctl --user restart openclaw-gateway
   ```
   ⚠ **v0.3.64 pilot discovered this is insufficient.** The `openclaw
   channels list` output still reports `openclaw-weixin: not installed,
   not configured, disabled` after a restart. The file-move puts the
   extension package on disk where the gateway can find it, but the
   gateway's plugin loader does not auto-activate it. The result is:
   diagnostic sub-check #2 (extension enabled) reports PASS, but the
   channel manager still treats it as not installed. Real inbound still
   does not work via this path.

   **Path B (catalog-correct installation, what the gateway actually
   expects)**:
   ```bash
   openclaw channels add openclaw-weixin
   # OR (if add requires auth)
   openclaw channels install openclaw-weixin
   ```
   This invokes the official catalog entry
   (`@tencent-weixin/openclaw-weixin@2.4.3` with
   `sha512-dPQbidUNWigC6V10vGW4i+GLH09x+6zUhafZRjuxkJ9GDu8o62WBsnUTojp4KqUH756hz+t2v9khiCRSi0dBDw==`).
   The installed extension version is **2.4.3** (the on-disk package is
   1.0.2 — a 2-version gap). v0.3.64 did **NOT** run this command because
   it would change the installed package version (operator decision).

3. **Authenticate the WeChat channel** (the channel is described in the
   catalog as "Personal WeChat messaging via QR-code login"):

   ```bash
   openclaw channels login openclaw-weixin
   # OR (depending on CLI subcommand surface)
   openclaw weixin auth
   ```
   **This requires the operator to scan a QR code with their personal
   WeChat app.** The QR code is the standard way personal WeChat
   accounts register with a third-party long-poll client. v0.3.64
   **deliberately did NOT** run this command because:
   - It requires a human-in-the-loop action
   - It creates a persistent session tied to a personal WeChat account
   - It is outside the "lite fix" scope of v0.3.62 / v0.3.64
   - The user profile rule states "登录微信/绕过限制/读取敏感 cookie 时停止"

4. **Verify via diagnostic**:
   ```bash
   python3 scripts/diagnose_wechat_inbound.py
   ```
   Confirm sub-check #2 (WeChat extension enabled) is now ✓.

5. **Send a test article** to the bot and verify a new capture JSON appears in
   `inbox/raw/wechat/`.

6. **Optionally consume the new capture** with the bridge:
   ```bash
   python3 scripts/wechat_inbound_to_capture.py --dry-run    # preview
   python3 scripts/wechat_inbound_to_capture.py --import      # actually import
   ```

## 6.5. v0.3.64 pilot findings (canonical addendum)

The v0.3.64 pilot performed a controlled re-enable → observe → rollback
sequence and discovered that **the file-move approach in §6 step 2 Path A
is not sufficient on its own**. The full pilot report is at
`reports/openclaw_weixin_reenable_pilot_v0.3.64_20260629.md`. Key findings:

- `openclaw channels list --all` reports `openclaw-weixin: not installed,
  not configured, disabled` even after a clean Path A re-enable + restart.
- The official catalog expects version **2.4.3**; the on-disk package
  is **1.0.2**. Path B (`openclaw channels add openclaw-weixin`) would
  install the correct version.
- The channel description in the catalog is "Personal WeChat messaging
  via QR-code login" — i.e. operator QR-code scanning is a prerequisite
  for any real inbound.
- v0.3.64 deliberately **rolled back** the Path A mv before reporting,
  to leave the system in its pre-pilot state. Final diagnostic after
  rollback: 2/4 sub-checks pass (same as v0.3.62 baseline).
- **Reason for disable on 2026-04-09 = not found in local evidence.**
  No journal entries, no memory files, no patch logs from that day
  mention weixin. The directory name's `2026-04-09-211122` suffix is
  the only timestamp.

## 7. Why the existing import script was not enough

`scripts/import_wechat_article_capture.py` (579 lines) does its job well:
consumes a capture JSON and emits the canonical 5-file KB directory. What it
does **not** do:

- Locate the "most recent" or "next-to-process" capture (operator has to know
  the path)
- Validate the JSON schema upfront with a clean error message
- Distinguish "live inbound" from "manually cached" in its output

The new bridge fills those three gaps, plus surfaces a clear next-step command
the operator can copy-paste.

## 8. Files added in v0.3.62

| File | Purpose |
|---|---|
| `scripts/diagnose_wechat_inbound.py` | Read-only diagnostic. Emits text or JSON. Exits 0. |
| `scripts/wechat_inbound_to_capture.py` | Read-mostly bridge. Default dry-run. No Telegram. No login. |
| `docs/workflows/wechat-real-inbound-troubleshooting.md` | This document. |
| `reports/openclaw_weixin_real_inbound_fix_v0.3.62_20260629.md` | v0.3.62 task report. |

## 9. Files NOT modified in v0.3.62

- `scripts/import_wechat_article_capture.py` (existing 579-line script, untouched)
- `inbox/raw/wechat/*.json` (capture files, untouched)
- `~/.openclaw/extensions-disabled/` (extension state, untouched)
- `~/.openclaw/extensions/` (extension state, untouched)
- Any KB `content/articles/**` file (no new imports)
- Any `reports/*.md` (no historical reports modified)
- Any Telegram bot configuration (no outbound messages sent)

## 10. Operator decision matrix

| Operator wants | Action |
|---|---|
| Just see whether the chain works | `python3 scripts/diagnose_wechat_inbound.py` |
| Consume a manually-cached capture without re-enabling anything | `python3 scripts/wechat_inbound_to_capture.py --dry-run` then `--import` |
| Re-enable real inbound | Follow §6 step-by-step |
| Permanently remove the chain | Same as re-enabling but with `rm -rf` on the extension; or stop importing from `inbox/raw/wechat/` |

## 11. P0 / P1 / P2 status after v0.3.62

- **P0**: none (no real failure introduced; the chain was already partially broken before this task)
- **P1 (fixed by v0.3.62)**: there is now a single-command diagnostic + a single-command bridge
- **P2 (remaining, requires operator decision)**: extension-disabled state, which is outside v0.3.62 scope

## 12. Reproducing the diagnostic at any time

```bash
cd ~/hermes-knowledge-base
python3 scripts/diagnose_wechat_inbound.py            # human-readable
python3 scripts/diagnose_wechat_inbound.py --json | jq  # machine-readable
```