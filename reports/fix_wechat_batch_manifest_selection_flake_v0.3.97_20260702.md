# v0.3.97: Fix Deterministic WeChat Batch Manifest Selection

**STATUS:** PASS

**DATE:** 2026-07-02
**TASK:** `v0.3.97-fix-wechat-batch-manifest-selection-flake`
**TAGS:** unchanged (no tag movement)

---

## ROOT_CAUSE

`tests/run_wechat_batch_smoke.py` used an mtime-based `_find_latest_manifest()` helper:

```python
files = sorted(reports.glob(f"{prefix}*.json"),
               key=lambda p: p.stat().st_mtime, reverse=True)
return files[0] if files else None
```

This sorted manifests by **filesystem mtime**, then picked the newest. The flaw:

1. Each smoke invocation runs the batch script 4 times (Smokes 1, 2, 3, 4).
2. The batch script writes `reports/wechat_batch_import_<timestamp>.{md,json}` with a `YYYYMMDD_HHMMSS` stamp.
3. When two batch runs finish within the same wall-clock second (very common on fast machines), their timestamps collide.
4. With colliding timestamps, mtime becomes the tiebreaker — but FS mtime resolution varies (1s on ext4 default, 1ns on some filesystems). Even with 1ns resolution, **a different smoke's manifest can still be picked** if its file was written later in the same second.

Concretely, the failure mode:
- Smoke 1 writes manifest A (`wechat_batch_import_20260702_115503.json`).
- Smoke 2 starts immediately and writes manifest B (`wechat_batch_import_20260702_115503.json` — same second).
- After Smoke 2 returns, `_find_latest_manifest()` may return A's manifest (from Smoke 1), because mtime order doesn't necessarily match process-call order.
- Smoke 2 reads A's items and asserts "second item is DRY_RUN_DUPLICATE" — but A has only 1 item (the first input). Assertion fails.

**v0.3.96 first noticed this** when running the full gate via `scripts/run_full_gate.py`. The gate runner made the race visible because the full mode runs `run_wechat_batch_smoke` after `run_smoke_tests` in the same second, then after multiple other steps — increasing the chance that leftover manifests from the prior run are still on disk.

**v0.3.96 did not fix it** (it just observed the flake). v0.3.97 fixes it.

---

## FIX

### scripts/wechat_batch_import.py

1. Added `--run-id <id>` argument.
   - When provided, manifest paths are computed as:
     - `reports/wechat_batch_import_<run_id>.md`
     - `reports/wechat_batch_import_<run_id>.json`
   - When omitted, behavior is **unchanged** — legacy timestamp stamp is used.

2. `_write_manifest()` now accepts `run_id` and uses it as the file basename when present.

3. The manifest JSON includes a `run_id` field (empty string when legacy mode).

4. After writing the manifest, the script emits a single-line JSON summary on **stdout** (not stderr) with the exact paths:
   ```json
   {"ok": true, "mode": "dry-run", "total": 2,
    "summary": {"DRY_RUN_OK": 2},
    "markdown_report_path": "/abs/path/...md",
    "json_report_path": "/abs/path/...json",
    "run_id": "smoke_<pid>_<ts_ns>_<uuid8>"}
   ```

### tests/run_wechat_batch_smoke.py

1. Removed `_find_latest_manifest()` entirely — no mtime lookup.
2. Added `make_run_id()` → `smoke_<pid>_<timestamp_ns>_<uuid8>`.
3. Added `run_batch_with_run_id(args)` helper:
   - Generates unique `--run-id`.
   - Invokes the batch script.
   - Parses the **stdout JSON line** to extract `json_report_path` exactly.
   - Falls back to constructing the expected path from the run_id if parsing fails (defense in depth).
4. Each of Smokes 1-4 uses `run_batch_with_run_id(...)` instead of the old mtime-based lookup.

---

## REGRESSION

**5 consecutive `python3 tests/run_wechat_batch_smoke.py` runs:**

| Run | Result |
|-----|--------|
| 1   | 5/5 PASS |
| 2   | 5/5 PASS |
| 3   | 5/5 PASS |
| 4   | 5/5 PASS |
| 5   | 5/5 PASS |

**0 flakes.**

21 smoke-`<pid>-<ts>-<uuid>` manifests in `reports/` after 5 runs (all untracked, correctly excluded from git).

Stale tracked `reports/wechat_batch_import_*.{json,md}` from v0.3.71 are untouched (`git status` clean for those files). No tracked artifacts created.

---

## GATES

- `python3 -m py_compile scripts/*.py` → PASS
- `python3 tests/run_wechat_batch_smoke.py` → 5/5 PASS (5 consecutive runs, 0 flakes)
- `python3 scripts/run_full_gate.py --quick` → 7/7 PASS
- `python3 scripts/run_full_gate.py` → 16/17 PASS + 1 PASS_WITH_WARNINGS (audit_kb_state 29 soft warnings, unchanged); 0 failed; tracked working tree detects own uncommitted changes as `FAILED_CLEANLINESS` (correct behavior pre-commit)

Post-commit, the tracked working tree will be clean and the gate will exit 0.

---

## FILES_CHANGED

- `scripts/wechat_batch_import.py` (modified)
  - Added `--run-id` CLI argument
  - `_write_manifest()` accepts run_id parameter
  - Added stdout JSON summary with `json_report_path` / `markdown_report_path`
- `tests/run_wechat_batch_smoke.py` (rewritten)
  - Removed `_find_latest_manifest()` (mtime dependency eliminated)
  - Added `make_run_id()` and `run_batch_with_run_id()`
  - Smokes 1-4 use deterministic manifest path

---

## COMPATIBILITY

- Users not passing `--run-id`: behavior **unchanged**. Existing scripts / cron / manual invocations continue to work — manifest filename still uses timestamp.
- Manifest JSON schema extended with `run_id` field (empty string in legacy mode). Backward compatible.
- No `.gitignore` changes.
- No existing tracked artifacts modified.

---

## REPORT

This document: `reports/fix_wechat_batch_manifest_selection_flake_v0.3.97_20260702.md`

---

## NEXT RECOMMENDATIONS

1. All callers that need to read a batch manifest back should use `--run-id` and parse the stdout JSON for exact path.
2. The legacy mtime-based manifest lookup pattern (if found anywhere else in the codebase) should be migrated to the same `--run-id` pattern.
3. The pre-existing flake class is now eliminated; future batch smoke runs should be 5/5 deterministic.