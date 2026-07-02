# Hermes Knowledge Base

> 个人静态知识库。Hermes agent 维护内容采集、翻译、归档与发布；站点由 GitHub Pages 提供在线浏览。
>
> **当前稳定版本：** `v0.4.0-operator-ready-material-ingestion` (commit `c1695fd`)
> **Full gate 状态：** `PASS_WITH_WARNINGS` — 0 hard failures，1 软警告 (`audit_kb_state` 29 条 tags/topics 软范围漂移，content 自带，未变更多个月；详见 [docs/OPERATOR_PLAYBOOK.md §1.1](docs/OPERATOR_PLAYBOOK.md#11-known-soft-warnings-informational-only))
> **入口脚本：** [`scripts/material_to_kb.py`](scripts/material_to_kb.py)（统一材料入口）+ [`scripts/run_full_gate.py`](scripts/run_full_gate.py)（统一全量门禁）
> **本 README 角色：** 项目首页说明（最短路径 + 文档导航）。所有 daily import / 各材料详细流程 → [docs/OPERATOR_PLAYBOOK.md](docs/OPERATOR_PLAYBOOK.md)。

---

## 1. 一句话说明

把"想留但不想再翻原文"的外部材料（公众号 / 网页 / 视频 / PDF / 本地文件 / 项目文档）转成有元数据、有中文译本、有结构化笔记、可被全文检索的静态知识库。所有内容以 `metadata.yaml` 为单一入口，质量门禁一律在 `scripts/` 下。

---

## 2. 线上入口

| 入口 | 地址 |
|---|---|
| 在线浏览（GitHub Pages） | <https://conanxin.github.io/hermes-knowledge-base/> |
| 单条详情页 | <https://conanxin.github.io/hermes-knowledge-base/items/<slug>/> |
| 本地预览 | `python3 -m http.server 8000 -d site` → <http://localhost:8000> |
| 仓库 | <https://github.com/conanxin/hermes-knowledge-base> |
| 多媒体资产（GitHub Releases） | [docs/releases.md](docs/releases.md) |

完整文档导航见 [§11](#11-详细文档导航)。

---

## 3. 当前 KB 状态

> 由 [`scripts/audit_kb_state.py`](scripts/audit_kb_state.py) 在本次 commit 时输出（real metadata.yaml count = 66）。这是当前真值；下一次任务 / commit 前如需刷新，跑一次 `python3 scripts/audit_kb_state.py` 并把数字粘回本节即可。

| 类型 | 数量 | 是否需要 zh-CN 翻译 | 落地目录 |
|---|---|---|---|
| `article` | 36 | 是 | `content/articles/YYYY/` |
| `note` | 10 | 否（中文原生） | `content/notes/`, `content/legacy-knowledge/` |
| `essay` | 8 | 是 | `content/articles/YYYY/` |
| `resource_collection` | 5 | 否 | `content/resource_collections/` |
| `project` | 4 | 否 | `content/projects/` |
| `video` | 1 | 是 | `content/articles/YYYY/` |
| `academic_paper` | 1 | 是 | `content/papers/` |
| `interview` | 1 | 是 | `content/articles/YYYY/` |
| **总计** | **66** | — | — |

类型 schema 见 [docs/TAXONOMY.md](docs/TAXONOMY.md)。

---

## 4. 支持的材料矩阵（v0.4.0）

| 材料类型 | 状态 | 入口 |
|---|---|---|
| 微信公众号 URL（公开） | ✅ 公开 URL 直抓 + 本地文件兜底 | `material_to_kb.py` |
| 普通网页 URL | ✅ robots-friendly 公开页 | `material_to_kb.py` |
| YouTube URL（有 transcript） | ✅ **full transcript 才入库** | `material_to_kb.py` |
| YouTube URL（无 transcript / 登录 / 私密） | 🛑 BLOCKED | — |
| 本地 HTML / MD / TXT | ✅ | `material_to_kb.py` |
| 本地 PDF（extractable text layer） | ✅ PyMuPDF 本地提取 | `material_to_kb.py` |
| 本地 PDF（扫描版） | 🛑 `BLOCKED_NEEDS_OCR`（不写半成品） | OCR 走 [docs/import-recipes/PDF_OCR_LOCAL.md](docs/import-recipes/PDF_OCR_LOCAL.md) |
| Release-backed assets（`.mp4` / `.mp3` / 大二进制） | ✅ 不入 git，走 GitHub Release | [docs/releases.md](docs/releases.md) |

**Hard guarantees（任何入口都遵守）：**

- ❌ 不登录微信、不扫码、不读 cookie、不绕 paywall。
- ❌ 不下载完整 YouTube 视频；只取 transcript / 公开 caption。
- ❌ 不写半成品 KB 条目（无 transcript / 扫描 PDF / 登录墙 / 不完整正文 → BLOCKED）。
- ✅ `check_kb.py` / `check_pages_sync.py` 是 hard-stop；FAIL 时严禁 commit。

完整规则、BLOCKED 状态码、停止条件见 [docs/OPERATOR_PLAYBOOK.md §3](docs/OPERATOR_PLAYBOOK.md#3-supported-material-matrix) 与 [§10](docs/OPERATOR_PLAYBOOK.md#10-blocked--failed-status-reference)。

---

## 5. 日常使用：统一材料入口

**单篇：**

```bash
# Dry-run（默认安全模式，不写 KB 条目）— 推荐第一步
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --dry-run

# 真入库（写入 KB 并 commit/push 由后续 gate 校验）
python3 scripts/material_to_kb.py --input "<URL_OR_FILE>" --import
```

**批量：**

```bash
# tmp/materials.txt 每行一个 URL 或本地路径
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --dry-run
python3 scripts/material_to_kb.py --input-list tmp/materials.txt --import
```

`scripts/material_to_kb.py` 是 **unified router**，按输入自动分发到 `wechat_url_to_kb.py` / `web_article_to_kb.py` / `youtube_to_kb.py` / `pdf_to_kb.py`。完整各材料 flow（robots.txt 策略 / dedup / 三层去重 / transcript 阈值 / OCR 兜底等）见 [docs/OPERATOR_PLAYBOOK.md §2–§8](docs/OPERATOR_PLAYBOOK.md)。

---

## 6. 维护 / 发布门禁

**快速检查（sub-minute）：**

```bash
python3 scripts/run_full_gate.py --quick
```

**完整门禁（pre-commit / pre-push，必跑）：**

```bash
python3 scripts/run_full_gate.py --json --output reports/full_gate_run_$(date +%Y%m%d_%H%M%S).json
```

完整版含 17 个步骤：py_compile + 10 个 smoke suites + `check_release_assets` + `check_release_tags` + `check_kb` + `update_site` + `audit_kb_state` + `check_pages_sync`。Runner 会在 gate 后自动校验 **tracked working tree** 是否被污染；发现 `FAILED_CLEANLINESS` 即拒绝。

**退出码含义：**

- `PASS` — 全绿，可提交。
- `PASS_WITH_WARNINGS` — 0 hard failures，软警告（如 audit soft range）；可提交，记录 warns。
- `FAILED_GATE` — 有步骤 hard FAIL；**禁止** commit。
- `FAILED_CLEANLINESS` — gate 通过但产生了 tracked dirty（多半是 `update_site` 的合法 diff，需明示 commit）。

详细 status 含义见 [docs/OPERATOR_PLAYBOOK.md §9.3](docs/OPERATOR_PLAYBOOK.md#93-status-meanings)。

---

## 7. 仓库目录结构

```
hermes-knowledge-base/
├── README.md                    # 本文件（项目首页）
├── CHANGELOG.md                 # 完整 changelog
├── content/                     # KB 条目（articles / papers / projects / notes / legacy-knowledge / resource_collections / books[预留] / videos[预留]）
├── inbox/raw/                   # 原始 capture JSON / 素材（wechat capture 放 inbox/raw/wechat/）
├── scripts/                     # 自动化（gate / build / sync / fetchers / OCR bridge / diagnostic）
├── templates/                   # prompts / metadata / notes 模板
├── reports/                     # 每次任务的运行报告 + full_gate_run_*.json
├── docs/                        # 手册源 + GitHub Pages 发布面
│   ├── OPERATOR_PLAYBOOK.md     #   - 日常使用手册（v0.4.0+）
│   ├── AGENT_COMMANDS.md        #   - agent 命令总纲
│   ├── RELEASES.md              #   - 发布索引 + 推荐下一版
│   ├── releases.md              #   - GitHub Release assets 索引
│   ├── TAXONOMY.md / VERSIONING.md / REPORTING_TEMPLATE.md / ...
│   ├── commands/                #   - 每个能力的命令短档
│   ├── workflows/               #   - 完整工作流（含 wechat troubleshoot）
│   ├── import-recipes/          #   - 完整 recipe（PDF OCR / Gutenberg …）
│   ├── releases/                #   - 逐版本 release notes
│   └── items/, data/            #   - 生成产物（catalog / index / 详情页）
├── site/                        # 本地开发 / 预览镜像（必须与 docs/ 字节级一致）
└── tests/                       # 冒烟测试（11 个 smoke runner）
```

> `docs/` 同时承担两个角色：(a) 手册 / 工作流文档的源；(b) GitHub Pages 的发布面。`site/` 是开发、调试、本地预览的镜像面。任何一边改动都要在另一边 `cp` 镜像，并由 `scripts/check_pages_sync.py` 校验一致性。

---

## 8. 内容模型

每个 KB 条目以 `metadata.yaml` 为单一入口（含 `type` / `title` / `source_url` / `tags` / `topics` / `status` / `created` / `imported_at` / …），正文与中文译本与笔记在同目录的 `.md` 文件中。完整字段约束与每种 type 的必填项见 [docs/TAXONOMY.md](docs/TAXONOMY.md)。

---

## 9. Release-Backed Assets

`.mp4` / `.mp3` / 大二进制（秉烛游 MV / 字幕 / 海报 / 项目 demo 等）不进 git。流程：先把原文件上传到 GitHub Release，再在 KB 条目的 `metadata.yaml` 用 `asset_release_tag` / `asset_filename` 链接过来。完整策略与 `check_release_assets.py` 校验规则见 [docs/releases.md](docs/releases.md)。

---

## 10. 新电脑恢复

```bash
# 1. 克隆
git clone https://github.com/conanxin/hermes-knowledge-base
cd hermes-knowledge-base

# 2. 同步到当前稳定版本
git checkout v0.4.0-operator-ready-material-ingestion

# 3. 安装 Python 依赖（按需）
python3 -m pip install --user --break-system-packages pyyaml pymupdf requests beautifulsoup4

# 4. 跑 quick gate 确认环境干净
python3 scripts/run_full_gate.py --quick
```

恢复完成后所有日常命令从 [§5](#5-日常使用统一材料入口) 开始。

---

## 11. 详细文档导航

| 文档 | 何时打开 |
|---|---|
| [docs/OPERATOR_PLAYBOOK.md](docs/OPERATOR_PLAYBOOK.md) | **日常使用主手册**：daily import / WeChat / web / YouTube / PDF / release assets / gates / BLOCKED 参考 / git discipline / new-machine recovery |
| [docs/AGENT_COMMANDS.md](docs/AGENT_COMMANDS.md) | agent 任务规范：preflight / postflight / divergence 决策树 / tags-topics soft WARN policy / 各 material 完整 recipe |
| [docs/RELEASES.md](docs/RELEASES.md) | 版本历史 + 推荐下一版 |
| [docs/releases.md](docs/releases.md) | GitHub Release assets 索引（大文件） |
| [docs/TAXONOMY.md](docs/TAXONOMY.md) | metadata.yaml 字段约束 + 每种 type 的 schema |
| [docs/VERSIONING.md](docs/VERSIONING.md) | tag 规则 + 历史 duplicate 表 |
| [docs/REPORTING_TEMPLATE.md](docs/REPORTING_TEMPLATE.md) | 报告模板 |
| [docs/YOUTUBE_CAPABILITIES.md](docs/YOUTUBE_CAPABILITIES.md) | YouTube 能力公开文档 |
| [docs/commands/](docs/commands/) | 每种能力的命令短档 |
| [docs/workflows/](docs/workflows/) | 完整工作流（含 wechat troubleshoot） |
| [docs/import-recipes/](docs/import-recipes/) | 完整 recipe（PDF OCR / Gutenberg …） |
| [CHANGELOG.md](CHANGELOG.md) | 完整 changelog |

---

## 12. Releases

完整 release notes：[docs/RELEASES.md](docs/RELEASES.md) 与 [CHANGELOG.md](CHANGELOG.md)。

**近期里程碑：**

| 版本 | 主题 | 备注 |
|---|---|---|
| **v0.4.0** | **Operator-Ready Material Ingestion Baseline**（当前稳定） | 统一入口 + 全量门禁 + operator playbook + release assets policy 整合；tag `v0.4.0-operator-ready-material-ingestion`；详细见 `reports/operator_ready_material_ingestion_release_v0.4.0_20260702.md` |
| **v0.3.91** | **Material Ingestion Stable Baseline**（上一个稳定） | 微信公众号 / 普通网页 / YouTube / 本地 HTML·MD·TXT / 本地 PDF 全稳定；tag `v0.3.91-material-ingestion-stable-baseline` |
| **v0.3.96** | **Full Gate Runner + Tag SHA Sanity** | `run_full_gate.py` 统一入口；`check_release_tags` 显式纳入；tag `v0.3.96-full-gate-runner-and-tag-sanity` |
| v0.3.92 | 秉烛游 MV assets（GitHub Release） | `.mp4` / `.mp3` / 大二进制走 Release；tag `v0.3.92-bingzhu-you-mv-assets` |
| v0.3.90 | PDF smoke 修复 | `pdf_to_kb.py --import` 不再调用 `update_site.py`；`run_pdf_import_smoke.py` 26 → 33 checks |
| v0.3.86 | PDF / 本地文档 KB 导入路线 | PyMuPDF；扫描版 BLOCKED |
| v0.3.84 | Fetch-result handoff + inbox overwrite 保护 | 避免 429 退化；inbox 低 rank 拒绝覆盖 |
| v0.3.83 | YouTube provider 环境可选补齐 | `yt-dlp` + `youtube-transcript-api` |
| v0.3.81–82 | YouTube fetch quality gate + automatic transcript providers | full / partial / metadata_only |
| v0.3.79 | YouTube transcript-gated KB import | 统一入口 `youtube_url` |
| v0.3.77 | 普通网页文章入库 | 统一入口 `generic_web_url` |
| v0.3.76 | 统一材料入库路由器 | `material_to_kb.py` 起点 |
| v0.3.71 | 微信公众号批量入库 + 三层去重 | `wechat_batch_import.py` |
| v0.3.69 | 微信公众号 URL 直接入库通道 | `wechat_url_to_kb.py`（公开 URL + 本地文件兜底） |
| v0.3.68 | local divergence 治理 + tags/topics soft-WARN policy |  |
| v0.3.65 | README-only entrypoint refresh（首次） |  |

---

*Last refreshed for v0.4.1 README operator-ready rewrite on 2026-07-02.*