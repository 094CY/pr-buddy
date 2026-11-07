# 微信公众号 HTML 排版模板规范（品牌色可配置）

> 本规范定义了企业与品牌公众号文章的 HTML 排版标准，适用于各类主体。浏览器中全选复制 → 粘贴到公众号编辑器 → 保留排版。
>
> **品牌色**：本文所有代码示例用默认主色 `#1f4e79` 书写。有品牌色时不手改，排好后运行 `python3 <本 Skill 目录>/references/brand_theme.py "#品牌主色" --apply <公众号.html>` 一次替换全部角色色；太浅的品牌色会被自动加深到可读（与白底、色块底的对比度都 ≥4.5:1）。主体没有品牌色时就用默认色，不要自造一套。
>
> **零改写**：HTML 只做排版容器，所有文字来自 Markdown 定稿，交付前用 `<本 Skill 目录>/references/check_markdown_html_consistency.sh` 校验。

## 目录

- ⚠️ 第零原则（凌驾一切）
- 组件选用决策框架（铁律）
- 核心原则
- 设计系统
- 组件库
- HTML 骨架模板
- 灵活性原则
- 公众号编辑器已知坑点清单
- 格式自检清单
- 公众号发布版 vs 完整版

## ⚠️ 第零原则（凌驾一切）

> **公众号编辑器的实际渲染效果是唯一标准，浏览器预览仅供参考。**

公众号编辑器不是标准浏览器。它会**主动剥离、改写、忽略**大量 HTML/CSS 特性。因此：

1. **不要假设浏览器能渲染的，公众号就能渲染**——每种 HTML 元素/CSS 属性组合，默认怀疑其公众号兼容性
2. **遇到模板中没有覆盖的新写法，先查「已知坑点清单」；清单也没有的，按最保守写法处理**
3. **任何在公众号端出现的样式丢失，必须回溯根因并固化到本规范**
4. **灵活性 ≠ 随意性**——组件可以按需选用、参数可以微调，但公众号兼容性底线不可突破

## 组件选用决策框架（铁律）

> **先判断内容性质，再选组件。禁止凭感觉随意套用。**

| 内容性质 | 判断标准 | 使用组件 | 文字色 |
|---------|---------|---------|--------|
| **结论/信号/判断** | 这段话在给出一个判断、一个结论、一个核心信号 | 核心信号色块（主色） | `#1f4e79` |
| **数据/指标/结构化信息** | 这段话在展示具体数据、对比信息、列举要点 | 灰色信息卡片 | `#666`（卡片正文） |
| **辅助观点/类比** | 这段话在补充一个角度、一个类比、一个轻量强调 | 主色浅底辅助高亮色块 | `#1f4e79` |
| **普通正文** | 这段话在叙述过程、解释背景、铺陈信息 | 无装饰正文 `<p>` | `#444` |

**主色色块使用场景（明确）：**

| 场景 | 出现位置 | 说明 | 示例 |
|------|---------|------|------|
| **开头定调** | 引言里那句说清全文结论的话（如果有） | 原位包裹，不另写、不搬家 | "这家工厂把质检从抽检改成全检，返工率降下来的同时，交期也稳了" |
| **章节核心结论** | **内容核心段落处，位置灵活不固定** | 当某段文字本身就是转折性/总结性结论时，直接在该段落处加主色色块 | "问题清楚了：客流集中在晚市、备餐跟不上、翻台慢、差评都落在等位上。这几件事叠在一起，多招一个人解决不了，只能改动线。" |
| **效果类结论** | 数据展示之后、意义拉升之处 | 有数据支撑的规模化意义结论 | "这对整个行业意味着…" |
| **全文总结性结论** | 收尾部分 | 把全文意义拉升的那句话 | "省下来的不只是那几个小时，而是团队终于能把时间花在客户身上" |

**数量节奏：**
- 不设数量：正文里有几段真正的判断/信号/转折，就用几处；一处没有就不放
- **禁止**：为了凑数在每个章节结尾硬塞；为了“开头定调”另写一句正文里没有的话
- **核心原则**：主色色块跟着**结论段落**走，不是跟着**章节结构**走。读到一段结论是判断/信号/转折的文字，就在该段落处加色块；没有合适的结论段落，宁可不放

**灰色信息卡片使用场景（明确）：**

| 场景 | 说明 | 与主色色块的区别 |
|------|------|-----------------|
| **数据展示** | 结构化的数据、指标、核心成果数字 | 数据是「信息」，结论是「判断」——数据→灰色卡片，结论→主色色块 |
| **对比/列举** | 并列信息的对比呈现（按实际条数） | 列举多个要点时用卡片，单个核心结论用主色色块 |
| **补充说明** | 对正文某段信息的卡片化展开 | 补充性、解释性文字→灰色卡片；结论性、判断性文字→主色色块 |
| **关键信息聚合** | 把分散在正文里的要点聚合到一个卡片 | 聚合「信息」用灰色，聚合「结论」用主色 |

**常见错误（禁止）：**
- ❌ 数据段落改成主色色块 → 数据是信息，应用灰色卡片
- ❌ 结论段落套灰色卡片 → 结论是判断，应用主色色块
- ❌ 中间明明有核心结论段落却没标出来，或反过来为了凑数硬塞
- ❌ 灰色卡片内出现主色文字 → 色系统一，灰色卡片只用 `#333`/`#666`
- ❌ 同一场景的多个相关数据点拆成多张独立卡片 → 应聚合到一张卡片内分段呈现（铁律）
- ❌ 从正文中抽走一段做主色色块 → 核心结论段落应**就地**用色块包裹，正文不得缺失（铁律）
- ❌ 同一段文字在正文和色块中重复出现 → 二选一，禁止重复（铁律）

---

## 核心原则

1. **`#article` 正文区域样式必须内联**（inline style）——微信编辑器会剥离 `<style>` 块和 `class` 属性
2. **`#article` 内部禁用 class**——外层预览容器可用 class，但正文区域全部 inline style
3. **样式写到最内层元素**——不要把视觉属性写到父容器指望子元素继承
4. **正文段落一律 `text-align:justify`**（两端对齐）
5. **主标题左对齐**（`text-align:left`），不居中
6. **字体字号全局统一**——不允许段落间字号不一致
7. **色块与后续内容必须有呼吸间距**——色块底部间距 ≥ 普通段落间距
8. **严格忠于原文（铁律）**——HTML 只做排版容器，**禁止添加、改写、删减、调换任何文字**：可以把原有段落原位放进色块或卡片容器（按上方决策框架），但不给卡片、列表加 Markdown 里没有的标题或标签，子标题不套色块。所有文字与 Markdown 定稿逐字一致（唯二例外：章节序号 01/02、图注）
9. **同一会话内禁止多版本文件**——迭代修改时直接覆盖主文件，`-V2`/`-V3` 等多版本文件**一律禁止**。跨会话大改需保留旧版本时，按 `原文件名_V旧版本号_YYYYMMDD.ext` 格式重命名旧文件后再覆盖，禁止在同一目录下同时存在多个版本
10. **交付前必须跑一致性脚本并 PASS**——`bash <本 Skill 目录>/references/check_markdown_html_consistency.sh <定稿.md> <公众号.html>`；FAIL 时按脚本列出的句子逐条修正后重跑
11. **公众号两端缩进兼容（8号缩进标准）**——`#article` 容器 `padding: 30px 36px`

## 设计系统

### 字体栈

```
font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
```

### 主题色系（默认主色，可配置）

| 用途 | 色值 | 说明 |
|------|------|------|
| **主色**（标题左线、步骤标签背景） | `#1f4e79` | 默认深蓝；有品牌色时由 brand_theme.py 替换 |
| **正文加粗强调色** | `#1a1a2e` | 近黑深色，`<strong>` 默认色，不随品牌色变 |
| **核心信号/金句色块背景** | `linear-gradient(135deg, #eff3f6, #e6ecf0)` | 主色浅底渐变（由主色推导） |
| **核心信号/金句色块文字** | `#1f4e79` | 主色，在主色浅底上保证对比度 |
| **辅助高亮色块背景** | `#f4f6f8` | 更浅的主色底，次级信号 |
| **辅助高亮色块文字** | `#1f4e79` | 与核心信号一致 |
| **卡片背景 / 边框** | `#f8f9fa` / `1px solid #eee` | 极浅灰 |
| **卡片底部标签** | 背景 `#eee`，文字 `#666` | 灰色系，与卡片整体色系统一 |
| **正文色** | `#444` | 深灰（手机端可读性优先，不用纯黑） |
| **卡片正文色** | `#666` | 灰色，与灰色卡片色系统一 |
| **标题色** | `#1a1a2e` | 近黑深色，不随品牌色变 |

> **铁律（色系统一规则）**：
> - 主色系色块（核心信号/辅助高亮）→ 主色字体（`#1f4e79`），严禁灰色
> - 灰色系卡片（信息卡片）→ 灰色/黑色字体（`#333`/`#666`），严禁主色
> - **禁止混搭**：不得将灰色卡片配主色文字，也不得将主色色块配灰色文字

### 字体字号参数

| 元素 | 字号 | 颜色 | 字重 | 行高 | 对齐 | 备注 |
|------|------|------|------|------|------|------|
| 主标题 h1 | 22px | #1a1a2e | 700 | 1.5 | left | `letter-spacing:0.5px` |
| 二级标题 h2 | 18px | #1f4e79 | 700 | 1.4 | left | 左主色线 `3px solid #1f4e79` |
| 正文 p | 15px | #444 | 400 | 1.9 | justify | 段间距 `margin:0 0 24px` |
| 卡片正文 | 15px | #666 | 400 | 1.8 | justify | 与正文同号 |
| 步骤标签 | 13px | #fff（主色底 `#1f4e79`） | 700 | — | — | 胶囊圆角 `12px` |
| 卡片底部标签 | 13px | #666（灰色底 `#eee`） | 600 | — | — | 圆角 `4px` |
| 核心信号/金句主文 | 15px | #1f4e79 | 700 | 1.7 | justify | 与正文同号，保持统一 |
| 辅助高亮主文 | 15px | #1f4e79 | 600 | 1.7 | justify | |

### 间距规范

| 场景 | 值 | 说明 |
|------|-----|------|
| 标题区底部 | 28px | |
| 正文段间 | 24px | 章节内最后一段 `margin:0` |
| 块级组件顶部 | 24px | 色块/卡片与上方文字必须留呼吸距（铁律） |
| 章节 section 顶部 | 48px | 拉开章节标题与上方色块/段落的距离 |
| 章节 section 底部 | 40px | 章节间大呼吸 |
| 核心信号色块底部 | 40px | 色块后跟标题时必须 |
| 辅助高亮色块底部 | 24px | 后跟正文时用 24px |
| 连续卡片间距 | 12px | 最后一张 `margin:24px 0 16px` |
| 结尾 section 底部 | 28px | 页面收尾 |

## 组件库

### 1. 标题区

```html
<section style="text-align:left;margin-bottom:28px;">
  <h1 style="font-size:22px;font-weight:700;color:#1a1a2e;line-height:1.5;margin:0;letter-spacing:0.5px;">主标题</h1>
</section>
```

### 2. 二级标题（带左主色线 + 章节序号）

```html
<h2 style="font-size:18px;font-weight:700;color:#1a1a2e;border-left:3px solid #1f4e79;padding-left:10px;margin:0 0 16px;line-height:1.4;"><span style="color:#1f4e79;margin-right:8px;">01</span>标题</h2>
```

- 序号用主色 `#1f4e79`，与左主色线同色，形成视觉统一
- 序号与标题之间留 `8px` 间距
- 序号 01/02 是排版时加的唯一装饰性文字：Markdown 的 `##` 标题不写序号，一致性脚本会忽略它

### 3. 正文段落

```html
<p style="font-size:15px;color:#444;line-height:1.9;margin:0 0 24px;text-align:justify;">正文</p>
```

- 加粗：`<strong style="color:#1a1a2e;">加粗文字</strong>`
- 章节内最后一段 `margin:0`

### 4. 引言段落

```html
<section style="margin-bottom:24px;">
  <p style="font-size:15px;color:#444;line-height:1.9;margin:0 0 24px;text-align:justify;">引言文字</p>
</section>
```

### 5. 核心信号色块（主色渐变）

```html
<section style="background:linear-gradient(135deg,#eff3f6,#e6ecf0);border-radius:8px;padding:16px 20px;margin:24px 0 40px;">
  <p style="font-size:15px;font-weight:700;color:#1f4e79;line-height:1.7;margin:0;text-align:justify;">核心信号文字</p>
</section>
```

- 数量按正文里真实的结论段落定，不设固定数
- 底部 40px，后面跟章节标题留足呼吸

### 6. 辅助高亮色块（主色浅底）

```html
<section style="background:#f4f6f8;border-radius:8px;padding:16px 20px;margin:24px 0 24px;">
  <p style="font-size:15px;font-weight:600;color:#1f4e79;line-height:1.7;margin:0;text-align:justify;">辅助观点/类比</p>
</section>
```

### 6.1 主色强调文字（无色块底色）

```html
<p style="font-size:15px;color:#1f4e79;font-weight:600;line-height:1.9;margin:24px 0 24px;text-align:justify;">主色强调文字——不带背景色，仅用字色区分</p>
```

- **定位**：介于辅助高亮色块与普通正文之间的「轻量强调」手段
- **适用场景**：需要强调但不值得用色块的段落

### 7. 信息卡片（对比/列举）

```html
<section style="background:#f8f9fa;border-radius:8px;padding:20px;margin:24px 0 12px;border:1px solid #eee;">
  <p style="margin:0 0 10px;"><strong style="color:#1a1a2e;">🔵 卡片标题</strong></p>
  <p style="font-size:15px;color:#666;line-height:1.8;margin:0 0 16px;text-align:justify;">卡片正文</p>
  <p style="margin:0;"><span style="display:inline-block;background:#eee;color:#666;font-size:13px;font-weight:600;padding:3px 10px;border-radius:4px;">底部标签</span></p>
</section>
```
> **色系统一**：灰色卡片内部全部使用灰色系（背景 `#f8f9fa`/`#eee`，文字 `#333`/`#666`），严禁出现主色

### 8. 步骤标签（内联胶囊）

```html
<span style="display:inline-block;background:#1f4e79;color:#fff;font-size:13px;font-weight:700;padding:2px 10px;border-radius:12px;margin-right:6px;">第一步：接</span>
```

### 9. 收尾段（纯文字，无装饰）

```html
<p style="font-size:15px;color:#444;line-height:1.9;margin:24px 0 28px;text-align:justify;">收尾原文</p>
```

- 收尾用正文样式（`#444`，字重 400），不加色块、不加主色、不加粗，让内容本身说话
- 收尾是不是一句金句、要不要有金句，由 Markdown 定稿决定；排版不另写金句

### 10. 信心卡片（数据/成果背书）

```html
<section style="background:linear-gradient(135deg,#eff3f6,#e6ecf0);border-radius:8px;padding:20px 24px;margin:24px 0 24px;">
  <p style="font-size:14px;color:#1f4e79;font-weight:700;margin:0 0 12px;line-height:1.4;">核心成果</p>
  <p style="font-size:24px;font-weight:700;color:#1a1a2e;margin:0 0 4px;line-height:1.3;">82%</p>
  <p style="font-size:14px;color:#666;margin:0;line-height:1.5;">回头客占比，门店会员系统统计</p>
</section>
```

- **定位**：用数据说话，增强说服力。适合展示关键指标、核心成果、客户背书
- **结构**：顶部小标签（主色）+ 大数字（深色）+ 说明文字（灰色）；三处文字都必须来自 Markdown 定稿（例如 Markdown 里写的是“回头客占比 82%（门店会员系统统计）”），数字必须有来源
- **数量**：有几组值得单独展示的关键数据就用几张，通常在效果相关部分
- 多组数据并列时，用连续卡片结构，间距 `12px`

### 11. 配图区块（含可选图注）

```html
<section style="margin:32px 0;text-align:center;">
  <img src="[base64编码或公网URL]" style="max-width:100%;height:auto;border-radius:8px;display:block;margin:0 auto 8px;" />
  <p style="font-size:13px;color:#999;line-height:1.6;margin:0;text-align:center;">图注文字</p>
</section>
```

## HTML 骨架模板

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>公众号排版 - 文章标题</title>
<style>
body { background: #f5f5f5; margin: 0; padding: 20px 0; font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif; }
.tip-bar { max-width: 620px; margin: 0 auto 16px; background: #eff3f6; border: 1px solid #1f4e79; border-radius: 8px; padding: 12px 16px; font-size: 13px; color: #1f4e79; line-height: 1.6; }
.tip-bar strong { color: #1f4e79; }
.tip-bar code { background: #e6ecf0; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
#article { max-width: 580px; margin: 0 auto; background: #fff; padding: 30px 36px; }
</style>
</head>
<body>

<div class="tip-bar">
  <strong>📋 使用方法：</strong>只选中下方白色区域的文章内容（不要选这个提示框），<code>Ctrl/Cmd+C</code> 复制，然后到公众号编辑器 <code>Ctrl/Cmd+V</code> 粘贴即可。
</div>

<div id="article">

<!-- 标题 -->
<section style="text-align:left;margin-bottom:28px;">
  <h1 style="font-size:22px;font-weight:700;color:#1a1a2e;line-height:1.5;margin:0;letter-spacing:0.5px;">文章标题</h1>
</section>

<!-- 引言 -->
<section style="margin-bottom:24px;">
  <p style="font-size:15px;color:#444;line-height:1.9;margin:0 0 24px;text-align:justify;">引言段落...</p>
</section>

<!-- 核心信号色块（可选：引言里有那句结论时原位包裹） -->
<section style="background:linear-gradient(135deg,#eff3f6,#e6ecf0);border-radius:8px;padding:16px 20px;margin:24px 0 40px;">
  <p style="font-size:15px;font-weight:700;color:#1f4e79;line-height:1.7;margin:0;text-align:justify;">核心信号原文</p>
</section>

<!-- 正文章节（按需重复） -->
<section style="margin:48px 0 40px;">
  <h2 style="font-size:18px;font-weight:700;color:#1a1a2e;border-left:3px solid #1f4e79;padding-left:10px;margin:0 0 16px;line-height:1.4;"><span style="color:#1f4e79;margin-right:8px;">01</span>章节标题</h2>
  <p style="font-size:15px;color:#444;line-height:1.9;margin:0 0 24px;text-align:justify;">正文...</p>
  <p style="font-size:15px;color:#444;line-height:1.9;margin:0;text-align:justify;">章节最后一段...</p>
</section>

<!-- 结尾 -->
<section style="margin:48px 0 28px;">
  <p style="font-size:15px;color:#444;line-height:1.9;margin:0 0 24px;text-align:justify;">结尾段落...</p>
</section>

<!-- 收尾段（组件 9：正文样式，无装饰） -->

</div>

</body>
</html>
```

## 灵活性原则

1. **组件按需选用**——不是每篇都要卡片、步骤标签、辅助高亮。内容决定形式
2. **色块数量跟着内容走**——有几处真正的结论就用几处，不设数量；色块太重时部分改用主色强调文字
3. **主色文字 vs 色块的节奏**——长文中穿插使用，避免通篇色块太重
4. **卡片数量不限**——按并列信息的实际条数
5. **间距可微调**——基准值 ±4px 范围内灵活调整
6. **组件分布均衡（禁止前后割裂）**——同类组件不要连着扎堆，中间留出纯文本
7. **分块不改字**——可以重排为色块/卡片，但不改正文措辞

## 公众号编辑器已知坑点清单

### 安全区（可放心使用）

| 特性 | 备注 |
|------|------|
| `<section>` + inline style | 主力容器，最可靠 |
| `<p>` / `<strong>` / `<em>` + inline style | 文本类基础标签 |
| `<span>` + inline style | 行内包装 |
| `border-left` / `border-radius` | 装饰性边框 |
| `background` / `linear-gradient` | 色块/渐变 |
| `display:inline-block` | 胶囊标签等 |
| `<td style="...">`/`<th style="...">` | 表格样式唯一可靠写法 |

### 危险区（会被剥离或表现异常）

| 特性 | 表现 | 正确替代 |
|------|------|---------|
| `<style>` 块 / `class` 引用 | 整体剥离 | 所有样式 inline |
| `<hr>` | 样式不可控 | 用 `<section>` + `border-bottom` 模拟 |
| `<tr style="background/color:...">` | 被剥离 | 所有视觉属性写到 `<td>`/`<th>` |
| `<strong style="font-size:...">` | 字号跳变 | `<strong>` 只设 `color` |
| `flexbox` / `grid` / `float` | 不可靠 | 用 `<table>` 或嵌套 `<section>` |
| `transform` / `animation` | 不支持 | 不使用 |

### 表格公众号兼容写法（铁律）

1. **所有 background、color 必须写在 `<td>` / `<th>` 上**，不写在 `<tr>` 上
2. **border 用 `border:1px solid #色值`** 写在每个 `<td>`/`<th>` 上
3. **每个 `<td>`/`<th>` 必须显式声明 `background`**

**表头标准写法**：

```html
<tr>
  <th style="padding:10px 8px;text-align:left;font-weight:600;background:#1f4e79;color:#fff;border:1px solid #1f4e79;">维度</th>
  <th style="padding:10px 8px;text-align:center;font-weight:600;background:#1f4e79;color:#fff;border:1px solid #1f4e79;">列名</th>
</tr>
```

## 格式自检清单

### 第一层：排版基础（每篇必检）

1. ✅ 所有正文 `<p>` 都有 `text-align:justify`
2. ✅ 正文字号统一 15px / #444 / 行高 1.9
3. ✅ 主标题左对齐
4. ✅ `#article` 内部无 class、无外部 CSS 引用
5. ✅ 核心信号色块底部间距 ≥ 40px；色块都是原位包裹的正文原句
6. ✅ 强调色块文字统一 `#1f4e79`（禁灰色）
7. ✅ **强调色只有一个主色**——除主色及其浅底、灰色系外，没有混入其他色系；已按需运行 brand_theme.py
8. ✅ 组件分布均衡——同类组件没有扎堆
9. ✅ **色系统一检查**——主色色块内无灰色文字，灰色卡片内无主色文字（底部标签也须灰色系）

### 第二层：公众号兼容性专项

10. ✅ 所有视觉属性写在最内层渲染元素上
11. ✅ 表格每个 `<td>`/`<th>` 都有 `border` + 显式 `background`
12. ✅ `#article` 内无 `<style>` 块、无 `<hr>`
13. ✅ 无 flexbox/grid/float/position:absolute

### 第三层：零改写闸门（强制）

14. ✅ 运行 `bash <本 Skill 目录>/references/check_markdown_html_consistency.sh <定稿.md> <公众号.html>`，结果 PASS（章节序号 01/02 和图注会被脚本自动忽略）
15. ✅ FAIL 时按脚本列出的句子逐条修正后重跑；不用“只是格式差异”解释 FAIL

交付说明里写脚本的实际输出结论，不写“已校验 ✅”。

## 公众号发布版 vs 完整版

| 内容 | 完整版(.md) | 公众号版(.html) |
|------|-----------|----------------|
| 主标题 | ✅ 头部 | ✅ 作为 h1 |
| 备选标题 | ✅ | ❌ |
| 信息缺口清单 | ✅（如有，定稿前应清零） | ❌ |
| 元信息（字数/内容类型/渠道） | ✅ | ❌ |

两个版本都不附引用来源表；需要出处时写在正文句子里。

---

*默认主色 `#1f4e79`；品牌色通过 brand_theme.py 配置，不手工改色值。*
