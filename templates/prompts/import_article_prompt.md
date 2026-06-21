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

1. 如果 `check_kb.py` 返回 FAIL，**严禁**执行 commit/push。
2. 如果 `check_kb.py` 返回 FAIL，**严禁**将失败条目同步到 `docs/data/catalog.json`。
3. `article` 的 `word_count` 必须是纯数字（例如 4500），**严禁**使用 "~4500"、"约4500"、"4.5k" 等字符串形式。
4. 发现 `content/` 下存在半成品条目时，必须先修复或隔离到 `inbox/quarantine/`，再继续执行 `update_site.py`。
5. 除非用户明确说“先不要 commit/push”，否则完整导入流程应自动运行到 check → update_site → commit → push；但当 check 失败时必须立即停止并报告。
## 质量门禁（硬性规则）

1. 如果 `check_kb.py` 返回 FAIL，**严禁**执行 commit/push。
2. 如果 `check_kb.py` 返回 FAIL，**严禁**将失败条目同步到 `docs/data/catalog.json`。
3. `article` 的 `word_count` 必须是纯数字（例如 4500），**严禁**使用 "~4500"、"约4500"、"4.5k" 等字符串形式。
4. 发现 `content/` 下存在半成品条目时，必须先修复或隔离到 `inbox/quarantine/`，再继续执行 `update_site.py`。
5. 除非用户明确说“先不要 commit/push”，否则完整导入流程应自动运行到 check → update_site → commit → push；但当 check 失败时必须立即停止并报告。
