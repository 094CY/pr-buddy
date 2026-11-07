#!/usr/bin/env python3
# origin: 094CY/pr-buddy
"""
article_lint.py — 宣发内容机械检查（终检第一层）

只检查“能数出来”的规则；标题、主题、论证、品牌调性等判断类规则不在这里。
输出三级结果：
  ERROR  ：格式与流程硬项（头部格式、字数偏差、重复句、时间标记、待确认未列清单、写前论证卡缺项或写明“回应不了”），修完重跑直到 0
  REVIEW ：需要人看一眼的项，逐条看语境，该改改、该留留；没有绝对禁用词
           - 合规类（每处都列）：绝对化表述、医疗与功效用语、承诺与保证用语、价格比较与促销用语
           - AI 痕迹信号（只列反复出现或同段叠用的）
  INFO   ：统计信息；单次出现的信号词只在这里统计，不需要处理
  不检查：段落长短、加粗个数、金句/情绪点/总结句的数量和位置——由内容决定

用法：
  python3 article_lint.py <稿件.md>                     # 常规稿件（有固定头部）
  python3 article_lint.py <稿件.md> --short             # 短视频脚本等无头部稿件：不查头部和字数标注
  python3 article_lint.py <稿件.md> --short --no-card   # 配文：再免查写前论证卡
"""

import argparse
import difflib
import os
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wordcount import count_markdown, extract_body, split_header  # noqa: E402

ALT_TITLES = 3
# 破折号参考线（按内容类型；与 anti-ai-traces.md 一致，超过只提示，不是上限）
DASH_REF = {"新闻通稿": 3, "产品手册": 3, "服务说明": 3, "声明": 3, "促销": 3, "上新": 3,
            "知识科普": 5, "种草笔记": 5, "实操教程": 5, "专业解读": 5, "活动稿": 5,
            "短视频脚本": 5, "配文": 5,
            "品牌稿": 8, "深度文章": 8, "案例故事": 8, "产品软文": 8}
DASH_DEFAULT = 5

CARD_FIELDS = ("核心信息", "目标受众", "成立依据", "最强质疑", "回应", "论证主线", "受众价值", "合规边界")
HEAD_KEYS = ("内容类型", "发布渠道", "主体类型")

# ---- 信号词表（与 anti-ai-traces.md 同步维护；不是禁用词，只统计密度） ----
SIGNALS = {
    "空洞强调词": ["此外", "值得注意的是", "值得一提的是", "需要指出的是", "毋庸置疑", "不言而喻", "毫无疑问"],
    "企业黑话": ["赋能", "闭环", "底座", "沉淀", "抓手", "全栈", "一站式", "全链路", "飞轮效应"],
    "夸张修饰词": ["革命性的", "史无前例", "开创性的", "划时代", "无与伦比", "首屈一指", "强大的", "卓越的"],
    "空泛品牌词": ["匠心", "初心", "有温度", "品质生活", "极致体验", "高端大气", "绝绝子", "yyds", "氛围感拉满"],
    "连接废话": ["综上所述", "总而言之", "与此同时", "在这一背景下", "在此基础上", "基于上述分析"],
    "协作痕迹": ["希望这对您有帮助", "如果您需要更多信息", "以下是为您", "这是一个很好的问题"],
    "通用积极结论": ["未来可期", "前景广阔", "值得期待", "拭目以待", "激动人心的时代"],
    "无主体归因": ["业内专家认为", "行业人士指出", "有观点认为", "多个来源显示", "很多顾客说", "不少用户反馈"],
    "知识截止套话": ["根据公开信息", "据了解", "虽然具体细节有限"],
    "Meta表达": ["信号只有一句话", "不用再科普", "接下来我要说"],
    "废话开头": ["随着人工智能的快速发展", "随着AI的快速发展", "随着经济的快速发展", "在当今", "浪潮下"],
}

# ---- 合规类 REVIEW（每处都列；不是禁用词，确认依据、类目和规则后决定改或留） ----
COMPLIANCE = {
    "绝对化表述": (
        re.compile(r"国家级|最高级|(行业|业内|业界|全国|全球|国内|全省|全市|全城|本地|市场|全网|同类)(第一|领先|最[\u4e00-\u9fff])|唯一|100%|百分之百|"
                   r"遥遥领先|颠覆性?|最强|最佳(?!实践)|首个|首家|顶级|极致|王牌|销量冠军|NO\.?1|No\.?1"),
        "“国家级/最高级/最佳”不用于自我评价；其余须有可查证依据并说清范围，或是第三方原话，否则改为事实描述"),
    "医疗与功效用语": (
        re.compile(r"治疗|治愈|根治|疗效|药效|疗程|消炎|杀菌|抑菌|抗菌|抗病毒|抗炎|抗过敏|降血压|降血糖|降血脂|降三高|"
                   r"抗癌|防癌|抗肿瘤|增强免疫|提高免疫|提升免疫|排毒|祛湿|补肾|养胃|护胃|护肝|养肝|润肺|壮阳|助眠|安神|减肥|瘦身|燃脂|"
                   r"医学级|药妆|医用|处方|修复屏障|祛痘|祛斑|生发|防脱"),
        "普通食品不写疾病预防和治疗功能；化妆品不明示或暗示医疗作用；保健食品、医疗相关按 compliance-notes.md 第三节；非敏感类目语境（如“治疗设备”“医用耗材”本身是产品名）可留"),
    "承诺与保证用语": (
        re.compile(r"保证|包过|包会|包教包会|包退|稳赚|保本|保收益|无风险|零风险|无效退款|立竿见影|一次见效|"
                   r"永不|绝不反弹|无副作用|绝对安全|必涨|升值|回报率|收益率|通过率|提分"),
        "教育培训不承诺效果和通过率；金融与招商不承诺收益；房地产不承诺升值；其余承诺须真实可兑现"),
    "价格与促销用语": (
        re.compile(r"原价|划线价|市场价|专柜价|门市价|指导价|建议零售价|史上最低|全网最低|最低价|跳楼价|清仓|亏本|"
                   r"限时|限量|仅剩|最后\s*\d+|买一送一|赠送|送[一二三四五六七八九十两\d]|免费|\d+(?:\.\d+)?\s*折"),
        "被比较价格须真实（未标明含义的不高于前七日最低成交价）；赠品写品名和数量；“限时/限量/免费”写清期限、数量和条件"),
}

TIME_MARK = re.compile(r"截至目前|截至\s*\d{4}|截止\s*\d{4}|实测时间|测试时间|更新时间|数据截至|统计截至|[（(]\s*据[^）)]{0,20}[，,]\s*\d{4}[-./年]\d{1,2}")
TITLE_DATE = re.compile(r"[（(]\s*\d{4}\s*年(\s*\d{1,2}\s*月)?\s*[)）]")
SHELL_H2 = re.compile(r"^(?:[一二三四五六七八九十]+、|\d+[.、]?\s*)?(概述|背景|方案|总结|结语|小结|介绍)$")
NEG_PARALLEL = re.compile(r"不是[^。！？\n]{1,30}而是|不仅仅是|不仅[^。！？\n]{1,30}(而且|更是)")
SELF_QA = re.compile(r"[？?]\s*(因为|答案是|答案很简单|原因是|原因很简单|这意味着|意味着)")

errors, reviews, infos = [], [], []


def sentences(text):
    return [s.strip() for s in re.split(r"(?<=[。！？!?])", text) if s.strip()]


def plain(s):
    s = re.sub(r"\*\*|\*|`|^#+\s*|^>\s*|^[-*+]\s+|^\d+\.\s+", "", s.strip())
    return re.sub(r"\s+", "", s)


def check_header(head, words):
    rec = re.search(r"^\**主标题\**\s*[:：]\s*(.+)", head, flags=re.M)
    if not rec:
        errors.append("头部缺少「主标题」")
    alts = []
    m = re.search(r"备选标题\**\s*[:：]?\s*\n([\s\S]*?)(\n\s*\n[^\d\s]|\n全文字数|\n\**内容类型|$)", head)
    if m:
        alts = re.findall(r"^\s*\d+[.、]\s*(.+)$", m.group(1), flags=re.M)
    if len(alts) != ALT_TITLES:
        errors.append(f"备选标题应为 {ALT_TITLES} 条，实际 {len(alts)} 条")
    elif not any("推荐" in a for a in alts):
        errors.append("备选标题中未标注（推荐）项")
    for t in ([rec.group(1)] if rec else []) + alts:
        if TITLE_DATE.search(t):
            errors.append(f"标题含日期标记：{t.strip()}")
    lab = re.search(r"全文字数\**\s*[:：]\s*约?\s*(\d+)", head)
    if not lab:
        errors.append(f"头部缺少「全文字数」，实测 {words} 字")
    elif words and abs(int(lab.group(1)) - words) / words > 0.10:
        errors.append(f"标注字数 {lab.group(1)} 与实测 {words} 偏差超过 10%，按 wordcount.py 结果改写")
    for k in HEAD_KEYS:
        if k not in head:
            errors.append(f"头部缺少「{k}」")


def main(path, short=False, no_card=False):
    raw = open(path, encoding="utf-8").read()
    head_lines, _ = split_header(raw)
    head = "\n".join(head_lines) if head_lines else "\n".join(raw.split("\n")[:30])
    body = re.sub(r"```[\s\S]*?```", "", extract_body(raw))   # 代码块不参与文字检查
    words = count_markdown(raw)["wechat_count"]
    ctype = re.search(r"内容类型\**\s*[:：]\s*(\S+)", head)

    # ---------- 1. 头部 ----------
    if not short:
        check_header(head, words)

    lines = body.split("\n")
    paras = [l.strip() for l in lines if l.strip() and not l.strip().startswith("|")]

    # ---------- 2. 标题层级 ----------
    for l in lines:
        s = l.strip()
        if not short and re.match(r"^#\s", s):
            reviews.append(f"正文出现一级标题「{s}」：标题以头部主标题为准，正文不写 H1")
        if re.match(r"^#{2,3}\s", s) and SHELL_H2.match(s.lstrip("#").strip()):
            reviews.append(f"[空壳小标题]「{s}」：换成有信息量或画面感的小标题")

    # ---------- 3. 破折号（参考线） ----------
    limit = DASH_DEFAULT
    if ctype:
        for k, v in DASH_REF.items():
            if k in ctype.group(1):
                limit = v
                break
    dash_total = body.count("——")
    if dash_total > limit:
        reviews.append(f"[破折号] {dash_total} 处，超过该类型参考线约 {limit} 处：逐个看，不需要停顿强调的换成逗号/冒号/句号")
    prev_has = False
    for p in paras:
        n = p.count("——")
        if n > 1:
            reviews.append(f"[破折号] 同段 {n} 处：{p[:30]}…")
        if n and prev_has:
            reviews.append(f"[破折号] 相邻两段都有：{p[:30]}…")
        prev_has = n > 0

    # ---------- 4. 零时间标记 ----------
    for l in lines:
        for mm in TIME_MARK.finditer(l):
            errors.append(f"时间标记「{mm.group(0)}」：{l.strip()[:30]}…")

    # ---------- 5. 重复 ----------
    seen = {}
    for s in sentences(body):
        k = plain(s)
        if len(k) >= 15:
            seen[k] = seen.get(k, 0) + 1
    for k, n in seen.items():
        if n > 1:
            errors.append(f"句子重复 {n} 次：{k[:30]}…")
    long_paras = [plain(p) for p in paras if len(plain(p)) >= 40]
    for i in range(len(long_paras)):
        for j in range(i + 1, len(long_paras)):
            r = difflib.SequenceMatcher(None, long_paras[i], long_paras[j]).ratio()
            if r >= 0.8 and long_paras[i] != long_paras[j]:
                reviews.append(f"两段高度相似（{r:.0%}）：{long_paras[i][:20]}… / {long_paras[j][:20]}…")

    # ---------- 6. 待确认 ----------
    pending = len(re.findall(r"\[(?:终检)?待确认[^\]]*\]|【待确认】", body))
    if pending and not re.search(r"^#{1,6}\s*信息缺口", raw, flags=re.M):
        errors.append(f"正文有 {pending} 处待确认标记，但文末缺少「## 信息缺口清单」")

    # ---------- 6.5 写前论证卡（只核对写没写，不判断写得对不对；配文豁免） ----------
    is_caption = no_card or bool(ctype and "配文" in ctype.group(1))
    card = re.search(r"<!--\s*写前论证卡([\s\S]*?)-->", raw)
    if not is_caption:
        if not card:
            errors.append("缺少写前论证卡（稿件末尾的 <!-- 写前论证卡 ... --> 注释，见 SKILL.md Step 4.5）")
        else:
            for f in CARD_FIELDS:
                m = re.search(rf"^[ \t]*{f}[ \t]*[:：][ \t]*(.*)$", card.group(1), flags=re.M)
                if not m or len(m.group(1).strip()) < 4:
                    errors.append(f"写前论证卡「{f}」缺失或为空")
            rsp = re.search(r"^[ \t]*回应[ \t]*[:：][ \t]*(.*)$", card.group(1), flags=re.M)
            if rsp and "回应不了" in rsp.group(1):
                errors.append("写前论证卡写明最强质疑“回应不了”：按 Step 4.5 收窄或改写核心信息，不动笔")

    # ---------- 7. REVIEW：合规类（每处都列） ----------
    comp_count = {}
    for cat, (pat, tip) in COMPLIANCE.items():
        hits = list(pat.finditer(body))
        comp_count[cat] = len(hits)
        for mm in hits:
            ctx = body[max(0, mm.start() - 15): mm.end() + 10].replace("\n", " ")
            reviews.append(f"[{cat}]「{mm.group(0)}」：{tip}。…{ctx}…")

    # ---------- 8. REVIEW：AI 痕迹信号（只列反复出现或同类叠用） ----------
    single = []
    for cat, ws in SIGNALS.items():
        hits = {w: body.count(w) for w in ws if w in body}
        total = sum(hits.values())
        for w, n in hits.items():
            if n >= 2 or total >= 3:
                where = next(l.strip()[:24] for l in lines if w in l)
                reviews.append(f"[{cat}]「{w}」{n} 次（同类合计 {total}）：看语境是否在堆砌，例：{where}…")
            else:
                single.append(w)
    if single:
        infos.append("单次出现的信号词（不需处理）：" + "、".join(single))
    neg = len(NEG_PARALLEL.findall(body))
    for p in paras:
        if len(NEG_PARALLEL.findall(p)) >= 2:
            reviews.append(f"[否定式排比] 同段叠用：{plain(p)[:24]}…（看是否在套格式）")
    qa = [body[max(0, s.start() - 20): s.end() + 5].replace("\n", " ") for s in SELF_QA.finditer(body)]
    if len(qa) >= 2:
        reviews.append(f"[自问自答] {len(qa)} 处，看是否在当过渡句套用：" + " / ".join(f"…{c}…" for c in qa[:4]))
    elif qa:
        infos.append(f"自问自答 1 处（不需处理）：…{qa[0]}…")

    comp = "；".join(f"{k} {v}" for k, v in comp_count.items())
    infos.append(f"正文字数 {words}；破折号 {dash_total}（参考线 {limit}）；否定式排比 {neg} 处；待确认 {pending} 处；段落 {len(paras)} 个")
    infos.append(f"合规类：{comp}；模式：{'短稿' if short else '常规'}{'，免论证卡' if is_caption else ''}")

    for tag, items in (("ERROR", errors), ("REVIEW", reviews), ("INFO", infos)):
        print(f"== {tag}（{len(items)}）")
        for it in items:
            print(f"  - {it}")
    print("RESULT:", "FAIL" if errors else "PASS（REVIEW 项按语境逐条判断）" if reviews else "PASS")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="宣发内容 Markdown 机械检查")
    ap.add_argument("file")
    ap.add_argument("--short", action="store_true", help="无固定头部的短稿（短视频脚本、配文）：不查头部和字数标注")
    ap.add_argument("--no-card", action="store_true", help="免查写前论证卡（仅配文）")
    a = ap.parse_args()
    main(a.file, short=a.short, no_card=a.no_card)
