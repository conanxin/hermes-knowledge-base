# Material KB Import Workflow

> **版本**: 1.5 (`v0.3.84`)
> **创建时间**: 2026-07-01  
> **入口命令**: [`docs/commands/material-kb-import-command.md`](../commands/material-kb-import-command.md)  
> **入口脚本**: `scripts/material_to_kb.py`

---

## 工作流目标

让用户以后可以只说：

```text
解读并入库这个材料：
<公众号链接 / 普通网页链接 / YouTube 链接 / PDF / HTML / Markdown / TXT>
```

或批量：

```text
批量解读并入库这些材料：
<materials.txt>
```

agent 先使用 `scripts/material_to_kb.py` 判断材料类型，再路由到仓库已经存在且稳定的导入能力。没有稳定路线的类型必须返回 `BLOCKED_UNSUPPORTED`，不能临时拼一个半成品抓取器。v0.3.77 起普通网页 URL 路由到 `scripts/web_article_to_kb.py`；v0.3.79 起 YouTube URL 路由到 `scripts/youtube_to_kb.py`。

---

## Step 0: 仓库检查

```bash
git status --short
git branch --show-current
git fetch origin main --tags
python3 scripts/check_task_preflight.py --planned-tag v0.3.79-youtube-transcript-kb-import-route --classify-dirty --json
```

要求：

- 当前分支是 `main`。
- 没有非本任务 tracked dirty 改动。
- 不 `git reset`。
- 不 `git add -A`。
- 不删除未跟踪 artifact。

---

## Step 1: dry-run 路由

单条：

```bash
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --dry-run
```

批量：

```bash
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run
```

检查报告中的：

- `inferred_type`
- `route`
- `status`
- `failure_reason`
- 是否存在 `BLOCKED_UNSUPPORTED`
- 是否有 `BLOCKED_FETCH_FAILED` 或 `BLOCKED_INCOMPLETE_TEXT`

dry-run 不应写入 KB 条目。

---

## Step 2: import

只有 dry-run 结果满足预期时才执行：

```bash
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --import
python3 scripts/material_to_kb.py --input "<YOUTUBE_URL>" --allow-partial-transcript --import
python3 scripts/material_to_kb.py --input "<YOUTUBE_URL>" --allow-auto-captions --import
```

或：

```bash
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --import
```

当前 v0.3.79 的真实导入路线包括：

- 微信公众号 URL
- 微信公众号 HTML / Markdown / TXT
- 普通网页 URL
- YouTube URL（前提是可获取字幕 / transcript）

PDF 如果没有仓库内稳定脚本，必须保留 `BLOCKED_UNSUPPORTED`。YouTube 如果无字幕、字幕过短、需要登录或无法公开获取 transcript，必须返回 `BLOCKED_INCOMPLETE_TEXT` / `BLOCKED_UNSUPPORTED`，不得写半成品条目。

---

## Step 3: YouTube Quality Gate

For YouTube inputs, `material_to_kb.py` delegates to `youtube_to_kb.py` and preserves the
quality gate fields in the material report.

| fetch_quality | Dry-run | Import default | Import with `--allow-partial-transcript` |
|---|---|---|---|
| `full` | allowed | allowed when visible transcript text is at least 800 chars | allowed |
| `partial` | allowed with warning | `BLOCKED_INCOMPLETE_TEXT` | allowed only when visible transcript text is at least 800 chars |
| `metadata_only` | reportable only | `BLOCKED_INCOMPLETE_TEXT` | blocked |
| blocked fetch | blocked | blocked | blocked |

Record these fields in the markdown and JSON report: `fetch_status`, `fetch_quality`,
`fetch_reason`, `transcript_language`, `transcript_kind`, `transcript_char_count`,
`import_allowed`, and `import_block_reason`.

v0.3.82 provider chain:

- direct `captionTracks`: original, `vtt`, `srv3`, `ttml`, `json3`
- subtitle-only `yt-dlp`: `--skip-download`; no video files are downloaded
- optional `youtube-transcript-api`: only when already installed
- metadata-only diagnostics: never importable

Automatic captions require explicit `--allow-auto-captions` for import and must be marked
`transcript_kind: auto` plus `transcript_needs_review: true`. The material JSON report keeps
`provider_attempts` for each YouTube input so failed providers and fallback success are auditable.

### v0.3.83 provider environment (optional install)

`yt-dlp` 和 `youtube-transcript-api` 是 **可选** provider；都不在时 chain 仍降级到 metadata_only。

```bash
python -m pip install --upgrade yt-dlp youtube-transcript-api
# Debian/WSL PEP 668 时：
python -m pip install --user --break-system-packages --upgrade yt-dlp youtube-transcript-api
```

不变量（与 YouTube 命令 / workflow 文档一致）：

- 不下载视频文件，yt-dlp 走 `--skip-download`，只输出 metadata / subtitle
- 不使用 cookie / 登录态 / 伪装绕过
- 只有 `fetch_quality=full` 且 `transcript_char_count >= 800` 才入库；`partial` /
  `metadata_only` / blocked / 空字幕 一律不写 KB 条目
- auto captions 记 `transcript_kind: auto` + `transcript_needs_review: true`，导入需
  `--allow-auto-captions`

### v0.3.84 fetch-result handoff + inbox overwrite protection

`material_to_kb.py` 跑过 in-process YouTube fetch layer 后，若结果是 `full`（或被允许时的
`partial`）会把 capture 序列化到 `tmp/material_fetches/youtube_<video_id>_<timestamp>.json`，
并把 `--fetch-result-json <path>` 传给 YouTube subprocess。subprocess 加载 handoff 后跳过
refetch，从而避免「第一次拿到 full、第二次 429 后退化为 metadata_only」的问题。

只对 `full` / `partial` 写 handoff；`metadata_only` / blocked / 空结果仍让 subprocess refetch
（这样新的 attempt 仍被记录）。handoff 文件 gitignored，不进仓库。

`inbox/raw/youtube/*.json` 也加了 overwrite 保护：

- 质量 rank：`full` (4) > `partial` (3) > `metadata_only` (2) > `blocked` (1) > `none` (0)
- 同一 `video_id` 上遇到更低 rank 的新 capture，subprocess 拒绝覆盖、返回原 capture 路径
- 决策（existing path / quality / overwrite bool / reason）记在 capture 的 `overwrite_decision`
  和 subprocess stderr summary 上

材料报告里 item 新增 `handoff_used: true` 和 `fetch_result_json_path` 两个字段用于审计。

---

## Step 4: 统一报告

每次运行都会写：

```text
reports/material_import_YYYYMMDD_HHMMSS.md
reports/material_import_YYYYMMDD_HHMMSS.json
```

批量导入时，一个 input 失败不能中断整批；最终报告必须保留每条 input 的结果。

---

## Step 5: 门禁

如果本次有真实 `IMPORTED`：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

如果没有真实导入：

```bash
python3 -m py_compile scripts/*.py
python3 tests/run_material_router_smoke.py
```

任务收口或版本提交前仍按完整任务门禁执行。

---

## 当前路由表

| inferred_type | 输入 | 路由 | 状态 |
|---|---|---|---|
| `wechat_url` | `mp.weixin.qq.com` / `weixin.qq.com` | `wechat_url_to_kb.py` 或 `wechat_batch_import.py` | 支持 |
| `local_text_article` | `.html` / `.htm` / `.md` / `.markdown` / `.txt` | `wechat_url_to_kb.py` local file mode 或 batch | 支持 |
| `youtube_url` | `youtube.com` / `youtu.be` | `youtube_to_kb.py` | 支持，有字幕才入库 |
| `generic_web_url` | 其他 HTTP(S) URL | `web_article_to_kb.py` | 支持 |
| `pdf_file` | 本地 `.pdf` | 未接入稳定脚本 | `BLOCKED_UNSUPPORTED` |

---

## 停止条件

- 仓库存在明显无关 tracked dirty 改动。
- 下游 WeChat 脚本判断正文不完整。
- `check_kb.py` 或 `check_pages_sync.py` 失败。
- 用户要求的材料类型尚未实现稳定导入路线。
- 需要登录、扫码、cookie 或绕过访问限制才能获取正文。
- 普通网页正文不完整、明显截断或 robots.txt 禁止抓取。

发生停止时，状态应写为 `BLOCKED_*` 或 `FAILED_*`，并在报告中保留原因。
