# Word-Count Metadata Refresh (v0.3.67) — 2026-06-29

## Summary

metadata-only warning cleanup. 7 个 `word_count.translation` 漂移 WARN 全部归零：每个 metadata.yaml 的 `word_count.translation` 数值被更新为 `translation.zh-CN.md` 实际 CJK 字符数（脚本统计 `[\u4e00-\u9fff]` 范围）。**未**改任何正文 / 翻译 / 摘要 / 笔记 / 微信 / 微信公众号 JSON 任何文件。

⚠ **本任务的全部 metadata.yaml 字字 patch 在 patch 写盘期间被外部 session commit `493a3e0` 提前 push 到 origin/main**，本任务 commit 走"audit-trail-only" 路径——与 v0.3.65 / v0.3.66 模式一致。

| 维度 | Before | After |
|---|---|---|
| `check_kb.py` WARN 数量 | 7 (全部 word_count.translation drift) | **0** |
| `audit_kb_state.py` HARD FAILURES | 0 | 0 |
| `audit_kb_state.py` WARN 数量（其余） | 24 | 24（不变） |
| `check_pages_sync.py` | PASS | PASS |
| `update_site.py` 派生文件是否变化 | — | **无 diff**（catalog 导出不含 word_count 字段） |

---

## 1. Drift 清单（before / after）

| # | metadata.yaml path | declared (before) | actual CJK | patched (after) | delta (before → after) |
|---|---|---:|---:|---:|---|
| 1 | `content/articles/2026/2026-06-27-swift-modest-proposal/metadata.yaml` | 3200 | 5157 | **5157** | -2057 (declared 偏低 38.0%) |
| 2 | `content/articles/2026/2026-06-27-thoreau-walking/metadata.yaml` | 19600 | 5584 | **5584** | +14016 (declared 偏高 251.0%) |
| 3 | `content/articles/2026/2026-06-28-wechat-可可乐博-携手之外国际学习科学年会isls-2026-的五条主线/metadata.yaml` | 11422 | 10414 | **10414** | +1008 (declared 偏高 9.7%) |
| 4 | `content/articles/2026/2026-06-27-thoreau-civil-disobedience/metadata.yaml` | 1500 | 1353 | **1353** | +147 (declared 偏高 10.9%) |
| 5 | `content/articles/2026/2026-06-25-jasmi-the-old-world-is-dying/metadata.yaml` | 3800 | 4360 | **4360** | -560 (declared 偏低 12.8%) |
| 6 | `content/articles/2026/2026-06-27-emerson-self-reliance/metadata.yaml` | 11000 | 7859 | **7859** | +3141 (declared 偏高 40.0%) |
| 7 | `content/articles/2026/2026-06-27-emerson-compensation/metadata.yaml` | 17500 | 4571 | **4571** | +12929 (declared 偏高 282.9%) |

所有 7 项 patched 后**字字等于** `check_kb.py` 报的 `actual_cjk` 数值（脚本与本任务独立统计一致）。

---

## 2. 严格限制对账

| 限制 | 状态 | 证据 |
|---|---|---|
| 不导入新内容 | ✅ | 54/54 不变；`check_kb.py` 仍 54 条 PASS |
| 不改正文文件 | ✅ | `git diff` 仅触及 7 个 metadata.yaml；`source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` / `raw_payload.json` 全部零 diff（spec 字段 grep 全空） |
| 不修翻译 | ✅ | `translation.zh-CN.md` 全部 7 个均未触；CJK 字符数与 patch 前完全一致 |
| 不重写 metadata 其他字段 | ✅ | 每个 metadata.yaml 改动 = 1 行 = `word_count.translation: <OLD> → <NEW>`；其它字段（title / author / source_url / tags / topics / content_kind / import_method / import_version / word_count.source / `*_date` 等）零修改 |
| 不批量裁剪 tags/topics | ✅ | 24 个 tag/topic soft-range WARN 保持不变（与 baseline 一致） |
| 不做微信绑定 / 扫码 / `openclaw channels add/login` | ✅ | 整轮未触发；`wechat-real-inbound-troubleshooting.md` 与 `import_wechat_article_capture.py` 未触 |
| 不提交 pre-existing dirty | ✅ | `memory/2026-06-29.md` / `reports/metadata_cleanup_baseline_freeze_v0.3.66.md` / `reports/v0.3.66_metadata_cleanup_baseline_freeze_report_20260629.md` / `reports/v0.3.65_residual_tag_warn_refinement_report_20260629.md` 全程未 add（其中前 3 个已被外部 commit `493a3e0` 推上 main；第 4 个的 M 改也已被 `493a3e0` 一并带入 HEAD） |
| 不提交 `~/.openclaw` | ✅ | 该目录不在工作树 |
| per-file `git add` | ✅ | 仅 add 本任务产出的 `reports/word_count_metadata_refresh_v0.3.67_20260629.md`（详见 §6） |

---

## 3. git diff stat（patch 写盘后、HEAD 493a3e0 推进前那一刻）

```
 content/articles/2026/2026-06-25-jasmi-the-old-world-is-dying/metadata.yaml | 2 +-
 content/articles/2026/2026-06-27-emerson-compensation/metadata.yaml          | 2 +-
 content/articles/2026/2026-06-27-emerson-self-reliance/metadata.yaml         | 2 +-
 content/articles/2026/2026-06-27-swift-modest-proposal/metadata.yaml         | 2 +-
 content/articles/2026/2026-06-27-thoreau-civil-disobedience/metadata.yaml    | 2 +-
 content/articles/2026/2026-06-27-thoreau-walking/metadata.yaml               | 2 +-
 content/articles/2026/2026-06-28-wechat-可可乐博-携手之外国际学习科学年会isls-2026-的五条主线/metadata.yaml | 2 +-
 7 files changed, 7 insertions(+), 7 deletions(-)
```

**每个文件 1 行 1 改 = 2 字符 diff**（仅 `word_count.translation: <OLD> → <NEW>`）。

sanity check（`swift-modest-proposal`）：

```diff
 word_count:
   source: 3500
-  translation: 3200
+  translation: 5157
 content_kind: "essay"
 import_method: "short_command_preflight_e2e_regression"
 import_version: "v0.3.39"
```

> 注：上表所列 7 个 metadata.yaml 的 patch 内容（确切字符）**字字相同**于外部 session commit `493a3e0` 内对应文件的 diff。这是为什么 7 个 file 在我 patch 写盘后 → HEAD 被 `493a3e0` 推进后 → working tree SHA 与 HEAD SHA 一致 → `git status` 报告 clean。

---

## 4. update_site.py 派生产物清单

`scripts/update_site.py` 5 步全部 OK：

| 步 | 脚本 | 结果 |
|---|---|---|
| 0 | `check_kb.py`（hard-stop） | PASS 54/54，0 warnings |
| 1 | `build_index.py` | OK |
| 2 | `export_site_data.py` | OK |
| 3 | `generate_item_pages.py` | OK |
| 4 | `sync_pages_docs.py` | OK |
| 5 | `check_pages_sync.py`（post-sync） | OK |

派生文件 SHA 对照（worktree vs HEAD `493a3e0`）：

| 路径 | worktree SHA | HEAD SHA | 变化 |
|---|---|---|---|
| `site/index.html` | `8f3f50e3f148` | `8f3f50e3f148` | 相同（HEAD 已含） |
| `docs/index.html` | `8f3f50e3f148` | `8f3f50e3f148` | 相同（HEAD 已含） |
| `site/data/catalog.json` | `6e86a2438fb7` | `6e86a2438fb7` | 相同（HEAD 已含） |
| `docs/data/catalog.json` | `6e86a2438fb7` | `6e86a2438fb7` | 相同（HEAD 已含） |

> **关键观察**：`site/` / `docs/` / `index/` 派生文件在 update_site.py 重新生成后**字节级与 HEAD 完全一致**。这意味着：catalog 导出 / 详情页 / index/timeline / index/tags / index/authors / index/catalog.jsonl **不读取** `word_count.translation` 字段（catalog 只输出基本元数据 type/title/source/author/dates/tags/topics）。**所以 update_site 派生 0 dirty**——本任务 commit 不需要 add site/docs/index 任何文件。

外部 commit `493a3e0` 推上来的 `site/data/catalog.json` / `docs/data/catalog.json` / `index/catalog.jsonl` / `index/tags.md` / `index/authors.md` 的 diff 在 `git show 493a3e0` 里能看到（30/30/20/50 行），但它们与本任务本次重新跑 update_site.py 的结果**字节级相同**（deterministic generation）。

---

## 5. 质量门结果汇总

| Gate | Pre-edit | Post-edit (after patch + update_site) |
|---|---|---|
| py_compile `scripts/*.py` | OK | OK |
| `check_kb.py` | PASS, **7 WARN** | **PASS, 0 WARN** ← 7 → 0 |
| `audit_kb_state.py` | PASS_WITH_WARNINGS, 24 WARN, HARD=0 | PASS_WITH_WARNINGS, 24 WARN, HARD=0（24 是 tag/topic soft-range，与本任务无关） |
| `check_pages_sync.py` | PASS | PASS |
| preflight `--classify-dirty --json`（post-update） | n/a | PASS_WITH_WARNINGS（仅 dirty 2 项 EXTERNAL；memory/ + reports/v0.3.66_metadata_cleanup_baseline_freeze_report_20260629.md 已被外部 `493a3e0` 带入 HEAD） |
| update_site.py 5-step | n/a | All steps OK |

---

## 6. 修改文件清单（实际 git add）

`HEAD = 493a3e0` 之后 working tree clean，**没有 metadata.yaml 可 commit**。本任务 commit 仅含 audit trail：

- **new**: `reports/word_count_metadata_refresh_v0.3.67_20260629.md`（本文件）

**NOT to be added**（即使在工作树）：

- 7 × `content/articles/.../metadata.yaml`（已由 `493a3e0` 推上 main，worktree SHA = HEAD SHA，无 diff）
- 任何 `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` / `raw_payload.json`（本任务全程未触；零 diff）
- `memory/2026-06-29.md`（外部 session 产物，本任务不 add；HEAD `493a3e0` 已含）
- `reports/metadata_cleanup_baseline_freeze_v0.3.66.md`（同上）
- `reports/v0.3.66_metadata_cleanup_baseline_freeze_report_20260629.md`（同上）
- `reports/v0.3.65_residual_tag_warn_refinement_report_20260629.md`（外部 session 的 M 已被 `493a3e0` 一并带入 HEAD；worktree SHA = HEAD SHA）
- `site/` / `docs/` / `index/` 任何派生文件（HEAD `493a3e0` 已含）
- `~/.openclaw/*`（不在工作树）

---

## 7. 残留 / 后续建议

1. **`memory/` 路径分类 bug**（preflight 改进项）：当前 `_TASK_RELEVANT_PATH_PREFIXES` 不含 `memory/`，所以 `memory/2026-06-29.md` 在 `--classify-dirty` 模式下被分类为 `unstaged` 而非 `task-relevant`，会误导 agent 把 memory/ 改动当作 EXTERNAL。**下一微小版本**（v0.3.68+）建议把 `memory/` 加入 `_TASK_RELEVANT_PATH_PREFIXES`。
2. **派生文件不读 `word_count` 字段**：确认 `site/data/catalog.json` / `index/catalog.jsonl` / `items/*/index.html` 都不输出 word_count，所以**本任务 commit 0 dirty site/docs/index** 是设计行为，不是 bug。Audit/详情页如果以后想显示字数，需先在 `export_site_data.py` + `generate_item_pages.py` 加 word_count 字段输出。
3. **24 个 tag/topic soft-range WARN 仍存在**：本次范围只清 word_count，未动 tags/topics。可在下个 v0.3.68 单独处理（按各条目阅读形态做 fit-into-range 评估）。
4. **preflight 头 head_sync 偏差瞬态问题**：本次 session 期间 origin/main 至少被外部 session 推进 2 次（`dbe0aeb` → `493a3e0`），preflight 在两窗口之间报 FAIL。**这是 v0.3.66 设计的 v0.3.66+ 行为**——降级为 PASS_WITH_WARNINGS 后继续。无需修复；只是 operator 要意识到 session 期间外部活动频繁。
5. **外部 session 并行执行问题**：v0.3.65 / v0.3.66 / v0.3.67 三次任务都发生"核心改动被外部 commit 提前落地"模式。建议 future tasks 先 `git fetch` 再做 `git diff HEAD...origin/main` 检查，避免"做无用功"。本任务已经按这个习惯来跑，但外部 session 速度更快。
6. **dbe0aeb / 493a3e0 这两个 commit 都引入"历史 reports 微调"**：v0.3.65 报告被 dbe0aeb + 493a3e0 两次微调（line 30 SHA 回填），严格说仍属"修改历史 reports"模式——但这是外部 session 在我未在场时做的，不归本任务。下一微小版本可考虑冻结历史 reports：`.gitattributes` 加 `reports/v0.3.[0-6][0-9]_*.md merge=ours` 防止 rebase / amend 时被覆盖。

---

## 8. 残留 WARN（与本任务正交）

| WARN | 数量 | 类别 | 处置 |
|---|---:|---|---|
| `tags count` 越出 soft range [6,12] | 多个 | 软范围提示 | 待 v0.3.68+ 单独 fit-into-range |
| `topics count` 越出 soft range [3,8] | 多个 | 软范围提示 | 同上 |
| `check_release_tags.py` 推荐下一版 | 1 | 推荐 next minor | tag hygiene，下次 minor 切到 v0.3.68+ 时消除 |

---

## 9. 工作清单（Git 侧）

预期 commit 改动 1 个文件：

- new: `reports/word_count_metadata_refresh_v0.3.67_20260629.md`（本文件，audit trail）

预期 `git add`（per-file）：

```bash
git add reports/word_count_metadata_refresh_v0.3.67_20260629.md
```

commit 消息：`Refresh translation word_count metadata`
tag：`v0.3.67-word-count-metadata-refresh`（与 preflight `--planned-tag` 一致；不撞 v0.3.65 / v0.3.66 / v0.3.62-pdf-ocr-* / v0.3.63-pdf-ocr-*）
push：origin main + tag。
