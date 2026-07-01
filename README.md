# Hermes Knowledge Base

个人静态知识库。Hermes agent 维护内容采集、翻译、归档与发布；站点由 GitHub Pages 提供在线浏览。

## 1. 项目一句话说明

把"想留但不想再翻原文"的外部材料（文章 / 散文 / 论文 / 视频 / 播客 / 资源集合 / 个人笔记 / 项目）转成有元数据、有中文译本、有结构化笔记、可被全文检索的静态知识库。所有内容以 `metadata.yaml` 为单一入口，质量门禁一律在 `scripts/` 下。

## 2. 入口

| 入口 | 地址 |
|---|---|
| 在线浏览（GitHub Pages） | <https://conanxin.github.io/hermes-knowledge-base/> |
| 在线浏览（每条记录详情页） | <https://conanxin.github.io/hermes-knowledge-base/items/<slug>/> |
| 本地预览 | `python3 -m http.server 8000 -d site` → <http://localhost:8000> |
| 仓库自身 | <https://github.com/conanxin/hermes-knowledge-base> |
| Changelog | [CHANGELOG.md](CHANGELOG.md) |
| 发布索引 | [docs/RELEASES.md](docs/RELEASES.md) |
| 完整使用手册 | [docs/AGENT_COMMANDS.md](docs/AGENT_COMMANDS.md) |

## 3. 当前状态

<!-- KB_STATE_START — auto-updated by scripts/audit_kb_state.py -->
<!-- Run `python3 scripts/audit_kb_state.py` to refresh; do not edit manually. -->
<!-- Real total = 56 items. Last refreshed: 2026-07-01 (v0.3.70). -->

| 类型 | 数量 | 说明 | 目录 |
|------|------|------|------|
| article | 26 | 外部文章（含 wechat 子集），有 source_url，需翻译 | `content/articles/` |
| essay | 8 | 散文 / 自传性长文，与 article 同等需要翻译 | `content/articles/` |
| note | 9 | 中文笔记，无翻译，来源 `legacy-knowledge` 或 `notes` | `content/legacy-knowledge/`, `content/notes/` |
| resource_collection | 5 | 资源集合（结构化列表，无翻译） | `content/resource_collections/` |
| project | 4 | 项目文档（有 source_url，无翻译） | `content/projects/` |
| video | 2 | YouTube 视频知识包（transcript + cards + analysis） | `content/articles/` |
| academic_paper | 1 | 学术论文（tandfonline 等） | `content/papers/` |
| interview | 1 | 长访谈（视频/播客转录） | `content/articles/` |
| **总计** | **56** | — | — |

<!-- KB_STATE_END -->

> managed block 由 `scripts/audit_kb_state.py` 维护。除非审计脚本显式要求刷新，否则不要手改其中的统计数字；任何"加一条减一条"的动作都会让这个块和真实 `content/` 又漂一次。

## 4. 支持的内容类型

> 当前实际生效的 8 类（与上表一致）：`article` / `essay` / `note` / `resource_collection` / `project` / `video` / `academic_paper` / `interview`。

类型分区与"是否需要中文译本"的真实情况：

| 类型 | 是否需要翻译 | 内容来源 | 落地目录 |
|---|---|---|---|
| `article` | 是（zh-CN） | URL 文章（含 wechat 子集） | `content/articles/YYYY/` |
| `essay` | 是（zh-CN） | 长篇散文 / 自传性长文 | `content/articles/YYYY/` |
| `note` | 否（中文原生） | 个人笔记 / legacy 迁移 | `content/notes/`, `content/legacy-knowledge/` |
| `resource_collection` | 否 | 结构化资源清单 / listicle | `content/resource_collections/` |
| `project` | 否 | 项目文档（有 source_url） | `content/projects/` |
| `video` | 是（zh-CN） | YouTube 视频知识包 | `content/articles/YYYY/` |
| `academic_paper` | 是（zh-CN） | 学术论文（tandfonline 等） | `content/papers/` |
| `interview` | 是（zh-CN） | 长访谈转录 | `content/articles/YYYY/` |

每种类型的 schema 与字段约束见 [docs/TAXONOMY.md](docs/TAXONOMY.md)。

## 5. Quick Start

```bash
# 1. 拉取
git pull --ff-only

# 2. 任务启动前必跑（任何任务）
python3 scripts/check_task_preflight.py

# 3. 一次性完成"质量门禁 + 重建 + 同步"
python3 scripts/update_site.py

# 4. 离线浏览
python3 -m http.server 8000 -d site
# → http://localhost:8000
```

只想确认 KB 健康、不重建：

```bash
python3 scripts/check_kb.py
python3 scripts/audit_kb_state.py
```

## 6. 导入能力总览

四种导入入口各自有完整工作流文档；README 只放最短命令，详细步骤、停止条件、字段约束请打开对应的 docs/workflows 文件。

| 能力 | 触发命令（最短） | 文档 | 注意事项 |
|---|---|---|---|
| 统一材料入口 | 「解读并入库这个材料：<URL 或 本地文件>」<br>「批量解读并入库这些材料：<materials.txt>」 | [docs/commands/material-kb-import-command.md](docs/commands/material-kb-import-command.md), [docs/workflows/material-kb-import-workflow.md](docs/workflows/material-kb-import-workflow.md) | v0.3.76 起做最小可用路由：微信公众号 URL/HTML/MD/TXT 支持；YouTube、普通网页、PDF 只有仓库存在稳定路线时才接入，否则返回 `BLOCKED_UNSUPPORTED` |
| URL 文章 | 「入库并完整翻译：<url>」 | [docs/AGENT_COMMANDS.md](docs/AGENT_COMMANDS.md) | 默认 `content_type=article`、zh-CN、自动 commit/push |
| 本地 PDF | 「把这个本地 PDF OCR 识别、完整翻译并加入 Hermes 知识库：<abs-path>」 | [docs/import-recipes/PDF_OCR_LOCAL.md](docs/import-recipes/PDF_OCR_LOCAL.md), [docs/workflows/pdf-ocr-kb-import-workflow.md](docs/workflows/pdf-ocr-kb-import-workflow.md) | 必须**绝对路径**；PDF 本身不入仓，只留 `source.local-ref.txt` |
| 微信公众号文章 | 「解读并入库这篇公众号文章：<mp.weixin.qq.com 链接>」<br>「解读并入库这个公众号文章本地文件：<path>」<br>「批量解读并入库这些公众号文章：<urls.txt 或多行 URL>」 | [docs/commands/wechat-url-kb-import-command.md](docs/commands/wechat-url-kb-import-command.md), [docs/commands/wechat-batch-kb-import-command.md](docs/commands/wechat-batch-kb-import-command.md), [docs/workflows/wechat-article-kb-import-workflow.md](docs/workflows/wechat-article-kb-import-workflow.md) | **v0.3.69 起支持公开 URL 直抓 + 本地文件兜底；v0.3.71 起支持批量 + 三层去重**（不登录、不扫码、不读 cookie）；OpenClaw 实时链路仍 disabled，详见 §7 |
| YouTube 视频 | 「预检这个 YouTube 视频：<url>」<br>「解读这个 YouTube 视频并加入 Hermes 知识库：<url>」 | [docs/YOUTUBE_CAPABILITIES.md](docs/YOUTUBE_CAPABILITIES.md), [docs/workflows/youtube-link-preflight-workflow.md](docs/workflows/youtube-link-preflight-workflow.md), [docs/workflows/youtube-video-brief-workflow.md](docs/workflows/youtube-video-brief-workflow.md) | 不登录、不读 cookie、不下载完整视频、私密视频直接 BLOCKED 并归档 |

### 7. 微信公众号：当前真实能力

**两条可用通道**（都不登录微信、不扫码、不读 cookie）：

#### 通道 A（v0.3.69+，推荐）：公开 URL 直抓 + 本地文件兜底

只给一个 `mp.weixin.qq.com` 链接，或浏览器另存的 HTML/Markdown/TXT，`scripts/wechat_url_to_kb.py` 抓取公开页面、解析正文、生成标准 capture JSON，再走同一条基线入库流程。

最短命令（WorkBuddy 里直接说）：

```
解读并入库这篇公众号文章：
<mp.weixin.qq.com 链接>
```

本地文件兜底：

```
解读并入库这个公众号文章本地文件：
<本地 html/md/txt 路径>
```

底层脚本：

```bash
# dry-run（默认安全模式，不写 KB 条目）
python3 scripts/wechat_url_to_kb.py --url "<mp.weixin.qq.com 链接>" --dry-run
# 真的入库
python3 scripts/wechat_url_to_kb.py --url "<mp.weixin.qq.com 链接>" --import
# 本地文件四选一
python3 scripts/wechat_url_to_kb.py --html-file <path> --import
python3 scripts/wechat_url_to_kb.py --markdown-file <path> --import
python3 scripts/wechat_url_to_kb.py --text-file <path> --import
```

抓不到完整正文（登录墙 / 拦截 / 截断）时 HARD STOP，提示用户另存为本地文件。详见 [docs/commands/wechat-url-kb-import-command.md](docs/commands/wechat-url-kb-import-command.md)。

#### 通道 A 批量模式（v0.3.71+）

一次给多个链接或本地文件，`scripts/wechat_batch_import.py` 逐篇调用通道 A，三层去重（source_url / title+account+date / content sha256），单篇失败不中断整批，最后生成 markdown + json 双格式 manifest。

最短命令：

```
批量解读并入库这些公众号文章：
<urls.txt 或多行 URL>
```

本地文件批量：

```
批量解读并入库这些公众号本地文件：
<files.txt 或多行 .html/.md/.txt 路径>
```

详见 [docs/commands/wechat-batch-kb-import-command.md](docs/commands/wechat-batch-kb-import-command.md)。

#### 通道 B（v0.3.62，OpenClaw 捕获包桥接）

`@tencent-weixin/openclaw-weixin` 扩展自 2026-04-09 起处于 disabled 状态（详见 [docs/workflows/wechat-real-inbound-troubleshooting.md](docs/workflows/wechat-real-inbound-troubleshooting.md) §2），实时全自动链路不通，但可用已存在的 capture JSON 走桥接：

- ❌ 实时：WeChat → OpenClaw 网关 → capture JSON → KB（扩展 disabled，长轮询不注册）
- ✅ 推荐：已绑定微信的 agent → 写入 standard capture JSON 到 `inbox/raw/wechat/` → 标准 capture JSON → Hermes KB dry-run/import

具体落地（任选其一）：

```bash
# 只看能否解析、不入库
python3 scripts/wechat_inbound_to_capture.py --dry-run

# 用 latest / 指定的 capture JSON 跑一次入库（脚本内部仍默认 --dry-run，需再加 --no-import-dry-run 才会真正产出 5 文件）
python3 scripts/wechat_inbound_to_capture.py --import

# 直接对指定 capture 文件做入库语义检查 + 生成 KB 5 文件 dry-run
python3 scripts/import_wechat_article_capture.py --dry-run inbox/raw/wechat/<file>.json
# 真入库：去掉 --dry-run
```

不要做（硬停止）：

- ❌ `openclaw channels add openclaw-weixin` / `openclaw channels login openclaw-weixin` —— 需要 QR 扫码，operator 决策
- ❌ 读浏览器 cookie、绕过扩展禁用
- ❌ "扫一次码就自动收文"的承诺 —— 这条链路 v0.3.62 状态是 PARTIAL（详见 troubleshooting 文档 §2）

扩展链路重新打通、运营扫码登录 `openclaw-weixin` 的完整步骤见 [docs/workflows/wechat-real-inbound-troubleshooting.md](docs/workflows/wechat-real-inbound-troubleshooting.md) §6。该动作需 operator 显式确认，不在 Hermes 自动化范围内。

### 详情页 / 浏览能力

在线浏览页面内可：

- 按类型筛选（覆盖上面 8 类，不再只是 4 类）
- 按关键词搜索（标题 / 标签 / 主题）
- 按日期倒序排列
- 卡片标题 / "阅读 →" → 站内详情页 `/items/<slug>/`，卡片右侧 GitHub 按钮 → 仓库原始目录
- 一键复制 path

类型差异化默认展开 / 折叠规则见 [docs/AGENT_COMMANDS.md](docs/AGENT_COMMANDS.md) 与站内实现。

## 8. 标准质量门禁（一致命令集）

无论是导入流程中、还是单纯发布流程中，都跑同一组：

| 顺序 | 命令 | 性质 | 期望 |
|---|---|---|---|
| 0 | `python3 scripts/check_task_preflight.py [--planned-tag <v0.3.N-...>] [--allow-warnings]` | task 启动前 | PASS / PASS_WITH_WARNINGS |
| 0 | `python3 -m py_compile scripts/*.py` | 编译 | exit 0 |
| 1 | `python3 scripts/check_kb.py` | 内容完整性 | PASS（v0.3.60 起 word-count drift 仅 WARN） |
| 2 | `python3 scripts/update_site.py` | 一键重建并同步 | exit 0（含同步 + post-sync 检查） |
| 3 | `python3 scripts/audit_kb_state.py` | 状态审计：drift、目录、类型、catalog 同步 | PASS_WITH_WARNINGS（HARD FAILURES 必须为 0） |
| 4 | `python3 scripts/check_pages_sync.py` | site/ ↔ docs/ 发布镜像一致性 | PASS（v0.3.60 起是 post-sync gate） |

`check_kb.py` 是硬门禁：

- 失败 → `update_site.py` 不会触碰 `site/data/catalog.json` 或 `docs/`，直接退非 0
- 失败 → 严禁 commit / push
- 半成品条目（缺文件、字段为 0、翻译不完整）必须先修复或隔离到 `inbox/quarantine/`

`scripts/update_site.py` 的真实内部顺序（与脚本注释一致）：
1. `check_kb.py` （hard-stop）
2. `build_index.py`
3. `export_site_data.py`
4. `generate_item_pages.py`
5. `sync_pages_docs.py`
6. `check_pages_sync.py` （post-sync integrity check；非 0 即拒绝宣称成功）

## 9. 仓库目录结构

```
hermes-knowledge-base/
├── README.md                    # 本文件（项目入口页）
├── CLAUDE.md                    # Agent 行为准则（read-first）
├── CHANGELOG.md                 # 完整 changelog
├── DESIGN_RATIONALE.md          # 设计原则（read-first，CSS / 组件）
├── content/                     # 所有 KB 条目
│   ├── articles/                #   - article / essay / video / interview
│   ├── papers/                  #   - academic_paper
│   ├── projects/                #   - project
│   ├── resource_collections/    #   - resource_collection（现行）
│   ├── collections/             #   - legacy（详见 docs/LEGACY_MIGRATION.md）
│   ├── notes/                   #   - note
│   ├── legacy-knowledge/        #   - 历史迁移条目（note 源）
│   ├── books/                   #   - 预留：book 类型尚未启用
│   └── videos/                  #   - 预留：video 资源原档（当前 KB 走 articles/）
├── inbox/raw/                   # 原始素材 / capture JSON（不入 KB；wechat JSON 放 inbox/raw/wechat/）
├── scripts/                     # 自动化（质量门禁 / 构建 / 同步 / 桥接 / 诊断）
├── templates/                   # 模板（prompts / metadata / notes …）
├── reports/                     # 每次任务的运行报告
├── docs/                        # 手册目录 + GitHub Pages 发布目录
│   ├── AGENT_COMMANDS.md        #   - Agent 命令总纲
│   ├── TAXONOMY.md              #   - 字段与类型 schema
│   ├── RELEASES.md              #   - 发布索引 + 推荐下一版
│   ├── VERSIONING.md            #   - 标签规则与历史 duplicate 表
│   ├── REPORTING_TEMPLATE.md    #   - 报告模板
│   ├── TRANSLATION_RESIDUE_POLICY.md
│   ├── LISTICLE_IMPORT_RULES.md
│   ├── MUSIC_ARTICLE_RULES.md
│   ├── COLLECTIONS.md / LEGACY_MIGRATION.md
│   ├── YOUTUBE_CAPABILITIES.md / CLOUD_HERMES_INTEGRATION.md
│   ├── commands/                #   - 每种能力的命令短档
│   ├── import-recipes/          #   - 完整 recipe（PDF、Gutenberg …）
│   ├── workflows/               #   - 完整工作流（含 wechat troubleshoot）
│   ├── releases/                #   - 逐版本的 release notes
│   ├── items/                   #   - 已生成的详情页快照（生成产物）
│   └── data/                    #   - catalog / index 产物
├── site/                        # 本地开发/预览面；与 docs/ 镜像
└── 发布：site/ ↔ docs/ 必须字节级一致，由 scripts/check_pages_sync.py 校核
```

> `docs/` 同时承担两个角色：(a) 手册/工作流文档的源；(b) GitHub Pages 的发布面。`site/` 是开发、调试、本地预览（`python3 -m http.server 8000 -d site`）的镜像面。任何一边改动都要在另一边 `cp` 镜像，并由 `scripts/check_pages_sync.py` 校验一致性。

## 10. Agent 操作边界

| 可以做 | 不可以做 |
|---|---|
| 跑 §8 的全部质量门禁 | 不登录微信、不扫 QR、不读 cookie |
| `git pull --ff-only` / `git add <file-per-file>`（严禁 `git add -A`） | 不改 KB 正文（source.md / translation.zh-CN.md / summary.md / notes.md）一旦条目创建 |
| per-file `git add`，commit + annotated tag + push | 不动历史 `reports/*.md` |
| 引用 `docs/workflows/*` 与 `templates/prompts/*` 实施导入 | 不绕过 `check_kb.py` hard-stop（FAIL 时严禁 commit） |
| 用 `--dry-run` 桥接脚本预览 | 不承诺"转一次就自动入库"——公众号链路当前 PARTIAL |

完整边界与白 / 黑名单见 [CLAUDE.md](CLAUDE.md)。

### 并发 session / local divergence 处理入口（v0.3.68+）

当多个 agent session 同时在仓库上工作时，可能出现 local HEAD 与 origin/main 偏差。**不要**立即 `git pull --rebase` / `git push --force`。任务启动前先做 4 步：

1. `git fetch origin main --tags`（**只**拉 refs，**不**动工作树）
2. `python3 scripts/check_task_preflight.py --planned-tag v0.3.N-task --classify-dirty --json` 看 `git_divergence` 字段（v0.3.68+ 新增）
3. 按 [docs/AGENT_COMMANDS.md §"任务启动前 Divergence 检查" 的决策树](docs/AGENT_COMMANDS.md#任务启动前-divergence-检查v0368) 处理：synced 继续；behind clean pull；ahead 记录；diverged 询问用户
4. 不得 `git push --force` / `git reset --hard origin/main` / 在 dirty 上 `git pull --rebase`

### Tags / Topics 软范围 WARN 政策（v0.3.68+）

`scripts/audit_kb_state.py` 的约 24 个 `tags count` / `topics count` 软范围漂移 WARN 属于**信息性提示**，**不**作为 immediate cleanup target。**不**批量裁剪；长尾条目（listicle / video / music / research cluster）允许 tags > 12、topics > 8。完整 policy 与理由见 [docs/AGENT_COMMANDS.md §"Tags / Topics 软范围 WARN 处理"](docs/AGENT_COMMANDS.md#tags--topics-软范围-warn-处理v0368-policy)。

## 11. 近期里程碑

完整 release notes 在 [docs/RELEASES.md](docs/RELEASES.md) 与 [CHANGELOG.md](CHANGELOG.md)。近期：

| 版本 | 主题 | 备注 |
|---|---|---|
| v0.3.60 | KB state dashboard 与 README managed block 起点 | 当前类型统计的来源 |
| v0.3.62 | 微信公众号状态权威说明 + capture bridge + diagnostic | 奠定 §7 当前真实能力叙述 |
| v0.3.64 | WeChat 扩展 re-enable pilot（观测 / 回滚） | 验证 Path A 不足以激活 channel；完整回滚到 v0.3.62 状态 |
| **v0.3.65** | **本版本：README-only entrypoint refresh** | 详细见 `reports/readme_entrypoint_refresh_v0.3.65_20260629.md` |
| v0.3.66 | README §9 目录树去重 + preflight `--classify-dirty` flag | 详细见 `reports/readme_polish_preflight_dirty_split_v0.3.66_20260629.md` |
| v0.3.67 | `word_count.translation` 漂移刷新（7→0 WARN） | 详细见 `reports/word_count_metadata_refresh_v0.3.67_20260629.md` |
| **v0.3.68** | **本版本：local divergence 治理 + tags/topics soft-WARN policy 文档化** | 详细见 `reports/local_divergence_and_soft_warn_policy_v0.3.68_20260629.md` |
| **v0.3.69** | **新增微信公众号 URL 直接入库通道**（`scripts/wechat_url_to_kb.py`，公开 URL/HTML/MD/TXT → capture → KB） | 不登录、不扫码、不读 cookie；详见 `reports/wechat_url_direct_kb_import_v0.3.69_20260701.md` |
| v0.3.70 | Windows item page 生成修复 + topics/tags 误判修复 + word_count drift 修复 | 详见 `reports/wechat_import_hardening_windows_pages_fix_v0.3.70_20260701.md` |
| **v0.3.70** | **YouTube 视频解读入库：Ali Abdaal "Financial Freedom is Easy"** | 第 2 条 video 类型；详见 `reports/youtube_video_brief_kb_import_v0.3.70_20260701.md` |
| **v0.3.71** | **新增微信公众号批量入库 + 三层去重**（`scripts/wechat_batch_import.py`，URL 列表/多文件 → 去重 → manifest 报告） | 详见 `reports/wechat_batch_import_dedup_report_v0.3.71_20260701.md` |
| **v0.3.76** | **新增统一材料入库路由器**（`scripts/material_to_kb.py`，URL/本地文件 → 已有稳定入库脚本） | WeChat URL/HTML/MD/TXT 支持；YouTube/普通网页/PDF 未接入稳定脚本时返回 `BLOCKED_UNSUPPORTED` |

---

*Last refreshed for v0.3.76 on 2026-07-01.*
