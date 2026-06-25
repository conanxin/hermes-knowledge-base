# youtube-brief

> **命令名称**: `youtube-brief`
> **用途**: 把 YouTube 视频转成中文知识包
> **Workflow**: `youtube-video-brief-workflow.md`
> **创建时间**: 2026-06-25
> **版本**: 1.0

---

## 一句话说明

提供一个 YouTube 链接，自动生成包含字幕、翻译、深度解读、知识卡片和分享文章的完整中文知识包。

---

## 最短调用方式

```
解读这个 YouTube 视频：https://youtu.be/VIDEO_ID
```

---

## 标准调用方式

```
请按照 youtube-video-brief-workflow.md 处理这个 YouTube 视频：https://youtu.be/VIDEO_ID
```

---

## 输出目录规则

```
~/.openclaw/workspace/outputs/youtube-video-brief/YYYYMMDD-video-title-slug/
```

**示例**:
```
~/.openclaw/workspace/outputs/youtube-video-brief/20260625-conan-harvard-commencement-2026/
```

---

## 输出文件清单（11 个）

### 核心交付物（6 个）
| 文件 | 说明 |
|------|------|
| `metadata.json` | 视频元数据（标题、频道、时长、发布日期、字幕来源） |
| `transcript.original.srt` | 原始英文字幕 |
| `transcript.zh.md` | 中文翻译字幕（带时间戳） |
| `transcript.bilingual.md` | 双语对照字幕 |
| `analysis.zh.md` | 深度解读（分段分析、核心观点、背景补充、应用建议） |
| `summary-post.zh.md` | 分享文章（适合收藏/发布，标题 ≤ 20 字） |

### 知识库交付物（3 个）
| 文件 | 说明 |
|------|------|
| `index.md` | 知识库总入口（推荐阅读顺序、适合谁读） |
| `notes.md` | 永久笔记（核心问题、观点、可迁移方法） |
| `cards.md` | 知识卡片（10 张可复用卡片） |

### 其他（2 个）
| 文件 | 说明 |
|------|------|
| `cover.jpg` | 视频封面图 |
| `report.md` | 执行报告（执行过程、字幕来源、文件清单） |

---

## 成功案例路径

```
~/.openclaw/workspace/outputs/youtube-video-brief/20260625-conan-harvard-commencement-2026/
```

**案例内容**: Conan O'Brien 哈佛大学 2026 毕业典礼演讲（24 分 53 秒）

---

## 注意事项

| 规则 | 说明 |
|------|------|
| ❌ 不登录账号 | 不登录 YouTube/Google 账号 |
| ❌ 不读取 Cookie | 不读取浏览器 Cookie |
| ❌ 不下载完整视频 | 仅提取字幕和元数据，不下载视频文件 |
| ⚠️ 无字幕时 BLOCKED | 如果视频没有任何字幕，标记为 BLOCKED，不擅自重型转写 |
| ✅ 字幕优先级 | 人工英文字幕 → 自动英文字幕 → 其他可用字幕 |

---

## 失败处理

| 场景 | 处理 |
|------|------|
| 无字幕 | BLOCKED，记录到 report.md，建议用户确认是否音频转写 |
| 需要音频转写 | BLOCKED，重型 Whisper 转写需用户明确授权 |
| 视频不可访问 | BLOCKED，记录错误信息，建议更换网络或确认链接 |
| 翻译失败 | PARTIAL_PASS，保留英文原文，说明未翻译部分 |

---

## 关联文档

| 文档 | 路径 |
|------|------|
| 完整 Workflow 文档 | `~/.openclaw/workspace/docs/workflows/youtube-video-brief-workflow.md` |
| 本命令说明 | `~/.openclaw/workspace/docs/commands/youtube-brief-command.md` |

---

## 快捷调用示例

```
# 最短调用
解读这个 YouTube 视频：https://youtu.be/F3fCktnkBbc

# 标准调用
请按照 youtube-video-brief-workflow.md 处理这个 YouTube 视频：https://youtu.be/F3fCktnkBbc

# 带输出目录指定
请解读这个 YouTube 视频：https://youtu.be/VIDEO_ID
输出到：~/my-videos/
```

---

*命令文档固化完成。可直接复制调用示例使用。*
