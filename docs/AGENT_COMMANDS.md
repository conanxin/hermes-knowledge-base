# Agent Commands

## 短命令：导入文章到知识库

当用户说以下任意一种表达时，Hermes 默认执行完整导入流程：

- "把这篇文章完整翻译并加入知识库：【URL】"
- "入库并完整翻译：【URL】"
- "加入知识库：【URL】"
- "翻译后入库：【URL】"
- "把这篇文章完整翻译并加入知识库：URL"

### 默认行为

| 参数 | 默认值 |
|------|--------|
| content_type | article |
| 翻译语言 | zh-CN |
| 目录名格式 | YYYY-MM-DD-来源-slug |
| tags/topics | 由 Hermes 根据内容自动判断 |
| commit & push | 自动执行 |

### 🚨 硬规则：路由判定（v0.4+ 新增，2026-06-25）

**触发语 → 目标仓库的映射是硬性规则，不允许自由发挥：**

| 触发语类型 | 唯一目标 | 禁止动作 |
|-----------|---------|----------|
| 「加入知识库」「入库」「完整翻译并加入知识库」「翻译后入库」 | `~/hermes-knowledge-base` | ❌ 不得创建 standalone project / 专题页 / 独立 GitHub Pages 项目 / projects grid 条目 |
| 「做成专题页」「生成独立项目」「发布成项目页」「加入 projects 页面」 | `~/conanxin.github.io/projects/<slug>/` | ❌ 不得顺手入库 KB（用户没说要入库） |

**判定步骤**（每次导入前必走）：

1. **优先匹配"知识库"语义**：用户消息里只要出现"知识库""KB""入库""翻译后入库"任何一词，**强制走 KB 路线**。
2. **次优匹配"项目"语义**：只有出现"专题页""独立项目""项目页""projects 页面"时，才走 project publishing workflow。
3. **歧义时询问**：如果两者都没出现，**必须用 `clarify` 工具反问**，不得默认猜。
4. **默认绝不走 project 路线**：即使文章本身视觉上适合做专题页（如长篇翻译 + 配图），只要用户说"加入知识库"，就只入库 KB。专题页是 separate step。
5. **误路由检测（任何时候都跑）**：任何执行结果输出 `https://conanxin.github.io/projects/...` URL 时，必须自检：
   - 用户原话里有"知识库" / "KB" / "入库" 吗？ → 有 → **wrong route，立即修复**
   - 用户原话里有"专题页" / "独立项目" 吗？ → 有 → 合法
   - 都没有？ → 立即停止，询问用户

**Wrong route 恢复流程（必须按顺序执行）**：

1. **不要删除已生成的 standalone project**（用户可能已经在访问，删了会丢数据）
2. **立即停止后续步骤**，不要继续 commit/push standalone project 路线
3. **生成 wrong route 报告**到 `~/.hermes/workspace/reports/cloud_hermes_wrong_route_<date>_<slug>.md`，明确写出：
   - 用户原话触发语
   - 误生成的 URL
   - 正确的目标 URL
   - 修复动作清单
4. **补做 KB 入库**：在 `~/hermes-knowledge-base/content/articles/YYYY/YYYY-MM-DD-<source>-<slug>/` 下生成完整 5 文件
5. **同时**在 `metadata.yaml` 中加 `related_project_url` 字段指向 standalone project，注明 "上一轮误生成但保留的专题页"，让两份资源互相可发现
6. **跑完整质量门禁** → commit KB 入库 → push（standalone project 路线同步 commit，但 commit message 注明 "wrong route"）
7. **不修改** `~/conanxin.github.io/projects/data.json`（projects grid）—— 因为 standalone project 不属于项目索引
8. **最终回复用户时显式说明**：上一轮是 wrong route，已补做 KB 入库，详情页 URL 是 `https://conanxin.github.io/hermes-knowledge-base/items/<slug>/`

**反例**（禁止行为）：

- ❌ 用户说"加入知识库"，却生成了 `/projects/<slug>/` standalone project
- ❌ 看到文章适合做专题页就擅自加 "做成可访问页面"
- ❌ 翻译完顺手同步给 `projects/data.json` projects grid
- ❌ 因为 KB 入库流程"麻烦"而走更简单的 project 路线

**正例**（期望行为）：

- ✅ 用户说"加入知识库" → 走 KB 5 文件流程 → 输出 `items/<slug>/` URL
- ✅ 用户说"做成专题页" → 走 project workflow → 输出 `/projects/<slug>/` URL
- ✅ 用户说"加入知识库 + 做成专题页" → 两个都做，但 KB 是主、专题页是辅（在 KB metadata 里 `related_project_url` 标注）

### 执行流程

1. 抓取正文（web_extract → browser 降级）
2. 创建目录结构
3. 保存 source.md
4. 完整翻译为 translation.zh-CN.md
5. 生成 metadata.yaml（含 title_zh, source_site, word_count 等完整字段）
6. 生成 summary.md
7. 生成 notes.md（使用统一模板）
8. 处理 assets/
9. 更新索引（build_index.py）
10. 更新在线浏览页（update_site.py）
11. 运行质量检查（check_kb.py + check_translation_residue.py）
12. Commit & Push
13. 生成导入报告

### 质量门禁

导入完成后必须满足：

- check_kb.py PASS（0 issues）
- update_site.py PASS（site/ 和 docs/ 同步完成）
- check_pages_sync.py PASS（site/ ↔ docs/ 内容一致）
- check_translation_residue.py 软门禁：suspicious_count < 20（长名单 / 影视 / 书单类文章例外 — 详见 [LISTICLE_IMPORT_RULES.md](LISTICLE_IMPORT_RULES.md) §6）
- metadata.yaml 字段完整（含 title_zh, source_site, language, translation_language, word_count）
- word_count.source > 0 且 word_count.translation > 0
- notes.md 使用统一模板

### 📋 长名单文章（listicle）特殊规则

当文章为 **Top N / Best N / Greatest N / 排名型 listicle**(例如 Paste「100 greatest songs of the 1960s」),**必须**按以下加强流程处理。**完整规范**：[docs/LISTICLE_IMPORT_RULES.md](LISTICLE_IMPORT_RULES.md)。

**5 条核心约束**（细节见链接）：

1. **必须先完整解析 source.md** — 不得基于截断版 web_extract 开始翻译。
2. **翻译前结构预检** — 统计 H2 数量、检查编号连续性、查重、记录分页范围。
3. **翻译后结构对齐** — source.md 与 translation.zh-CN.md 的编号标题必须一一对应。错位 / 缺号 / 重复 / 凭空捏造 → hard-stop。
4. **metadata + summary 必须记录 coverage_scope** — 例：`coverage_scope: "rank_100_to_51_only"` + `is_partial_series: true`。
5. **residue 状态分级** — 长名单文章 residue 可能很高(全是专名),状态用 `PASS_WITH_WARNINGS` 而非简单 `PASS`。但必须在 metadata.translation_notes 与报告中说明专名类型,不得因数高而掩盖真正漏译。

**历史案例**：2026-06-26 Paste「100 greatest songs of the 1960s」(commit `725b7a9`) 翻译过程曾因截断导致 #76-#66 共 11 首歌 H2 错位 + #75 缺失 + #74 凭空捏造,后续通过 source 重提取与 patch 修复,经验固化到 LISTICLE_IMPORT_RULES.md。

### 导入后自动执行的质量检查

每篇文章导入完成后，Hermes 会自动运行：

```bash
python3 scripts/check_kb.py
python3 scripts/update_site.py
python3 scripts/check_pages_sync.py
python3 scripts/check_translation_residue.py
```

**check_kb.py** 必须 PASS，否则修复问题后再继续。  
**update_site.py** 必须 PASS，确保 site/ 和 docs/ 同步完成。  
**check_pages_sync.py** 必须 PASS（`update_site.py` 内置在 sync 后会自动运行此检查），确保所有发布文件 site/ 与 docs/ 内容一致。  
**check_translation_residue.py** 可以有 warning，但严重残留必须修复。

### 强制停止条件

以下情况 Hermes 必须停止导入，向用户报告，不要强行入库：

- URL 无法访问或返回 404/403/500
- 正文抓取不完整（明显截断、缺少关键章节）
- 文章需要登录或付费才能阅读完整内容
- 内容类型不明确（无法判断是文章、论文、评论等）
- 翻译后英文残留严重（suspicious_count ≥ 20）
- metadata 关键字段无法确定（如作者、标题缺失）

### 追问场景

如果用户只说"把这篇文章加入知识库"但没有提供 URL，Hermes 应该追问：
"请提供文章 URL。"

如果用户提供多个 URL 且没有明确说明，Hermes 应该追问：
"您想导入哪一篇文章？请提供具体 URL。"

### 模板位置

完整导入流程模板：`templates/prompts/import_article_prompt.md`

metadata 模板：`templates/metadata.yaml`

notes 模板：`templates/notes.md`

## 质量门禁（硬性规则）

1. `update_site.py` 已在最前面内置 `check_kb.py` 硬停止。如果 `check_kb.py` 返回 FAIL，`update_site.py` 立即返回非 0，**不会**运行 build / export / generate / sync，**不会**触碰 `site/data/catalog.json` 或 `docs/`。在 check 修复前**严禁**执行 commit / push。
2. `word_count` 字段必须是 YAML 对象，**不允许**用带引号的字符串或裸数字。规范格式：

   ```yaml
   word_count:
     source: 4434        # 整数（source.md 实际词数）
     translation: 7079   # 整数（translation.zh-CN.md 实际 CJK 字数）
   ```

   不允许：`word_count: 4500`、`word_count: "4500"`、`word_count: "~4500"`、`word_count: 约4500`。
3. 发现 `content/` 下存在半成品条目时，必须先修复或隔离到 `inbox/quarantine/`，再继续执行 `update_site.py`。
4. 除非用户明确说"先不要 commit/push"，否则完整导入流程应自动运行到 check → update_site → commit → push；但当 check 失败时必须立即停止并报告。

### 完整流水线顺序（更新于 v0.3.8+）

```
check_kb.py            ← 质量门禁，FAIL 立即停止
build_index.py
export_site_data.py
generate_item_pages.py
sync_pages_docs.py
```

## 云端 Hermes 使用同一知识库

> 适用于云端 Hermes Agent (Ubuntu VM, `ubuntu@VM-0-4-ubuntu`)

### 云端路径

- **本地仓库路径**：`~/hermes-knowledge-base/`
- **远程 URL**：`https://github.com/conanxin/hermes-knowledge-base.git`
- **不使用** `~/.hermes/wiki/knowledge/` 作为知识库路径（该目录是 Hermes 内部研究归档，命名空间独立）
- **不修改** OpenClaw 目录（`~/.openclaw/` 等）

### 云端导入前必须 pull --ff-only

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
git status   # 必须干净
```

- 任何非 fast-forward 的情况都意味着本地有未推送的 commit 或历史分歧 — 立即停止并报告
- 拉取后必须确认 `git log -1` 与 origin/main 一致

### 云端 push 走 repo-local proxy

云端网络环境特殊：默认 `ALL_PROXY=socks5://127.0.0.1:7898` 环境变量会触发 git 客户端的 GnuTLS bug（`GnuTLS recv error (-110)`），导致 `git fetch` / `git push` 失败。

**解决方案（只对当前 KB 仓库生效，不污染全局）**：

```bash
cd ~/hermes-knowledge-base
git config --local http.proxy  socks5://127.0.0.1:7898
git config --local https.proxy socks5://127.0.0.1:7898
```

**验证**：

```bash
git config --local --get http.proxy   # 预期: socks5://127.0.0.1:7898
git config --local --get https.proxy  # 预期: socks5://127.0.0.1:7898
git fetch origin                       # 静默 exit 0
git pull --ff-only origin main         # "Already up to date."
git push --dry-run origin main         # "Everything up-to-date"
```

如果仍出现 GnuTLS -110：说明 SOCKS 代理端口或 sing-box 状态变化（pid 1751052 / 1751024）— 排查代理健康。如果出现 401/403：token 失效 — 报告，不执行 `gh auth refresh`。

### 云端约束（与本地一致 + 额外）

- 不 force push
- 不 rebase 共享分支
- 不修改历史 commit
- 不写入 token
- 不执行 `gh auth refresh`
- 不修改 Telegram / gateway / cron / systemd
- 不依赖 Telegram 通知（云端 Telegram 通道当前离线）
- commit 前必须确认工作区只包含本次导入相关文件

### 云端完整流水线顺序

```
git fetch origin
git pull --ff-only origin main
check_kb.py            ← 质量门禁，FAIL 立即停止（不得 commit / push）
build_index.py
export_site_data.py
generate_item_pages.py
sync_pages_docs.py
check_pages_sync.py
check_translation_residue.py
git add <本次相关文件>
git commit -m "<语义化 message>"
git push origin main
```

完整规范与故障排查：[CLOUD_HERMES_INTEGRATION.md](CLOUD_HERMES_INTEGRATION.md)
