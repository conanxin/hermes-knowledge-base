# Web Article KB Import Workflow

> **版本**: 1.0 (`v0.3.77`)
> **创建时间**: 2026-07-01
> **入口命令**: [`docs/commands/web-article-kb-import-command.md`](../commands/web-article-kb-import-command.md)
> **入口脚本**: `scripts/web_article_to_kb.py`

---

## 工作流目标

让用户可以说：

```text
解读并入库这个网页文章：
<URL>
```

或通过统一入口：

```text
解读并入库这个材料：
<URL>
```

脚本负责公开 HTTP 抓取、正文抽取、完整性判断、去重、生成标准 article 六文件，并让 `scripts/material_to_kb.py` 能把普通网页 URL 路由到该路线。

---

## Step 0: 仓库检查

```bash
git status --short
git branch --show-current
git fetch origin main --tags
python3 scripts/check_task_preflight.py --planned-tag v0.3.77-generic-web-article-import-route --classify-dirty --json
```

要求：

- 当前分支是 `main`。
- 没有明显无关 tracked dirty 改动。
- 不 `git reset`。
- 不 `git add -A`。
- 不删除未跟踪 artifact。

---

## Step 1: dry-run 抓取与抽取

```bash
python3 scripts/web_article_to_kb.py --url "<URL>" --dry-run
```

本地 fixture / 已保存文件：

```bash
python3 scripts/web_article_to_kb.py --html-file "<path>" --dry-run
python3 scripts/web_article_to_kb.py --markdown-file "<path>" --dry-run
python3 scripts/web_article_to_kb.py --text-file "<path>" --dry-run
```

dry-run 可以写 capture JSON 到 `inbox/raw/web/`，但不写 `content/articles/` 条目。

---

## Step 2: 正文抽取优先级

抽取顺序：

1. `article`
2. `main`
3. schema.org `Article` / `NewsArticle` JSON-LD
4. OpenGraph / Twitter metadata
5. 常见正文容器，如 `articleBody`、`post-content`、`entry-content`
6. body 可见文本 fallback

如果 fallback 后仍无法确认正文完整，必须 hard stop。

---

## Step 3: import

只有 dry-run 结果满足预期时才执行：

```bash
python3 scripts/web_article_to_kb.py --url "<URL>" --import
```

导入结果固定是 `type: article`、`content_kind: web_article`、`source_platform: web`，写入 `content/articles/YYYY/<slug>/`，不创建 project。

---

## Step 4: 统一入口路由

`scripts/material_to_kb.py` 的普通 HTTP(S) URL 路由表：

| inferred_type | 输入 | 路由 | 状态 |
|---|---|---|---|
| `generic_web_url` | 非 WeChat、非 YouTube 的 HTTP(S) URL | `web_article_to_kb.py` | 支持 |

批量 input-list 中，一个普通网页失败不能中断整批；YouTube URL 走 `youtube_to_kb.py` 专门路线，PDF 仍保持 `BLOCKED_UNSUPPORTED`。

---

## Step 5: 去重策略

真实导入前按四层去重：

1. `source_url`
2. `canonical_url`
3. `title + source_site + published_date`
4. `content_hash`

重复时返回 `SKIPPED_DUPLICATE`，报告中记录 `duplicate_of`，不写新条目。

---

## Step 6: 图片策略

普通网页图片的 v0.3.77 最小支持是：Markdown 中图片能渲染。默认不下载普通网页图片。

可选参数：

```bash
python3 scripts/web_article_to_kb.py --url "<URL>" --import --localize-images
python3 scripts/web_article_to_kb.py --url "<URL>" --import --no-localize-images
```

公众号图片本地化仍由 `scripts/localize_article_images.py` 和 WeChat 路线负责，普通网页路线不得改变公众号行为。

---

## Step 7: 门禁

真实导入后运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

版本任务收口还应运行：

```bash
python3 -m py_compile scripts/*.py
python3 tests/run_web_article_smoke.py
python3 tests/run_material_router_smoke.py
```

---

## 停止条件

- 需要登录、cookie、扫码、付费或绕过访问限制。
- robots.txt 禁止抓取。
- 公开 HTTP 抓取失败。
- 正文缺失、过短、截断或只有摘要。
- 无法确认标题和正文对应。
- 触发重复检查。
- `check_kb.py` 或 `check_pages_sync.py` 失败。

发生停止时，状态写为 `BLOCKED_*`、`SKIPPED_DUPLICATE` 或 `FAILED_*`，并在报告中保留原因。
