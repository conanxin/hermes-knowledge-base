# 能力笔记：一键把 YouTube 视频加入知识库

## 核心问题

YouTube 视频解读完成后，如何让产物（字幕、翻译、分析、笔记）进入长期可检索的知识库？

## 命令形式

### 最短命令
```
请把这个 YouTube 视频解读产物加入知识库：
~/.openclaw/workspace/outputs/youtube-video-brief/20260625-conan-harvard-commencement-2026/
```

### 标准命令
```
请按照 youtube-video-kb-import-workflow.md 把以下产物加入知识库：
~/.openclaw/workspace/outputs/youtube-video-brief/20260625-conan-harvard-commencement-2026/

目标仓库：~/hermes-knowledge-base
```

## 内部流程

```
1. 检查仓库（git remote、status、结构）
2. 创建视频知识库条目（metadata.yaml + summary.md + notes.md + source.md）
3. 同步 workflow / command 文档到知识库 docs/
4. 新增知识库能力说明（YouTube Video Brief 能力文章）
5. 执行检查脚本（check_kb.py → check_translation_residue.py → build_index.py → update_site.py）
6. 生成入库报告
7. 提交和推送
```

## 输出结构

```
content/articles/2026/2026-06-25-conan-harvard-commencement-2026/
├── metadata.yaml
├── summary.md
├── notes.md
└── source.md

content/articles/2026/2026-06-25-youtube-video-brief-workflow/
├── metadata.yaml
├── summary.md
├── notes.md
└── source.md

docs/workflows/youtube-video-brief-workflow.md
docs/commands/youtube-brief-command.md

reports/youtube_video_brief_kb_import_YYYYMMDD.md
```

## 失败边界

| 场景 | 处理 |
|------|------|
| 仓库 dirty（非本任务相关未提交改动） | BLOCKED，报告未提交文件 |
| 缺少产物文件 | BLOCKED，建议先执行 youtube-brief |
| check_kb.py 失败 | BLOCKED，不 commit |
| build_index.py 失败 | BLOCKED（如果仓库要求），不 commit |
| push 失败 | BLOCKED，记录错误信息 |

## 使用场景

- **单次入库**：解读完一个视频，立即入库
- **批量入库**：多个视频解读完成后，逐个或批量入库
- **团队共享**：通过 GitHub Pages 让团队成员访问已入库视频
- **个人知识管理**：建立可检索、可关联的视频知识索引

## 下一步扩展

1. **自动扫描**：检测 `outputs/youtube-video-brief/` 中的新产物，自动提示入库
2. **多平台发布**：入库后自动生成小红书、公众号、Twitter/X 格式
3. **语义关联**：基于视频内容自动与知识库已有条目建立双向链接
4. **播客化**：从入库产物生成播客提纲和 TTS 朗读稿

## 关联能力

- **youtube-brief**：生成视频知识包（前置能力）
- **youtube-kb-import**：把知识包加入知识库（本能力）
- **Hermes Knowledge Base**：知识存储和检索基础设施
