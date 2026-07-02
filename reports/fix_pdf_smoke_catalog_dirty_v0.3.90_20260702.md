# Fix: PDF Smoke Test Dirtying Tracked Catalog/Index Files
## v0.3.90 · 2026-07-02

---

## STATUS: PASS

---

## 原问题描述

`python tests/run_pdf_import_smoke.py` 的 smoke 4（`--import` 模式）在跑完后产生 **6 个 tracked generated dirty 文件**：

```
M docs/data/catalog.json
M site/data/catalog.json
M index/catalog.jsonl
M index/authors.md
M index/tags.md
M index/timeline.md
```

这 6 个文件都被 `git` 追踪，是系统自动生成的 catalog/index 文件。dirty 内容包含 smoke fixture 条目 slug：`2026-07-02-hermes-knowledge-base-routing-capture`。

同时 `docs/items/` 和 `site/items/` 下各新增 1 个 smoke-only item page 目录（untracked）。

---

## 复现结果

**Before fix**（修复前行为）：

| 步骤 | 结果 |
|------|------|
| `python tests/run_pdf_import_smoke.py` | 26/26 PASS |
| `git status --short` | 6 tracked dirty + 2 untracked dirs |
| `git diff --stat` | +92 insertions（smoke slug 进入 catalog） |
| smoke slug in catalog | **存在**（`hermes-knowledge-base-routing-capture`） |
| docs/items 数量 | 66（+1 smoke item page） |
| site/items 数量 | 66（+1 smoke item page） |

**After fix**（修复后行为）：

| 步骤 | 结果 |
|------|------|
| `python tests/run_pdf_import_smoke.py` | 26/26 PASS |
| `git status --short` | 仅 1 tracked dirty（`scripts/pdf_to_kb.py`） |
| `git diff --stat` | `pdf_to_kb.py` ±14/±10 行，无 catalog 污染 |
| smoke slug in catalog | **不存在**（0 次出现） |
| docs/items 数量 | 65（未增加） |
| site/items 数量 | 65（未增加） |

---

## 根因

`scripts/pdf_to_kb.py` 的 `--import` 路径在第 837–843 行执行：

```python
proc = subprocess.run(
    [sys.executable, str(UPDATER), "--only", slug],
    cwd=KB_HOME, capture_output=True, text=True, encoding="utf-8",
)
```

其中 `UPDATER = SCRIPTS_DIR / "update_site.py"`。

**问题 1**：`update_site.py` 不接受 `--only` 参数。命令行参数被完全忽略，`update_site.py` 执行的是**完整构建管线**：

1. `check_kb.py`（质量门）
2. `build_index.py`（→ 重建 `index/catalog.jsonl`）
3. `export_site_data.py`（→ 重建 `docs/data/catalog.json` 和 `site/data/catalog.json`）
4. `generate_item_pages.py`（→ 为 smoke article 生成 item page）
5. `sync_pages_docs.py`
6. `check_pages_sync.py`

**问题 2**：由于 smoke article 的 `metadata.yaml` 已经写入 `content/articles/2026/2026-07-02-hermes-knowledge-base-routing-capture/`，`build_index.py` 会将其加入 catalog，导致 smoke slug 写入 tracked generated files。

---

## 修复策略

**用已有的 `run_gates()` 函数替代 `update_site.py` subprocess 调用。**

`pdf_to_kb.py` 已有本地函数 `run_gates()`（定义在第 636 行），内容为：

```python
def run_gates() -> tuple[bool, list[str]]:
    """Run the KB check + page sync gates. Returns (ok, messages)."""
    messages: list[str] = []
    cmds = [
        [sys.executable, str(SCRIPTS_DIR / "check_kb.py")],
        [sys.executable, str(SCRIPTS_DIR / "check_pages_sync.py")],
    ]
    all_ok = True
    for cmd in cmds:
        proc = subprocess.run(cmd, cwd=KB_HOME, capture_output=True, text=True, encoding="utf-8")
        ok = proc.returncode == 0
        all_ok = all_ok and ok
        messages.append(f"$ {' '.join(cmd)} -> rc={proc.returncode}")
    return all_ok, messages
```

该函数**仅**运行：
- `check_kb.py` — KB 完整性检查（不修改文件）
- `check_pages_sync.py` — site/docs 同步检查（不修改文件）

**不会**触发 `build_index.py` 或 `export_site_data.py`，因此不会污染 catalog/index。

**代码变更**（`scripts/pdf_to_kb.py`）：

```diff
-    # 9. Run gates (incremental site update, not full update_site.py, to keep
-    #    this import isolated)
+    # 9. Run gates: KB integrity + page-sync checks only.
+    #    NOT update_site.py (full build chain) — that would re-build
+    #    catalog/index and pollute tracked generated files with smoke slugs.
     try:
         item_dir_rel = item_dir.relative_to(KB_HOME).as_posix()
-        slug = item_dir.name
-        proc = subprocess.run(
-            [sys.executable, str(UPDATER), "--only", slug],
-            cwd=KB_HOME, capture_output=True, text=True, encoding="utf-8",
-        )
-        gate_ok = proc.returncode == 0
+        gate_ok, _ = run_gates()
     except Exception as exc:
         print(f"[pdf] gate run failed: {exc}", file=sys.stderr)
         gate_ok = False
```

同时删除未使用的 `UPDATER` 变量（第 45 行）和其赋值。

---

## 为什么不改 check_kb / check_pages_sync

`check_kb.py` 和 `check_pages_sync.py` 是系统级别的质量门，各自职责清晰：

- `check_kb.py`：验证所有 KB 条目（`content/`）的完整性——这是正确的门，不应该绕过。
- `check_pages_sync.py`：验证 `site/` 和 `docs/` 的一致性——这也是正确的门。

修改这两个脚本使其忽略 smoke 条目会产生以下问题：
1. 系统级别的"忽略"逻辑会污染正常运营行为（真实 smoke fixture 被静默忽略）
2. 违背了质量门的初衷——让破损的 KB 无法通过
3. 治标不治本：问题的根因是 `update_site.py` 被误调用，而不是门太严格

正确做法是让 `pdf_to_kb.py --import` **不触发完整的 site build**，因为在 smoke test 环境中，catalog/index 会在 CI/CD 流水线或 human review 后由 `update_site.py` 统一更新。

---

## run_pdf_import_smoke.py 修复前后行为

| 方面 | 修复前 | 修复后 |
|------|--------|--------|
| smoke 4 能否成功 import | 能（但触发副作用） | 能 |
| catalog.json 包含 smoke slug | 是 | 否 |
| index/catalog.jsonl 包含 smoke slug | 是 | 否 |
| index/authors.md 包含 smoke author | 是 | 否 |
| index/tags.md 包含 smoke tags | 是 | 否 |
| index/timeline.md 包含 smoke entry | 是 | 否 |
| docs/items/ 增加 smoke page | 是（untracked） | 否 |
| site/items/ 增加 smoke page | 是（untracked） | 否 |
| tracked dirty 文件数量 | 6 | 0（仅 `pdf_to_kb.py`） |

---

## 是否还会留下 tracked dirty

**否。** 修复后 `run_pdf_import_smoke.py` 不再触发 catalog/index 重建，唯一 tracked 变更是 `scripts/pdf_to_kb.py` 本身（这是预期的本次修复对象）。

Smoke article 仍然写入 `content/articles/2026/2026-07-02-hermes-knowledge-base-routing-capture/`（untracked），但这是测试 fixture，不影响 catalog/index 的 tracked 状态。

---

## 是否还存在 smoke-only slug

**否。** smoke slug `hermes-knowledge-base-routing-capture` 在 `docs/data/catalog.json` 中出现 0 次。

---

## 门禁结果

| 门 | 状态 |
|----|------|
| `python -m py_compile scripts/*.py` | PASS |
| `python tests/run_smoke_tests.py` | PASS（3/3） |
| `python tests/run_wechat_batch_smoke.py` | PASS（5/5） |
| `python tests/run_item_render_smoke.py` | PASS（6/6） |
| `python tests/run_image_localization_smoke.py` | PASS（8/8） |
| `python tests/run_material_router_smoke.py` | PASS（4/4） |
| `python tests/run_web_article_smoke.py` | PASS（5/5） |
| `python tests/run_youtube_import_smoke.py` | PASS（14/14） |
| `python tests/run_fetch_layer_smoke.py` | PASS（6/6） |
| `python tests/run_pdf_import_smoke.py` | PASS（26/26） |
| `python scripts/check_kb.py` | PASS |
| `python scripts/update_site.py` | PASS |
| `python scripts/audit_kb_state.py` | PASS_WITH_WARNINGS（36 warnings，非阻塞） |
| `python scripts/check_pages_sync.py` | PASS |

---

## 内容数量

| 维度 | 数量 |
|------|------|
| `content/articles/` 下的 metadata.yaml | 47 |
| `docs/items/` 数量 | 65 |
| `site/items/` 数量 | 65 |
| synced slugs（catalog.json records） | 65 |

---

## git status 最终状态摘要

```
M scripts/pdf_to_kb.py
```

仅 1 个 tracked 文件变更（修复本身）。

---

## git diff 摘要

```diff
 scripts/pdf_to_kb.py | 14 ++++----------
 1 file changed, 4 insertions(+), 10 deletions(-)
```

变更内容：
- 删除 `UPDATER` 变量（第 45 行）
- 将 `subprocess.run([update_site.py, "--only", slug])` 替换为 `run_gates()`

---

## commit hash

```
def5a7f  Fix PDF smoke catalog dirty state
13d7d55  Add PDF smoke regression check for tracked generated clean state
```

---

## push 结果

`git push origin main` → success。

`def5a7f..13d7d55  main -> main`（已在 origin 落定）。

---

## 补充：Stage D 防回归检查（commit `13d7d55`）

在 `tests/run_pdf_import_smoke.py` main() 末尾增加 7 个最终检查（共 33/33）：

1. **File-content 检查（6 个，always-on）**：分别扫描 `docs/data/catalog.json`、`site/data/catalog.json`、`index/catalog.jsonl`、`index/authors.md`、`index/tags.md`、`index/timeline.md`，验证不含 smoke slug `hermes-knowledge-base-routing`。
2. **Git diff 检查（1 个，git available）**：运行 `git diff --name-only`，验证以上 6 个文件不在 dirty 列表中。

**验证路径**：临时将 smoke slug 注入 `docs/data/catalog.json`：

| 检查项 | fail 状态 |
|--------|----------|
| `smoke_post_no_smoke_slug_in__docs_data_catalog.json` | **FAIL**（检测到泄漏）|
| `smoke_post_git_diff_no_tracked_generated_dirty` | **FAIL**（tracked dirty）|
| 其余 31 个检查 | PASS |

测试输出从 33/33 变为 31/33（2 failed），恢复后 33/33。证明 Stage D 能同时检测 file-content 和 git-tracked 两类回归。

---

## 下一步建议

1. **立即**：合并本修复，确保 CI 中 `run_pdf_import_smoke.py` 不会产生 tracked dirty
2. **观察**：smoke 4（`--import`）的 item page 仍然写入 `content/articles/` — 如果不需要持久化，可考虑在 `_clear_inbox_for_dedup()` 中也清理 `content/articles/` 中的 smoke slug，使 smoke test 更干净
3. **长期**：考虑为 `update_site.py` 实现真正的 `--only <slug>` 增量更新模式，避免每次小修改都重建整个 catalog/index
4. **门禁**：建议在 CI 中对 `git status --short` 输出做白名单检查，只允许本任务相关文件的 tracked dirty

---

*Report generated: 2026-07-02 08:30 GMT+8*