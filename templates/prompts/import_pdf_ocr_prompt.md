# 完整翻译并加入知识库：本地 PDF OCR 流程

> **Status**: Active since v0.3.62
> **Required recipe (MUST load first)**: `docs/import-recipes/PDF_OCR_LOCAL.md`
> **Workflow**: `docs/workflows/pdf-ocr-kb-import-workflow.md`
> **Command**: `docs/commands/pdf-ocr-kb-import-command.md`
> **Inherits**: `templates/prompts/import_article_prompt.md` (KB-vs-project route detection, hard-stop on missing fields)

## Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `{{PDF_PATH}}` | **YES** | — | Absolute path to a local PDF on the user's machine |
| `{{CONTENT_TYPE_HINT}}` | no | `essay` | Hint for `type` field in metadata.yaml (`essay` / `paper` / `book-chapter` / `report`) |
| `{{TITLE_HINT}}` | no | (extract from PDF) | Pre-supplied title; if present, use it; otherwise extract from cover page |
| `{{AUTHOR_HINT}}` | no | (extract from PDF) | Pre-supplied author; if present, use it; otherwise extract from cover / running header |
| `{{PUSH_MODE}}` | no | `commit_and_push` | `commit_and_push` (default) or `dry_run` (write + quality gate only, no commit/push) |

If `{{PDF_PATH}}` is missing, **call `clarify` to ask for the path**.
Do not guess.

## 🚨 硬规则：路由判定（继承自 import_article_prompt.md）

**本节是第一道门,必须在所有其他动作之前读完并应用。**

### 触发语 → 目标仓库映射

| 用户消息包含 | 唯一正确目标 | 绝对禁止 |
|---|---|---|
| "加入知识库" / "入库" / "完整翻译并加入" / "翻译后入库" / "KB" + **本地 PDF** | `~/hermes-knowledge-base/content/articles/...` | ❌ 创建 standalone project、❌ 修改 `~/conanxin.github.io/projects/data.json`、❌ 跳过 OCR 步骤 |
| "做成专题页" / "发布成项目页" | `~/conanxin.github.io/projects/<slug>/` | ❌ 顺手入库 KB(用户没说要入库) |
| 都不包含 | —— | ❌ 默认猜;必须用 `clarify` 工具反问 |

**本地 PDF 路线专属禁项**:

- 用户只说"分析这个 PDF" / "总结这个 PDF" → **read-only**,**不得自动入库**
- 用户未提供 PDF 路径 → **ask/blocked**,**不得猜路径**
- 不得生成 standalone project
- 不得修改 `projects/data.json`
- 不得将远程 URL 假装为"本地"——若 PDF 在网上,先下载到本地再用本流程

## 触发条件

用户说以下任意表达时执行:

- "把这个本地 PDF OCR 识别、完整翻译并加入 Hermes 知识库: `<path>`"
- "本地 PDF 入库: `<path>`"
- "OCR 并翻译入库: `<path>`"
- "把 PDF 文档识别、翻译后加入知识库: `<path>`"
- "把这个 PDF OCR 之后加进 KB: `<path>`"

不触发本流程(明确):

- "分析这个 PDF" / "读一下这个 PDF" / "总结这个 PDF" → read-only
- 用户只给 URL,不给本地路径 → 使用 `import_article_prompt.md` 流程

## 完整执行顺序

### Phase 0 — Preflight (mandatory, blocking)

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
git rev-parse --short HEAD                # 必须 == origin/main
python3 scripts/check_release_tags.py     # 取得 recommended_next_minor
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-pdf-ocr-<slug>
```

Preflight FAIL → 写 `reports/pdf_ocr_local_import_blocked_<YYYYMMDD>.md`,停止。

### Phase 1 — 加载 recipe

**MUST load** `docs/import-recipes/PDF_OCR_LOCAL.md` 整篇。不允许基于记忆/印象做 PDF OCR 流程。

### Phase 2 — PDF 检视

```bash
test -f "{{PDF_PATH}}" || BLOCKED
pdfinfo "{{PDF_PATH}}" | head -25
pdftotext "{{PDF_PATH}}" - | wc -c   # 0 = 扫描
```

### Phase 3 — 文本层检测与 OCR 决策

按 `PDF_OCR_LOCAL.md` §5 表格判定:

- `pdftotext` 字节 ≥ 200/页 → 文本层 PDF,直接用 `pdftotext -layout` 抽取
- `pdftotext` 字节 ≈ 0 → 扫描件,走 OCR fallback

### Phase 4 — OCR (扫描件)

```bash
mkdir -p /tmp/pdf-ocr-pages
pdftoppm -r 250 "{{PDF_PATH}}" /tmp/pdf-ocr-pages/page -png
for p in /tmp/pdf-ocr-pages/page-*.png; do tesseract "$p" "${p%.png}"; done
cat /tmp/pdf-ocr-pages/page-*.txt > /tmp/pdf-ocr-pages/all.txt
```

### Phase 5 — 写条目目录(6 个文件)

按 `PDF_OCR_LOCAL.md` §9-§15 规则写:

1. `metadata.yaml` — `source_url_missing: true` + `source_site: "local-pdf"` + `local_pdf_path: "inbox/raw/pdf/<slug>.pdf"`
2. `source.md` — 完整 OCR 文本,带 `<!-- page: N -->` 标记,所有 OCR 噪声加 `[OCR疑似: ...]` 标注
3. `translation.zh-CN.md` — 完整简体中文翻译
4. `summary.md` — 一句话 + 论点 + 关键金句 + 延伸问题
5. `notes.md` — preflight/duplicate/blocked/OCR 决策 + 相关条目
6. `source.local-ref.txt` — 本地引用(PDF 不入仓)

外加 `reports/pdf_ocr_import_<DATE>-<slug>.md` — OCR 证据报告。

### Phase 6 — 质量门禁(全 PASS 才可继续)

```bash
python3 scripts/check_kb.py                  # 必须 PASS
python3 scripts/update_site.py               # 必须 5/5 PASS
python3 scripts/check_pages_sync.py          # 必须 PASS
python3 scripts/check_translation_residue.py # WARN-only
```

`check_kb.py` 或 `check_pages_sync.py` FAIL → blocked。
`check_translation_residue.py` 报告**真实未翻译段**(非专名/书名/URL)→ 修复或 blocked。

### Phase 7 — 逐文件 git add(必须)

```bash
# 不要用 git add -A 或 git add .
git add content/articles/$DATE/$DATE-$SLUG/metadata.yaml
git add content/articles/$DATE/$DATE-$SLUG/source.md
git add content/articles/$DATE/$DATE-$SLUG/translation.zh-CN.md
git add content/articles/$DATE/$DATE-$SLUG/summary.md
git add content/articles/$DATE/$DATE-$SLUG/notes.md
git add content/articles/$DATE/$DATE-$SLUG/source.local-ref.txt
git add reports/pdf_ocr_import_$DATE-$SLUG.md
git add docs/data/catalog.json site/data/catalog.json
git add index/authors.md index/catalog.jsonl index/tags.md index/timeline.md
git add docs/items/$DATE-$SLUG/index.html
git add site/items/$DATE-$SLUG/index.html

git diff --cached --stat
git diff --cached --name-only
```

如果 `{{PUSH_MODE}} == dry_run`,到此停止,生成 dry-run 报告。

### Phase 8 — Commit + Push

```bash
git -c user.email="<>" -c user.name="<>" commit -m "Add OCR PDF knowledge entry: <title_zh> (zh-CN)"
git push origin main
```

如果 push 被 reject(remote 有新 commit):

1. `git fetch origin`
2. `git reset --hard origin/main` (不用 `git pull --rebase`)
3. 重新生成文件(从对话上下文恢复 OCR 文本)
4. 重新跑 Phase 6 + 7 + 8

### Phase 9 — 报告

按 `docs/REPORTING_TEMPLATE.md` 模板 3 输出。位置:
`reports/pdf_ocr_local_import_recipe_v0.3.N_<YYYYMMDD>.md`

必填字段见 `PDF_OCR_LOCAL.md` §22。

## Hard-stop 规则(本流程专属)

继承 `PDF_OCR_LOCAL.md` §18 全部 hard-stop。本流程额外 hard-stop:

- **未提供 `{{PDF_PATH}}`** → blocked;不要猜路径
- **用户消息不含"入库"/"加入"等词** → blocked;只做 read-only 分析
- **PDF 文件不存在** → blocked;`test -f` 失败
- **OCR 后仍存在不可识别页** → blocked;按 `PDF_OCR_LOCAL.md` §18.3
- **`check_kb.py` / `check_pages_sync.py` FAIL** → blocked;不 commit / 不 push
- **`check_translation_residue.py` 报告真实未翻译段** → blocked;修复或停止

## 报告必填段

```markdown
### 1. STATUS
- 状态: PASS / WARN / FAIL / PENDING_CDN_SYNC
- 任务类型: 写入并发布
- {{PUSH_MODE}}: commit_and_push / dry_run

### 2. SCOPE
- 做了什么: <OCR + 翻译 + 入库 + push 完整列表>
- 没做什么: <明确排除>
- 边界: <本地 PDF 入库,无 standalone project,无 projects/data.json 修改>

### 3. ACTIONS (按阶段)
- 阶段 1: 准备 [READ-ONLY] fetch + pull
- 阶段 2: PDF 检视 [READ-ONLY] pdfinfo + pdftotext
- 阶段 3: OCR [READ-ONLY] tesseract + pdftoppm (or N/A 文本层)
- 阶段 4: 写入 [WRITE] 6 个 entry 文件 + OCR 报告
- 阶段 5: 构建 [GENERATE] update_site.py 5/5
- 阶段 6: 检查 [READ-ONLY] check_kb / check_pages_sync / check_translation_residue
- 阶段 7: 发布 [PUSH] per-file git add + commit + push
- 阶段 8: live 验证 [LIVE] curl home / catalog / detail

### 4. FILES CHANGED
| 路径 | 操作 | Δ |
|---|---|---|
| content/articles/.../metadata.yaml | [WRITE] | +X |
| content/articles/.../source.md | [WRITE] | +X |
| content/articles/.../translation.zh-CN.md | [WRITE] | +X |
| content/articles/.../summary.md | [WRITE] | +X |
| content/articles/.../notes.md | [WRITE] | +X |
| content/articles/.../source.local-ref.txt | [WRITE] | +X |
| reports/pdf_ocr_import_<DATE>-<slug>.md | [WRITE] | +X |
| docs/data/catalog.json | [GENERATE] | +X |
| site/data/catalog.json | [GENERATE] | +X |
| index/{authors,catalog.jsonl,tags,timeline}.md | [GENERATE] | +X |
| docs/items/.../index.html | [GENERATE] | +X |
| site/items/.../index.html | [GENERATE] | +X |

### 4.5 OCR / PDF specifics
- OCR 方法: <tesseract-5.3.4-ocr-250dpi | pdftotext | 其他>
- 页数: <N> 页
- 文本层: 有(<bytes>) / 无(0 字节,OCR fallback)
- 字符级 OCR 噪声: <count> 处,全部 [OCR疑似: ...]
- 源文件: <绝对路径>
- 源文件 sha256: <hash or null>
- 入仓方式: gitignored,本地引用通过 source.local-ref.txt

### 4.6 Translation quality
- source 词数: <N>
- translation CJK 字数: <M>
- 翻译残留: <count> 项(<专名/书名/URL 列表>)
- 是否需要修复: 否(全部 allowlist)

### 5. EVIDENCE
| 引用 | 置信度 | 验证时间 |
|---|---|---|
| commit <hash> | high | <刚才> |
| check_kb.py PASS | high | <刚才> |
| update_site.py 5/5 PASS | high | <刚才> |
| check_pages_sync.py PASS | high | <刚才> |
| check_translation_residue.py <count> WARNING | medium | <刚才> |

### 6. WARNINGS
- (任何 postflight / residue warning)

### 7. COMMIT / PUSH / LIVE
- commit: <hash>
- push: success
- live home: 200
- live catalog: N+1 records / PENDING_CDN_SYNC
- live detail page: 200 / PENDING_CDN_SYNC

### 8. KNOWN LIMITATIONS
- <OCR 噪声 / 翻译残留 / 扫描边界 完整列表>

### 9. NEXT ACTION
- (无 / 提示用户下一步)
```

## 已知良好案例

`content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/`
(commit `bdb1bc8`,v0.3.59 时期) — 4 页扫描 PDF,Le Guin
*The Carrier Bag Theory of Fiction* 完整 + 姊妹篇 *Heroes* 开篇。
OCR 8 处字符级噪声全部以 `[OCR疑似: ...]` 标记。`check_kb.py` 53→54
PASS。`update_site.py` 5/5。`check_pages_sync.py` PASS。
`check_translation_residue.py` WARNING 9 项全部为书名/专名。

## 与其他 prompt 模板的关系

- `import_article_prompt.md` — URL 文章导入。**不适用于**本地 PDF。
- `import_wechat_article_prompt.md` — 微信公众号文章。**不适用于**本地 PDF。
- `youtube_kb_import_prompt.md` — YouTube 视频。**不适用于**本地 PDF。

如果用户消息同时暗示两种来源(例如"这个 PDF 是 YouTube 视频的
转录稿"),按用户的主要意图路由;若意图不明确,`clarify` 反问。
