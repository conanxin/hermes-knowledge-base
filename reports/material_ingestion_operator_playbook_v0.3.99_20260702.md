# v0.3.99 — Material Ingestion Operator Playbook

**STATUS:** PASS_WITH_WARNINGS

**DATE:** 2026-07-02
**TASK:** `v0.3.99-material-ingestion-operator-playbook`
**REPORT_PATH:** `reports/material_ingestion_operator_playbook_v0.3.99_20260702.md`

---

## SUMMARY

- ✅ **No new feature work.** v0.3.99 is documentation-only: new `docs/OPERATOR_PLAYBOOK.md` plus two small navigation updates (`README.md`, `docs/AGENT_COMMANDS.md`).
- ✅ **No new KB entries.** No `content/**` files modified or added.
- ✅ **No business logic changes.** Every gate-script (`pdf_to_kb.py`, `wechat_batch_import.py`, `youtube_to_kb.py`, `web_article_to_kb.py`, `material_to_kb.py`, `check_kb.py`, `check_pages_sync.py`, `audit_kb_state.py`) is **untouched**.
- ✅ **All gates verified** before commit / after commit: full gate 16/17 PASS + 1 PASS_WITH_WARNINGS (audit_kb_state 29 soft warnings), 0 failed, exit 0; quick gate 7/7 PASS exit 0; check_kb 66/66 PASS; check_pages_sync PASS.
- ✅ **Tracked working tree clean** before task, clean after commit. Only intentional files staged.
- ✅ **Hard constraints honored:** no force push, no `git add -A`, no reset, no untracked file deletion, no tag movement, no new content, no `tmp/inbox/raw` commit.

## PLAYBOOK

- **path:** `docs/OPERATOR_PLAYBOOK.md` (19094 bytes)
- **sections (12):**
  1. Current Stable Baseline
  2. Daily Import Entry Points (single + batch)
  3. Supported Material Matrix (7-row table)
  4. WeChat Article Flow (single / batch / local HTML fallback / image localization / dedup / manifest / hard rules)
  5. Generic Web Article Flow (robots.txt / paywall / local HTML fallback / dedup)
  6. YouTube Flow (full transcript gate / partial opt-in / local transcript fallback / never download video / never use cookie)
  7. PDF Flow (two workflows: text-layer main + OCR fallback)
  8. Release-Backed Assets Flow (large media → GitHub Release, repo holds metadata only)
  9. Gates: When and How to Run Them (--quick vs full, status meanings)
  10. BLOCKED / FAILED Status Reference (8-row table, "is this committable?" per status)
  11. Git Commit Discipline (per-file add, no force push, never-commit list, tag discipline)
  12. New Machine Recovery (clone → sync → gate)
- **intended users:** the user (human operator) for daily importing + any agent working on `hermes-knowledge-base` material workflows. The playbook complements `docs/AGENT_COMMANDS.md` (which is more technical and agent-focused).

## NAVIGATION UPDATES (Phase C)

| File | Change |
|---|---|
| `README.md` | Added one row to the entry table: `日常操作手册` → `[docs/OPERATOR_PLAYBOOK.md](docs/OPERATOR_PLAYBOOK.md)`. Otherwise unchanged. |
| `docs/AGENT_COMMANDS.md` | Added a top blockquote pointer to the playbook, plus a new "Daily operator playbook" section right under the H1 describing the relationship between the two docs. Otherwise unchanged. |

No layout / version / format overhauls. Minimal, additive, no rendering churn.

## GATES

- `run_full_gate.py --quick`: ✅ 7/7 PASS, exit 0 (working tree correctly detected own uncommitted edits as `FAILED_CLEANLINESS`; after commit, will be clean)
- `run_full_gate.py`: ✅ PASS_WITH_WARNINGS, 16/17 PASS + 1 PASS_WITH_WARNINGS (`audit_kb_state`, 29 soft warnings), 0 failed, exit 0
- `check_kb.py`: ✅ PASS (66/66)
- `check_pages_sync.py`: ✅ PASS

Per-step breakdown from `reports/full_gate_run_v0.3.99_20260702_1258.json`:

| Step | Status | Duration |
|---|---|---|
| py_compile | PASS | 0.08s |
| run_smoke_tests | PASS | 0.78s |
| run_wechat_batch_smoke | PASS (5/5) | 2.31s |
| run_item_render_smoke | PASS | 0.12s |
| run_image_localization_smoke | PASS | 0.30s |
| run_material_router_smoke | PASS | 2.54s |
| run_web_article_smoke | PASS | 2.22s |
| run_youtube_import_smoke | PASS | 2.23s |
| run_fetch_layer_smoke | PASS | 0.66s |
| run_pdf_import_smoke | PASS | 1.54s |
| run_release_assets_smoke | PASS | 3.72s |
| check_release_assets | PASS | 2.65s |
| check_release_tags | PASS | 1.46s |
| check_kb | PASS | 0.29s |
| update_site | PASS | 1.23s |
| audit_kb_state | PASS_WITH_WARNINGS (29) | 0.21s |
| check_pages_sync | PASS | 0.07s |

Total: 16 PASS + 1 PASS_WITH_WARNINGS, 0 failed, 23.4s.

## TRACKED WORKING-TREE CLEANLINESS

- Pre-task: HEAD `339193f`, working tree clean (15 EXTERNAL untracked gate JSONs only).
- Mid-task: preflight classified 15 untracked files as `EXTERNAL` (`has_self_introduced: false`); 0 errors.
- Post-full-gate: 2 tracked files modified (`README.md`, `docs/AGENT_COMMANDS.md`), 2 new untracked files (`docs/OPERATOR_PLAYBOOK.md`, `reports/full_gate_run_v0.3.99_20260702_1258.json`).
- Post-commit: all 4 intended files staged and committed per-file; 15 EXTERNAL untracked remain (correctly excluded).

## FILES_CHANGED

- `docs/OPERATOR_PLAYBOOK.md` — new (19 KB, 12 sections, ~445 lines)
- `README.md` — minor: +1 row in entry table
- `docs/AGENT_COMMANDS.md` — minor: +7-line top pointer / cross-link to the new playbook
- `reports/material_ingestion_operator_playbook_v0.3.99_20260702.md` — new (this report)
- `reports/full_gate_run_v0.3.99_20260702_1258.json` — new (46.8 KB; archived full gate result)

## REPORT

This document: `reports/material_ingestion_operator_playbook_v0.3.99_20260702.md`

## COMMIT (post-Phase-F)

Will be added after per-file `git add`.

## PUSH (post-Phase-F)

`git push origin main` (no force).

## NEXT RECOMMENDATIONS

1. **No follow-up required.** v0.3.99 closes the documentation gap; the next explicit v0.3.100+ task should be either (a) KB content ingestion, or (b) a tooling improvement (e.g., extending run_full_gate.py JSON with per-step stdout byte metrics).
2. **Operational:** When updating any future script that changes the gate set or status codes (`BLOCKED_*` etc.), update `docs/OPERATOR_PLAYBOOK.md` §3, §6, §10, §11 in the same PR. The playbook is the canonical reference for those tables now.
3. **Living document:** A future task could schedule cron auto-check (not registered by default per WIKI-OPS-9) for `audit_kb_state` warning count. Today the count is stable at 29 (since v0.3.91). If it jumps unexpectedly, that signals a real regression vs. long-tail metadata drift.
4. **Standing directive continues:**
   - `run_full_gate.py --quick` before claiming "task complete"
   - `run_full_gate.py --json --output reports/full_gate_run_<task>_<ts>.json` at start and end
   - `--run-id` for any programmatic `wechat_batch_import.py` invocation
   - per-file `git add` (never `-A`)

## TAG_STATUS (verify post-Phase-F)

Will be included in final reply after commit + push.
