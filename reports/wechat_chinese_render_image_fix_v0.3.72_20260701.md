# WeChat Chinese Render + Image Fix — v0.3.72

- **任务标签**: `v0.3.72-wechat-chinese-render-image-fix`
- **创建时间**: 2026-07-01
- **STATUS**: **PASS**
- **commit message**: `Fix Chinese WeChat article rendering and images`

---

## §1 STATUS

**PASS**

修复了三个问题：
1. 中文公众号文章详情页不再显示重复的"中文翻译"区——改为只显示一次"正文 / 中文原文"。
2. Markdown 图片 `![](url)` 现在渲染为 `<img>` 标签，不再以裸文本显示。
3. 既有文章里的空图片引用 `![]()` 也被正确清理（不再残留为裸 markdown）。

---

## §2 问题诊断

### 问题 1：中文翻译与原文重复

- `source.md` = 文章标题/作者/来源/日期/链接 header + 完整中文正文
- `translation.zh-CN.md` = 完整中文正文（无 header）
- 两者相似度 99.5%（仅差 header 块）
- metadata 已标 `language: "zh-CN"` + `translation_language: "zh-CN"`
- 详情页同时显示"中文翻译"和"原文 / 源文本"两个区块 → 内容重复

### 问题 2：图片不渲染

- `generate_item_pages.py` 的 `_apply_inline()` 处理了链接 `[text](url)` 但没处理图片 `![alt](url)`
- `_LINK_RE` 正则 `r"\[([^\]]+)\]\(([^)\s]+)\)"` 对 `![](url)` 不匹配（空 alt 不满足 `([^\]]+)`）
- 结果：102 个 `![` 以裸文本出现在 HTML 中，0 个 `<img>` 标签

### 问题 3：空图片引用

- `2026-06-24-421news-the-people-are-never-right` 的 source.md 里有 `![]()` 空图片引用
- 修复前的图片正则要求 URL 至少 1 字符，空 URL 不匹配 → 残留为裸 markdown

---

## §3 修改文件列表

### 修改

| 文件 | 说明 |
|------|------|
| `scripts/generate_item_pages.py` | 1. 新增 `_IMAGE_RE` + `_image_sub()`，在 `_apply_inline` 中先于 `_LINK_RE` 处理 `![alt](url)` → `<img>`；空 URL 的 `![]()` 被丢弃。2. 新增 `_detect_translation_mirror()` 函数：检查 `is_translation_mirror: true` 标志或启发式（language=zh-CN + translation_language=zh-CN + source/translation 相似度 ≥ 85%）。3. `load_record_body()` 对 mirror 文章删除 translation section。4. 新增 `_section_label()` / `_section_open()` / `_primary_body_key()` 的 `is_mirror` 参数：mirror 文章的 source 重命名为"正文 / 中文原文"、默认展开、成为 primary body。 |
| `scripts/import_wechat_article_capture.py` | metadata 生成器新增 `is_translation_mirror: true` 字段（所有新导入的中文公众号文章都会带上） |
| `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/metadata.yaml` | 新增 `is_translation_mirror: true` |
| `site/styles.css` + `docs/styles.css` | 新增 `.markdown-body img` 样式：max-width:100%、height:auto、border-radius:8px、display:block、lazy load |
| `docs/data/catalog.json` / `site/data/catalog.json` / `index/catalog.jsonl` | 含新 is_translation_mirror 字段 |
| `docs/items/*/index.html` / `site/items/*/index.html` | 重新生成（4 个 item 页面有实质变化：两步路 + ISLS + 421news + jasmi） |

### 新增

| 文件 | 说明 |
|------|------|
| `tests/fixtures/wechat_chinese_with_images.md` | 合成中文文章 fixture（含图片） |
| `tests/run_item_render_smoke.py` | 6 项渲染 smoke 测试 |
| `reports/wechat_chinese_render_image_fix_v0.3.72_20260701.md` | 本报告 |

---

## §4 中文文章去重显示策略

**检测**（`_detect_translation_mirror()`）：
1. 优先看 metadata 的 `is_translation_mirror: true` 标志
2. 回退启发式：`language == "zh-CN"` AND `translation_language == "zh-CN"` AND source/translation 相似度 ≥ 85%

**处理**：
- 删除 translation section（不渲染"中文翻译"）
- source section 重命名为"正文 / 中文原文"
- source 成为 primary body（贡献 TOC、默认展开）

**外文文章不受影响**：英文文章（如 paulgraham-superlinear-returns）仍显示"中文翻译"+"原文 / 源文本"两个区块。

---

## §5 Markdown 渲染修复方式

在 `_apply_inline()` 中，在 `_LINK_RE` 之前新增 `_IMAGE_RE` 替换：

```python
_IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)\s]*)\)")

def _image_sub(m):
    alt, url = m.group(1), m.group(2)
    if not url:  # 空 URL 的 ![]() 直接丢弃
        return ""
    url = url.replace("&amp;", "&")
    alt_attr = f' alt="{html.escape(alt, quote=True)}"' if alt else ""
    return f'<img src="{html.escape(url, quote=True)}"{alt_attr} loading="lazy">'

s = _IMAGE_RE.sub(_image_sub, s)  # 先处理图片
s = _LINK_RE.sub(_link_sub, s)    # 再处理链接
```

关键点：
- 图片正则的 URL 组用 `[^)\s]*`（允许空字符串），空 URL 的 `![]()` 被丢弃而非残留
- 图片正则必须在链接正则之前执行，否则 `![alt](url)` 会被链接正则匹配为 `!<a>alt</a>`

CSS：
```css
.markdown-body img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 8px 0;
  display: block;
}
```

---

## §6 图片渲染策略

**当前采用：远程图片渲染**。

- 页面中的 `mmbiz.qpic.cn` 图片以 `<img src="远程URL">` 形式渲染
- 优点：零额外存储、实现简单
- 缺点：依赖微信 CDN 不防盗链；若微信下线图片则失效

**后续建议：本地化图片**（本轮未做）：
1. 入库时下载图片到 `content/articles/YYYY/<slug>/assets/`
2. 站点生成时复制到 `docs/items/<slug>/assets/` + `site/items/<slug>/assets/`
3. Markdown 图片链接改写为本地相对路径
4. 避免微信防盗链或图片失效

---

## §7 "两步路"文章修复结果

| 检查项 | 修复前 | 修复后 |
|--------|--------|--------|
| "中文翻译"区 | 显示（与"原文"重复） | **不显示** ✅ |
| "正文 / 中文原文"区 | 不存在（标为"原文 / 源文本"） | **显示** ✅ |
| 图片渲染 | 0 个 `<img>`，102 个裸 `![` | **52 个 `<img>`，0 个裸 `![`** ✅ |
| 裸 mmbiz markdown | 102 处 | **0 处** ✅ |
| summary.md / notes.md | 人工补全内容 | **保留不动** ✅ |
| 条目本身 | 存在 | **保留不删** ✅ |

---

## §8 数量统计

| 计数项 | 值 |
|--------|-----|
| content/articles | 56 |
| docs/items | 56 |
| site/items | 56 |
| synced slugs | 56 |

---

## §9 测试命令和结果

| 命令 | 结果 |
|------|------|
| `python3 -m py_compile scripts/*.py` | PASS |
| `python3 tests/run_smoke_tests.py` | ALL SMOKE TESTS PASSED (3/3) |
| `python3 tests/run_wechat_batch_smoke.py` | ALL BATCH SMOKE TESTS PASSED (5/5) |
| `python3 tests/run_item_render_smoke.py` | ALL RENDER SMOKE TESTS PASSED (6/6) |
| `python3 scripts/check_kb.py` | PASS (56/56) |
| `python3 scripts/update_site.py` | PASS（56 个 item 页面，无删除） |
| `python3 scripts/audit_kb_state.py` | PASS_WITH_WARNINGS (0 HARD FAIL) |
| `python3 scripts/check_pages_sync.py` | PASS（56 slugs + 完整性） |

---

## §10 门禁结果

| 顺序 | 命令 | 结果 |
|------|------|------|
| 1 | `py_compile scripts/*.py` | PASS |
| 2 | `run_smoke_tests.py` | PASS (3/3) |
| 3 | `run_wechat_batch_smoke.py` | PASS (5/5) |
| 4 | `run_item_render_smoke.py` | PASS (6/6) |
| 5 | `check_kb.py` | PASS (56/56) |
| 6 | `update_site.py` | PASS（56 item pages） |
| 7 | `audit_kb_state.py` | PASS_WITH_WARNINGS |
| 8 | `check_pages_sync.py` | PASS（56 slugs） |

---

## §11 git diff 摘要

```
18 files changed
M scripts/generate_item_pages.py (图片渲染 + mirror 检测)
M scripts/import_wechat_article_capture.py (is_translation_mirror 字段)
M content/articles/.../metadata.yaml (is_translation_mirror: true)
M site/styles.css + docs/styles.css (img CSS)
M docs/data/catalog.json + site/data/catalog.json + index/catalog.jsonl
M docs/items/*/index.html + site/items/*/index.html (4 个有实质变化)
+ tests/fixtures/wechat_chinese_with_images.md
+ tests/run_item_render_smoke.py
+ reports/wechat_chinese_render_image_fix_v0.3.72_20260701.md
```

---

## §12 Commit / Push

- **commit message**: `Fix Chinese WeChat article rendering and images`
- **commit 方式**: 逐文件 `git add`
- **commit hash**: 见最终回复
- **push**: `git push origin main`
- **force push**: 无

---

## §13 下一步建议

1. **图片本地化**：当前依赖微信 CDN，建议后续实现图片下载到 `assets/` + 路径改写（见 §6）。
2. **已有中文文章回填 `is_translation_mirror`**：当前只有"两步路"和"ISLS"两篇公众号文章有此标志；ISLS 文章的 `is_translation_mirror` 是启发式检测自动识别的（无需手动加），但其他非公众号的中文 article 如果也有翻译镜像问题，可以批量回填。
3. **`_detect_translation_mirror` 性能**：`difflib.SequenceMatcher` 对长文本（14K 字符）的相似度计算约 50ms，56 个条目全量重建约 2.8s——可接受，但如果条目数增长到数百，可考虑缓存或预计算。
4. **Markdown renderer 增强**：当前是 stdlib 最小实现，不支持表格列对齐、嵌套列表等复杂语法；如果后续需要更完整渲染，可考虑引入 `markdown` 或 `mistune` 库。
