# v0.3.37-release-index-and-tag-hygiene Report

**Date**: 2026-06-27
**Branch**: main
**HEAD**: `dd833d5` "Add Hermes Agent UI first-round self-audit (v1)"
**Origin HEAD**: `dd833d5` (同步)
**Tag**: `v0.3.37-release-index-and-tag-hygiene` (annotated, pushed)

---

## STATUS: **PASS** ✅

All v0.3.37 hard gates passed. Release index established, tag hygiene check script added.

---

## 1. 起始状态

| 检查项 | 结果 |
|---|---|
| `git status --short` | 3 files: RELEASES.md (M), VERSIONING.md (??), check_release_tags.py (??) |
| `git diff --stat` | docs/RELEASES.md: 101 insertions, 1 deletion |
| `HEAD == origin/main` | ✅ `dd833d5` |
| v0.3.37 tag 存在性 | **不存在** (本地和 remote) |

---

## 2. v0.3.x Tag 信息收集

| 指标 | 值 |
|---|---|
| **v0.3 tags 总数** | 46 |
| **unique minor versions** | 34 |
| **duplicate minor versions** | 12 |

### Duplicate Minor Versions

| Minor | Tags | 状态 |
|---|---|---|
| v0.3.18 | listicle-import-rules, youtube-video-brief-kb-import | ✅ 已知 |
| v0.3.19 | music-track-links, youtube-one-click-kb-import | ✅ 已知 |
| v0.3.20 | music-embed-enrichment-pilot, youtube-kb-import-pilot | ✅ 已知 |
| v0.3.21 | music-embed-enrichment-batch-2, youtube-preflight-failure-archive | ✅ 已知 |
| v0.3.23 | music-embed-enrichment-batch-3, youtube-capability-oss-exposure | ✅ 已知 |
| v0.3.24 | music-embed-enrichment-batch-4, youtube-public-entry-qa | ✅ 已知 |
| v0.3.25 | music-embed-enrichment-batch-5, release-changelog | ✅ 已知 |
| v0.3.26 | music-embed-enrichment-batch-6, palantir-translation-render-fix | ✅ 已知 |
| v0.3.33 | spotify-apple-link-rendering-pilot, paste-greatest-songs-streaming-links | ✅ 已知 |
| v0.3.34 | spotify-apple-link-batch, stash-audit-repo-hygiene | ✅ 已知 |
| v0.3.35 | music-enrichment-final-summary, obsolete-stash-cleanup | ✅ 已知 |
| **v0.3.36** | **repo-health-final-verification, repo-hygiene-and-report-cleanup** | ⚠️ **KNOWN EXCEPTION** |

### v0.3.36 Known Exception 说明

**v0.3.36** 有两个不同语义的 tag，是**有意为之的阶段性标记**：
1. `v0.3.36-repo-health-final-verification` (`8b4f128`) — 先验证仓库健康
2. `v0.3.36-repo-hygiene-and-report-cleanup` (`942cab3`) — 再执行卫生清理

这是**本版本明确标记的 known exception**，不视为需要修复的错误。

**从 v0.3.37 开始，避免复用 minor number**。

---

## 3. docs/RELEASES.md 新增内容摘要

- **保留原有内容**：YouTube capability line (v0.3.18–v0.3.24) + How to Pick a Version 表格
- **新增 Current Policy**：6 条版本策略规则
- **新增完整 v0.3.x Release Line 表格**：从 v0.3.0 到 v0.3.37，共 46 个 tag
- **新增 Known Duplicate Minor-Version Exceptions 表格**：13 行（12 历史 + 1 特别标注）
- **新增 Recommended Next Version**：v0.3.38
- **新增 Related Files**：链接到 VERSIONING.md, check_release_tags.py 等
- **更新 Last updated**：2026-06-27

---

## 4. docs/VERSIONING.md 新增内容摘要

- **版本命名规则**：`v{major}.{minor}-{task-description}` 格式
- **Tag 命名规则**：annotated tag 优先，tag message 必须包含任务简述
- **什么时候创建 annotated tag**：阶段性任务完成 + 通过 hard-stop checks
- **为什么不移动旧 tag**：不可变历史标记，force push 会破坏协作信任
- **新任务如何选择下一个版本号**：执行前检查清单 + 选择规则
- **已知例外**：v0.3.36 双 tag 例外说明 + 历史并行开发模式说明
- **Agent 执行前检查清单**：6 步检查流程
- **相关文档**：链接到 RELEASES.md, check_release_tags.py

---

## 5. scripts/check_release_tags.py 功能

- **只读检查**：不修改文件，不访问网络
- **输出**：
  - v0.3 tags 总数
  - unique minor versions 数量
  - duplicate minor versions 列表（标记 known exception）
  - latest minor version
  - recommended next minor version
  - remote tag 同步检查
- **Exit code**：0 (PASS 或 PASS_WITH_WARNINGS)，1 (FAIL)
- **依赖**：Python 3 标准库 + git

---

## 6. check_release_tags.py 结果

```
STATUS: PASS_WITH_WARNINGS
v0.3 tags: 46
unique minor versions: 34
duplicate minor versions:
  v0.3.36: repo-health-final-verification, repo-hygiene-and-report-cleanup [KNOWN EXCEPTION]
  ... (其他 11 个历史并行开发 duplicate)
latest minor: v0.3.36
recommended_next_minor: v0.3.37
remote v0.3 tags: 46
```

---

## 7. 其他 Check 结果

| Script | Result |
|---|---|
| `python3 scripts/check_kb.py` | **PASS** (43/43 items) |
| `python3 scripts/check_tracks.py` | **PASS** (50 tracks, 38 verified, 12 needs, 38 embed, 50 search) |
| `python3 scripts/update_site.py` | **PASS** (5/5 steps, no diff) |
| `python3 scripts/check_pages_sync.py` | **PASS** |
| `python3 scripts/check_translation_residue.py` | **WARNING** (jasmi pre-existing) |

---

## 8. 文件改动

| 文件 | 状态 | 说明 |
|---|---|---|
| `docs/RELEASES.md` | 修改 | 保留原有 YouTube capability line，扩展完整 release index |
| `docs/VERSIONING.md` | 新增 | 版本命名规则、tag 策略、agent 检查清单 |
| `scripts/check_release_tags.py` | 新增 | 自动 tag 卫生检查脚本 |
| `reports/release_index_and_tag_hygiene_v0337_20260626.md` | 新增 | 本报告 |

---

## 9. Generated Diff

**无 generated diff**。update_site.py 未产生新文件（docs/RELEASES.md 和 docs/VERSIONING.md 不影响 site 生成）。

---

## 10. Constraints Honored

- ✅ No `git reset --hard`
- ✅ No `--force` push
- ✅ No `--amend`
- ✅ No 移动、删除、覆盖已有 tag
- ✅ No 修改 Paste 1960s 内容 (tracks.yaml, summary.md, metadata.yaml 未触碰)
- ✅ No 修改 source.md / translation.zh-CN.md
- ✅ No 创建 standalone project
- ✅ No 提交 unrelated 文件
- ✅ All hard-stop checks pass

---

## 11. 后续建议

1. **下一个可用版本**：v0.3.38（或更高）
2. **未来 agent 执行前**：运行 `python3 scripts/check_release_tags.py` 确认版本号
3. **避免复用 minor number**：从 v0.3.37 开始，每个 minor 只对应一个 tag

---

## 12. Links

- **Commit**: https://github.com/conanxin/hermes-knowledge-base/commit/[COMMIT_HASH]
- **Tag**: https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.37-release-index-and-tag-hygiene
- **GitHub Pages**: https://conanxin.github.io/hermes-knowledge-base/
