# Stash Audit and Repo Hygiene Report (v0.3.34)

**任务名称**: STASH_AUDIT_AND_REPO_HYGIENE_V0334
**日期**: 2026-06-27
**状态**: PASS

## 仓库状态

- HEAD: 01bb6fc (Merge remote-tracking branch 'origin/main')
- Branch: main
- Remote: origin (https://github.com/conanxin/hermes-knowledge-base.git)
- Worktree: clean
- Stash 总数: 17 (2 条为空 stash)

## 当前 Tags 摘要

| Tag | Commit |
|-----|--------|
| v0.3.26-palantir-translation-render-fix | 8c59e3c |
| v0.3.32-final-candidate-sweep-and-coverage-sync | d393433 |
| v0.3.33-paste-greatest-songs-streaming-links | e3d1ec6 |
| v0.3.33-spotify-apple-link-rendering-pilot | e3d1ec6 |
| v0.3.34-spotify-apple-link-batch | 01bb6fc |

## Stash 审计总表

| ID | 消息 | 文件数 | 主要任务 | 状态 | 风险 | 建议 |
|----|------|--------|----------|------|------|------|
| stash@{0} | stash tracks.yaml before v0.3.26 post_tag_verify | 1 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{1} | stash tracks.yaml before palantir translation fix | 1 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{2} | stash paste-greatest-songs changes before palantir translation fix | 2 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{3} | stash remaining paste changes before palantir commit | 11 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{4} | stash paste-greatest-songs changes before palantir commit | 10 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{5} | stash item pages before palantir video import | 2 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{6} | stash docs/styles.css and generate_item_pages.py before palantir video import | 3 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{7} | stash unrelated changes before palantir video import | 4 | catalog/index | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{8} | stash unrelated paste tracks changes before palantir video import | 6 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{9} | stash site generation artifacts before v0.3.22 commit | 84 | youtube-capability | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{10} | stash all remaining docs/site modifications before v0.3.22 | 77 | youtube-capability | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{11} | stash unrelated changes before v0.3.22 youtube-oss-exposure | 2 | youtube-capability | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{12} | stash unrelated changes before v0.3.21 youtube-preflight | 1 | youtube-capability | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{13} | stash unrelated changes before v0.3.20 verify | 7 | youtube-capability | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{14} | stash unrelated paste tracks before v0.3.20 tag | 2 | paste-greatest-songs | superseded_by_later_commit | low | drop_after_user_confirm |
| stash@{15} | stash paste greatest songs article before v0.3.19 tagging | 0 | paste-greatest-songs | duplicate_or_obsolete | none | drop_after_user_confirm |
| stash@{16} | stash v0.3.18 tag report before v0.3.19 tagging | 0 | tag-report | duplicate_or_obsolete | none | drop_after_user_confirm |

## 按任务分组的 Stash 清单

### Paste-Greatest-Songs 任务 (stash 0-8, 14)

共 10 条 stash，全部与 paste-greatest-songs 音乐条目相关。

**判断依据**:
- v0.3.33 tag (e3d1ec6) 已包含完整的 paste-greatest-songs streaming links 修复
- v0.3.34 tag (01bb6fc) 已包含进一步的 streaming link batch 更新
- 这些 stash 的内容（tracks.yaml, metadata.yaml, summary.md, catalog.json, styles.css, generate_item_pages.py, item pages）已全部在后续提交中覆盖

**建议**: 全部可安全删除

### YouTube-Capability 任务 (stash 9-13)

共 5 条 stash，与 YouTube 能力线相关。

**判断依据**:
- v0.3.18 至 v0.3.25 tags 已覆盖 YouTube 视频导入、预检、失败归档、OSS 暴露、QA、release changelog
- stash 9-13 的内容（README.md, YOUTUBE_CAPABILITIES.md, commands, workflows, items/index.html, app.js, templates, generate_item_pages.py）已全部在后续提交中覆盖

**建议**: 全部可安全删除

### 空 Stash (stash 15-16)

共 2 条空 stash。

**判断依据**:
- 创建时工作树已 clean，无实际内容

**建议**: 直接删除

## 可安全后续删除候选列表

| Stash ID | 原因 |
|----------|------|
| stash@{0} | v0.3.33/v0.3.34 已覆盖 |
| stash@{1} | v0.3.33/v0.3.34 已覆盖 |
| stash@{2} | v0.3.33/v0.3.34 已覆盖 |
| stash@{3} | v0.3.33/v0.3.34 已覆盖 |
| stash@{4} | v0.3.33/v0.3.34 已覆盖 |
| stash@{5} | v0.3.33/v0.3.34 已覆盖 |
| stash@{6} | v0.3.33/v0.3.34 已覆盖 |
| stash@{7} | v0.3.33/v0.3.34 已覆盖 |
| stash@{8} | v0.3.33/v0.3.34 已覆盖 |
| stash@{9} | v0.3.22-v0.3.25 已覆盖 |
| stash@{10} | v0.3.22-v0.3.25 已覆盖 |
| stash@{11} | v0.3.22-v0.3.25 已覆盖 |
| stash@{12} | v0.3.22-v0.3.25 已覆盖 |
| stash@{13} | v0.3.22-v0.3.25 已覆盖 |
| stash@{14} | v0.3.33/v0.3.34 已覆盖 |
| stash@{15} | 空 stash |
| stash@{16} | 空 stash |

**总计**: 17 条 stash 全部可安全删除

## 仍需保留列表

无

## 需要人工确认列表

无 (基于当前信息判断全部可删除)

## 风险说明

1. **删除前建议备份**: 虽然判断全部可删除，但建议先执行 `git stash show -p stash@{N}` 确认无意外内容
2. **顺序删除**: 从 stash@{16} 开始倒序删除，避免索引变化导致误删
3. **分批删除**: 不要一次性删除全部 17 条，建议分 3-4 批执行

## 后续建议

1. **清理 stash**: 执行 `git stash clear` 或逐条 `git stash drop stash@{N}`
2. **建立 stash 规范**: 未来 stash 时添加更详细的描述，包含关联的 issue/任务编号
3. **及时清理**: 任务完成后立即清理相关 stash，避免累积
4. **自动化检查**: 在 CI/CD 或 pre-commit hook 中检查 stash 数量，超过阈值时告警

## 执行命令参考

```bash
# 查看单条 stash 内容确认
git stash show -p stash@{0}

# 删除单条 stash
git stash drop stash@{0}

# 清空所有 stash (谨慎使用)
git stash clear
```

---

**注意**: 本报告仅做审计记录，不执行任何删除操作。实际删除需用户确认。
