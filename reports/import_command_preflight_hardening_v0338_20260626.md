# v0.3.38-import-command-preflight-hardening Report

**Date**: 2026-06-27
**Branch**: main
**HEAD**: `d2e0af0` "Harden import command preflight checks"
**Origin HEAD**: `d2e0af0` (同步)
**Tag**: `v0.3.38-import-command-preflight-hardening` (annotated, pushed)

---

## STATUS: **PASS** ✅

All v0.3.38 hard gates passed. Preflight script added, documentation updated, tag created.

---

## 1. 起始状态

| 检查项 | 结果 |
|---|---|
| `git status --short` | clean (pull 后) |
| `HEAD == origin/main` | ✅ `012eb6b` → `d2e0af0` |
| v0.3.38 tag 存在性 | **不存在** |
| `check_release_tags.py` recommended next minor | **v0.3.38** ✅ |

---

## 2. 新增脚本

### scripts/check_task_preflight.py

**功能**：任务启动前 preflight 检查

**核心检查**：
1. Git repo 有效性
2. Working tree clean
3. HEAD 与 origin/main 同步
4. Planned tag 不存在（本地和 remote）
5. Minor version 不冲突（不小于 recommended next minor）
6. 核心检查脚本通过（check_kb.py, check_pages_sync.py, check_tracks.py）

**参数**：
- `--planned-tag` — 指定 planned version tag
- `--allow-warnings` — 允许 PASS_WITH_WARNINGS
- `--skip-heavy-checks` — 跳过 check_tracks.py
- `--json` — JSON 输出

**示例命令**：
```bash
python3 scripts/check_task_preflight.py --planned-tag v0.3.38-import-command-preflight-hardening
```

**输出**：
```
STATUS: PASS
Checks:
  git_repo: PASS
  git_status: PASS
  head_sync: PASS
  version_number: PASS
  check_release_tags: PASS_WITH_WARNINGS
  check_kb: PASS
  check_pages_sync: PASS
  check_tracks: PASS
```

---

## 3. 文档更新摘要

### docs/AGENT_COMMANDS.md

- **新增 Preflight 章节**：所有任务开始前必须先运行 preflight
- **普通导入示例**：`python3 scripts/check_task_preflight.py`
- **Versioned task 示例**：`python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name`
- **Preflight 结果处理表格**：PASS / PASS_WITH_WARNINGS / FAIL
- **导入流程**：1. Preflight → 2. 抓取 → 3. 质量检查 → 4. 生成站点 → 5. Commit/Push → 6. Tag
- **版本号选择**：先运行 check_release_tags.py

### docs/CLOUD_HERMES_INTEGRATION.md

- **新增云端 Hermes 开工规则**：
  1. 工作目录必须是 `~/hermes-knowledge-base`
  2. 必须 `fetch + pull --ff-only`
  3. 必须运行 `check_task_preflight.py`
  4. Versioned task 必须传 `--planned-tag`
  5. 禁止 dirty tree / tag 已存在 / 复用版本号
  6. 禁止 force push / commit --amend / git reset --hard

### docs/VERSIONING.md

- **新增 Mandatory Preflight 章节**：v0.3.38+ 所有 versioned task 必须运行 preflight
- **新增 Preflight 检查内容**：6 项检查清单
- **新增 Preflight 结果处理表格**
- **新增版本号选择规则**：先运行 check_release_tags.py，以 recommended_next_minor 为准
- **新增 Tag 创建前后验证**：创建前/后命令
- **新增 Tag 已存在处理**：不删除、不覆盖、不 force push
- **扩展 Agent 检查清单**：加入 preflight 步骤
- **新增 Related Files**：链接到 AGENT_COMMANDS.md, CLOUD_HERMES_INTEGRATION.md

### templates/prompts/import_article_prompt.md

- **新增 Step 0: Preflight（v0.3.38+ 强制）**
- **新增 preflight 命令示例**：普通任务 + versioned task
- **新增 preflight 结果处理表格**
- **抓取阶段补充**：URL 失败/paywall/ACL/正文不完整 → hard stop
- **长名单文章补充**：必须使用完整 source.md

### README.md

- **最小补充**：质量检查命令表格加入 `check_task_preflight.py`
- **新增 preflight 命令示例**

---

## 4. Check 结果

| Script | Result |
|---|---|
| `check_task_preflight.py` | **PASS** (with --planned-tag v0.3.38) |
| `check_release_tags.py` | **PASS_WITH_WARNINGS** (v0.3.36 known exception) |
| `check_kb.py` | **PASS** (44/44 items) |
| `check_tracks.py` | **PASS** (38 verified, 12 needs, 38 embed, 50 search) |
| `update_site.py` | **PASS** (5/5 steps) |
| `check_pages_sync.py` | **PASS** |
| `check_translation_residue.py` | **WARNING** (jasmi pre-existing) |

---

## 5. 文件改动

| 文件 | 状态 | 说明 |
|---|---|---|
| `README.md` | 修改 | 最小补充 preflight 引用 (8 lines) |
| `docs/AGENT_COMMANDS.md` | 重写 | 新增 preflight + 导入流程 (287 lines) |
| `docs/CLOUD_HERMES_INTEGRATION.md` | 重写 | 云端开工规则 (257 lines) |
| `docs/VERSIONING.md` | 修改 | 扩展 preflight + tag 验证 (61 lines) |
| `scripts/check_task_preflight.py` | 新增 | Preflight 检查脚本 (236 lines) |
| `templates/prompts/import_article_prompt.md` | 修改 | 新增 Step 0 preflight (55 lines) |

---

## 6. Generated Diff

**无 generated diff**。update_site.py 未产生新文件（文档更新不影响 site 生成）。

---

## 7. Constraints Honored

- ✅ No `git reset --hard`
- ✅ No `--force` push
- ✅ No `--amend`
- ✅ No 移动/删除/覆盖已有 tag
- ✅ No 修改 Paste 1960s 内容
- ✅ No 修改 source.md / translation.zh-CN.md / tracks.yaml / summary.md / metadata.yaml
- ✅ No 创建 standalone project
- ✅ No 提交 unrelated 文件
- ✅ All hard-stop checks pass

---

## 8. 后续建议

1. **下一个可用版本**：v0.3.39（check_release_tags.py 已确认）
2. **未来导入任务**：必须先运行 `python3 scripts/check_task_preflight.py`
3. **Versioned task**：必须传 `--planned-tag`

---

## 9. Links

- **Commit**: https://github.com/conanxin/hermes-knowledge-base/commit/d2e0af0
- **Tag**: https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.38-import-command-preflight-hardening
- **GitHub Pages**: https://conanxin.github.io/hermes-knowledge-base/
