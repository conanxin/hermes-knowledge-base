# WeChat Summary Image Live Verification v0.3.75a

STATUS: PASS

## Scope

- Task: `v0.3.75a-wechat-summary-image-live-verification`
- Verification date: 2026-07-01
- Target commit: `c834b3be0a0d7a6c81ed1e88bab32400be52eae8`
- Base URL: `https://conanxin.github.io/hermes-knowledge-base/`
- Cache-busting query used: `?v=c834b3b`
- Content mutation: none
- Image download/refetch: none
- Empty commit: no
- Push: no

## Startup State

- Required first command path: `Set-Location D:\Codex\hermes-knowledge-base`
- Branch: `main`
- Local `HEAD`: `c834b3be0a0d7a6c81ed1e88bab32400be52eae8`
- `origin/main`: `c834b3be0a0d7a6c81ed1e88bab32400be52eae8`
- `git fetch origin main --tags`: PASS

Untracked artifacts observed and preserved:

- `AGENTS.md`
- `inbox/raw/wechat/2026-06-30-测试公众号文章知识管理与长期主义*.json`
- `inbox/raw/wechat/2026-07-01-京郊徒步入门三条经典路线对比*.json`
- `reports/wechat_batch_import_20260701_141248.*`
- `reports/wechat_batch_import_20260701_141249.*`
- `reports/wechat_batch_import_20260701_141250.*`
- `reports/wechat_batch_import_20260701_141252.*`
- `reports/wechat_batch_import_20260701_143732.*`
- `reports/wechat_batch_import_20260701_143733.*`
- `reports/wechat_batch_import_20260701_143734.*`
- `reports/wechat_batch_import_20260701_143736.*`

## Local Scan

Scanned:

- `content/articles/**/*.md`
- `docs/items/**/*.html`
- `site/items/**/*.html`

Results:

| Surface | `mmbiz.qpic.cn` | `src="https://mmbiz.qpic.cn` | `![](https://mmbiz.qpic.cn` | `![` |
|---|---:|---:|---:|---:|
| `content/articles` Markdown | 0 | 0 | 0 | 202 |
| `docs/items` HTML | 0 | 0 | 0 | 0 |
| `site/items` HTML | 0 | 0 | 0 | 0 |

Notes:

- The `![` count in `content/articles` is expected because local Markdown still contains local image syntax such as `![alt](assets/...)`.
- Public HTML contains 0 bare Markdown image patterns.

Local gates:

- `python scripts/check_kb.py`: PASS, 61/61
- `python scripts/check_pages_sync.py`: PASS, 61 slugs

## Live Page Checks

All 7 current WeChat item pages under `docs/items/` were checked online. All returned HTTP 200. All had:

- `mmbiz.qpic.cn`: 0
- bare Markdown image syntax: 0
- failed checked asset URLs: 0

Summary:

- Pages checked: 7
- Pages passed: 7
- Pages failed: 0
- Live `mmbiz.qpic.cn` refs across checked pages: 0
- Live raw Markdown image refs across checked pages: 0
- Live local asset image refs found: 99
- Asset URLs checked: 16
- Asset URLs passed: 16
- Asset URLs failed: 0

The `可可乐博` page has no local image assets in the built page or local `docs/items` page; it is clean and image-free, so `src="assets/` is not applicable for that page. The 6 priority pages named in the task all include local `assets/` images.

### Per-Page Details

#### 北京热门徒步线路TOP10

- page_url: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-30-wechat-%E4%B8%A4%E6%AD%A5%E8%B7%AF-%E5%8C%97%E4%BA%AC%E7%83%AD%E9%97%A8%E5%BE%92%E6%AD%A5%E7%BA%BF%E8%B7%AFtop10/?v=c834b3b`
- http_status: 200
- mmbiz_count: 0
- raw_markdown_image_count: 0
- local_asset_img_count: 52
- checked_asset_urls:
  - `assets/image-001.gif`: 200, `image/gif`, 7,687,137 bytes
  - `assets/image-002.png`: 200, `image/png`, 74,653 bytes
  - `assets/image-003.jpg`: 200, `image/jpeg`, 452,092 bytes
- failed_asset_urls: none

#### 逆流而上的爱与勇气——写在阿伦特诞辰120周年之际

- page_url: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-28-wechat-%E6%96%87%E6%B1%87%E8%AF%BB%E4%B9%A6%E5%91%A8%E6%8A%A5-%E9%80%86%E6%B5%81%E8%80%8C%E4%B8%8A%E7%9A%84%E7%88%B1%E4%B8%8E%E5%8B%87%E6%B0%94%E5%86%99%E5%9C%A8%E9%98%BF%E4%BC%A6%E7%89%B9%E8%AF%9E%E8%BE%B0120%E5%91%A8%E5%B9%B4%E4%B9%8B%E9%99%85/?v=c834b3b`
- http_status: 200
- mmbiz_count: 0
- raw_markdown_image_count: 0
- local_asset_img_count: 10
- checked_asset_urls:
  - `assets/image-001.jpg`: 200, `image/jpeg`, 424,236 bytes
  - `assets/image-002.png`: 200, `image/png`, 2,301 bytes
  - `assets/image-003.png`: 200, `image/png`, 952,927 bytes
- failed_asset_urls: none

#### 从传统评点看金庸｜《倚天》篇：张无忌为什么总是被骗？

- page_url: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-27-wechat-%E6%BE%8E%E6%B9%83%E7%BF%BB%E4%B9%A6%E5%85%9A-%E4%BB%8E%E4%BC%A0%E7%BB%9F%E8%AF%84%E7%82%B9%E7%9C%8B%E9%87%91%E5%BA%B8%E5%80%9A%E5%A4%A9%E7%AF%87%E5%BC%A0%E6%97%A0%E5%BF%8C%E4%B8%BA%E4%BB%80%E4%B9%88%E6%80%BB%E6%98%AF%E8%A2%AB%E9%AA%97/?v=c834b3b`
- http_status: 200
- mmbiz_count: 0
- raw_markdown_image_count: 0
- local_asset_img_count: 4
- checked_asset_urls:
  - `assets/image-001.jpg`: 200, `image/jpeg`, 75,286 bytes
  - `assets/image-002.jpg`: 200, `image/jpeg`, 56,874 bytes
  - `assets/image-003.jpg`: 200, `image/jpeg`, 13,678 bytes
- failed_asset_urls: none

#### 专访林小英：接受教育，最终是为了让我们把日子过得生动

- page_url: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-wechat-%E6%96%B0%E4%BA%AC%E6%8A%A5%E4%B9%A6%E8%AF%84%E5%91%A8%E5%88%8A-%E4%B8%93%E8%AE%BF%E6%9E%97%E5%B0%8F%E8%8B%B1%E6%8E%A5%E5%8F%97%E6%95%99%E8%82%B2%E6%9C%80%E7%BB%88%E6%98%AF%E4%B8%BA%E4%BA%86%E8%AE%A9%E6%88%91%E4%BB%AC%E6%8A%8A%E6%97%A5%E5%AD%90%E8%BF%87%E5%BE%97%E7%94%9F%E5%8A%A8/?v=c834b3b`
- http_status: 200
- mmbiz_count: 0
- raw_markdown_image_count: 0
- local_asset_img_count: 14
- checked_asset_urls:
  - `assets/image-001.gif`: 200, `image/gif`, 364,147 bytes
  - `assets/image-002.jpg`: 200, `image/jpeg`, 281,731 bytes
  - `assets/image-003.gif`: 200, `image/gif`, 6,757 bytes
- failed_asset_urls: none

#### “我生病了，要去西湖玩玩才能好起来”

- page_url: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-wechat-%E8%AF%91%E6%9E%97%E5%87%BA%E7%89%88%E7%A4%BE-%E6%88%91%E7%94%9F%E7%97%85%E4%BA%86%E8%A6%81%E5%8E%BB%E8%A5%BF%E6%B9%96%E7%8E%A9%E7%8E%A9%E6%89%8D%E8%83%BD%E5%A5%BD%E8%B5%B7%E6%9D%A5/?v=c834b3b`
- http_status: 200
- mmbiz_count: 0
- raw_markdown_image_count: 0
- local_asset_img_count: 17
- checked_asset_urls:
  - `assets/image-001.jpg`: 200, `image/jpeg`, 115,744 bytes
  - `assets/image-002.png`: 200, `image/png`, 1,538,013 bytes
  - `assets/image-003.png`: 200, `image/png`, 2,494,705 bytes
- failed_asset_urls: none

#### AI无法教会的三件事

- page_url: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-26-wechat-%E8%85%BE%E8%AE%AF%E7%A0%94%E7%A9%B6%E9%99%A2-ai%E6%97%A0%E6%B3%95%E6%95%99%E4%BC%9A%E7%9A%84%E4%B8%89%E4%BB%B6%E4%BA%8B/?v=c834b3b`
- http_status: 200
- mmbiz_count: 0
- raw_markdown_image_count: 0
- local_asset_img_count: 2
- checked_asset_urls:
  - `assets/image-001.png`: 200, `image/png`, 342,154 bytes
- failed_asset_urls: none

#### 携手之外：国际学习科学年会（ISLS）2026 的五条主线

- page_url: `https://conanxin.github.io/hermes-knowledge-base/items/2026-06-28-wechat-%E5%8F%AF%E5%8F%AF%E4%B9%90%E5%8D%9A-%E6%90%BA%E6%89%8B%E4%B9%8B%E5%A4%96%E5%9B%BD%E9%99%85%E5%AD%A6%E4%B9%A0%E7%A7%91%E5%AD%A6%E5%B9%B4%E4%BC%9Aisls-2026-%E7%9A%84%E4%BA%94%E6%9D%A1%E4%B8%BB%E7%BA%BF/?v=c834b3b`
- http_status: 200
- mmbiz_count: 0
- raw_markdown_image_count: 0
- local_asset_img_count: 0
- checked_asset_urls: none; page is image-free locally and online
- failed_asset_urls: none

## Live Catalog Check

- catalog_url: `https://conanxin.github.io/hermes-knowledge-base/data/catalog.json?v=c834b3b`
- http_status: 200
- record_count: 61
- mmbiz_count: 0
- Contains v0.3.73 5 WeChat articles: yes
  - `专访林小英：接受教育，最终是为了让我们把日子过得生动`
  - `AI无法教会的三件事`
  - `“我生病了，要去西湖玩玩才能好起来”`
  - `从传统评点看金庸｜《倚天》篇：张无忌为什么总是被骗？`
  - `逆流而上的爱与勇气——写在阿伦特诞辰120周年之际`
- Contains `两步路` article: yes
- Live WeChat catalog entries found: 7

## Pages Rebuild Decision

- Local public surface has 0 `mmbiz.qpic.cn`.
- Live pages have 0 `mmbiz.qpic.cn`.
- Live catalog has 0 `mmbiz.qpic.cn`.
- GitHub Pages stale: no evidence.
- Pages rebuild needed: no
- Empty commit used: no
- Push result: N/A

## Next Steps

- No article/content action needed.
- Keep preserving untracked raw/batch artifacts unless a separate cleanup task explicitly handles them.
- Optional future hardening: make a tiny reusable live-verification script to avoid repeating the long inline URL scan.
