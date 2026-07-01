# WeChat URL Direct KB Import — v0.3.69

- **任务标签**: `v0.3.69-wechat-url-direct-kb-import`
- **创建时间**: 2026-07-01
- **STATUS**: **PASS**
- **commit message**: `Add direct WeChat URL KB import workflow`

---

## §1 STATUS

**PASS**

新增"只给一个公众号链接就能自动入库"的通道（`scripts/wechat_url_to_kb.py`），并兼容本地 HTML/Markdown/TXT 兜底。所有质量门禁通过，工作树只含本任务相关文件。

---

## §2 Scope（新增能力说明）

为 Hermes Knowledge Base 增加一条**不依赖 OpenClaw** 的微信公众号文章入库通道：

1. **公开 URL 直抓**：`scripts/wechat_url_to_kb.py --url <mp.weixin.qq.com 链接>` 用浏览器 UA 公开抓取页面，解析标题/公众号名/作者/发布时间/正文/封面/摘要，转 Markdown，生成标准 capture JSON。
2. **本地文件兜底**：`--html-file` / `--markdown-file` / `--text-file`，解析同样的字段。
3. **下游入库**：capture JSON 交给既有 `scripts/import_wechat_article_capture.py`，在 `content/articles/YYYY/YYYY-MM-DD-wechat-<account>-<title>/` 下生成 6 文件 KB 条目。
4. **硬停止**：抓不到完整正文 / 登录墙 / 截断 / 拦截 / 标题正文不对应 / `check_kb.py` 失败 → 退出码 1，只生成报告，不写半成品。
5. **结构化摘要 + 笔记**：增强 `import_wechat_article_capture.py` 的 `summary.md` / `notes.md` 生成器，覆盖 9 个分析小节（一句话总结 / 核心问题 / 主要观点 / 论证结构 / 关键概念 / 背景补充 / 摘录句子 / KB 已有条目关联 / 个人阅读提示），启发式填充可从正文提取的部分，解释性内容留给 WorkBuddy / 读者补全。
6. **中文兼容**：`translation.zh-CN.md` 对中文原文做"清洗 WeChat 页脚后镜像 source"的兼容处理，满足 schema 又不丢内容，`check_kb.py` 不因"中文无需翻译"失败。

**硬约束遵守**：不登录微信、不扫码、不读 cookie、不绕过微信访问限制、不启用 `openclaw-weixin`、不 force push、不 `git add -A`、不写半成品、不把公众号文章做成 `project`、不创建 `conanxin.github.io/projects` 页面。

---

## §3 Actions（修改文件列表）

### 新增

| 文件 | 说明 |
|------|------|
| `scripts/wechat_url_to_kb.py` | URL/本地文件 → capture JSON → 调用 import 脚本的主入口 |
| `docs/commands/wechat-url-kb-import-command.md` | 新命令短档 |
| `tests/fixtures/wechat_sample_article.html` | 离线测试用公众号 HTML fixture |

### 修改

| 文件 | 说明 |
|------|------|
| `scripts/import_wechat_article_capture.py` | 增强 `generate_summary_md` / `generate_notes_md`，覆盖 9 段分析结构；新增 `_split_paragraphs` / `_extract_key_sentences` / `_extract_headings` / `_infer_core_concepts` 辅助函数 |
| `docs/workflows/wechat-article-kb-import-workflow.md` | 升级到 v1.1：新增"v1.1 公开 URL 直抓 + 本地文件兜底"章节、输入/前置条件/最短提示词/关联文档更新 |
| `docs/AGENT_COMMANDS.md` | 新增 §2d「微信公众号 URL 直接入库流程（v0.3.69+）」 |
| `README.md` | §6 表格、§7「公众号」两通道拆分、changelog 加 v0.3.69 行、最后刷新日期更新 |

---

## §4 新增脚本用法

```bash
# 公开 URL（推荐入口）
python3 scripts/wechat_url_to_kb.py --url "<mp.weixin.qq.com 链接>" --dry-run
python3 scripts/wechat_url_to_kb.py --url "<mp.weixin.qq.com 链接>" --import

# 本地 HTML（链接抓不到时的兜底）
python3 scripts/wechat_url_to_kb.py --html-file  <path/to/article.html> --import

# 本地 Markdown
python3 scripts/wechat_url_to_kb.py --markdown-file <path/to/article.md> --import

# 本地纯文本
python3 scripts/wechat_url_to_kb.py --text-file <path/to/article.txt> --import
```

**WorkBuddy 短命令**：

```
解读并入库这篇公众号文章：
<mp.weixin.qq.com 链接>
```

```
解读并入库这个公众号文章本地文件：
<本地 html/md/txt 路径>
```

---

## §5 支持的输入方式

| 输入 | 支持 | 说明 |
|------|------|------|
| 公开 `mp.weixin.qq.com` URL | ✅ | 浏览器 UA 公开抓取；不登录、不扫码、不读 cookie |
| 本地 HTML | ✅ | 浏览器另存的完整 HTML |
| 本地 Markdown | ✅ | 带 / 不带 frontmatter 均可（`标题:` `公众号:` 等键值自动识别） |
| 本地 TXT | ✅ | 纯文本，按空行分段 |
| OpenClaw capture JSON | ✅（既有） | 走 `wechat_inbound_to_capture.py` / `import_wechat_article_capture.py`，本次未改动 |

### 仍然不支持的情况

- 需要登录微信才能查看的文章（环境限制，硬停止）
- 微信对公开访问做了反爬拦截的文章（硬停止，绝不绕过）
- 只在微信客户端内可见、外部抓不到全文的文章（硬停止）
- 付费 / 隐藏 / 已删除的文章（硬停止）
- 扫码关注后才能阅读全文的文章（硬停止）

遇到以上情况，脚本提示：

> 这个链接无法直接抓全文，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。

---

## §6 full-text failure behavior

当 `--url` 抓取失败时，`wechat_url_to_kb.py` 退出码 1，**不写任何 KB 条目**，不写 capture JSON 之外的中间产物，stderr 输出：

```
HARD STOP: <具体原因>
这个链接无法直接抓全文，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。
```

下游 `import_wechat_article_capture.py` 自身也有独立的硬停止（exit 1）：正文 < 200 字 / CJK < 50 / 段落 < 3 / 命中截断标记 / 命中阻断短语 / 标题正文无 CJK 重叠。两层硬停止叠加，保证不会写入半成品条目。

---

## §7 EVIDENCE — 测试命令和结果

### 最小测试（不需要真实抓微信）

```bash
# 1. fixture dry-run（生成 capture JSON + import 脚本 dry-run 校验）
python3 scripts/wechat_url_to_kb.py --html-file tests/fixtures/wechat_sample_article.html --dry-run
# → STATUS: DRY_RUN_OK  (exit 0)

# 2. 对生成的 capture JSON 再跑一次 import 脚本 dry-run
python3 scripts/import_wechat_article_capture.py --dry-run <上一步生成的 capture.json>
# → STATUS: DRY_RUN_OK  (exit 0)
```

两条命令在本机均 `STATUS: DRY_RUN_OK` / exit 0。fixture 解析出：标题「测试公众号文章：知识管理与长期主义」、公众号「测试知识公众号」、作者「辛测试」、发布日期「2026-06-30」、正文 1140 字符。

### 实际写入验证（仅用于验证 pipeline，已清理）

为确认 `--import` 真的能写 KB 条目，临时跑了一次 `--html-file <fixture> --import`，在 `content/articles/2026/2026-06-30-wechat-测试知识公众号-测试公众号文章知识管理与长期主义/` 下生成了完整 6 文件，`check_kb.py` 此时显示 `PASS: 55`。**验证完成后已删除该测试条目与对应 capture JSON**，恢复到 54 条基线，工作树只含本任务文件。

---

## §8 质量门禁结果

| 顺序 | 命令 | 结果 | 备注 |
|------|------|------|------|
| 1 | `python3 -m py_compile scripts/*.py` | **PASS** | 所有脚本字节码编译通过 |
| 2 | `python3 scripts/check_kb.py` | **PASS** | 54/54 items，0 FAIL |
| 3 | `python3 scripts/update_site.py` | **PASS（环境 WARNING）** | exit 0；但见下方"环境说明" |
| 4 | `python3 scripts/audit_kb_state.py` | **PASS_WITH_WARNINGS** | 0 HARD FAIL，24 WARN（全部是既有条目的 topics/tags 软范围超限，与本次无关） |
| 5 | `python3 scripts/check_pages_sync.py` | **PASS** | 54 slugs 全部 site↔docs 字节一致 |

### 环境说明：update_site.py 在 Windows 下的既有 bug

`scripts/generate_item_pages.py`（被 `update_site.py` 调用）在 Windows 上把所有记录判为"non-content path"并 skip，最终生成 0 个 item 页，进而把既有 54 个 `site/items/*/index.html` 和 `docs/items/*/index.html` 全部删除。根因是该脚本的"content path"过滤在 Windows 反斜杠路径（`content\articles\...`）下失效——**这是仓库既有的 Windows 兼容 bug，与本次任务无关**（本次未改动 `generate_item_pages.py` / `update_site.py`）。在仓库的规范 Linux 环境下 `content/articles/...` 路径正常，update_site 不会删页。

**处理**：我已 `git checkout --` 还原 update_site 产生的全部删除与 catalog 变更，工作树只保留本任务的 7 个文件。还原后 `check_pages_sync.py` 仍 PASS（54 slugs 字节一致）。**本次 commit 不包含 update_site 的环境性删页**。

### 生成的示例 capture JSON 路径

fixture dry-run 生成的示例 capture JSON 路径（已清理，不入仓）：

```
inbox/raw/wechat/2026-06-30-测试公众号文章知识管理与长期主义.json
```

schema 与 `inbox/raw/wechat/2026-06-29-isls-2026-cached.json` 兼容，字段：`title` / `source_url` / `account_name` / `author` / `published_date` / `captured_at` / `content_markdown` / `cover_url` / `digest`。

### 是否真实导入文章

**否**。本次只验证了 pipeline（dry-run + 一次临时 `--import` 后立即清理），没有把任何真实公众号文章永久入库。fixture 文章是测试用途，不入 `content/articles/`。

---

## §9 Commit / Push

- **commit message**: `Add direct WeChat URL KB import workflow`
- **commit 方式**: 逐文件 `git add`（未使用 `git add -A`）
- **commit hash**: 见最终回复 `COMMIT` 字段
- **push**: `git push origin main`，结果见最终回复 `PUSH` 字段
- **tag**: 未创建 tag（任务名为 `v0.3.69-wechat-url-direct-kb-import`，按仓库惯例 tag 由 release 流程单独处理；preflight 确认 `v0.3.69` 为下一个可用 minor）

---

## §10 Preflight

任务开始前执行：

```bash
git fetch origin main --tags
python3 scripts/check_task_preflight.py --planned-tag v0.3.69-wechat-url-direct-kb-import --classify-dirty --json
```

结果：
- `git_repo`: PASS
- `git_status`: PASS（working tree clean，无非本任务 dirty 改动）
- `head_sync`: PASS（HEAD 与 `origin/main` 一致，`ahead=0 behind=0`，无分叉）
- `tag_available`: PASS（`v0.3.69` 未被占用，且 `check_release_tags.py` 推荐 `v0.3.69` 为下一个 minor）
- `check_release_tags` / `check_kb` / `check_pages_sync` / `check_tracks`：preflight 内部调用因使用 WindowsApps `python3` stub 误报 FAIL；用 managed Python 直接运行均 PASS（详见 §8）

**无分叉、无非本任务 dirty 改动 → 未 BLOCKED，按计划执行。**

---

## §11 下一步建议

1. **WorkBuddy 接入**：把"解读并入库这篇公众号文章：`<url>`"这条短命令在 WorkBuddy 侧映射到 `scripts/wechat_url_to_kb.py --url <url> --import`，并在入库后让 WorkBuddy 补全 `summary.md` / `notes.md` 里的"（请人工补充）"解释性小节。
2. **真实链接回归**：挑 1-2 篇公开可抓的公众号文章做端到端回归，确认 `--url --import` 在真实微信页面结构下能解析出完整正文（fixture 只覆盖了已知结构）。
3. **修 `generate_item_pages.py` 的 Windows 路径 bug**（独立任务）：让 `update_site.py` 在 Windows 下也能正确生成 item 页，避免每次都要手动还原。本次未动该脚本（超出本任务范围）。
4. **去重**：`import_wechat_article_capture.py` 已生成 `dedupe_key`，可在入库前先扫 `content/articles/` 检测重复，命中则提示而非覆盖。
5. **多文章批量**：支持一次给多个链接 / 多个本地文件，循环入库。

---

## §12 关联文档

- 命令短档：`docs/commands/wechat-url-kb-import-command.md`
- 完整工作流：`docs/workflows/wechat-article-kb-import-workflow.md`
- Agent 命令总纲：`docs/AGENT_COMMANDS.md` §2d
- 入口脚本：`scripts/wechat_url_to_kb.py`
- 基线脚本：`scripts/import_wechat_article_capture.py`
- 测试 fixture：`tests/fixtures/wechat_sample_article.html`
