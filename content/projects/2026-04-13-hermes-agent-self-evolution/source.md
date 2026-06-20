<!-- 来源: https://github.com/NousResearch/hermes-agent-self-evolution -->
<!-- 摄入日期: 2026-04-07 -->
<!-- 状态更新: 2026-04-13 -->
<!-- 迁移日期: 2026-06-20 -->

# Hermes Agent Self-Evolution

## 概述

**当前定位**：Runtime Optimization 研究平台（冻结基线 v1）

项目已从"文本进化探索"降级为"runtime optimization 研究平台"。核心定位是验证 pipeline 连通性、研究 demonstration injection 的 variance，**而非生产可用的 skill 文本优化器**。

使用 DSPy + BootstrapFewShot（GEPA 自动 fallback）进行 runtime optimization。每次运行约 $2-10，但当前 metrics 变化来自 demonstration injection 效应，而非 SKILL.md 文本的实际改写。

---

## 状态摘要（2026-04-13）

| 维度 | 状态 |
|------|------|
| 跨类型可运行性 | 已验证（3 skills） |
| 稳定正向优化 | 未验证（variance -9.6% ~ +18.1%） |
| 文本进化 | 未发生（artifact 与 baseline 相同） |
| live 迁移就绪 | 不适合 |

**三技能验证结果**：

| Skill | 类型 | Metrics | Artifact 变化 |
|-------|------|---------|---------------|
| github-code-review | 代码审查 | +18.1% | 未变化 |
| plan | 规划约束 | +4.1% | 未变化 |
| polymarket | 数据查询 | -9.6% | 未变化 |

---

## 核心架构

```
当前 skill/prompt/tool ──► 生成 eval dataset
                                    │
                                    ▼
                              GEPA 优化器 ◄── 执行轨迹
                                    │              ▲
                                    ▼              │
                              候选变体 ──► 评估
                                    │
                              约束门控 (tests, size limits, benchmarks)
                                    │
                              最佳变体 ──► PR 到 hermes-agent
```

GEPA 读取执行轨迹来理解 **为什么** 失败 (不仅仅是失败了)，然后提出针对性改进。

---

## 五个阶段

| 阶段 | 目标 | 引擎 | 状态 |
|------|------|------|------|
| **Phase 1** | Skill files (SKILL.md) | DSPy + GEPA | 已实现 |
| **Phase 2** | Tool descriptions | DSPy + GEPA | 计划中 |
| **Phase 3** | System prompt sections | DSPy + GEPA | 计划中 |
| **Phase 4** | Tool implementation code | Darwinian Evolver | 计划中 |
| **Phase 5** | Continuous improvement loop | Automated pipeline | 计划中 |

---

## 优化目标分层

### Tier 1: Skill 文件 (最高价值，最低风险)
- **目标**: SKILL.md 文件 — agent 遵循的程序指令
- **方式**: 将 skill 文本包装为 DSPy 模块，通过 batch_runner 在测试任务上评估，用 GEPA 进化
- **为什么有效**: Skills 是纯文本，容易突变，直接可测量
- **例子**: 进化 `github-code-review` skill，通过已知良好 code reviews 的数据集测试

### Tier 2: Tool 描述 (中等价值，低风险)
- **目标**: tool schemas 中的 `description` 字段
- **方式**: GEPA 进化描述，评估 agent 是否为给定任务选择正确的工具
- **为什么有效**: 工具选择是分类问题 — DSPy 优化的完美用例

### Tier 3: System Prompt 组件 (高价值，更高风险)
- **目标**: system prompt 的各部分 (persona, policies, formatting instructions)
- **方式**: 将 prompt_builder.py 各部分参数化为 DSPy Signatures，用 GEPA 优化
- **风险**: 必须小心不破坏 prompt caching

### Tier 4: 代码进化 (最高价值，最高风险)
- **目标**: 工具实现代码、辅助函数
- **方式**: Darwinian Evolver 与 GitBasedOrganism，通过 pytest + batch_runner 测试

---

## 引擎

| 引擎 | 功能 | 许可证 |
|------|------|--------|
| **DSPy + GEPA** | 反射式 prompt 进化 — 读取执行轨迹，提出针对性突变 | MIT |
| **Darwinian Evolver** | 代码进化，基于 Git 的 organisms | AGPL v3 (仅外部 CLI) |
| **DSPy MIPROv2** | Few-shot 示例、指令文本的优化 | MIT |

---

## 约束与护栏

每个进化变体必须通过：

1. **完整测试套件** — `pytest tests/ -q` 必须 100% 通过
2. **大小限制** — Skills ≤15KB, tool descriptions ≤500 chars
3. **缓存兼容性** — 无会话中更改
4. **语义保持** — 不能偏离原始目的
5. **PR 审查** — 所有更改通过人类审查，永远不直接 commit

---

## 基准作为 fitness 信号

| 基准 | 测试内容 | 速度 | 成本 | 角色 |
|------|----------|------|------|------|
| **TBLite** | 编码/sysadmin (100 任务) | ~1-2h | ~$20-50 | **主要回归检查** |
| **TerminalBench2** | 编码/sysadmin (89 较难任务) | ~2-4h | ~$50-200 | **彻底验证** |
| **YC-Bench** | 长视野战略一致性 (100-500 turns) | ~3-6h | ~$50-200 | **一致性检查** |

**关键原则**: 基准是 **门控**，不是 fitness 函数。Fitness 函数是任务特定的。

---

## 优化循环

```
候选变体
    │
    ├──► pytest (必须 100% 通过) ────────── 门控 1: 功能正确性
    │
    ├──► TBLite 快速子集 (20 任务) ───────── 门控 2: 快速能力检查
    │
    ├──► 任务特定 eval 数据集 ─────────────── Fitness: 质量分数
    │
    ▼
仅最佳候选 (top 3)
    │
    ├──► 完整 TBLite (100 任务) ───────────── 门控 3: 彻底回归检查
    │
    ├──► YC-Bench fast_test ───────────────── 门控 4: 一致性检查
    │
    ▼
最佳候选 → 带有完整指标的 PR
```

---

## 成本

- GEPA 优化: ~$2-10 每次运行
- Darwinian Evolver: ~$2-9 每个任务
- 批量评估: 取决于测试用例数量和模型成本

**建议**: 从小 eval 集开始 (10-20 个例子)，为重要技能扩展规模。

---

## 与 Hermes 的关系

**hermes-agent-self-evolution 操作 ON hermes-agent，不是 inside 它。** 无需更改 agent repo。它从 hermes-agent 代码库读取，将进化版本写入 git 分支，为人类审查创建 PR。

| hermes-agent 组件 | 自我进化如何使用它 |
|-------------------|---------------------|
| `batch_runner.py` | 并行运行 agent 在测试任务上 |
| `environments/benchmarks/tblite/` | 基准门控 |
| `hermes_state.py` (SessionDB) | 挖掘真实使用作为 eval 数据 |
| `agent/prompt_builder.py` | 读取当前 prompt 部分 (只读) |
| `tools/registry.py` | 读取当前 tool 描述 (只读) |
| `skills/` 目录 | 读取当前 skills，将进化版本写入分支 |

---

## 快速开始

```bash
# 安装
git clone https://github.com/NousResearch/hermes-agent-self-evolution.git
cd hermes-agent-self-evolution
pip install -e ".[dev]"

# 指向你的 hermes-agent repo
export HERMES_AGENT_REPO=~/.hermes/hermes-agent

# 进化一个 skill (合成 eval 数据)
python -m evolution.skills.evolve_skill \
    --skill github-code-review \
    --iterations 10 \
    --eval-source synthetic

# 或使用 Claude Code, Copilot, Hermes 的真实会话历史
python -m evolution.skills.evolve_skill \
    --skill github-code-review \
    --iterations 10 \
    --eval-source sessiondb
```

---

## 当前边界（关键）

### 能做什么
- 新 skill 的 pipeline 连通性验证
- runtime sensitivity / variance 研究
- demonstration injection 效应量化

### 不能做什么
- 自动迁入 live Hermes（优化效果不稳定）
- 声称"skill 已被优化"（metrics 来自 demonstration bias）
- 在当前基线上追求 stable positive gain

### 重启 text-mutation 的前提
- 更强模型（GPT-4 / Claude）可用，或
- 新的架构方案（非 GEPA/BootstrapFewShot）

---

## 关联文档

- 实验仓库：`/home/conanxin/project/experiments/hermes-agent-self-evolution/`
- 基线规格：`SELF_EVOLUTION_STATUS.md`
- 验证报告：`TRI_SKILL_VALIDATION_V2.md`

---

*摄入日期: 2026-04-07*  
*状态更新: 2026-04-13*  
*迁移日期: 2026-06-20*