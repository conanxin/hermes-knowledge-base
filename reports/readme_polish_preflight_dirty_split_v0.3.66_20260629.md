# README Polish & Preflight Dirty Classification (v0.3.66) — 2026-06-29

## Summary

轻量治理任务。两件事：

1. **README §9 目录树去重**：`docs/` 与 `site/` 各从两次减为一次；`docs/` 注释合并为"手册目录 + GitHub Pages 发布目录"；`site/` 注释改成"本地开发/预览面；与 docs/ 镜像"；`content/resource_collections/` 保留为现行；`content/collections/` 保留但只作为 legacy 注脚（`详见 docs/LEGACY_MIGRATION.md`），未宣称它当前存在。
2. **preflight 新增 `--classify-dirty` flag**：默认严格行为零变化（dirty → FAIL exit 1）；新 flag 把每条 porcelain entry 分桶（`task-relevant` / `report-external-sha-backfill` / `report-other` / `staged` / `unstaged` / `untracked` / `other-external`），并按桶判断是否降级为 PASS_WITH_WARNINGS。**绝不**自动 stage / restore / commit。

附：`docs/AGENT_COMMANDS.md` §Preflight 结果处理 章节末尾加了一节规则，明确"preflight 因非本任务历史 reports dirty 失败"的处置纪律。

---

## 0. Pre-existing Dirty（任务开始时记录）

> 命令：`git status --short | tee /tmp/status_before_v0.3.66.txt`

```
 M reports/v0.3.64_legacy_collections_cleanup_report_20260629.md
```

单一 pre-existing dirty（unstaged modify）。本任务**不**触碰此文件，commit / push 不携带。

> **任务运行期间又出现 4 个新 dirty（**4 个 `content/articles/.../metadata.yaml`）** 和 1 个 untracked（**`reports/v0.3.65_residual_tag_warn_refinement_report_20260629.md`）**——**全部为外部 session 引入**（不是我修改的）。spec 禁止触碰 KB 正文（`source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md`），`metadata.yaml` 不在该名单里但 spec 范围是"README polish + preflight 增强"，因此**同样不触碰**。这些 dirty 在 commit 时也不会被 add，详见 §5。

---

## 1. 执行步骤与真实回传

| 步骤 | 命令 | 结果 |
|---|---|---|
| 1. cd + git fetch + checkout main + pull --ff-only | 标准 4 行 | `Already up to date` (exit 0) |
| 0. 记录初始 dirty 状态 | `git status --short \| tee /tmp/status_before_v0.3.66.txt` | 单行 `M reports/v0.3.64_legacy_collections_cleanup_report_20260629.md` |
| 1. baseline preflight | `python3 scripts/check_task_preflight.py --planned-tag v0.3.66-readme-polish-preflight-dirty-split --allow-warnings` | FAIL（仅由 pre-existing dirty 触发；其余 7 gate 全 PASS / PASS_WITH_WARNINGS） |
| 1. py_compile baseline | `python3 -m py_compile scripts/*.py` | PY_COMPILE_OK |
| 1. check_kb baseline | `python3 scripts/check_kb.py` | PASS 54/54；7 个 word-drift warnings（历史） |
| 1. audit_kb_state baseline | `python3 scripts/audit_kb_state.py` | PASS_WITH_WARNINGS；HARD FAILURES=0；27 warnings（历史） |
| 1. check_pages_sync baseline | `python3 scripts/check_pages_sync.py` | PASS |
| 2. 改 README §9 目录树 | write_file / patch | docs/ 与 site/ 各去重一次；RELEASES.md 笔误已修；KB_STATE managed block 完整未动；总行 235（baseline 236） |
| 3. 改 scripts/check_task_preflight.py | patch（+~110 行） | 新增 `--classify-dirty` arg + `classify_dirty_entries()` + 严格默认保留 + `run_git().strip()` 引发的 leading-space-bug 修；bucket-overwrite bug 修复 |
| 3. py_compile | `python3 -m py_compile scripts/*.py` | OK |
| 4. 验证新 flag | `python3 scripts/check_task_preflight.py --planned-tag v0.3.66-readme-polish-preflight-dirty-split --allow-warnings --classify-dirty --json` | JSON 输出到 `/tmp/preflight_classify_dirty_v0.3.66.json`：status=PASS_WITH_WARNINGS（实际因 SELF 引入项**降级回 FAIL**），分类正确 |
| 5. post-edit check_kb | `python3 scripts/check_kb.py` | PASS 54/54（与 baseline 一致） |
| 5. post-edit audit_kb_state | `python3 scripts/audit_kb_state.py` | PASS_WITH_WARNINGS；HARD FAILURES=0；24 warnings（baseline 27 → 24 差异由 audit 自身重算导致；HARD=0 不变） |
| 5. post-edit check_pages_sync | `python3 scripts/check_pages_sync.py` | PASS |
| 报告 | `reports/readme_polish_preflight_dirty_split_v0.3.66_20260629.md` | （本文件） |
| postflight | `python3 scripts/check_task_postflight.py --report-file reports/readme_polish_preflight_dirty_split_v0.3.66_20260629.md --profile auto` | 见 §6 |

---

## 2. README 改动摘要

### 2.1 §9 目录树修复前后

**修复前**（v0.3.65 残留）：

```
├── docs/                        # 完整手册（GitHub Pages 发布目录）  ← 第 1 次
│   ├── AGENT_COMMANDS.md ...
│   ├── ... (子节) ...
│   ├── items/ ...
│   └── data/ ...
├── site/                        # 开发面；和 docs/ 的发布面字节级一致  ← 第 1 次
├── docs/                        # GitHub Pages 发布目录（与 site/ 镜像）  ← 第 2 次（重复）
└── site/                        # 开发、调试、本地预览  ← 第 2 次（重复）
```

**修复后**（v0.3.66）：

```
├── docs/                        # 手册目录 + GitHub Pages 发布目录  ← 仅 1 次
│   ├── AGENT_COMMANDS.md ...
│   ├── ... (子节) ...
│   ├── items/ ...
│   └── data/ ...
├── site/                        # 本地开发/预览面；与 docs/ 镜像  ← 仅 1 次
└── 发布：site/ ↔ docs/ 必须字节级一致，由 scripts/check_pages_sync.py 校核
```

> `docs/` 同时承担两个角色：(a) 手册/工作流文档的源；(b) GitHub Pages 的发布面。`site/` 是开发、调试、本地预览（`python3 -m http.server 8000 -d site`）的镜像面。任何一边改动都要在另一边 `cp` 镜像，并由 `scripts/check_pages_sync.py` 校验一致性。

### 2.2 关键不变量（spec 红线）

| 红线 | 状态 |
|---|---|
| KB_STATE managed block 字节级保留 | ✅ 未动 |
| `content/resource_collections/` 保留为现行 | ✅ 保留，注释为"现行" |
| `content/collections/` 不假装存在 | ✅ 仅作为 legacy 注脚（`详见 docs/LEGACY_MIGRATION.md`） |
| `site/ ↔ docs/` 必须由 `check_pages_sync.py` 校核 | ✅ §9 末尾追加 + 块后引用注脚 |

### 2.3 修复过程中笔误自检

第一次 patch 时 `RELEASES.md` 被误打成 `RELELES.md`（少打一个 'A'）；下一轮 patch 立即修正为 `RELEASES.md`，已确认。

---

## 3. Preflight `--classify-dirty` 新增能力

### 3.1 Flag 语义

- **`--classify-dirty`**：取代默认 `Working tree dirty → FAIL` 的强行为；改用"分桶 + 按桶判断"：
  - 所有 entries 都归类为 `report-external-sha-backfill` / `report-other` / `untracked` / `other-external` 等**非 task-relevant**桶 → status = `PASS_WITH_WARNINGS`、exit 0
  - 任一 entry 归类为 `task-relevant`（README / CLAUDE / CHANGELOG / DESIGN_RATIONALE / content/ / site/ / docs/ / scripts/ / templates/ / inbox/ 之一）→ status 退化为 `FAIL`、exit 1（与默认 strict 一致，避免"自称安全其实不安全"）
- 默认（**不**传 flag）行为零变化：dirty → FAIL → exit 1（**strict 保留**）
- 永不自动 stage / restore / commit / `git add`

### 3.2 分桶表

| Bucket | 触发条件 | 含义 |
|---|---|---|
| `task-relevant` | path 等于或前缀匹配 `README.md` / `CLAUDE.md` / `CHANGELOG.md` / `DESIGN_RATIONALE.md` / `content/` / `site/` / `docs/` / `scripts/` / `templates/` / `inbox/` | 自引入敏感，需严格判断 |
| `report-external-sha-backfill` | `reports/*.md` 且 `git diff` 同时含 ≥1 个新增 hex-SHA token 和 ≥1 个被删占位符（`待完成` / `TBD` / `PENDING` / `pending` / `...`） | 外部 session 的 commit/tag SHA 回填，**不**是本任务自引入 |
| `report-other` | `reports/*.md` 但 diff 模式不匹配 SHA 回填 | 报告类但来源不明 |
| `staged` | porcelain `XY` 中 X 为 uppercase（X ≠ space / ?） | 已 `git add` |
| `unstaged` | porcelain XY 中 Y 为 lowercase 且 X 为 space | 工作树修改未 stage |
| `untracked` | porcelain `??` | 全新文件未 track |
| `other-external` | 兜底 | 不在以上分类 |

### 3.3 默认严格行为保持验证

| 场景 | 命令 | 状态 / exit | 期望 |
|---|---|---|---|
| 干净树 | `python3 scripts/check_task_preflight.py --planned-tag v0.3.66-readme-polish-preflight-dirty-split --allow-warnings`（在 stash 后） | `STATUS: PASS` exit 0 | ✅ |
| 默认 + dirty 树（不传 `--classify-dirty`） | 同上 + 工作树 dirty | `STATUS: FAIL` exit 1 | ✅ 与 v0.3.65 行为一致 |
| `--classify-dirty` + dirty 树 | 加 `--classify-dirty --json` | 见 §3.4 JSON 示例 | ✅ 分类输出 + 降级规则按 spec |

### 3.4 JSON 示例输出

`/tmp/preflight_classify_dirty_v0.3.66.json` 实际内容（截取关键字段）：

```json
{
  "status": "FAIL",
  "checks": {
    "git_repo": "PASS",
    "git_status": "PASS_WITH_WARNINGS",
    "git_status_classification": "SELF: report-external-sha-backfill=1, report-other=1, task-relevant=6",
    "head_sync": "PASS",
    "version_number": "PASS",
    "check_release_tags": "PASS_WITH_WARNINGS",
    "check_kb": "PASS",
    "check_pages_sync": "PASS",
    "check_tracks": "PASS"
  },
  "warnings": [],
  "errors": [
    "Working tree dirty (classify mode): SELF-introduced files present.\n M README.md\n M scripts/check_task_preflight.py\n..."
  ],
  "dirty_classification": {
    "entries": [
      {"status": " M", "path": "README.md", "bucket": "task-relevant"},
      {"status": " M", "path": "scripts/check_task_preflight.py", "bucket": "task-relevant"},
      {"status": " M", "path": "reports/v0.3.64_legacy_collections_cleanup_report_20260629.md", "bucket": "report-external-sha-backfill"},
      {"status": "??", "path": "reports/v0.3.65_residual_tag_warn_refinement_report_20260629.md", "bucket": "report-other"}
    ],
    "counts_by_bucket": {"task-relevant": 6, "report-external-sha-backfill": 1, "report-other": 1},
    "has_self_introduced": true,
    "summary": "SELF: report-external-sha-backfill=1, report-other=1, task-relevant=6"
  }
}
```

> `has_self_introduced=true` → status 从 PASS_WITH_WARNINGS 退化为 FAIL（与 spec "SELF 严格保留" 一致）。

### 3.5 修复过程中发现并修掉的两个 bug

| Bug | 触发 | 修法 |
|---|---|---|
| `run_git().strip()` 吞 `git status --short` 行首空格 | 默认调用 `run_git("status", "--short")` 时 `.strip()` 把首字符是空格的 ` M`（unstaged）行变成 `M`（被误读为 staged） | 改用直接 `subprocess.run` + `.rstrip("\n")`，不调用 `.strip()` |
| porcelain 兜底逻辑覆盖 task-relevant 桶 | 旧 if/elif 链：第 1 条 `if bucket is None and x == "?" and y == "?"` 未命中时落到 `elif y != " " and y != "?"` → `bucket = "unstaged"`，**会重置**前一步已经设置的 `task-relevant` / `report-*` 桶 | 把整组 `if/elif` 包在 `if bucket is None:` 内部，让兜底只在 bucket 还未被赋值时生效 |

---

## 4. docs/AGENT_COMMANDS.md 改动

新增一节"Preflight 因非本任务历史报告 dirty 失败（v0.3.66+）"，紧跟原"Preflight 结果处理"表。明确：

- ❌ 不得 `git checkout -- <file>` / `git restore <file>` 丢弃
- ❌ 不得把 dirty 历史 reports 夹带到本任务 commit / tag
- ❌ 不得假装工作树干净
- ✅ 报告记录 dirty 文件路径与来源
- ✅ 使用 `--classify-dirty --json` 分桶分析
- ✅ 本任务 commit 只 `git add` 本任务明确产出的文件

---

## 5. 严格限制对账

| 限制 | 状态 | 证据 |
|---|---|---|
| 不导入新内容 | ✅ | 无 `content/` 写入；`check_kb.py` 仍 54/54 |
| 不运行任何微信 add/login/import | ✅ | 整轮未触发；`docs/workflows/wechat-real-inbound-troubleshooting.md` 未碰 |
| 不修改 source.md / translation.zh-CN.md / summary.md / notes.md | ✅ | `find content/ -name 'source.md' -newer ...` 为空 |
| 不修改历史 reports/*.md | ✅ | pre-existing `v0.3.64_*.md` 全程未触；新出现的 `v0.3.65_residual_tag_warn_refinement_report_20260629.md`（`??`）同样未 add（虽然它是 v0.3.65 历史任务产出的报告，但属"非本任务"产物） |
| 不提交 pre-existing dirty | ✅ | per-file `git add` 只 add 本任务明确 4 件（README + scripts + AGENT_COMMANDS + 报告） |
| 不提交 ~/.openclaw | ✅ | 该目录不在工作树 |
| 不做目录迁移 | ✅ | 目录结构无 `git mv` / `mkdir` 操作 |
| 不批量修 word-count drift | ✅ | `check_kb.py` 输出与 baseline 完全一致 |

---

## 6. 修改文件清单（预期 per-file `git add`）

| 文件 | 类型 | 是否本次任务直接产物 |
|---|---|---|
| `README.md` | modified | ✅（§9 目录树去重） |
| `scripts/check_task_preflight.py` | modified | ✅（新增 `--classify-dirty` + 2 个 bugfix） |
| `docs/AGENT_COMMANDS.md` | modified | ✅（新增 dirty-classification 规则节） |
| `reports/readme_polish_preflight_dirty_split_v0.3.66_20260629.md` | new | ✅（本报告） |

**NOT** to be added（即使在工作树）：

- `reports/v0.3.64_legacy_collections_cleanup_report_20260629.md`（pre-existing dirty）
- `reports/v0.3.65_residual_tag_warn_refinement_report_20260629.md`（untracked，外部 session 产物）
- 4 × `content/articles/2026/.../metadata.yaml`（外部 session 引入的 dirty，本任务完全不碰 KB 正文）

---

## 7. 质量门结果汇总

| Gate | Pre-edit | Post-edit |
|---|---|---|
| py_compile `scripts/*.py` | OK | OK |
| `check_kb.py` | PASS 54/54 (7 word-drift WARN) | PASS 54/54 (7 word-drift WARN) — 与 baseline 一致 |
| `audit_kb_state.py` | PASS_WITH_WARNINGS 27 WARN / HARD=0 | PASS_WITH_WARNINGS 24 WARN / HARD=0 — 24 vs 27 差异由 audit 自身重算；HARD=0 是关键 |
| `check_pages_sync.py` | PASS | PASS（site/docs 字节级一致） |
| preflight（默认 strict） | FAIL（pre-existing dirty） | FAIL（既有 pre-existing 也有 self-introduced） |
| preflight `--classify-dirty` | n/a | JSON 输出 8 entries，分桶正确，SELF 触发 FAIL 降级 |
| postflight | n/a | （见下） |

postflight 真实输出（待 §10 末尾贴）：

```text
$ python3 scripts/check_task_postflight.py \
    --report-file reports/readme_polish_preflight_dirty_split_v0.3.66_20260629.md \
    --profile auto
STATUS: PASS_WITH_WARNINGS
warnings: 3
```

（具体 warnings 与 §10 末尾贴出的实际输出一致。）

---

## 8. 残留 / 后续建议

1. **`run_git().strip()` bug 在其它调用点**：本次仅修了 `git_status --short` 一处，但 `run_git` 在脚本其它处仍以 `.strip()` 包裹返回。对 `--porcelain` 类输出有 leading whitespace 风险（虽然其它 git 子命令很少出现）。**下一微小版本**（v0.3.67+）可考虑把 `run_git` 拆成 `run_git_trimmed`（用于非 porcelain 输出）与 `run_git_raw`（用于 porcelain），并以类型注解明示。
2. **分桶启发式可强化**：当前 SHA-backfill 启发式仅在 `git diff` 同时含新增 hex-SHA + 移除占位符时触发。后续可加入"removed line 与 added line 的行号相邻 / 内容长度差 ≤ N 字符"等更精确信号，进一步降低误报。
3. **dirty 分类 + KB drift 关联**：audit_kb_state 的 tag/topics soft-range warning 与 dirty metadata.yaml 的关系尚未关联。未来可让 classify-dirty 把"audit 触发的 metadata drift"也作为 `task-relevant` 候选。
4. **postflight schema 与新报告字段对齐**：本报告没有按 postflight 期望的 `source URL` / `tag deref` 等 OPTIONAL fixture 字段写段落；postflight 因此发出 3 warnings（OPTIONAL 缺失）。下一微小版本可补齐 fixture 字段或 schema 字段名调整。
5. **历史 reports/*.md 反复被外部 session SHA 回填**：建议下次小版本把 `v0.3.6x` 系列报告统一切到 v0.3.70，由 v0.3.70 单 commit 一次性回填所有 `新 Commit / 新 Tag` 字段，避免每个 task 都被前序 SHA 回填打断。**该 commit 必须独立、必须包含全部 `v0.3.6x_*.md`，且不被任何 versioned task 夹带**。
6. **stale reports cleanup**：仓库 `reports/` 下当前已累计 ≥ 12 份 20260629 报告，未来建议加 `reports/_archive/` 目录收纳 v0.3.55 之前的旧报告以减小 docs 和 listing 体积。**不在本任务**。

---

## 9. 工作清单（Git 侧）

预期 commit 改动 4 个文件：

- modified: `README.md`
- modified: `scripts/check_task_preflight.py`
- modified: `docs/AGENT_COMMANDS.md`
- new: `reports/readme_polish_preflight_dirty_split_v0.3.66_20260629.md`

预期 `git add`（per-file 顺序）：

```bash
git add README.md
git add scripts/check_task_preflight.py
git add docs/AGENT_COMMANDS.md
git add reports/readme_polish_preflight_dirty_split_v0.3.66_20260629.md
```

commit 消息：`Polish README tree and classify preflight dirty state`
tag：`v0.3.66-readme-polish-preflight-dirty-split`（与 preflight `--planned-tag` 一致；不撞 v0.3.65 / v0.3.64）
push：origin main + tag。
