# YouTube Video Brief — OpenClaw Workflow

> **版本**: 1.0
> **创建时间**: 2026-06-25
> **来源**: 固化自 Conan O'Brien Harvard 2026 毕业演讲解读成功案例
> **成功案例路径**: `~/.openclaw/workspace/outputs/youtube-video-brief/20260625-conan-harvard-commencement-2026/`

---

## 工作流名称

**YouTube Video Brief** — 一站式 YouTube 视频知识包生成

## 一句话描述

提供一个 YouTube URL，自动生成包含元数据、字幕、翻译、深度解读、知识卡片、分享文章和报告的完整知识包。

---

## 输入

| 参数 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `YouTube URL` | ✅ | — | 完整 YouTube 链接或视频 ID |
| `目标语言` | ❌ | `zh-Hans` | 翻译目标语言代码 |
| `输出目录` | ❌ | 自动命名 | 格式：`YYYYMMDD-video-title-slug/` |

---

## 输出文件清单

### 核心交付物（10 个）

| 文件 | 类型 | 说明 | 必含 |
|------|------|------|------|
| `metadata.json` | 元数据 | 标题、频道、时长、发布日期、字幕来源、语言信息 | ✅ |
| `transcript.original.srt` | 原始字幕 | 英文字幕 SRT 格式（或 VTT） | ✅ |
| `transcript.zh.md` | 中文翻译 | 带时间戳的纯中文翻译 | ✅ |
| `transcript.bilingual.md` | 双语对照 | 英文+中文逐段对照 | ✅ |
| `analysis.zh.md` | 深度解读 | 结构分析、核心概念、背景补充、应用建议 | ✅ |
| `summary-post.zh.md` | 分享文章 | 适合收藏/发布的中文总结（标题 ≤ 20 字） | ✅ |
| `cover.jpg` | 封面图 | 视频缩略图 | ✅ |

### 知识库交付物（3 个）

| 文件 | 类型 | 说明 | 必含 |
|------|------|------|------|
| `index.md` | 总入口 | 视频信息、文件清单、推荐阅读顺序、适合谁读 | ✅ |
| `notes.md` | 永久笔记 | 核心问题、观点、概念、可迁移方法、追问问题 | ✅ |
| `cards.md` | 知识卡片 | 10 张可复用卡片（概念+解释+例子+场景） | ✅ |

### 执行记录（1 个）

| 文件 | 类型 | 说明 |
|------|------|------|
| `report.md` | 执行报告 | 执行结果、字幕来源、段落数、文件清单、缺失说明、后续建议 |

---

## 标准执行步骤

### Step 1: 获取 Metadata
- 使用 `baoyu-youtube-transcript` 或 `yt-dlp` 获取视频信息
- 提取字段：title, channel, duration, publish_date, url, video_id, description
- 保存 `metadata.json`
- 同时下载 `cover.jpg`

### Step 2: 提取字幕
- **优先级**（按顺序尝试）：
  1. 人工创建英文字幕（`en` manual）
  2. 自动英文字幕（`en` auto-generated）
  3. 其他可用语言字幕
  4. 如果目标语言已有字幕（如 `zh-Hans` / `zh-Hant`），优先使用并跳过翻译
- 保存为 `transcript.original.srt`（或 `.vtt`）
- 如果**没有任何字幕** → 进入失败处理流程

### Step 3: 翻译字幕（如需要）
- 如果源语言 ≠ 目标语言，执行 AI 翻译
- 保留原始时间戳
- 分段数通常为 30-60 段（根据视频长度自动分块）
- 翻译要求：保留原文风格（幽默、讽刺、口语化等）
- 输出：`transcript.zh.md`（纯中文）+ `transcript.bilingual.md`（双语对照）

### Step 4: 生成深度解读（analysis.zh.md）
基于翻译字幕，生成结构化分析：
- 这个视频主要讲了什么（1 段总结）
- 分段解读（5-7 个部分）
- 核心观点（3-5 条）
- 关键概念解释（专有名词、文化梗、背景知识）
- 背景补充（时间、地点、政治/社会语境）
- 值得注意的论据（引用原文 + 分析）
- 可能的问题、争议或局限
- 对中国的启发（以中国职场人/创业者视角）
- 可以如何应用（具体可操作建议）

### Step 5: 生成分享文章（summary-post.zh.md）
- 标题 ≤ 20 字
- 结构清晰：引言 → 核心内容 → 具体启发 → 行动建议
- 有具体内容，不空泛
- 包含原文引用和中文解读
- 800-1500 字，适合收藏或发布

### Step 6: 生成知识库入口（index.md）
- 标题 + 视频链接 + 基本信息
- 文件清单（带类型和说明）
- 一句话总结
- 适合谁读（用户画像）
- 推荐阅读顺序（1-5 步）
- 核心标签

### Step 7: 生成永久笔记（notes.md）
- 视频核心问题（1 个）
- 核心观点（原文引用 + 中文解读）
- 关键概念（表格：概念/解释/出现位置）
- 重要段落（原文+中文，3-5 段）
- 我的理解（个人化反思）
- 可迁移的方法（3 个可操作练习）
- 可以继续追问的问题（5-7 个）

### Step 8: 生成知识卡片（cards.md）
- 10 张知识卡片
- 每张卡片格式：
  - 卡片标题（概念名）
  - 核心概念（1 个词/短语）
  - 解释（3-5 句）
  - 例子（原文或演讲中的例子）
  - 可应用场景（3-5 个场景）
- 卡片可单独复制使用，也可组合成套

### Step 9: 生成执行报告（report.md）
- 执行结果：PASS / PARTIAL_PASS / BLOCKED
- 视频基本信息表格
- 字幕来源说明
- 翻译段落数
- 已生成文件清单（大小 + 说明 + 状态）
- 缺失文件说明
- 输出目录绝对路径
- 后续建议

---

## 失败处理

### 没有字幕
- 使用 `yt-dlp --list-subs` 或 `baoyu-youtube-transcript --list` 确认可用字幕
- 如果没有任何字幕 → **标记为 BLOCKED**
- 在 `report.md` 中说明：
  - 该视频无字幕
  - 建议：检查是否为英文内容，如果是 → 可考虑音频转写（需用户明确授权）
  - 如果视频非英文且无任何字幕 → 建议放弃或寻找替代资源

### 需要音频转写（Whisper/重型音频处理）
- **必须 BLOCKED**，不要擅自执行
- 原因：音频转写消耗大量计算资源，且质量不可控
- 在 `report.md` 中记录：
  - 视频无字幕
  - 建议音频转写（需用户确认）
  - 提供预估时间和资源需求
- 用户确认后，再执行转写并重新进入标准流程

### 视频不可访问
- 可能原因：地区限制、已删除、私密视频、需要登录
- 记录错误信息到 `report.md`
- 标记为 BLOCKED
- 建议：尝试更换网络环境、寻找镜像、请求用户确认视频可访问

### 翻译失败（特定语言无可用模型）
- 尝试备用翻译方案（如 fallback 到通用模型）
- 如果仍然失败 → 标记为 PARTIAL_PASS
- 保留英文原文，在 `report.md` 中说明未翻译部分

---

## 最短调用提示词

```
请对以下 YouTube 视频执行 YouTube Video Brief 工作流：
https://youtu.be/VIDEO_ID

输出目录：~/.openclaw/workspace/outputs/youtube-video-brief/
```

---

## 完整调用提示词

```
请在 cloud_openclaw 执行一个 YouTube 视频解读任务。

目标：
对这个 YouTube 视频完成：
1. 提取视频基础信息；
2. 提取字幕，优先使用官方字幕，其次使用 YouTube 自动字幕；
3. 将字幕完整翻译成中文，保留时间戳；
4. 基于字幕内容做中文深度解读；
5. 输出一个可阅读的中文知识包。

视频链接：https://youtu.be/VIDEO_ID

执行要求：
- 优先使用 baoyu-youtube-transcript 或 yt-dlp。
- 先检查视频 metadata：标题、作者/频道、发布时间、时长、URL。
- 字幕提取优先级：人工英文字幕 → 自动英文字幕 → 中文字幕 → 其他可用字幕。
- 如有英文字幕，翻译成中文；如已有中文字幕，也要整理成清晰中文稿。
- 保留原始时间戳，输出双语或中文时间轴。
- 不要登录我的 YouTube 账号，不要读取浏览器 Cookie。
- 不要下载完整视频，除非字幕完全不可用且必须转写；如果需要转写，先标记为 BLOCKED，不要擅自跑重型 Whisper/音频转写。
- 不要扩大任务范围到其他视频。

输出目录：~/.openclaw/workspace/outputs/youtube-video-brief/
请创建以日期和视频标题 slug 命名的子目录，例如：20260625-video-title-slug/

需要生成以下文件：
1. metadata.json（title, channel, duration, publish_date, url, subtitle_source, language）
2. transcript.original.srt / transcript.original.vtt（原始字幕）
3. transcript.zh.md（中文翻译字幕，保留时间戳，分段清晰）
4. transcript.bilingual.md（原文+中文，保留时间戳，方便对照阅读）
5. analysis.zh.md（主要讲了什么、分段解读、核心观点、关键概念解释、背景补充、值得注意的论据、可能的问题/争议/局限、对我的启发、可以如何应用）
6. summary-post.zh.md（适合收藏/发布的中文总结文章，标题不超过20字，结构清晰，不要空泛）
7. index.md（知识库总入口：标题、视频链接、频道/作者、发布时间、字幕来源、文件清单、一句话总结、适合谁读、推荐阅读顺序）
8. notes.md（永久笔记：核心问题、核心观点、关键概念、重要段落、我的理解、可迁移的方法、可以继续追问的问题）
9. cards.md（10 张知识卡片：卡片标题、核心概念、解释、例子、可应用场景）
10. report.md（执行过程、字幕来源、段落数、输出文件路径、失败原因和下一步建议）

最终回复：
OPENCLAW_STATUS: PASS 或 BLOCKED
OUTPUT_DIR: <输出目录绝对路径>
REPORT_PATH: <report.md 绝对路径>
FILES:
- <文件1>
- <文件2>
...
```

---

## 本次成功案例路径

```
~/.openclaw/workspace/outputs/youtube-video-brief/20260625-conan-harvard-commencement-2026/
```

**案例内容**：Conan O'Brien 哈佛大学 2026 毕业典礼演讲（24 分 53 秒）

**案例特点**：
- 视频有官方人工英文字幕（baoyu-youtube-transcript 成功提取）
- 46 段翻译，保留时间戳
- 中文翻译保留 Conan 的幽默、自嘲和讽刺风格
- 深度解读包含 7 部分结构分析、关键概念解释、政治背景补充、中国视角应用建议
- 分享文章标题："让哈佛成为你最不重要的事"（12 字）
- 10 张知识卡片覆盖：标签钝化、社群属性、转型、运气、成就内化、自嘲、不擅长、喜剧批评、算法自恋、后学历学习

---

## 后续可扩展方向

### 1. 导入 Hermes
- 将 `metadata.json` + `analysis.zh.md` + `notes.md` 自动导入 Hermes 知识库
- 建立标签索引，支持后续语义检索
- 自动关联相似视频/演讲/主题

### 2. 导入 Open Notebook
- 将 `notes.md` 自动转换为 Open Notebook 格式
- 建立双向链接（核心概念 ↔ 其他笔记）
- 支持每日回顾和间隔重复

### 3. 生成小红书笔记
- 从 `summary-post.zh.md` 提取核心观点
- 重新排版为小红书格式（短段落、emoji、 hashtag）
- 自动配图（cover.jpg + 金句截图）

### 4. 生成公众号文章
- 从 `summary-post.zh.md` 扩展为长文
- 添加导语、互动话题、延伸阅读
- 自动生成封面图（基于 cover.jpg + 标题 overlay）

### 5. 生成播客提纲
- 从 `analysis.zh.md` 提取讨论要点
- 生成 3-5 个讨论话题 + 时间分配
- 自动生成开场白和结束语

### 6. 生成 Anki 卡片
- 从 `cards.md` 提取核心概念
- 自动生成正面/背面 Anki 格式（.apkg 或纯文本）
- 支持音频朗读（TTS）

---

## 技术栈

| 工具 | 用途 | 备注 |
|------|------|------|
| `baoyu-youtube-transcript` | 字幕提取、元数据获取 | 首选，无需 API key |
| `yt-dlp` | 备选字幕提取 | 需要安装 |
| OpenClaw subagent | 翻译、分析、生成 | 隔离执行，不污染主会话 |
| `metadata.json` | 数据交换格式 | 被所有下游步骤读取 |
| 文件系统 | 协调层 | 无 API 调用，无消息队列 |

---

## 维护说明

- 每次执行成功后，更新 `report.md` 中的 `generated_at` 字段
- 如遇到新类型的失败，更新"失败处理"章节
- 新增扩展方向时，在"后续可扩展方向"追加
- 版本升级时，更新版本号并记录变更日志

---

*Workflow 固化完成。可直接复制"最短调用提示词"或"完整调用提示词"使用。*
