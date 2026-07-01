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

### 任务启动前 Divergence 检查（v0.3.68+）

任何任务第一步**必须**先记录本地 / 远端拓扑，**不要**立刻 `git pull`：

```bash
cd ~/hermes-knowledge-base
git status --short                                # 1. 工作树 dirty
git rev-parse HEAD                                 # 2. 本地 HEAD
git fetch origin main --tags                       # 3. 拉取最新 refs（不修改工作树）
git rev-parse origin/main                          # 4. 远端 main
git merge-base HEAD origin/main                    # 5. 共同祖先
git rev-list --left-right --count HEAD...origin/main  # 6. ahead/behind
```

`scripts/check_task_preflight.py` 现在（v0.3.68+）在 JSON 输出中包含 `git_divergence` 字段：

```json
{
  "git_divergence": {
    "head":         "<sha>",
    "origin_main":  "<sha>",
    "merge_base":   "<sha>",
    "ahead_count":  0,
    "behind_count": 0,
    "is_diverged":  false,
    "is_ahead":     false,
    "is_behind":    false,
    "is_synced":    true
  }
}
```

`is_diverged / is_ahead / is_behind / is_synced` 四个布尔字段给 agent 与人一个一眼可读的拓扑状态。

#### Divergence 决策树（v0.3.68+）

| 拓扑 | 处置 |
|------|------|
| **synced**（ahead=0, behind=0） | 继续，**不要** pull（已同步） |
| **behind**（behind>0, ahead=0） + 工作树 clean | `git pull --ff-only origin main` |
| **behind**（behind>0, ahead=0） + 工作树 dirty | **停止**——先 commit / stash 当前工作，再 pull；不要在 dirty 上 pull |
| **ahead**（ahead>0, behind=0） + ahead commit 是本任务产物 | 继续，**记录** ahead commit 列表；不要立刻 push；commit / tag 流程中会一并 push |
| **ahead**（ahead>0, behind=0） + ahead commit 是外部 session 产物 | **停止并询问用户**；不要 reset、不要 force push、不要 `git push --force-with-lease`；建议先 `git log --oneline origin/main..HEAD` 看 ahead 内容 |
| **diverged**（ahead>0, behind>0） | **停止并询问用户**；不要自动 merge / rebase；需要 explicit `git merge origin/main` 或 `git rebase origin/main` 用户授权 |

#### 严格禁止

- ❌ 任何情况下**不得** `git push --force` / `--force-with-lease` / `-f`（v0.3.67 出现过 `befb3f9` 因外部 force-push 抹掉 `ea035c6` 的现象；本任务严禁此操作）
- ❌ 不得在 dirty 工作树上 `git pull --rebase`（会产生未审阅的 rebase 冲突）
- ❌ 不得用 `git reset --hard origin/main` 覆盖本地 ahead commits（会丢工作）
- ❌ 不得在未询问用户的情况下处理 external-session 的 ahead commits

#### Preflight 因非本任务历史报告 dirty 失败（v0.3.66+）

如果 preflight FAIL 的**唯一**原因是 `Working tree dirty:`，且 dirty 条目仅来自**历史 `reports/*.md` 的外部 SHA 回填**（通常是上一次别 session 留下的字段补全），不得：

- ❌ 自行 `git checkout -- <file>` / `git restore <file>` 丢弃
- ❌ 把这些历史 reports 一并 `git add` 夹带到本任务的 commit / tag 中
- ❌ 假装工作树干净

应：

- ✅ 在报告中明确记录 dirty 文件路径与来源（pre-existing / 外部 session）
- ✅ 询问用户或使用 v0.3.66 新增的 `python3 scripts/check_task_preflight.py --classify-dirty --json` 模式（仅在全部 dirty 归类为 EXTERNAL 时降级为 PASS_WITH_WARNINGS，且**绝不**自动 stage / restore / commit）
- ✅ 在本任务 commit 中 per-file `git add`，只携带本任务明确产出的文件
- ✅ 后续任务以同样纪律处理（per-task 自报 dirty 来源，不假定继承前序任务）

### Tags / Topics 软范围 WARN 处理（v0.3.68+ policy）

`scripts/audit_kb_state.py` 持续报告约 24 个 `tags count outside [6,12]` 与 `topics count outside [3,8]` 软范围漂移。**这是 WARN，不是 FAIL**——绝**不**作为 immediate cleanup target。

具体规则：

- ❌ 不得在 routine commit / governance commit 里**批量裁剪** tags / topics 来"fit into range"
- ❌ 不得为了消除 WARN 而删除有信息量的标签（如 listicle / video / music / research cluster 等条目的细分标签）
- ✅ 长尾条目（listicle / video / music / 多源研究综述 / anthology 类）允许 tags > 12、topics > 8，因为分类细粒度本身是该条目的知识价值的一部分
- ✅ 短条目（短文 / 单点笔记）允许 tags < 6、topics < 3
- ✅ `audit_kb_state.py` 继续 WARN-only——不升级为 FAIL，不阻塞 preflight / postflight
- ✅ 软范围 WARN 的清理属于**专项治理任务**（如 v0.3.63 `tag-soft-limit-convergence`），必须单独立项、用户明确授权、单点 commit；不在治理任务中顺手做

> 此政策背后的原因：tags / topics 是 KB 的**显性**知识图谱信号；批量裁剪会破坏 search / browse 的细粒度可发现性。审计 WARN 是"未来可能值得整理"提示，不是"立刻修"指令。

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

### 2d. 微信公众号 URL 直接入库流程（v0.3.69+）

**触发语**（任一即可）：

- "解读并入库这篇公众号文章：`<mp.weixin.qq.com 链接>`"
- "把这个公众号文章加入知识库：`<mp.weixin.qq.com 链接>`"
- "解读并入库这个公众号文章本地文件：`<本地 html/md/txt 路径>`"

**入口脚本**：`scripts/wechat_url_to_kb.py`
**基线脚本**：`scripts/import_wechat_article_capture.py`（capture JSON → KB 条目）
**必须加载**：[docs/commands/wechat-url-kb-import-command.md](commands/wechat-url-kb-import-command.md) 与 [docs/workflows/wechat-article-kb-import-workflow.md](workflows/wechat-article-kb-import-workflow.md) §"v1.1 新增"。

**最短命令**：

```
解读并入库这篇公众号文章：
<mp.weixin.qq.com 链接>
```

本地文件兜底：

```
解读并入库这个公众号文章本地文件：
<本地 html/md/txt 路径>
```

**底层调用**：

```bash
# dry-run（默认安全模式）
python3 scripts/wechat_url_to_kb.py --url "<链接>" --dry-run
# 真的入库
python3 scripts/wechat_url_to_kb.py --url "<链接>" --import
# 本地文件四选一
python3 scripts/wechat_url_to_kb.py --html-file <path> --import
python3 scripts/wechat_url_to_kb.py --markdown-file <path> --import
python3 scripts/wechat_url_to_kb.py --text-file <path> --import
```

**默认输出结构**（与其它 article 入库一致的 6 文件，无 `source.local-ref.txt`）：

```
content/articles/YYYY/YYYY-MM-DD-wechat-<account-slug>-<title-slug>/
├── metadata.yaml            # content_kind: wechat_official_article
├── source.md                # 原文 Markdown 全文
├── translation.zh-CN.md     # 中文原文按 schema 兼容（清洗 WeChat 页脚后镜像 source）
├── summary.md               # 9 段结构化摘要（一句话总结/核心问题/主要观点/论证结构/关键概念/背景补充/摘录句子/KB 关联/阅读提示）
├── notes.md                 # 结构化阅读笔记（接受/反思/联想/行动/摘录/概念/结构/提醒/提示）
└── raw_payload.json         # 原始 capture JSON 备份
```

中间产物：`inbox/raw/wechat/YYYY-MM-DD-<slug>.json`

**硬约束**：

1. **不登录微信、不扫码、不读 cookie、不绕过微信访问限制、不启用 OpenClaw `@tencent-weixin/openclaw-weixin`**
2. 只抓公开页面；抓不到完整正文即 HARD STOP，不写半成品条目
3. **不做 `project`，不创建 `conanxin.github.io/projects` 页面**，只做 `article`
4. 中文原文用 `translation.zh-CN.md` 兼容处理（清洗后镜像 source），不得因"中文无需翻译"导致 `check_kb.py` 失败

**Hard-stop 规则**：

- 抓不到完整正文 / 页面要求登录 / 只返回摘要 / 正文明显截断 / 只有标题
- 微信拦截公开访问（命中"请在微信客户端打开"等阻断短语）
- 无法确认标题和正文对应
- `import_wechat_article_capture.py` 校验失败（exit 1）
- `check_kb.py` 失败

遇到硬停止时提示用户：

> 这个链接无法直接抓全文，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。

**质量门禁**：

```bash
python3 -m py_compile scripts/*.py
python3 scripts/check_kb.py            # PASS 必填
python3 scripts/update_site.py         # PASS 必填
python3 scripts/audit_kb_state.py      # PASS 必填
python3 scripts/check_pages_sync.py    # PASS 必填
```

**最小测试**（不需要真实抓微信）：

```bash
python3 scripts/wechat_url_to_kb.py --html-file tests/fixtures/wechat_sample_article.html --dry-run
python3 scripts/import_wechat_article_capture.py --dry-run <上一步生成的 capture.json>
```

两条都应输出 `STATUS: DRY_RUN_OK` / `STATUS: PASS`。

**完整流程**：[docs/workflows/wechat-article-kb-import-workflow.md](workflows/wechat-article-kb-import-workflow.md)
**用户入口命令**：[docs/commands/wechat-url-kb-import-command.md](commands/wechat-url-kb-import-command.md)

### 2e. 微信公众号批量入库流程（v0.3.71+）

**触发语**（任一即可）：

- "批量解读并入库这些公众号文章：`<urls.txt>`"
- "批量解读并入库这些公众号文章：`<多行 mp.weixin.qq.com 链接>`"
- "批量解读并入库这些公众号本地文件：`<files.txt>`"

**入口脚本**：`scripts/wechat_batch_import.py`
**单篇脚本**：`scripts/wechat_url_to_kb.py`（v0.3.69）
**必须加载**：[docs/commands/wechat-batch-kb-import-command.md](commands/wechat-batch-kb-import-command.md)。

**最短命令**：

```
批量解读并入库这些公众号文章：
<urls.txt 或多行 URL>
```

本地文件批量：

```
批量解读并入库这些公众号本地文件：
<files.txt 或多行 .html/.md/.txt 路径>
```

**底层调用**：

```bash
# dry-run（默认安全模式）
python3 scripts/wechat_batch_import.py --input urls.txt --dry-run
# 真的入库（末尾自动跑质量门禁）
python3 scripts/wechat_batch_import.py --input urls.txt --import
# 也可直接传多个 --url / --html-file
python3 scripts/wechat_batch_import.py --url "<u1>" --url "<u2>" --import
```

**去重策略**（三层，入库前完成）：

1. `source_url` 去重（URL 归一化后比对）
2. `title + account_name + published_date` 三元组去重
3. `sha256(visible_text)` 正文内容哈希去重

重复输入标记 `SKIPPED_DUPLICATE` / `DRY_RUN_DUPLICATE`，manifest 写明 `duplicate_of`。

**失败策略**：单篇失败（`BLOCKED_FETCH_FAILED` / `BLOCKED_INCOMPLETE_TEXT` / `FAILED_IMPORT`）不中断整批。所有文章处理完后，若 `--import` 且 ≥1 篇 IMPORTED，自动运行四项质量门禁；门禁失败 → 退出码 2，manifest 标 `FAILED_GATE`，不 commit / 不 push。

**manifest**：

```
reports/wechat_batch_import_YYYYMMDD_HHMMSS.md
reports/wechat_batch_import_YYYYMMDD_HHMMSS.json
```

每篇一行，字段含 status / title / account / date / source_url / capture_json_path / kb_article_path / docs_item_path / site_item_path / failure_reason / duplicate_of。

**硬约束**：不登录微信、不扫码、不读 cookie、不绕过微信限制、不 force push、不 `git add -A`、不写半成品、不做 `project`。

**最小测试**：

```bash
python3 tests/run_wechat_batch_smoke.py
```

5 项 smoke：多 fixture 批处理 / 重复检测 / `/AI/` URL 陷阱回归 / 失败隔离 / pages_sync 仍 55 slugs。

**完整流程**：[docs/workflows/wechat-article-kb-import-workflow.md](workflows/wechat-article-kb-import-workflow.md)
**用户入口命令**：[docs/commands/wechat-batch-kb-import-command.md](commands/wechat-batch-kb-import-command.md)

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
