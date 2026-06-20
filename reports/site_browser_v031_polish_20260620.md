# v0.3.1 Static Knowledge Base Browser Polish

## STATUS: PASS

## 修改文件

| 文件 | 修改内容 |
|------|----------|
| `site/app.js` | 倒序排列、显示 author/date、chip 样式、筛选计数、搜索空态提示、复制 path、GitHub 链接 |
| `site/styles.css` | chip 样式、record-info、record-actions、action-link、action-btn、空态样式 |
| `scripts/export_site_data.py` | 增加 `updated_date` 字段（captured_date → migrated_date → published_date） |
| `README.md` | 补充本地浏览功能说明 |

## 浏览页新增功能

1. **默认倒序排列**：按 `updated_date` 降序显示
2. **显示字段**：title_zh、title、type、author、date、tags、path
3. **chip 样式**：圆角标签，更清晰
4. **筛选计数**：All (17)、article (4)、note (5)、project (4)、collection (4)
5. **搜索空态**：未找到匹配记录，请尝试其他关键词
6. **复制 path**：一键复制到剪贴板
7. **GitHub 链接**：可打开对应文件或目录路径
8. **移动端保持可读**

## 脚本结果

| 脚本 | 结果 |
|------|------|
| `check_kb.py` | **PASS** — 17 items, 17 PASS, 0 FAIL |
| `build_index.py` | **PASS** — 17 records, 126 tags, 13 authors, 4 months |
| `export_site_data.py` | **PASS** — 导出 17 records 到 site/data/catalog.json |
| `check_translation_residue.py` | **WARNING** — 4 files 有专有名词残留（预期行为） |

## 本地浏览命令

```bash
python3 scripts/export_site_data.py
python3 -m http.server 8000 -d site
# 浏览器打开 http://localhost:8000
```

## Commit

- `TBD` — Polish static knowledge base browser
- https://github.com/conanxin/hermes-knowledge-base/commit/TBD
