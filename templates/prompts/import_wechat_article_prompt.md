# 微信公众号文章入库（导入流程提示模板）

## 🚨 硬规则：路由判定

**本节是导入流程的第一道门，必须在所有其他动作之前读完并应用。**

### 触发语 → 目标仓库映射

| 用户消息包含 | 唯一正确目标 | 绝对禁止 |
|------------|-------------|---------|
| 「把这篇公众号文章加入 Hermes 知识库」 / 「入库这篇公众号文章」 / 「保存这篇公众号全文到知识库」 | `~/hermes-knowledge-base` | ❌ 创建 standalone project / 专题页 / 独立 GitHub Pages 项目 / 修改 `~/conanxin.github.io/projects/data.json` |
| 都不包含 | —— | ❌ 默认猜；必须用 clarify 反问 |

### 正确输出结构

**KB 路线**（唯一正确路线）：

```
~/hermes-knowledge-base/content/articles/YYYY/YYYY-MM-DD-wechat-<account-slug>-<title-slug>/
├── metadata.yaml         # 含 content_kind, source_platform, dedupe_key, wechat, capture 字段
├── source.md             # 原文完整
├── translation.zh-CN.md  # 清洗后的中文正文（V1 可与 source.md 一致）
├── summary.md            # 摘要 + 关键论点
├── notes.md              # 关键摘记 + 我的想法 + 可延伸研究
└── raw_payload.json      # 原始 JSON 捕获包备份
```

### 禁止事项

- ❌ 不要把公众号文章做成 standalone project
- ❌ 不要创建独立项目页
- ❌ 不要修改 `conanxin.github.io/projects`
- ❌ 不要把半成品写入 `content/articles/`

---

## 触发条件

用户说以下任意表达时执行：

- "把这篇公众号文章加入 Hermes 知识库"
- "入库这篇公众号文章"
- "保存这篇公众号全文到知识库"

## 默认行为

| 参数 | 默认值 |
|------|--------|
| content_type | article |
| 语言 | zh-CN（中文原文） |
| 翻译语言 | zh-CN（V1 无需翻译，translation.zh-CN.md 为清洗后的正文） |
| 目录名格式 | YYYY-MM-DD-wechat-公众号-slug-标题-slug |
| content_kind | wechat_official_article |
| source_platform | wechat_official_account |
| tags/topics | 由 Hermes 根据内容自动判断 |
| commit & push | 自动执行（除非用户说"先不要 push"） |

## 执行流程

### 0. Preflight（强制）

**所有导入任务开始前必须先运行 preflight：**

```bash
cd ~/hermes-knowledge-base
git fetch origin
git pull --ff-only origin main
python3 scripts/check_task_preflight.py
```

**Preflight 结果处理：**

| 结果 | 处理方式 |
|------|----------|
| **PASS** | 继续执行导入 |
| **PASS_WITH_WARNINGS** | 仅当 warning 为已知非阻断项时可继续 |
| **FAIL** | **立即停止**，不得进入导入阶段 |

### 1. 读取公众号文章全文

- OpenClaw（通过 @tencent-weixin/openclaw-weixin）读取文章全文
- 生成 JSON 捕获包，包含：title, source_url, account_name, author, published_date, captured_at, content_markdown

### 2. 确认是否拿到全文

**Hard stop 条件（满足任意一条即停止）：**

- content_markdown 为空或空白
- content_markdown 长度 < 200 字符
- content_markdown 中文字符 < 50
- 内容包含截断标记（如"阅读全文"、"..."、"此内容因违规无法查看"）
- 内容只有摘要/导语，没有正文主体
- 内容需要登录或付费才能阅读完整内容
- 内容无法访问（404/403/500）

**处理方式：**
- 立即停止，向用户报告原因
- 不写入 `content/articles/` 任何文件
- 可选：将失败的捕获包保存到 `data/wechat-failures/`

### 3. 先保存 raw

在生成 KB 条目前，先保存原始 JSON 捕获包：

```bash
# 作为 raw_payload.json 保存到条目目录中
# 这是后续审计和重建的备份
```

### 4. 生成 KB 条目

运行导入脚本：

```bash
python3 scripts/import_wechat_article_capture.py <path-to-capture.json>
```

脚本自动生成：
- `metadata.yaml` — 含 content_kind、source_platform、dedupe_key、wechat、capture 字段
- `source.md` — 原文全文
- `translation.zh-CN.md` — 清洗后的中文正文
- `summary.md` — 自动摘要
- `notes.md` — 结构化笔记模板
- `raw_payload.json` — 原始 JSON 捕获包

**metadata.yaml 特殊字段：**

```yaml
content_kind: "wechat_official_article"
source_platform: "wechat_official_account"
dedupe_key: "wechat:<url-hash>:<title-slug>"
wechat:
  account_name: "公众号名称"
  url_params:
    __biz: "..."
capture:
  tool: "openclaw-weixin"
  captured_at: "2026-06-29T09:00:00"
  version: "1.0"
```

**word_count 要求：**
- `word_count.source` 和 `word_count.translation` 必须是整数
- 基于 source.md 和 translation.zh-CN.md 实际计算

### 5. 更新索引和站点

```bash
python3 scripts/update_site.py
```

### 6. 运行质量检查

```bash
python3 scripts/check_kb.py
python3 scripts/check_translation_residue.py
```

### 7. Commit & Push

```bash
git add <新增文件>
git commit -m "Add WeChat article: <title>"
git push origin main
```

### 8. 生成导入报告

按 REPORTING_TEMPLATE.md 输出任务报告，必须包含：
- 文章标题和来源
- 新增条目路径
- word_count
- dedupe_key
- commit hash
- push 结果

---

## 强制停止条件

以下情况 Hermes 必须停止导入，向用户报告，不要强行入库：

- URL 无法访问或返回 404/403/500
- content_markdown 为空或明显截断
- 文章只有摘要，没有正文主体
- 内容需要登录或付费才能阅读完整内容
- 内容中文字符极少（< 50），不是中文文章
- 文章已删除或违规无法查看
- metadata 关键字段无法确定（如 title、source_url 缺失）

## 禁止事项

- 不要修改 Hermes 源码
- 不要重启 hermes-gateway.service
- 不要安装新依赖（使用现有工具）
- 不要推送 GitHub 除非用户授权
- 不要发送 Telegram 消息
- 不要暴露 API key、token、secret
- **不要生成残缺入库结果（缺少文件、字段为 0、内容不完整）**
- **不要把公众号文章做成 standalone project**
- **不要创建独立项目页**
- **不要修改 conanxin.github.io/projects**

## 质量门禁（硬性规则）

1. `update_site.py` 已在最前面内置 `check_kb.py` 硬停止。如果 `check_kb.py` 返回 FAIL，`update_site.py` 立即返回非 0，**不会**运行 build / export / generate / sync。在 check 修复前**严禁**执行 commit / push。
2. `word_count` 字段必须是 YAML 对象，**不允许**用带引号的字符串或裸数字。规范格式：

   ```yaml
   word_count:
     source: 4434        # 整数
     translation: 7079   # 整数
   ```

   不允许：`word_count: 4500`、`word_count: "4500"`、`word_count: "~4500"`。
3. 发现 `content/` 下存在半成品条目时，必须先修复或隔离到 `inbox/quarantine/`，再继续执行 `update_site.py`。
4. 除非用户明确说"先不要 commit/push"，否则完整导入流程应自动运行到 check → update_site → commit → push；但当 check 失败时必须立即停止并报告。

## 完整流水线顺序

```
check_kb.py            ← 质量门禁，FAIL 立即停止
build_index.py
export_site_data.py
generate_item_pages.py
sync_pages_docs.py
```

---

## 微信中可用的短命令

| 命令 | 说明 |
|------|------|
| "把这篇公众号文章加入 Hermes 知识库" | 完整命令，导入到 KB |
| "入库这篇公众号文章" | 简短命令，同上 |
| "保存这篇公众号全文到知识库" | 强调全文，同上 |

---

*Prompt 模板固化完成。可直接复制到 Agent 上下文中使用。*
