#!/usr/bin/env python3
# origin: 094CY/pr-buddy
"""
wordcount.py — 公众号口径字数统计（本 Skill 内置版）

口径：1 汉字 = 1 字；1 个英文单词 = 1 字；1 个数字串 = 1 字；中文标点计入；
      Markdown 语法、HTML 标签、空白不计；头部元信息、信息缺口清单、HTML 注释不计。

用法：
    python3 wordcount.py <article.md>            # 输出正文字数与应标注字数
    python3 wordcount.py <article.md> --json     # 机器可读输出（供 article_lint.py 使用）
    python3 wordcount.py <article.md> --html <wechat.html>   # 同时统计 HTML 正文
"""

import argparse
import html as htmllib
import json
import re

META_KEYS = ("主标题", "备选标题", "全文字数", "内容类型", "发布渠道", "主体类型")
META_LINE = re.compile(r"^\**\s*(" + "|".join(META_KEYS) + r")\s*\**\s*[:：]")
TAIL_HEADING = re.compile(r"^#{1,6}\s*(信息缺口|引用来源|参考来源|参考文献)")


def split_header(text):
    """头部 = 第一个独立 '---' 之前、且含元信息关键词的部分。返回 (头部行列表, 正文文本)。"""
    lines = text.split("\n")
    for i, line in enumerate(lines[:80]):
        if line.strip() == "---":
            head = "\n".join(lines[:i])
            if any(k in head for k in META_KEYS):
                return lines[:i], "\n".join(lines[i + 1:])
            break
    return [], text


def extract_body(text):
    """返回只含正文的 Markdown 文本（去头部元信息、首行 H1、信息缺口/引用来源及其后内容、HTML 注释）。"""
    _, body = split_header(text)
    out, in_alt, seen_content = [], False, False
    for line in body.split("\n"):
        s = line.strip()
        if TAIL_HEADING.match(s):
            break
        if META_LINE.match(s):
            in_alt = "备选标题" in s
            continue
        if in_alt:
            if s == "" or re.match(r"^\d+[.、]", s):
                continue
            in_alt = False
        if not seen_content and re.match(r"^#\s+", s):  # 正文开头的 H1 视为标题，不计入
            seen_content = True
            continue
        if s:
            seen_content = True
        out.append(line)
    body = "\n".join(out)
    return re.sub(r"<!--[\s\S]*?-->", "", body)


def strip_markdown_syntax(text):
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.M)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<!\*)\*(?!\s)(.+?)(?<!\s)\*(?!\*)", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"^\s*-{3,}\s*$", "", text, flags=re.M)
    text = re.sub(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$", "", text, flags=re.M)
    text = text.replace("|", " ")
    text = re.sub(r"^\s*>\s?", "", text, flags=re.M)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.M)
    return text


def html_article_text(html_text):
    m = re.search(r'<div[^>]*id=["\']article["\'][^>]*>([\s\S]*)</div>', html_text)
    part = m.group(1) if m else html_text
    part = re.sub(r"<(style|script)[\s\S]*?</\1>", "", part)
    part = re.sub(r"<!--[\s\S]*?-->", "", part)
    return htmllib.unescape(re.sub(r"<[^>]+>", "", part))


def count_words(text):
    chinese = re.findall(r"[\u4e00-\u9fff\u3400-\u4dbf]", text)
    cn_punct = re.findall(r"[，。！？、；：“”‘’（）—…《》【】·～「」『』〈〉〖〗〔〕]", text)
    en_words = re.findall(r"[A-Za-z]+", text)
    numbers = re.findall(r"\d+", text)
    return {
        "chinese_chars": len(chinese),
        "cn_punctuation": len(cn_punct),
        "english_words": len(en_words),
        "number_groups": len(numbers),
        "wechat_count": len(chinese) + len(cn_punct) + len(en_words) + len(numbers),
    }


def count_markdown(text):
    return count_words(strip_markdown_syntax(extract_body(text)))


def label_value(n):
    """标注值：千字以上取整到百位，百字以上取整到十位，与实测偏差始终 <10%。"""
    if n >= 1000:
        return int(round(n, -2))
    return int(round(n, -1)) if n >= 100 else n


def main():
    ap = argparse.ArgumentParser(description="公众号口径字数统计")
    ap.add_argument("file")
    ap.add_argument("--html")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    with open(args.file, encoding="utf-8") as f:
        c = count_markdown(f.read())
    result = {"file": args.file, "count": c["wechat_count"], "label": label_value(c["wechat_count"]), "detail": c}
    if args.html:
        with open(args.html, encoding="utf-8") as f:
            result["html_count"] = count_words(html_article_text(f.read()))["wechat_count"]

    if args.json:
        print(json.dumps(result, ensure_ascii=False))
        return
    print(f"正文字数（公众号口径）：{result['count']}")
    print(f"  汉字 {c['chinese_chars']} + 中文标点 {c['cn_punctuation']} + 英文词 {c['english_words']} + 数字串 {c['number_groups']}")
    if args.html:
        print(f"HTML 正文字数：{result['html_count']}")
    print(f"头部应标注：全文字数：约{result['label']}字")


if __name__ == "__main__":
    main()
