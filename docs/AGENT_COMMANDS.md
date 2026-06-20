# Hermes Knowledge Base 短命令约定

本文档定义了用户与 Hermes agent 交互时的短命令规则。当用户以特定格式发出指令时，Hermes 默认执行预设的完整工作流，无需追问。

---

## 触发短命令的句式

以下任意句式均触发文章导入流程：

- "把这篇文章完整翻译并加入知识库：【URL】"
- "入库并完整翻译：【URL】"
- "加入知识库：【URL】"
- "翻译后入库：【URL】"

其中 【URL】可以是：
- 单个 URL
- 多个 URL（以空格或换行分隔）

---

## 默认执行流程

触发后，Hermes 默认执行 `templates/prompts/import_article_prompt.md` 中定义的完整流程：

1. 抓取正文（web_extract → browser fallback）
2. 保存 `source.md`
3. 完整准确翻译为 `translation.zh-CN.md`
4. 生成 `summary.md`
5. 生成 `metadata.yaml`
6. 生成 `notes.md`
7. 处理必要 `assets/`（图片等）
8. 更新索引（`scripts/build_index.py`）
9. 运行检查（`scripts/check_kb.py`）
10. `git add -A && git commit -m "Add [文章标题] article"`
11. `git push origin main`
12. 输出导入报告

---

## 默认参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `content_type` | `article` | 内容类型 |
| `翻译语言` | `zh-CN` | 简体中文 |
| `commit message` | 自动生成 | `Add [文章标题] article` |
| `目录名` | 自动 | `YYYY-MM-DD-来源-slug` |
| `tags` | 自动 | Hermes 根据内容判断 |
| `topics` | 自动 | Hermes 根据内容判断 |
| `status` | `imported` | 导入状态 |

---

## 不追问的情况（直接执行）

以下情况 Hermes **不需要追问**，直接执行：

- URL 可正常访问
- 页面是标准文章（blog post、news article、essay）
- 内容可完整抓取
- 用户给了单个 URL
- 用户没有写"先不要 push"或"先不要 commit"

---

## 必须追问的情况

以下情况 Hermes **必须追问** 用户，确认后再执行：

| 情况 | 追问内容 |
|------|----------|
| URL 无法访问 | "该 URL 无法访问，请确认链接是否正确" |
| 无法判断内容类型 | "该页面看起来是视频/论文/书籍/GitHub 项目，是否仍按文章导入？" |
| 需要登录或付费墙 | "该页面需要登录或付费，是否继续？" |
| 正文明显不完整 | "抓取到的内容似乎不完整（仅 X 字），是否继续？" |
| 多个 URL 未说明 | "您提供了 X 个 URL，是否全部导入？" |
| 用户明确阻止 | "您写了'先不要 push/commit'，是否暂存本地？" |

---

## 覆盖默认行为

用户可以通过以下方式覆盖默认参数：

| 指令 | 效果 |
|------|------|
| "content_type: paper" | 按论文导入（检查 abstract、references 等） |
| "content_type: book" | 按书籍导入（检查 chapters 等） |
| "tags: AI, 机器学习" | 指定标签 |
| "topics: 技术, 研究" | 指定主题 |
| "先不要 push" | 执行到 commit 为止，不 push |
| "先不要 commit" | 执行到生成文件为止，不 commit |
| "翻译为英文" | 输出 `translation.en.md` 而非 `translation.zh-CN.md` |

---

## 示例

### 示例 1：标准导入

用户：把这篇文章完整翻译并加入知识库：https://arun.is/blog/jr-logo/

Hermes：直接执行完整导入流程，无需追问。

### 示例 2：多个 URL

用户：加入知识库：
https://example.com/article1
https://example.com/article2

Hermes：追问 "您提供了 2 个 URL，是否全部导入？"

### 示例 3：付费墙

用户：翻译后入库：https://example.com/paywalled-article

Hermes：追问 "该页面需要付费访问，是否继续？"

### 示例 4：覆盖参数

用户：把这篇文章加入知识库：https://example.com/ai-paper，content_type: paper，tags: 深度学习

Hermes：按论文导入流程执行，使用指定标签。

---

## 相关文件

- `templates/prompts/import_article_prompt.md` — 完整导入流程模板
- `scripts/check_kb.py` — 知识库完整性检查
- `scripts/build_index.py` — 索引构建
- `README.md` — 项目说明
