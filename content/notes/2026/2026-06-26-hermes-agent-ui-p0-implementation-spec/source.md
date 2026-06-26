# Hermes Agent UI P0 实施规范：来源与方法

## 派生关系

本条目是 4 层派生的最下游：

```
2026-06-26-shape-of-ai-ux-patterns                              (resource_collection, 原始)
  └── 2026-06-26-hermes-agent-ui-shape-of-ai-checklist          (note, 自检表 v1)
        └── 2026-06-26-hermes-agent-ui-self-audit-v1            (note, 审计 v1)
              └── 2026-06-26-hermes-agent-ui-p0-implementation-spec  (note, 本条目, 实施规范)
```

`based_on` 字段列出 3 个直接上游（不列 Shape of AI，因其已是 checklist 的上游）。

## 规范 vs 实施 vs 实现

本规范的三个边界：

| 类型 | 含义 | 是否本规范 |
|---|---|---|
| **规范（Spec）** | 定义"应该怎么输出"、"按什么模板"、"哪些字段必填" | ✅ 是 |
| **实施（Implementation）** | 改 prompt / 话术 / 工具描述 / 报告模板 | 引用本规范（agent 自我实施） |
| **实现（Engineering）** | 写新工具 / 新组件 / 新脚本 | ❌ 不在本规范范围（属 v1 路线阶段 3） |

**关键区分**：本规范只回答"输出格式"和"验收标准"，不回答"怎么改代码"。

## 数据来源：本规范的"实证基础"

本规范的并发协议章节（§8）基于以下最近 3 次实际任务经验：

1. **2026-06-26 item_count 修复** (`b42212d`)：单 agent 顺序 push，CDN 第二次轮询同步（~30s）
2. **2026-06-26 checklist 创建** (`9aed075`)：catalog 41→42，第一次 push 失败（force-push 风险），reset-and-rebuild 模式被验证
3. **2026-06-26 self-audit 创建** (`dd833d5`)：catalog 42→43，CDN 第二次轮询同步（~30s），rebase 已 fast-forward

这 3 次任务的真实数据成为本规范的**经验基底**——所有"CDN 同步时间"、"PENDING_CDN_SYNC 不判 FAIL"等结论都来自实证，不是推测。

## 实施规范的设计原则

### 原则 1：8 段报告是下限，不是上限

报告模板的 8 段（Status / Scope / Actions / Evidence / Commit/Push / Live / Limits / Next）是**最低要求**。任务复杂时（如包含多 sub-agent、跨平台 verify、CDN 同步）可加段，但不减段。

**为什么不强制更多段**：报告 8 段已经覆盖 Trust builders 的 3 个 P0 项（Source citation / Human review / Confidence score）。更多段会提高门槛，反而让人不写。

### 原则 2：PASS / WARN / FAIL 三态，不只有 PASS / FAIL

`WARN` 的引入是为了诚实标注"未完成 / 未验证 / 暂未同步"等状态，而不是把它们藏起来或者误报 PASS。

**例子**：

- "CDN 暂未同步，标记 PENDING_CDN_SYNC" → WARN（不阻断，等同步后复查）
- "未跑复现实验，仅启发式判断" → WARN（不阻断，下次补实验）
- "Evidence 缺置信度字段" → WARN（不阻断，下次补）
- "check_kb.py FAIL" → FAIL（阻断，必须修）
- "push 失败" → FAIL（阻断，必须重试或 reset-and-rebuild）

### 原则 3：每条 P0 都有"最小实施规则"——不依赖 UI

5 P0 的最小实施规则**全部在 prompt / 报告 / 工具描述层可改**，不需要新写工具或新组件。这与 Self-Audit v1 路线阶段 1（无代码流程规范）对齐。

**反例警告**：

> 如果某条 P0 的最小实施规则必须改 UI 组件才能满足，那这条 P0 应该被推迟到路线阶段 3，不在 v1 范围。

### 原则 4：并发协议独立成章节——它影响所有 P0

并发 agent 写仓库是本规范**最常被违反**的边界。把 fetch / pull / rebase / check / push / CDN 同步独立成 §8 章节，目的是让 agent 在写多步任务时**不必重新发明协议**——直接照抄。

**为什么 §8 最重要**：其他 P0 影响"输出格式"，§8 影响"任务能否完成"。§8 失败则整个任务 FAIL。

## 借鉴的其他规范

本规范参考了以下已有的工程实践（不直接复制）：

- **CONTRIBUTING.md 模式**：模板化报告 → 降低边际成本
- **Conventional Commits 模式**：固定 commit message 格式 → 可解析
- **Status Page 模式**：Status / Scope / Actions / Evidence / Next 的分段
- **Postmortem 模板（Google SRE）**：Limits / Next 的诚实标注
- **kb-article-import skill 的 STATUS block**：Telegram 友好的报告格式

## 维护约定

### 何时升级 v1 → v2

满足以下任一条件时升级：

1. 5 P0 全部落地（按 Self-Audit v1 路线阶段 1 + 2 完成）
2. 30 天内应用本规范 ≥ 10 次，复盘显示 WARN 比例 < 5%
3. Self-Audit 出 v2，本规范必须同步升级
4. 新增 agent 工作流工具（cronjob / delegate_task），并发协议章节需扩展

### 不要做的事

- **不要**把本规范固化为"agent 必须遵守"——它是 SOP 不是宪法
- **不要**因为某次任务没按规范而 FAIL 整个任务——WARN 是设计目的
- **不要**在没复现实验的情况下把"启发式"误报为"实证"——诚实标注来源
- **不要**让本规范变成纯流程清单——必须包含示例报告片段（agent 抄作业用）

## 已知限制

1. **本规范是 SOP，不是 enforcement**——没有代码层面的检查点
2. **WARN 状态依赖 agent 自觉**——可能存在"漏报 WARN"的情况
3. **并发协议基于最近 3 次经验**——更多边缘情况（multi-agent parallel push）未覆盖
4. **报告模板不带国际化**——目前只中文，跨语言任务需扩展
5. **8 段报告对简单任务偏重**——比如纯 read 类任务只需 3 段（见 §7 三类任务差异化）

## 与项目记忆的关联

本规范的执行依赖以下项目记忆：

- **Telegram typing action**：Status "思考中" 的视觉对应
- **MEDIA 协议**：Inline Action 的"已生效"标签可借助 MEDIA 消息格式
- **sub-agent 隔离**：`hermes-agent-spawning` / `delegate_task` 提供独立 cwd
- **session DB 持久化**：所有 commit / push 操作可回看（"Evidence" 的 last-validated 字段）
- **multi-platform home channel**：Live 验证需逐平台 curl / sha256
- **OpenClaw 异步任务**：cronjob 任务需在 PENDING 状态时单独标注

如果项目记忆本身有误（如某工具已下线），本规范相应章节需要修正。
