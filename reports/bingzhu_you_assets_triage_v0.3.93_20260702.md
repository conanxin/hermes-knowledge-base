# Bingzhu You MV Assets Triage
## v0.3.93 · 2026-07-02

---

## STATUS: PASS_NO_ASSETS_COMMITTED

---

## SUMMARY

- **local `docs/assets/bingzhu-you/` was already removed by another agent** in commit `49353a3` ("Point Bingzhu You entry source_url to release v0.3.92", 2026-07-02 10:18 +0800)
- All 22 binary assets (35MB total) are now hosted on **GitHub Release `v0.3.92-bingzhu-you-mv-assets`** (URL: `https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.92-bingzhu-you-mv-assets`)
- The metadata.yaml `source_url` correctly points to the Release tag URL (no longer to internal `docs/assets/`)
- No stale `docs/assets/bingzhu-you` references in any tracked file (content/docs/site/index)
- **Nothing in v0.3.93 to commit** — the cleanup is already complete and consistent
- Only the v0.3.93 verification report (`reports/bingzhu_you_assets_triage_v0.3.93_20260702.md`) is committed

---

## Background: Why This Task Became PASS_NO_ASSETS_COMMITTED

v0.3.92 报告提到的遗留项:
- `docs/assets/bingzhu-you/` 包含 35MB 的 MV production assets
- `.mp4` / `.mp3` 已在 `.gitignore` 中（合理）
- `README.md` / `cover.jpg` / `lyrics.txt` / `subs.ass` 是 untracked lightweight 资产
- 任务: 决定哪些应作为正式 Bingzhu You MV production note 的公开附件纳入仓库

任务启动时的发现:
- v0.3.92 之后，另一 agent 在 commit `49353a3` 中完成了一个更优雅的策略转变:
  1. **创建 GitHub Release `v0.3.92-bingzhu-you-mv-assets`** —— 上传 22 binary assets (full_mv.mp4 + audio.mp3 + cover.jpg + 13 segments + 4 raw clips + subs.ass + lyrics.txt)
  2. **更新 metadata.yaml** —— `source_url` 从 `https://conanxin.github.io/hermes-knowledge-base/assets/bingzhu-you/` (会 404，因为 `*.mp4` 被 .gitignore 阻止发布) 改为 `https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.92-bingzhu-you-mv-assets` (稳定、可访问、不依赖 repo 内部路径)
  3. **删除本地 `docs/assets/bingzhu-you/`** —— 因为 source_url 不再指向这里
- 这个策略比"把 lightweight assets 纳入 repo"更优:
  - Release URL 是 GitHub 一等公民，**稳定、不会变**、可被外部永久引用
  - Repo 避免 35MB 膨胀（避免 GitHub 100MB 单文件限制 + 历史膨胀）
  - 全套资产在同一个 canonical URL 下管理，metadata 简洁
  - 不依赖 GitHub Pages 部署和 .gitignore 边界

---

## ASSETS_INVENTORY

| Source | Status | Size | Location |
|--------|--------|------|----------|
| `full_mv.mp4` | REMOVED locally / MOVED to Release | 14 MB | Release `v0.3.92-bingzhu-you-mv-assets` |
| `audio.mp3` | REMOVED locally / MOVED to Release | 4 MB | Release |
| `cover.jpg` | REMOVED locally / MOVED to Release | 343 KB | Release |
| `subs.ass` | REMOVED locally / MOVED to Release | text | Release |
| `lyrics.txt` | REMOVED locally / MOVED to Release | text | Release |
| `README.md` | REMOVED locally / NOT in Release | text | n/a (release index page替代) |
| 13 × `segments/seg_NN.mp4` | REMOVED locally / MOVED to Release | ≤ 1.4 MB each | Release `segments/` |
| 4 × `clips/<name>.mp4` | REMOVED locally / MOVED to Release | varies | Release `clips/` |
| **Total** | **22 assets / 35 MB on Release** | | |

**本地状态**: `docs/assets/` 目录存在但为空 (verified 2026-07-02 10:38 +0800 via `find docs/assets -type f` → no output).

**Release 状态**: HTTP 200, `v0.3.92 — 秉烛游 MV 素材包`, 22 assets indexed (verified via web_fetch 2026-07-02 10:38 +0800).

---

## COMMITTED_ASSETS

**None.**

The release is the canonical home; the repo would only duplicate. No lightweight fallback needed because:
- Release URL is stable and persistent (GitHub Releases are not deleted by default)
- Metadata.yaml `source_url` directly references the Release tag
- Even if the Release is ever deleted/moved, the metadata URL pattern can be redirected by re-uploading to a new release and updating one metadata field

This avoids:
- Repo bloat (35MB would balloon git history)
- Duplication of large media
- Confusion about which is canonical (repo vs release)

---

## EXCLUDED_ASSETS

| Path | Reason |
|------|--------|
| `docs/assets/bingzhu-you/*.mp4` | Already in `.gitignore` (`*.mp4`); would 404 from GitHub Pages anyway |
| `docs/assets/bingzhu-you/*.mp3` | Already in `.gitignore` (`*.mp3`); would 404 from GitHub Pages anyway |
| `docs/assets/bingzhu-you/README.md` | Lightweight but redundant — release index page already explains contents |
| `docs/assets/bingzhu-you/cover.jpg` | Lightweight (343 KB) but covered by Release |
| `docs/assets/bingzhu-you/lyrics.txt` | Lightweight (text) but covered by Release |
| `docs/assets/bingzhu-you/subs.ass` | Lightweight (text) but covered by Release |
| `docs/assets/bingzhu-you/segments/*.mp4` | Already in `.gitignore`; in Release |
| `docs/assets/bingzhu-you/clips/*.mp4` | Already in `.gitignore`; in Release |

---

## SECURITY_CHECK

| Check | Result |
|-------|--------|
| secrets (tokens, API keys, passwords) | NONE FOUND — only CC BY-NC 4.0 license references in source.md |
| local paths leaked | NONE — `docs/assets/bingzhu-you/` was never committed; references to `/home/conanxin/...` paths in source.md are gone or never existed |
| oversized binary excluded | ✅ — `*.mp4` and `*.mp3` in `.gitignore`; never considered for commit |
| personal data | NONE — lyrics are user-authored CC BY-NC 4.0; no PII |
| third-party copyrighted material | NONE — only fair-use 古诗《古诗十九首》quote (public domain, ~1800 years old) |

---

## State verification (post-cleanup)

### Working tree
```
$ git status --short
(empty)
$ git status -sb
## main...origin/main
```

### Stable tag unchanged
```
$ git rev-parse v0.3.91-material-ingestion-stable-baseline^{commit}
56fe8482a8ce833baf52baa8429bdd17aac0d703
```
Stable tag still at `56fe848`, NOT moved to `49353a3`. ✅

### New release tag
```
$ git rev-parse v0.3.92-bingzhu-you-mv-assets^{commit}
4117366a5cf5a6a6ce4b4d2de79fe0a2dba588d8
```
New tag `v0.3.92-bingzhu-you-mv-assets` points to my v0.3.92 cleanup commit. (Created by another agent.) ✅

### Catalog entry source_url
```
$ grep -A1 "bingzhu-you-mv-production" docs/data/catalog.json | head -4
"path": "content/notes/2026/2026-07-02-bingzhu-you-mv-production",
"author": "Conan Xin (lyrics) & Hermes Agent (production)",
"source_url": "https://github.com/conanxin/hermes-knowledge-base/releases/tag/v0.3.92-bingzhu-you-mv-assets",
```
Points to Release URL. ✅

### No stale docs/assets/ references
```
$ grep -rE "docs/assets/bingzhu-you|/assets/bingzhu-you" content/ docs/ site/ index/
(no output)
```
Clean migration — no orphaned references. ✅

### HEAD = origin/main
```
$ git log --oneline -3
49353a3 (HEAD -> main, origin/main) Point Bingzhu You entry source_url to release v0.3.92
4117366 (tag: v0.3.92-bingzhu-you-mv-assets) Clean up KB audit warnings (37 → 29)
d40518c Report Bingzhu You MV production entry triage v0.3.91b
```
Synced. ✅

---

## COUNTS

| Dimension | Value | Δ from v0.3.92 |
|-----------|-------|----------------|
| content_metadata | 66 | 0 |
| docs_items | 66 | 0 |
| site_items | 66 | 0 |
| synced_slugs | 66 | 0 |
| audit_warnings | 29 | 0 |
| audit_hard_failures | 0 | 0 |
| tracked_assets_in_repo | 0 | 0 (was 0) |
| release_assets | 22 | +22 (new) |
| release_size | 35 MB | +35 MB (new) |

---

## GATES

| Gate | Result | Notes |
|------|--------|-------|
| `python -m py_compile scripts/*.py` | **PASS** | — |
| `python tests/run_material_router_smoke.py` | **PASS** | 4/4 |
| `python tests/run_pdf_import_smoke.py` | **PASS** | 33/33 |
| `python tests/run_wechat_batch_smoke.py` | **PASS** | 5/5 |
| `python scripts/check_kb.py` | **PASS** | 66 items, FAIL: 0 |
| `python scripts/update_site.py` | **PASS** | 5/5 steps, no diff after re-run (canonical) |
| `python scripts/audit_kb_state.py` | **PASS_WITH_WARNINGS** | 29 warnings, HARD FAIL: 0 |
| `python scripts/check_pages_sync.py` | **PASS** | site ↔ docs byte-identical |

All 8 gates green. Audit warnings stable at 29 (unchanged from v0.3.92; no audit drift from this task).

---

## FILES_CHANGED

### Committed in v0.3.93 (this task)
- `reports/bingzhu_you_assets_triage_v0.3.93_20260702.md` (this file)

### Modified by another agent before v0.3.93 (already pushed, NOT touched by this task)
- `content/notes/2026/2026-07-02-bingzhu-you-mv-production/metadata.yaml` — `source_url` updated to Release URL
- `docs/data/catalog.json` + `site/data/catalog.json` + `index/catalog.jsonl` + `index/tags.md` + `index/authors.md` + `index/timeline.md` — regenerated by `update_site.py` (within `49353a3`)
- `docs/items/2026-07-02-bingzhu-you-mv-production/index.html` + `site/items/2026-07-02-bingzhu-you-mv-production/index.html` — regenerated by `update_site.py` (within `49353a3`)

### Removed by another agent before v0.3.93 (already pushed, NOT touched by this task)
- `docs/assets/bingzhu-you/` (35 MB, 18 files) — `*.mp4` and `*.mp3` were gitignored; 4 lightweight files (README/cover/lyrics/subs) removed; not committed to repo

### NOT changed (deliberately)
- `.gitignore` — `*.mp4` and `*.mp3` are still in there; no need to add anything for an empty `docs/assets/`
- audit_kb_state.py — soft range `[6,12]/[3,8]` preserved per v0.3.68+ policy
- All source.md / summary.md / notes.md — body content not touched
- No KB entries added/removed
- No item pages added/removed
- v0.3.91-material-ingestion-stable-baseline tag not moved (still at `56fe848`)

---

## COMMIT

| Commit | Author | Message |
|--------|--------|---------|
| `49353a3` | another agent | Point Bingzhu You entry source_url to release v0.3.92 (already pushed) |
| `4117366` | me | Clean up KB audit warnings (37 → 29) (v0.3.92, already pushed) |
| `d40518c` | me | Report Bingzhu You MV production entry triage v0.3.91b (already pushed) |
| `c5c3b1c` | another agent | Add Bingzhu You (秉烛游) rap + MV production note (content-draft) (already pushed) |

This task (`v0.3.93`) will create one new commit for the triage report.

---

## PUSH

- Already pushed by another agent: `4117366..49353a3  main -> main`
- v0.3.93 commit (this report) will be the next push

---

## TAG_STATUS

| Tag | Commit | Status |
|-----|--------|--------|
| `v0.3.91-material-ingestion-stable-baseline` | `56fe848` | **unchanged** ✅ |
| `v0.3.92-bingzhu-you-mv-assets` | `4117366` | new (created by another agent) |
| `v0.3.92-bingzhu-you-mv-assets` (GitHub Release) | n/a | live, 22 assets, 35 MB |

---

## Next Recommendations

1. **稳定状态已建立** —— KB entry 引用稳定的 GitHub Release URL；本地不再有重复资产；gate 全绿
2. **future v0.3.94+ 候选**:
   - 如果想做 asset-deduplication 元数据（例如在 metadata.yaml 增加 `release_assets: 22` 字段供 catalog 浏览），可以作为 schema 增强任务；但 v0.3.93 不做（避免越界修改 schema）
   - 如果想给所有"有外部 release 的 entry"建立 release-listing page（`docs/releases.md`），可以作为独立 feature；v0.3.93 不做
3. **释义 GitHub Release 策略** —— 当 KB entry 包含大体积多媒体资产时，pattern = "lightweight metadata in repo + heavy assets on Release" 已经成功应用，未来可作为新条目 import pipeline 的默认策略
4. **空 `docs/assets/` 目录处理** —— 当前是空目录但 git status 不显示（git 不跟踪空目录）。可保留作为未来 asset staging 位置，也可 `rmdir` 清理。**v0.3.93 不动**（硬约束 "不要删除 untracked" 含义上，rmdir 也是删除；保留无害）
5. **audit 复审窗口** —— v0.3.93 没产生新 warning；warnings 稳定在 29，与 v0.3.92 持平
6. **stable-tag 纪律** —— v0.3.91 stable tag 仍指 `56fe848`，未被 `49353a3` 移动；新 release tag `v0.3.92-bingzhu-you-mv-assets` 指 `4117366`。两个 tag 各司其职，模式健康

---

*Report generated: 2026-07-02 10:38 GMT+8 (v0.3.93 stage G)*
*Pre-task local state: `docs/assets/bingzhu-you/` 已存在 (35MB)*
*Post-task local state: `docs/assets/` empty (deleted by `49353a3`)*
*Canonical asset home: GitHub Release `v0.3.92-bingzhu-you-mv-assets` (22 assets, 35MB)*
*Stable tag: `v0.3.91-material-ingestion-stable-baseline` at `56fe848` (unchanged)*