---
name: zima-design
description: ZimaBlueAI 设计合奏引擎（Design Ensemble）——把结构多样性、动效手感、数据化设计智能三个内置引擎与 impeccable / huashu-design / taste-engine 三个外部体系编排成一套路由协议，目标是每次交付都涌现出不同的、贴近人类审美的设计方案，而不是单一风格或 AI 模板味。触发词：设计一个页面 / 落地页 / 官网 / 产品 UI / redesign / 重设计 / 多给几个方向 / 别做成 AI 味 / anti-slop / 设计评审 / 动效 / 配色 / 字体搭配 / 选个风格 / design a landing page / make it feel human。不用于纯后端、非视觉任务。
---

# zima-design · 设计合奏引擎

一次好的设计交付需要三种互补的智能：**结构与主题的多样性**（这次和上次长得不一样）、**动效与手感**（每一次交互都对得起手指）、**数据化的选型依据**（风格/配色/字体不是拍脑袋）。没有一个单独的体系同时做好这三件事，所以 zima-design 把它们编排成合奏，由本协议充当指挥。

## 三条铁律（凌驾于一切引擎输出）

1. **多样性优先**：连续两次交付不得共享同一套「宏结构 × 主题 × 卡片物理 × 动效人格」组合。宁可换一个次优主题，不许复用上一次的模板。
2. **诚实**：不编造指标、用户数、证言；示例数据必须标注。设计的「活」来自结构与动效，不来自吹嘘的文案。
3. **验收前置**：任何 HTML/UI 交付前必须过一遍验收栈（见文末），六轴自评 <3 分的轴必须返工。

## 内置引擎（本 skill 目录内，按需读取）

| 引擎 | 位置 | 管什么 | 何时读 |
|------|------|--------|--------|
| **anti-slop**（结构与主题） | `engines/anti-slop/SKILL.md` + `references/` | 21 种页面宏结构、20 具名主题 + custom OKLCH、4 genre、57 条 slop-test 验收关卡、audit/redesign 动词 | 从零建页面/落地页/官网；审计或重设计已有页面 |
| **motion**（动效与手感） | `engines/motion/emil-design-eng/SKILL.md`（核心）；`apple-design/`（手势物理）；`review-animations/`（验收）；`find-animation-opportunities/`、`improve-animations/`、`animation-vocabulary/` | 动画决策框架（频率门→目的→缓动→时长）、弹簧物理、手势/拖拽、性能铁律（只动 transform/opacity）、Sonner 组件原则 | 页面里有任何交互/动效；动效专项审查；「让它更有手感」 |
| **database**（数据检索） | `engines/database/ui-ux-pro-max/SKILL.md`（主）；`design/`、`design-system/`、`ui-styling/`、`brand/`、`banner-design/`、`slides/` | 84 风格 / 192 配色 / 74 字体搭配 / 192 产品类型 / 98 UX 准则 / 25 图表类型 / 22 技术栈，Python 本地检索 | 选型犹豫时（什么风格适合这个产品？配色？字体?）；React/Vue/Flutter 等具体栈的落地建议 |

> 引擎目录内的文件是**逐字节保留的上游本体**（便于跟进上游升级，出处见 `NOTICE.md`）。引擎内部说的「本 skill」指引擎自身；调用其脚本时用完整路径，例如
> `python .claude/skills/zima-design/engines/database/ui-ux-pro-max/scripts/search.py "<query>" --domain style`。

## 外部联动（已安装则征用，未安装不阻塞）

| 体系 | 探测路径 | 管什么 |
|------|----------|--------|
| **impeccable** | `~/.claude/skills/impeccable/` | 工程化设计动词（craft/shape/audit/polish/bolder/quieter/typeset/colorize…）、brand vs product register 分流、PRODUCT.md/DESIGN.md 项目记忆 |
| **huashu-design** | `~/.claude/skills/huashu-design/` | 设计方向顾问（5 流派 × 20 设计哲学，3 方向并行 demo）、专家 5 维评审、HTML→MP4/GIF |
| **taste-engine** | `~/.claude/skills/taste-engine/` 或本仓库 `taste-engine/` | 口味档位（三个拨盘）+ anti-slop preflight 轻量预检 |

## 路由表

按任务类型决定谁主导、谁辅助（主导引擎的协议全文必读，辅助引擎按需抽读）：

| 任务 | 主导 | 辅助 |
|------|------|------|
| 从零做落地页/官网/营销页 | anti-slop（选 genre→主题→宏结构） | database 校验风格与配色选型；motion 出交互层；impeccable `craft` 流程做工程化 |
| 从零做产品 UI/仪表盘/工具 | database（产品类型→风格→栈规则） | impeccable product register；motion 交互层；anti-slop 通用关卡兜底 |
| 已有页面「变好看/去 AI 味」 | anti-slop `audit` 动词（57 关卡逐条） | 修补走 impeccable `polish`/`quieter`/`bolder`；重做走 anti-slop `redesign` |
| 动效专项（加动效/审动效/优化动效） | motion（决策框架 + review 十条标准） | apple-design 手势物理；database 的 GSAP preset |
| 方向未定「多给几个方向看看」 | huashu-design 方向顾问（3 差异化方向） | 每个方向用 anti-slop 的不同「主题×宏结构」组合落地，禁止三个方向共享骨架 |
| 交付后评审 | huashu/viz-deck 5 维评审 | motion `review-animations` 管动效分项 |

**Register 判断先行**（借 impeccable 的分流）：设计**是**产品（营销页/作品集/宣传）→ 敢用大主题、大动效；设计**服务**产品（工具/后台/表单）→ 数据库准则优先、动效克制（高频操作零动画）。

## 多样性协议（合奏的核心价值）

每次开工前，在五条独立轴上**显式做出选择并记录**，形成本次的「设计签名」：

1. **宏结构**（21 选 1）——不得与上一次交付相同
2. **主题/哲学**（anti-slop 20 主题 ∪ huashu 20 哲学 ∪ database 84 风格）——同一产品线可以复用主题，但版式必须换
3. **动效人格**——playful-bouncy（弹簧过冲）/ crisp-professional（150-250ms ease-out）/ calm-editorial（淡入为主）三选一，全页统一
4. **卡片物理**——hairline 扁平 / 厚边硬影 / 无边色块 / 柔影单层 / 分层影，五选一
5. **密度节奏**——通铺留白 / 一段刻意密集 / 杂志式混排

把选择写进交付物头部注释：`<!-- zima-design signature: 宏结构=split-studio 主题=lumen 动效=calm 物理=hairline 密度=杂志混排 -->`，这既是自查，也是下一次「不得重复」的台账。同时执行 anti-slop 的**禁共享尾巴**规则：hero 之后的后半页（features→证言→定价→footer 连招）不得与任何一次历史交付同构。

## 交付验收栈（顺序执行，全过才能交）

1. **anti-slop 通用关卡子集**——居中堆叠 hero / badge-pill / 三等卡 / 编造指标 / 斜体标题 / 令牌锁定 / 320px 无横滚 / reduced-motion 降级
2. **motion 十条动效标准**（页面有动效时）——`transition: all` / `ease-in` / `scale(0)` 入场 / 键盘触发动画 / >300ms UI 动效，一票不过
3. **六轴自评盖章**——P/H/E/S/R/V 各 1–5 分，任一轴 <3 返工，通过后在头部注释盖章
4. **（可选）5 维专家评审**——出片级交付走 huashu/viz-deck 的 philosophy/hierarchy/craft/functionality/originality 雷达

## Demos

`demos/` 有两组示范：**闭环三件套**（虚构产品 Curio）——`demo-before-ai-slop.html`（12 处 slop 特征标本）→ `demo-audit-report.md`（24 项抽查 17 FAIL）→ `demo-after-redesign-hum.html`（Hum 主题重做）；**多风格样片画廊**——`demo-style-cobalt-devtool.html`（Cobalt × dev-tool，真 ⌘K 面板）、`demo-style-lumen-night.html`（Lumen·Night × marquee-hero，灯丝仪器 + 读数条）、`demo-style-carnival-bento.html`（Carnival·Studio-Night × loud bento，双色对撞 + 硬偏移阴影）。四张页面四套签名，五轴零重叠——多样性协议的实物证明。每张头部带 signature + critique 双盖章。详见 `demos/README.md`。

## 与本仓库其他 skill 的分工

- **viz-deck / viz-charts / biz-html-viz / zima-html-ppt**：垂直交付管线（deck/图表/决策报告/PPT）。它们的 SKILL.md 已内联「反 AI slop 硬闸」做底线；需要完整设计智能时，桥接到本 skill。
- **taste-engine**：已有产出的轻量口味叠加；zima-design 是从零设计的完整合奏。先 zima-design 后 taste-engine 微调。
