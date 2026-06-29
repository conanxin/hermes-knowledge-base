# wechat-article-kb-import

> **命令名称**: `wechat-article-kb-import`
> **用途**: 一键把微信公众号文章全文加入 Hermes Knowledge Base
> **Workflow**: `wechat-article-kb-import-workflow.md`
> **基线脚本**: `scripts/import_wechat_article_capture.py`
> **创建时间**: 2026-06-29
> **版本**: 1.0

---

## 一句话说明

基于 OpenClaw 读取的微信公众号文章全文捕获包，自动完成知识库入库、索引更新和站点发布。

---

## 最短调用方式

```
把这篇公众号文章加入 Hermes 知识库
```

或在微信中直接转发文章并说：

```
入库这篇公众号文章
```

---

## 标准调用方式

```
请按照 wechat-article-kb-import-workflow.md 把这篇公众号文章加入知识库：
<path-to-capture.json>

目标仓库：~/hermes-knowledge-base
```

---

## 输入要求

| 参数 | 必填 | 说明 |
|------|------|------|
| `JSON 捕获包` | ✅ | OpenClaw 读取的公众号文章全文，包含 title、source_url、account_name、author、published_date、captured_at、content_markdown |
| `目标仓库` | ❌ | 默认 `~/hermes-knowledge-base` |

---

## 输出目录规则

**知识库条目**：
```
content/articles/YYYY/YYYY-MM-DD-wechat-<account-slug>-<title-slug>/
```

**示例**：
```
content/articles/2026/2026-06-29-wechat-晚点latepost-标题/
```

---

## 输出文件清单

### 知识库条目（6 个）

| 文件 | 说明 |
|------|------|
| `metadata.yaml` | 知识库元数据（含 content_kind, source_platform, dedupe_key, wechat, capture 字段） |
| `source.md` | 原文全文（保留原始 markdown） |
| `translation.zh-CN.md` | 清洗后的中文正文（V1 可与 source.md 一致） |
| `summary.md` | 文章摘要（自动提取 + 待补充） |
| `notes.md` | 结构化笔记模板（接受/反思/联想/行动） |
| `raw_payload.json` | 原始 JSON 捕获包（完整备份） |

---

## 成功案例路径

**基线脚本**: `scripts/import_wechat_article_capture.py`（v1.0）

**示例条目**：
```
content/articles/2026/2026-06-29-wechat-测试公众号-测试公众号文章标题/
```

---

## 前置条件

1. ✅ OpenClaw 已接入 @tencent-weixin/openclaw-weixin（能读取公众号全文）
2. ✅ Hermes Knowledge Base 仓库已 clone（`~/hermes-knowledge-base`）
3. ✅ 仓库状态 clean（无未提交修改）

---

## 注意事项

| 规则 | 说明 |
|------|------|
| ❌ 不做成 standalone project | 公众号文章只入 KB，不做独立项目页 |
| ❌ 不修改 conanxin.github.io/projects | 不创建或修改 projects 页面 |
| ❌ 内容不完整时 hard stop | 截断/空内容/仅摘要 → 不写入 |
| ❌ 不 force push | 正常推送 |
| ❌ 不暴露绝对路径 | 公开文章中不写 `/home/ubuntu` 等路径 |
| ⚠️ 仓库 dirty 时 BLOCKED | 存在非本任务相关未提交改动时停止 |
| ✅ 检查脚本失败时 BLOCKED | 任何检查失败都不 commit |

---

## 失败处理

| 场景 | 处理 |
|------|------|
| 内容不完整 | HARD STOP，记录原因，建议检查文章状态 |
| 仓库 dirty | BLOCKED，报告未提交文件，建议 stash 后重试 |
| check_kb.py 失败 | BLOCKED，记录错误，建议修复后重试 |
| update_site.py 失败 | BLOCKED，记录错误 |
| push 失败 | BLOCKED，记录错误，建议检查网络和权限 |

---

## 关联文档

| 文档 | 路径 |
|------|------|
| 完整 Workflow 文档 | `docs/workflows/wechat-article-kb-import-workflow.md` |
| 本命令说明 | `docs/commands/wechat-article-kb-import-command.md` |
| 导入 Prompt | `templates/prompts/import_wechat_article_prompt.md` |

---

## 快捷调用示例

```
# 最短调用（微信中直接说）
把这篇公众号文章加入 Hermes 知识库

# 标准调用
请按照 wechat-article-kb-import-workflow.md 把这篇公众号文章加入知识库：
<path-to-capture.json>

# 指定仓库
请把这篇公众号文章加入知识库：
<path-to-capture.json>
目标仓库：~/my-knowledge-base
```

---

## 与通用 article-import 的区别

| 维度 | 通用 article-import | wechat-article-kb-import |
|------|---------------------|--------------------------|
| 来源 | 任意网页 URL | 微信公众号文章 |
| 输入 | URL | JSON 捕获包 |
| 语言 | 通常为英文 → 翻译为中文 | 中文原文，V1 无需翻译 |
| content_kind | 默认 | `wechat_official_article` |
| dedupe_key | 无 | 基于 URL + title 生成 |
| raw_payload | 无 | 保存 `raw_payload.json` |

---

*命令文档固化完成。可直接复制调用示例使用。*
