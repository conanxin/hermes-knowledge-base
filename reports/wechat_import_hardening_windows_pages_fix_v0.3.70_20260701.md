# WeChat Import Hardening + Windows Item Pages Fix — v0.3.70

- **任务标签**: `v0.3.70-wechat-import-hardening-and-windows-pages-fix`
- **创建时间**: 2026-07-01
- **STATUS**: **PASS**
- **commit message**: `Fix WeChat import metadata and Windows item page generation`

---

## §1 STATUS

**PASS**

修复了 v0.3.69 暴露的三个问题：

1. **Windows 路径分隔符 bug**：`generate_item_pages.py` / `export_site_data.py` / `build_index.py` 在 Windows 下用反斜杠路径 `content\articles\...`，导致 `path.startswith("content/")` 判断失败，生成 0 个 item 页面并删除既有页面。现已统一转为 POSIX 路径，Windows 和 Linux 行为一致。
2. **公众号 topics/tags 误判**：徒步文章因图片 URL 含 `/AI/` 被误判为"人工智能"。现已让推断只基于 `extract_visible_text()` 清洗后的可见文本，且"人工智能/AI"只认明确语义关键词（人工智能/大模型/LLM/ChatGPT 等），不再认裸 "AI" 子串。
3. **word_count drift**：`count_words_mixed` 原本把图片 URL、Markdown 链接目标里的英文 token 也算进正文词数，导致中文文章 drift 32.9%。现已先 `extract_visible_text()` 清洗再计数，drift 降到 3.2%。

`check_pages_sync.py` 也增加了第 3 段"content→items 完整性检查"，能直接发现 content/ 里有条目但 site/items 或 docs/items 缺详情页的情况——这正是上一轮被 Windows bug 遮蔽的失败模式。

---

## §2 修复的问题

### 问题 1：Windows 路径分隔符 bug（任务 A）

**根因**：
- `scripts/build_index.py` 第 71 行 `ordered["path"] = str(rel_path.parent)` 在 Windows 上产生 `content\articles\2026\xxx`。
- `scripts/export_site_data.py` 第 89 行 `path.startswith("content/")` 对反斜杠路径返回 False，导致所有记录的 `detail_url` 为空。
- `scripts/generate_item_pages.py` 第 1222 行 `path_str.startswith("content/")` 同样返回 False，导致所有记录被 skip，生成 0 个 item 页面。
- `slug_from_path()` 用 `split("/")` 在反斜杠路径上拿不到正确的最后一段。

**修复方式**（统一转 POSIX）：
- `build_index.py`：`ordered["path"] = rel_path.parent.as_posix()` —— 从源头输出 POSIX 路径。
- `export_site_data.py`：`slug_from_path()` 先 `path.replace("\\", "/")` 再 split；`content/` 前缀检查也先 `posix_path = path.replace("\\", "/")`。
- `generate_item_pages.py`：`slug_from_path()` 同上；`content/` 前缀检查用 `posix_path = path_str.replace("\\", "/")`。
- `check_pages_sync.py`：新增第 3 段 `check_content_completeness()`，扫 `content/**/metadata.yaml` 得到期望 slug 集合，与 site/items 和 docs/items 对比，缺失即报 FAIL。

**不改 Linux 行为**：POSIX 路径在 Linux 上 `replace("\\","/")` 是 no-op（Linux 路径不含反斜杠），`as_posix()` 在 Linux 上等价于 `str()`。

### 问题 2：公众号 topics/tags 误判（任务 B）

**根因**：`infer_topics` / `infer_tags` 直接在 `title + content[:2000]` 上做 `if kw in text`，而 content 里包含大量 `![](https://mmbiz.qpic.cn/.../AI/...)` 图片 URL——裸 "AI" 子串命中了"人工智能"关键词列表里的 "AI"。

**修复方式**：
- 新增 `extract_visible_text(text)`：用正则剥除 HTML 标签、Markdown 图片/链接（保留 alt/label 文本）、裸 URL、`src=/href=` 属性、base64 data URI。
- `infer_topics` / `infer_tags` 改为对 `extract_visible_text(...)` 的结果做关键词匹配。
- "人工智能" / "AI" 标签的关键词列表收紧为明确语义词：`人工智能 / 大模型 / 生成式 AI / 生成式AI / LLM / ChatGPT / Claude / OpenAI / AI agent / 机器学习 / 深度学习 / 神经网络 / GPT-4 / GPT-5 / 语言模型 / prompt engineering / 提示工程`。删掉裸 "AI"。
- 新增"户外"和"自然地理"主题域：`徒步 / 户外 / 登山 / 爬升 / 穿越 / 山脊 / 古道 / 营地 / 补给 / 导航 / 越野 / hiking`、`山脉 / 海拔 / 草甸 / 峡谷 / 河谷 / 森林 / 湖泊 / 地貌 / 地理 / 自然 / 生态 / 植被 / 气候`。
- `infer_tags` 同样新增 `徒步 / 户外 / 京郊 / 路线` 标签桶。

### 问题 3：word_count drift（任务 C）

**根因**：`count_words_mixed` 用 `re.findall(r"[a-zA-Z]+", text)` 数英文 token，而图片 URL 里的 `mmbiz / qpic / cn / jpg / wx_fmt / appmsg` 全被算成英文词，导致中文文章 word_count 虚高。

**修复方式**：
- `count_words_mixed` 改为先 `extract_visible_text(text)` 清洗，再数 CJK 字符 + 长度 ≥ 2 的英文 token（跳过单字符噪声）。
- 对"两步路"文章重新计算并修正 `metadata.yaml` 的 `word_count`：source 4589 → 3208，translation 4589 → 3208。drift 从 32.9% 降到 3.2%（3107 CJK vs 3208 声明，差 101 个英文 token，正常）。
- **没有放宽 `check_kb.py` 的 5% drift 阈值**——修复完全在生成侧。

### 问题 4：check_pages_sync 完整性（任务 A 第 5 点）

**根因**：`check_pages_sync.py` 只比较 site/items 和 docs/items 是否互相一致，不检查 content/ 里的条目是否都有对应详情页。所以即便 generate_item_pages 生成了 0 个页面、site 和 docs 都是 0 个 slug，它也会报 PASS。

**修复方式**：新增第 3 段 `check_content_completeness()`，从 `content/**/metadata.yaml` 推导期望 slug 集合，与 site/items 和 docs/items 对比。任一侧缺即 FAIL。

---

## §3 修改文件列表

### 修改

| 文件 | 说明 |
|------|------|
| `scripts/build_index.py` | `ordered["path"]` 改用 `rel_path.parent.as_posix()`，从源头输出 POSIX 路径 |
| `scripts/export_site_data.py` | `slug_from_path()` + `content/` 前缀检查统一转 POSIX |
| `scripts/generate_item_pages.py` | `slug_from_path()` + `content/` 前缀检查统一转 POSIX |
| `scripts/check_pages_sync.py` | 新增第 3 段 content→items 完整性检查；报告从 [1/2][2/2] 变 [1/3][2/3][3/3] |
| `scripts/import_wechat_article_capture.py` | 新增 `extract_visible_text()`；`count_words_mixed` 改为基于可见文本；`infer_topics`/`infer_tags` 改为基于可见文本 + 收紧 AI 关键词 + 新增户外/自然地理域 |
| `content/articles/2026/2026-06-30-wechat-两步路-北京热门徒步线路top10/metadata.yaml` | `word_count.source/translation` 4589 → 3208（修正 drift） |
| `docs/data/catalog.json` | 路径转为 POSIX + 含新条目 |
| `site/data/catalog.json` | 同上（site 镜像） |
| `index/catalog.jsonl` | 路径转为 POSIX |

### 新增

| 文件 | 说明 |
|------|------|
| `tests/fixtures/wechat_sample_hiking_article.html` | 合成徒步文章 fixture，HTML 里故意放图片 URL 含 `/AI/`，验证不被误判 |
| `tests/run_smoke_tests.py` | 3 项 smoke 测试：AI 陷阱、import 消费、pages_sync 完整性 |
| `docs/items/2026-06-30-wechat-两步路-北京热门徒步线路top10/index.html` | 两步路文章详情页（docs 镜像） |
| `site/items/2026-06-30-wechat-两步路-北京热门徒步线路top10/index.html` | 两步路文章详情页（site 源） |

---

## §4 Windows 路径修复方式

统一规则：**所有写入 catalog/index 的路径字段都用 POSIX 风格（正斜杠），所有读取 catalog/index 做字符串比较的代码都先 `.replace("\\", "/")` 归一化**。

| 位置 | 修复前 | 修复后 |
|------|--------|--------|
| `build_index.py` L71 | `str(rel_path.parent)` → `content\articles\...`（Windows） | `rel_path.parent.as_posix()` → `content/articles/...` |
| `export_site_data.py` slug_from_path | `path.split("/")[-1]` | `path.replace("\\","/").split("/")[-1]` |
| `export_site_data.py` content/ 检查 | `path.startswith("content/")` | `posix_path = path.replace("\\","/"); posix_path.startswith("content/")` |
| `generate_item_pages.py` slug_from_path | 同上 | 同上 |
| `generate_item_pages.py` content/ 检查 | `path_str.startswith("content/")` | `posix_path = path_str.replace("\\","/"); posix_path.startswith("content/")` |

Linux 行为不变：Linux 路径不含反斜杠，`replace("\\","/")` 是 no-op，`as_posix()` 等价于 `str()`。

---

## §5 topics/tags 修复方式

```
extract_visible_text(text):
  1. 删 HTML 标签 <img...> <a href>...</a>
  2. Markdown 链接/图片 [text](url) / ![alt](url) → 只保留 text/alt
  3. 删裸 URL https://... ftp://...
  4. 删 src="..." href="..." data-src="..." 属性片段
  5. 删 base64 data URI
  返回: 仅含可见散文的文本
```

- `infer_topics` / `infer_tags` 都先调 `extract_visible_text` 再做关键词匹配。
- "人工智能" / "AI" 关键词列表收紧为明确语义词，删掉裸 "AI"。
- 新增"户外"/"自然地理"主题域 + "徒步"/"户外"/"京郊"/"路线"标签桶。

**验证**（hiking fixture，HTML 里图片 URL 含 `/AI/`）：
- 修复前：topics = `['人工智能']`，tags 含 `'AI'`
- 修复后：topics = `['科技', '历史', '户外', '自然地理']`，tags = `['写作', '徒步', '户外', '路线', '京郊', '微信', '合成测试公众号']` —— 不含 人工智能/AI ✅

---

## §6 word_count 修复方式

```
count_words_mixed(text):
  visible = extract_visible_text(text)
  cjk = count_cjk_chars(visible)
  english_words = len(re.findall(r"[a-zA-Z]{2,}", visible))  # 跳过单字符
  return cjk + english_words
```

**对"两步路"文章的修正**：
- 修复前：source=4589, translation=4589, 实际 CJK=3079, drift=32.9%（WARN）
- 修复后：source=3208, translation=3208, 实际 CJK=3107, drift=3.2%（< 5%，无 WARN）✅

**没有放宽 `check_kb.py` 的 5% drift 阈值**——修复完全在生成侧。

---

## §7 新增 fixture / smoke 说明

### Fixture: `tests/fixtures/wechat_sample_hiking_article.html`

合成徒步文章（非真实公众号全文，无版权问题），HTML 里故意放两张图片，URL 含 `/AI/` 子串：
```html
<img src="https://mmbiz.qpic.cn/mmbiz_jpg/AI/trap_hiking_photo_001.jpg" ...>
<img src="https://mmbiz.qpic.cn/mmbiz_jpg/AI/trap_hiking_photo_002.jpg" ...>
```
正文含徒步/路线/爬升/轨迹/古道/海拔/草甸等户外词汇。预期：topics 含 户外/自然地理，不含 人工智能。

### Smoke 脚本: `tests/run_smoke_tests.py`

3 项离线 smoke 测试，无需网络：

1. **AI 陷阱**：`wechat_url_to_kb.py --html-file <hiking fixture> --dry-run` 生成 capture，`infer_topics`/`infer_tags` 不含 人工智能/AI，且含户外/徒步域。
2. **import 消费**：`import_wechat_article_capture.py --dry-run <capture.json>` 退出 0 且输出 `STATUS: DRY_RUN_OK`。
3. **pages_sync 完整性**：`check_pages_sync.py` 报告含 `[3/3] Content→items completeness` 段。

运行：`python3 tests/run_smoke_tests.py` → `ALL SMOKE TESTS PASSED (3/3)`。

---

## §8 "两步路"文章详情页

修复前（v0.3.69）：该文章在 catalog 里但 generate_item_pages 在 Windows 下生成了 0 个页面，详情页缺失，check_pages_sync 报 54 slugs（因为只比 site↔docs 一致性，没发现缺页）。

修复后（v0.3.70）：
- `docs/items/2026-06-30-wechat-两步路-北京热门徒步线路top10/index.html` ✅ 已生成
- `site/items/2026-06-30-wechat-两步路-北京热门徒步线路top10/index.html` ✅ 已生成
- check_pages_sync 从 54 slugs → 55 slugs ✅

---

## §9 数量统计

| 计数项 | v0.3.69 | v0.3.70 |
|--------|---------|---------|
| content/ metadata.yaml | 55 | 55 |
| docs/items/ slugs | 54 | **55** ✅ |
| site/items/ slugs | 54 | **55** ✅ |
| check_pages_sync synced slugs | 54 | **55** ✅ |

---

## §10 执行过的命令和结果

| 命令 | 结果 |
|------|------|
| `python3 -m py_compile scripts/*.py` | PASS |
| `python3 scripts/check_kb.py` | PASS (55/55, 0 FAIL, 0 WARN) |
| `python3 scripts/update_site.py` | PASS（生成 55 个 item 页面，无删除） |
| `python3 scripts/audit_kb_state.py` | PASS_WITH_WARNINGS (0 HARD FAIL, 24 WARN 均为既有条目 topics/tags 软范围) |
| `python3 scripts/check_pages_sync.py` | PASS（55 slugs site↔docs 一致 + content→items 完整性通过） |
| `python3 tests/run_smoke_tests.py` | ALL SMOKE TESTS PASSED (3/3) |
| `python3 scripts/wechat_url_to_kb.py --html-file tests/fixtures/wechat_sample_hiking_article.html --dry-run` | STATUS: DRY_RUN_OK |
| `python3 scripts/import_wechat_article_capture.py --dry-run <capture.json>` | STATUS: DRY_RUN_OK |

---

## §11 git diff 摘要

```
9 files changed, 726 insertions(+), 540 deletions(-)
+ 4 new entries (hiking fixture, smoke script, 两步路 item pages ×2)
```

主要改动：
- `scripts/build_index.py`：1 行（as_posix）
- `scripts/export_site_data.py`：slug_from_path + content/ 检查转 POSIX
- `scripts/generate_item_pages.py`：slug_from_path + content/ 检查转 POSIX
- `scripts/check_pages_sync.py`：+85 行（第 3 段完整性检查）
- `scripts/import_wechat_article_capture.py`：+135 行（extract_visible_text + infer 重写 + count_words_mixed 重写）
- `content/articles/.../metadata.yaml`：word_count 4589 → 3208
- `docs/data/catalog.json` + `site/data/catalog.json` + `index/catalog.jsonl`：路径转 POSIX

---

## §12 Commit / Push

- **commit message**: `Fix WeChat import metadata and Windows item page generation`
- **commit 方式**: 逐文件 `git add`（未用 `git add -A`）
- **commit hash**: 见最终回复 `COMMIT` 字段
- **push**: `git push origin main`，结果见最终回复 `PUSH` 字段
- **force push**: 无
- **tag**: 未创建 tag

---

## §13 Preflight

任务开始前：
- `git fetch origin main --tags`：成功
- 当前分支：main，与 origin/main 同步（HEAD = 600637f）
- `check_task_preflight.py --planned-tag v0.3.70-... --classify-dirty --json`：`git_divergence.is_synced = true`，工作树 clean，无分叉、无非本任务 dirty

---

## §14 下一步建议

1. **Linux 端验证**：本次在 Windows 完成，建议在 Linux 环境跑一次 `update_site.py` 确认 POSIX 路径修复不改变 Linux 行为（预期无变化）。
2. **更多领域关键词**：当前只补了户外/自然地理两域，后续可按入库文章主题逐步扩充（音乐/艺术/科学/医学等）。
3. **`infer_topics`/`infer_tags` 升级为 LLM 推断**：启发式关键词表的覆盖终归有限，长期建议在 `--import` 后由 WorkBuddy 用 LLM 基于全文重新推断 topics/tags，覆盖更准。
4. **word_count 进一步精确**：当前 `count_words_mixed` 对中英混排文章仍是 CJK + 英文词之和，若需要更严格的"可见字符数"可改为只数 CJK + 英文词（不含标点/数字），但需同步调整 check_kb.py 的 drift 阈值语义。
5. **item 页面增量更新**：当前 `generate_item_pages.py` 每次全量重生成 55 个页面，量大后可能变慢；可考虑只重生成变化的条目（基于 metadata.yaml mtime）。
