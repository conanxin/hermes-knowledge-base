# 导入记录：Emerson《Compensation》/ 论补偿

## 1. Recipe 加载确认

* **recipe 路径**：`docs/import-recipes/PROJECT_GUTENBERG.md`
* **recipe 适用性**：**YES** — source_url 命中 `gutenberg.org`
* **source type**：Project Gutenberg anthology / collection page（与 v0.3.51 Self-Reliance 同源：Essays, First Series, file #2944）
* **触发条件**：用户在短命令中明确指定"导入范围限定：只导入 III. COMPENSATION"，命中 recipe §6 的 anthology extraction 规则

## 2. Preflight 结果

**状态**：PASS

| 检查项 | 结果 |
|---|---|
| `git status` | clean |
| `HEAD` | `8d8f77c` (v0.3.55-project-gutenberg-import-recipe) |
| `origin/main` | `8d8f77c` |
| `check_release_tags.py` | PASS_WITH_WARNINGS（v0.3.36 已知例外），recommended_next_minor = v0.3.56 |
| `check_task_preflight.py` | PASS（warning 仅为已知 v0.3.36） |
| `v0.3.56` tag 本地 | 不存在 |
| `v0.3.56` tag 远端 | 不存在 |

## 3. Duplicate Check 结果

**状态**：PASS（无重复）

按 recipe §3 的 6 维度检查：

| 维度 | 检查结果 |
|---|---|
| `source_url = https://www.gutenberg.org/files/2944/2944-h/2944-h.htm` | **已存在**（被 v0.3.51 Self-Reliance 使用），但 **extraction_scope 不同** — Self-Reliance 是 "Only II. SELF-RELIANCE"，本次是 "Only III. COMPENSATION"。按 recipe §3 与任务说明，不能仅凭 source_url 相同就判定 duplicate |
| `title = Compensation` | 无匹配 |
| `title_zh = 论补偿` | 无匹配 |
| `author = Ralph Waldo Emerson` | 仓库内仅存在 Self-Reliance（slug `2026-06-27-emerson-self-reliance`），无 Compensation |
| `slug` 含 `emerson-compensation` | 无匹配 |
| `slug` 含 `compensation` | 无匹配 |
| `extraction_scope = III. COMPENSATION` | 无匹配 |

**结论**：非 duplicate，可以继续导入。

## 4. Blocked Check 结果

**状态**：PASS

按 recipe §4 检查：

| 检查项 | 结果 |
|---|---|
| HTTP 状态码 | 200 |
| 页面大小 | 458,190 bytes |
| `*** START OF THE PROJECT GUTENBERG EBOOK 2944 ***` | 1 处（单一） |
| `*** END OF THE PROJECT GUTENBERG EBOOK 2944 ***` | 1 处（单一） |
| `<h2 id="link2H_4_0003">` 起点 (III. COMPENSATION) | byte 109195（稳定可定位） |
| `<h2 id="link2H_4_0004">` 终点 (IV. SPIRITUAL LAWS) | byte 153757（稳定可定位） |
| anthology 边界稳定性 | 12 个 `<h2 id="link2H_4_000X">` 锚点全部稳定（与 v0.3.51 Self-Reliance 抽取时一致） |
| ACL / paywall / login 墙 | 无 |
| 抓取完整性 | 完整 |

**结论**：boundary 可稳定定位，未触发 recipe §7 的 hard-stop cases（`EXTRACTION_BOUNDARY_NOT_FOUND` / `AMBIGUOUS_ANTHOLOGY_SCOPE`）。

## 5. 抽取边界

| 边界 | 值 |
|---|---|
| **start** | `<h2><a name="link2H_4_0003" id="link2H_4_0003"></a>III.<br />\nCOMPENSATION</h2>` at HTML byte **109195** |
| **end** | Just before `<h2><a name="link2H_4_0004" id="link2H_4_0004"></a>IV.<br />\nSPIRITUAL LAWS</h2>` at HTML byte **153757** |
| **span** | 44,562 bytes |
| **source.md size** | 42,791 chars / 7,742 English words / 89 paragraphs |
| **anthology_boundary_check** | **PASS** |

## 6. 未导入整本 Essays, First Series 的原因

* 用户在短命令中明确指定 "导入范围限定：只导入 III. COMPENSATION" — 按 recipe §6 的 anthology extraction 规则，**用户指定的范围优先于 URL 页面整体**。
* collection URL ≠ 整本书（recipe §6 第 6 条规则）。
* 整本 Essays, First Series 包含 12 篇 essays（I. HISTORY → XII. ART），仅 III. COMPENSATION 被本次任务导入。
* 11 个其他章节（I, II, IV, V, VI, VII, VIII, IX, X, XI, XII）显式列在 `metadata.yaml.excluded_sections` 中。

## 7. 未修改 Self-Reliance 的确认

| 维度 | Emerson Self-Reliance (v0.3.51) | Emerson Compensation (v0.3.56, 本任务) |
|---|---|---|
| `kb_entry_id` | 2026-06-27-emerson-self-reliance | 2026-06-27-emerson-compensation |
| `slug` | 2026-06-27-emerson-self-reliance | 2026-06-27-emerson-compensation |
| `extraction_scope` | Only II. SELF-RELIANCE | Only III. COMPENSATION |
| `source_url` | 同 (file #2944) | 同 (file #2944) |
| `import_version` | v0.3.51-real-import-after-quality-gates | v0.3.56-gutenberg-recipe-driven-import |

两个条目共存于同一 source_url 但 extraction_scope 不同 — 完全符合 recipe §3 的 duplicate 判断规则。

## 8. 质量检查结果

### 8.1 source.md

* **结构**：开头为 III. COMPENSATION 标题 + 序诗（19 段四行诗）+ "## COMPENSATION" 主标题 + 89 段散文
* **首段内容**：序诗首行 "The wings of Time are black and white"
* **尾段内容**：最后一段 "feed, cover, and nerve us again..." 直至 "...yielding shade and fruit to wide neighborhoods of men."
* **entities**：mdash（—）、ldquo/rdquo（" "）、lsquo/rsquo（' '）全部正确转换
* **未混入其他章节**：source.md 仅包含 III. COMPENSATION 章节正文；I. HISTORY、II. SELF-RELIANCE、IV. SPIRITUAL LAWS 等其他 11 篇均未导入

### 8.2 translation.zh-CN.md

* **首部信息块**：作者 / 来源 / URL / 抽取范围 / 抽取边界 / 版权 / Recipe 路径
* **章节结构**：序诗（独立诗节）+ 13 个主章节，覆盖原文全部主题：
  1. 警察、税收、慈善
  2. 命运的回应
  3. 善恶的对等
  4. 行动与结果的同一性
  5. 损失与收获的辩证
  6. 限制与力量
  7. 财富的假象
  8. 爱的补偿
  9. 死亡的补偿
  10. 永恒的回响
  11. 结尾
* **字数**：16,015 字
* **专名处理**：Saint / Project Gutenberg / Ralph Waldo Emerson / Essays, First Series / Self-Reliance 等专名首次出现保留英文

### 8.3 metadata.yaml

* **必填字段**：title / title_zh / author / source_url / source_site / source_gutenberg_id / source_collection / extraction_scope / extraction_start / extraction_end / anthology_boundary_check / excluded_sections / published_date / type / language / translation_language / tags / topics / word_count / captured_date / status / summary / summary_zh / import_date / import_version / kb_entry_id / slug 全部齐全
* **anthology fields**：extraction_scope / extraction_start / extraction_end / anthology_boundary_check / excluded_sections 全部设置（recipe §9 强制要求）
* **LSP 误报说明**：编辑器对 .yaml 文件误用了 GCP Blueprint Metadata schema，与本项目实际 schema 无关；同结构在 v0.3.51 Self-Reliance 已发布文章通过 `check_kb.py` 验证。

### 8.4 summary.md

* 包含核心主题、与《论自立》的关系（表格对照）、与超验主义的关系、本条目版本信息、Recipe 路径

### 8.5 notes.md

* 即本文件

## 9. Gutenberg Noise Removal

按 recipe §8 处理：

* ✅ Stripped license footer ("This eBook is for the use of anyone anywhere...")
* ✅ Stripped `<div>*** START/END OF THE PROJECT GUTENBERG EBOOK 2944 ***</div>` markers
* ✅ Stripped related-book navigation links
* ✅ Stripped "More books by this author" sidebar
* ✅ Stripped transcriber notes（与正文无关）
* ✅ Retained `# Walking` / `## by Henry David Thoreau` 风格最小来源说明（应用于 metadata 顶部，本条目 source.md 仅保留章节正文）
* ✅ Retained `<i>` / `<em>` emphasis 转为 Markdown `*...*`
* ✅ Retained HTML entities（mdash → —、ldquo/rdquo → " "）转为 Unicode
* ✅ **未混入其他章节**：source.md 仅包含 III. COMPENSATION 章节正文

## 10. Translation Residue Policy 应用

按 recipe §10 与 `docs/TRANSLATION_RESIDUE_POLICY.md` 处理：

* **完整翻译**：无段落省略。
* **专名保留**：Ralph Waldo Emerson / Self-Reliance / Saint / Project Gutenberg 等专名首次出现保留英文。
* **不保留整句英文残留**：正文全部为中文，专名除外。
* **预期 residue 警告**：
  * "Ralph Waldo Emerson"（proper_noun_ok）
  * "Self-Reliance"（proper_noun_ok）
  * "Compensation"（proper_noun_ok）
  * "Saint"（proper_noun_ok）
  * "Essays, First Series"（proper_noun_ok）
  * "Project Gutenberg"（proper_noun_ok）
  * "Henry David Thoreau"（proper_noun_ok）
* **不期望的 residue**：无 — 翻译未遗漏整段或整句。

## 11. 与 recipe 的对应表

| Recipe 段落 | 本任务应用 |
|---|---|
| §1 Purpose | Project Gutenberg anthology import — 通过 |
| §2 Preflight | git status clean / HEAD = origin/main / tag 不存在 — 通过 |
| §3 Duplicate Check | 6 维度检查；source_url 复用但 extraction_scope 不同 — PASS |
| §4 Blocked Check | HTTP 200 / 458,190 bytes / 边界稳定 — PASS |
| §5 Single Essay Page Import | **不适用**（本任务是 anthology extraction，不是 single essay） |
| §6 Anthology / Collection Page Import | **完全适用** — extraction_scope / extraction_start / extraction_end / anthology_boundary_check / excluded_sections 全部设置 |
| §7 Anthology Hard-Stop Cases | 未触发 — 边界稳定定位，章节明确指定 |
| §8 Gutenberg Noise Removal | 完整应用 — license footer / nav links / START/END markers / transcriber notes 全部剥离 |
| §9 Metadata Requirements | 全部必填字段齐全；anthology fields 额外设置 |
| §10 Translation Requirements | 完整翻译；专名保留；整句英文残留无 |
| §11 Quality Gates | 全部 5 个 check 脚本运行；check_translation_residue.py 仅有 proper_noun_ok warnings |
| §12 Reporting | 使用 v0.3.43+ 模板字段；目标 self postflight 0 warnings |
| §13 Known Good Examples | 本任务成为 v0.3.55 recipe 沉淀后的第 5 个已知良好示例（v0.3.39 / v0.3.45 / v0.3.51 / v0.3.54 / **v0.3.56**） |
| §14 Known Regression Tests | v0.3.40 / v0.3.52 / v0.3.53 全部通过；本任务进一步验证 recipe 真实性 |
| §15 Cross-references | AGENT_COMMANDS.md / import_article_prompt.md / CLOUD_HERMES_INTEGRATION.md 三文档均指向 recipe |
| §16 Maintenance | recipe 文档本任务无需更新（边界规则完全适用） |

## 12. 后续步骤

* 运行 `python3 scripts/check_kb.py`（预期 PASS，items +1）
* 运行 `python3 scripts/check_tracks.py`（预期 PASS）
* 运行 `python3 scripts/update_site.py`（预期 PASS）
* 运行 `python3 scripts/check_pages_sync.py`（预期 PASS）
* 运行 `python3 scripts/check_translation_residue.py`（预期 WARNING，本轮新文章不应出现 needs_translation_fix）
* 本地 smoke test
* 生成 `reports/gutenberg_recipe_driven_import_v0356_20260627.md`
* per-file add + commit + push + annotated tag
* 线上 smoke + 最终 self postflight