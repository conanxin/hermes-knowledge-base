# material-kb-import

> **命令名称**: `material-kb-import`  
> **用途**: 给一个 URL 或本地文件，由统一入口判断材料类型，并路由到仓库已有的稳定入库脚本。  
> **Workflow**: [`docs/workflows/material-kb-import-workflow.md`](../workflows/material-kb-import-workflow.md)  
> **入口脚本**: `scripts/material_to_kb.py`  
> **创建时间**: 2026-07-01  
> **任务标签**: `v0.3.76-unified-material-kb-import-router`; `v0.3.77-generic-web-article-import-route`; `v0.3.79-youtube-transcript-kb-import-route`; `v0.3.86-pdf-local-document-kb-import-route`

---

## 最短调用

在 WorkBuddy 里直接说：

```text
解读并入库这个材料：
<URL 或 本地文件>
```

批量：

```text
批量解读并入库这些材料：
<materials.txt>
```

脚本形式：

```bash
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --dry-run
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --import
python3 scripts/material_to_kb.py --input "<YOUTUBE_URL>" --allow-partial-transcript --import
python3 scripts/material_to_kb.py --input "<YOUTUBE_URL>" --allow-auto-captions --import
python3 scripts/material_to_kb.py --input "<YOUTUBE_URL>" --caption-provider yt-dlp --dry-run
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --import
```

`--dry-run` 是默认安全模式，不写 KB 条目。只有显式传 `--import` 才会调用下游脚本真实入库。

## v0.3.83 YouTube provider environment

YouTube 相关 fallback (`yt-dlp` + `youtube-transcript-api`) 是 **可选** provider，环境缺失时
链照样能跑 (降级为 metadata_only)。要启用时：

```bash
python -m pip install --upgrade yt-dlp youtube-transcript-api
# Debian/WSL PEP 668 时：
python -m pip install --user --break-system-packages --upgrade yt-dlp youtube-transcript-api
```

保证：

- 不下载视频文件 (yt-dlp 仅 `--skip-download`，只取 metadata / subtitle)
- 不使用 cookie / 登录态 / 伪装绕过
- 只有 `fetch_quality=full` 且 `transcript_char_count >= 800` 才入库；`partial` / `metadata_only` / blocked 不写条目
- auto captions 标记 `transcript_kind: auto` + `transcript_needs_review: true`，导入需 `--allow-auto-captions`

详见 `docs/commands/youtube-kb-import-command.md` 与 `docs/workflows/youtube-video-kb-import-workflow.md`。

---

## input-list 格式

每行一个 URL 或本地文件路径：

```text
# comments are skipped
https://mp.weixin.qq.com/s/...
saved-wechat-article.html
notes/article.md

# blank lines are skipped
```

空行和 `#` 开头的行会跳过。

---

## 当前支持状态

| 材料类型 | 匹配规则 | 当前状态 | 路由 |
|---|---|---|---|
| 微信公众号 URL | `mp.weixin.qq.com`, `weixin.qq.com` | 支持 | 单输入走 `scripts/wechat_url_to_kb.py`，多输入走 `scripts/wechat_batch_import.py` |
| 微信公众号 HTML / MD / TXT | `.html`, `.htm`, `.md`, `.markdown`, `.txt` | 支持 | `wechat_url_to_kb.py` local file mode；批量走 `wechat_batch_import.py` |
| YouTube URL | `youtube.com`, `youtu.be` | 支持，前提是能获取字幕 / transcript | `scripts/youtube_to_kb.py` |
| 普通网页 URL | 其他 `http://` / `https://` | 支持 | `scripts/web_article_to_kb.py` |
| 本地 PDF（可提取文本层） | `.pdf` 后缀 | 支持（v0.3.86 起） | `scripts/pdf_to_kb.py` |
| 本地 PDF（扫描版 / 无文本层） | `.pdf` 后缀但 pymupdf 提不到文本 | 阻塞返回 `BLOCKED_NEEDS_OCR` | `scripts/pdf_to_kb.py` 写入失败 capture，不入库 |
| 其他未知后缀 | — | `BLOCKED_UNSUPPORTED` | 不引入临时抓取器 |

统一入口不会临时发明抓取器。没有稳定脚本的类型必须明确返回 `BLOCKED_UNSUPPORTED`，并写入失败原因。v0.3.77 起普通网页 URL 已接入公开 HTTP 抓取路线；v0.3.79 起 YouTube URL 已接入字幕/转录稿路线；v0.3.86 起本地可提取文本 PDF 接入 `pdf_to_kb.py`。三条路线都不登录、不读 cookie、不绕过 paywall 或访问限制，不完整正文/字幕/扫描版 PDF 会 hard stop。

---

## YouTube Quality Gate

v0.3.81 adds an import quality gate for `youtube_to_kb.py` and the unified material router.

- `fetch_quality=full`: dry-run and import are allowed when visible transcript text is at least 800 chars.
- `fetch_quality=partial`: dry-run is allowed with a warning; import is blocked unless `--allow-partial-transcript` is explicitly set and the transcript still passes the minimum length gate.
- `fetch_quality=metadata_only`: dry-run may report metadata, but import is always `BLOCKED_INCOMPLETE_TEXT`.
- blocked fetches, empty captions, no transcript body, login/cookie/paywall/private access, and text below the threshold never write KB entries.
- Material reports include `fetch_status`, `fetch_quality`, `fetch_reason`, `transcript_language`, `transcript_kind`, `transcript_char_count`, `import_allowed`, and `import_block_reason`.

v0.3.82 adds automatic transcript providers before the metadata-only fallback:

1. direct `captionTracks`: try original URL, `fmt=vtt`, `fmt=srv3`, `fmt=ttml`, and `fmt=json3`
2. subtitle-only `yt-dlp`: `--skip-download`, write subtitles only, never video files
3. optional `youtube-transcript-api`: used only when already installed
4. metadata diagnostics: report-only, never importable

Automatic captions can be `fetch_quality=full`, but import requires explicit
`--allow-auto-captions`; generated entries record `transcript_kind: auto` and
`transcript_needs_review: true`. Material JSON reports include `provider_attempts`
for every YouTube input.

v0.3.84 adds a fetch-result handoff to the YouTube subprocess:

- `material_to_kb.py` runs the in-process fetch layer first. When the fetch is `full` (or
  `partial` when allowed) the router serializes the capture to
  `tmp/material_fetches/youtube_<video_id>_<timestamp>.json` and passes
  `--fetch-result-json <path>` to the YouTube subprocess. The subprocess loads the handoff
  and skips refetch, which prevents 429 throttling turning a real full transcript into
  `metadata_only` on the second call.
- A handoff is **only** written for `full` / `partial` results; `metadata_only`, `blocked`,
  or empty results still cause the subprocess to refetch so a fresh attempt is logged.
- Material items gain `handoff_used: true` and `fetch_result_json_path` when the handoff is
  used. The handoff file is gitignored under `tmp/material_fetches/`.

## v0.3.86 本地 PDF 路线

新增 `scripts/pdf_to_kb.py`，统一入口会把 `.pdf` 路由进去：

```bash
python3 scripts/material_to_kb.py --input "<file.pdf>" --dry-run
python3 scripts/material_to_kb.py --input "<file.pdf>" --import
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --import
```

也可以直接调子脚本：

```bash
python3 scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --dry-run
python3 scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --import
```

提取后端：**PyMuPDF (pymupdf)**，完全本地，不联网。

| PDF 类型 | 行为 |
|---|---|
| 可提取文本层 PDF | `DRY_RUN_OK` 或 `IMPORTED` |
| 扫描版 / 图像版 PDF | `BLOCKED_NEEDS_OCR` (exit 4)，不写半成品 |
| 文本层残缺 | `BLOCKED_INCOMPLETE_TEXT`，可加 `--allow-partial-text` 放宽 |
| 重复 PDF (sha256 / path / (title, author, page_count) 命中已有条目) | `SKIPPED_DUPLICATE` |

入库产出 6 文件：`content/articles/YYYY/<slug>/{metadata.yaml, source.md, translation.zh-CN.md, summary.md, notes.md, raw_payload.json}`。docs / site HTML 由统一入口的 `update_site.py` 增量生成。

- **不内置 OCR**：扫描版永远不会被当作 full capture 入库。
- **不伪造文本**：`--allow-partial-text` 也只是把硬阈值放宽，仍然是基于真实提取的文本。
- **不下载 PDF**：必须用户已经在本地。
- **不读 cookie / 登录态**：纯本地库调用。

详见 [`docs/commands/pdf-kb-import-command.md`](pdf-kb-import-command.md) 与 [`docs/workflows/pdf-kb-import-workflow.md`](../workflows/pdf-kb-import-workflow.md)。

v0.3.84 also adds inbox overwrite protection for `inbox/raw/youtube/*.json`:

- Quality rank: `full` (4) > `partial` (3) > `metadata_only` (2) > `blocked` (1) > `none` (0).
- A weaker capture (lower rank) for an existing `video_id` is refused; the existing capture
  path is returned instead, with `overwrite: false` recorded on the subprocess stderr summary.

---

## 报告

每次运行都会生成两份报告：

```text
reports/material_import_YYYYMMDD_HHMMSS.md
reports/material_import_YYYYMMDD_HHMMSS.json
```

每条 input 记录：

- `input`
- `inferred_type`
- `route`
- `status`
- `title`
- `source_url`
- `kb_article_path`
- `docs_item_path`
- `site_item_path`
- `capture_json_path`
- `route_report_path`
- `failure_reason`
- `fetch_status`
- `fetch_quality`
- `fetch_reason`
- `transcript_language`
- `transcript_kind`
- `transcript_char_count`
- `import_allowed`
- `import_block_reason`
- `provider_attempts`

状态值包括：

- `IMPORTED`
- `DRY_RUN_OK`
- `SKIPPED_DUPLICATE`
- `BLOCKED_UNSUPPORTED`
- `BLOCKED_FETCH_FAILED`
- `BLOCKED_INCOMPLETE_TEXT`
- `FAILED_IMPORT`
- `FAILED_GATE`

---

## 门禁

如果 `--import` 产生了真实 `IMPORTED` 条目，统一入口会运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

如果没有真实导入，任务收口只需要轻量检查：

```bash
python3 -m py_compile scripts/*.py
python3 tests/run_material_router_smoke.py
```

---

## 边界

- 不重新实现公众号导入，只复用现有 `wechat_url_to_kb.py` / `wechat_batch_import.py`。
- 不绕过公众号访问限制，不登录、不扫码、不读 cookie。
- 不伪造 PDF 导入能力；YouTube 只有在能获取可用字幕 / transcript 时才入库。
- 普通网页路线只处理公开可访问正文；需要登录、cookie、付费墙或 JS 登录态的页面返回 `BLOCKED_*`。
- 不覆盖已有 `summary.md` / `notes.md`。
- 不删除 KB 条目、item pages 或 assets。
