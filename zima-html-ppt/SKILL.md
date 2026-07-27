---
name: zima-html-ppt
description: >-
  生成 ZimaBlueAI 现场讲演 deck —— 暖纸编辑风（ZimaBlue Editorial）单文件 HTML 幻灯片，
  自带演讲者模式（按 S 弹出逐字稿 + 计时 + 议程的提词器窗口）、键盘翻页、每页配额计时、
  Chart.js 图表、入场动效。v2 加了工程治理层：方案先行的 deck-plan、deck.json ↔ HTML
  双向构建与反解（改稿不必重读 HTML）、七道闸门（路由/结构/身份/外壳/质量/浏览器/回滚）、
  missing evidence 证据纪律。当用户要"做现场 PPT / 讲演 deck / 上台用的幻灯片 / 内训课件 /
  路演稿 / 训战材料 / 带演讲者模式的 HTML PPT / 暖纸风 deck / ZimaBlue 风格幻灯片 /
  改一版讲演稿"时使用。不要用于：终端风决策报告（用 biz-html-viz）、深空风 keynote/原型/
  视频/可编辑 PPTX（用 viz-deck）、单张图表或知识图谱（用 viz-charts）、纯营销落地页。
  触发词：现场PPT、讲演deck、上台幻灯片、演讲者模式、提词器、逐字稿、暖纸风、
  ZimaBlue风格、内训课件、训战材料、路演稿、改稿重出。
license: MIT
---

# zima-html-ppt：ZimaBlueAI 现场讲演 deck

把一份内容做成**能上台讲**的单文件 HTML 幻灯片：暖纸编辑风的视觉 + 招牌的**演讲者模式**
（提词器窗口），并且**做完之后还改得动**——deck.json 是事实源，HTML 是产物，改稿走反解不走
重读。提炼自 ZimaBlueAI 实战母版 `D1-破局与进化.html` / `D2-三场战役.html` /
`D3-训练方案.html`。

## 一句话定位

- **风格** = ZimaBlue Editorial：暖纸底 `#f7f4ee` + 深青主色 `#1b5e5a` + 金/赭点缀 +
  发丝卡片 + 顶部 teal→gold→red 三色条 + 大号 tabular-nums 数字。
- **能力** = 键盘翻页 + 每页配额计时（超时变红）+ **演讲者模式（S 键提词器）** +
  Chart.js 图表 + 克制入场动效，全部内联在一个 `.html` 里，可离线（仅 Chart.js 走 CDN）。
- **治理** = 方案先行 + JSON 事实源 + 机器闸门 + 证据纪律，别人接手改稿不用猜。

## 何时用 / 何时不用

| 要做的 | 用 |
|---|---|
| 上台讲、客户路演、内训训战、带提词器的现场幻灯片 | **本技能** |
| 工程师/董事会看的终端风决策报告（黑底酸黄、零动效、可打印签字） | `biz-html-viz` |
| 深空蓝紫风 keynote / 高保真原型 / MP4 视频 / 可编辑 PPTX | `viz-deck` |
| 单张数据图表 / 3D 知识图谱 | `viz-charts` |
| 营销落地页 | 不是这个技能 |

边界拿不准时跑一遍路由闸门：`python scripts/trigger_eval.py`。

> 与 openclaw/hermes 的 `viz-channel` 关系：channel 在 IM 里对话式产出时，默认风格就是这套
> ZimaBlue Editorial。本技能是这套风格 + 演讲者模式的**完整规范与起步模板**来源。

---

## 工作流

### Step 0 —— 自检资产（一条命令）

```bash
python scripts/zima_deck.py locate      # macOS/Linux 用 python3
```

结果里 `"standalone": true` 才继续。脚本只用 Python 标准库，不联网。

### Step 1 —— 先做方案，再做页面（必做）

读 `references/workflow.md`，按 `templates/deck-plan-template.md` 写出 `deck-plan.md`：
意图卡（受众/场景/时长/离线边界/证据）→ 三方向选择卡（`1a` 说服 / `2b` 决策 / `3c` 训战，
明确推荐一个默认）→ 逐页计划表（含**视觉所有者**一列）。

用户说「直接生成 / 按默认 / 跳过确认」时不必停下等，但**方案稿照写**。

### Step 2 —— 读设计系统与演讲者模式（必读）

- `references/design-system.md`：令牌、字体层级、签名元素、组件清单、图表调性、动效与自检。
- `references/speaker-mode.md`：逐字稿 `.notes` 约定、五种标签语义、`data-min` 计时、键盘映射。

**不读直接写 = 视觉漂移。演讲者模式不是可选项**——ZimaBlueAI 的 deck 默认都带。

### Step 3 —— 选一条构建路线

| | **脚本构建（默认）** | 手写 starter |
|---|---|---|
| 起点 | 写 `deck.json`（契约见 `references/deck-json.md`） | 复制 `templates/zima-ppt-starter.html` |
| 适合 | 要改稿、要校验、要留档 | 一次性、版式高度定制 |
| 改稿 | `extract` → 改 JSON → `build` | 人重读 HTML 手改 |
| 校验 | 全套闸门 | 只跑 HTML 层闸门 |

```bash
# 新建：只在这一次铸 deckId
python scripts/zima_deck.py build deck.json \
  --output output/2026-07-27-slug-deck.html \
  --new-document --write-back \
  --report reports/deck-validation.json

# 改稿：从原文件继承身份，产出 sibling，绝不原地覆盖
python scripts/zima_deck.py extract output/2026-07-27-slug-deck.html --output deck.json
python scripts/zima_deck.py build deck.json \
  --identity-source output/2026-07-27-slug-deck.html \
  --output output/2026-07-27-slug-deck.updated.html \
  --report reports/deck-validation.json

# 手写 deck 也能校验（含 --legacy 反解成 JSON 再走脚本路线）
python scripts/zima_deck.py validate output/hand-written.html
python scripts/zima_deck.py extract output/hand-written.html --legacy --output deck.json
```

文件名：`{YYYY-MM-DD}-{slug}-deck.html`，输出到用户指定目录或 `output/`。

### Step 4 —— 过闸门，然后自己开一遍浏览器

读 `references/gates.md`。结构闸门必须零 error 才产出；warning 每条要么改掉、
要么在交付说明里解释。**脚本过了不等于验收过了**——封面、最密的一页、带图表的一页，
外加按 S 的演讲者窗口，都得人亲眼看过。没看就按名字写 `missing evidence`。

### Step 5 —— 按输出契约交付

`deck-plan.md` + `deck.json` + `.html` + `reports/deck-validation.json` + 一段交付说明
（路径、页数与总配额、离线边界、已验证项、仍属 missing evidence 的项）。

---

## 内容质量规则

- 章节 3–5 段，总页 12–25 页；单页正文克制，靠 `metrics`/`bars`/图表说话。
- 每页 `min` 配额齐全，之和等于承诺时长；每页写逐字稿（要念的话写成完整句，打 `say`/`data`）。
- **视觉所有者**：一条信息只由标题 / 图表 / 卡片 / 正文 / 逐字稿其中一个层级负责；
  屏幕上的字和嘴里念的话不许是同一句。
- 一页强调色 ≤ 2 种；一份 deck 只一种主视觉调性。
- 数字用真值，估值标 `[估]`、缺失标 `[N/A]`，严禁编造；竞品用对方的话。
- 反 AI 味：不写"不是 X 而是 Y"、不堆黑话、emoji 不当图标。

## 风格档位 · Taste（默认 1/1/1）

这套现场讲演风的"口味档位"是 **variance=1 · motion=1 · density=1**：非对称编辑式留白、
只做克制入场动效、平衡密度。守住三条就不会跑偏：

- **一页强调色 ≤ 2 种**；语义色只给语义（红=风险/降、绿=正向、金="看这里"）。
- **动效只做入场**（翻页 / 卡片 / 数字滚动 / 条形填充），禁无限循环、霓虹辉光、粒子；带 `prefers-reduced-motion` 降级。
- **标题用结论句、数字用真值**："营收四季翻倍" 而非 "营收分析"；估值标 `[估]`、缺失标 `[N/A]`，严禁编造。

交付前用上面三条 + design-system.md 第 10 节清单各扫一遍（名词式标题、强调色超标、
逐字稿过短这三条校验脚本会自动告警）。

## 文件结构

```
zima-html-ppt/
├── SKILL.md                          这份
├── NOTICE.md                         治理层方法论溯源与署名
├── references/
│   ├── design-system.md              ZimaBlue Editorial 视觉规范（必读）
│   ├── speaker-mode.md               演讲者模式 + 逐字稿 + 计时引擎（必读）
│   ├── workflow.md                   方案先行工作流 · 内容→组件映射 · 浏览器验收
│   ├── deck-json.md                  deck.json 文档契约 v1.0
│   └── gates.md                      七道闸门 · 输出契约 · missing evidence 纪律
├── templates/
│   ├── zima-ppt-starter.html         手写路线：全引擎起步骨架（复制即用）
│   ├── zima-ppt-shell.html           脚本路线：build 用的固定 shell（勿手改内容）
│   └── deck-plan-template.md         deck-plan.md 模板
├── scripts/
│   ├── zima_deck.py                  locate / build / extract / validate
│   └── trigger_eval.py               路由闸门
├── evals/
│   ├── fixtures/minimal-deck.json    好稿：必须零 error、反解一致
│   ├── fixtures/broken-deck.json     坏稿：必须被拦下，逐类点名
│   ├── trigger_cases.json            路由边界用例
│   └── run_fixtures.py               闸门自身的回归（15 项）
└── examples/                         完整走过一遍链路的示范交付
    ├── zima-html-ppt-v2-deck-plan.md 方案稿（含视觉所有者列与 missing evidence）
    ├── zima-html-ppt-v2.deck.json    文档源，14 页 / 23 分钟 / 11 种块
    ├── 2026-07-27-…-v2-deck.html     产物，零 error 零 warning
    └── reports/deck-validation.json  闸门报告
```

> 不知道一份合格交付长什么样，就打开 `examples/` —— 那四个文件就是输出契约的实例，
> plan 里连它自己没验到的三项 missing evidence 都写着。

## 反模式

- ❌ 不写 `deck-plan.md` 直接开做（视觉所有者没定，页面话必然多）。
- ❌ 跳过 design-system.md 直接写，配色/卡片/三色条漂移。
- ❌ 做 deck 不带演讲者模式（漏 `.notes` / 漏 `S` 键绑定 / 漏 `data-min`）。
- ❌ `.notes` 写进 `section` 内部（必须同级、紧随其后）。
- ❌ 改稿时重铸 `deckId`，或直接原地覆盖原 `.html`。
- ❌ 结构闸门报 error 还 `--force` 硬出。
- ❌ 没开浏览器就写"已验证"（该写 `missing evidence: browser visual review`）。
- ❌ 用 biz-html-viz 的黑黄配色或 viz-deck 的深空配色（那是别的技能）。
- ❌ `title` 用名词标题（要用结论句）；数字不用 tabular-nums。
- ❌ 大面积铺色、重边框重投影、无限循环动效、emoji 当图标。
- ❌ 留下未替换的 `{{占位}}`；编造数字。

---

## 反 AI slop 硬闸 · zima-design 联动

交付前除本 skill 自身规范与反模式清单外，再过一遍下面六条**硬闸**——蒸馏自
[nutlope/hallmark](https://github.com/nutlope/hallmark)（MIT · Anti-AI-slop design skill，
已收编为本仓库 `zima-design` 的 anti-slop 引擎）的六大纪律，任何 HTML / deck / 图表产出都适用：

1. **交付前六轴自评** — Philosophy / Hierarchy / Execution / Specificity / Restraint / Variety
   各打 1–5 分，任一 < 3 先返工再交付；把分数以注释盖在产物头部
   （`<!-- zima-design pre-emit critique: P5 H4 E5 S4 R5 V5 -->`）。
2. **诚实文案** — 用户没给的指标一律不编：禁止 "+47% conversion"、"50,000+ teams"、
   编造的 testimonial / logo 墙 / 案例数；缺数据用 `—` + 「待确认」灰块占位，或换一种版式。
3. **令牌锁定** — 主题选定后，色值与 `font-family` 只许引用 `:root` 令牌
   （`var(--color-accent)` / `var(--font-display)`）；禁止内联 hex / OKLCH / 裸字体名，
   需要新值先入令牌块再引用。
4. **禁手绘假 chrome** — 不画假浏览器栏（红黄绿点 + URL 胶囊）、假手机壳、
   假代码窗标题栏、假 IDE 窗口；要么真截图包 `<figure>`（至多发丝描边），要么让内容裸站。
5. **响应式硬底线** — 320 / 375 / 414 / 768px 四档无横向滚动（根上 `overflow-x: clip`，
   不用 `hidden`）；带图网格轨道用 `minmax(0,1fr)` 不用裸 `1fr`；可点击文本（按钮 / 导航 /
   CTA）不许折成两行；超长词标题加 `overflow-wrap: anywhere; min-width: 0`。
6. **标题禁斜体** — 标题与 display 字一律 roman（`font-style: normal`）；
   强调用字重 / 强调色 / 下划线承载，斜体只留正文强调。

**结构多样性**：同一会话连续产出多份同类交付物时，轮换章节节奏与版式骨架——
两份产出不允许共享同一套「hero → 三卡 → CTA」式模板节奏。

若本机装有 **zima-design** skill（`~/.claude/skills/zima-design/`、项目 `.claude/skills/zima-design/`
或 `.codex/skills/zima-design/`），交付前加载其 `engines/anti-slop/references/slop-test.md` 跑 **universal 子集**
（视觉 / 排版 / 文案 / 对比度 / a11y / 微交互关卡；报告与 deck 类产出跳过整页宏结构轮换与
`.hallmark/log.json` 项目记忆关卡）。口味档位与选材 / 文案细则见姊妹层 **taste-engine**
（`references/anti-slop-preflight.md`）。
