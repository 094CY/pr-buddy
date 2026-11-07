<!-- origin: 094CY/pr-buddy -->
# PR-Buddy

> 通用企业产品与品牌宣发内容引擎：七类主体 × 15 类内容 × 8 类渠道，内置事实校准、写前论证卡、合规边界与脚本化终检。
> 本仓库是一个 **Agent Skill**，不是可运行的软件项目：没有后端、环境变量与部署步骤，也不需要配图。

## 这是什么

为任意企业、品牌、门店、工作室或机构撰写、修改、润色宣发文字：新闻通稿、品牌故事、行业深度文章、
知识科普、专业解读、实操教程、产品软文、种草笔记、客户案例、活动稿、上新促销、产品手册、声明回应、
短视频脚本、社群配文，共 15 类。

核心是**不编造**：时间节点、现状、趋势、数字、排名、价格，以及主张依赖的机制，查不到就标 `[待确认]`；
动笔前先过写前论证卡（核心信息、目标受众、成立依据、最强质疑、论证主线、受众价值、合规边界），
任一不过就不写；初稿只出 `.md`，用户确认定稿后才生成 `.docx` 或公众号 HTML。

## 安装

把本仓库**整个目录**复制到你的 Agent 技能目录，保持目录名 `pr-buddy`：

```
# 示例：兼容 Agent Skills 的客户端
cp -R pr-buddy ~/.claude/skills/

# 示例：项目级技能
cp -R pr-buddy <你的项目>/.claude/skills/
```

技能入口是 `SKILL.md`；`references/`（含 `types/` 子目录）、`agents/` 是它的资源，
需与 `SKILL.md` 保持同级，**不要只复制单个文件**。随包脚本只依赖 `python3` 标准库，
无需安装依赖或配置密钥。

## 目录结构（完整清单）

| 路径 | 作用 |
|---|---|
| `SKILL.md` | 技能定义：铁律、身份边界、执行流程、15 类内容索引、写前论证卡、回退规则 |
| `agents/openai.yaml` | 智能体接口描述（显示名、默认提示词） |
| `references/activation-checklist-10s.md` | 每次激活先读：决定本次加载哪些文件 |
| `references/template.md` | 输出文件命名与头部格式 |
| `references/enterprise-profiles.md` | 七类主体的决策方式、信任来源与调性 |
| `references/brand-fact-sheet.md` | 主体事实校准表 |
| `references/structure.md` | 八类渠道的结构与写法差异 |
| `references/writing-guide.md` | 写作规则（唯一来源） |
| `references/anti-ai-traces.md` | 去 AI 痕迹的语境与密度判断 |
| `references/argumentation-guide.md` | 论证方法 |
| `references/marketing-strategy.md` | 转化、收尾、合作植入、标题 |
| `references/style-genes.md` | 风格基因 |
| `references/compliance-notes.md` | 合规边界与敏感类目 |
| `references/revision-protocol.md` | 修改任务的诊断与处理 |
| `references/final-check.md` | 终检脚本、判断维度与交付说明 |
| `references/wechat-html-template.md` | 公众号 HTML 排版模板 |
| `references/types/` 下 15 个 `.md` | 15 类内容各自的采集、结构、渠道版本与主体调整 |
| `references/article_lint.py` | 稿件终检（论证卡、时间标记、合规用语等） |
| `references/wordcount.py` | 字数统计，用于填写头部字数 |
| `references/brand_theme.py` | 品牌调性推断 |
| `references/md_to_docx.py` | Markdown 转 Word（定稿后） |
| `references/check_markdown_html_consistency.sh` | 校验 MD 与公众号 HTML 正文一致 |
| `LICENSE` / `NOTICE.md` | 授权条款与方法论说明 |

## 工作流

```mermaid
flowchart LR
    A[信息采集 / 事实校准] --> B[主体画像]
    B --> C[判定类型与渠道]
    C --> D[写前论证卡 硬闸门]
    D -->|任一不过| C
    D -->|通过| E[写作]
    E --> F[脚本终检 + 判断维度]
    F --> G[交付 .md 审稿]
    G -->|用户确认定稿| H[.docx / 公众号 HTML]
```

## 使用

在对话中提及新闻稿、品牌故事、深度文章、种草笔记、客户案例、活动稿、上新促销、声明回应、
短视频脚本、朋友圈配文等词即可触发，也可以直接说明「为 X 写一篇 Y 渠道的 Z」。

终检必须用真实命令跑并把结果写进交付说明，不自评「已遵守」：

```bash
python3 references/wordcount.py --help
python3 references/article_lint.py --help
```

## 事实与合规

稿件里的客户名称、顾客评价、数字与效果数据必须有来源与授权；未授权的客户写脱敏称呼，
不给出可反推身份的细节。`references/compliance-notes.md` 覆盖个人信息、广告用语与敏感类目；
敏感类目的发布终稿应提醒用户走法务或平台审核。本技能不出具法律意见。

## 许可与作者

非商业研究与学习许可，仅供个人学习、研究与非商业技术交流；禁止任何商业用途。完整条款见 [LICENSE](./LICENSE)。

Copyright (c) 2026 094CY · https://github.com/094CY
