# 完整翻译并加入知识库（导入流程提示模板）

## 🚨 硬规则：路由判定（v0.4+ 新增，2026-06-25）

**本节是导入流程的第一道门，必须在所有其他动作之前读完并应用。**

### 触发语 → 目标仓库映射（不允许自由发挥）

| 用户消息包含 | 唯一正确目标 | 绝对禁止 |
|------------|-------------|---------|
| 「加入知识库」 / 「入库」 / 「完整翻译并加入知识库」 / 「翻译后入库」 / 「KB」 | `~/hermes-knowledge-base` | ❌ 创建 standalone project / 专题页 / 独立 GitHub Pages 项目 / 修改 `~/conanxin.github.io/projects/data.json` |
| 「做成专题页」 / 「生成独立项目」 / 「发布成项目页」 / 「加入 projects 页面」 | `~/conanxin.github.io/projects/<slug>/` | ❌ 顺手入库 KB（用户没说要入库） |
| 都不包含 | —— | ❌ 默认猜；必须用 `clarify` 工具反问 |

### 正确输出结构

**KB 路线**（默认 / 推荐）：

```
~/hermes-knowledge-base/content/articles/YYYY-MM-DD-<source>-<slug>/
├── metadata.yaml         # 完整 schema + word_count + related_project_url (可选)
├── source.md             # 原文完整
├── translation.zh-CN.md  # 中文翻译完整
├── summary.md            # 摘要 + 关键人物/概念 + 延伸问题
└── notes.md              # 关键摘记 + 我的想法 + 可延伸研究 + 待确认问题
```

**Project 路线**（仅在用户明确说"做成专题页"等时）：

```
~/conanxin.github.io/projects/<slug>/
├── index.html
├── styles.css
├── app.js
└── content/             # 可选
```

### Wrong route 检测（每个输出完成后必跑）

```python
# 在最终回复之前，Hermes 必须自检：
output_url = "..."  # 你即将输出的最终 URL
user_input = "..."  # 用户原始消息

is_kb_route = any(kw in user_input for kw in ["加入知识库", "入库", "KB", "翻译后入库"])
is_project_route = any(kw in user_input for kw in ["专题页", "独立项目", "项目页", "projects 页面"])

if is_kb_route and "/projects/" in output_url:
    raise WrongRouteError("用户说加入知识库，但输出 /projects/ URL → wrong route")
if is_project_route and "/hermes-knowledge-base/items/" in output_url and "同时加入知识库" not in user_input:
    raise WrongRouteError("用户只要专题页，但顺手入了 KB → 越权")
```

### Wrong route 恢复流程（标准动作）

1. **不删除**已生成的 standalone project（用户可能在线访问）
2. **立即停止**后续 push / commit
3. **生成 wrong route 报告**到 `~/.hermes/workspace/reports/cloud_hermes_wrong_route_<date>_<slug>.md`
4. **补做 KB 入库**到 `~/hermes-knowledge-base/content/articles/YYYY-MM-DD-<source>-<slug>/`，在 metadata.yaml 加：
   ```yaml
   related_project_url: "https://conanxin.github.io/projects/<slug>/"
   related_project_note: "上一轮误生成但保留的专题页（wrong route 标杆案例）"
   ```
5. **跑完整门禁**：`check_kb.py` → `update_site.py` → `check_pages_sync.py` → `check_translation_residue.py` → 全 PASS
6. **commit + push 两条路线**，commit message 注明 "wrong route" / "after wrong route recovery"
7. **不修改** `~/conanxin.github.io/projects/data.json`（standalone project 不属于 projects grid）
8. **最终回复**：显式说明上一轮是 wrong route + 已补做 KB 入库 + 输出正确的 KB 详情页 URL

### 历史案例（防止再犯）

- ❌ 2026-06-24 Yarvin 文章：用户说"加入知识库"，却生成了 `~/conanxin.github.io/projects/yarvin-moldbug-cn/` standalone project + 修改了 `projects/data.json`。本节硬规则就是为防止再犯而设。

---

## 触发条件

用户说以下任意表达时执行：

- "把这篇文章完整翻译并加入知识库：URL"
- "入库并完整翻译：URL"
- "加入知识库：URL"
- "翻译后入库：URL"

## 默认行为

| 参数 | 默认值 |
|------|--------|
| content_type | article |
| 翻译语言 | zh-CN |
| 目录名格式 | YYYY-MM-DD-来源-slug |
| tags/topics | 由 Hermes 根据内容自动判断 |
| commit & push | 自动执行（除非用户说"先不要 push"） |

## 执行流程

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

## 强制停止条件

以下情况 Hermes 必须停止导入，向用户报告，不要强行入库：

- URL 无法访问或返回 404/403/500
- 正文抓取不完整（明显截断、缺少关键章节）
- 文章需要登录或付费才能阅读完整内容
- 内容类型不明确（无法判断是文章、论文、评论等）
- 翻译后英文残留严重（suspicious_count ≥ 20）
- metadata 关键字段无法确定（如作者、标题缺失）

## 禁止事项

- 不要修改 Hermes 源码
- 不要重启 hermes-gateway.service
- 不要安装新依赖（使用现有工具）
- 不要推送 GitHub 除非用户授权
- 不要发送 Telegram 消息
- 不要暴露 API key、token、secret
- **不要生成残缺入库结果（缺少文件、字段为 0、翻译不完整）**

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

## 完整流水线顺序（更新于 v0.3.8+）

```
check_kb.py            ← 质量门禁，FAIL 立即停止
build_index.py
export_site_data.py
generate_item_pages.py
sync_pages_docs.py
```
