# WeChat Image Localization — v0.3.74

- **任务标签**: `v0.3.74-wechat-image-localization`
- **创建时间**: 2026-07-01
- **STATUS**: **PASS**
- **commit message**: `Localize WeChat article images`

---

## §1 STATUS

**PASS**

新增公众号图片本地化能力：96 张远程 `mmbiz.qpic.cn` 图片已全部下载到对应 KB 条目的 `assets/` 目录，source.md / translation.zh-CN.md 中的图片链接已改写为本地相对路径 `assets/image-NNN.<ext>`，站点生成时自动复制到 `site/items/<slug>/assets/` 和 `docs/items/<slug>/assets/`。页面不再依赖远程微信 CDN。

---

## §2 新增能力说明

### scripts/localize_article_images.py

支持：
- `--article-path <path>`：处理单篇文章
- `--all-wechat`：处理所有 `content_kind: wechat_official_article` 的条目
- `--dry-run`：只报告不下载

工作流程：
1. 扫描 source.md / translation.zh-CN.md 中的 `![alt](url)` Markdown 图片
2. 识别 `https://mmbiz.qpic.cn/...` 等远程图片
3. 下载到 `content/articles/YYYY/<slug>/assets/image-NNN.<ext>`
4. 文件名稳定：`image-001.jpg`, `image-002.png`, ...
5. 扩展名从 Content-Type 或 URL 推断
6. 改写 Markdown 图片链接为 `![alt](assets/image-NNN.<ext>)`
7. mirror 文章的 source.md 和 translation.zh-CN.md 同步改写
8. 下载失败时保留原远程 URL，记录失败原因
9. 不登录微信、不扫码、不读 cookie

### generate_item_pages.py 集成

在 `generate_item_pages()` 主循环中，每生成一个 item 页面后检查 `content/articles/.../assets/` 目录是否存在；存在则用 `shutil.copytree` 复制到 `site/items/<slug>/assets/`。`sync_pages_docs.py` 的 `_copy_tree` 已经递归镜像整个 `items/` 子树，所以 assets 自动同步到 `docs/items/`。

---

## §3 图片本地化策略

- **当前采用**：完全本地化 — 所有远程图片下载到本地 `assets/`
- **文件命名**：`image-NNN.<ext>`（顺序编号，稳定可复现）
- **扩展名推断**：优先 HTTP Content-Type，回退 URL 路径
- **mirror 同步**：source.md 和 translation.zh-CN.md 同时改写
- **失败处理**：下载失败保留原远程 URL，不编造本地路径
- **幂等性**：重复运行不会重复下载（已本地化的图片不再有远程 URL）
- **请求头**：浏览器 UA + Referer: https://mp.weixin.qq.com/（不登录、不读 cookie）

---

## §4 回填结果

### 总览

| 指标 | 值 |
|------|-----|
| articles_processed | 7 |
| image_total | 96 |
| image_localized | 96 |
| image_failed | 0 |
| fallback_remote_kept | 0 |

### 每篇文章

| # | article | image_total | image_localized | image_failed | assets_path |
|---|---------|-------------|-----------------|--------------|-------------|
| 1 | 2026-06-26-wechat-新京报书评周刊-专访林小英... | 13 | 13 | 0 | assets/ |
| 2 | 2026-06-26-wechat-腾讯研究院-ai无法教会的三件事 | 1 | 1 | 0 | assets/ |
| 3 | 2026-06-26-wechat-译林出版社-我生病了要去西湖... | 17 | 17 | 0 | assets/ |
| 4 | 2026-06-27-wechat-澎湃翻书党-从传统评点看金庸... | 4 | 4 | 0 | assets/ |
| 5 | 2026-06-28-wechat-可可乐博-携手之外...ISLS... | 0 | 0 | 0 | (无图片) |
| 6 | 2026-06-28-wechat-文汇读书周报-逆流而上的爱... | 9 | 9 | 0 | assets/ |
| 7 | 2026-06-30-wechat-两步路-北京热门徒步线路top10 | 52 | 52 | 0 | assets/ |

---

## §5 页面检查

### "两步路"文章（52 张图片）

| 检查项 | 结果 |
|--------|------|
| content/.../assets/ 存在 | ✅ 52 个文件 |
| docs/items/.../assets/ 存在 | ✅ 52 个文件 |
| site/items/.../assets/ 存在 | ✅ 52 个文件 |
| 页面中 `src="assets/image-` | ✅ 52 个 |
| 页面中 `src="https://mmbiz.qpic.cn` | ✅ 0 个 |
| 裸 Markdown 图片 `![](...)` | ✅ 0 个 |

### 所有 wechat 文章的 assets 目录

| 位置 | 含 assets 的目录数 |
|------|-------------------|
| content/articles/ | 6 |
| site/items/ | 6 |
| docs/items/ | 6 |

---

## §6 修改文件列表

### 新增

| 文件 | 说明 |
|------|------|
| `scripts/localize_article_images.py` | 图片本地化主脚本 |
| `tests/run_image_localization_smoke.py` | 7 项 smoke 测试 |
| `reports/wechat_image_localization_v0.3.74_20260701.md` | 本报告 |
| 6 个 `content/articles/.../assets/` 目录 | 96 张本地图片 |
| 6 个 `site/items/.../assets/` 目录 | 同上（站点镜像） |
| 6 个 `docs/items/.../assets/` 目录 | 同上（Pages 镜像） |

### 修改

| 文件 | 说明 |
|------|------|
| `scripts/generate_item_pages.py` | 在 item 页面生成后复制 assets/ 到 site/items/ |
| 12 个 source.md / translation.zh-CN.md | 图片链接从远程改写为本地 assets/ |
| docs/data/catalog.json, site/data/catalog.json, index/* | update_site 重新生成 |
| 6 个 site/items/.../index.html + 6 个 docs/items/.../index.html | 重新生成（图片 src 变为本地） |

---

## §7 门禁结果

| 顺序 | 命令 | 结果 |
|------|------|------|
| 1 | `py_compile scripts/*.py` | PASS |
| 2 | `run_smoke_tests.py` | PASS (3/3) |
| 3 | `run_wechat_batch_smoke.py` | PASS (5/5) |
| 4 | `run_item_render_smoke.py` | PASS (6/6) |
| 5 | `run_image_localization_smoke.py` | PASS (7/7) |
| 6 | `check_kb.py` | PASS (61/61) |
| 7 | `update_site.py` | PASS（61 item pages，无删除） |
| 8 | `audit_kb_state.py` | PASS_WITH_WARNINGS (0 HARD FAIL) |
| 9 | `check_pages_sync.py` | PASS（61 slugs + 完整性） |

---

## §8 数量统计

| 计数项 | 值 |
|--------|-----|
| content/articles | 61 |
| docs/items | 61 |
| site/items | 61 |
| synced slugs | 61 |

---

## §9 git diff 摘要

```
60 files changed
+ scripts/localize_article_images.py (新增)
+ tests/run_image_localization_smoke.py (新增)
+ reports/wechat_image_localization_v0.3.74_20260701.md (新增)
+ 96 image files under content/articles/**/assets/
+ 96 image files under site/items/**/assets/
+ 96 image files under docs/items/**/assets/
M scripts/generate_item_pages.py (assets copy)
M 12 × source.md / translation.zh-CN.md (URL → local rewrite)
M catalog/index (regenerated)
M 12 × site/items/.../index.html + docs/items/.../index.html (regenerated)
```

---

## §10 Commit / Push

- **commit message**: `Localize WeChat article images`
- **commit 方式**: 逐文件 `git add`
- **commit hash**: 见最终回复
- **push**: `git push origin main`
- **force push**: 无

---

## §11 下一步建议

1. **`--localize-images` 集成到导入流程**：当前 `wechat_url_to_kb.py` / `wechat_batch_import.py` 尚未内置 `--localize-images` 参数——新文章入库后需要手动跑 `localize_article_images.py --all-wechat`。建议后续在 batch import 的 `--import` 模式末尾自动调用图片本地化。
2. **图片去重**：当前每篇文章独立编号 `image-NNN`，如果多篇文章引用同一张图片，会重复下载。可考虑跨文章去重（但 WeChat 图片通常每篇独立，这个问题不大）。
3. **图片懒加载**：已通过 `<img loading="lazy">` 实现，浏览器会延迟加载视口外的图片。
4. **WebP 转换**：当前保留原始格式（jpg/png/gif），可考虑统一转 WebP 减小体积（但增加依赖）。
5. **图片尺寸优化**：当前下载原始尺寸，可考虑生成缩略图或限制最大尺寸。
