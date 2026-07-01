# wechat-url-kb-import

> **命令名称**: `wechat-url-kb-import`
> **用途**: 只给一个 `mp.weixin.qq.com` 链接（或本地另存的 HTML / Markdown / TXT 文件），就自动完成"抓取正文 → 解析 → 生成 capture JSON → 入库 → 校验"全流程
> **Workflow**: [`docs/workflows/wechat-article-kb-import-workflow.md`](../workflows/wechat-article-kb-import-workflow.md)
> **入口脚本**: `scripts/wechat_url_to_kb.py`
> **下游脚本**: `scripts/import_wechat_article_capture.py`
> **创建时间**: 2026-07-01
> **版本**: 1.0
> **任务标签**: `v0.3.69-wechat-url-direct-kb-import`

---

## 一句话说明

输入一个公众号链接（或本地另存的文章文件），自动抓取公开页面、解析标题/作者/正文、生成标准 capture JSON，并把它变成 `content/articles/YYYY/` 下的知识库条目。**不登录、不扫码、不读 cookie、不绕过微信访问限制。**

---

## 最短调用方式（推荐）

在 WorkBuddy 里直接说：

```
解读并入库这篇公众号文章：
<mp.weixin.qq.com 链接>
```

WorkBuddy 会把它翻译成：

```bash
python3 scripts/wechat_url_to_kb.py --url "<mp.weixin.qq.com 链接>" --import
```

并按 [`wechat-article-kb-import-workflow.md`](../workflows/wechat-article-kb-import-workflow.md) 完成：capture → 入库 → `check_kb.py` → `update_site.py` → commit / push。

---

## 本地文件兜底命令

如果链接抓不到全文（见下方"硬停止条件"），在浏览器里把文章另存为 HTML / Markdown / TXT，然后对 WorkBuddy 说：

```
解读并入库这个公众号文章本地文件：
<本地 html/md/txt 路径>
```

WorkBuddy 会翻译成下面四选一：

```bash
# HTML（推荐，能保留最多结构）
python3 scripts/wechat_url_to_kb.py --html-file  <path/to/article.html> --import

# Markdown
python3 scripts/wechat_url_to_kb.py --markdown-file <path/to/article.md> --import

# 纯文本
python3 scripts/wechat_url_to_kb.py --text-file <path/to/article.txt> --import
```

---

## 脚本支持的完整参数

```bash
python3 scripts/wechat_url_to_kb.py \
    (--url <mp.weixin.qq.com 链接> | --html-file <path> | --markdown-file <path> | --text-file <path>) \
    [--dry-run | --import] \
    [--out <capture.json 显式输出路径>] \
    [--timeout <秒>]
```

| 参数 | 必填 | 说明 |
|------|------|------|
| `--url` | 四选一 | 公众号文章公开链接（必须是 `mp.weixin.qq.com` 域名） |
| `--html-file` | 四选一 | 浏览器另存的完整 HTML |
| `--markdown-file` | 四选一 | 本地 Markdown 文件 |
| `--text-file` | 四选一 | 本地纯文本文件 |
| `--dry-run` | 默认 | 只生成 capture JSON 并跑 import 脚本的 `--dry-run`，**不写知识库条目** |
| `--import` | 可选 | 生成 capture JSON 并真的写入 `content/articles/YYYY/` 下的 KB 条目 |
| `--out` | 可选 | 显式指定 capture JSON 输出路径（默认 `inbox/raw/wechat/YYYY-MM-DD-<slug>.json`） |
| `--timeout` | 可选 | URL 抓取超时秒数，默认 20 |

> 既不传 `--dry-run` 也不传 `--import` 时，默认走 `--dry-run`（安全优先）。

---

## 输入要求

| 参数 | 必填 | 说明 |
|------|------|------|
| 公众号链接 / 本地文件 | ✅ | 必须能拿到**完整正文**（不是摘要、不是登录墙） |
| 目标仓库 | ❌ | 默认脚本所在仓库就是 `hermes-knowledge-base` |

---

## 输出目录规则

**Capture JSON**（中间产物，可被 `wechat_inbound_to_capture.py` 复用）：
```
inbox/raw/wechat/YYYY-MM-DD-<title-slug>.json
```

**知识库条目**（由 `import_wechat_article_capture.py` 写入）：
```
content/articles/YYYY/YYYY-MM-DD-wechat-<account-slug>-<title-slug>/
```

> 注意：**只做 `article`，不做 `project`，不创建 `conanxin.github.io/projects` 页面。**

---

## 输出文件清单

每个 KB 条目固定 6 个文件：

| 文件 | 说明 |
|------|------|
| `metadata.yaml` | 元数据（含 `content_kind: wechat_official_article`、`source_platform: wechat_official_account`、`dedupe_key`、`wechat`、`capture` 字段） |
| `source.md` | 原文全文（Markdown） |
| `translation.zh-CN.md` | 中文正文（中文原文按 schema 兼容处理：清洗 WeChat 页脚后镜像 source，保证 `check_kb.py` 不因"中文无需翻译"而失败） |
| `summary.md` | 结构化摘要，包含 9 个分析小节（一句话总结 / 核心问题 / 主要观点 / 论证结构 / 关键概念 / 背景补充 / 值得摘录的句子 / 与 KB 已有条目的可能关联 / 个人阅读提示）。脚本用启发式填充可从正文提取的部分，解释性内容留给 WorkBuddy 补全 |
| `notes.md` | 结构化阅读笔记（接受 / 反思 / 联想 / 行动 + 摘录 + 关键概念 + 结构 + 提醒 + 阅读提示） |
| `raw_payload.json` | 原始 capture JSON 完整备份 |

---

## 硬停止条件（HARD STOP，不写半成品条目）

出现以下任一情况，脚本退出码为 1，只生成报告，**不写 KB 条目**：

- 获取不到完整正文
- 页面要求登录 / 扫码
- 页面只返回摘要
- 正文明显截断（命中 `... / 阅读全文 / 前往阅读` 等截断标记）
- 只有标题没有正文
- 微信拦截公开访问（命中"请在微信客户端打开"等阻断短语）
- 无法确认文章标题和正文对应（标题里的 CJK 字符在正文里一个都没出现）
- `check_kb.py` 失败

遇到硬停止时，脚本会提示：

> 这个链接无法直接抓全文，请在浏览器中另存为 HTML / Markdown / TXT 后再交给 WorkBuddy。

---

## 前置条件

1. ✅ `hermes-knowledge-base` 仓库已 clone，且 remote 指向 `conanxin/hermes-knowledge-base`
2. ✅ 仓库状态 clean（无未提交的非本任务改动）
3. ✅ Python 环境有 `requests` + `beautifulsoup4`（仅 `--url` / `--html-file` 路径需要；`--markdown-file` / `--text-file` 只用标准库）
4. ❌ **不需要** OpenClaw `@tencent-weixin/openclaw-weixin`（本命令是 OpenClaw 之外的"公开抓取 + 本地文件兜底"通道）

---

## 最小测试（无需真实抓微信）

```bash
# 1. 用 fixture 跑 dry-run（生成 capture JSON + import 脚本 dry-run 校验）
python3 scripts/wechat_url_to_kb.py --html-file tests/fixtures/wechat_sample_article.html --dry-run

# 2. 直接对生成的 capture JSON 再跑一次 import 脚本的 dry-run
python3 scripts/import_wechat_article_capture.py --dry-run <上一步生成的 capture.json>
```

两条命令都应输出 `STATUS: DRY_RUN_OK` / `STATUS: PASS`。

---

## 与既有命令的关系

| 命令 | 输入 | 适用场景 |
|------|------|----------|
| `wechat-article-kb-import`（旧） | OpenClaw 读取的 capture JSON | OpenClaw 启用时 |
| **`wechat-url-kb-import`（本命令）** | 公众号 URL 或本地文件 | OpenClaw 不可用 / 想直接给链接 |
| `pdf-ocr-kb-import` | 本地 PDF | PDF 资料 |
| `youtube-kb-import` | YouTube 链接 | 视频字幕入库 |

---

## 注意事项

- 本命令**只抓公开页面**。微信对部分文章做了反爬限制，遇到拦截就 HARD STOP，绝不绕过。
- `translation.zh-CN.md` 对中文原文做"清洗后镜像 source"的兼容处理，既满足 schema 又不丢失内容；`word_count.translation` 与 `word_count.source` 接近是正常现象。
- WorkBuddy 在跑完 `--import` 后，建议人工或 LLM 把 `summary.md` / `notes.md` 里的"（请人工补充）"小节补全——脚本只搭了结构骨架。
