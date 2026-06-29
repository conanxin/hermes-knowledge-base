# Agent Commands

## 任务报告

**所有 agent 任务完成后必须按 [docs/REPORTING_TEMPLATE.md](REPORTING_TEMPLATE.md) 输出报告。** 三类任务对应三个模板:

| 任务类型 | 模板 | 必填段数 |
|---|---|---|
| 只读审计 (read / search / grep / analyze) | 模板 1 | 3 段 |
| 写入不发布 (write_file / patch / build_index) | 模板 2 | 5 段 |
| 写入并发布 (git push / deploy / publish / 跨 agent 共享) | 模板 3 | 9 段 |

**硬性规则**:
- 任务结束**不能只写"完成了"**,必须有 §2 Scope + §3 Actions + §5 EVIDENCE 三段最低证据
- 只读任务也要有 STATUS + Scope + EVIDENCE(模板 1)
- 写本地文件但未 push 的,标模板 2
- 涉及 `git push` / `deploy` / `publish` 的,标模板 3,且必须含 §7 Commit/Push/Live 段
- `PENDING_CDN_SYNC` 是合法 WARN,不判 FAIL
- 详细的状态词、动作标签、生命周期定义、CDN 延迟规则、并发协议见 [REPORTING_TEMPLATE.md](REPORTING_TEMPLATE.md)

**报告字段要求（v0.3.43+）**:
- versioned task 报告应遵循 [docs/REPORTING_TEMPLATE.md](REPORTING_TEMPLATE.md) §13 覆盖率审计字段清单
- 最终报告必须包含: commit / tag / tag deref / checks / git status
- 如果 postflight 输出 warning,最终回复必须列出 warning

### 任务收尾 Postflight（v0.3.41+）

**每个 versioned task 在 commit/tag 后推荐运行 postflight：**

```bash
python3 scripts/check_task_postflight.py \
    --report-file reports/<task_report>.md \
    --profile auto
# 旧 CLI（v0.3.41 之前，已弃用，仅作为历史快照保留；不再被脚本接受为推荐写法）：
#     --report ... --tag ... --expect-clean --expect-head-origin
# 新 CLI 用 --report-file + --profile auto|publish|article_import|versioned。
# --expect-clean / --expect-head-origin 在新 CLI 中作为可选 flag 仍可附加在
# --profile auto 之后（脚本会接受它们以做 working-tree/HEAD 校验），但推荐
# 显式加 --tag <tag> 以让 postflight 验证 tag deref。
```

**说明：**
- v0.3.41 起 postflight 是 **WARN-only**，不作为 FAIL gate。
- 有 warning 时不要假装 PASS，必须写入最终报告。
- tag missing、report 缺字段、dirty tree 都应记录。
- 当前不强制阻断后续任务，但推荐在报告中说明。

**Legacy profile-based 检查（仍支持）：**

```bash
# 完整任务报告(模板 3 写入并发布)
python3 scripts/check_task_postflight.py \
    --report-file reports/<task>.md \
    --profile publish
```
# 旧版 v0.3.x 7 段约束报告(legacy 豁免)
python3 scripts/check_task_postflight.py \
    --report-file reports/<task>_v0338_20260626.md \
    --profile versioned

# 自动推断 profile + JSON 输出(供 agent 解析)
python3 scripts/check_task_postflight.py \
    --report-file reports/<task>.md \
    --profile auto --json
```

**Profile 选错会怎样**:用 `--profile auto` 即可,脚本从文件名 + 标题启发式推断。如显式选错(比如把 v0.3.x 7 段报告当 publish 跑),脚本会因缺必填段返回 WARN(默认)或 FAIL(`--strict`),不修改任何文件。

**它不是强制门禁,除非未来另行启用 `--strict`**:默认 WARN-only 行为(任何 WARN 不阻断),只在显式 `--strict` 时返回非 0。完整规则见 [REPORTING_TEMPLATE.md §10](REPORTING_TEMPLATE.md)。

---

## 任务启动前 Preflight

**所有任务开始前必须先运行 preflight 检查。**

### 普通导入 / 维护任务

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
python3 scripts/check_task_preflight.py
```

### 带版本 Tag 的 Versioned Task

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task-name
```

### Preflight 结果处理

| 结果 | 处理方式 |
|------|----------|
| **PASS** | 继续执行任务 |
| **PASS_WITH_WARNINGS** | 仅当 warning 为已知非阻断项（如 v0.3.36 known duplicate）时可继续，并在报告中记录 |
| **FAIL** | **立即停止**，不得继续导入、不得 update_site、不得 commit/push |

---

## 导入文章流程

### 1. Preflight

```bash
python3 scripts/check_task_preflight.py
```

### 2. 抓取与翻译

- 抓取 URL 内容
- 如果 URL 抓取失败 / paywall / ACL / 正文不完整 → **hard stop**，记录失败原因
- 完整翻译

### 2a. Anthology / Collection 页面抽取（v0.3.52+）

如果用户提供的是合集 URL（如 Project Gutenberg 全书页），但只指定单篇 / 单一章节：

```
把这篇文章完整翻译并加入知识库：
https://www.gutenberg.org/files/2944/2944-h/2944-h.htm

导入范围限定：
只导入 Ralph Waldo Emerson 的 Self-Reliance 一文。
```

**规则**：

- 明确范围优先于 URL 页面整体
- collection URL 不等于导入整本书
- 必须做 extraction boundary check
- 仅抽取指定边界，其他章节不得混入
- 必须记录 `extraction_scope` 字段到 metadata.yaml
- 必须在 notes.md 记录起点和终点

完整规范见 [templates/prompts/import_article_prompt.md § Anthology / Collection Page 单篇抽取规则](../templates/prompts/import_article_prompt.md)

### 2b. Source-Specific Import Recipes (v0.3.55+)

不同来源的文章有不同的抓取 / 清洗 / 抽取规则。当 source_url 命中一个已知的来源类型时，**必须先加载并遵守对应 recipe**：

| Source type | Recipe |
|---|---|
| Project Gutenberg (gutenberg.org) | [docs/import-recipes/PROJECT_GUTENBERG.md](import-recipes/PROJECT_GUTENBERG.md) |
| Local PDF file (扫描件或文本层) | [docs/import-recipes/PDF_OCR_LOCAL.md](import-recipes/PDF_OCR_LOCAL.md) |

**Project Gutenberg 特定要求**：

- 导入 Project Gutenberg 来源（单篇 essay 或合集章节）请优先参考 [docs/import-recipes/PROJECT_GUTENBERG.md](import-recipes/PROJECT_GUTENBERG.md)。
- collection page / anthology page（多章节合集页）必须遵守该 recipe 的 §6 (单篇抽取) 与 §7 (hard-stop cases)。
- 不得跳过 recipe 中的 duplicate / blocked / extraction scope 检查。
- 报告中必须记录 recipe 是否适用、是否触发 hard-stop。

**本地 PDF OCR 特定要求**：

- 任何"把这个本地 PDF OCR 识别、翻译并加入知识库"任务**必须**优先加载
  [docs/import-recipes/PDF_OCR_LOCAL.md](import-recipes/PDF_OCR_LOCAL.md)。
- 不得跳过 PDF 检视（pdfinfo / pdftotext）、OCR fallback、OCR 证据报告生成。
- PDF 文件本身 gitignored；用 `source.local-ref.txt` 保留本地引用。
- 详情见 [docs/workflows/pdf-ocr-kb-import-workflow.md](workflows/pdf-ocr-kb-import-workflow.md)
  与 [docs/commands/pdf-ocr-kb-import-command.md](commands/pdf-ocr-kb-import-command.md)。

### 2c. 本地 PDF OCR 入库流程（v0.3.62+）

将 §2b 的"Source-Specific Recipes"展开为本地 PDF 入库专门小节。

**触发语**（任一即可）：

- "把这个本地 PDF OCR 识别、完整翻译并加入 Hermes 知识库：`<path>`"
- "本地 PDF 入库：`<path>`"
- "OCR 并翻译入库：`<path>`"
- "把 PDF 文档识别、翻译后加入知识库：`<path>`"

**必须加载**：[docs/import-recipes/PDF_OCR_LOCAL.md](import-recipes/PDF_OCR_LOCAL.md) **整篇**，不允许基于记忆自由发挥。

**最短命令**：

```
把这个本地 PDF OCR 识别、完整翻译并加入 Hermes 知识库：/abs/path/to/file.pdf
```

`<path>` 必须是绝对路径。`./relative.pdf` 或 `~/Downloads/foo.pdf` 不合规；用户必须给出绝对路径，或 agent 自行 resolve 一次再代入。

**默认输出结构**（与 URL 文章导入完全相同的 5 文件 + 1 个本地引用）：

```
content/articles/YYYY/YYYY-MM-DD-<slug>/
├── metadata.yaml            # source_url_missing: true, source_site: "local-pdf"
├── source.md                # 完整 OCR 文本 + <!-- page: N --> + [OCR疑似: ...]
├── translation.zh-CN.md     # 完整简体中文翻译
├── summary.md               # 中文摘要 + 关键金句 + 延伸问题
├── notes.md                 # preflight/duplicate/blocked/OCR 决策
└── source.local-ref.txt     # PDF 本地引用（PDF 本身不入仓）
```

外加 `reports/pdf_ocr_import_<DATE>-<slug>.md` —— OCR 证据报告，必填。

**PDF 入库 vs URL 文章的差异**：

| 差异点 | URL 文章 | 本地 PDF |
|---|---|---|
| 输入 | 远程 URL | 本地绝对路径 |
| 抽取 | `curl` / `web_extract` | `pdfinfo` + `pdftotext`(有文本层)或 `pdftoppm` + `tesseract`(无文本层/扫描件) |
| `source_url` | 真实 URL | `null`，配 `source_url_missing: true` |
| `source_site` | URL host | `"local-pdf"`（规范值） |
| 本地引用 | 不需要 | `source.local-ref.txt` 必填 |
| 入仓 PDF | n/a | gitignored（`.gitignore` 已含 `*.pdf`） |
| Hard-stop | paywall / ACL / 抓取失败 | PDF 不存在 / 加密 / OCR 失败 / 多页不可识别 |

**Hard-stop 规则**（来自 [docs/import-recipes/PDF_OCR_LOCAL.md §18](import-recipes/PDF_OCR_LOCAL.md)）：

- 用户只说"分析这个 PDF" → **read-only**，不得自动入库
- 用户未提供 PDF 路径 → **必须 `clarify` 反问或 blocked**，不得猜
- PDF 不存在 / 加密 / 损坏 → blocked
- OCR 后仍有明显大段缺失 → blocked
- 多页不可识别 → blocked
- 文本层 / OCR 乱码严重 → blocked
- 目录/正文边界无法判断 → blocked
- 无法确认文档完整性 → blocked
- metadata 关键字段无法用 `source_url_missing` / `local-pdf` / `unknown` 合法表达 → blocked
- `check_kb.py` 或 `check_pages_sync.py` FAIL → blocked
- `check_translation_residue.py` 报告真实未翻译段（非 allowlist 内的专名/书名/URL） → 修复或 blocked

**质量门禁**（与 URL 文章同）：

```bash
python3 scripts/check_kb.py                  # PASS 必填
python3 scripts/update_site.py               # 5/5 PASS 必填
python3 scripts/check_pages_sync.py          # PASS 必填
python3 scripts/check_translation_residue.py # WARN-only
```

**报告模板要求**：

- 模板 3（写入并发布），9 段
- 必填 §4.5 OCR / PDF specifics（OCR 方法、页数、字符级噪声数、源文件路径、sha256、入仓方式）
- 必填 §4.6 Translation quality（source 词数、CJK 字数、翻译残留清单、是否需修复）
- 必填 §7 Commit / Push / Live（commit hash、push success、live URL 或 PENDING_CDN_SYNC）
- 必填 §8 Known limitations（每一条 OCR 噪声 + 翻译残留）

**完整流程**：[docs/workflows/pdf-ocr-kb-import-workflow.md](workflows/pdf-ocr-kb-import-workflow.md)
**用户入口命令**：[docs/commands/pdf-ocr-kb-import-command.md](commands/pdf-ocr-kb-import-command.md)
**可复用 prompt**：[templates/prompts/import_pdf_ocr_prompt.md](../templates/prompts/import_pdf_ocr_prompt.md)
**已知良好案例**：`content/articles/2026/2026-06-29-le-guin-carrier-bag-theory-of-fiction/`（commit `bdb1bc8`）

### 3. 质量检查

```bash
python3 scripts/check_kb.py
python3 scripts/check_pages_sync.py
```

### 4. 生成站点

```bash
python3 scripts/update_site.py
```

### 5. 最终检查

```bash
python3 scripts/check_translation_residue.py
```

### 6. Commit + Push

```bash
git add <相关文件>
git diff --cached --stat
git diff --cached --name-only
git commit -m "描述性提交信息"
git push origin main
```

### 7. Tag（如果是 versioned task）

```bash
git tag -a v0.3.N-task-name <commit> -m "Tag message"
git push origin v0.3.N-task-name
```

---

## 版本号选择

1. 运行 `python3 scripts/check_release_tags.py`
2. 以 `recommended_next_minor` 为准
3. 不要复用已使用过的 minor number
4. 从 v0.3.37 开始，每个 minor 只对应一个 tag

---

## 相关文档

- [docs/VERSIONING.md](VERSIONING.md) — 版本命名规则与 tag 策略
- [scripts/check_task_preflight.py](../scripts/check_task_preflight.py) — Preflight 检查脚本
- [scripts/check_release_tags.py](../scripts/check_release_tags.py) — Tag 卫生检查
