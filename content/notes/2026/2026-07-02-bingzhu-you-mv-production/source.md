# Source · 原始资料与工具

## 古诗原典

**汉乐府《古诗十九首》之十五**

> 生年不满百,常怀千岁忧。
> 昼短苦夜长,何不秉烛游?
> 为乐当及时,何能待来兹?
> 愚者爱惜费,但为后世嗤。

**出处**:《文选》卷二十九,题为"古诗十九首"。最早由梁代萧统编入《文选》时定名,**作者佚名**,一般认为是东汉末年(约公元 1-2 世纪)文人作品,因十九首风格相近、形式相似而得名。

**历代解读**:
- 钟嵘《诗品》评为"文温以丽,意悲而远,惊心动魄,可谓几乎一字千金"
- 主题是"人生苦短、及时行乐"——这与中国传统儒家"节欲"主流话语形成有趣张力
- 末句"但为后世嗤"是反讽:**愚者攒钱不花,反而被后人笑话**——与今天"月光族 vs 储蓄族"讨论同构

## 工具栈

### 音乐生成

| 工具 | 用途 | 关键参数 |
|---|---|---|
| `mmx music generate` | 一次性生成完整音频 | model: `music-2.6`, BPM 88, key A minor, format mp3 256kbps |

**Prompt 全文**:

```
Chinese old school boom bap hip-hop rap, 808 sub-bass, vinyl crackle,
guzheng and erhu samples blended with trap hi-hats, cinematic tension
into uplifting release, male vocal with confident flow
```

**Lyrics file**:见 `summary.md` 的"改写后的歌词"段落,8 段共 ~80 行中文说唱。

### 视频生成

#### Clip A · 书生举烛(S2V-01)

```
A lone Chinese scholar in flowing traditional robes stands on a misty
rooftop at night. He slowly raises a single candle above his head.
The candle flame grows impossibly large and golden, casting warm
divine light that pushes back the dark mist. Cinematic camera slowly
pushes in. Moody, atmospheric, ancient meets mystical. Anamorphic
lens, film grain, 24fps cinematic motion.
```

**模式**:S2V-01(subject-image 用封面)· 6s · 1280×720 · 704 KB

#### Clip B · 城市起舞(I2V / Hailuo-2.3)

```
Cinematic camera pulls back from the album cover. The lone scholar
on the rooftop begins to dance with the candle held high, ancient
robes flowing. The candle flame ignites into a thousand golden sparks
that rain down over the neon cyberpunk city below. Camera tilts
down to reveal the vast cityscape. Dynamic motion, energetic,
hip-hop music video energy. Anamorphic lens flare, neon reflections,
24fps.
```

**模式**:Hailuo-2.3(first-frame 用封面)· 6s · 768×768 · 2.3 MB

#### Clip C · 金雨倾泻(I2V / Hailuo-2.3)

```
Golden rainstorm cascading over a vast neon cyberpunk city at night.
Thousands of luminous golden droplets fall slowly through the air,
each catching the city light. Camera sweeps across rooftops as
silhouetted figures dance below with arms raised. Heavy atmosphere,
fog, golden bokeh, anamorphic lens flare, 24fps cinematic motion.
```

**模式**:Hailuo-2.3 · 6s · 768×768 · 3.8 MB

#### Clip D · 收束溶光(S2V-01)

```
The Chinese scholar walks slowly forward into a vast field of
golden candlelight, viewed from behind. The camera follows him in
a long tracking shot. He raises the candle one final time, and the
entire screen dissolves into pure warm golden light. Serene,
contemplative, peaceful resolution. Slow motion, soft bokeh
particles, atmospheric fog, cinematic 24fps, anamorphic
widescreen feel.
```

**模式**:S2V-01 · 6s · 1280×720 · 818 KB

### 视频合成

| 步骤 | 命令形态 | 关键参数 |
|---|---|---|
| 标准化 | ffmpeg -vf "scale=720:720:force_original_aspect_ratio=decrease,pad=720:720:..." | 每个 clip 都到 720×720 square |
| 拼接 | ffmpeg -f concat -safe 0 | 4 段顺序连成 1 个 24s 循环单元 |
| 循环到音频 | ffmpeg -stream_loop 5 | 6 个循环 = 144s,截到 129.4s |
| 烧字幕 | ffmpeg -vf "ass=bingzhu_subs_720.ass" | libass filter,720×720 坐标系 |
| 加片头片尾 | ffmpeg drawtext=textfile=... | textfile 避开中文转义坑 |
| 切片 | ffmpeg -ss -t -crf 30 | 13 段 × 10.4s,目标 ≤ 1.4 MB |

### 字幕(ASS)关键节选

```
[Script Info]
ScriptType: V4.00+
PlayResX: 720
PlayResY: 720

[V4+ Styles]
Style: Default,Noto Sans CJK SC,40,&H00FFFFFF,...

[V4+ Events]
Dialogue: 0,0:00:00.00,0:00:04.50,Title,,0,0,0,,秉烛游
Dialogue: 0,0:00:04.50,0:00:09.00,Default,,0,0,0,,生年不满百,常怀千岁忧
Dialogue: 0,0:00:50.00,0:00:55.50,Default,,0,0,0,,昼短苦夜长 何不秉烛游
... (共 24 行 Dialogue,完整版见仓库)
```

## 仓库结构(在 `conanxin/bingzhu-you`)

```
bingzhu-you/
├── README.md                          # 仓库简介 + 收听/观看指引
├── bingzhu_you.mp3                    # 完整音频(2:09 · 4 MB · 256 kbps)
├── bingzhu_you_cover.jpg              # 封面图(1024×1024 · 343 KB)
├── bingzhu_you_lyrics.txt             # 歌词(mm music 格式)
├── bingzhu_subs_720.ass               # 字幕源文件
├── text_assets/                       # drawtext 用的文本片段
│   ├── title.txt
│   ├── subtitle.txt
│   ├── credit_composer.txt
│   ├── outro_main.txt
│   ├── outro_poem1.txt
│   ├── outro_poem2.txt
│   ├── outro_credits1.txt
│   └── outro_credits2.txt
├── clips/                             # 4 段 AI 原始素材
│   ├── A_scholar_lifts_candle.mp4
│   ├── B_dance_over_city.mp4
│   ├── C_golden_rain.mp4
│   └── D_walks_into_light.mp4
├── full_mv.mp4                        # 完整版 2:09 · 14 MB · 720×720
└── segments/                          # 13 段 Telegram 适配版
    ├── seg_01_intro.mp4
    ├── seg_02..12.mp4
    └── seg_13_outro.mp4
```

## 重现指令(给未来想复制这个流程的人)

```bash
# 1. 准备歌词文件(8 段中文说唱,带 [Verse]/[Chorus] 标签)
# 2. 生成音频
mmx music generate --prompt "..." --lyrics-file lyrics.txt --bpm 88 --out song.mp3

# 3. 并行生成 4 段 AI 视频
mmx video generate --model S2V-01 --subject-image cover.jpg --prompt "A scene" --async --download clips/A.mp4
mmx video generate --model Hailuo-2.3 --first-frame cover.jpg --prompt "B scene" --async --download clips/B.mp4
mmx video generate --model Hailuo-2.3 --first-frame cover.jpg --prompt "C scene" --async --download clips/C.mp4
mmx video generate --model S2V-01 --subject-image cover.jpg --prompt "D scene" --async --download clips/D.mp4

# 4. ffmpeg 标准化 + 拼接 + 循环到音频长度
# 5. ffmpeg 烧 ASS 字幕
# 6. ffmpeg 拼接 intro + subs版 + outro
# 7. ffmpeg 切成 ≤ 1.4 MB 小片段(约 10s 一段)
# 8. 逐段发送到 Telegram
```

## 相关资源

- **mmx CLI**:MiniMax 提供的 AI 模型统一 CLI 工具
- **ffmpeg**:开源视频处理工具,带 libass、libx264、libfreetype
- **Noto Sans CJK SC**:Google 开源中文字体,被 drawtext 和 libass 共同使用
- **Telegram Bot API**:视频上传通道对几 MB 以上 mp4 偶发超时(实测阈值 ~1.5 MB)
