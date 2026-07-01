# Real WeChat URL Import Test — 北京热门徒步线路TOP10

- **任务**: 用 v0.3.69 新增的 `wechat_url_to_kb.py` 真实入库一篇公众号文章
- **执行时间**: 2026-07-01
- **STATUS**: **PASS**
- **commit message**: `Import WeChat article: 北京热门徒步线路TOP10`

---

## §1 STATUS

**PASS**

用 `scripts/wechat_url_to_kb.py --url ... --import` 成功抓取并入库了一篇真实公众号文章。公开抓取、解析、capture JSON 生成、KB 条目写入、质量门禁全通过。

---

## §2 文章信息

| 字段 | 值 |
|------|------|
| 标题 | 北京热门徒步线路TOP10！ |
| 公众号 | 两步路 |
| 作者 | 两步路线路 |
| 发布日期 | 2026-06-30 |
| 原文链接 | https://mp.weixin.qq.com/s/GkZeHHlEUUXXutxPckcrPg |
| 正文长度 | 14036 字符 |
| 抓取方式 | 公开 URL 直抓（浏览器 UA，不登录、不扫码、不读 cookie） |

---

## §3 执行步骤

### Step 1: 公开抓取 + dry-run

```bash
python3 scripts/wechat_url_to_kb.py --url "https://mp.weixin.qq.com/s/GkZeHHlEUUXXutxPckcrPg" --dry-run
```

结果：抓取成功，解析出标题/公众号/作者/发布日期/正文 14036 字符，dry-run 校验通过。

### Step 2: 真实入库

```bash
python3 scripts/wechat_url_to_kb.py --url "https://mp.weixin.qq.com/s/GkZeHHlEUUXXutxPckcrPg" --import
```

结果：在 `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/` 下生成 6 文件 KB 条目。

### Step 3: 人工修正与解读补全

脚本用启发式填充的 topics/tags 不准确（把徒步文章误判为"人工智能"），手动修正为：
- topics: 户外 / 徒步 / 北京 / 京郊 / 自然地理
- tags: 两步路 / 徒步 / 北京 / 京郊 / 户外 / 徒步线路 / 公众号

`summary.md` 和 `notes.md` 从脚本骨架补全为完整分析，覆盖 9 段：
- 一句话总结 / 核心问题 / 主要观点 / 论证结构 / 关键概念 / 背景补充 / 摘录句子 / KB 关联 / 阅读提示
- notes.md 额外含：接受 / 反思 / 联想 / 行动

### Step 4: 质量门禁

| 命令 | 结果 | 备注 |
|------|------|------|
| `check_kb.py` | **PASS** (55/55) | 1 WARN: word_count.translation drift 32.9%（中英混排，CJK+English word 计数 vs 纯 CJK 计数差异，WARN-only 不阻断） |
| `update_site.py` | **PASS** (exit 0) | catalog/index 已更新含新条目；item 页面因 Windows 路径 bug 已还原（见 §5） |
| `audit_kb_state.py` | **PASS_WITH_WARNINGS** | 0 HARD FAIL, 24 WARN（均为既有条目 topics/tags 软范围超限，与本次无关） |
| `check_pages_sync.py` | **PASS** | 54 slugs site↔docs 字节一致 |

### Step 5: Commit + Push

逐文件 `git add`（未用 `git add -A`），commit message `Import WeChat article: 北京热门徒步线路TOP10`，push 到 origin/main。

---

## §4 修改文件列表

### 新增

| 文件 | 说明 |
|------|------|
| `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/metadata.yaml` | KB 条目元数据 |
| `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/source.md` | 原文 Markdown 全文 |
| `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/translation.zh-CN.md` | 中文正文（兼容镜像） |
| `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/summary.md` | 结构化摘要（9 段，已补全分析） |
| `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/notes.md` | 阅读笔记（接受/反思/联想/行动，已补全） |
| `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/raw_payload.json` | 原始 capture JSON 备份 |
| `inbox/raw/wechat/2026-06-30-北京热门徒步线路top10-2.json` | 中间产物 capture JSON |
| `reports/wechat_real_import_test_北京热门徒步线路top10_20260701.md` | 本报告 |

### 修改（update_site.py 产出的 catalog/index 更新）

| 文件 | 说明 |
|------|------|
| `docs/data/catalog.json` | 新增条目入目录 |
| `site/data/catalog.json` | 同上（site 镜像） |
| `index/catalog.jsonl` | 同上 |
| `index/authors.md` | 作者索引 |
| `index/tags.md` | 标签索引 |
| `index/timeline.md` | 时间线索引 |

---

## §5 环境说明：update_site.py 的 Windows bug

`scripts/generate_item_pages.py`（被 `update_site.py` 调用）在 Windows 反斜杠路径下把所有记录判为"non-content path"并 skip，生成 0 个 item 页，进而把既有 54 个 `site/items/*/index.html` 和 `docs/items/*/index.html` 全部删除。这是仓库既有的 Windows 兼容 bug（规范 Linux 环境无此问题），与本次任务无关。

**处理**：已 `git checkout --` 还原 108 个 item 页面删除；保留 catalog/index 的合法更新（含新条目）。新条目的 item 页面在 Linux 环境下重新运行 `update_site.py` 即可生成。

---

## §6 下一步建议

1. **在 Linux 环境重跑 `update_site.py`**：为新条目生成 item 页面（Windows 下 generate_item_pages.py 有路径 bug）。
2. **修 `generate_item_pages.py` 的 Windows 路径 bug**（独立任务）：让路径过滤兼容 `\` 和 `/`。
3. **改进 `infer_topics` / `infer_tags` 启发式**：当前对非科技类文章（如户外/徒步）会误判为"人工智能"——建议在 `import_wechat_article_capture.py` 里扩充领域关键词表，或让 WorkBuddy 在 `--import` 后自动修正 topics/tags。
4. **word_count.translation 计数优化**：当前 `count_words_mixed` 把图片 URL 里的英文 token 也计入，导致 CJK 文章的 word_count 偏高；可考虑只统计正文文字、跳过 markdown 链接/图片 URL。
