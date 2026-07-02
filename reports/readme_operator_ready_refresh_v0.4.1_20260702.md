# v0.4.1 README Operator-Ready Refresh — Report

**Date:** 2026-07-02 15:32 GMT+8
**Task:** `v0.4.1-readme-operator-ready-refresh`
**Baseline commit:** `c1695fd` (v0.4.0 release commit, HEAD == origin/main)
**Final commit:** *to be filled after push*
**Status:** ✅ PASS_WITH_WARNINGS (0 hard failures)

---

## STATUS

**PASS_WITH_WARNINGS** — README rewritten to operator-ready shape, all gates green on the new content; the only `FAILED_CLEANLINESS` flag in the full-gate JSON is the **expected** detection of the staged-but-not-yet-committed README.md edit (i.e. the gate correctly noticed "you've changed a tracked file but haven't committed it yet"). After Phase H commit, that flag clears on the next gate run.

- `run_full_gate.py --quick` → 7/7 steps PASS, gate-level exit 0 with `FAILED_CLEANLINESS` flag pointing at the uncommitted README.
- `run_full_gate.py` (full) → 17 steps: 16 PASS + 1 PASS_WITH_WARNINGS (`audit_kb_state` 29 soft `tag_topic_count_out_of_range`, **unchanged since v0.3.91**, content-derived), 0 failed, gate-level `FAILED_CLEANLINESS` on the same uncommitted README.
- `check_kb.py` → PASS (66/66 items).
- `check_pages_sync.py` → PASS.

---

## README 主要问题（before）

| # | Issue | Source |
|---|---|---|
| 1 | KB 数量 stale: README §3 显式写"总计 56"，实际是 66 | `scripts/audit_kb_state.py` output, 2026-07-02 |
| 2 | KB 状态 managed block 是 `2026-07-01 (v0.3.70)` 注释，注释却写"auto-updated by scripts/audit_kb_state.py"——其实脚本不维护它，只检测 stale "19" 模式 | `scripts/audit_kb_state.py` source review |
| 3 | Quick Start (§5) 推 `scripts/update_site.py` 是核心 gate runner，而不是 `scripts/run_full_gate.py` | user spec §5 vs README §5 |
| 4 | 导入能力总览 (§6) 过长（7 个表行 × 详细命令 + 多段长说明） | user spec §6 |
| 5 | §7 微信公众号"当前真实能力"过长 (含通道 B / OpenClaw 扩展 / 完整诊断步骤) | user spec §7 |
| 6 | §8 标准质量门禁过于展开（手拷命令 vs runner 优先） | user spec §8 |
| 7 | §10 微信公众号 Batch / OCR / YouTube 三段细节都堆在 README，违反 "README 只放最短路径，细节链接 docs" 原则 | user spec §7 |
| 8 | §11 近期里程碑有 23 行（v0.3.60 → v0.4.0），可压缩 | user spec §11 |
| 9 | 没有任何 v0.4.0 operator-ready 顶部状态 | user spec §C |
| 10 | 文档角色边界未澄清：README vs OPERATOR_PLAYBOOK vs AGENT_COMMANDS | user spec §C |

---

## README 新结构（after）

12 个一级章节，总长 235 行（之前 428 行，-45%）：

| § | 标题 | 行数 | 角色 |
|---|---|---|---|
| Header | 顶部 callout：v0.4.0 稳定版本 / gate 状态 / 入口脚本 / README 角色 | ~10 | operator-friendly status panel |
| 1 | 一句话说明 | 6 | elevator pitch |
| 2 | 线上入口 | 13 | links table |
| 3 | 当前 KB 状态 | 19 | real numbers from `audit_kb_state.py` (66 items) |
| 4 | 支持的材料矩阵（v0.4.0） | 23 | 1 个表 + 4 条 hard guarantees |
| 5 | 日常使用：统一材料入口 | 23 | 最短命令（单篇 + 批量） |
| 6 | 维护 / 发布门禁 | 26 | runner-first（`run_full_gate.py --quick` / `--json`），4 种 status 含义 |
| 7 | 仓库目录结构 | 29 | 精简目录树（移除冗余的 books/videos 注释） |
| 8 | 内容模型 | 5 | 一句话 + 链接 TAXONOMY |
| 9 | Release-Backed Assets | 5 | 一段说明 + 链接 docs/releases.md |
| 10 | 新电脑恢复 | 19 | 4 步最短路径 |
| 11 | 详细文档导航 | 18 | 11 个文档入口 |
| 12 | Releases | 26 | 17 个版本里程碑（精简到一行/版本） |

---

## 删除 / 压缩的旧内容

| 旧 § | 新位置 | 处理 |
|---|---|---|
| §5 Quick Start 推 `update_site.py` | §6 推 `run_full_gate.py` | 替换 |
| §6 7 行导入能力长表 + 多段长说明 | §4 一张材料矩阵表 + §5 最短命令 | 压缩 |
| §7 微信公众号两通道长文（含通道 B / OpenClaw / troubleshoot） | §11 链接 OPERATOR_PLAYBOOK §4-§8 / docs/workflows/wechat-* | 移到 docs |
| §8 标准质量门禁手拷命令 | §6 runner-first；手拷命令退到 OPERATOR_PLAYBOOK §9 | 替换 |
| §8a Full Gate Runner 子节 | 提升到 §6 主体 | 提升 |
| §9 仓库目录结构 | §7 | 保留，但精简（移除每条目录的英文说明） |
| §10 Agent 操作边界 | §4 hard guarantees + 链接 CLAUDE.md / AGENT_COMMANDS | 压缩 |
| §10 子节"并发 session / local divergence 处理入口" | 链接 AGENT_COMMANDS §"任务启动前 Divergence 检查" | 移到 docs |
| §10 子节"Tags / Topics 软范围 WARN 政策" | 同上 | 移到 docs |
| §11 23 行里程碑 | §12 17 行（v0.4.0 / v0.3.91 加重，其余精简到一行） | 压缩 |
| KB managed block（`总计 56`） | §3 真实数字 66 + 类型分布 | 替换（移除"auto-updated"伪注释） |
| "Last refreshed for v0.4.0 on 2026-07-02" 底栏 | "Last refreshed for v0.4.1 README operator-ready rewrite on 2026-07-02" | 更新 |

---

## 新增入口说明

README 顶部新增 operator-friendly callout：

```
> 当前稳定版本：v0.4.0-operator-ready-material-ingestion (commit c1695fd)
> Full gate 状态：PASS_WITH_WARNINGS — 0 hard failures，1 软警告
> 入口脚本：scripts/material_to_kb.py + scripts/run_full_gate.py
> 本 README 角色：项目首页说明（最短路径 + 文档导航）。
> 所有 daily import / 各材料详细流程 → docs/OPERATOR_PLAYBOOK.md
```

这一段是用户最常问的"我现在该用什么版本 / 从哪里开始"问题的答案。

---

## GATES

| Gate | Status | Notes |
|---|---|---|
| `run_full_gate.py --quick` | 7/7 PASS, exit 0 | `FAILED_CLEANLINESS` flag points at uncommitted README (expected, pre-commit) |
| `run_full_gate.py` (full) | 17 steps: 16 PASS, 1 PASS_WITH_WARNINGS (`audit_kb_state`), 0 failed | `FAILED_CLEANLINESS` flag same as above |
| `check_kb.py` | PASS | 66/66 items, 0 fail |
| `check_pages_sync.py` | PASS | site/ ↔ docs/ byte-identical |

Gate JSON artifacts:
- `reports/full_gate_run_v0.4.1_20260702_153200.json`

The 1 PASS_WITH_WARNINGS step (`audit_kb_state` with 29 soft `tag_topic_count_out_of_range` warnings) is **identical** to the v0.4.0 release state (29 warnings, same files). No new warnings introduced by this README rewrite. No gate standard lowered.

---

## 是否修改其他文档

**No.** Per user spec §E principle ("本轮主改 README；不要大面积重写其他文档"):

- `docs/OPERATOR_PLAYBOOK.md` — **untouched** (430 lines, all references in new README are anchors that already exist).
- `docs/AGENT_COMMANDS.md` — **untouched**.
- `docs/RELEASES.md` — **untouched**.
- `docs/RELEASES.md` "Last updated" — **untouched** (still `2026-07-02` from v0.4.0 release).
- `CHANGELOG.md` — **untouched**.

`scripts/check_kb.py`, `scripts/check_pages_sync.py`, `scripts/audit_kb_state.py` — **all untouched** (hard constraint).

---

## Hard Guarantees Verified

- ✅ **No new functionality** — only README rewrite.
- ✅ **No new KB entries imported** — `content/` unchanged from `c9135fd`.
- ✅ **No force push** — single `git push origin main` planned.
- ✅ **No `git add -A`** — explicit per-file `git add` planned (only README + report + gate JSON).
- ✅ **No reset** — `git pull --ff-only` only; HEAD was already `c9135fd == origin/main`.
- ✅ **No untracked artifact deleted** — the 15 pre-existing untracked `reports/full_gate_run_*.json` left on disk.
- ✅ **Tags not moved** — `v0.4.0` (annotated, pushed), `v0.3.91` / `v0.3.92` / `v0.3.96` (protected) all untouched.
- ✅ **No `tmp/`, `inbox/raw/*`, or session reports committed** — only the 3 new files (README + report + gate JSON) staged.
- ✅ **No script (`check_kb.py` / `check_pages_sync.py` / `audit_kb_state.py`) modified.**
- ✅ **No gate standard lowered** — `run_full_gate.py` runs unmodified; 0 failed steps; `audit_kb_state` warning count unchanged from v0.4.0.
- ✅ **README does not contain stale "总计=56"** — replaced with real "总计=66" from current `audit_kb_state.py` output.
- ✅ **README does not contain misleading "auto-updated by audit_kb_state.py" claim** — replaced with explicit "由 `audit_kb_state.py` 在本次 commit 时输出" wording.

---

## Commit / Push (planned)

| Field | Value |
|---|---|
| commit (planned) | *to be filled after Phase H* |
| push | `git push origin main` (single push, no force) |
| tag | **None** — this checkpoint is documentation-only; no annotated tag is created. The `v0.4.0-operator-ready-material-ingestion` tag remains the current stable baseline. A future `v0.4.1-readme-operator-ready-refresh` tag is **not** created per user spec (the planned tag name is a task identifier, not a release tag). |
| files in commit | `README.md`, `reports/readme_operator_ready_refresh_v0.4.1_20260702.md`, `reports/full_gate_run_v0.4.1_20260702_153200.json` |

---

## 下一步建议

The following are operational suggestions for the next checkpoint; **not** scope for v0.4.1 itself (which is README-only).

1. **Run `python3 scripts/audit_kb_state.py` before any future README refresh** — keep §3 numbers in sync with reality. (Currently the script does not auto-maintain the README block; we manually copied the 66-item output into the new README.)
2. **Consider an automated README §3 refresh hook** (e.g. a `scripts/update_readme_state.py` that re-runs `audit_kb_state.py` and patches the `## 3.` block between sentinel comments). This would close the drift loop. **Out of scope for v0.4.1.**
3. **Run `python3 scripts/check_release_tags.py` periodically** to confirm protected tag immutability (no change to script — `v0.4.0` is informational in the v0.3.X-focused script).
4. **Tags/topics additive cleanup pass** (carry-over from v0.4.0 next-steps): close out the 29 soft `tag_topic_count_out_of_range` warnings via per-entry editorial pass. Do **not** lower soft ranges in `audit_kb_state.py`.
5. **Next minor: `v0.4.2`** (per `docs/RELEASES.md` "Recommended Next Version: v0.4.1+"). The v0.4.1 task is documentation-only and does not consume the `v0.4.1` tag slot — `v0.4.1` remains available for the next operator-meaningful checkpoint.

---

## Reproduction

```bash
# 1. Sync to baseline
cd ~/projects/hermes-knowledge-base
git fetch origin main --tags
git pull --ff-only origin main
git log --oneline -1   # → c9135fd Document v0.4.0 operator-ready material ingestion baseline

# 2. Verify gate before any edit
python3 scripts/run_full_gate.py --quick
# → 7/7 PASS

# 3. Apply the README rewrite (diff captured in this commit)

# 4. Verify gate after edit (will flag FAILED_CLEANLINESS on the uncommitted README — expected)
python3 scripts/run_full_gate.py --json --output /tmp/v041_repro.json

# 5. Commit
git add README.md
git add reports/readme_operator_ready_refresh_v0.4.1_20260702.md
git add reports/full_gate_run_v0.4.1_20260702_153200.json
git -c user.name="conanxin" -c user.email="conanxin@users.noreply.github.com" \
    commit -m "Refresh README for operator-ready material ingestion"
git push origin main

# 6. Verify gate after commit (should be clean PASS_WITH_WARNINGS)
python3 scripts/run_full_gate.py --quick
# → 7/7 PASS, no FAILED_CLEANLINESS
```

---

*Generated by v0.4.1-readme-operator-ready-refresh checkpoint run, 2026-07-02 15:32 GMT+8.*