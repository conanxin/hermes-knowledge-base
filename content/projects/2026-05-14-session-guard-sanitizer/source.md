# Session Guard Phase 1 Report

## STATUS: PASS

## HOST_SCOPE
- **hostname:** DESKTOP-3A8N7VN
- **user:** conanxin
- **date:** 2026-05-14T13:56:21+08:00
- **pwd:** /home/conanxin/.openclaw/workspace
- **os:** Linux 6.6.87.2-microsoft-standard-WSL2 (x64)
- **shell:** bash

## TARGET_FILE
`/home/conanxin/hermes-agent/agent/auxiliary_client.py`

## BACKUP_DIR
`/home/conanxin/.hermes/backups/session_guard_1_20260514_135621`

## FILES_BACKED_UP
- `auxiliary_client.py.bak` (original, 94,588 bytes)

## FILES_MODIFIED
- `/home/conanxin/hermes-agent/agent/auxiliary_client.py`
  - Added `import copy` at line 45
  - Added `_sanitize_orphan_tool_calls_before_request()` at line 64
  - Integrated sanitizer into `call_llm()` at line 2129
  - Integrated sanitizer into `async_call_llm()` at line 2333

## PATCH_SUMMARY
Added a pure-Python pre-request sanitizer that scans the message history for orphaned `assistant.tool_calls` entries (i.e. assistant messages with `tool_calls` whose IDs lack matching `role="tool"` responses). For each orphan, a synthetic `role="tool"` message is inserted immediately after the assistant message, neutralizing the orphan before the request reaches the OpenAI-compatible API. This prevents the recurring HTTP 400:
```
an assistant message with 'tool_calls' must be followed by tool messages responding to each 'tool_call_id'
```

## SANITIZER_FUNCTION
```python
def _sanitize_orphan_tool_calls_before_request(messages: list) -> tuple:
```
- **Location:** `/home/conanxin/hermes-agent/agent/auxiliary_client.py:64`
- **Input:** `messages` list (OpenAI chat.completions format)
- **Output:** `(repaired_messages, repair_report)`
- **Behavior:**
  - Deep-copies input (never mutates caller's list)
  - Collects all existing `tool_call_id`s from `role="tool"` messages
  - For each `assistant.tool_calls` entry, checks if every `id` has a matching tool response
  - Missing IDs trigger synthetic tool message insertion immediately after the assistant message
  - Missing `tool_call.id` fields are counted in `skipped_missing_id_count` (no crash)
- **Repair report keys:**
  - `repaired` (bool)
  - `inserted_count` (int)
  - `inserted_tool_call_ids` (list[str])
  - `skipped_missing_id_count` (int)

## REQUEST_INTEGRATION_POINT
- **Function:** `call_llm()` (sync)
- **Location:** Line 2129
- **Code:**
  ```python
  messages, _tool_repair = _sanitize_orphan_tool_calls_before_request(messages)
  if _tool_repair.get("inserted_count"):
      logger.info(
          "Tool-call sanitizer: inserted %d synthetic tool responses "
          "for orphan tool_calls (ids: %s)",
          _tool_repair["inserted_count"],
          _tool_repair["inserted_tool_call_ids"][:10],
      )
  ```
- **Placement:** Immediately after `_resolve_task_provider_model()` and before `_build_call_kwargs()` / `client.chat.completions.create()`
- **Effect:** Both primary and fallback API calls use the already-sanitized `messages` list

## FALLBACK_INTEGRATION_POINT
- **Function:** `async_call_llm()` (async)
- **Location:** Line 2333
- **Code:** Same pattern as sync version
- **Placement:** Immediately after `_resolve_task_provider_model()` and before `_build_call_kwargs()` / `await client.chat.completions.create()`
- **Effect:** Fallback retry uses sanitized messages automatically (since `messages` is sanitized once at function entry)

## PY_COMPILE_RESULT
- **Command:** `python3 -m py_compile agent/auxiliary_client.py`
- **Result:** PASS (exit code 0)

## SYNTHETIC_TEST_RESULT
- **Test script:** `/home/conanxin/.hermes/backups/session_guard_1_20260514_135621/test_orphan_tool_sanitizer.py`
- **Test A (normal pairing):** PASS — `inserted_count=0`
- **Test B (missing tool response):** PASS — inserted 1 synthetic tool message
- **Test C (multi tool_calls partial missing):** PASS — only补缺失的 (2 of 3)
- **Test D (tool_call without id):** PASS — no crash, `skipped_missing_id_count=1`
- **Test E (no mutation of original):** PASS — original list unchanged
- **Test F (empty messages):** PASS — safe return
- **Overall:** ALL TESTS PASSED

## SHA256_BEFORE
```
22c11ab5dd92796136db4b7ec3ce6cc609c2a2e4a8dcfff05cc51b2464c62464  /home/conanxin/hermes-agent/agent/auxiliary_client.py
```

## SHA256_AFTER
```
84621fb8a4f8082a112d3866f79a50291c797b57d690b640f661bce6296bee02  /home/conanxin/hermes-agent/agent/auxiliary_client.py
```

## PRODUCTION_CONFIG_CHANGED: YES_CODE_PATCH_ONLY

## HERMES_MAIN_VENV_MODIFIED: NO

## PACKAGES_INSTALLED: NONE

## GATEWAY_RESTARTED: NO

## CRON_CHANGED: NO

## SYSTEMD_CHANGED: NO

## OPENCLAW_DIST_MODIFIED: NO

## RISKS
- **Low risk.** The sanitizer is a defensive pre-flight check that only *adds* synthetic tool responses when orphans are detected. It never removes or modifies existing messages.
- The synthetic tool response content (`[RECOVERED_ORPHAN_TOOL_CALL] ...`) is clearly marked and will not be confused with real tool output.
- Deep-copy prevents mutation of caller state.
- The sanitizer is idempotent: running it twice on the same messages produces the same result (orphans are fixed on first run, second run finds no new orphans).
- Logger output is capped at 10 IDs to prevent log flooding.

## ROLLBACK
```bash
# Restore from backup
cp /home/conanxin/.hermes/backups/session_guard_1_20260514_135621/auxiliary_client.py.bak \
   /home/conanxin/hermes-agent/agent/auxiliary_client.py
```

## NEXT_BEST_STEP
1. **Phase 2 (Runtime Validation):** Monitor gateway logs for the sanitizer's `logger.info` lines over the next 24–48 hours. If orphans are detected frequently, the underlying truncation/compression bug needs separate fixes (context_compressor.py, truncateOversizedToolResults).
2. **Phase 3 (Context Compressor Hardening):** Patch `context_compressor.py` lines 429–487 to also validate tool-call pairing during compaction, preventing orphans at the source.
3. **Phase 4 (Request Dump Cleanup):** Extend `performGatewaySessionReset` to delete stale `request_dump_*.json` files.
4. **Phase 5 (OpenClaw Dist):** If Phase 1–3 do not fully eliminate the issue, patch the OpenClaw JS dist fallback path to also sanitize messages before retry.
