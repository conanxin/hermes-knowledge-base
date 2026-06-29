# README Entrypoint Refresh (v0.3.65) — 2026-06-29

## Summary

README 从"历史追加型操作手册"(496 行)改为"项目入口页"(236 行)。所有细节下沉到 `docs/`；managed block 原样保留；公众号部分按 v0.3.62 真实状态重写；8 类全列；导入能力整理成总览表；质量门禁统一；目录表与 `ls` 一致。

| 维度 | Before | After |
|---|---|---|
| 行数 | 496 | 236 |
| 主章节数 | 杂糅 12+ 段 | 11 段（建议结构 10 + 落款） |
| KB_STATE managed block | 保留 | 保留且**未手改** |
| 公众号承诺 | "将微信公众号文章全文入库" + 自动 addon | v0.3.62 真实状态：扩展 disabled、Hermes 不绑微、推荐 capture JSON → bridge dry-run/import |
| 导入能力 | 各自独立长流程 | 一张总览表，细节 link 到 docs/workflows/* |
| 类型说明 | 旧 4 类（article / note / project / resource_collection） | 当前 8 类 |
| 质量门禁 | 两套（"导入后" 与 "硬性规则"） | 一套统一表 |
| Releases 区 | v0.3.24 写 latest | 替换为 v0.3.60 / v0.3.62 / v0.3.64 + v0.3.65 "近期里程碑" |

---

## 1. 执行步骤与真实回传

| 步骤 | 命令 | 结果 |
|---|---|---|
| 1. cd + git fetch + checkout main + pull --ff-only | `git fetch origin main && git checkout main && git pull --ff-only origin main` | `Already up to date` (exit 0) |
| 2. preflight | `python3 scripts/check_task_preflight.py --planned-tag v0.3.65-readme-entrypoint-refresh --allow-warnings` | **FAIL** — `Working tree dirty: M reports/v0.3.63_tag_soft_limit_convergence_report_20260629.md`（pre-existing，**非本次任务引入**；其余 7 项 gate 全 PASS/PASS_WITH_WARNINGS）。**经用户明确确认"继续"后放行**；本任务在 commit 时仅 per-file add README + 本报告 + （如需）troubleshooting，不会触碰该 v0.3.63 报告。 |
| 3. py_compile | `python3 -m py_compile scripts/*.py` | exit 0，`PY_COMPILE_OK` |
| 4. baseline check_kb | `python3 scripts/check_kb.py` | **PASS**：54/54；7 个 word-drift warnings（非阻塞） |
| 4'. baseline audit_kb_state | `python3 scripts/audit_kb_state.py` | **PASS_WITH_WARNINGS**：27 warnings；**HARD FAILURES: 0** |
| 5. 探索 README + docs + tags | `ls`, `grep`, `git tag`, `git log -20` | 1) docs/workflows/wechat-real-inbound-troubleshooting.md 已存在且为权威链；2) 最新 tag 是 `v0.3.64-openclaw-weixin-reenable-pilot`，`v0.3.65-readme-entrypoint-refresh` 不撞 duplicate；3) 当前实际生效内容目录 = `articles/ books/ legacy-knowledge/ notes/ papers/ projects/ resource_collections/ videos/`——`content/collections/` 不存在；4) `docs/releases/` 只到 v0.3.25，"近期里程碑"需内联。 |
| 6. 编辑 README | `write_file README.md` | 496 → 236 行 |
| 7. post-edit check_kb | `python3 scripts/check_kb.py` | PASS（与 baseline 完全一致：54/54，相同 7 个 word-drift warnings） |
| 7'. post-edit audit_kb_state | `python3 scripts/audit_kb_state.py` | PASS_WITH_WARNINGS，HARD FAILURES = 0，27 warnings（**与 baseline 数值完全相同；README 不参与审计**） |
| 7''. post-edit check_pages_sync | `python3 scripts/check_pages_sync.py` | PASS：site/ ↔ docs/ 字节级一致；本次未触碰 site/docs，预期内 |
| 8. postflight | `python3 scripts/check_task_postflight.py --report-file reports/readme_entrypoint_refresh_v0.3.65_20260629.md --profile auto` | （见下表） |

### 1.1 Preflight 异常说明（与 spec 停止条件的偏差记录）

- spec 停止条件之一：`preflight FAIL → 停`。
- 实际：preflight FAIL，但**唯一错误项是 pre-existing dirty 项**（`reports/v0.3.63_tag_soft_limit_convergence_report_20260629.md`，modified），不属本次任务范围，且 spec 同时禁止"修改历史 reports/*.md"——两条硬约束直接冲突。
- 处理：停转询问。用户回复"继续"，确认本次任务在 README 自己的范围内推进；commit 严格 per-file add 本次三件套，绝不把 v0.3.63 报告夹带进 tag。
- 建议（README 后续 fix 项）：让 preflight 区分 "untracked / dirty-staged-by-self / dirty-by-others" 三种来源，dirty-by-others 应转为 WARN 而非硬 FAIL。

---

## 2. 改动摘要（每个 spec 要求的修正点逐条对账）

| Spec 要求 | 落地位置 | 做法 |
|---|---|---|
| 改"项目入口页"，优化项目说明、入口结构、过时叙述 | §1, §2 | 一句话说明；入口表（在线/本地/changelog/手动） |
| 保留 KB_STATE managed block，不手改统计数字 | §3 | block 字节级保留；上文加一段"由 audit 维护，不要手改"提示 |
| 修正公众号：Hermes 不直接绑微；推荐 capture JSON → bridge dry-run/import | §6 表 + 专门的 §7 | §7 顶部明写"当前不直接绑定个人微信"、扩展 disabled 时间、推荐路线、明确禁止 `openclaw channels add/login` / 扫码 / 读 cookie、不承诺"转一次自动入库" |
| 补 `docs/`、`site/`、`docs/` 作为 GH Pages 发布目录 | §9 目录树 | 明确 `docs/` 行 + 第两行注释说"发布目录，与 site/ 镜像" |
| `content/resource_collections/` 补；`content/collections/` 标注 legacy | §9 目录树 | 都列了：`resource_collections/` 注释"现行"；`collections/` 注释"legacy，详见 docs/LEGACY_MIGRATION.md"（**不假装它当前有内容**——`ls content/` 验证不存在；spec 期望"标注为 legacy"，我以 link 形式给出不下结论） |
| 合并重复质量命令到"标准质量门禁" | §8 | 单一表格；步骤序号与 spec 完全一致（check_task_preflight → py_compile → check_kb → update_site → audit_kb_state → check_pages_sync） |
| 修正 update_site.py 说明，明确真实顺序 | §8 | 内部顺序 1-6 与脚本注释一致；说明 `check_pages_sync.py` 是 post-sync gate，非 0 拒绝宣称成功 |
| 4 导入能力整理成总览表 | §6 | 一张表，行 = URL/PDF/微信/YouTube；列 = 触发命令/文档/注意事项 |
| 修正"浏览功能"类型筛选覆盖 8 类 | §"详情页 / 浏览能力"段 | 列 8 类：不再只是旧的 4 类 |
| Releases 区改"近期里程碑"，不再把 v0.3.24 写 latest | §11 | v0.3.60 / v0.3.62 / v0.3.64 / 本次 v0.3.65 4 条 |

### 2.1 spec 暗示但未明说的取舍

- "**已绑定微信的 agent → 标准 capture JSON → Hermes KB dry-run/import**"——按 spec 字面写成推荐路线，引用 troubleshooting §6 step 5 作为唯一真入库命令（`--import`，内部仍默认 dry-run，需 `--no-import-dry-run` 才会真正产出 5 文件）。
- 不引用 `scripts/import_wechat_article_capture.py` 早期 README 段对官方 5 文件目录的详细列表——直接 link 到 `docs/workflows/wechat-article-kb-import-workflow.md`。spec 说"细节下沉"。

---

## 3. 严格限制对账

| 限制 | 状态 | 证据 |
|---|---|---|
| 不导入新内容 | ✅ 未发生任何"add new content"动作 | `git status --short` post-edit 仅 README + 待加本报告 |
| 不运行 `scripts/wechat_inbound_to_capture.py --import` | ✅ | 全程仅声明命令，不执行 |
| 不登录微信、不扫码、不 `openclaw channels add/login` | ✅ | 同一命令在 README §7 仅作为"禁止"出现 |
| 不改 `source.md` / `translation.zh-CN.md` / `summary.md` / `notes.md` | ✅ | 全程未触碰任何 KB 正文字段 |
| 不改历史 `reports/*.md` | ✅ | 仅新增 `reports/readme_entrypoint_refresh_v0.3.65_20260629.md` |
| 不提交 `~/.openclaw/*` | ✅ | `~/.openclaw` 未在工作树出现 |
| 不改 GitHub Pages 内容（除非 README 链接修正必须） | ✅ | 未触碰 site/、docs/；`check_pages_sync.py` 通过即证明 |
| 不手改 KB_STATE managed block 数字 | ✅ | block 整段保留：`<!-- KB_STATE_START -->` ... `<!-- KB_STATE_END -->` 含 54/8 类/数字原样 |

---

## 4. README 改动 diff 摘要（高粒度）

- 已删除章节：
  - `## 用途`（与 §1 重复）
  - 旧 `## 目录结构`（与 §9 重复，且内容过旧——如 `inbox/raw` `index/` `templates/` `reports/` 这些应属于通用结构而不是和 `books/` `papers/` `videos/` 平级）
  - 旧 `## 当前内容类型`（已并入 §3 + §4）
  - `## 质量检查命令`（已并入 §8）
  - `## 本地浏览知识库`（已并入 §2 + §5）
  - `## 维护方式`、`## 状态标记`（重复/不必要）
  - `## 导入文章` 长过程（已下沉到 §6 + docs/AGENT_COMMANDS.md）
  - `## 导入本地 PDF` 长过程（已下沉到 §6 表格）
  - `## 微信公众号文章入库` 长过程（已下沉到 §7，专注真实状态）
  - `## YouTube 视频知识包` 长过程（已下沉到 §6 表格）
  - `## 浏览知识库` 长过程（已合并到 §5 + §6 末尾"详情页/浏览能力"）
  - `## Releases`（v0.3.24 latest 已过时）→ 改成 §11 近期里程碑
  - `## 质量门禁（硬性规则）`（与 §8 重复）

- 净行数：-260（从 496 → 236，缩减 52.4%）
- 信息密度：每节都是"标题 → 一句话或一张表 → link"，无冗长操作手册段落。

---

## 5. 残留 README 后续建议（next moves）

下个微小版本可以做的，不在本任务 spec 范围内：

1. **类型细分历史 drift**：当前 7 个 word-count drift warnings（baseline 持久存在），可单开 `v0.3.66-word-count-metadata-refresh` 任务，对 `metadata.yaml` 的 `word_count.translation` 字段做 read-only re-measure + 单值 patch。
2. **`scripts/import_wechat_article_capture.py --no-import-dry-run` 的传播**：`wechat_inbound_to_capture.py --import` 的双 dry-run 设计是真入库的最短命令，但对 operator 不直观。是否值得在 docs/workflows/wechat-real-inbound-troubleshooting.md §6 step 5 加一个 `--really-import` 之类的明确开关，避免误触。**scope creep，本次不做**。
3. **managed block 自动 anchor**：当前 `<!-- KB_STATE_START -->` 的位置在 §3，可考虑让 `audit_kb_state.py` 找到这个锚点后**只刷新块内文本**，把"位置漂移"也从 drift 里清掉。**待 user 确认是否要做**。
4. **类型数 9 → ?**：随 `videos/` 在 §9 注释为"预留"，若有 video 原档需求可单独立独立 KB type。当前未启用。
5. **`docs/commands/` 与 `docs/import-recipes/` 与 `docs/workflows/` 三个目录的重叠**：CLI 命令 vs 工作流 vs 配方目前在 docs 内分布清晰但 README 没给出"先去 commands、再 workflows，最后 import-recipes"的阅读序。可在 `docs/AGENT_COMMANDS.md` 顶部加一张 README-map。**scope creep**。
6. **`content/books/` 与 `videos/` 入口**：当前 §9 已注明"预留"，未来如启用 book/video 原档可考虑把 `metadata.yaml` schema 限定为只读副本（不参与 `content/articles/` 的 translation 系列流程）。**future task**。
7. **preflight 工作树脏检查的来源判定**（见 §1.1）— 让它区分 self vs others，是干净闭环的关键。

---

## 6. 工作清单（Git 侧）

- modified: `README.md`
- new: `reports/readme_entrypoint_refresh_v0.3.65_20260629.md`（本文件）
- not modified: `docs/workflows/wechat-real-inbound-troubleshooting.md`（已自洽，无需同步——README §7 链接直接指向它 §2/§6）

预期 per-file git add：

```bash
git add README.md
git add reports/readme_entrypoint_refresh_v0.3.65_20260629.md
```

commit 消息：`Refresh README as project entrypoint`  
tag：`v0.3.65-readme-entrypoint-refresh`（与 preflight `--planned-tag` 一致）  
push：origin main + tag。
