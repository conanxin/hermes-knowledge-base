# web-article-kb-import

> **命令名称**: `web-article-kb-import`
> **用途**: 把公开可访问的普通网页文章抓取、抽取正文并加入 Hermes Knowledge Base。
> **Workflow**: [`docs/workflows/web-article-kb-import-workflow.md`](../workflows/web-article-kb-import-workflow.md)
> **入口脚本**: `scripts/web_article_to_kb.py`
> **创建时间**: 2026-07-01
> **任务标签**: `v0.3.77-generic-web-article-import-route`

---

## 最短调用

在 WorkBuddy 里直接说：

```text
解读并入库这个网页文章：
<URL>
```

统一入口也可以处理普通网页 URL：

```text
解读并入库这个材料：
<URL>
```

脚本形式：

```bash
python3 scripts/web_article_to_kb.py --url "<URL>" --dry-run
python3 scripts/web_article_to_kb.py --url "<URL>" --import
```

本地 fixture / 已保存文件的安全测试入口：

```bash
python3 scripts/web_article_to_kb.py --html-file "<path>" --dry-run
python3 scripts/web_article_to_kb.py --markdown-file "<path>" --dry-run
python3 scripts/web_article_to_kb.py --text-file "<path>" --dry-run
```

---

## 支持范围

- 普通 `http://` / `https://` 文章页面。
- 公开可访问、不需要登录、不需要 cookie、不需要浏览器会话的正文。
- HTML 中能通过 `article`、`main`、schema.org Article/NewsArticle、OpenGraph/Twitter metadata、常见正文容器或 body fallback 抽取出的文章。
- 中文网页会生成 `source_language: zh-CN`、`translation_language: zh-CN`、`is_translation_mirror: true`。
- 英文网页会生成合法的中文翻译占位草稿，并在文件中标注需要人工复核；不会伪造完整人工翻译。

---

## 不支持与 hard stop

遇到以下情况必须停止，不写半成品 KB 条目：

- 需要登录、付费、cookie、扫码或绕过访问限制。
- robots.txt 明确禁止抓取。
- 页面依赖登录态 JS 才能看到正文。
- 只能抽到标题、摘要或明显截断正文。
- 正文完整性判断失败。
- URL 是微信公众号、YouTube、PDF 或其他已有专门路线的材料。

状态应写为：

- `BLOCKED_FETCH_FAILED`
- `BLOCKED_INCOMPLETE_TEXT`
- `BLOCKED_UNSUPPORTED`

---

## 输出

抓取记录写入：

```text
inbox/raw/web/YYYY-MM-DD-<slug>.json
```

真实入库时写入：

```text
content/articles/YYYY/YYYY-MM-DD-web-<site>-<title>/
├── metadata.yaml
├── source.md
├── translation.zh-CN.md
├── summary.md
├── notes.md
└── raw_payload.json
```

普通网页图片默认不下载；Markdown 会保留可渲染图片链接。需要试验图片本地化时可显式使用 `--localize-images`，但不要影响公众号图片本地化路线。

---

## 去重

入库前按以下顺序检查重复：

1. `source_url`
2. `canonical_url`
3. `title + source_site + published_date`
4. `content_hash`

重复时返回 `SKIPPED_DUPLICATE`，报告中写 `duplicate_of`，不创建新条目。

---

## 质量门禁

真实导入后至少运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

本路线 smoke：

```bash
python3 tests/run_web_article_smoke.py
```
