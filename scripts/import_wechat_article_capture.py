#!/usr/bin/env python3
"""Import WeChat Official Account article capture into Hermes Knowledge Base.

Usage:
    python3 scripts/import_wechat_article_capture.py <path-to-capture.json>
    python3 scripts/import_wechat_article_capture.py --dry-run <path-to-capture.json>
    python3 scripts/import_wechat_article_capture.py -- <path-to-capture.json>

Input JSON schema (minimum required fields):
{
  "title": "文章标题",
  "source_url": "https://mp.weixin.qq.com/s/...",
  "account_name": "公众号名称",
  "author": "作者名（可选）",
  "published_date": "YYYY-MM-DD",
  "captured_at": "YYYY-MM-DDTHH:MM:SS",
  "content_markdown": "## 正文..."
}

Output directory:
    content/articles/YYYY/YYYY-MM-DD-wechat-<account-slug>-<title-slug>/

Files generated:
    metadata.yaml, source.md, translation.zh-CN.md, summary.md, notes.md, raw_payload.json

Exit codes:
    0 - Success
    1 - Hard stop (content incomplete / invalid)
    2 - Input error (file not found, bad JSON)
    3 - Runtime error (repo not found, write failure)
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path


# --- Constants ---
MIN_CONTENT_LENGTH = 200          # Minimum meaningful Chinese article length
MIN_PARAGRAPH_COUNT = 3           # Minimum paragraphs for a real article
TRUNCATION_MARKERS = [
    "...", "…", "阅读全文", "点击查看", "请查看", "完整内容",
    "前往查看", "前往阅读", "继续阅读", "查看原文", "查看完整",
    "阅读更多", "阅读剩余", "剩余内容", "未完待续", "待续",
    "此内容因违规无法查看", "该内容已被发布者删除", "此内容无法访问",
    "赞赏", "喜欢作者", "点击“喜欢作者”", "内容太水了，"
]
ABSTRACT_ONLY_PATTERNS = [
    r"^(?:摘要|简介)[:：]",           # Explicitly labeled as abstract/summary at start
]


def slugify(text: str, max_len: int = 40) -> str:
    """Convert Chinese/English text to URL-safe slug."""
    if not text:
        return "untitled"
    # Normalize unicode
    text = unicodedata.normalize("NFKC", text)
    # Keep Chinese characters, ASCII letters, digits
    text = re.sub(r"[^\u4e00-\u9fff\w\s-]", "", text)
    # Replace whitespace with hyphens
    text = re.sub(r"[\s]+", "-", text.strip())
    # Collapse multiple hyphens
    text = re.sub(r"-+", "-", text)
    # Truncate
    if len(text) > max_len:
        # Try to cut at a word boundary for Chinese
        text = text[:max_len].rsplit("-", 1)[0] if "-" in text[:max_len] else text[:max_len]
    return text.lower().strip("-") or "untitled"


def count_cjk_chars(text: str) -> int:
    """Count CJK characters in text."""
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def count_words_mixed(text: str) -> int:
    """Count words: CJK chars + English words."""
    cjk = count_cjk_chars(text)
    # Count English word-like tokens
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    return cjk + english_words


def validate_content_markdown(content: str, title: str) -> tuple[bool, str]:
    """
    Validate that content_markdown contains a real full article.
    Returns (is_valid, reason).
    """
    if not content or not content.strip():
        return False, "content_markdown is empty"

    content_stripped = content.strip()

    # 1. Length check
    if len(content_stripped) < MIN_CONTENT_LENGTH:
        return False, f"content too short ({len(content_stripped)} chars < {MIN_CONTENT_LENGTH})"

    # 2. CJK density check — Chinese article must have substantial Chinese text
    cjk_count = count_cjk_chars(content_stripped)
    if cjk_count < 50:
        return False, f"too few Chinese characters ({cjk_count} < 50), likely not a Chinese article body"

    # 3. Paragraph count check
    paragraphs = [p for p in content_stripped.split("\n\n") if p.strip()]
    if len(paragraphs) < MIN_PARAGRAPH_COUNT:
        return False, f"too few paragraphs ({len(paragraphs)} < {MIN_PARAGRAPH_COUNT})"

    # 4. Truncation marker check
    content_lower = content_stripped.lower()
    for marker in TRUNCATION_MARKERS:
        if marker.lower() in content_lower[-200:]:  # Check end of content
            return False, f"truncation marker detected near end: '{marker}'"

    # 5. Abstract-only check
    for pattern in ABSTRACT_ONLY_PATTERNS:
        if re.search(pattern, content_stripped, re.MULTILINE):
            # But allow if it's long enough (might just have the word "摘要" in body)
            if len(content_stripped) < 800:
                return False, f"abstract-only pattern detected and content is short"

    # 6. Title repetition check — if content is just the title repeated or title + tiny snippet
    title_clean = re.sub(r"[^\u4e00-\u9fff\w]", "", title)
    content_clean = re.sub(r"[^\u4e00-\u9fff\w]", "", content_stripped)
    if title_clean and content_clean.startswith(title_clean) and len(content_clean) - len(title_clean) < 200:
        return False, "content appears to be just the title with minimal body"

    # 7. Check for common WeChat "needs to open in app" messages
    blocked_phrases = [
        "请在微信客户端打开", "请在微信打开", "请使用微信查看", "请在手机端查看",
        "此链接无法在微信外打开", "请使用微信客户端",
    ]
    for bp in blocked_phrases:
        if bp in content_stripped:
            return False, f"blocked content phrase: '{bp}'"

    return True, ""


def generate_dedupe_key(source_url: str, title: str) -> str:
    """Generate a deduplication key from URL and title."""
    # Extract the 's' parameter from WeChat URLs if present
    url_hash = ""
    match = re.search(r"[/=]([a-zA-Z0-9_-]{10,})", source_url)
    if match:
        url_hash = match.group(1)
    title_part = slugify(title, max_len=30)
    if url_hash:
        return f"wechat:{url_hash}:{title_part}"
    return f"wechat:{title_part}"


def generate_metadata_yaml(data: dict, word_count_source: int, word_count_translation: int,
                           item_dir: Path, dedupe_key: str) -> str:
    """Generate metadata.yaml content for WeChat article."""
    title = data.get("title", "").strip()
    author = data.get("author", "").strip() or data.get("account_name", "").strip()
    published_date = data.get("published_date", "").strip()
    captured_at = data.get("captured_at", "").strip()
    # Normalize captured_at to YYYY-MM-DD if it's ISO format
    if captured_at and "T" in captured_at:
        try:
            dt = datetime.fromisoformat(captured_at.replace("Z", "+00:00"))
            captured_date = dt.strftime("%Y-%m-%d")
        except ValueError:
            captured_date = datetime.now().strftime("%Y-%m-%d")
    else:
        captured_date = captured_at or datetime.now().strftime("%Y-%m-%d")

    # Extract account_name
    account_name = data.get("account_name", "").strip()

    # Extract biz/uin from URL if available
    url_params = {}
    if "?" in data.get("source_url", ""):
        from urllib.parse import parse_qs, urlparse
        parsed = urlparse(data.get("source_url", ""))
        qs = parse_qs(parsed.query)
        for k in ["__biz", "biz", "uin"]:
            if k in qs:
                url_params[k] = qs[k][0]

    # Generate topics and tags from content
    content = data.get("content_markdown", "")
    # Simple topic extraction: first 3-5 unique keywords from content
    # (In production, this would use LLM or TF-IDF; here we use simple heuristics)
    topics = infer_topics(content, title)
    tags = infer_tags(content, title, account_name)

    yaml_content = f'''title: "{escape_yaml_string(title)}"
title_zh: "{escape_yaml_string(title)}"
source_url: "{data.get('source_url', '')}"
source_site: "{escape_yaml_string(account_name)}"
author: "{escape_yaml_string(author)}"
published_date: "{published_date}"
captured_date: "{captured_date}"
language: "zh-CN"
translation_language: "zh-CN"
status: "translated"
type: "article"
content_kind: "wechat_official_article"
source_platform: "wechat_official_account"
dedupe_key: "{dedupe_key}"
topics:
{format_yaml_list(topics, indent=2)}
tags:
{format_yaml_list(tags, indent=2)}
word_count:
  source: {word_count_source}
  translation: {word_count_translation}
wechat:
  account_name: "{escape_yaml_string(account_name)}"
  url_params:
{format_yaml_dict(url_params, indent=4)}
capture:
  tool: "openclaw-weixin"
  captured_at: "{captured_at}"
  version: "1.0"
path: "{item_dir.relative_to(Path(__file__).parent.parent).as_posix()}/"
'''
    return yaml_content


def escape_yaml_string(s: str) -> str:
    """Escape a string for YAML double-quoted scalar."""
    if not s:
        return ""
    # Escape backslashes and quotes
    s = s.replace("\\", "\\\\").replace('"', '\\"')
    return s


def format_yaml_list(items: list, indent: int = 0) -> str:
    """Format a list for YAML."""
    if not items:
        return " " * indent + '- "PLACEHOLDER"'
    lines = []
    for item in items:
        lines.append(" " * indent + f'- "{escape_yaml_string(item)}"')
    return "\n".join(lines)


def format_yaml_dict(d: dict, indent: int = 0) -> str:
    """Format a dict for YAML."""
    if not d:
        return " " * indent + "# no params extracted"
    lines = []
    for k, v in sorted(d.items()) if d else d.items():
        lines.append(" " * indent + f'{k}: "{escape_yaml_string(str(v))}"')
    return "\n".join(lines) if lines else " " * indent + "# no params extracted"


def infer_topics(content: str, title: str) -> list:
    """Infer topics from content and title."""
    # Simple heuristic: extract common Chinese domain words
    domain_keywords = {
        "人工智能": ["人工智能", "AI", "大模型", "机器学习", "深度学习", "神经网络"],
        "科技": ["科技", "技术", "互联网", "数字化", "算法", "编程", "代码"],
        "商业": ["商业", "创业", "投资", "融资", "市场", "品牌", "营销", "战略"],
        "产品": ["产品", "设计", "用户体验", "产品经理", "交互", "迭代"],
        "文化": ["文化", "艺术", "文学", "电影", "音乐", "阅读", "写作"],
        "社会": ["社会", "教育", "医疗", "城市", "公共", "政策", "治理"],
        "生活": ["生活", "健康", "美食", "旅行", "家居", "运动", "心理"],
        "哲学": ["哲学", "思想", "认知", "意识", "存在", "伦理", "道德"],
        "历史": ["历史", "考古", "文明", "传统", "古代", "近代"],
        "经济": ["经济", "金融", "货币", "贸易", "产业", "供应链"],
    }
    matched = []
    text = title + " " + content[:2000]
    for topic, keywords in domain_keywords.items():
        for kw in keywords:
            if kw in text:
                matched.append(topic)
                break
    if not matched:
        matched = ["阅读笔记"]
    # Limit to 3-8
    return matched[:8]


def infer_tags(content: str, title: str, account_name: str) -> list:
    """Infer tags from content and title."""
    tags = set()
    text = title + " " + content[:2000]

    # Add account as tag
    if account_name:
        tags.add(account_name)

    # Common tech tags
    tech_tags = {
        "AI": ["人工智能", "AI", "大模型", "ChatGPT", "Claude", "GPT"],
        "微信": ["微信", "公众号", "WeChat"],
        "互联网": ["互联网", "Web", "网络", "平台"],
        "创业": ["创业", "startup", "创始人"],
        "投资": ["投资", " VC", "融资", "PE ", "IPO"],
        "阅读": ["阅读", "读书", "书评", "书单"],
        "写作": ["写作", "文章", "撰稿", "文案"],
        "认知": ["认知", "思维", "心智", "心理学"],
        "健康": ["健康", "养生", "医疗", "健身"],
        "教育": ["教育", "学习", "课程", "教学"],
    }
    for tag, keywords in tech_tags.items():
        for kw in keywords:
            if kw in text:
                tags.add(tag)
                break

    # Add some generic tags if too few
    if len(tags) < 6:
        tags.update(["公众号", "文章", "阅读"])

    return list(tags)[:12]


def _split_paragraphs(content: str) -> list:
    """Split content into non-empty stripped paragraphs (headings kept inline)."""
    return [p.strip() for p in content.split("\n\n") if p.strip()]


def _extract_key_sentences(paragraphs: list, max_count: int = 8) -> list:
    """Heuristic: pick reasonably long, assertion-like sentences from the body."""
    key = []
    for p in paragraphs[:12]:
        # Skip heading lines
        if p.startswith("#"):
            continue
        sentences = re.split(r"(?<=[。！？])", p)
        for s in sentences:
            s = s.strip()
            # Keep sentences that look like assertions: 20-180 chars, CJK-rich
            if 20 <= len(s) <= 180 and count_cjk_chars(s) >= 10:
                key.append(s)
            if len(key) >= max_count:
                break
        if len(key) >= max_count:
            break
    return key


def _extract_headings(content: str) -> list:
    """Extract markdown headings (## and ###) as the article's structural skeleton."""
    heads = []
    for line in content.splitlines():
        m = re.match(r"^(#{2,4})\s+(.+)$", line.strip())
        if m:
            level = len(m.group(1))
            heads.append(f"{'  ' * (level - 2)}- {m.group(2).strip()}")
    return heads


def _infer_core_concepts(content: str, title: str) -> list:
    """Best-effort: surface candidate key concepts via high-frequency CJK 2-4 grams."""
    text = title + " " + content
    # Drop markdown noise
    text = re.sub(r"[#*`\[\]()\-]", " ", text)
    grams = {}
    # Simple 2-char CJK n-gram counting
    cjk = re.findall(r"[\u4e00-\u9fff]{2,6}", text)
    for tok in cjk:
        if len(tok) >= 2:
            grams[tok] = grams.get(tok, 0) + 1
    # Filter too-generic single grams; keep multi-char phrases with freq >= 2
    candidates = [(g, c) for g, c in grams.items() if c >= 2 and len(g) >= 2]
    candidates.sort(key=lambda x: (-x[1], -len(x[0])))
    seen = set()
    out = []
    for g, _ in candidates:
        # De-dup substrings: skip if a longer candidate already contains it
        if any(g in s and g != s for s in seen):
            continue
        seen.add(g)
        out.append(g)
        if len(out) >= 8:
            break
    return out


def generate_summary_md(title: str, content: str, author: str, account_name: str) -> str:
    """Generate summary.md — structured analytical summary.

    Covers the 9 required analysis facets:
      一句话总结 · 文章核心问题 · 主要观点 · 论证结构 · 关键概念 ·
      背景补充 · 值得摘录的句子 · 与知识库已有条目的可能关联 · 个人阅读提示

    Heuristic fills are produced where the text supports them; interpretive
    facets are emitted as clearly-marked scaffolds for the LLM operator
    (WorkBuddy) to enrich after import. The scaffold itself is valid for
    check_kb.py — no half-baked *factual* claims are invented.
    """
    paragraphs = _split_paragraphs(content)
    first_para = paragraphs[0] if paragraphs else ""
    if len(first_para) > 300:
        first_para = first_para[:300] + "..."

    key_sentences = _extract_key_sentences(paragraphs, max_count=6)
    headings = _extract_headings(content)
    concepts = _infer_core_concepts(content, title)

    key_sentences_text = "\n".join(f"{i+1}. {s}" for i, s in enumerate(key_sentences[:6])) if key_sentences \
        else "（正文较短，未提取到典型论点句；请人工补充）"
    headings_text = "\n".join(headings) if headings else "（未检测到小标题；请人工补充）"
    concepts_text = "、".join(concepts) if concepts else "（请人工补充）"

    return f'''# 摘要：{title}

**作者**：{author or "未知"}
**来源**：{account_name}

## 一句话总结

（请用一句话概括全文主旨。提示：可结合下方"文章核心问题"与"主要观点"得出。）

## 文章核心问题

（作者试图回答的中心问题是什么？例如"在 X 条件下，Y 应当如何 Z"。请人工补充。）

## 主要观点

{key_sentences_text}

## 论证结构

文章的结构骨架（按小标题还原）：

{headings_text}

## 关键概念

{concepts_text}

## 背景补充

（作者写作时的时代/行业/学术背景，以及读者需要的前置知识。请人工补充。）

## 值得摘录的句子

{key_sentences_text if key_sentences else "（请人工挑选最值得保留的 2-3 句）"}

## 与知识库已有条目的可能关联

（这篇和 KB 里已有的哪些条目主题相近、观点互补或对立？请人工或检索后补充。）

## 个人阅读提示：这篇文章为什么值得保存

（一句话说明你保存它的理由——是为了某个论点、某个案例、还是某种写法。请人工补充。）

---

## 附：首段原文（用于校对）

{first_para}
'''


def generate_notes_md(title: str, content: str) -> str:
    """Generate notes.md — structured reading notes scaffold.

    Mirrors the 9-facet analysis structure of summary.md but organized as
    personal reading notes (接受 / 反思 / 联想 / 行动 + 阅读提示).
    Interpretive sections are scaffolds for the LLM operator to enrich.
    """
    paragraphs = _split_paragraphs(content)
    key_sentences = _extract_key_sentences(paragraphs, max_count=4)
    headings = _extract_headings(content)
    concepts = _infer_core_concepts(content, title)

    key_quotes = "\n".join(f"> {s}" for s in key_sentences[:4]) if key_sentences \
        else "> （请人工挑选值得摘录的句子）"
    headings_text = "\n".join(headings) if headings else "（未检测到小标题）"
    concepts_text = "、".join(concepts[:6]) if concepts else "（请人工补充）"

    return f'''# 阅读笔记：{title}

> 个人批注，结构按"接受 / 反思 / 联想 / 行动 + 阅读提示"组织。
> 每一节都是 scaffold：脚本已尽可能用启发式填充可从正文提取的部分，
> 解释性内容（如"我同意什么""联想到哪篇 KB 条目"）留给 WorkBuddy / 读者补全。

## 一、接受（作者说服我的部分）

（作者哪些观点/论证我认可？为什么？请人工补充。）

## 二、反思（我仍存疑或需要补充的部分）

（哪些论点证据不足、哪些结论我不同意、哪些前提值得追问？请人工补充。）

## 三、联想（与其他文本 / KB 条目的呼应）

| 文本 / KB 条目 | 呼应点 |
|------|--------|
| （待补充） | （待补充） |

## 四、行动（我打算做的事情）

- [ ] （待填写：要读的下一篇 / 要做的实验 / 要写下的反驳 / 要更新的笔记）

## 五、值得摘录的句子

{key_quotes}

## 六、关键概念

{concepts_text}

## 七、文章结构（小标题还原）

{headings_text}

## 八、保留给未来自己的提醒

> （请人工补充：下次重读这篇文章时，最该想起的一句话或一个判断。）

## 九、个人阅读提示：这篇文章为什么值得保存

> （请人工补充：一句话说明保存它的理由。）
'''


def generate_source_md(title: str, source_url: str, account_name: str, author: str,
                       published_date: str, content: str) -> str:
    """Generate source.md content — the original full text."""
    header = f"# {title}\n\n"
    if author:
        header += f"**作者**：{author}\n\n"
    if account_name:
        header += f"**来源**：{account_name}\n\n"
    if published_date:
        header += f"**发布日期**：{published_date}\n\n"
    header += f"**原文链接**：{source_url}\n\n"
    header += "---\n\n"
    return header + content


def generate_translation_md(content: str) -> str:
    """Generate translation.zh-CN.md — for Chinese articles, V1 can mirror source."""
    # V1: Clean up the markdown slightly but keep the Chinese text as-is
    # Remove common WeChat footer artifacts
    cleaned = content
    # Remove excessive "Read more" type CTAs at the end
    footer_patterns = [
        r"\n+---+\n+(?:推荐阅读|精选阅读|更多阅读|相关文章|热门文章|喜欢作者|赞赏).*",
        r"\n+\d+\s*(?:人已阅读|阅读|赞|在看|分享).*",
    ]
    for pattern in footer_patterns:
        cleaned = re.sub(pattern, "", cleaned, flags=re.DOTALL | re.IGNORECASE)
    return cleaned.strip()


def main():
    parser = argparse.ArgumentParser(description="Import WeChat article capture into KB")
    parser.add_argument("capture_json", help="Path to the WeChat capture JSON file")
    parser.add_argument("--dry-run", action="store_true", help="Validate but do not write")
    parser.add_argument("--force", action="store_true", help="Skip validation (dangerous)")
    args = parser.parse_args()

    capture_path = Path(args.capture_json)
    if not capture_path.exists():
        print(f"ERROR: Capture file not found: {capture_path}", file=sys.stderr)
        sys.exit(2)

    # Load JSON
    try:
        with open(capture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"ERROR: Failed to read file: {e}", file=sys.stderr)
        sys.exit(2)

    # Extract required fields
    title = data.get("title", "").strip()
    source_url = data.get("source_url", "").strip()
    account_name = data.get("account_name", "").strip()
    author = data.get("author", "").strip()
    published_date = data.get("published_date", "").strip()
    captured_at = data.get("captured_at", "").strip()
    content_markdown = data.get("content_markdown", "")

    # Validate required fields
    missing = []
    if not title:
        missing.append("title")
    if not source_url:
        missing.append("source_url")
    if not account_name:
        missing.append("account_name")
    if not published_date:
        missing.append("published_date")
    if not captured_at:
        missing.append("captured_at")
    if missing:
        print(f"ERROR: Missing required fields: {', '.join(missing)}", file=sys.stderr)
        sys.exit(2)

    # Validate content_markdown
    if not args.force:
        is_valid, reason = validate_content_markdown(content_markdown, title)
        if not is_valid:
            print(f"HARD STOP: Content validation failed: {reason}", file=sys.stderr)
            print(f"  title: {title}", file=sys.stderr)
            print(f"  source_url: {source_url}", file=sys.stderr)
            print(f"  content length: {len(content_markdown) if content_markdown else 0}", file=sys.stderr)
            sys.exit(1)

    # Compute paths
    repo_root = Path(__file__).parent.parent
    try:
        # Try to resolve from capture file location relative to repo
        if (repo_root / "content" / "articles").exists():
            articles_dir = repo_root / "content" / "articles"
        else:
            # Fallback: try to find repo from capture path
            articles_dir = capture_path.parent.parent / "content" / "articles"
            if not articles_dir.exists():
                print(f"ERROR: Cannot find content/articles/ directory", file=sys.stderr)
                sys.exit(3)
    except Exception:
        print(f"ERROR: Cannot determine repo root", file=sys.stderr)
        sys.exit(3)

    # Parse date for directory naming
    try:
        if published_date:
            dt = datetime.strptime(published_date, "%Y-%m-%d")
        else:
            dt = datetime.now()
    except ValueError:
        dt = datetime.now()
        published_date = dt.strftime("%Y-%m-%d")

    year = dt.strftime("%Y")
    date_str = dt.strftime("%Y-%m-%d")
    account_slug = slugify(account_name, max_len=20)
    title_slug = slugify(title, max_len=40)
    dir_name = f"{date_str}-wechat-{account_slug}-{title_slug}"
    item_dir = articles_dir / year / dir_name

    # Calculate word counts
    word_count_source = count_words_mixed(content_markdown)
    cleaned_translation = generate_translation_md(content_markdown)
    word_count_translation = count_words_mixed(cleaned_translation)

    # Ensure integer counts
    word_count_source = int(word_count_source)
    word_count_translation = int(word_count_translation)

    if word_count_source <= 0 or word_count_translation <= 0:
        print(f"HARD STOP: word_count is zero or negative (source={word_count_source}, translation={word_count_translation})", file=sys.stderr)
        sys.exit(1)

    # Generate dedupe key
    dedupe_key = generate_dedupe_key(source_url, title)

    # Generate content
    metadata_yaml = generate_metadata_yaml(
        data, word_count_source, word_count_translation, item_dir, dedupe_key
    )
    source_md = generate_source_md(title, source_url, account_name, author, published_date, content_markdown)
    translation_md = cleaned_translation
    summary_md = generate_summary_md(title, content_markdown, author, account_name)
    notes_md = generate_notes_md(title, content_markdown)

    if args.dry_run:
        print("DRY RUN: Would create the following files:")
        print(f"  Directory: {item_dir}")
        print(f"  Files:")
        print(f"    - metadata.yaml ({len(metadata_yaml)} chars)")
        print(f"    - source.md ({len(source_md)} chars)")
        print(f"    - translation.zh-CN.md ({len(translation_md)} chars)")
        print(f"    - summary.md ({len(summary_md)} chars)")
        print(f"    - notes.md ({len(notes_md)} chars)")
        print(f"    - raw_payload.json ({len(json.dumps(data, ensure_ascii=False, indent=2))} chars)")
        print(f"  Word counts: source={word_count_source}, translation={word_count_translation}")
        print(f"  Dedupe key: {dedupe_key}")
        print("\nSTATUS: DRY_RUN_OK")
        sys.exit(0)

    # Create directories
    item_dir.mkdir(parents=True, exist_ok=True)

    # Write files
    try:
        (item_dir / "metadata.yaml").write_text(metadata_yaml, encoding="utf-8")
        (item_dir / "source.md").write_text(source_md, encoding="utf-8")
        (item_dir / "translation.zh-CN.md").write_text(translation_md, encoding="utf-8")
        (item_dir / "summary.md").write_text(summary_md, encoding="utf-8")
        (item_dir / "notes.md").write_text(notes_md, encoding="utf-8")
        (item_dir / "raw_payload.json").write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    except Exception as e:
        print(f"ERROR: Failed to write files: {e}", file=sys.stderr)
        sys.exit(3)

    print(f"SUCCESS: WeChat article imported to {item_dir}")
    print(f"  Word counts: source={word_count_source}, translation={word_count_translation}")
    print(f"  Dedupe key: {dedupe_key}")
    print(f"\nSTATUS: PASS")


if __name__ == "__main__":
    main()
