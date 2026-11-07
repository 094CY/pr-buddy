#!/usr/bin/env python3
# origin: 094CY/pr-buddy
"""
md_to_docx.py — 定稿 Markdown 转 .docx（只用 Python 标准库，任何电脑装了 python3 即可运行）

字体规范：Microsoft YaHei，w:rFonts 的 ascii / hAnsi / eastAsia / cs 四项全部设置；
          正文 10.5pt，H1 18pt，H2 14pt，H3 12pt，1.5 倍行距。

用法：
    python3 md_to_docx.py <定稿.md> [输出.docx] [--title 标题]
    python3 md_to_docx.py --check <文件.docx>        # 字体规范校验

转换内容：
    - 标题取头部“主标题”（或 --title），作为 H1
    - 去掉头部元信息、备选标题、信息缺口清单、HTML 注释（与 wordcount.py 同一套规则）
    - 支持 ## / ### 标题、段落、**加粗**、*斜体*、`行内代码`、无序/有序列表、引用块、表格、代码块、PNG/JPEG 图片
"""

import html
import os
import re
import struct
import sys
import zipfile

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wordcount import extract_body, split_header  # noqa: E402

FONT = "Microsoft YaHei"
ALLOWED_CN = ["微软雅黑", "Microsoft YaHei", "思源黑体", "Source Han Sans", "Noto Sans CJK SC", "Noto Sans SC", "等线", "DengXian"]
SIZES = {"title": 36, "h2": 28, "h3": 24, "body": 21}  # 半磅
EMU_PER_PX = 9525
MAX_WIDTH_EMU = int(15.0 / 2.54 * 914400)  # 正文宽度约 15cm


def esc(s):
    return html.escape(s, quote=False)


def rpr(size=None, bold=False, italic=False, color=None):
    x = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:eastAsia="{FONT}" w:cs="{FONT}"/>'
    if bold:
        x += "<w:b/><w:bCs/>"
    if italic:
        x += "<w:i/><w:iCs/>"
    if color:
        x += f'<w:color w:val="{color}"/>'
    if size:
        x += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
    return f"<w:rPr>{x}</w:rPr>"


def runs(text, size=None, base_bold=False, color=None):
    """行内 Markdown → w:r 列表"""
    out = []
    pattern = re.compile(r"(\*\*.+?\*\*|`[^`]+`|(?<![\w*])\*(?!\s).+?(?<!\s)\*(?![\w*]))")
    pos = 0
    for m in pattern.finditer(text):
        if m.start() > pos:
            out.append((text[pos:m.start()], base_bold, False))
        tok = m.group(0)
        if tok.startswith("**"):
            out.append((tok[2:-2], True, False))
        elif tok.startswith("`"):
            out.append((tok[1:-1], base_bold, False))
        else:
            out.append((tok[1:-1], base_bold, True))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], base_bold, False))
    xml = ""
    for s, b, i in out:
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
        if s:
            xml += f'<w:r>{rpr(size, b, i, color)}<w:t xml:space="preserve">{esc(s)}</w:t></w:r>'
    return xml


def para(inner, style=None, indent=0, align=None, spacing_after=120):
    ppr = ""
    if style:
        ppr += f'<w:pStyle w:val="{style}"/>'
    ppr += f'<w:spacing w:after="{spacing_after}" w:line="360" w:lineRule="auto"/>'
    if indent:
        ppr += f'<w:ind w:left="{indent}"/>'
    if align:
        ppr += f'<w:jc w:val="{align}"/>'
    return f"<w:p><w:pPr>{ppr}</w:pPr>{inner}</w:p>"


def image_size(path):
    with open(path, "rb") as f:
        data = f.read(65536)
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        w, h = struct.unpack(">II", data[16:24])
        return w, h, "png"
    if data[:2] == b"\xff\xd8":
        i = 2
        while i < len(data) - 9:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                h, w = struct.unpack(">HH", data[i + 5:i + 9])
                return w, h, "jpeg"
            seg = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + seg
    return None


class Doc:
    def __init__(self, base_dir):
        self.base = base_dir
        self.body = []
        self.media = []  # (zip 内文件名, 本地路径, rId)

    def add_image(self, src, alt):
        path = src if os.path.isabs(src) else os.path.join(self.base, src)
        info = image_size(path) if os.path.isfile(path) else None
        if not info:
            self.body.append(para(runs(f"[图片：{alt or src}]", SIZES["body"], color="999999"), align="center"))
            return
        w, h, ext = info
        n = len(self.media) + 1
        rid = f"rIdImg{n}"
        self.media.append((f"media/image{n}.{ext}", path, rid))
        cx, cy = w * EMU_PER_PX, h * EMU_PER_PX
        if cx > MAX_WIDTH_EMU:
            cy = int(cy * MAX_WIDTH_EMU / cx)
            cx = MAX_WIDTH_EMU
        drawing = (
            f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0"><wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:docPr id="{n}" name="Picture {n}"/>'
            '<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            '<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            '<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="{n}" name="image{n}"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
            "</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r>"
        )
        self.body.append(para(drawing, align="center"))
        if alt:
            self.body.append(para(runs(alt, 18, color="999999"), align="center"))

    def add_table(self, rows):
        cells_xml = ""
        for ri, row in enumerate(rows):
            tr = ""
            for c in row:
                shade = '<w:shd w:val="clear" w:color="auto" w:fill="F2F2F2"/>' if ri == 0 else ""
                tr += (f"<w:tc><w:tcPr>{shade}</w:tcPr>"
                       + para(runs(c.strip(), SIZES["body"], base_bold=(ri == 0)), spacing_after=0) + "</w:tc>")
            cells_xml += f"<w:tr>{tr}</w:tr>"
        border = "".join(f'<w:{b} w:val="single" w:sz="4" w:space="0" w:color="BFBFBF"/>'
                         for b in ("top", "left", "bottom", "right", "insideH", "insideV"))
        self.body.append(f'<w:tbl><w:tblPr><w:tblW w:w="5000" w:type="pct"/><w:tblBorders>{border}</w:tblBorders></w:tblPr>{cells_xml}</w:tbl>')
        self.body.append(para("", spacing_after=0))

    def build(self, md_text, title):
        if title:
            self.body.append(para(runs(title, SIZES["title"], base_bold=True), style="Title"))
        lines = md_text.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i]
            s = line.strip()
            if not s or re.match(r"^-{3,}$", s):
                i += 1
                continue
            if s.startswith("```"):
                i += 1
                while i < len(lines) and not lines[i].strip().startswith("```"):
                    self.body.append(para(runs(lines[i], SIZES["body"]), indent=360, spacing_after=0))
                    i += 1
                i += 1
                continue
            if s.startswith("|"):
                rows = []
                while i < len(lines) and lines[i].strip().startswith("|"):
                    r = lines[i].strip()
                    if not re.match(r"^\|?\s*:?-{3,}", r):
                        rows.append(r.strip("|").split("|"))
                    i += 1
                self.add_table(rows)
                continue
            m = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)[^)]*\)$", s)
            if m:
                self.add_image(m.group(2), m.group(1))
                i += 1
                continue
            m = re.match(r"^(#{1,6})\s+(.+)$", s)
            if m:
                level = len(m.group(1))
                key, style = ("h2", "Heading2") if level <= 2 else ("h3", "Heading3")
                self.body.append(para(runs(m.group(2), SIZES[key], base_bold=True), style=style, spacing_after=160))
                i += 1
                continue
            m = re.match(r"^>\s?(.*)$", s)
            if m:
                self.body.append(para(runs(m.group(1), SIZES["body"], color="595959"), indent=420))
                i += 1
                continue
            m = re.match(r"^[-*+]\s+(.+)$", s)
            if m:
                self.body.append(para(runs("• " + m.group(1), SIZES["body"]), indent=360))
                i += 1
                continue
            m = re.match(r"^(\d+)[.、]\s*(.+)$", s)
            if m:
                self.body.append(para(runs(f"{m.group(1)}. {m.group(2)}", SIZES["body"]), indent=360))
                i += 1
                continue
            self.body.append(para(runs(s, SIZES["body"]), align="both"))
            i += 1

    def save(self, out):
        ns = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
              'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
              'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"')
        sect = '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="851" w:footer="992" w:gutter="0"/></w:sectPr>'
        document = f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document {ns}><w:body>{"".join(self.body)}{sect}</w:body></w:document>'
        fonts = f'<w:rFonts w:ascii="{FONT}" w:hAnsi="{FONT}" w:eastAsia="{FONT}" w:cs="{FONT}"/>'

        def style(sid, name, size):
            return (f'<w:style w:type="paragraph" w:styleId="{sid}"><w:name w:val="{name}"/><w:basedOn w:val="Normal"/>'
                    f'<w:pPr><w:keepNext/><w:spacing w:before="240" w:after="160"/></w:pPr>'
                    f'<w:rPr>{fonts}<w:b/><w:sz w:val="{size}"/><w:szCs w:val="{size}"/></w:rPr></w:style>')
        styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                  '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                  f'<w:docDefaults><w:rPrDefault><w:rPr>{fonts}<w:sz w:val="{SIZES["body"]}"/><w:szCs w:val="{SIZES["body"]}"/><w:lang w:val="en-US" w:eastAsia="zh-CN"/></w:rPr></w:rPrDefault>'
                  '<w:pPrDefault><w:pPr><w:spacing w:after="120" w:line="360" w:lineRule="auto"/></w:pPr></w:pPrDefault></w:docDefaults>'
                  f'<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr>{fonts}</w:rPr></w:style>'
                  + style("Title", "Title", SIZES["title"]) + style("Heading2", "heading 2", SIZES["h2"]) + style("Heading3", "heading 3", SIZES["h3"])
                  + "</w:styles>")
        rels_doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Id="rIdStyles" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
                    + "".join(f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" Target="{name}"/>' for name, _, rid in self.media)
                    + "</Relationships>")
        ctypes = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                  '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                  '<Default Extension="xml" ContentType="application/xml"/>'
                  '<Default Extension="png" ContentType="image/png"/><Default Extension="jpeg" ContentType="image/jpeg"/>'
                  '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
                  '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
                  "</Types>")
        rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
                "</Relationships>")
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("[Content_Types].xml", ctypes)
            z.writestr("_rels/.rels", rels)
            z.writestr("word/document.xml", document)
            z.writestr("word/styles.xml", styles)
            z.writestr("word/_rels/document.xml.rels", rels_doc)
            for name, path, _ in self.media:
                z.write(path, "word/" + name)


def check(path):
    with zipfile.ZipFile(path) as z:
        xml = "".join(z.read(n).decode("utf-8", "ignore") for n in z.namelist() if n in ("word/document.xml", "word/styles.xml"))
    tags = re.findall(r"<w:rFonts\s[^>]*>", xml)
    bad = []
    for t in tags:
        m = re.search(r'w:eastAsia="([^"]*)"', t)
        if not m:
            bad.append("缺 w:eastAsia：" + t[:80])
        elif not any(f in m.group(1) for f in ALLOWED_CN):
            bad.append(f"中文字体不合规（{m.group(1)}）")
        elif not all(a in t for a in ('w:ascii=', 'w:hAnsi=', 'w:cs=')):
            bad.append("四项字体属性不全：" + t[:80])
    print(f"rFonts 共 {len(tags)} 处")
    if not tags:
        print("FAIL: 未找到任何 rFonts 声明")
        return 1
    if bad:
        print(f"FAIL: {len(bad)} 处不合规")
        for b in bad[:20]:
            print("  -", b)
        return 1
    print("PASS: 字体规范校验通过")
    return 0


def main(argv):
    if len(argv) >= 2 and argv[0] == "--check":
        return check(argv[1])
    if not argv:
        print(__doc__)
        return 2
    title = None
    if "--title" in argv:
        k = argv.index("--title")
        title = argv[k + 1]
        argv = argv[:k] + argv[k + 2:]
    src = argv[0]
    out = argv[1] if len(argv) > 1 else os.path.splitext(src)[0] + ".docx"
    raw = open(src, encoding="utf-8").read()
    if not title:
        head = "\n".join(split_header(raw)[0])
        m = re.search(r"^\**主标题\**\s*[:：]\s*(.+)", head, flags=re.M) or re.search(r"^#\s+(.+)$", raw, flags=re.M)
        title = m.group(1).strip() if m else ""
    body = extract_body(raw)
    pending = body.count("[待确认]") + body.count("【待确认】")
    doc = Doc(os.path.dirname(os.path.abspath(src)))
    doc.build(body, title)
    doc.save(out)
    print(f"已生成：{out}")
    if pending:
        print(f"WARN: 正文仍有 {pending} 处 [待确认]，定稿前应清零")
    return check(out)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
