---
name: zima-html-ppt
description: >-
  生成 ZimaBlueAI 现场讲演 deck —— 暖纸编辑风（ZimaBlue Editorial）单文件 HTML 幻灯片，
  自带演讲者模式（按 S 弹出逐字稿 + 计时 + 议程的提词器窗口）、键盘翻页、每页配额计时、
  Chart.js 图表、入场动效。当用户要"做现场 PPT / 讲演 deck / 上台用的幻灯片 / 内训课件 /
  路演稿 / 训战材料 / 带演讲者模式的 HTML PPT / 暖纸风 deck / ZimaBlue 风格幻灯片"时使用。
  母版：D1-破局与进化 / D2-三场战役 / D3-训练方案。复制 templates/zima-ppt-starter.html
  填内容即可。不要用于：终端风决策报告（用 biz-html-viz）、深空风 keynote/原型/视频（用 viz-deck）、
  纯营销落地页。触发词：现场PPT、讲演deck、上台幻灯片、演讲者模式、提词器、逐字稿、暖纸风、
  ZimaBlue风格、内训课件、训战材料、路演稿。
license: MIT
---

# zima-html-ppt：ZimaBlueAI 现场讲演 deck

把一份内容做成**能上台讲**的单文件 HTML 幻灯片：暖纸编辑风的视觉 + 招牌的**演讲者模式**
（提词器窗口）。提炼自 ZimaBlueAI 实战母版 `D1-破局与进化.html` / `D2-三场战役.html` /
`D3-训练方案.html`。

## 一句话定位

- **风格** = ZimaBlue Editorial：暖纸底 `#f7f4ee` + 深青主色 `#1b5e5a` + 金/赭点缀 +
  发丝卡片 + 顶部 teal→gold→red 三色条 + 大号 tabular-nums 数字。
- **能力** = 键盘翻页 + 每页配额计时（超时变红）+ **演讲者模式（S 键提词器）** +
  Chart.js 图表 + 克制入场动效，全部内联在一个 `.html` 里，可离线（仅 Chart.js 走 CDN）。

## 何时用 / 何时不用

| 要做的 | 用 |
|---|---|
| 上台讲、客户路演、内训训战、带提词器的现场幻灯片 | **本技能** |
| 工程师/董事会看的终端风决策报告（黑底酸黄、零动效、可打印签字） | `biz-html-viz` |
| 深空蓝紫风 keynote / 高保真原型 / MP4 视频 / 可编辑 PPTX | `viz-deck` |
| 单张数据图表 / 3D 知识图谱 | `viz-charts` |
| 营销落地页 | 不是这个技能 |

> 与 openclaw/hermes 的 `viz-channel` 关系：channel 在 IM 里对话式产出时，默认风格就是这套
> ZimaBlue Editorial。本技能是这套风格 + 演讲者模式的**完整规范与起步模板**来源。

## 工作流

### Step 1 —— 读设计系统（必读）

`references/design-system.md`：令牌、字体层级、签名元素、组件清单、图表调性、动效与自检。
**不读直接写 = 视觉漂移。**

### Step 2 —— 读演讲者模式（做 deck 必带）

`references/speaker-mode.md`：逐字稿 `.notes` 约定、五种标签语义（cue/say/do/data/bridge）、
`data-min` 计时、键盘映射、提词器窗口结构。**演讲者模式不是可选项**——ZimaBlueAI 的 deck
默认都带。

### Step 3 —— 复制起步模板填内容

复制 `templates/zima-ppt-starter.html` →
- 改 `:root` 别动（保一致）；
- 每页一个 `<section class="slide" data-min="N">`，紧跟一个 `<div class="notes" data-min="N">`；
- `h2` 用**结论句**不用名词；数字用 `data-count`/`data-suffix`/`data-dec` 触发滚动；
- 要图表的页加 `data-chart="名"`，在 `buildChart()` 里按名懒建；
- 替换所有 `{{占位}}`。

文件名：`{YYYY-MM-DD}-{slug}-deck.html`，输出到用户指定目录或 `output/`。

### Step 4 —— 交付前自检

跑 `references/design-system.md` 第 10 节清单，**重点确认按 S 能弹出演讲者窗口、逐字稿
橙色高亮、计时和议程都正确**。条件允许就在浏览器里翻一遍 + 开一次演讲者窗口。

## 内容质量规则

- 章节 3–5 段，总页 12–25 页；单页正文克制，靠 `.metric`/`.bar`/图表说话。
- 每页 `data-min` 配额齐全；每页写对应 `.notes` 逐字稿（要念的话写成完整句，打 `tag-say`/`tag-data`）。
- 一页强调色 ≤ 2 种；一份 deck 只一种主视觉调性。
- 数字用真值，估值标 `[估]`、缺失标 `[N/A]`，严禁编造；竞品用对方的话。
- 反 AI 味：不写"不是 X 而是 Y"、不堆黑话、emoji 不当图标。

## 风格档位 · Taste（默认 1/1/1）

这套现场讲演风的"口味档位"是 **variance=1 · motion=1 · density=1**：非对称编辑式留白、
只做克制入场动效、平衡密度。守住三条就不会跑偏：

- **一页强调色 ≤ 2 种**；语义色只给语义（红=风险/降、绿=正向、金="看这里"）。
- **动效只做入场**（翻页 / 卡片 / 数字滚动 / 条形填充），禁无限循环、霓虹辉光、粒子；带 `prefers-reduced-motion` 降级。
- **标题用结论句、数字用真值**："营收四季翻倍" 而非 "营收分析"；估值标 `[估]`、缺失标 `[N/A]`，严禁编造。

交付前用上面三条 + design-system.md 第 10 节清单各扫一遍。

## 文件结构

```
zima-html-ppt/
├── SKILL.md                          这份
├── references/
│   ├── design-system.md              ZimaBlue Editorial 视觉规范（必读）
│   └── speaker-mode.md               演讲者模式 + 逐字稿 + 计时引擎（必读）
└── templates/
    └── zima-ppt-starter.html         全引擎起步骨架（含演讲者模式，复制即用）
```

## 反模式

- ❌ 跳过 design-system.md 直接写，配色/卡片/三色条漂移。
- ❌ 做 deck 不带演讲者模式（漏 `.notes` / 漏 `S` 键绑定 / 漏 `data-min`）。
- ❌ `.notes` 写进 `section` 内部（必须同级、紧随其后）。
- ❌ 用 biz-html-viz 的黑黄配色或 viz-deck 的深空配色（那是别的技能）。
- ❌ `h2` 用名词标题（要用结论句）；数字不用 tabular-nums。
- ❌ 大面积铺色、重边框重投影、无限循环动效、emoji 当图标。
- ❌ 留下未替换的 `{{占位}}`；编造数字。
