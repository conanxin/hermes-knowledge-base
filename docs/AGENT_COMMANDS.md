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
- check_translation_residue.py 无严重残留（suspicious_count < 20）
- metadata.yaml 字段完整（含 title_zh, source_site, language, translation_language, word_count）
- word_count.source > 0 且 word_count.translation > 0
- notes.md 使用统一模板

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
