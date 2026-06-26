# Hermes Agent 任务报告模板：摘要

## 是什么

**Hermes Agent Task Report Template** 是 [P0 Implementation Spec](2026-06-26-hermes-agent-ui-p0-implementation-spec) 中 8 段报告模板的**可直接复制版本**。目标是"用一行命令复制粘贴、填空就发",不再写长篇理论。

**一句话定位**：本条目是 SOP 的"实操清单",P0 Spec 是"理论依据"。**用本模板,引用 P0 Spec 解释为什么**。

## 三个模板

| 模板 | 适用 | 必填段 |
|---|---|---|
| [只读审计任务报告模板](#模板-1-只读审计任务报告模板) | read / search / grep / analyze | 3 段 (Status / Scope / Evidence) |
| [写入但不发布任务报告模板](#模板-2-写入但不发布任务报告模板) | patch / write / build / 报告生成 | 5 段 (+ Actions / Files) |
| [写入并发布任务报告模板](#模板-3-写入并发布任务报告模板) | push / deploy / publish / 跨 agent 共享 | 9 段 (全部,含 Checks / Live / Next) |

## 标签词汇表(直接用)

- **状态标签**:`PASS` / `WARN` / `FAIL` / `PENDING_CDN_SYNC` / `RESOLVED`
- **执行标签**:`[READ-ONLY]` / `[WRITE]` / `[GENERATE]` / `[PUSH]` / `[LIVE]`
- **生命周期标签**:`proposed` / `applied` / `pushed` / `live`(每个动作必须属于其一)

**注意**:P0 Spec 用 `[DRY-RUN]` / `[APPLIED]`,本模板用 `[READ-ONLY]` / `[WRITE]` / `[GENERATE]` / `[PUSH]` / `[LIVE]`(更具体)。**两套标签都有效,本模板以更细粒度为准**。

## 何时用哪个模板

按 **任务对远端状态的影响** 分类:

| 影响等级 | 模板 | 例子 |
|---|---|---|
| **只读** | 模板 1 (3 段) | `ls /` / `grep` / `web_search` / `read_file` |
| **写本地** | 模板 2 (5 段) | `write_file` / `patch` / `build_index.py` |
| **发远端** | 模板 3 (9 段) | `git push` / `deploy` / `send_message` / `publish` |

如果任务从"写本地"升级为"发远端"(如发现需要 push),**必须改用模板 3** 并补全缺失段。

## 4 个支撑章节

| 章节 | 作用 |
|---|---|
| [§1 状态三态说明](#1-状态三态说明) | 3 套三态(PASS/WARN/FAIL、读写发、本地/远端/live)的语义边界 |
| [§2 CDN 延迟处理规则](#2-cdn-延迟处理规则) | `PENDING_CDN_SYNC` 的进入和退出条件 |
| [§3 多 agent 并发最小协议](#3-多-agent-并发最小协议) | 5 步最小协议(从 P0 Spec §8 简化) |
| [§4 以后如何使用](#4-以后如何使用) | 强制/可选使用场景 + 反模式 |

## 不做什么

- **不写长篇理论**:P0 Spec 已写,本条目只复制 + 简化
- **不复述 P0 Spec 的所有内容**:每节用 1-2 句话引用
- **不引入新概念**:`proposed / applied / pushed / live` 是生命周期标签,与 P0 Spec 的 [DRY-RUN] / [APPLIED] 一一对应
- **不强制**:`[READ-ONLY]` / `[WRITE]` 等标签是建议,不用也不阻断任务完成

## 派生关系

```
2026-06-26-shape-of-ai-ux-patterns                              (原始, 资源条目)
  └── 2026-06-26-hermes-agent-ui-shape-of-ai-checklist          (自检表 v1)
        └── 2026-06-26-hermes-agent-ui-self-audit-v1            (审计 v1)
              └── 2026-06-26-hermes-agent-ui-p0-implementation-spec  (P0 规范)
                    └── 2026-06-26-hermes-agent-task-report-template  (本条目, 实操模板)
```

5 层派生的最下游,直接给 agent 用。

## 何时更新本模板

- 当 P0 Spec 升级到 v2 时,本模板同步更新
- 当某类任务出现模板不覆盖的情况(如下次出现)时,扩展模板
- 当 §3 最小协议增加新步骤时,本模板的"写入并发布"段同步更新

## 与 P0 Spec 的差异

| 维度 | P0 Spec | 本模板 |
|---|---|---|
| 性质 | 规范 (SOP 理论) | 模板 (实操清单) |
| 长度 | 长(2600 行) | 短(< 500 行) |
| 复用 | 引用为权威 | 复制粘贴直接用 |
| 抽象度 | 抽象(Section 编号、原则解释) | 具体(填空、命令行、具体 URL 格式) |
| 验证 | 5 P0 逐条规范 | 3 模板 + 4 支撑 |
| 读者 | 设计者 | 实施者(agent 自身) |

## 一句话总结

> **本模板 = "复制 → 填空 → 发送"。P0 Spec = "为什么这样填空"。**
