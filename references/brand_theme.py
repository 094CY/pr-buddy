#!/usr/bin/env python3
# origin: 094CY/pr-buddy
"""
brand_theme.py — 由品牌主色推导公众号 HTML 配色（只依赖 python3 标准库）

wechat-html-template.md 的组件用一套默认色写成。本脚本按主体的品牌主色推导同一套角色色，
并可把 HTML 里的默认色一次替换成品牌色。

角色：
  primary      主色：h2 左线与序号、步骤标签底色、表头底色、色块文字（白字在其上、其在浅底上都需可读）
  signal_from  核心信号色块渐变起点（主色极浅调）
  signal_to    核心信号色块渐变终点
  soft         辅助高亮色块底色
  code_bg      预览提示框里 code 的底色

可读性：主色与白色、与自身浅色块底的对比度任一不足 4.5:1 时自动加深（太浅的主色做文字和白字底色都看不清），并在输出里说明。

用法：
  python3 brand_theme.py "#C8102E"                    # 打印配色表
  python3 brand_theme.py "#C8102E" --json             # 机器可读
  python3 brand_theme.py "#C8102E" --apply 公众号.html  # 把 HTML 中的默认色替换为品牌色（原地写回）
"""

import argparse
import json
import re
import sys

DEFAULT_PRIMARY = "#1f4e79"   # 模板默认主色（中性深蓝，用户未给品牌色时使用）


def parse_hex(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if not re.fullmatch(r"[0-9a-fA-F]{6}", h):
        raise ValueError(f"不是合法的十六进制颜色：{h}")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def to_hex(rgb):
    return "#" + "".join(f"{max(0, min(255, round(c))):02x}" for c in rgb)


def luminance(rgb):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(rgb, other, t):
    """t=0 返回 rgb，t=1 返回 other。"""
    return tuple(c + (o - c) * t for c, o in zip(rgb, other))


WHITE, BLACK = (255, 255, 255), (0, 0, 0)


def derive(primary_hex):
    src = parse_hex(primary_hex)
    p, steps = src, 0
    while (contrast(p, WHITE) < 4.5 or contrast(p, mix(p, WHITE, 0.89)) < 4.5) and steps < 40:
        p = mix(p, BLACK, 0.05)
        steps += 1
    signal_from = mix(p, WHITE, 0.93)
    signal_to = mix(p, WHITE, 0.89)
    soft = mix(p, WHITE, 0.95)
    code_bg = mix(p, WHITE, 0.89)
    theme = {
        "primary": to_hex(p),
        "signal_from": to_hex(signal_from),
        "signal_to": to_hex(signal_to),
        "soft": to_hex(soft),
        "code_bg": to_hex(code_bg),
    }
    notes = []
    if steps:
        notes.append(f"输入色 {to_hex(src)} 与白色 {contrast(src, WHITE):.2f}:1、在自身浅色块底上 {contrast(src, mix(src, WHITE, 0.89)):.2f}:1，"
                     f"未同时达到 4.5:1，已加深为 {theme['primary']}（与白色 {contrast(p, WHITE):.2f}:1）")
    notes.append(f"主色在信号色块底上的对比度 {contrast(p, signal_to):.2f}:1")
    return theme, notes


def main():
    ap = argparse.ArgumentParser(description="由品牌主色推导公众号 HTML 配色")
    ap.add_argument("color", nargs="?", default=DEFAULT_PRIMARY, help="品牌主色，如 #C8102E；不填用模板默认色")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--apply", metavar="HTML", help="把 HTML 中的模板默认色替换为品牌色，原地写回")
    a = ap.parse_args()

    try:
        theme, notes = derive(a.color)
    except ValueError as e:
        print(e)
        sys.exit(2)
    default, _ = derive(DEFAULT_PRIMARY)

    if a.apply:
        with open(a.apply, encoding="utf-8") as f:
            html = f.read()
        total = 0
        for k in theme:
            pat = re.compile(re.escape(default[k]), re.I)
            html, n = pat.subn(theme[k], html)
            total += n
        with open(a.apply, "w", encoding="utf-8") as f:
            f.write(html)
        print(f"已替换 {total} 处默认色 → 品牌色（{theme['primary']}）：{a.apply}")
        for n in notes:
            print("  - " + n)
        return

    if a.json:
        print(json.dumps({"theme": theme, "default": default, "notes": notes}, ensure_ascii=False))
        return
    print("角色           品牌色    模板默认色")
    for k in theme:
        print(f"{k:<14} {theme[k]}   {default[k]}")
    for n in notes:
        print("  - " + n)
    print("用法提示：按模板默认色写完 HTML 后，加 --apply <公众号.html> 一次替换；正文 #444、标题 #1a1a2e、灰色卡片色不随品牌变化。")


if __name__ == "__main__":
    main()
