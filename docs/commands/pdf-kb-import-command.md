# pdf-kb-import

> **命令名称**: `pdf-kb-import`
> **用途**: 一键把本地 PDF（可提取文本层）加入 Hermes Knowledge Base
> **Workflow**: [`docs/workflows/pdf-kb-import-workflow.md`](../workflows/pdf-kb-import-workflow.md)
> **入口脚本**: `scripts/pdf_to_kb.py`
> **基线 tag**: `v0.3.86-pdf-local-document-kb-import-route`
> **创建时间**: 2026-07-02
> **版本**: 1.0

---

## 最短调用

在 WorkBuddy 里直接说：

```text
解读并入库这个 PDF：
/path/to/document.pdf
```

脚本形式：

```bash
python3 scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --dry-run
python3 scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --import
python3 scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --allow-partial-text --dry-run
```

统一入口也会自动路由（v0.3.86 起）：

```bash
python3 scripts/material_to_kb.py --input "<file.pdf>" --dry-run
python3 scripts/material_to_kb.py --input "<file.pdf>" --import
```

`--dry-run` 是默认安全模式，不写 KB 条目；只有显式传 `--import` 才会调用真实入库。

---

## v0.3.86 当前支持范围

| PDF 类型 | 当前状态 | 行为 |
|---|---|---|
| 可提取文本层 PDF（text-layer） | 支持 | 提取文本 → 分类 → 校验 → 去重 → 入库 6 文件 |
| 中英文混合 / 纯英文 / 纯中文 | 支持 | 自动识别源语言，写入 `metadata.yaml` |
| 扫描版 / 图像版 PDF（无文本层） | **不支持** | 返回 `BLOCKED_NEEDS_OCR`，不写半成品 |
| 文本层残缺 PDF（avg < `MIN_AVG_CHARS_PER_PAGE`） | 部分支持 | 默认 blocked，加 `--allow-partial-text` 才允许导入 |
| 加密 / 受保护 PDF | 不支持 | 返回 `BLOCKED_NEEDS_OCR` 或 PdfImportError |
| 非 PDF 后缀 | 不支持 | `material_to_kb.py` 返回 `BLOCKED_UNSUPPORTED` |

**当前不在范围内：**

- 不内置 OCR 引擎（Tesseract / PaddleOCR / cloud OCR 都没接）。
- 不伪造扫描版 OCR 文本，不会把空 capture 当 full capture 入库。
- 不下载 PDF（必须是用户已经下载到本地的文件）。
- 不读浏览器 cookie / 登录态 / 任何网络凭据。

如需扫描版 PDF 支持，需要先开 `pdf-ocr-kb-import-route` 任务，把 OCR provider
接进来（参考 `docs/commands/pdf-ocr-kb-import-command.md`，但当前还没有任何稳定 OCR 实现）。

---

## 文本提取与分类

`pdf_to_kb.py` 使用本地 `pymupdf` (PyMuPDF) 提取，不联网。

```python
extract_text_with_metadata(pdf_path)
  -> (pages, raw_meta)        # pages: list[ {page:int, text:str, char_count:int} ]
classify_pdf(pages, raw_meta, allow_partial)
  -> classification {
       page_count, total_chars, cjk_char_count, is_chinese, source_language,
       empty_page_count, avg_chars_per_page,
       text_layer_strategy: 'full' | 'partial' | 'needs_ocr',
       hard_stop:           ''  | 'BLOCKED_NEEDS_OCR' | 'BLOCKED_INCOMPLETE_TEXT',
     }
```

最小阈值（可在 `scripts/pdf_to_kb.py` 顶部调整）：

```python
MIN_TOTAL_CHARS        = 400   # 全文最少字符
MIN_PARAGRAPHS         = 3     # 段落数下限
MIN_CJK_CHARS_FOR_CHINESE_PDF = 100   # 中文 PDF 最少 CJK 字符
MIN_ENGLISH_WORDS      = 80    # 英文 PDF 最少 word 数
MIN_AVG_CHARS_PER_PAGE = 40    # 平均每页字符下限 (触发 partial)
```

扫面判定（`text_layer_strategy == "needs_ocr"`）：

```python
total_chars == 0
  OR (empty_pages / total_pages >= 0.6 AND total_chars < page_count * 10)
```

满足任一条件即 hard-stop，不入库。

---

## 去重键

`pdf_to_kb.py` 在 `--import` 之前会构造一个 dedup 索引，覆盖：

| 键 | 来源 | 命中后行为 |
|---|---|---|
| `by_pdf_sha256` | 文件 SHA-256 | 返回 `SKIPPED_DUPLICATE` + `duplicate_of` |
| `by_source_path` | 已存条目的 `local_source` 绝对路径 | 同上 |
| `by_title_author_pages` | (title, author, page_count) 三元组 | 同上 |
| `by_content_hash` | 抽取文本的 SHA-256（嵌入在 `raw_payload.json`） | 同上（命中已有条目 raw_payload） |

命中任一键即视为重复；不写新条目，但会在 `inbox/raw/pdf/` 留一份 dry-run capture 以便审计。

---

## 输出：6 文件 KB 条目

`--import` 成功后会在 `content/articles/YYYY/<slug>/` 写出：

```text
content/articles/YYYY/YYYY-MM-DD-<slug>/
├── metadata.yaml         # 单一入口；标题/作者/语言/翻译/tags/word_count
├── source.md             # 原文 markdown（页面顺序拼接）
├── translation.zh-CN.md  # 占位翻译（v0.3.86 不内置翻译引擎）
├── summary.md            # 一句话总结 / 核心问题 / 主要观点 / 关键概念（占位）
├── notes.md              # 接受的观点 / 反思的观点 / 可执行行动（占位）
└── raw_payload.json      # pdf_file / pdf_sha256 / page_count / content_markdown / content_hash
```

`docs/items/<slug>/index.html` 和 `site/items/<slug>/index.html` 由 `update_site.py` 生成，
不需要 PDF 脚本自己写 HTML。

---

## 状态值与退出码

`pdf_to_kb.py` 输出大写 `STATUS:` 行（与 `youtube_to_kb.py` / `web_article_to_kb.py` / `wechat_url_to_kb.py` 对齐），方便统一入口 `parse_status_line()` 解析。

| 退出码 | STATUS | 含义 |
|---|---|---|
| 0 | `IMPORTED` | 真实写入 KB 条目 |
| 0 | `DRY_RUN_OK` | dry-run 跑通，capture 写入 `inbox/raw/pdf/` |
| 0 | `SKIPPED_DUPLICATE` | 命中 dedup，未写入新条目 |
| 4 | `BLOCKED_NEEDS_OCR` | 扫描版 / 无文本层，不入库 |
| 4 | `BLOCKED_INCOMPLETE_TEXT` | 文本过少 / 段过少，未通过 `--allow-partial-text` |
| 5 | `FAILED_GATE` | 写入 KB 后 `update_site.py` 失败 |

`material_to_kb.py` 会在自己的 JSON 报告里把这些状态归并到标准 summary 中。

---

## capture JSON

无论 dry-run 还是 import，每次都会写 `inbox/raw/pdf/<slug>-<sha16>.json`：

```json
{
  "schema_version": 1,
  "kind": "pdf_text_layer_capture",
  "pdf_file": "/absolute/path/to/file.pdf",
  "pdf_file_name": "file.pdf",
  "pdf_sha256": "<full hex>",
  "pdf_file_size": 12345,
  "extracted_at": "2026-07-02T06:39:35",
  "extraction_backend": "pymupdf",
  "page_count": 12,
  "total_chars": 8432,
  "source_language": "en",
  "is_chinese": false,
  "cjk_char_count": 12,
  "title": "...",
  "author": "...",
  "subject": "...",
  "pdf_metadata": {
    "producer": "...",
    "creator": "...",
    "creation_date": "...",
    "mod_date": "..."
  },
  "content_markdown": "...joined text...",
  "page_records": [{"page": 1, "char_count": 700}, ...],
  "text_layer_strategy": "full",
  "classification": { ... },
  "dry_run": true
}
```

Blocked 状态另写 `*-BLOCKED_NEEDS_OCR.json` 或 `*-BLOCKED_INCOMPLETE_TEXT.json`，
包含 `extraction_status` 和 `blocked_reason`。

---

## 报告

如果走统一入口，每次运行都会生成两份报告：

```text
reports/material_import_YYYYMMDD_HHMMSS.md
reports/material_import_YYYYMMDD_HHMMSS.json
```

PDF 路线额外字段：

- `inferred_type`: `pdf_file`
- `route`: `pdf_to_kb.py`
- `route_kind`: `pdf`
- `capture_json_path`: `inbox/raw/pdf/...`
- `failure_reason`: 仅在 BLOCKED 时有内容
- `status`: 见上表

---

## 门禁

如果 `--import` 产生了真实 `IMPORTED` 条目，统一入口会运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
python3 scripts/check_pages_sync.py
```

PDF 单独的轻量 smoke（不需要真实 PDF）：

```bash
python3 -m py_compile scripts/pdf_to_kb.py
python3 tests/run_pdf_import_smoke.py   # 26/26 checks
```

---

## 当前范围 vs 暂不支持

**支持：**

- 可提取文本层的 PDF（英文 / 中文 / 中英混合）。
- 中文 PDF 自动 `translation_language: zh-CN` + `is_translation_mirror: true`。
- 英文 PDF 写入 `translation.zh-CN.md` 占位翻译（仍由人工补）。
- 重复检测：内容 hash + path + (title, author, page_count)。
- dry-run 预演 + 真导入 + 状态行解析。

**暂不支持：**

- 扫描版 PDF OCR（Tesseract / PaddleOCR / 云 OCR 都没接）。
- 加密 PDF / 受密码保护的 PDF。
- 嵌入字体不规范的扫描版（pymupdf 也提不到文本，会被识别为 `needs_ocr`）。
- 多列 / 双栏排版的版式还原（直接按页面顺序拼接，跨栏不会重排）。
- PDF 内嵌图片 OCR / 公式识别。

如果用户问"扫描版能不能入库"，统一答案：

> 当前 v0.3.86 只支持可提取文本层 PDF。扫描版会返回 `BLOCKED_NEEDS_OCR`，不会伪造 OCR 文本。请提供可提取文本版的 PDF，或先在本地 OCR 转成 text-layer PDF 再来。

---

## 相关命令 / 工作流

- 统一入口：[`docs/commands/material-kb-import-command.md`](material-kb-import-command.md)
- 工作流：[`docs/workflows/pdf-kb-import-workflow.md`](../workflows/pdf-kb-import-workflow.md)
- 扫描版 PDF（占位）：[`docs/commands/pdf-ocr-kb-import-command.md`](pdf-ocr-kb-import-command.md)