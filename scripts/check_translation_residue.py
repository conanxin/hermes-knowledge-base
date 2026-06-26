#!/usr/bin/env python3
"""
轻量英文残留检查脚本
扫描所有 translation.zh-CN.md，识别明显可疑的英文残留。
专有名词、URL、代码、文件名、括号中的英文原名不算严重问题。
输出每篇文章的 suspicious_count 和简短样例。
该脚本只做 warning，不作为硬失败。
"""

import os
import re
from pathlib import Path
import yaml

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"
ALLOWLIST_FILE = BASE_DIR / "config" / "translation_residue_allowlist.yaml"

# 加载 allowlist
ALLOWLIST = []
if ALLOWLIST_FILE.exists():
    try:
        with open(ALLOWLIST_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
            ALLOWLIST = data.get("allowed_residues", [])
    except Exception:
        ALLOWLIST = []

def is_allowlisted(rel_path, text):
    """检查文本是否在 allowlist 中"""
    for entry in ALLOWLIST:
        if entry.get("token") in text:
            # 路径匹配：支持精确匹配或后缀匹配
            entry_path = entry.get("path", "")
            # 将 allowlist path 转为相对路径比较
            entry_rel = Path(entry_path).relative_to(BASE_DIR) if entry_path.startswith(str(BASE_DIR)) else Path(entry_path)
            check_rel = Path(rel_path)
            # 比较目录或文件路径
            if str(entry_rel) == str(check_rel) or str(entry_rel.parent) == str(check_rel) or str(entry_rel).startswith(str(check_rel)):
                return True
    return False

# 允许保留的英文模式（不算严重问题）
ALLOWED_PATTERNS = [
    r'https?://\S+',           # URL
    r'\[[^\]]+\]\([^\)]+\)',   # Markdown 链接
    r'`[^`]+`',                # 代码
    r'\*\*[^\*]+\*\*',         # 粗体
    r'\*[^\*]+\*',             # 斜体
    r'[A-Z][a-z]+\s+[A-Z][a-z]+',  # 人名（如 Steven Spielberg）
    r'[A-Z]{2,8}',             # 缩写（如 NASA, JR, NDC）
    r'[a-z]+\.[a-z]+',         # 文件名（如 .md, .py）
    r'\([^\)]*[a-zA-Z]+[^\)]*\)',  # 括号中的英文
    r'\d{4}-\d{2}-\d{2}',      # 日期
    r'\d+\.\d+',               # 数字
    r'\d+%',                   # 百分比
    r'\d+[KMkm]',              # 单位
    r'\d+\.\d+[KMkm]',         # 带小数单位
    r'\d+[xX]\d+',             # 分辨率
    r'\d+[a-zA-Z]+',           # 数字+字母
    r'[A-Z][a-z]+\d+',         # 型号
    r'\d+\.\d+\.\d+',          # 版本号
    r'v\d+\.\d+',              # 版本
    r'\d{1,3}(,\d{3})+',       # 千分位数字
    r'\$\d+',                  # 金额
    r'\d+\s*[a-zA-Z]+',        # 数字+单位
    r'[A-Z][a-z]+-[A-Z][a-z]+', # 连字符人名
    r'[A-Z][a-z]+\s+[A-Z]\.\s*[A-Z][a-z]+', # 中间名缩写
    r'\b[A-Z]{1,2}\b',         # 单字母缩写
    r'\b[a-z]+\b',             # 单个小写单词（可能是未翻译）
]

# 可疑模式：连续多个英文单词
SUSPICIOUS_PATTERN = re.compile(r'[a-zA-Z]{2,}(?:\s+[a-zA-Z]{2,}){2,}')

# 最小可疑长度
MIN_SUSPICIOUS_LEN = 15


def strip_html_comments(text):
    """剥离 HTML 注释块（<!-- ... -->），包括单行和多行。
    HTML comments are source/build annotations, not user-visible translation text.
    它们包含 import metadata、translation notes、build hints 等，不应被当作翻译残留。
    """
    return re.sub(r'<!--.*?-->', ' ', text, flags=re.DOTALL)


def is_allowed(text):
    """检查文本是否匹配允许的模式"""
    for pattern in ALLOWED_PATTERNS:
        if re.fullmatch(pattern, text):
            return True
    return False


def check_translation_residue():
    """Check translation residue in all translation.zh-CN.md files"""
    warnings = []
    total_files = 0

    for trans_file in CONTENT_DIR.rglob("translation.zh-CN.md"):
        total_files += 1
        item_dir = trans_file.parent
        rel_path = item_dir.relative_to(BASE_DIR)

        with open(trans_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 剥离 HTML 注释（v0.3.49）：注释内是 source/build metadata，不是用户可见译文
        content = strip_html_comments(content)

        # 移除 Markdown 语法
        clean = re.sub(r'[#*_`\[\]\(\)]', ' ', content)
        clean = re.sub(r'https?://\S+', ' ', clean)

        # 查找可疑英文残留
        suspicious = []
        allowlisted = []
        for match in SUSPICIOUS_PATTERN.finditer(clean):
            text = match.group()
            if len(text) >= MIN_SUSPICIOUS_LEN and not is_allowed(text):
                if is_allowlisted(str(rel_path), text):
                    allowlisted.append(text)
                else:
                    suspicious.append(text)

        # 去重并限制样例数量
        unique = list(dict.fromkeys(suspicious))[:5]
        count = len(suspicious)

        if count > 0 or allowlisted:
            warnings.append({
                "path": str(rel_path),
                "count": count,
                "samples": unique,
                "allowlisted_count": len(allowlisted),
                "allowlisted_samples": list(dict.fromkeys(allowlisted))[:3]
            })

    print(f"\n{'='*50}")
    print(f"Translation Residue Check")
    print(f"{'='*50}")
    print(f"Total files scanned: {total_files}")
    print(f"Files with warnings: {len(warnings)}")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings:
            print(f"\n  [{w['path']}]")
            if w['count'] > 0:
                print(f"  suspicious_count: {w['count']}")
                for sample in w['samples']:
                    print(f"    - {sample}")
            if w.get('allowlisted_count', 0) > 0:
                print(f"  allowlisted_count: {w['allowlisted_count']} (known non-blocker)")
                for sample in w.get('allowlisted_samples', []):
                    print(f"    ~ {sample}")
        has_real_warnings = any(w['count'] > 0 for w in warnings)
        if has_real_warnings:
            print("\nSTATUS: WARNING — review samples above")
        else:
            print("\nSTATUS: PASS — only known non-blockers found")
        return 0  # 非零退出码表示失败，这里只做 warning
    else:
        print("\nSTATUS: PASS — no suspicious residue found")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(check_translation_residue())
