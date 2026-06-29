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
| `{{PUSH_MODE}}` | no | `commit_and_push` | 见下方 `{{PUSH_MODE}} 分支` 一节。允许值: `commit_and_push` (默认) / `local_only` (本地落盘不提交) / `dry_run` (可行性分析,不写 content)。空值等同 `commit_and_push`;任何其他值 → **hard-stop**,不猜测 |

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

## {{PUSH_MODE}} 分支(必读,在 Phase 0 之前判定)

**第一动作**:解析 `{{PUSH_MODE}}` 的值,然后在 Phase 0 之前决定本次执行的分支。空值 → `commit_and_push`(默认)。任何非下列三个值之一 → **hard-stop,不得猜测**。

| 分支 | 是否创建 content 条目 | 是否修改 site/docs/catalog/index | 是否 commit | 是否 push | 是否 tag | 报告必填 |
|---|---|---|---|---|---|---|
| `commit_and_push` (默认) | 是 | 是 | 是(逐文件 `git add`) | 是(`origin main`) | 是 | commit hash / push status / live URL 或 `PENDING_CDN_SYNC` |
| `local_only` | 是 | 否 | **否** | **否** | **否** | `STATUS: LOCAL_ONLY` 或 `PASS_LOCAL` + `git status` 列出新增/修改 |
| `dry_run` | **否** | **否** | **否** | **否** | **否** | 明确 `no content entry created` / `no OCR import committed` |

### `commit_and_push`(默认模式)

完整流程,无任何省略:

1. Phase 0 → 6:全部执行(包含 OCR、6 文件条目、`update_site.py` 重建、三个质量门禁)
2. Phase 7:逐文件 `git add`(不使用 `git add -A` / `git add .`)
3. Phase 8:`commit` + `push origin main`
4. live smoke:curl home / catalog / detail
5. 报告:commit hash / push status / live URL(若 CDN 尚未同步则写 `PENDING_CDN_SYNC`)

### `local_only`(本地落盘但不发布)

只生成本地条目、OCR 报告和检查结果,**不 commit / 不 push / 不 tag**。

允许的动作:

- Phase 0:fetch + pull(允许)
- Phase 2 — 5:PDF 检视、OCR 决策、OCR 落盘、6 文件 entry 写入
- Phase 6:`check_kb.py` 必须 PASS;`update_site.py` 不允许运行(`local_only` 明确不改 site)
- `git status` 必须列出新增/修改文件(不 `git add`)

不允许的动作:

- ❌ 任何 `git add` / `git commit` / `git push` / `git tag`
- ❌ `python3 scripts/update_site.py`
- ❌ 修改 `docs/data/catalog.json` / `site/data/catalog.json` / `index/*.md` / `docs/items/...` / `site/items/...`
- ❌ live smoke

报告必填:`STATUS: LOCAL_ONLY` 或 `PASS_LOCAL`;`ACTIONS` 段明确每个阶段的 `[WRITE-LOCAL]` 标签;`FILES CHANGED` 段标 `[WRITE]` 但 `commit/push` 字段写 `N/A (local_only)`;附 `git status` 完整输出。

### `dry_run`(可行性分析,不写 content)

只做 PDF 检测、文本层判断、OCR 可行性分析和导入计划。

允许的动作(全部 `[READ-ONLY]`):

- Phase 0:fetch + pull + 取得 `recommended_next_minor`(留作参考,不打 tag)
- Phase 2:PDF 检视(`pdfinfo` / `pdftotext` 字节统计)
- Phase 3:文本层检测 + OCR 决策(选 tesseract 还是 pdftotext)
- 输出 `reports/pdf_ocr_import_dry_run_<slug>_<YYYYMMDD>.md`:
  - PDF 基础信息(页数、文件大小、是否扫描件)
  - 文本层判定与 OCR 方法选择
  - 预计 OCR 耗时(基于页数 × 单页估算)
  - 预计 content 条目结构(类型、slug、6 文件清单)
  - 预计 6 个文件大致路径(`content/articles/<DATE>/<DATE>-<slug>/...`)
  - 质量门禁预期(check_kb / check_pages_sync / check_translation_residue 各自预估)
  - 完整翻译字数估算(基于中文字符密度)
  - `commit_and_push` 模式下的预计 `git add` 列表

不允许的动作:

- ❌ 创建任何正式 `content/articles/...` 条目
- ❌ 任何 OCR 实际执行(不跑 tesseract / pdftoppm / pdftotext 落盘)
- ❌ 修改 `site/` / `docs/` / `catalog.json` / `index/`
- ❌ `git add` / `git commit` / `git push` / `git tag`

报告必填:`STATUS: PASS_DRY_RUN` 或 `DRY_RUN_PLAN_READY`;明确写 `no content entry created` / `no OCR import committed`;`ACTIONS` 段全部标 `[READ-ONLY]`;不附 `FILES CHANGED` 段(改附 `PLANNED FILES` 段,只列计划路径)。

### 分支校验

在 Phase 0 末尾必须输出:

```text
PUSH_MODE resolved: <commit_and_push|local_only|dry_run>
(若为 dry_run / local_only:停止线 = <对应阶段>,跳过 commit/push/tag)
```

如果 `{{PUSH_MODE}}` 不属于 `commit_and_push` / `local_only` / `dry_run` 之一(含拼写错误、大小写不一致、缩写)→ 写 `reports/pdf_ocr_local_import_blocked_<YYYYMMDD>.md`,**hard-stop,不进入 Phase 0**。

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

**Phase 0 收尾**:输出 `PUSH_MODE resolved: <branch>`。若分支为 `local_only` 或 `dry_run`,对应阶段(Phase 5/6/7)按 `{{PUSH_MODE}} 分支` 一节中的停止线提前结束。

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

如果 `{{PUSH_MODE}} == dry_run` 或 `{{PUSH_MODE}} == local_only`,**Phase 7 — 9 整体不执行**:
按 `{{PUSH_MODE}} 分支` 一节中的停止线,在 `dry_run` 模式下在 Phase 3 之后生成 dry-run 报告后即停;在 `local_only` 模式下 Phase 6 之后(已生成 `git status` 列表)即停。**绝对不要 `git add` / `git commit` / `git push` / `git tag`**。

### Phase 8 — Commit + Push(仅 `commit_and_push`)

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
- **`{{PUSH_MODE}}` 不在 `commit_and_push` / `local_only` / `dry_run` 三值之内** → blocked;写 `reports/pdf_ocr_local_import_blocked_<YYYYMMDD>.md`,不进入 Phase 0;**不猜测默认值**

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
