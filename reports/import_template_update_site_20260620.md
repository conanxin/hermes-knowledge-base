# Update Import Workflow to Refresh Published Site

## STATUS: PASS

## 修改文件

| 文件 | 修改内容 |
|------|----------|
| `templates/prompts/import_article_prompt.md` | 新增步骤 10：更新在线浏览页（update_site.py），更新质量门禁清单，调整步骤编号 |
| `docs/AGENT_COMMANDS.md` | 执行流程加入 update_site.py，质量门禁加入 update_site.py PASS，导入后自动检查加入 update_site.py |
| `README.md` | 导入后自动检查加入 update_site.py，质量门禁规则加入"在线浏览页同步" |

## 脚本结果

| 脚本 | 结果 |
|------|------|
| `check_kb.py` | **PASS** — 17 items, 17 PASS, 0 FAIL |
| `update_site.py` | **PASS** — build_index.py + export_site_data.py + sync_pages_docs.py 全部通过 |
| `check_translation_residue.py` | **WARNING** — 4 files 专有名词残留（预期行为） |

## site/docs 同步检查

| 检查项 | 结果 |
|--------|------|
| `site/data/catalog.json` vs `docs/data/catalog.json` | **IDENTICAL** — diff 验证通过 |

## 使用方式

### 分步更新

```bash
python3 scripts/build_index.py
python3 scripts/export_site_data.py
python3 scripts/sync_pages_docs.py
```

### 一键更新

```bash
python3 scripts/update_site.py
```

## Commit

- `f37e470` — Update import workflow to refresh published site
- https://github.com/conanxin/hermes-knowledge-base/commit/f37e470
