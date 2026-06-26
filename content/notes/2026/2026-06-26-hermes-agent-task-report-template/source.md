# Hermes Agent 任务报告模板：来源与方法

## 派生关系

5 层派生的最下游:

```
2026-06-26-shape-of-ai-ux-patterns                              (resource_collection, 原始)
  └── 2026-06-26-hermes-agent-ui-shape-of-ai-checklist          (note, 自检表 v1)
        └── 2026-06-26-hermes-agent-ui-self-audit-v1            (note, 审计 v1)
              └── 2026-06-26-hermes-agent-ui-p0-implementation-spec  (note, P0 规范)
                    └── 2026-06-26-hermes-agent-task-report-template  (note, 本条目, 实操模板)
```

`based_on` 字段列出 3 个直接上游(不列原始 Shape of AI 和 checklist,因已是 P0 Spec 的上游)。

## 模板 vs 规范 vs 实施

| 类型 | 含义 | 本条目 |
|---|---|---|
| **模板 (Template)** | 可直接复制的填空清单 | ✅ 是 |
| **规范 (Spec)** | 定义"应该怎么输出"的原则 | 引用(P0 Spec) |
| **实施 (Implementation)** | 改 prompt / 话术 / 工具描述 | agent 自身应用 |
| **实现 (Engineering)** | 写新工具 / 组件 / 脚本 | ❌ 不在本条目 |

**本条目的边界**:**只回答"怎么填",不回答"为什么这样填"**。所有"为什么"都引用 P0 Spec。

## 标签词汇表的设计

本模板在 P0 Spec 的 `[DRY-RUN] / [APPLIED]` 基础上扩展为更细的 5 标签系统:

| 标签 | P0 Spec 对应 | 含义 |
|---|---|---|
| `[READ-ONLY]` | (P0 Spec 未明确) | 只读操作,无副作用 |
| `[WRITE]` | `[APPLIED]` 本地 | 已写入本地文件,未推远端 |
| `[GENERATE]` | `[APPLIED]` 派生 | 已生成派生文件(如 catalog.json),源来自本地 |
| `[PUSH]` | `[APPLIED]` 远端 | 已 push 到远端(git push) |
| `[LIVE]` | (本条目新加) | 已在 live CDN 验证 |

**为什么不用 P0 Spec 的二标签**:实际任务中"已应用"和"已 push"和"已 live"是 3 个不同的事,二标签把它们混为一谈。**5 标签让 8 段报告里的"动作生命周期"更精确**。

**向后兼容**:用 `[DRY-RUN] / [APPLIED]` 也接受,但本模板鼓励用 5 标签。

## 模板分段的设计

P0 Spec §6 用 8 段(Sta/Scop/Act/Evid/Com/Live/Lim/Next),本模板扩展为 9 段(+ **Files changed** + **Checks**):

| 段 | P0 Spec | 本模板 | 区别 |
|---|---|---|---|
| Status | §1 | §1 | 相同 |
| Scope | §2 | §2 | 相同 |
| Actions | §3 | §3 | 用 5 标签,更细 |
| Evidence | §4 | §4 | 相同(三件套) |
| **Files changed** | (隐含) | §5 | **本模板新增**:独立列出修改文件 |
| **Checks** | (隐含) | §6 | **本模板新增**:check_kb / check_pages_sync 等 |
| Commit / Push | §5 | §7 | 合并到一段 |
| Live | §6 | §8 | 同 P0 Spec |
| Limitations | §7 | (合并到 §9 Next 之前的备注) | 简化 |
| Next | §8 | §9 | 相同 |

**为什么加 Files / Checks 段**:P0 Spec 把"文件变更"和"check 结果"分别隐含在 §3 Actions / §4 Evidence 里,但实际复盘时**单独成段**更易 grep / 解析。本模板把它们独立。

## 4 支撑章节的来源

| 章节 | 来自 P0 Spec 哪里 | 简化原则 |
|---|---|---|
| 状态三态说明 | P0 Spec §6 三态验收 + §7 三类任务 | 把 3 套三态合并到一节,加交叉引用表 |
| CDN 延迟处理规则 | P0 Spec §8.3 模式 B | 从 bash 脚本 + 失败模式总结为 5 行规则 |
| 多 agent 并发最小协议 | P0 Spec §8.2 13 步 | 简化为 5 步最小集(非最小集回到 P0 Spec) |
| 以后如何使用 | P0 Spec §9 | 缩短 + 加"反模式"段落 |

## 何时不要用本模板

- **纯只读且结果极简** (如 `ls` 列出 3 个文件):不需要报告,直接贴结果
- **debug 类诊断**:本模板不适用,直接贴错误 + 调用栈
- **chat 闲聊**:不用任何模板
- **用户明确说"brief"**:简化为 1-2 句话,不强制 8/9 段

## 维护约定

### 何时升级 v1 → v2

- 当某类任务"用本模板仍报告不完整"出现 3+ 次时,扩展该模板
- 当 P0 Spec 升级到 v2 时,本模板同步升级
- 当最小协议 (§3) 需要新增步骤时,本模板的"写入并发布"段同步

### 不要做的事

- **不要**在每段都强加字数要求 — 简洁优于完整
- **不要**把"4 支撑章节"当模板必填 — 它们是参考
- **不要**让本模板变成"形式主义" — 一个 5 行的报告,填空到位,优于一个 50 行的报告凑字数

## 已知限制

1. **本模板是"填空清单",不是"完整报告生成器"** — 复杂的 reasoning / debugging 不适合用此格式
2. **状态三态有重叠**:PASS + PENDING_CDN_SYNC 可能同时出现(本模板定义为"PASS in Git, PENDING_CDN_SYNC in live",§1 详述)
3. **CDN 轮询脚本只对 GitHub Pages 适用** — 其他 CDN (Vercel / Cloudflare Pages) 需要替换轮询 URL
4. **本模板不强制**:本仓库内只用于 hermes-knowledge-base 相关任务;其他 agent (OpenClaw / ConPort) 引用本模板时,需要适配
5. **附录里的"已废弃标签"段落**:P0 Spec 的 `[DRY-RUN] / [APPLIED]` 仍可用但已非首选,本模板推荐 5 标签体系

## 与项目记忆的关联

本模板的执行依赖项目记忆:

- **Telegram typing action**:对应"执行中"状态
- **MEDIA 协议**:用于 [PUSH] 后的"已生效"反馈
- **sub-agent 隔离**:用于 §3 最小协议中的"并发写入"判断
- **session DB 持久化**:用于 Evidence 段的"last-validated"时间
- **多平台 home channel**:用于 [LIVE] 段的逐平台 curl

如果项目记忆本身有误,本模板相应段需要修正。
