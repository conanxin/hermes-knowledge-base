# Real WeChat Batch Import Regression — v0.3.73

- **任务标签**: `v0.3.73-wechat-real-batch-regression`
- **创建时间**: 2026-07-01
- **STATUS**: **PASS**
- **commit message**: `Import real WeChat batch regression articles`

---

## §1 STATUS

**PASS**

5 篇公众号文章全部成功导入。所有门禁通过（check_kb 61/61, check_pages_sync 61 slugs）。页面渲染正确（无"中文翻译"重复，图片渲染为 `<img>`）。

---

## §2 输入链接列表

1. https://mp.weixin.qq.com/s/3YC72QkVirX7AJpl58cnow
2. https://mp.weixin.qq.com/s/XtJsfYmI0LrGyo42Yjc3PA
3. https://mp.weixin.qq.com/s/BwLPBh-f435DVn-ivvSohQ
4. https://mp.weixin.qq.com/s/wxCIOlazQlZxa_6KulnSFQ
5. https://mp.weixin.qq.com/s/be9-vAYCkq_a_RkuZEpEiw

---

## §3 每篇文章结果

| # | status | title | account | date | source_url |
|---|--------|-------|---------|------|------------|
| 1 | IMPORTED | 逆流而上的爱与勇气——写在阿伦特诞辰120周年之际 | 文汇读书周报 | 2026-06-28 | https://mp.weixin.qq.com/s/3YC72QkVirX7AJpl58cnow |
| 2 | IMPORTED | 从传统评点看金庸｜《倚天》篇：张无忌为什么总是被骗？ | 澎湃翻书党 | 2026-06-27 | https://mp.weixin.qq.com/s/XtJsfYmI0LrGyo42Yjc3PA |
| 3 | IMPORTED | 专访林小英：接受教育，最终是为了让我们把日子过得生动 | 新京报书评周刊 | 2026-06-26 | https://mp.weixin.qq.com/s/BwLPBh-f435DVn-ivvSohQ |
| 4 | IMPORTED | "我生病了，要去西湖玩玩才能好起来" | 译林出版社 | 2026-06-26 | https://mp.weixin.qq.com/s/wxCIOlazQlZxa_6KulnSFQ |
| 5 | IMPORTED | AI无法教会的三件事 | 腾讯研究院 | 2026-06-26 | https://mp.weixin.qq.com/s/be9-vAYCkq_a_RkuZEpEiw |

capture_json_path / kb_article_path / docs_item_path / site_item_path 详见 manifest JSON（`reports/wechat_batch_import_20260701_112909.json`）。

---

## §4 汇总

| 状态 | 数量 |
|------|------|
| total | 5 |
| imported | 5 |
| skipped_duplicate | 0 |
| blocked_fetch_failed | 0 |
| blocked_incomplete_text | 0 |
| failed_import | 0 |
| failed_gate | 0 |

---

## §5 新增 KB 条目列表

| # | 条目路径 |
|---|---------|
| 1 | `content/articles/2026/2026-06-28-wechat-文汇读书周报-逆流而上的爱与勇气写在阿伦特诞辰120周年之际/` |
| 2 | `content/articles/2026/2026-06-27-wechat-澎湃翻书党-从传统评点看金庸倚天篇张无忌为什么总是被骗/` |
| 3 | `content/articles/2026/2026-06-26-wechat-新京报书评周刊-专访林小英接受教育最终是为了让我们把日子过得生动/` |
| 4 | `content/articles/2026/2026-06-26-wechat-译林出版社-我生病了要去西湖玩玩才能好起来/` |
| 5 | `content/articles/2026/2026-06-26-wechat-腾讯研究院-ai无法教会的三件事/` |

每个条目含完整 6 文件：metadata.yaml / source.md / translation.zh-CN.md / summary.md / notes.md / raw_payload.json。

metadata 关键字段：
- `content_kind: "wechat_official_article"` ✅
- `source_platform: "wechat_official_account"` ✅
- `source_url` 正确 ✅
- `title / account / author / published_date` 正确 ✅
- `is_translation_mirror: true` ✅（v0.3.72 新字段，确保不显示重复"中文翻译"）

---

## §6 页面渲染检查

对 5 篇新文章的 site/items 详情页检查：

| 文章 | "中文翻译" | "正文 / 中文原文" | 裸 mmbiz markdown | `<img>` 数 |
|------|-----------|-------------------|-------------------|-----------|
| 阿伦特诞辰 | 0 ✅ | 1 ✅ | 0 ✅ | 10 ✅ |
| 金庸倚天 | 0 ✅ | 1 ✅ | 0 ✅ | 4 ✅ |
| 林小英专访 | 0 ✅ | 1 ✅ | 0 ✅ | 14 ✅ |
| 西湖玩玩 | 0 ✅ | 1 ✅ | 0 ✅ | 17 ✅ |
| AI三件事 | 0 ✅ | 1 ✅ | 0 ✅ | 2 ✅ |

**结论**：
- 无"中文翻译"重复 ✅
- 无裸 Markdown 图片链接 ✅
- 图片渲染为 `<img>` ✅

---

## §7 数量统计

| 计数项 | 值 |
|--------|-----|
| content/articles | 61（从 56 增加 5） |
| docs/items | 61 |
| site/items | 61 |
| synced slugs | 61 |

---

## §8 门禁结果

| 顺序 | 命令 | 结果 |
|------|------|------|
| 1 | `py_compile scripts/*.py` | PASS |
| 2 | `run_smoke_tests.py` | PASS (3/3) |
| 3 | `run_wechat_batch_smoke.py` | PASS (5/5) |
| 4 | `run_item_render_smoke.py` | PASS (6/6) |
| 5 | `check_kb.py` | PASS (61/61) |
| 6 | `update_site.py` | PASS（61 个 item 页面，无删除） |
| 7 | `audit_kb_state.py` | PASS_WITH_WARNINGS (0 HARD FAIL, 28 WARN) |
| 8 | `check_pages_sync.py` | PASS（61 slugs + 完整性） |

---

## §9 git diff 摘要

```
新增 5 个 KB 条目（每个 6 文件 = 30 文件）
新增 5 个 capture JSON（inbox/raw/wechat/）
新增 5 个 docs/items/*/index.html
新增 5 个 site/items/*/index.html
修改 catalog/index（docs/data/catalog.json, site/data/catalog.json, index/catalog.jsonl, index/authors.md, index/tags.md, index/timeline.md）
新增 manifest（reports/wechat_batch_import_20260701_112909.md + .json）
新增本报告
```

---

## §10 Commit / Push

- **commit message**: `Import real WeChat batch regression articles`
- **commit 方式**: 逐文件 `git add`
- **commit hash**: 见最终回复
- **push**: `git push origin main`

---

## §11 下一步建议

1. **人工补全 summary.md / notes.md**：脚本生成的 summary/notes 是结构化骨架（启发式填充关键句 + 小标题 + 概念），解释性部分（一句话总结、核心问题、个人阅读提示等）留有"（请人工补充）"占位。建议对这 5 篇文章逐一补全。
2. **topics/tags 人工修正**：脚本的 `infer_topics` / `infer_tags` 对文学/教育/哲学类文章的覆盖有限——这 5 篇文章的 topics 列表可能不够准确（如阿伦特文章应含"哲学""政治"主题），建议人工修正。
3. **重复检测验证**：如果对同一批 URL 再跑一次 `--import`，应全部 `SKIPPED_DUPLICATE`——建议做一次重复检测回归。
4. **图片本地化**：当前仍依赖微信 CDN（mmbiz.qpic.cn），建议后续实现图片下载到 `assets/` + 路径改写。
