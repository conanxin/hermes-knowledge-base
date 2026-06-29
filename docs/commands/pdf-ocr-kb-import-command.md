# `pdf-ocr-kb-import` Command

> **Status**: Active since v0.3.62
> **Workflow**: `docs/workflows/pdf-ocr-kb-import-workflow.md`
> **Recipe (MUST load)**: `docs/import-recipes/PDF_OCR_LOCAL.md`
> **Prompt template**: `templates/prompts/import_pdf_ocr_prompt.md`

## Purpose

The single user-facing entry point for importing a **local PDF** into
the Hermes Knowledge Base. The command:

1. Receives an absolute PDF path from the user.
2. Runs OCR if the PDF has no text layer.
3. Translates the full text into Simplified Chinese.
4. Builds a knowledge-base entry with the standard layout.
5. Pushes to the catalog and reports commit hash + live status.

## Shortest call

```
把这个本地 PDF OCR 识别、完整翻译并加入 Hermes 知识库：<PDF_PATH>
```

`<PDF_PATH>` must be an **absolute path** to a PDF file on the user's
machine (e.g. `/home/conanxin/Downloads/some-doc.pdf`).

## Other acceptable phrasings

The command accepts a small set of natural-language variants. The two
required ingredients in every variant are:

1. The PDF is **local** (not a URL).
2. The user explicitly wants the document **imported into the KB**
   (added, archived, integrated) — not just summarized or analyzed.

| Variant | Example |
|---|---|
| 本地 PDF 入库 | `本地 PDF 入库：/home/conanxin/Downloads/foo.pdf` |
| OCR 并翻译入库 | `OCR 并翻译入库：/home/conxin/Downloads/foo.pdf` |
| 把 PDF 文档识别、翻译后加入知识库 | `把 PDF 文档识别、翻译后加入知识库：/path/to/file.pdf` |
| 导入这个本地 PDF | `导入这个本地 PDF：<path>` |
| 把这个 PDF OCR 之后加进 KB | `把这个 PDF OCR 之后加进 KB：<path>` |

## `{{PUSH_MODE}}` variants(同一命令,三种执行模式)

The single command supports three execution modes via a `{{PUSH_MODE}}`
flag. The user can request a variant with explicit phrasing; if the
phrasing does not specify, the default is `commit_and_push`.

### 1. 默认提交(`commit_and_push`)

完整流程:OCR / 翻译 / 入库 / 逐文件 `git add` / `commit` / `push origin main` / live smoke。

```
把这个本地 PDF OCR 识别、完整翻译并加入 Hermes 知识库：<PDF_PATH>
```

等价变体:`本地 PDF 入库:<PDF_PATH>` / `OCR 并翻译入库:<PDF_PATH>` / 任何已有 "入库" / "加入" 关键字的本地 PDF 触发语(详见上表)。

### 2. 只生成本地结果(`local_only`)

只生成本地条目、OCR 报告和检查结果,**不 commit / 不 push / 不 tag**。适用场景:用户想先在本地看完结果再决定是否发布,或当前环境不允许推送到 `origin main`(如离线 / CI 失败恢复期)。

```
本地 PDF OCR 入库但先不要 commit/push：<PDF_PATH>
```

等价变体:

- `本地 PDF 入库(暂不发布):<PDF_PATH>`
- `先本地 OCR 入库,稍后我自己提交:<PDF_PATH>`
- `本地 PDF 入库但不要 push:<PDF_PATH>`

执行结果:`content/articles/.../6 文件` + `reports/pdf_ocr_import_*.md` 全部写好;`check_kb.py` PASS;**`update_site.py` 不跑**;`git status` 列出新增/修改文件;报告 `STATUS: LOCAL_ONLY` 或 `PASS_LOCAL`。

### 3. 只做 dry-run(`dry_run`)

只做 PDF 检测、文本层判断、OCR 可行性分析和导入计划,**不创建 content 条目**。适用场景:用户在提交大文档前先评估工作量,或确认 OCR 质量是否过关。

```
先 dry-run 分析这个 PDF 是否适合 OCR 入库：<PDF_PATH>
```

等价变体:

- `先评估这个 PDF 的 OCR 入库可行性:<PDF_PATH>`
- `dry-run 这个 PDF:<PDF_PATH>`
- `先分析一下这个 PDF 能不能 OCR 入库:<PDF_PATH>`

执行结果:只输出 `reports/pdf_ocr_import_dry_run_<slug>_<YYYYMMDD>.md`(含 PDF 元信息、文本层判定、OCR 方法选择、预计 6 文件路径、预计耗时);**不写 content**;**不跑 OCR 落盘**;**不 commit / push / tag**;报告 `STATUS: PASS_DRY_RUN` 或 `DRY_RUN_PLAN_READY` + 明确 `no content entry created` / `no OCR import committed`。

### 4. 默认值与 hard-stop

- 用户没指定模式 → 默认 `commit_and_push`。
- 用户给的模式不是 `commit_and_push` / `local_only` / `dry_run` 之一 → hard-stop,写 `reports/pdf_ocr_local_import_blocked_<YYYYMMDD>.md`,**不进入 §3 之后的任何步骤**。
- 三个分支的硬约束见 recipe §3.1 与 workflow Phase 0.5:`dry_run` 不得写 content;`local_only` 不得 commit/push;`commit_and_push` 才允许 live smoke。

## When to use

Use this command when:

- The user has a PDF on disk (already downloaded, scanned, or
  generated).
- The user wants the PDF **persisted in the knowledge base**, not
  just summarized in chat.
- The user has supplied an **absolute path** to the file.

## When NOT to use (explicit prohibitions)

| User input | Correct action | Forbidden action |
|---|---|---|
| "分析这个 PDF：`<path>`" (without "入库"/"加入") | Read-only analysis; reply in chat | ❌ Auto-import into KB |
| "总结这个 PDF" | Read-only summary; reply in chat | ❌ Auto-import |
| (no path supplied) | `clarify` to ask for path | ❌ Guess a path |
| URL like "https://example.com/foo.pdf" (remote PDF) | Use URL-import command, not local-PDF command | ❌ Try to download and pretend it's "local" |
| "做成专题页" / "发布成项目页" | Use `projects/` route (different command) | ❌ Mix into KB import |

The fourth row is important: a remote PDF should be downloaded first
(if the user wants it as "local") and then re-submitted with a local
path. Do not conflate "download + import" with "import from a path
that already exists on disk".

## Safety boundaries

- No installation of new system packages. Use only the OCR / PDF
  tools already available locally.
- No modification of `conanxin.github.io/projects/data.json`.
- No standalone project generation.
- No Telegram messages (unless the user is in a Telegram session and
  the report is the natural channel — see workflow doc).
- No restart of `hermes-gateway.service`.
- No modification of Hermes Agent source code.
- The PDF file itself is **not committed** to git (it is gitignored
  via `*.pdf`); a `source.local-ref.txt` keeps the local pointer.

## Output

After a successful import, the user receives:

1. A summary of the OCR result (method, page count, coverage).
2. The path of the new KB entry directory.
3. The list of files generated.
4. The result of each quality gate (`check_kb.py`, `update_site.py`,
   `check_pages_sync.py`, `check_translation_residue.py`).
5. The commit hash.
6. The push status.
7. The live URL or `PENDING_CDN_SYNC` if the CDN has not caught up.
8. Known OCR / translation limitations (every flagged OCR artifact
   and every un-translated residue).

The full report goes to
`reports/pdf_ocr_local_import_recipe_v0.3.N_<YYYYMMDD>.md` (template 3,
9 sections). For blocked imports, the report goes to
`reports/pdf_ocr_local_import_blocked_<YYYYMMDD>.md` (template 1, 3
sections).

## Differences from URL-based article import

| Aspect | URL import (`import_article`) | Local PDF import (`pdf-ocr-kb-import`) |
|---|---|---|
| Source | Remote URL | Local file path |
| Fetch step | `curl` / `web_extract` | `test -f` (no network) |
| Content extraction | HTML / Markdown parse | `pdftotext` (text layer) or `tesseract` (OCR) |
| `source_url` | Real URL | `null` with `source_url_missing: true` |
| `source_site` | URL host (e.g. `gutenberg.org`) | `"local-pdf"` |
| Local pointer | Not needed | `source.local-ref.txt` (always for PDF) |
| Hard-stop cases | Paywall, ACL, network failure | PDF missing, encrypted, OCR failure, multi-page unrecognizable |
| Translation source | The fetched HTML/MD content | The OCR'd `source.md` (with `[OCR疑似: ...]` flags) |

## Hard-stop rules (summary)

The full list is in `docs/import-recipes/PDF_OCR_LOCAL.md` §18. The
top-level rule: **no commit, no push, no catalog update, no Telegram**
until every gate is PASS. A blocked import produces a blocked report;
it does not silently half-finish.

## Output (template)

The final report (模板 3) must include, in addition to the standard
template fields:

```markdown
### 4.5 OCR / PDF specifics
- OCR 方法: tesseract-5.3.4-ocr-250dpi (or pdftotext if text layer present)
- 页数: <N> 页扫描 + 0 页文本层
- 字符级 OCR 噪声: <count> 处,全部以 [OCR疑似: ...] 标记
- 源文件: <absolute path>
- 源文件 sha256: <hash or null>
- 入仓方式: gitignored,本地引用通过 source.local-ref.txt

### 4.6 Translation quality
- source 词数: <N>
- translation CJK 字数: <M>
- 翻译残留: <count> 项,全部为专名/书名/URL(<sample 列表>)
- 是否需要修复: 否(全部 allowlist 内)
```

## Documentation

- Workflow: `docs/workflows/pdf-ocr-kb-import-workflow.md`
- Recipe: `docs/import-recipes/PDF_OCR_LOCAL.md`
- Prompt template: `templates/prompts/import_pdf_ocr_prompt.md`
- AGENT_COMMANDS reference: `docs/AGENT_COMMANDS.md` §本地 PDF OCR 入库流程
