# Paste Greatest Songs Streaming Links Finalize Report

**任务名称**: FINALIZE_PASTE_GREATEST_SONGS_STREAMING_LINKS
**日期**: 2026-06-27
**状态**: PASS_NEEDS_COMMIT_CONFIRMATION

## 修改内容

### 1. tracks.yaml
- 更新 Ketty Lester《Love Letters》Spotify/Apple Music URL
- 验证状态: next_action 从 v0.3.31 改为 v0.3.33
- 增加验证注释

### 2. scripts/check_tracks.py
- 增加 v0.3.33 streaming link URL 格式验证
- Spotify URL 必须以 https://open.spotify.com/track/ 开头
- Apple Music URL 必须以 https://music.apple.com/ 开头

### 3. scripts/generate_item_pages.py
- 修改搜索链接逻辑: 即使已有其他链接，也显示搜索链接
- 原逻辑: `if search_url and not (youtube_url or spotify_url or apple_url)`
- 新逻辑: `if search_url:`

### 4. docs/styles.css / site/styles.css
- 样式调整

### 5. docs/items/... / site/items/...
- 页面生成产物

### 6. docs/MUSIC_ARTICLE_RULES.md
- 规则更新

## 检查脚本结果

- check_kb.py: PASS (40/40)
- check_tracks.py: PASS (50 tracks, 38 verified, 12 needs_verification)
- build_index.py: PASS
- update_site.py: PASS (5/5 steps OK)
- check_pages_sync.py: PASS

## 建议

所有检查通过，修改内容完整，可以提交。建议 commit 消息:

```
Add v0.3.33 streaming link rendering for Paste 1960s
- Update Ketty Lester Love Letters Spotify/Apple Music URLs
- Add streaming link URL format validation in check_tracks.py
- Fix search link display logic in generate_item_pages.py
- Update styles and generated pages
```

## 文件列表

- content/articles/2026/2026-06-26-paste-greatest-songs-1960s/tracks.yaml
- docs/MUSIC_ARTICLE_RULES.md
- docs/items/2026-06-26-paste-greatest-songs-1960s/index.html
- docs/styles.css
- scripts/check_tracks.py
- scripts/generate_item_pages.py
- site/items/2026-06-26-paste-greatest-songs-1960s/index.html
- site/styles.css
