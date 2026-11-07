#!/usr/bin/env bash
# origin: 094CY/pr-buddy
# 公众号 HTML 零改写校验：Markdown 定稿 vs 公众号 HTML，逐句、保序双向比对
# 用法: bash check_markdown_html_consistency.sh <定稿.md> <公众号.html>
# 规则：
#   - 只比对正文：MD 去掉头部元信息/信息缺口清单/HTML 注释；HTML 只取 #article，去掉 h1 与 #999 灰字（图注/图片占位）
#   - 行内标签（strong/span/em）直接去除、不断句；块级标签（p/h2/section/td…）视为断行
#   - 保留顺序、不去重：HTML 里重复出现的句子会被判为“新增”
#   - 只是换了分块方式（一段拆成两个 <p>、拆进卡片）不算差异
# 退出码：0 PASS / 1 FAIL / 2 参数错误
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "用法: $0 <定稿.md> <公众号.html>"
  exit 2
fi
if [ ! -f "$1" ] || [ ! -f "$2" ]; then
  echo "文件不存在，请检查路径"
  exit 2
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 - "$DIR" "$1" "$2" <<'PY'
import difflib, html, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from wordcount import extract_body, split_header

md_raw = open(sys.argv[2], encoding="utf-8").read()
html_raw = open(sys.argv[3], encoding="utf-8").read()

def norm(s):
    s = s.replace("“", '"').replace("”", '"').replace("‘", "'").replace("’", "'")
    s = re.sub(r"[\U0001F300-\U0001FAFF\u2600-\u27BF\uFE0F]", "", s)   # emoji 标记不算改字
    s = re.sub(r"\s+", "", s)
    s = re.sub(r"^(\d+[.、]|0\d|[•·\-*+])", "", s)   # 0x 为章节序号装饰
    return s

def to_sents(units):
    out = []
    for u in units:
        for s in re.split(r"(?<=[。！？!?；;])", u):
            k = norm(s)
            if k and re.search(r"[\w\u4e00-\u9fff]", k):
                out.append(k)
    return out

# ---- 标题候选 ----
head_lines, _ = split_header(md_raw)
head = "\n".join(head_lines) or "\n".join(md_raw.split("\n")[:30])
titles = set()
m = re.search(r"^\**主标题\**\s*[:：]\s*(.+)", head, flags=re.M)
if m: titles.add(norm(m.group(1)))
for t in re.findall(r"^\s*\d+[.、]\s*(.+)$", head, flags=re.M):
    titles.add(norm(re.sub(r"[（(]推荐[）)]", "", t)))
h1 = re.search(r"^#\s+(.+)$", md_raw, flags=re.M)
if h1: titles.add(norm(h1.group(1)))

# ---- Markdown 正文 → 单元 ----
md_units = []
for line in extract_body(md_raw).split("\n"):
    s = line.strip()
    if not s or re.match(r"^-{3,}$", s):
        continue
    if s.startswith("|"):
        if re.match(r"^\|?\s*:?-{3,}", s):
            continue
        md_units += [c.strip() for c in s.strip("|").split("|")]
        continue
    s = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"^#{1,6}\s+|^>\s*|^[-*+]\s+", "", s)
    s = s.replace("**", "").replace("`", "")
    s = re.sub(r"(?<!\w)\*(\S.*?\S|\S)\*(?!\w)", r"\1", s)
    md_units.append(s)

# ---- HTML 正文 → 单元 ----
m = re.search(r'<div[^>]*id=["\']article["\'][^>]*>([\s\S]*)</div>', html_raw)
part = m.group(1) if m else html_raw
part = re.sub(r"<(style|script)[\s\S]*?</\1>", "", part)
part = re.sub(r"<!--[\s\S]*?-->", "", part)
html_h1 = [norm(html.unescape(re.sub(r"<[^>]+>", "", x))) for x in re.findall(r"<h1[^>]*>([\s\S]*?)</h1>", part)]
part = re.sub(r"<h1[^>]*>[\s\S]*?</h1>", "", part)
part = re.sub(r'<p[^>]*color:\s*#999[^>]*>[\s\S]*?</p>', "", part)   # 图注 / 图片占位
part = re.sub(r"</?(p|h[2-6]|section|div|li|ul|ol|tr|td|th|table|thead|tbody|blockquote)\b[^>]*>|<br\s*/?>", "\n", part)
part = re.sub(r"<[^>]+>", "", part)
html_units = [html.unescape(x).strip() for x in part.split("\n") if x.strip()]

a, b = to_sents(md_units), to_sents(html_units)
missing, extra = [], []
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
    if op == "equal":
        continue
    if "".join(a[i1:i2]) == "".join(b[j1:j2]):
        continue  # 仅分块方式不同
    missing += a[i1:i2]
    extra += b[j1:j2]

moved = [s for s in missing if s in extra]
for s in moved:
    missing.remove(s); extra.remove(s)

warn = []
if moved:
    warn.append(f"{len(moved)} 句位置被调换（内容未改）：" + " / ".join(x[:18] + "…" for x in moved[:5]))
for t in html_h1:
    if titles and t not in titles:
        warn.append(f"HTML 主标题不在推荐/备选标题中：{t}")

print(f"MD 正文 {len(a)} 句 / HTML 正文 {len(b)} 句")
for w in warn:
    print("WARN:", w)
if not missing and not extra:
    print("PASS: 零改写校验通过（无缺失、无新增、无重复）" + ("，但有调换，确认是否有意" if moved else ""))
    sys.exit(0)
print("FAIL: 零改写校验未通过")
print(f"- MD 有、HTML 缺失/被改写：{len(missing)}")
for s in missing[:30]: print("   ", s)
print(f"- HTML 新增/改写/重复：{len(extra)}")
for s in extra[:30]: print("   ", s)
sys.exit(1)
PY
