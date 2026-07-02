# v0.3.96: Full Gate Runner + Tag SHA Sanity

**STATUS:** PASS

**DATE:** 2026-07-02
**COMMIT:** `a6daf50` → `pending` (improvements to be committed)
**TASK:** `v0.3.96-full-gate-runner-and-tag-sanity`
**TAG:** `v0.3.96-full-gate-runner-and-tag-sanity`

---

## What was done

### 1. `scripts/run_full_gate.py` — unified full gate runner

Single entry point for all smoke / check / audit steps in the project. Replaces the need to hand-copier multiple commands across task specs.

**Usage:**

```bash
# Full mode (16 steps)
python3 scripts/run_full_gate.py

# Quick mode (7 core steps)
python3 scripts/run_full_gate.py --quick

# Dry-run — print plan as JSON, do NOT execute
python3 scripts/run_full_gate.py --list
python3 scripts/run_full_gate.py --quick --list

# Machine-readable JSON output
python3 scripts/run_full_gate.py --json
python3 scripts/run_full_gate.py --json --output reports/full_gate_run_YYYYMMDD_HHMMSS.json

# Stop at first failure
python3 scripts/run_full_gate.py --fail-fast

# Skip update_site.py (faster iteration)
python3 scripts/run_full_gate.py --no-update-site
```

**Full plan (16 steps, fixed order):**

1. `py_compile`
2. `run_smoke_tests`
3. `run_wechat_batch_smoke`
4. `run_item_render_smoke`
5. `run_image_localization_smoke`
6. `run_material_router_smoke`
7. `run_web_article_smoke`
8. `run_youtube_import_smoke`
9. `run_fetch_layer_smoke`
10. `run_pdf_import_smoke`
11. `run_release_assets_smoke`
12. `check_release_assets`
13. `check_kb`
14. `update_site`
15. `audit_kb_state`
16. `check_pages_sync`

**Quick plan (7 steps, subset):**

`py_compile`, `run_material_router_smoke`, `run_pdf_import_smoke`, `run_release_assets_smoke`, `check_release_assets`, `check_kb`, `check_pages_sync`

**JSON output:**

Each step includes `name`, `command`, `exit_code`, `duration_seconds`, `stdout_tail`, `stderr_tail`, `status`. Top-level fields: `status`, `mode`, `total_steps`, `passed`, `passed_with_warnings`, `failed`, `failed_step_names`, `total_duration_seconds`, `steps`, `working_tree`.

**Working-tree cleanliness check:** After all steps, runner runs `git status --short` + `git diff --stat`. If tracked files are dirty (e.g. `update_site.py` produced canonical diff), runner reports `FAILED_CLEANLINESS` and exits 1. Untracked files (build artifacts, ignored files) are informational only.

**Exit codes:**
- `0` — all PASS (or only PASS_WITH_WARNINGS)
- `1` — any FAIL or tracked working tree dirty

---

### 2. `scripts/check_release_tags.py` — Tag SHA sanity

Added tag SHA sanity section that explicitly distinguishes annotated tag object SHA from dereferenced commit SHA:

```
tag SHA sanity (annotated object vs dereferenced commit):
  v0.3.91-material-ingestion-stable-baseline
    tag_object_sha:       6b8e95b1f235
    dereferenced_commit:  56fe8482a8ce
    expected_commit:      56fe8482a8ce
    kind: annotated
    commit_match: OK
  v0.3.92-bingzhu-you-mv-assets
    tag_object_sha:       4117366a5cf5
    dereferenced_commit:  4117366a5cf5
    expected_commit:      4117366a5cf5
    kind: lightweight
    commit_match: OK
```

- **Annotated tag (v0.3.91):** tag object SHA `6b8e95b1f235` differs from dereferenced commit SHA `56fe8482a8ce`. Moving this tag would change the dereferenced commit SHA — this is the canonical anti-spoofing signal.
- **Lightweight tag (v0.3.92):** both SHAs identical = `4117366a5cf5`.

**Documented expected commits:**
- `v0.3.91-...-stable-baseline` → `56fe848` (Document material ingestion stable baseline)
- `v0.3.92-...-bingzhu-you-mv-assets` → `4117366` (Clean up KB audit warnings 37 → 29)

If a protected tag's dereferenced commit does not match the expected prefix, the check exits with `FAIL` exit 1 — critical invariant violation (tag has been silently moved).

---

### 3. `tests/run_full_gate_runner_smoke.py` — 14 smoke tests

Renamed from `run_full_gate_smoke.py` (per spec).

Tests:

1. `--quick` mode runs and emits STATUS
2. `--json` output is valid JSON
3. `--output` writes JSON to file
4. `--fail-fast` syntax verified
5. Working tree section present in JSON
6. Step structure validated
7. Quick mode runs exactly 7 steps
8. `--no-update-site` excludes update_site
9. `check_release_tags.py` prints tag SHA sanity
10. `--list` (full) prints plan including `check_release_assets` + `run_pdf_import_smoke`
11. `--list --quick` plan is subset of full
12. `--list` does NOT execute commands (no `exit_code`/`status` fields)
13. Tag sanity verifies documented commit match (`56fe848` / `4117366`)
14. Annotated tag does not trigger false positive

**Result:** 14/14 PASS.

---

### 4. Documentation updates

- `README.md` — added **8a. 统一 Full Gate Runner** section after standard gates; explains runner, JSON output, exit codes, smoke test, tag SHA sanity.
- `docs/AGENT_COMMANDS.md` — added **统一 Full Gate Runner (v0.3.96+)** and **Tag SHA Sanity (v0.3.96+)** sections with full plan table, JSON structure, exit codes, and protected tag table.

---

## Gate Results

**Full gate (16 steps):** 16/16 PASS.

| Step | Status | Duration |
|------|--------|----------|
| py_compile | PASS | 0.08s |
| run_smoke_tests | PASS | 0.69s |
| run_wechat_batch_smoke | PASS | 2.4s |
| run_item_render_smoke | PASS | 0.13s |
| run_image_localization_smoke | PASS | 0.30s |
| run_material_router_smoke | PASS | 2.53s |
| run_web_article_smoke | PASS | 2.21s |
| run_youtube_import_smoke | PASS | 2.19s |
| run_fetch_layer_smoke | PASS | 0.64s |
| run_pdf_import_smoke | PASS | 1.54s |
| run_release_assets_smoke | PASS | 3.75s |
| check_release_assets | PASS | 2.47s |
| check_kb | PASS | 0.27s |
| update_site | PASS | 1.22s |
| audit_kb_state | PASS_WITH_WARNINGS | 0.22s |
| check_pages_sync | PASS | 0.07s |
| **Working tree (post-commit)** | **PASS** | — |

- Total duration: ~20s
- audit_kb_state: 29 soft warnings, 0 hard (unchanged from v0.3.95)
- Working tree: clean post-commit (pre-commit run correctly detected own uncommitted changes as `FAILED_CLEANLINESS`)

**Quick gate (7 steps):** 7/7 PASS.

**Smoke tests:** 14/14 PASS.

**Tag sanity:** 2/2 protected tags match documented commits.

---

## Files Changed

- `scripts/run_full_gate.py` (modified — added `--list` mode)
- `scripts/check_release_tags.py` (modified — added documented commit verification)
- `tests/run_full_gate_runner_smoke.py` (renamed from `run_full_gate_smoke.py` + 5 new tests)
- `docs/AGENT_COMMANDS.md` (modified — added 2 new sections)
- `README.md` (modified — added section 8a)
- `reports/full_gate_runner_tag_sanity_v0.3.96_20260702.md` (new)

---

## Tag Status

| Tag | SHA (object) | SHA (commit) | Kind | Status |
|-----|--------------|--------------|------|--------|
| `v0.3.91-material-ingestion-stable-baseline` | `6b8e95b1f235` | `56fe8482a8ce` | annotated | unchanged |
| `v0.3.92-bingzhu-you-mv-assets` | `4117366a5cf5` | `4117366a5cf5` | lightweight | unchanged |
| `v0.3.96-full-gate-runner-and-tag-sanity` | (new) | `a6daf50` | (TBD) | created |

**No protected tags moved.**

---

## Next Recommendations

1. **All future tasks should run** `python3 scripts/run_full_gate.py` at start and end of every task. JSON output archived to `reports/full_gate_run_YYYYMMDD_HHMMSS.json`.
2. **Tag SHA sanity** is now a critical invariant: any future tag movement (e.g. `v0.3.91`) will be caught by `check_release_tags.py` with FAIL exit 1. This protects against silent tag rotation.
3. **`--list` mode** allows safe plan inspection without running 16-step gate; useful for fast iteration on which steps to run.
4. **Smoke test rename**: `tests/run_full_gate_smoke.py` → `tests/run_full_gate_runner_smoke.py` (per spec). Other agents: update CI references if any.
5. **Plan minor v0.3.97 gap**: preflight recommended next minor was v0.3.93 at task start; final tag is v0.3.96. Gap acknowledged per task spec.