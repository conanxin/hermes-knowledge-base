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
    --report reports/<task_report>.md \
    --tag v0.3.N-task-name \
    --expect-clean \
    --expect-head-origin
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

**Project Gutenberg 特定要求**：

- 导入 Project Gutenberg 来源（单篇 essay 或合集章节）请优先参考 [docs/import-recipes/PROJECT_GUTENBERG.md](import-recipes/PROJECT_GUTENBERG.md)。
- collection page / anthology page（多章节合集页）必须遵守该 recipe 的 §6 (单篇抽取) 与 §7 (hard-stop cases)。
- 不得跳过 recipe 中的 duplicate / blocked / extraction scope 检查。
- 报告中必须记录 recipe 是否适用、是否触发 hard-stop。

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
