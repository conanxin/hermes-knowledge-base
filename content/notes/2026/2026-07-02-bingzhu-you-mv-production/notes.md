# Notes · 制作过程中的技术决策

## 1. 歌词改写策略

- **保留古诗原句作为 hook**:Chorus 的 "昼短苦夜长,何不秉烛游" 是 8 个字对仗+7 个字,押韵游/忧/久/收,与古诗原句完全相同。**古今双关的核心钩子在 chorus 而非 verse**。
- **现代焦虑在 verse**:CPU/deadline/KPI/PPT/月亮不睡/咖啡续,这些意象是 2026 年打工人最熟悉的。把"千岁忧"翻译成现代语言,让古诗命题有当代共鸣。
- **verse 末尾两句对比**:"古人举着火把在长夜里跳舞 / 今人攥着手机在算法里沉浮"——这个对仗把整首歌从"个人焦虑"拉到"时代对比",**Bridge 才上"时间才是真货币"这种抽象判断**。
- **Outro 拆句**:"昼短——苦夜长 / 何不——秉烛游"破折号断句给最后一击,而不是连读,让节拍有 4 个落点,适合视频结尾渐入黑场。

## 2. 音乐生成的关键参数

| 参数 | 值 | 为什么 |
|---|---|---|
| BPM | 88 | boom bap 标准节奏;古诗的 5 字句对 4/4 拍每分 88 拍刚好一句一个气口 |
| 调式 | A minor | 小调自带悲壮,与中国古诗意象匹配 |
| 风格 | old school boom bap + 古风采样 | 1989-1995 美国东岸说唱的鼓+808 sub-bass,与古筝/二胡采样叠合 |
| 男声 vocal | chest voice + slight rasp | 比清澈少年声更"有故事",与"古人说话两千年"的开场匹配 |
| 结构 | intro-verse-chorus-verse-chorus-bridge-verse-outro | 标准 3 verse,让副歌重复 2 次加深记忆点 |

## 3. 视频分两路生成的理由

**为什么不全用 I2V**:Hailuo-2.3 的 I2V 模式(first-frame image)每次都会"重新诠释"首帧里的人物,跨 clip 的人物一致性无保证。如果 4 段都用 I2V,你会看到 4 个看起来相似但不相同的人——这破坏 MV 叙事。

**为什么不全用 S2V**:S2V-01 强 subject reference 适合"书生主体"画面,但对"城市金雨"这种空镜/风景类 prompt 反而过度锁定,生成速度慢且画面构图被 subject image 牵制。

**实际选择**:
- A 段(书生举烛)+ D 段(书生走向烛光):**S2V-01** + 封面作 subject-image,确保两段书生形象一致
- B 段(城市起舞)+ C 段(金雨):**Hailuo-2.3** + 封面作 first-frame,人物退到次要位置,环境为主

## 4. 字幕烧入的工程坑

**坑 1:ffmpeg drawtext 静默黑帧**

第一次用 `drawtext=text='秉烛游':fontcolor=white:...` 时,ffmpeg 没有报错但输出的视频是全黑——所有文字 glyph 没渲染。debug 日志显示 drawtext 在跑(parsing 成功),但 `mb I skip=99.9%` 说明画面静态。

**原因**:`text='中文'` 在 bash + Python subprocess 双层转义下,中文字符可能被错误地解析为 filter chain 的子结构。drawtext 解析失败但 ffmpeg 静默继续。

**修复**:把所有要渲染的中文文本写到独立 .txt 文件,用 `textfile=路径` 引用。完全绕开 shell 转义问题。

**坑 2:libass 坐标系错位**

昨晚 v1 的 `subs.ass` 是为 1080² 视频写的。今天 v2 视频是 720²,直接用会让字幕跑到画面外 1/3。改 `PlayResX/Y` 为 720,字号从 58 降到 40、96 降到 72,完整重新校准。

**坑 3:字幕时间轴与音频不同步**

mmx 生成的 mp3 实际时长是 129.38s(显示是 2:09 整数)。ASS 文件是按 2:09 整数写的,导致最后一行字幕比音频早 ~0.4s 结束。把最后一行 end 改成 `0:02:09.40` 对齐实际音频。

## 5. Telegram 通道的物理限制

**完整 14 MB 视频 4 次都失败**:不是文件大小,178 KB 的 6s 短视频能过,3.2 MB 的 30s 预告片就超时。

**真正原因**:Telegram Bot API 上传通道对每秒视频帧的处理有时间预算,可能跟 Bot 端处理时间窗有关,而非文件总大小。**经验阈值**:≤ 1.5 MB / ≤ 12s 稳定通过,> 3 MB 偶发超时,> 10 MB 几乎必超时。

**应对**:切成 13 段 × 10.4s × ≤ 1.4 MB,稳定通过。但个别段(如 seg_02 含丰富视觉动作)1.4 MB 也可能超时——这种情况下用 crf 36 重切到 0.6 MB 兜底。

## 6. 配额管理

**D 段被配额拦**:第 4 段 AI 视频生成时返回"insufficient quota"。**做法不是降级**——等下个配额周期补做后 rebuild 完整版。

**为什么不用"3 段循环 + 延长 D 段时间"**:那样 D 段画面会和 A/B/C 段同样长,失去"收束"的语义。但**4 段各 6s = 24s** 循环 6 次到 144s,实际我们只需要 129s,所以 v2 用 6 个完整循环覆盖完整音频。

## 7. 视觉验证的局限

**本地 vision API 不可用**(`MiniMax-M3` 模型限制),无法用 vision_analyze 自动判断抽帧画面是否真的有字幕。**替代方法**:用 PIL 数非灰色像素比例(中心 300×300 区域内非灰色像素 > 5% → 字幕渲染成功)。这是粗略但可行的 fallback。

**真正可靠的视觉验证**:用户在 Telegram 看每段视频 2-3 秒,确认内容、字幕、人物一致。这是**端到端**验证,没有 shortcut。

## 8. 这条管线的可复用性

**它不是一次性**:同一套 (mmx music-2.6 + S2V-01 + Hailuo-2.3 + ffmpeg libass + 切片) 流水线可以复制到:

- 任何**诗词改唱**项目(把 4-8 句古诗词 + 现代 context,做 2 分钟说唱)
- 任何**短文学作品的 MV 化**(小说节选、散文诗、歌词可视化)
- 任何**AI 协作创作**项目(给歌词/剧本/分镜,让 AI 完成音视频)

**Prompt 模板**(可重用):

```
# 音乐 prompt 模板
"<歌曲主题> <genre>, <instruments>, <mood>, male vocal with <vocal characteristic>,
BPM <N>, key <X> <major|minor>, structure intro-verse-chorus-..."

# S2V 视频 prompt 模板
"<subject-name> performs <action>. <environment>. <camera move>. <style keywords>."

# I2V 视频 prompt 模板
"<scene description>, camera <movement>, <lighting>, <style keywords>."
```

**下一步**可以把这个管线脚本化(`scripts/bingzhu_you_pipeline.sh`),输入歌词文本+封面图,自动产出 13 段 mp4——但这是后续项目,本次先收工。
