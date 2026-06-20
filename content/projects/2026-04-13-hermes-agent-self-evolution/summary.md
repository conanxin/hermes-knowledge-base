# 摘要：Hermes Agent Self-Evolution

## 旧内容主要讲什么

本文记录了 NousResearch 的 Hermes Agent Self-Evolution 项目，一个使用 DSPy + GEPA 实现 Agent 自我进化优化的研究平台。项目核心定位是验证 pipeline 连通性、研究 demonstration injection 的 variance，而非生产可用的 skill 文本优化器。

文章详细描述了项目的五个阶段（从 Skill 文件进化到 Continuous improvement loop）、优化目标分层（Tier 1-4）、核心引擎（DSPy + GEPA / Darwinian Evolver / MIPROv2）、约束与护栏、基准门控、优化循环、成本估算，以及与 Hermes Agent 的关系。

关键结论：当前项目已冻结基线 v1，metrics 变化来自 demonstration injection 效应而非 SKILL.md 文本的实际改写。三技能验证结果显示 variance 从 -9.6% 到 +18.1%，不稳定。

## 为什么值得迁移

1. **项目历史记录**：这是 Hermes Agent 生态的重要组成部分，记录了关键的技术决策和实验结果
2. **技术参考价值**：DSPy + GEPA 的优化思路对 prompt engineering 和 skill 优化有参考价值
3. **决策记录**：明确记录了"能做什么"和"不能做什么"的边界，避免未来重复踩坑
4. **成本估算**：提供了详细的成本数据（$2-10/次运行），对未来项目规划有帮助

## 迁移后如何使用

- **技术参考**：理解 DSPy + GEPA 的优化思路和局限性
- **项目复盘**：作为 Hermes Agent 自我进化项目的存档，供未来复盘参考
- **成本规划**：参考成本估算，规划类似项目的预算
- **边界意识**：理解当前技术边界，避免过度承诺

## 是否缺少来源 URL

否。来源 URL 为 GitHub 仓库：https://github.com/NousResearch/hermes-agent-self-evolution

## 后续是否需要补充或重写

- **短期**：无需补充，内容完整
- **中期**：如果项目重启或发布新版本，可更新状态
- **长期**：作为项目历史存档，长期保留

## 关键概念

| 概念 | 说明 |
|------|------|
| DSPy | 声明式编程框架，用于优化 LLM 调用 |
| GEPA | 反射式 prompt 进化引擎 |
| BootstrapFewShot | Few-shot 示例优化方法 |
| Darwinian Evolver | 代码进化引擎 |
| TBLite | 编码/sysadmin 基准测试 |
| TerminalBench2 | 较难的编码/sysadmin 基准 |
| YC-Bench | 长视野战略一致性测试 |
| Demonstration injection | 演示注入效应 |

## 关联内容

- 与 Hermes Agent 项目直接相关
- 与 DSPy 框架相关
- 与 Skill 优化和进化相关
