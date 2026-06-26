# 长名单文章导入规则（Listicle Import Rules）

> **状态**: v1.0 — 2026-06-26 固化
> **来源案例**: Paste Magazine「The 100 greatest songs of the 1960s」(commit `725b7a9`)
> **触发**: 任何包含「Top N / Best N / Greatest N / 排名 / listicle / #100 等编号结构」的文章
> **适用范围**: `~/hermes-knowledge-base` KB 导入流程,以及任何外部 agent 导入类似文章

## 为什么需要这些规则

2026-06-26 导入 Paste「The 100 greatest songs of the 1960s」时,**实际只覆盖了 #100–#51 共 50 首歌**。翻译过程中曾出现:

1. **编号错位**: web_extract 截断在 #89,我基于截断版继续翻译,导致 #76–#66 共 11 首歌的中文 H2 标题编号全部错位。
2. **缺失**: #75 Led Zeppelin 完全缺失。
3. **凭空捏造**: #74 出现了一首原文根本不存在的「The Staple Singers」段落。
4. **重复条目**: 修复过程中留下了 8 个重复 H2,需 dedup 清理。

**核心教训**: 长名单文章的 **「完整解析 source.md」必须在翻译之前完成**,不能边译边猜。翻译后必须做结构对齐检查。

---

## 1. 长名单文章识别

当文章**标题或结构**包含以下任一特征时,必须按 `long_list_article` 处理:

### 1.1 标题特征

| 标题模式 | 英文示例 | 中文示例 |
|---|---|---|
| Top N | "Top 100 essays", "Top 50 films" | 「100 大文章」 |
| Best N | "Best 100 songs" | 「100 首最佳歌曲」 |
| Greatest N | "Greatest albums of all time" | 「史上最伟大专辑」 |
| N [items] of [time period] | "25 books of 2024", "50 films of the decade" | 「2024 年 25 本书」 |
| All-time / Definitive lists | "The definitive 100", "All-time ranking" | 「权威排名」 |
| 排名 / 榜单 | "Billboard Hot 100", 「豆瓣 Top 250」 | |

### 1.2 结构特征

| 结构信号 | 含义 |
|---|---|
| 编号标题 (`#100 / #99 / #98 …`) | 排名型 listicle |
| 重复模式 (`## N. Artist: "Song"`) | 枚举型 listicle |
| 多页拆分 ("page 1 of 3", "continued on page 2") | 序列型 listicle |
| 「Top X」+ 文章中提到「see also / 详见 page 2」 | 分页型 listicle |

**识别时机**: 在 `web_extract` 返回结果**之后、翻译开始之前**做一次结构预检(见 §3)。

---

## 2. 长名单文章必须先完整解析 source.md

### 2.1 强约束

> **不得基于截断版 web_extract 开始翻译。**

`web_extract` 对长文章(>5000 chars)会自动截断,这是它的设计行为不是 bug。如果直接基于 web_extract 截断版开始翻译,会:

- 把截断当作「内容到此为止」,但原文其实还有几十个 H2
- 在不知道后续 H2 是什么的情况下主观填充内容
- 编号错位 + 缺失 + 凭空捏造

### 2.2 正确的获取路径

按 `kb-import-e2e-workflow` 的 fallback chain:

1. **首选 `web_extract`** — 仅作为「文章存在、内容可读」的预检,不能作为翻译源
2. **必须 `curl` + 解析 HTML** — 长名单文章**必须**走这一步,因为它没有 5000-char 截断
   ```bash
   curl -sL -x socks5://127.0.0.1:7898 \
     -A "Mozilla/5.0 ..." \
     "https://..." -o /tmp/source.html
   ```
3. **解析 HTML → markdown**:
   - 找 body 容器(`<article>` / `<div class="entry-content">` / `<div class="scroll-article-container">` / Substack `<div class="body markup">`)
   - 切到正确边界(`<aside>` / `<footer>` / SubscribeWidget / comment root)
   - 按 H2 切片,逐节提取文本
4. **保存为 source.md** — 这是**唯一**可信赖的翻译源

---

## 3. 翻译前必须做结构预检

在 `translation.zh-CN.md` 写第一行之前,**必须**对 source.md 完成以下检查:

### 3.1 计数检查

```python
import re
with open('source.md', 'r', encoding='utf-8') as f:
    src = f.read()
h2 = re.findall(r'^## (\d+)\. ', src, re.M)
print(f"H2 entries: {len(h2)}")
print(f"Numbers: {sorted([int(n) for n in h2], reverse=True)}")
```

预期输出(以 Paste 文章为例):
```
H2 entries: 50
Numbers: [100, 99, 98, ..., 52, 51]
```

### 3.2 编号连续性检查

```python
nums = sorted([int(n) for n in h2], reverse=True)
expected = list(range(max(nums), min(nums) - 1, -1))
if nums != expected:
    print(f"GAP DETECTED: expected {expected}, got {nums}")
```

如果出现 gap(如 `[100, 99, 97, 96, …]` — 缺 98):**必须查 source HTML 找出缺失编号对应的 H2 内容**,而不是凭空跳号。

### 3.3 重复检查

```python
from collections import Counter
c = Counter(nums)
dupes = [(n, k) for n, k in c.items() if k > 1]
if dupes:
    print(f"DUPLICATE NUMBERS: {dupes}")
```

重复编号意味着 source HTML 本身有结构问题 — 必须用 `<h2 id="...">` 或上下文区分,而不是任选一个删掉。

### 3.4 分页范围记录

如果文章说「Part 1 of 3」「Top 10 on page 3」「continued in next post」:

```python
# 在 source.md 顶部加 HTML 注释
<!-- Coverage: this page covers #100-#51 (50 entries) -->
<!-- Series: this is page 1 of 3 in the 100-songs series -->
<!-- Top 10 (#50-#1) are on a separate page and NOT covered -->
```

**绝对不得**假装已覆盖全部分页。Paste 那次的 #50-#1 在 page 3 上,本次只导入 #100-#51,**必须在 metadata 和 summary 中显式说明**。

---

## 4. 翻译后必须做结构对齐

### 4.1 Hard-Stop 检查

`source.md` 和 `translation.zh-CN.md` 的 **编号标题必须一一对应**。如果出现以下任一情况,**立即 hard-stop,不得 commit/push**:

- 错位(#76 在 translation 里出现为 #75 的内容)
- 缺号(50 个 source H2,翻译只有 49 个)
- 重复(翻译里某个编号出现两次)
- 凭空捏造(翻译里有 source 完全不存在的 H2)

### 4.2 对齐检查脚本

```python
import re
def h2_set(path):
    with open(path) as f:
        md = f.read()
    return {int(n): t for n, t in re.findall(r'^## (\d+)\. (.+?)$', md, re.M)}

src = h2_set('source.md')
tr = h2_set('translation.zh-CN.md')

assert set(src.keys()) == set(tr.keys()), \
    f"NUMBER MISMATCH: source={set(src.keys())-set(tr.keys())}, translation={set(tr.keys())-set(src.keys())}"

# Then check song names (handle ASCII vs curly quotes)
for n in src:
    src_song = src[n].split(':')[0].strip().lower()
    tr_song = tr[n].split(':')[0].strip().lower()
    if src_song[:8] not in tr_song:
        print(f"#{n} MISMATCH: src={src[n][:50]}, tr={tr[n][:50]}")
```

### 4.3 修复策略(如果发现错位)

1. **不删改 source.md** — source 是 ground truth
2. **从 source.md 重新提取错位编号对应的原始段落**
3. **用 `patch` 工具精确替换 translation.zh-CN.md 的错位段落**,保留正确的部分
4. **dedup**: 扫描整个 translation 文件,删除重复 H2(可能是修复过程的残留)
5. **重新跑 4.2 的对齐脚本** — 必须 50/50 通过
6. **在 notes.md 中记录修复过程** — 不掩盖错误,留下教训

---

## 5. metadata / summary.md 必须记录 coverage_scope

### 5.1 metadata.yaml 必填字段

长名单文章的 `metadata.yaml` 必须包含:

```yaml
# 覆盖范围(原文分多页时强制)
coverage_scope: "rank_100_to_51_only"     # 例:覆盖 #100-#51
is_partial_series: true                   # true=是系列文章的一部分

# 系列文章的相关链接(若有)
series_info:
  total_parts: 3
  this_part: 1
  covered_range: "rank_100_to_51"
  remaining_parts:
    - part: 2
      url: "https://..."
      covered_range: "rank_50_to_11"
    - part: 3
      url: "https://..."
      covered_range: "rank_10_to_1"
```

### 5.2 summary.md 必填段

长名单文章的 `summary.md` 必须包含一段 **「覆盖范围」**(Coverage Scope) 说明:

```markdown
## 覆盖范围

**本文范围**: 第 #100 至 #51 名,共 50 首歌曲
**原文分页**: 本次只涵盖第 1 页(共 3 页)
**未涵盖部分**:
- 第 #50 至 #11 名(第 2 页)
- 第 #10 至 #1 名(第 3 页,即 Top 10)

**完整系列 URL**: https://...
```

### 5.3 报告(report)必填段

`~/.hermes/workspace/reports/cloud_hermes_kb_e2e_import_<date>_<slug>.md` 必须包含:

```markdown
## Coverage scope

| Metric | Value |
|---|---|
| Source article total | 100 songs |
| This import covers | #100-#51 (50 songs) |
| Series pages | 1 of 3 |
| Remaining songs | #50-#1 (50 songs on 2 separate pages) |
```

---

## 6. Residue Warning 对长名单文章的解读

### 6.1 现状

`check_translation_residue.py` 是基于「连续英文片段」(≥3 词,长度 ≥15)的检测。**音乐 / 影视 / 书单类文章的 residue 数天然高**,因为:

- 每首歌都有英文歌名(2-5 词)
- 每个艺人都有英文名(2-3 词)
- 每个专辑都有英文名(1-5 词)
- 这些都是不可译的专名,必须保留

### 6.2 历史数据参考

| 文章类型 | 典型 suspicious_count | 解释 |
|---|---|---|
| 单篇评论文 | 2-10 | 普通人名 + 少量术语 |
| 长名单(50+ 歌曲 / 书籍 / 影视) | 50-150 | 50+ 专名 × 出现频率 |
| 学术综述 | 10-25 | 学术术语 + 引文 |

### 6.3 判定规则

**对长名单文章,residue warning 不直接阻断 commit**。但必须在 `metadata.yaml` 的 `translation_notes` 字段中**显式说明**主要 residue 的类型:

```yaml
translation_notes: |
  check_translation_residue.py returned suspicious_count=85.
  This is expected for a music catalog article containing 50 song titles,
  50 artist names, and 30+ album names (all preserved as proper nouns).
  No genuine untranslated paragraphs detected.
```

并且**必须在报告**中列出主要的专名类型:

```markdown
## Translation residue analysis

- suspicious_count: 85
- Main residue types:
  - Song titles: ~50 (e.g., "I Second That Emotion", "Stoned Soul Picnic")
  - Artist names: ~50 (e.g., "Wayne Shorter", "Pink Floyd")
  - Album names: ~30 (e.g., "Speak No Evil", "Kind of Blue")
- Genuine translation gaps: 0
- Recommendation: ACCEPT (proper nouns only, not translation errors)
```

### 6.4 不得忽略真正漏译

**residue 数高 ≠ 没有漏译**。在判定"全部是专名"之前,必须:

1. 抽样检查 residue 字符串 — 几乎全部应该是已知的歌名 / 艺人名 / 专辑名
2. 检查 translation.zh-CN.md 的整体 CJK 比例 — 长名单文章翻译比例应 ≥ 1.0x source word count
3. 检查是否有过长的英文段落(>50 词连续英文) — 这种通常是**真正的漏译**,不是专名

**判定流程**:
```
if residue_count > 20:
    sample_count = 10  # 抽 10 个
    proper_noun_count = count_proper_nouns(samples)
    if proper_noun_count >= 8:
        # 80%+ 是专名 → ACCEPT
    elif 5 <= proper_noun_count < 8:
        # 混合 → 报告说明,人工 review
    else:
        # <50% 是专名 → 真正漏译,需要 hard-stop
```

---

## 7. 状态标记:PASS_WITH_WARNINGS

### 7.1 三态分级

之前的导入状态只有 PASS / WARN / FAIL 三态。对长名单文章,引入 `PASS_WITH_WARNINGS`:

| 状态 | 含义 | commit 行为 |
|---|---|---|
| `PASS` | 所有 4 个硬门禁 + 全部 quality checks PASS,无任何 warning | 正常 commit |
| `PASS_WITH_WARNINGS` | 4 个硬门禁 PASS,但 residue 数高(residue 全是专名) | 正常 commit + 报告中说明 |
| `WARN` | 某个软门禁失败(例如 coverage 不完整但用户已知) | 正常 commit + 报告中明确警示 |
| `FAIL` | 硬门禁失败(错位 / 缺号 / 重复 / 凭空捏造) | **禁止 commit,必须修复** |

### 7.2 长名单文章的状态约定

Paste 那次的状态应该是 `PASS_WITH_WARNINGS`,不是简单 `PASS`,因为:

- check_kb.py: PASS(36/36)
- update_site.py: PASS(5/5)
- check_pages_sync.py: PASS(36/36 byte-identical)
- check_translation_residue.py: **WARNING(suspicious_count=85)** — 高于 KB 平均值(10.1)

但所有 4 个**硬**门禁都 PASS。`PASS_WITH_WARNINGS` 准确表达「硬门禁通过 + 软警告存在」。

### 7.3 在 commit message 中标记

```bash
git commit -m "Add Paste Magazine 1960s top 100 songs list #100-#51 (zh-CN, 50 songs) — PASS_WITH_WARNINGS (residue=85 proper nouns)"
```

---

## 8. 长名单文章导入检查清单(在 commit 之前自检)

```markdown
- [ ] 1. 已识别为 long_list_article(标题或结构匹配)
- [ ] 2. source.md 从原始 HTML 完整解析,不是 web_extract 截断版
- [ ] 3. source.md 顶部有 HTML 注释说明 coverage 与分页
- [ ] 4. source.md H2 编号连续(无 gap / 无重复)
- [ ] 5. metadata.yaml 含 coverage_scope + is_partial_series + series_info
- [ ] 6. summary.md 含「覆盖范围」段
- [ ] 7. translation.zh-CN.md 已写完,所有 source H2 一一对齐
- [ ] 8. 对齐脚本运行:50/50 (或对应数字)
- [ ] 9. residue analysis:专名占比 ≥80%,无真正漏译
- [ ] 10. notes.md 记录分页范围 + 任何翻译过程错误
- [ ] 11. 报告含 Coverage scope 表 + Residue analysis 段
- [ ] 12. 状态: PASS_WITH_WARNINGS(若 residue 高) / PASS(若全干净)
- [ ] 13. commit message 含状态标记
```

---

## 9. 历史案例

### 2026-06-26 Paste Magazine「The 100 greatest songs of the 1960s」(commit `725b7a9`)

**问题**:
- web_extract 截断在 #89,基于截断版继续翻译
- #76-#66 共 11 首歌 H2 标题错位
- #75 Led Zeppelin 缺失
- #74 凭空捏造 The Staple Singers 段落
- 修复过程留下 8 个重复 H2

**修复**:
- 用 patch 工具精确替换错位段落(基于 source.md 重新提取的原文)
- dedup 清理 8 个重复 H2
- 在 notes.md §9 中如实记录错误过程

**记入本规则**: 作为首个 long_list_article 教训案例,固化本文 §1-§8 全部规则。

---

## 10. 未来改进方向

1. **`check_translation_residue.py` 的 ALLOWED_PATTERNS 增加歌名 / 专辑名 pattern** — 见 `kb-import-e2e-workflow` skill §Pitfalls G
2. **新增 `scripts/check_listicle_structure.py`** — 自动化 §3 的结构预检与 §4 的结构对齐检查
3. **新增 `templates/listicle_metadata.yaml`** — 长名单文章的 metadata 模板(已含 coverage_scope / series_info 字段)

---

**维护者**: Hermes Agent
**最后更新**: 2026-06-26
**关联文档**:
- `docs/AGENT_COMMANDS.md` — 导入规则总览(本文被引用)
- `templates/prompts/import_article_prompt.md` — 完整导入流程
- `docs/TAXONOMY.md` — 标签体系
- `~/.hermes/skills/kb-import-e2e-workflow/` — link 4 e2e 导入流程