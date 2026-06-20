# Add GitHub Pages Sync Script

## STATUS: PASS

## 新增文件

| 文件 | 说明 |
|------|------|
| `scripts/sync_pages_docs.py` | 将 site/ 静态文件同步到 docs/，保留其他文档 |
| `scripts/update_site.py` | 一键运行 build_index.py + export_site_data.py + sync_pages_docs.py |
| `reports/site_browser_pages_sync_20260620.md` | 本报告 |

## 修改文件

| 文件 | 修改内容 |
|------|----------|
| `README.md` | 增加"更新在线浏览页"和"一键运行"说明 |

## 同步结果

| 文件 | 来源 | 目标 | 状态 |
|------|------|------|------|
| `index.html` | `site/` | `docs/` | 已同步 |
| `app.js` | `site/` | `docs/` | 已同步 |
| `styles.css` | `site/` | `docs/` | 已同步 |
| `data/catalog.json` | `site/` | `docs/` | 已同步 |

`site/data/catalog.json` 和 `docs/data/catalog.json` 内容一致（diff 验证通过）。

## 脚本结果

| 脚本 | 结果 |
|------|------|
| `check_kb.py` | **PASS** — 17 items, 17 PASS, 0 FAIL |
| `build_index.py` | **PASS** — 17 records, 126 tags, 13 authors, 4 months |
| `export_site_data.py` | **PASS** — 导出 17 records |
| `sync_pages_docs.py` | **PASS** — 同步 4 files |
| `check_translation_residue.py` | **WARNING** — 4 files 专有名词残留（预期） |

## 使用方式

### 分步运行

```bash
python3 scripts/build_index.py
python3 scripts/export_site_data.py
python3 scripts/sync_pages_docs.py
git status
```

### 一键运行

```bash
python3 scripts/update_site.py
```

## Commit

- `8ad4a37` — Add GitHub Pages sync script
- https://github.com/conanxin/hermes-knowledge-base/commit/8ad4a37
