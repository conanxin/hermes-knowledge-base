# 任务报告: v0.3.63 PDF OCR recipe postflight 与 PUSH_MODE 分支小修补

### 1. STATUS

- 状态: **PASS**
- 任务类型: 写入并发布(versioned docs-only hardening task)
- 阶段: Step 8/8 — 逐文件 git add / commit / tag / push
- 耗时: <本会话内完成,所有阶段在 1 turn 内闭环>
- preflight: PASS(8/8 checks)
- v0.3.62 postflight: PASS_WITH_WARNINGS(3 warnings,全部为可解释的 existing-state 提示,见 §5)
- 质量门禁: `check_kb.py` PASS / `check_pages_sync.py` PASS 54/54 / `check_translation_residue.py` WARNING(全部为专名/书名,pre-existing)

### 2. SCOPE

做了什么:

1. 重跑 v0.3.62 postflight,使用 v0.3.41+ 当前正确协议
   (`--report` / `--tag` / `--commit` / `--expect-clean` / `--expect-head-origin` / `--json`),
   输出 JSON 保存为 `reports/pdf_ocr_recipe_v0.3.62_postflight_20260629.json`。
2. 给 `templates/prompts/import_pdf_ocr_prompt.md` 新增显式 `{{PUSH_MODE}} 分支` 一节
   (在 Phase 0 之前判定,三种分支: `commit_and_push` / `local_only` / `dry_run`,
   含停止线、硬约束、报告必填字段、分支校验输出);同步更新 Phase 0 / Phase 7 / Phase 8 描述
   与 Hard-stop 规则。
3. 给 `docs/workflows/pdf-ocr-kb-import-workflow.md` 改写 Phase 10 Postflight 命令为 v0.3.41+ 协议,
   新增 Phase 0.5 `PUSH_MODE` 分支与执行阶段对应表,把 `--report-file` 标注为 legacy 兼容项
   (`--report` 优先);补 hard-stop 规则。
4. 给 `docs/import-recipes/PDF_OCR_LOCAL.md` 新增 §3.1 `PUSH_MODE` 分支(在 §3 之后立刻判定,
   三个分支的停止线与硬约束),§21 顶部加 `PUSH_MODE` 限制说明,§21.1 Postflight 单独成节
   (v0.3.41+ 当前正确命令 + 6 项要点),Appendix B 末尾用真实命令替换 `# python3 scripts/check_task_postflight.py ...` 占位。
5. 给 `docs/commands/pdf-ocr-kb-import-command.md` 新增 `{{PUSH_MODE}}` variants 节,
   列出三种调用方式(默认提交 / `local_only` / `dry_run`)与等价变体,以及默认值与 hard-stop 规则。
6. 跑 `check_kb.py` / `check_pages_sync.py` / `check_translation_residue.py` 三个质量门禁(全部通过)。
7. 写本报告 + JSON 收口。

没做什么(明确排除):

- ❌ 不处理任何新 PDF;❌ 不跑 OCR
- ❌ 不新增 `content/articles/` / `content/books/` / `content/papers/` 条目
- ❌ 不修改 Le Guin 条目(2026-06-29-le-guin-carrier-bag-theory-of-fiction)
- ❌ 不修改 `docs/data/catalog.json` / `site/data/catalog.json` / `docs/items/` / `site/items/` / `index/*.md`
- ❌ 不运行 `update_site.py`(`check_pages_sync.py` 未要求同步)
- ❌ 不安装新依赖
- ❌ 不重启 `hermes-gateway.service`
- ❌ 不发送 Telegram
- ❌ 不修改 `conanxin.github.io/projects/data.json`
- ❌ 不使用 `git add -A` 或 `git add .`
- ❌ 不修改 recipes / workflows / prompts 之外的内容(例如 `docs/AGENT_COMMANDS.md`)

边界声明:

- 本任务为 **docs-only hardening**,不重建站点、不改 catalog、不动 content。
- 三个质量门禁的现有 WARNING(7 条 `check_kb.py` 词数漂移 / 全部为专名的 `check_translation_residue.py` WARNING)
  均为 **pre-existing state**,本任务未引入新 warning,也未尝试修复(超出本任务 scope)。

### 3. ACTIONS(按阶段切分)

**阶段 1: 准备 [READ-ONLY]**

- `git fetch origin`
- `git pull --ff-only origin main` → Already up to date
- `python3 scripts/check_release_tags.py` → `recommended_next_minor: v0.3.63`
- `python3 scripts/check_task_preflight.py --planned-tag v0.3.63-pdf-ocr-postflight-pushmode` → **PASS**(8/8)

**阶段 2: 补跑 v0.3.62 postflight [READ-ONLY]**

- `python3 scripts/check_task_postflight.py --report reports/pdf_ocr_local_import_recipe_v0.3.62_20260629.md --tag v0.3.62-pdf-ocr-local-import-recipe --commit 00b913b00274ff43d3c2aba9ebb014c26fd7e79d --expect-clean --expect-head-origin --json` → **PASS_WITH_WARNINGS**
  - `tag_deref = 00b913b...` ✓ 与 `--commit` 一致
  - `HEAD = origin/main = 00b913b...` ✓
  - `git_clean = False`(untracked 仅 `reports/pdf_ocr_recipe_v0.3.62_postflight_20260629.json`,本任务刚生成的收口输出)
  - 3 warnings:
    1. working tree not clean(untracked JSON,即本次 postflight 输出本身)
    2. v0.3.62 报告缺 recommended import fields(source URL / content directory / GitHub Pages URL) — pre-existing(v0.3.62 任务时间早于 v0.3.41+ 推荐字段集,不影响 v0.3.62 任务自身的发布成功)
    3. v0.3.62 报告缺 recommended feature fields(modified files / checks) — pre-existing,同上
- 状态: PASS_WITH_WARNINGS,符合"继续"门

**阶段 3: 修改 prompt 模板 [WRITE]**

- `templates/prompts/import_pdf_ocr_prompt.md`:
  - 修改变量表中 `{{PUSH_MODE}}` 行的描述,明确三个允许值
  - 新增 `## {{PUSH_MODE}} 分支(必读,在 Phase 0 之前判定)` 整节(57 — 134 行),含:
    - 分支判定表(三个分支 × 7 个维度)
    - `commit_and_push`(默认模式)子节
    - `local_only`(本地落盘但不发布)子节(允许/不允许动作列表)
    - `dry_run`(可行性分析,不写 content)子节(允许/不允许动作列表 + dry-run 报告必填内容)
    - 分支校验输出 + 未知值 hard-stop
  - Phase 0 末尾追加 `PUSH_MODE resolved: <branch>` 输出要求
  - Phase 7 — 8 重写,明确"如果 `{{PUSH_MODE}} == dry_run` 或 `local_only`,Phase 7 — 9 整体不执行",Phase 8 标题改为 "Commit + Push(仅 `commit_and_push`)"
  - Hard-stop 规则追加:`{{PUSH_MODE}}` 不在三个值之内 → blocked,写 `pdf_ocr_local_import_blocked_<YYYYMMDD>.md`,不猜测

**阶段 4: 修改 workflow [WRITE]**

- `docs/workflows/pdf-ocr-kb-import-workflow.md`:
  - 修改变量表中 `{{PUSH_MODE}}` 描述(三值 + 空值等同默认 + 未知值 hard-stop)
  - 新增 `### Phase 0.5 — PUSH_MODE 分支与执行阶段对应(mandatory, blocking)` 整节(82 — 110 行),含三值表 + 停止线 + 分支校验输出 + 三个分支的差异说明
  - 重写 `### Phase 10 — Postflight` 为 v0.3.41+ 当前正确命令(`--report` / `--tag` / `--commit` / `--expect-clean` / `--expect-head-origin` / `--json`);明确 `--report-file` 为 legacy 兼容项;新增"判定真发布成功的 5 件套"引用
  - Hard-stop cases 追加"`{{PUSH_MODE}}` not in `commit_and_push` / `local_only` / `dry_run`"

**阶段 5: 修改 recipe [WRITE]**

- `docs/import-recipes/PDF_OCR_LOCAL.md`:
  - 新增 `### 3.1 PUSH_MODE 分支(在 §3 之后立刻判定)` 子节(62 — 96 行),含分支表 + 停止线 + 硬约束(三条) + 分支校验输出
  - §21 顶部加 PUSH_MODE 限制说明(仅 `commit_and_push` 执行)
  - 新增 `### 21.1 Postflight(versioned 任务必跑)` 整节(472 — 494 行),含 v0.3.41+ 当前正确命令 + 5 项要点(`--report` vs `--report-file` 优先级、4 个 flag 必传齐、`--strict` / `--json` 行为、live smoke vs postflight 分工、FAIL 处理)
  - Appendix B 末尾用真实命令替换占位

**阶段 6: 修改 command 文档 [WRITE]**

- `docs/commands/pdf-ocr-kb-import-command.md`:
  - 新增 `## {{PUSH_MODE}} variants(同一命令,三种执行模式)` 整节(44 — 100 行),含:
    1. 默认提交(`commit_and_push`)— 完整命令 + 等价变体
    2. 只生成本地结果(`local_only`)— 完整命令 + 3 个等价变体 + 执行结果描述
    3. 只做 dry-run(`dry_run`)— 完整命令 + 3 个等价变体 + 执行结果描述
    4. 默认值与 hard-stop 规则

**阶段 7: 质量门禁 [READ-ONLY]**

- `python3 scripts/check_kb.py` → **PASS** + 7 warnings(全部为 `word_count.translation drift`,pre-existing)
- `python3 scripts/check_pages_sync.py` → **PASS** 54/54(site slugs 54 / docs slugs 54 / all 54 byte-identical)
- `python3 scripts/check_translation_residue.py` → **WARNING**(所有 suspicious 项均为专名 / 书名 / URL / 英文标题,符合 `docs/TRANSLATION_RESIDUE_POLICY.md` 允许范围;pre-existing)
- `update_site.py` **未运行**(`check_pages_sync.py` PASS 不要求同步;且本任务为 docs-only)

**阶段 8: 报告 + 收口 [WRITE]**

- 写本报告(`reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629.md`,模板 3)
- 阶段 9 / 10 在下一 commit 完成:逐文件 `git add` / `commit` / `tag -a v0.3.63-pdf-ocr-postflight-pushmode` / `git push origin main` / `git push origin v0.3.63-pdf-ocr-postflight-pushmode`

### 4. FILES CHANGED

| 路径 | 操作 | Δ |
|---|---|---|
| `templates/prompts/import_pdf_ocr_prompt.md` | [WRITE] (edit) | +84 / −5 |
| `docs/workflows/pdf-ocr-kb-import-workflow.md` | [WRITE] (edit) | +50 / −5 |
| `docs/import-recipes/PDF_OCR_LOCAL.md` | [WRITE] (edit) | +67 / −1 |
| `docs/commands/pdf-ocr-kb-import-command.md` | [WRITE] (edit) | +54 / −0 |
| `reports/pdf_ocr_recipe_v0.3.62_postflight_20260629.json` | [WRITE] (new) | +1 |
| `reports/pdf_ocr_postflight_pushmode_hardening_v0.3.63_20260629.md` | [WRITE] (new) | +1 |

**Files unchanged**(明确没动):

- `content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/`(6 文件全部不动)
- `content/articles/...`(所有其它 53 个条目,本任务不动)
- `docs/data/catalog.json` / `site/data/catalog.json`
- `docs/items/...` / `site/items/...`(54 个 detail page 全部不动)
- `index/{authors,catalog.jsonl,tags,timeline}.md`
- `content/books/` / `content/papers/`(本任务无新增)
- `conanxin.github.io/projects/data.json`(跨仓库,本任务不动)
- `CLAUDE.md` / `DESIGN_RATIONALE.md` / `AGENTS.md` / `docs/AGENT_COMMANDS.md`(本任务不动;后续若想统一文档化 `PUSH_MODE` 概念,可在 v0.3.64+ 单独加)

**Diff stat**(本任务在 commit 时锁定 4 个 modified + 1 个 untracked JSON + 1 个新报告):

```
docs/commands/pdf-ocr-kb-import-command.md   | 54 ++++++
docs/import-recipes/PDF_OCR_LOCAL.md         | 68 +++++++++-
docs/workflows/pdf-ocr-kb-import-workflow.md | 55 +++++++-
templates/prompts/import_pdf_ocr_prompt.md   | 89 +++++++++++++-
4 files changed, 256 insertions(+), 10 deletions(-)
```

### 5. EVIDENCE

| 引用 | 置信度 | 验证时间 |
|---|---|---|
| `check_release_tags.py` → `recommended_next_minor: v0.3.63` | high | 2026-06-29 本会话 |
| `check_task_preflight.py` PASS 8/8 | high | 2026-06-29 本会话 |
| `check_task_postflight.py --report v0.3.62 --tag v0.3.62 --commit 00b913b...` → `PASS_WITH_WARNINGS` | high | 2026-06-29 本会话 |
| `tag_deref == commit == HEAD == origin/main == 00b913b00274ff43d3c2aba9ebb014c26fd7e79d` | high | 2026-06-29 本会话 |
| `check_kb.py` → STATUS: PASS, 7 pre-existing warnings | high | 2026-06-29 本会话 |
| `check_pages_sync.py` → STATUS: PASS 54/54 | high | 2026-06-29 本会话 |
| `check_translation_residue.py` → STATUS: WARNING(全部专名/书名,符合 `docs/TRANSLATION_RESIDUE_POLICY.md`) | high | 2026-06-29 本会话 |
| 4 个 modified 文件,均无 content / site / catalog 改动 | high | 2026-06-29 本会话 `git diff --stat` |
| 工作树 untracked 仅 `reports/pdf_ocr_recipe_v0.3.62_postflight_20260629.json` + 本报告 | high | 2026-06-29 本会话 `git status` |

### 6. CHECKS

| 检查 | 结果 |
|---|---|
| KB integrity(`check_kb.py`) | **PASS** + 7 pre-existing warnings(全部为 `word_count.translation drift`,非本任务引入) |
| Pages sync(`check_pages_sync.py`) | **PASS** 54/54(site 54 / docs 54 / byte-identical) |
| Translation residue(`check_translation_residue.py`) | **WARNING**(全部为专名 / 书名 / URL / 英文标题,符合 `docs/TRANSLATION_RESIDUE_POLICY.md` 允许范围;pre-existing) |
| Build pipeline(`update_site.py`) | **未运行**(`check_pages_sync.py` PASS 不要求同步;本任务为 docs-only) |
| Pre-push rebase | clean(0/0,pull --ff-only 已成功) |
| Preflight(v0.3.63) | **PASS** 8/8 |
| v0.3.62 postflight(补跑) | **PASS_WITH_WARNINGS**(3 warnings,全部为可解释的 existing-state 提示) |
| Live HTTP(本任务不涉及发布内容变化) | N/A(`check_pages_sync.py` 已是离线 byte-identity 验证) |

### 7. COMMIT / PUSH / LIVE

- commit hash: `<将在 step 8 实际 commit 后填入;预期:00b913b 之后的 1 个新 commit>`
- push status: `<将在 step 8 实际 push 后填入;预期:success>`
- rebase status: clean(0/0)
- 远端 ahead/behind: 0/0
- tag object: `<将在 step 8 实际 `git tag -a` 后填入>`
- tag deref commit: `<将等于 commit hash;预期:00b913b 之后的 1 个新 commit>`
- tag push: `<将在 step 8 实际 `git push origin v0.3.63-pdf-ocr-postflight-pushmode` 后填入;预期:success>`
- live CDN: **N/A**(本任务为 docs-only hardening,不修改任何用户可见的 catalog 字段;`site/styles.css` 未改,detail pages 未改,homepage / catalog 不会变化;不需要 live 验证)
- live last-modified: N/A

### 8. KNOWN LIMITATIONS

- 启发式判断: 无
- 未跑全流程: **docs-only hardening 不需要跑完整 publish 流程**(`check_pages_sync.py` 已 PASS、`update_site.py` 不需要重跑、live smoke 不适用)
- CDN 延迟: N/A(本任务不发布新内容)
- v0.3.62 postflight 报告的 3 warnings:
  1. working tree not clean:来自本任务刚生成的 `reports/pdf_ocr_recipe_v0.3.62_postflight_20260629.json`,不是真正的 dirty 状态。
  2. v0.3.62 报告缺 recommended import fields:pre-existing(v0.3.62 任务早于 v0.3.41+ 推荐字段集)。
  3. v0.3.62 报告缺 recommended feature fields:pre-existing,同上。
  上述 3 项均不阻塞本任务。是否补 v0.3.62 报告字段 → 见 §9 next action。
- pre-existing quality warnings: 7 条 `check_kb.py` 词数漂移 + 全部为专名的 `check_translation_residue.py` WARNING,均非本任务引入,是否清理超出本任务 scope。
- `--report-file` 兼容项保留:为不破坏 v0.3.41 之前的脚本调用,`--report-file` 仍作为 alias 接受;workflow / recipe / prompt 已明确 `--report` 优先。

### 9. NEXT ACTION

- (执行 step 8)逐文件 `git add` + `commit` + `tag -a v0.3.63-pdf-ocr-postflight-pushmode` + `git push origin main` + `git push origin v0.3.63-pdf-ocr-postflight-pushmode`。
- (可选,后续 v0.3.64+)补 v0.3.62 报告的 recommended import / feature 字段(`source URL` / `content directory` / `GitHub Pages URL` / `modified files` / `checks`),消除 v0.3.62 postflight 残余 warnings。本任务不做(超出 scope,且 v0.3.62 已发布)。
- (可选,后续 v0.3.64+)清理 7 条 `check_kb.py` pre-existing 词数漂移 warnings。本任务不做(超出 scope)。
- (可选,后续 v0.3.64+)把 `PUSH_MODE` 概念同步到 `docs/AGENT_COMMANDS.md` / `CLAUDE.md` / `DESIGN_RATIONALE.md` 的索引段落。本任务不做(超出 scope,且本次只动 4 个 PDF OCR 直接相关的文件)。
- (无 / 等待用户下一步指令)
