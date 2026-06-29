# Tag Policy 建议 v0.3.65

## 推荐引入 Tag Allowlist

### 现状
- 54 篇文章，539 个唯一标签
- 平均每篇 10 个标签
- 标签过多导致检索噪音和 WARN

### 建议 Allowlist（核心标签池，约 50 个）

```
AI, technology, philosophy, politics, writing, science, history, economics,
art, literature, psychology, sociology, education, environment, health,
music, film, design, startup, innovation, ethics, future, society, culture,
media, communication, science-fiction, poetry, essay, interview, review,
analysis, critique, China, US, Europe, Japan, India, global
```

### 作者名标签策略
- 允许作者名作为标签（按需提供）
- 避免同一作者的多语言重复

### 作品名标签策略
- 允许重要作品名作为标签
- 避免同作品的多语言重复

### 待合并标签（未来版本）

| 被合并 | 目标 | 置信度 |
|--------|------|--------|
| 老子, 庄子, 道德经 | 道家 | medium |
| Twitch, Airbnb, Justin.TV | startup | medium |

### 禁止模式

1. 中英文标签重复（已在 v0.3.65 清理）
2. tag-topic 重叠（已在 v0.3.65 清理部分）
3. 体裁标签（essay, interview）— 建议移至 topics 或删除

### 实施建议

1. 先引入 allowlist 作为 warning（不阻断）
2. 观察 2-4 周
3. 根据实际使用频率调整 allowlist
4. 稳定后改为 hard limit（可选）
