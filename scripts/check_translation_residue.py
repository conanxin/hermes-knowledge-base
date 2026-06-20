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

BASE_DIR = Path(__file__).parent.parent
CONTENT_DIR = BASE_DIR / "content"

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

        # 移除 Markdown 语法
        clean = re.sub(r'[#*_`\[\]\(\)]', ' ', content)
        clean = re.sub(r'https?://\S+', ' ', clean)

        # 查找可疑英文残留
        suspicious = []
        for match in SUSPICIOUS_PATTERN.finditer(clean):
            text = match.group()
            if len(text) >= MIN_SUSPICIOUS_LEN and not is_allowed(text):
                suspicious.append(text)

        # 去重并限制样例数量
        unique = list(dict.fromkeys(suspicious))[:5]
        count = len(suspicious)

        if count > 0:
            warnings.append({
                "path": str(rel_path),
                "count": count,
                "samples": unique
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
            print(f"  suspicious_count: {w['count']}")
            for sample in w['samples']:
                print(f"    - {sample}")
        print("\nSTATUS: WARNING — review samples above")
        return 0  # 非零退出码表示失败，这里只做 warning
    else:
        print("\nSTATUS: PASS — no suspicious residue found")
        return 0


if __name__ == "__main__":
    import sys
    sys.exit(check_translation_residue())
