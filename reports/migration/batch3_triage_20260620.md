# Batch 3 筛选评估报告

**日期**: 2026-06-20
**目标**: 只读评估 Batch 3 候选内容，筛选真正值得迁移的项目报告、Workshop 笔记或长期参考资料
**约束**: 不修改、不移动、不删除旧知识库任何文件；不创建迁移内容；不 commit

---

## STATUS: PASS

---

## Batch 3 扫描总数

| 来源目录 | 文件数 | 类型 |
|----------|--------|------|
| `~/.hermes/workspace/reports/` | 66 | 项目报告、健康检查、审计 |
| `~/.hermes/reports/hydro0x01_audit/` | 10+ | 安全审计（多阶段） |
| `~/.hermes/reports/session_guard/` | 3 | 会话安全审计 |
| `~/.hermes/wiki/research/*governance*.md` | 15+ | Skill Catalog / MLOps 治理 |
| `~/.hermes/wiki/research/*workshop*.md` | 4 | Workshop 笔记 |
| `~/.hermes/wiki/research/*wiki-ingest*.md` | 4 | Wiki 摄入维护记录 |
| **总计** | **约 100+** | — |

---

## 筛选维度

1. **长期复用价值**: 是否对未来项目或决策有参考意义
2. **用户当前项目相关性**: 是否和当前活跃项目有关
3. **清晰标题和上下文**: 是否有明确主题，而非临时日志
4. **可归入类型**: 是否能明确归入 project / note / report
5. **archive_index 适用性**: 是否只需保留索引，不迁移正文
6. **重复性**: 是否和现有 15 条记录重复

---

## 推荐迁移清单（10 篇）

### 1. Hydro0x01 安全审计总报告

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/reports/hydro0x01_audit/HYDRO0X01_LOCAL_HERMES_AUDIT.md` |
| 建议类型 | `project` |
| 建议路径 | `content/projects/2026-05-18-hydro0x01-security-audit/` |
| 推荐原因 | 完整的多阶段安全审计项目，有长期参考价值，结构清晰 |
| 相关性 | 高 — 和 Hermes 本地安全直接相关 |
| 重复性 | 无重复 |

### 2. Session Guard 预请求审查器设计

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/reports/session_guard/session_guard_1_pre_request_sanitizer_20260514_135621.md` |
| 建议类型 | `project` |
| 建议路径 | `content/projects/2026-05-14-session-guard-sanitizer/` |
| 推荐原因 | 安全功能设计文档，有实现细节和决策记录，可复用 |
| 相关性 | 高 — 和 Hermes 安全机制直接相关 |
| 重复性 | 无重复 |

### 3. Skill Catalog 治理 Phase 2 全局总结

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/wiki/research/hermes-skill-catalog-governance-phase2-global-summary-2026-04-16.md` |
| 建议类型 | `note` |
| 建议路径 | `content/legacy-knowledge/2026-04-16-skill-catalog-governance-phase2/` |
| 推荐原因 | Skill Catalog 治理的系统性总结，有方法论价值 |
| 相关性 | 中 — 和 Skill 管理相关，用户有 skill 维护需求 |
| 重复性 | 无重复 |

### 4. MLOps 治理 Phase 2 总结

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/wiki/research/hermes-mlops-governance-phase2-summary-2026-04-16.md` |
| 建议类型 | `note` |
| 建议路径 | `content/legacy-knowledge/2026-04-16-mlops-governance-phase2/` |
| 推荐原因 | MLOps 子组治理总结，有组织架构和方法论参考价值 |
| 相关性 | 中 — 和 MLOps 子组管理相关 |
| 重复性 | 无重复 |

### 5. Local Hermes Workshop 适配性分析

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/wiki/research/local-hermes-workshop-fit-analysis-2026-04-17.md` |
| 建议类型 | `note` |
| 建议路径 | `content/legacy-knowledge/2026-04-17-local-hermes-workshop-fit/` |
| 推荐原因 | Workshop 设计分析，有教育场景参考价值 |
| 相关性 | 中 — 和 Workshop 设计相关 |
| 重复性 | 无重复 |

### 6. Hermes 本地能力审计

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/workspace/reports/HERMES_LOCAL_CAPABILITY_AND_CRON_AUDIT_20260617_170106.md` |
| 建议类型 | `report` |
| 建议路径 | `content/legacy-knowledge/2026-06-17-hermes-local-capability-audit/` |
| 推荐原因 | 本地 Hermes 能力盘点，有运维参考价值 |
| 相关性 | 高 — 直接相关 |
| 重复性 | 无重复 |

### 7. Hermes 本地治理清理 R1

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/workspace/reports/HERMES_LOCAL_GOVERNANCE_CLEANUP_R1_20260617_171447.md` |
| 建议类型 | `report` |
| 建议路径 | `content/legacy-knowledge/2026-06-17-hermes-local-governance-cleanup/` |
| 推荐原因 | 治理清理决策记录，有方法论价值 |
| 相关性 | 中 — 和治理相关 |
| 重复性 | 无重复 |

### 8. Readers Convert MVP Phase 1

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/workspace/reports/READERS_CONVERT_MVP_PHASE1_20260614_131756.md` |
| 建议类型 | `project` |
| 建议路径 | `content/projects/2026-06-14-readers-convert-mvp/` |
| 推荐原因 | 产品 MVP 设计文档，有项目参考价值 |
| 相关性 | 中 — 和产品设计相关 |
| 重复性 | 无重复 |

### 9. Open Notebook Hermes Router V1.2

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/workspace/reports/OPEN_NOTEBOOK_HERMES_ROUTER_V1_2_SOURCE_HINTS_20260619.md` |
| 建议类型 | `project` |
| 建议路径 | `content/projects/2026-06-19-hermes-router-v1-2/` |
| 推荐原因 | 路由设计文档，有架构参考价值 |
| 相关性 | 高 — 和 Hermes 架构直接相关 |
| 重复性 | 无重复 |

### 10. Open Notebook Hermes Real Workflow Pilot

| 字段 | 值 |
|------|-----|
| 旧路径 | `~/.hermes/workspace/reports/OPEN_NOTEBOOK_HERMES_REAL_WORKFLOW_PILOT_V1_20260619.md` |
| 建议类型 | `project` |
| 建议路径 | `content/projects/2026-06-19-hermes-real-workflow-pilot/` |
| 推荐原因 | 工作流试点设计，有流程设计参考价值 |
| 相关性 | 高 — 和 Hermes 工作流直接相关 |
| 重复性 | 无重复 |

---

## 明确跳过清单

### 系统日志/健康检查（跳过原因：临时性、无长期价值）

| 文件 | 跳过原因 |
|------|----------|
| `HERMES_LOCAL_HEALTHCHECK_ENABLEMENT_R5_*.md` | 一次性健康检查启用记录 |
| `HERMES_LOCAL_HEALTHCHECK_VISIBILITY_R4_*.md` | 一次性健康检查可视化记录 |
| `HERMES_LOCAL_P1_MINIMAL_CLEANUP_R3_*.md` | 一次性清理记录 |
| `HERMES_LOCAL_R6_CLOSURE_VALIDATION_R7_*.md` | 一次性关闭验证记录 |
| `HERMES_LOCAL_SKILL_CATALOG_AND_LOGGER_R6_*.md` | 一次性日志记录 |
| `HERMES_LOCAL_TASK_OBSERVABILITY_R2_*.md` | 一次性任务观测记录 |

### Wiki 摄入维护（跳过原因：系统维护日志，非知识内容）

| 文件 | 跳过原因 |
|------|----------|
| `wiki-ingest-daily-failure-diagnosis-*.md` | 系统故障诊断日志 |
| `wiki-ingest-daily-fix-*.md` | 系统修复记录 |
| `wiki-ingest-daily-observation-record-*.md` | 系统观测记录 |
| `wiki-ingest-daily-postfix-smoke-*.md` | 系统冒烟测试记录 |

### 治理子组详细配置（跳过原因：过于细碎，已包含在全局总结中）

| 文件 | 跳过原因 |
|------|----------|
| `hermes-ai-development-group-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-autonomous-ai-agents-group-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-devops-group-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-manage-group-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-mlops-cloud-subgroup-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-mlops-evaluation-subgroup-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-mlops-inference-subgroup-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-mlops-models-subgroup-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-mlops-training-subgroup-governance-phase2-*.md` | 子组配置，已包含在全局总结 |
| `hermes-mlops-vector-databases-subgroup-governance-phase2-*.md` | 子组配置，已包含在全局总结 |

### 临时报告/中间状态（跳过原因：过时、不完整）

| 文件 | 跳过原因 |
|------|----------|
| `hermes-skill-catalog-maintenance-report-*.md` | 仅 324 字节，内容过少 |
| `hermes-skill-catalog-governance-phase1-*.md` | 已被 Phase 2 总结替代 |
| `hermes-skill-catalog-governance-phase3-backlog-*.md` | 中间状态，未完结 |
| `ODL_PDF_HERMES_CONFIG_AUDIT_*.md` | 一次性配置审计 |
| `ODL_PDF_HERMES_INTEGRATION_PHASE1_*.md` | 一次性集成记录 |
| `OPEN_NOTEBOOK_API_CAPABILITY_PROBE_*.md` | 一次性能力探测 |
| `OPEN_NOTEBOOK_DOCKER_PERMISSION_DIAG_*.md` | 一次性诊断记录 |
| `OPEN_NOTEBOOK_ENV_DRIFT_FIX_AND_CLEANUP_*.md` | 一次性环境修复 |
| `OPEN_NOTEBOOK_HERMES_FINALIZE_CONTRACT_V1_*.md` | 一次性合同记录 |
| `OPEN_NOTEBOOK_HERMES_INBOX_WRITER_V1_*.md` | 一次性功能设计 |
| `OPEN_NOTEBOOK_HERMES_INBOX_WRITER_V1_1_DUPLICATE_GUARD_*.md` | 一次性功能设计 |
| `OPEN_NOTEBOOK_HERMES_NOTEBOOK_ROUTER_V1_*.md` | 已被 V1.2 替代 |
| `OPEN_NOTEBOOK_HERMES_NOTEBOOK_ROUTER_V1_1_SCORING_AND_OVERRIDE_*.md` | 已被 V1.2 替代 |
| `OPEN_NOTEBOOK_HERMES_REPORT_ARCHIVE_HOOK_V1_*.md` | 一次性功能设计 |
| `OPEN_NOTEBOOK_HERMES_ROUTER_V1_2_SOURCE_HINTS_*.md` | 已推荐迁移 |
| `OPEN_NOTEBOOK_HERMES_TASK_TEMPLATE_SOURCE_HINTS_V1_*.md` | 一次性模板设计 |
| `OPEN_NOTEBOOK_LOCAL_SIDECAR_INTEGRATION_*.md` | 一次性集成记录 |
| `OPEN_NOTEBOOK_SINGLE_WRITE_SMOKE_*.md` | 一次性冒烟测试 |
| `HERMES_TASK_ASSET_INDEX_*.md` | 一次性资产索引 |

### Workshop 观察笔记（跳过原因：个人碎片笔记，结构松散）

| 文件 | 跳过原因 |
|------|----------|
| `local-hermes-workshop-continuity-closure-note-*.md` | 个人 Workshop 笔记，结构松散 |
| `local-hermes-workshop-observation-note-*.md` | 个人 Workshop 笔记，结构松散 |

---

## 重复项清单

| 潜在重复 | 现有记录 | 评估 |
|----------|----------|------|
| `hermes-skill-catalog-governance-phase2-global-summary-*.md` | 无直接重复 | 新内容，无重复 |
| `hermes-mlops-governance-phase2-summary-*.md` | 无直接重复 | 新内容，无重复 |
| `local-hermes-workshop-fit-analysis-*.md` | 无直接重复 | 新内容，无重复 |
| `HYDRO0X01_LOCAL_HERMES_AUDIT.md` | 无直接重复 | 新内容，无重复 |
| `session_guard_*.md` | 无直接重复 | 新内容，无重复 |

**结论**: Batch 3 推荐迁移内容和现有 15 条记录无重复。

---

## 是否建议进入 Batch 3 Pilot

**建议**: 可以进入 Batch 3 pilot，但需控制范围。

**理由**:
1. 从 100+ 篇中筛选出 10 篇推荐迁移，质量可控
2. 推荐内容有明确长期价值，和现有记录无重复
3. 建议先迁移 2 篇作为试点，验证流程后再扩展

**风险**:
1. Batch 3 内容多为项目报告，metadata 补全成本高
2. 部分内容为临时快照，时效性有限
3. 需要人工判断的内容较多，自动化程度低

---

## 建议 Pilot 2 篇

### 首选：Hydro0x01 安全审计总报告

| 字段 | 值 |
|------|-----|
| 原因 | 最完整的项目报告，有明确结构，长期价值高 |
| 类型 | `project` |
| 难度 | 中 — 需要补充 metadata 和整理子报告索引 |
| 预期工作量 | 60-90 分钟 |

### 次选：Session Guard 预请求审查器设计

| 字段 | 值 |
|------|-----|
| 原因 | 安全功能设计文档，结构清晰，和现有安全内容互补 |
| 类型 | `project` |
| 难度 | 低 — 结构清晰，metadata 易补全 |
| 预期工作量 | 30-60 分钟 |

---

## 总结

| 指标 | 数值 |
|------|------|
| 扫描总数 | 约 100+ 篇 |
| 推荐迁移 | 10 篇 |
| 明确跳过 | 约 90+ 篇 |
| 重复项 | 0 |
| 建议 pilot | 是，先迁移 2 篇 |
| 首选 pilot | Hydro0x01 安全审计总报告 |
| 次选 pilot | Session Guard 预请求审查器设计 |

**结论**: Batch 3 内容虽多，但经筛选后质量可控。建议先试点 2 篇，验证迁移流程后再决定是否扩展。
