# 激活清单（加载路由的唯一来源）

## 一、按任务加载

路径都相对 `references/`。

| 任务 | 判断信号 | 必读 | 涉及时再读 |
|------|---------|------|-----------|
| 写新稿 | 给了主体、产品、服务、门店、活动或案例素材，要出稿 | `template.md`、`enterprise-profiles.md` 当前主体一节、`structure.md`、当前类型的 `types/*.md`、`writing-guide.md`、`anti-ai-traces.md`、`compliance-notes.md`（普通类目扫第一、二节） | 具体产品、门店、数据 → `brand-fact-sheet.md` |
| 短视频脚本 / 配文 | 只要视频脚本或转发配文 | `enterprise-profiles.md` 当前主体一节、`types/short-video.md` 或 `types/caption.md`、`anti-ai-traces.md` | 敏感类目或促销 → `compliance-notes.md` |
| 修改已有稿 | 指向已有 .md，要求改、润色、压缩、调结构 | `revision-protocol.md`、`anti-ai-traces.md` | 主体事实 → `brand-fact-sheet.md`；合规用语 → `compliance-notes.md` |
| 定稿排版 | 用户明确说定稿，要 .docx 或公众号 HTML | `final-check.md`；公众号 HTML 加 `wechat-html-template.md` | — |

写新稿和修改交付前都读 `final-check.md`。

**按需补充**

| 需要 | 读 |
|------|-----|
| 标题、CTA、收尾、合作植入 | `marketing-strategy.md` |
| 开头、论证递进、受众共情、政策与热点锚定 | `argumentation-guide.md` |
| 风格调配 | `style-genes.md` |

## 二、四道闸门（没过不往下走）

0. **内容闸门**：主体画像想清；写前论证卡八项写全，SKILL.md Step 4.5 判定通过。配文免论证卡，但同样不能踩类目红线。
1. **格式闸门**：初稿阶段只交 .md。
2. **Markdown 闸门**：`article_lint.py` 的 ERROR 为 0；REVIEW 项按语境逐条判断。
3. **成品闸门**：HTML 一致性脚本 PASS；.docx 字体校验 PASS。

## 三、口径冲突时以谁为准

1. SKILL.md 区块 1 最高；`compliance-notes.md` 里的法定要求与铁律同级，用户口径也不能突破。
2. 用户本次给定的结构、口径高于其他默认规则。
3. 主体事实以用户资料和一手资料为准。
4. 各专题以对应文件为唯一来源：

| 专题 | 文件 |
|------|------|
| 主体画像 | `enterprise-profiles.md` |
| 事实校准 | `brand-fact-sheet.md` |
| 合规 | `compliance-notes.md` |
| 渠道与结构原则 | `structure.md` |
| 各类型的采集、结构、写法 | `types/*.md` |
| 通用写作规则 | `writing-guide.md` |
| 去 AI 痕迹 | `anti-ai-traces.md` |
| 转化、收尾、合作植入、标题 | `marketing-strategy.md` |
| 终检、脚本、交付说明 | `final-check.md` |
| 修改流程 | `revision-protocol.md` |
| 公众号 HTML | `wechat-html-template.md` |
| 通用采集、文件命名、头部格式 | `template.md` |

发现两处说法不一致时按上面顺序执行，并在交付说明里提一句。
