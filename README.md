# Hermes Knowledge Base

个人知识库，由 Hermes agent 自动维护。

## 用途

保存文章、书籍、论文、视频、项目的完整中文翻译、摘要、背景资料和个人笔记。

## 目录结构

| 目录 | 说明 |
|------|------|
| `inbox/raw/` | 原始素材（未处理的网页、PDF、截图等） |
| `content/articles/` | 文章 |
| `content/books/` | 书籍 |
| `content/papers/` | 论文 |
| `content/videos/` | 视频 |
| `content/projects/` | 项目 |
| `index/` | 索引和目录 |
| `scripts/` | 自动化脚本 |
| `templates/` | 模板 |
| `reports/` | 运行报告 |

## 维护方式

- Hermes agent 自动抓取、翻译、归档
- `scripts/build_index.py` 自动更新索引
- `scripts/check_kb.py` 检查内容完整性
- 所有内容通过 metadata.yaml 管理元数据

## 状态标记

- `captured` — 已捕获，待处理
- `translated` — 已翻译
- `summarized` — 已摘要
- `reviewed` — 已审阅
- `archived` — 已归档
