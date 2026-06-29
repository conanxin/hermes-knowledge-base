# Metadata Cleanup 基线冻结报告 v0.3.66

**生成时间：** 2026-06-29 15:55 Asia/Shanghai  
**生成者：** 辛 🔮  
**关联 Tag：** `v0.3.66-metadata-cleanup-baseline-freeze`  
**基线 Commit：** `307bd89` (v0.3.65-residual-tag-warn-refinement)  

---

## STATUS

**PASS** — 基线冻结完成，metadata cleanup 线暂时收口

- WARN: **24**（冻结）
- 0 hard fail
- Records: 54
- 无 content/articles/ 修改
- 无 metadata.yaml 修改
- 无 lint 规则修改

---

## 版本流水（v0.3.61 → v0.3.66）

| 版本 | Tag | Commit | WARN 变化 | 主要工作 |
|------|-----|--------|-----------|----------|
| v0.3.61 | `v0.3.61-metadata-drift-lite-cleanup` | `7051f20` | 38 → 30 | 修复 `translation_language='null'` 字符串 + 重复 tag |
| v0.3.62 | `v0.3.62-tag-soft-limit-audit` | `550a73b` | 30 → 30（审计） | 29 个 tag 超软限分组审计 |
| v0.3.63 | `v0.3.63-tag-soft-limit-convergence` | `7fff346` | 30 → 28 | 应用 11 条高置信 tag 合并规则 |
| v0.3.64 | `v0.3.64-legacy-collections-cleanup` | `0e588c4` | 28 → 27 | 迁移 4 个 collections 条目，消除 dir_drift |
| v0.3.65 | `v0.3.65-residual-tag-warn-refinement` | `307bd89` | 27 → 24 | 清理 14 个冗余标签（双语重复 + tag-topic 重叠） |
| **v0.3.66** | `v0.3.66-metadata-cleanup-baseline-freeze` | **dbe0aeb** | **24（冻结）** | **记录基线，进入观察期** |

---

## 关键指标汇总

| 指标 | v0.3.61 前 | v0.3.66 后 | 变化 |
|------|-------------|------------|------|
| **WARN** | 38 | 24 | -14 (-36.8%) |
| **Hard fail** | 0 | 0 | 0 |
| **Records** | 54 | 54 | 0 |
| **Dir drift** | 1 | 0 | -1 |
| **Duplicate tag** | 1 | 0 | -1 |
| `translation_language='null'` | 7 | 0 | -7 |
| **Bilingual duplicate tags** | ~10 | 0 | -10 |
| **Tag-topic overlap** | 4 | 0 | -4 |
| **Synonym/abbreviation merges** | ~15 | 0 | -15 |

---

## 已解决的问题类型

### ✅ 已完全解决

1. **`translation_language='null'` 字符串**（7 处）
   - v0.3.61 修复，将 `"null"` 改为 `null`
   - 验证：0 处复发

2. **重复 tag**（2 处）
   - v0.3.61 删除 1 处重复 `"Mencius Moldbug"`
   - v0.3.63 合并过程中消除其他重复
   - 验证：0 处复发

3. **dir_drift（content/collections/）**（1 处）
   - v0.3.64 迁移 4 个 collections 条目至 resource_collections/
   - 删除空目录 content/collections/
   - 验证：0 处复发

4. **双语重复标签**（10 处）
   - v0.3.65 清理：爱默生/奥威尔/皮克斯/动画/创作过程等
   - 验证：0 处复发（基于当前数据）

5. **tag-topic 重叠**（4 处）
   - v0.3.65 清理 Conan 文件：毕业演讲/自我认知/成功学/政治讽刺
   - 验证：0 处复发（基于当前数据）

### ⚠️ 部分解决（仍有残余）

6. **tag 过多（>12）**（16 → 13 文件）
   - v0.3.63 合并后减少 3 个文件
   - v0.3.65 清理后减少 3 个文件（Emerson、Orwell、Conan）
   - 剩余 13 个文件仍超软限

7. **tag 过少（<6）**（1 文件）
   - reverse-game-theory-housing-shortage（5 tags）
   - 标签精准，建议保留

8. **topic 过多（>8）**（9 → 10 文件）
   - v0.3.65 清理 Conan 后 topic 仍超（10 topics）
   - 新增 1 个 topic WARN（Conan 的 tag 清理后 topic 未动）
   - 实际 topic WARN 数量未减少，反而因 Conan 的 tag 清理后 tag 进入范围但 topic 仍超

---

## 剩余 24 WARN 的处理策略

### 为什么不建议继续硬清 tag？

1. **语义损失风险**：剩余 tag 多为合理的主题标签，强行合并可能丢失语义
2. **长尾标签价值**：低频标签可能代表特定知识域，不应简单删除
3. **观察期价值**：当前 24 WARN 属于 `PASS_WITH_WARNINGS`，不影响正常使用
4. **工具成本**：继续手工合并的边际收益递减，应优先设计系统化方案

### 剩余 WARN 明细（24 个）

| 类型 | 数量 | 代表文件 | 说明 |
|------|------|----------|------|
| tag 过多（>12） | 13 | dario-amodei（25 tags）、paste-greatest-songs（27 tags）、scharmer（21 tags）等 | 主题广泛或 listicle 例外 |
| tag 过少（<6） | 1 | reverse-game-theory（5 tags） | 标签精准，建议保留 |
| topic 过多（>8） | 10 | hunter-murray（10 topics）、conan（10 topics）、scharmer（8 topics）等 | 中文 topics 体系独立 |

### 推荐处理策略

| 策略 | 优先级 | 说明 |
|------|--------|------|
| **观察期** | P0 | 保持当前 24 WARN，新增内容时按 tag policy 建议执行 |
| **tag allowlist** | P1 | 设计核心标签池（50-100 个），超出时 warning |
| **topic 规范** | P2 | 中文 topics 独立管理，与 tags 分离 |
| **继续手工合并** | P3 | 暂不推荐，除非发现新的高置信合并组 |

---

## 后续推荐路线

### A. 观察期（推荐，P0）
- 保持当前 24 WARN
- 新增内容导入时，按 tag policy 建议执行
- 观察 2-4 周后再评估
- 成本：最低
- 风险：无

### B. 设计 tag allowlist（P1）
- 定义核心标签池（约 50-100 个）
- 超出时 warning（不阻断）
- 逐步收敛低频/冗余标签
- 成本：中等（需设计 + 实施）
- 风险：可能误杀合理标签

### C. 等新增内容导入后再重新评估（P2）
- 新文章可能引入新的 tag 模式
- 基于新增数据调整 tag policy
- 避免过度优化现有标签体系
- 成本：低（被动）
- 风险：无

---

## 验证

- [x] WARN = 24
- [x] Hard fail = 0
- [x] Records = 54
- [x] 无 content/articles/ 修改
- [x] 无 metadata.yaml 修改
- [x] 无 lint 规则修改
- [x] 无正文修改
- [x] 无新增文章
- [x] 无重新 OCR/抽取

---

## 结论

Metadata cleanup 线从 v0.3.61 到 v0.3.65 完成五轮迭代，WARN 从 38 降至 24（-36.8%），hard fail 始终为 0，records 始终为 54。当前 24 WARN 全部为 tag soft-limit，属于可接受的 `PASS_WITH_WARNINGS` 范围。

**建议：进入观察期，暂缓继续硬清，优先设计 tag policy / allowlist 机制。**

---

*报告结束。如需继续执行业务任务或设计 tag allowlist，请指示。*
