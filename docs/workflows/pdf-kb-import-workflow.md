# PDF KB Import Workflow

> **版本**: 1.0 (`v0.3.86`)
> **创建时间**: 2026-07-02
> **入口命令**: [`docs/commands/pdf-kb-import-command.md`](../commands/pdf-kb-import-command.md)
> **入口脚本**: `scripts/pdf_to_kb.py`
> **统一入口**: `scripts/material_to_kb.py`（v0.3.86 起自动路由 `.pdf`）

---

## 工作流目标

让用户以后可以只说：

```text
解读并入库这个 PDF：
/path/to/document.pdf
```

或批量：

```text
批量解读并入库这些材料：
<materials.txt>
```

agent 先用 `material_to_kb.py` 判断类型 → 路由到 `pdf_to_kb.py` → 本地 pymupdf 提取 → 校验
→ 去重 → 入库 6 文件 / `update_site.py` 生成 docs & site HTML。

**当前范围**：仅"可提取文本层 PDF"。扫描版会被识别为 `BLOCKED_NEEDS_OCR` 并 hard-stop，
绝不写入半成品 KB 条目。

---

## Step 0: 仓库检查

```bash
git status --short
git status -sb
git branch --show-current
git fetch origin main --tags
git log --oneline -5
python3 scripts/check_task_preflight.py --planned-tag v0.3.86-pdf-local-document-kb-import-route --classify-dirty --json
```

要求：

- 当前分支是 `main`。
- 没有非本任务 tracked dirty 改动（untracked 是允许的：inbox/raw/pdf/、tmp/、reports/）。
- 不 `git reset`。
- 不 `git add -A`。
- 不删除未跟踪 artifact。
- 不提交 `tmp/`、`.venv/`、`inbox/raw/pdf/*.json` 临时 capture、`reports/material_import_*.json`。
- 不覆盖已有 summary.md / notes.md。
- 不删除 KB 条目或 item pages。

依赖：

```bash
python3 -c "import fitz; print(fitz.__doc__.splitlines()[0])"   # PyMuPDF 1.27+
```

如果没有：

```bash
python3 -m pip install --user --break-system-packages --upgrade pymupdf
# 或
pip install --user pymupdf
```

---

## Step 1: dry-run 路由

单条：

```bash
python3 scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --dry-run
```

通过统一入口：

```bash
python3 scripts/material_to_kb.py --input "<file.pdf>" --dry-run
```

批量：

```bash
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run
```

期望输出（text-layer PDF）：

```text
[pdf] pdf=/path/to/file.pdf pages=12 chars=8432 strategy=full
[pdf] page_count: 12 chars: 8432 strategy: full
[pdf] capture_json_path: inbox/raw/pdf/2026-07-02-<slug>-<sha16>.json
[pdf] status: DRY_RUN_OK
STATUS: DRY_RUN_OK
```

期望输出（扫描版）：

```text
[pdf] pdf=/path/to/scanned.pdf pages=8 chars=0 strategy=needs_ocr
[pdf] status=BLOCKED_NEEDS_OCR reason=PDF appears to be scanned: total_chars=0, empty_page_count=8/8. Use the pdf-ocr-kb-import workflow instead.
[pdf] capture_json_path: inbox/raw/pdf/2026-07-02-scanned-<sha16>-BLOCKED_NEEDS_OCR.json
[pdf] status: BLOCKED_NEEDS_OCR
STATUS: BLOCKED_NEEDS_OCR
exit code: 4
```

期望输出（重复）：

```text
[pdf] status=SKIPPED_DUPLICATE duplicate_of=content/articles/2026/2026-07-02-<slug>
[pdf] capture_json_path: inbox/raw/pdf/...
[pdf] duplicate_of: content/articles/2026/2026-07-02-<slug>
[pdf] status: SKIPPED_DUPLICATE
STATUS: SKIPPED_DUPLICATE
```

---

## Step 2: 解读 dry-run capture

打开 `inbox/raw/pdf/<slug>-<sha16>.json`，人工核对：

- `page_count` / `total_chars` 是否与 PDF 元信息吻合。
- `title` / `author` 是否合理（取自 PDF metadata，不存在则用 stem）。
- `text_layer_strategy` 必须是 `full` 或 `partial`；`needs_ocr` 直接停止。
- `classification.empty_page_count` / `avg_chars_per_page` 是否异常。
- `content_markdown` 抽样几页是否完整可读。

不通过的话：

- text-layer 但被识别为 scanned → 检查 PDF 是否用非常规字体嵌入文本。
- `partial` 触发 → 加 `--allow-partial-text` 重跑 dry-run；或人工决策是否放弃。

---

## Step 3: 真导入

```bash
python3 scripts/pdf_to_kb.py --pdf-file "<file.pdf>" --import
# 或
python3 scripts/material_to_kb.py --input "<file.pdf>" --import
```

成功后：

```text
[pdf] capture_json_path: inbox/raw/pdf/...
[pdf] kb_article_path: content/articles/2026/2026-07-02-<slug>
[pdf] docs_item_path: docs/items/2026-07-02-<slug>/index.html
[pdf] site_item_path: site/items/2026-07-02-<slug>/index.html
[pdf] status: IMPORTED
STATUS: IMPORTED
```

6 文件落地：

```text
content/articles/2026/2026-07-02-<slug>/
├── metadata.yaml
├── source.md
├── translation.zh-CN.md     # 占位翻译
├── summary.md               # 占位
├── notes.md                 # 占位
└── raw_payload.json         # 包含 content_hash 供下次去重
```

---

## Step 4: 门禁

```bash
python3 -m py_compile scripts/*.py
python3 tests/run_smoke_tests.py
python3 tests/run_wechat_batch_smoke.py
python3 tests/run_item_render_smoke.py
python3 tests/run_image_localization_smoke.py
python3 tests/run_material_router_smoke.py     # v0.3.86: PDF 路线已加入并更新断言
python3 tests/run_web_article_smoke.py
python3 tests/run_youtube_import_smoke.py
python3 tests/run_fetch_layer_smoke.py
python3 tests/run_pdf_import_smoke.py          # v0.3.86 新增: 26/26 checks
python3 scripts/check_kb.py
python3 scripts/check_pages_sync.py
```

若 import 走统一入口，路由器会再自动跑：

```bash
python3 scripts/localize_article_images.py
python3 scripts/update_site.py
python3 scripts/audit_kb_state.py
```

---

## Step 5: 真实 PDF 回归（Stage I）

```bash
# 优先查找：
find tmp/ -maxdepth 4 -name "*.pdf"
find ~/Downloads/ -maxdepth 4 -name "*.pdf"
find /mnt/d/Downloads/ -maxdepth 4 -name "*.pdf"
find /mnt/d/Codex/hermes-knowledge-base/tmp/ -maxdepth 4 -name "*.pdf"
```

要求：

- 只导入 1 个真实 PDF。
- 必须是可提取文本 PDF。
- 如果没有真实 PDF，**不要伪造真实导入**，只跑 fixture smoke，并在报告里说明
  "需要用户提供 PDF"。
- 如果 PDF 是扫描版，`BLOCKED_NEEDS_OCR`，不写半成品。

当前 v0.3.86 的真实回归状态：**BLOCKED_NEEDS_REAL_PDF**（仓库里没有合适的真实 PDF）。
fixture smoke (`tests/run_pdf_import_smoke.py`) 已经覆盖 dry-run / extraction /
scanned / 6-file / dedup / router 五个端到端分支。

---

## Step 6: 报告与提交

```bash
git status --short
git add scripts/pdf_to_kb.py \
        scripts/material_to_kb.py \
        tests/run_pdf_import_smoke.py \
        tests/run_material_router_smoke.py \
        tests/fixtures/generate_sample_pdf.py \
        tests/fixtures/pdf_sample_document.pdf \
        tests/fixtures/pdf_scanned_fixture.pdf \
        tests/fixtures/material_router_sample.pdf \
        docs/commands/pdf-kb-import-command.md \
        docs/workflows/pdf-kb-import-workflow.md \
        docs/commands/material-kb-import-command.md \
        docs/workflows/material-kb-import-workflow.md \
        docs/AGENT_COMMANDS.md \
        README.md
git commit -m "..."
git push origin main
```

不 commit：

- `inbox/raw/pdf/*.json`（capture 临时文件）。
- `reports/material_import_*.{md,json}`（运行时报告）。
- `tmp/material_fetches/`（gitignored）。
- 工作树其他 dirty 改动（避免污染 commit）。

报告路径：

```text
reports/pdf_kb_import_v0.3.86_<timestamp>.md
```

---

## 常见场景

### 扫描版 PDF（hard-stop）

```text
[pdf] strategy=needs_ocr
[pdf] status: BLOCKED_NEEDS_OCR
exit code: 4
```

**不要重试**：v0.3.86 没有 OCR。回答用户：

> 当前 v0.3.86 不支持扫描版 OCR。如需入库，请先在本地 OCR（OCRmyPDF / Adobe / Apple Preview）
> 转成可提取文本层的 PDF，再走 `pdf_to_kb.py`。

### 文本层残缺

```text
[pdf] status=BLOCKED_INCOMPLETE_TEXT reason=too few CJK chars (87 < 100)
```

用户可选：

- 重跑带 `--allow-partial-text`，但 `partial` 状态的条目仍可能不完整。
- 拒绝入库：保留 capture 文件作审计，告知用户。

### 重复 PDF

```text
[pdf] status=SKIPPED_DUPLICATE
[pdf] duplicate_of: content/articles/2026/2026-07-02-<slug>
```

不要再次入库；capture 文件 `inbox/raw/pdf/...-<sha16>.json` 仍会写入以便审计。

### 嵌入式 PDF 字体（pymupdf 提不到文本）

```text
[pdf] strategy=needs_ocr
total_chars=0
```

视觉上是文本 PDF，但 pymupdf 提取为空：通常是因为 PDF 用图片形式嵌入了字体。
当前 v0.3.86 也会 hard-stop，归类为扫描版。建议先在本地 OCR 转可文本层。

---

## v0.3.86 决策记录

1. **不接 OCR**：v0.3.86 范围只到 text-layer PDF，避免时间被 OCR provider 选择
   （Tesseract / PaddleOCR / 云 OCR / 自训）拖垮。
2. **不接翻译**：和 wechat / web / youtube 路线一致，`translation.zh-CN.md` 仅占位，
   由人工 / 下游翻译管线补。
3. **dedup 三键**：sha256 + path + (title, author, page_count)。content_hash 作为第四键
   存在 `raw_payload.json` 内，未来可扩展。
4. **`STATUS:` 大写输出**：和 youtube / web / wechat 子脚本保持一致，方便统一入口解析。
5. **Router 路径**：v0.3.86 直接把 `.pdf` 路由到 `pdf_to_kb.py`，跳过 fetch 层（PDF 不是 URL）。

---

## 相关命令 / 工作流

- 统一入口：[`docs/commands/material-kb-import-command.md`](../commands/material-kb-import-command.md)
- 统一入口 workflow：[`docs/workflows/material-kb-import-workflow.md`](material-kb-import-workflow.md)
- 扫描版 PDF（占位，未实现）：[`docs/commands/pdf-ocr-kb-import-command.md`](../commands/pdf-ocr-kb-import-command.md)
- README / Agent 索引：[`docs/AGENT_COMMANDS.md`](../AGENT_COMMANDS.md)