# youtube-kb-import

> **命令名称**: `youtube-kb-import`
> **用途**: 一键把 YouTube 视频解读产物加入 Hermes Knowledge Base
> **Workflow**: `youtube-video-kb-import-workflow.md`
> **基线 tag**: `v0.3.18-youtube-video-brief-kb-import`
> **创建时间**: 2026-06-26
> **版本**: 1.0

---

## 一句话说明

基于已完成的 YouTube Video Brief 产物，自动完成知识库入库、能力说明补充、索引更新和站点发布。

---

## 最短调用方式

```
请把这个 YouTube 视频解读产物加入知识库：
<youtube-video-brief-output>/20260625-conan-harvard-commencement-2026/
```

---

## 标准调用方式

```
请按照 youtube-video-kb-import-workflow.md 把以下 YouTube 视频解读产物加入知识库：
<youtube-video-brief-output>/20260625-conan-harvard-commencement-2026/

目标仓库：~/hermes-knowledge-base
```

---

## 输入要求

| 参数 | 必填 | 说明 |
|------|------|------|
| `产物目录` | ✅ | YouTube Video Brief 的输出目录，包含 metadata.json、analysis.zh.md、notes.md 等 |
| `目标仓库` | ❌ | 默认 `~/hermes-knowledge-base` |

---

## 输出目录规则

**知识库条目**：
```
content/articles/YYYY/YYYY-MM-DD-video-title-slug/
```

**示例**：
```
content/articles/2026/2026-06-25-conan-harvard-commencement-2026/
```

**同步文档**：
```
docs/workflows/youtube-video-brief-workflow.md
docs/commands/youtube-brief-command.md
```

---

## 输出文件清单

### 视频知识库条目（4 个）
| 文件 | 说明 |
|------|------|
| `metadata.yaml` | 知识库元数据（title, type, category, tags, created, updated） |
| `summary.md` | 通俗文章，从 analysis.zh.md 和 summary-post.zh.md 提炼 |
| `notes.md` | 结构化笔记，从视频产物 notes.md 整理 |
| `source.md` | 来源说明，引用 workflow 和 command 文档 |

### 能力说明条目（4 个）
| 文件 | 说明 |
|------|------|
| `metadata.yaml` | 能力元数据 |
| `summary.md` | 能力介绍文章 |
| `notes.md` | 能力笔记 |
| `source.md` | 关联文档引用 |

### 同步文档（2 个）
| 文件 | 说明 |
|------|------|
| `docs/workflows/youtube-video-brief-workflow.md` | OpenClaw 工作流文档 |
| `docs/commands/youtube-brief-command.md` | OpenClaw 命令文档 |

### 报告（1 个）
| 文件 | 说明 |
|------|------|
| `reports/youtube_video_brief_kb_import_YYYYMMDD.md` | 入库执行报告 |

---

## 成功案例路径

**基线 tag**: `v0.3.18-youtube-video-brief-kb-import`（commit `87f5065`）

**视频条目**：
```
content/articles/2026/2026-06-25-conan-harvard-commencement-2026/
```

**能力条目**：
```
content/articles/2026/2026-06-25-youtube-video-brief-workflow/
```

---

## 前置条件

1. ✅ YouTube Video Brief 已完成（产物目录存在且文件完整）
2. ✅ Hermes Knowledge Base 仓库已 clone（`~/hermes-knowledge-base`）
3. ✅ 仓库状态 clean（无未提交修改）

---

## 注意事项

| 规则 | 说明 |
|------|------|
| ❌ 不重新下载视频 | 只基于已有产物 |
| ❌ 不重新翻译 | 只基于已有产物 |
| ❌ 不重新生成解读 | 只基于已有产物 |
| ❌ 不 force push | 正常推送 |
| ❌ 不暴露绝对路径 | 公开文章中不写 `/home/ubuntu` 等路径 |
| ⚠️ 仓库 dirty 时 BLOCKED | 存在非本任务相关未提交改动时停止 |
| ✅ 检查脚本失败时 BLOCKED | 任何检查失败都不 commit |

---

## 失败处理

| 场景 | 处理 |
|------|------|
| 仓库 dirty | BLOCKED，报告未提交文件，建议 stash 或提交后重试 |
| 缺少产物文件 | BLOCKED，记录缺失文件，建议先执行 youtube-brief |
| check_kb.py 失败 | BLOCKED，记录错误，建议修复后重试 |
| build_index.py 失败 | BLOCKED（如果仓库要求），记录错误 |
| push 失败 | BLOCKED，记录错误，建议检查网络和权限 |

---

## 关联文档

| 文档 | 路径 |
|------|------|
| 完整 Workflow 文档 | `docs/workflows/youtube-video-kb-import-workflow.md` |
| 视频解读 Workflow | `docs/workflows/youtube-video-brief-workflow.md` |
| 视频解读命令 | `docs/commands/youtube-brief-command.md` |
| 本命令说明 | `docs/commands/youtube-kb-import-command.md` |

---

## 快捷调用示例

```
# 最短调用
请把这个 YouTube 视频解读产物加入知识库：
<youtube-video-brief-output>/20260625-conan-harvard-commencement-2026/

# 标准调用
请按照 youtube-video-kb-import-workflow.md 把以下产物加入知识库：
<youtube-video-brief-output>/20260625-conan-harvard-commencement-2026/

# 指定仓库
请把以下产物加入知识库：
<youtube-video-brief-output>/20260625-conan-harvard-commencement-2026/
目标仓库：~/my-knowledge-base
```

---

## 与 youtube-brief 的关系

```
youtube-brief → 生成视频知识包（11 个文件）
youtube-kb-import → 把知识包加入 Hermes Knowledge Base（入库 + 索引 + 发布）
```

**使用顺序**：
1. 先用 `youtube-brief` 解读视频
2. 再用 `youtube-kb-import` 把产物入库

---

*命令文档固化完成。可直接复制调用示例使用。*
