# 中文原文

## 说明

本文为 OpenClaw 工作流说明文档，原文即为中文，无需翻译。

## 命令名称

一键把 YouTube 视频加入知识库 — YouTube Video KB Import

## 核心流程

1. 检查仓库状态（remote、分支、clean）
2. 创建视频知识库条目（metadata.yaml + summary.md + notes.md + source.md）
3. 同步 workflow / command 文档到知识库 docs/
4. 新增知识库能力说明（YouTube Video Brief 能力文章）
5. 执行检查脚本（check_kb.py → check_translation_residue.py → build_index.py → update_site.py）
6. 生成入库报告
7. 提交和推送

## 输入

- 视频解读产物目录（YouTube Video Brief 输出）
- 目标仓库（默认 ~/hermes-knowledge-base）

## 输出

- 视频知识库条目（4 个文件）
- 能力说明条目（4 个文件）
- 同步文档（2 个文件）
- 执行报告（1 个文件）

## 失败处理原则

- 仓库 dirty → BLOCKED
- 缺少产物文件 → BLOCKED
- 检查脚本失败 → BLOCKED
- push 失败 → BLOCKED

## 扩展方向

- 自动扫描入库
- 多平台发布（小红书、公众号、Twitter/X）
- 语义关联自动建立
- 播客化
