---
name: viz-charts
description: Render charts, diagrams, knowledge graphs, motion charts, and native PPTX charts for HTML reports or decks. Supports Mermaid, ECharts, SVG KPI and sparkline and gauge and progress and tag-cloud components, 3D knowledge graphs, MP4 or GIF motion chart export, and editable PowerPoint chart output. Use when the user asks for architecture diagrams, bar charts, data visualization, 3D knowledge graphs, animated charts, MP4 export, chart, mermaid, echarts, KG, knowledge graph, motion chart, native chart pptx, or editable PPTX chart, including needs from biz-html-viz or viz-deck.
license: MIT
---

# viz-charts: 报告内嵌图表与 3D 知识图谱

为 `biz-html-viz`（终端风）和 `viz-deck`（讲演风）两个报告 skill 提供图表渲染与项目可视化能力。**七类视觉表达 + 双模渲染 + 双主题 + MP4 视频导出**。

## 七类视觉表达

| 类型 | 类型数 | 路径 |
|---|---|---|
| **Mermaid** 关系/流程图 | 11 | `templates/mermaid/*.mmd` |
| **ECharts** 数据图表 | 25+ | `templates/echarts/*.json` |
| **轻量自研组件** SVG/CSS | 5 | `components/{kpi,sparkline,gauge,progress,tag-cloud}/` |
| **3D 知识图谱** WebGL | 3 viewer | `templates/kg3d/{code,doc,data}-graph.html` |
| **SVG 知识图谱** 环形 Context Graph / Circos 弦图 | 2 form | `references/svg-kg-guide.md` |
| **Motion 图表 → MP4/GIF** | 3 模式 | `templates/motion/*.html` + `references/motion-charts.md` |
| **Native PPTX 图表**（v3） | 8 chart types | `scripts/echarts_to_pptx.py` + `references/pptx-charts.md` |

## 两种渲染模式

| 模式 | 适用 | 实现 | 限制 |
|---|---|---|---|
| **inline** （默认） | 浏览器查看、嵌入 HTML 报告 | CDN 加载 mermaid + echarts + 3d-force-graph，jsdelivr→unpkg 双 fallback | 需联网；大图首次加载略慢 |
| **offline** | 离线归档、打印、邮件附件 | Node 脚本 SSR：ECharts 内置 SVG 渲染器，Mermaid 三档兜底（mermaid-isomorphic → mmdc → placeholder） | 3D KG **无离线模式**（WebGL 不能 SVG 化） |

## 两套主题

| 主题 | 配色 | 字体 | 适配 |
|---|---|---|---|
| `terminal` | 黑 #0a0a0a + 酸黄 #d4ff00 + 灰阶 | JetBrains Mono | biz-html-viz |
| `deck` | 深空 #030711 + 青 #42e8ff + 金 #ffd987 | Inter | viz-deck |

主题文件：`themes/terminal.js` / `themes/deck.js`，均导出 `echartsTheme / mermaidTheme / componentTheme` 三组配置。

## 工作流程

### Step 1 — 强制读决策树

`references/decision-tree.md` 是数据形态 → 视觉类型的选型映射。**任何图表/KG 请求**先读这个再选模板。

### Step 2 — 选模板与契约

读 `references/chart-cookbook.md` 找出对应模板的数据契约。

### Step 3 — 选渲染模式

**Inline 模式**（默认）：

往用户 HTML 报告里嵌入 Mermaid/ECharts/组件块，并在 `</body>` 前加：

```html
<script>
  window.VIZ_CHARTS_OPTS = {
    mermaidTheme: /* terminal | deck mermaidTheme 对象 */,
    echartsTheme: /* 同上的 echartsTheme 对象 */
  };
</script>
<script src="vendor/loaders/cdn-loader.js"></script>
```

**Offline 模式**（仅 Mermaid + ECharts，不含 3D KG）：

```bash
cd .claude/skills/viz-charts/renderers/node
npm install --silent
# Mermaid 离线渲染需要 chromium（仅首次）
npx playwright install chromium

node render-mermaid.mjs --input arch.mmd --output arch.svg --theme terminal
node render-echarts.mjs --input trend.json --output trend.svg --theme deck
node batch.mjs --input-dir ./charts --output-dir ./svgs --theme terminal
```

### Step 4 — 3D KG（特殊路径，只 inline）

读 `references/kg-builder-guide.md` 后：

```bash
node builders/code-kg.mjs --repo ./my-app --output code-kg.json --group-by dir
node builders/doc-kg.mjs --input ./docs --output doc-kg.json
# 渲染：把 JSON 替换进 viewer 模板的 {{KG_DATA_JSON}}
# 见 kg-builder-guide.md 的 "一键渲染脚本"
```

### Step 4b — SVG 知识图谱（环形 Context Graph / Circos · 纯 SVG · 可交互）

当关系图要**嵌进报告主流且要可交互**、或需要**矢量可缩放 / 可导出**而非 WebGL 时，用纯 SVG 两形态（读 `references/svg-kg-guide.md`）：

- **环形 Context Graph** —— 每个 category 一个独立环，节点排在环周，跨类贝塞尔连线、同类环内弧。数据/渲染解耦的 `{categories, entities, relationships}` 模型。交互：**拖拽节点 · 滚轮缩放 · 拖背景平移 · 点节点 BFS 邻域高亮 · 搜索定位**，外加环形 ↔ 力导向切换、按类过滤。适合"读类内结构 + 跨类关系密度"。
- **Circos 弦图** —— 一个大环切成扇区（每类一段 ideogram），外圈柱状 track 记权重，内部 ribbon 连关系。交互：悬停实体/扇区高亮其全部 ribbon。适合"在一张图里读全局关系 + 每实体权重"。

两者都是单段 SVG + 原生 JS（无 WebGL、无第三方图库），可直接落进 HTML 报告或 deck 的 `<section>`。何时用 3D vs SVG：节点多、要空间感 → 3D WebGL；要嵌报告、要交互/可导出/打印 → SVG 环形或 Circos。

### Step 5 — Motion → MP4（讲演 / 路演 / 演示视频）

仅当需求是**动画图表 + 录制视频**时启用。先读 `references/motion-charts.md` 选 motion 类型，再读 `references/mp4-export.md` 走 huashu-design 桥接。**终端风（biz-html-viz）禁用 motion**——决策签字报告必须零动效。

```bash
# 1) 生成 motion stage HTML（用 templates/motion/motion-stage-template.html）
# 2) 用 huashu-design 录制（CLI 风格：位置参数 + --key=value；输出自动同名 .mp4）
node ~/.claude/skills/huashu-design/scripts/render-video.js \
  ./output/trend-motion.html \
  --duration=6 --width=1920 --height=1080
# 3) 25fps + 60fps + GIF 三件套
bash ~/.claude/skills/huashu-design/scripts/convert-formats.sh ./output/trend-motion.mp4
```

时长 / 缓动 / 帧率请用 `themes/motion.js` 的 preset，保证多个动图节奏一致。

### Step 6 — 一致性检查

- 同一份报告内**所有图表用同一主题**（不要 terminal+deck 混搭）
- ECharts 系列 ≤ 7 个，Mermaid 节点 ≤ 30，超过转 ECharts graph 或 3D KG
- 每张图都有 `<figcaption>` 或 markdown 说明
- offline 输出的 SVG 含 `viewBox` 保证响应式
- 3D KG 单页不超过 1 个（多 WebGL canvas 同页性能崩）

## 标准嵌入结构

### Mermaid

```html
<figure class="chart-mermaid">
  <pre class="mermaid-source">
flowchart LR
    A[Event] --> B{Risk Gate}
    B -->|approved| C[Execute]
  </pre>
  <div class="mermaid-output"></div>
  <figcaption>图 1 · 主流程</figcaption>
</figure>
```

### ECharts

```html
<figure class="chart-echarts">
  <div data-echarts-option='{"xAxis":...,"series":[...]}'
       style="width:100%;height:320px"></div>
  <figcaption>图 2 · 季度营收</figcaption>
</figure>
```

### 自研组件

```html
<div class="kpi-card" data-kpi='{"label":"BURN","value":"¥1.06M","sparkline":[1,2,3,4]}'></div>
<span class="sparkline" data-spark='{"data":[1,2,3]}'></span>
<div class="mini-gauge" data-gauge='{"value":78,"max":100,"label":"完成度"}'></div>
<div class="progress-bar ok" data-progress='{"label":"M0","value":100}'></div>
<div class="tag-cloud" data-tags='[{"label":"Go","weight":10}]'></div>
```

### 3D KG

通常**独立链接**或**iframe 嵌入**，不掺主报告 main flow：

```html
<a href="./code-kg.html" class="btn-card">
  <h3>项目代码 KG (3D 交互)</h3>
  <p>点击在新窗口打开 · 142 文件 · 387 处依赖</p>
</a>
```

## 反模式

- ❌ 同一报告里混用 terminal + deck 主题
- ❌ 用 3D 图表（炫技）—— 仅在信息密度需要时用 3D 知识图谱
- ❌ Mermaid 节点 > 30 还硬画
- ❌ 直接把 ECharts option 写一大段 inline `<script>` 而不用 `data-echarts-option` 契约
- ❌ Offline 输出的 SVG 缺 viewBox
- ❌ 跳过 decision-tree.md 凭直觉选图
- ❌ 把"关键单值"用 ECharts 渲染（应该用 kpi-card 组件）
- ❌ 单页放多个 3D KG（WebGL 资源冲突）
- ❌ 在 terminal 主题 / 决策签字报告里加 motion 动画（违反 biz-html-viz 的"零动效"禁令）
- ❌ 一份 motion stage > 15 秒（观众注意力不够，分段）
- ❌ 录制画布 ≠ 1920×1080（上台投影/嵌入 keynote 会拉伸）
- ❌ 在 motion stage 里嵌多个图表（一 stage 一焦点，方便录制窗口对齐）

## 文件结构

```
viz-charts/
├── SKILL.md                          这份
├── README.md                         安装与速查
├── references/
│   ├── decision-tree.md              图表选型决策树（必读）
│   ├── chart-cookbook.md             36+ 视觉的数据契约
│   ├── integration-guide.md          如何集成进 biz-html-viz / viz-deck
│   ├── kg-builder-guide.md           3D KG 构建指南
│   ├── svg-kg-guide.md               环形 Context Graph + Circos 弦图（纯 SVG · 可交互）
│   ├── motion-charts.md              v2 新增 · motion 图表三类模式
│   └── mp4-export.md                 v2 新增 · 视频导出工具链桥接
├── themes/
│   ├── terminal.js                   biz-html-viz 配色
│   ├── deck.js                       viz-deck 配色
│   └── motion.js                     v2 新增 · 动画时长/缓动/帧率 preset
├── components/                       5 自研轻量组件
│   ├── kpi/kpi-card.html
│   ├── sparkline/sparkline.html
│   ├── gauge/mini-gauge.html
│   ├── progress/progress-bar.html
│   └── tag-cloud/tag-cloud.html
├── templates/
│   ├── mermaid/                      11 种 .mmd 模板
│   ├── echarts/                      25 种 .json 模板
│   ├── kg3d/                         3 种 3D KG viewer
│   │   ├── code-graph.html
│   │   ├── doc-graph.html
│   │   └── data-graph.html
│   └── motion/                       v2 新增 · motion stage 模板
│       └── motion-stage-template.html
├── builders/                         3D KG 数据生成器
│   ├── code-kg.mjs                   从 git repo 抽代码图
│   └── doc-kg.mjs                    从 markdown 抽文档图
├── vendor/loaders/
│   └── cdn-loader.js                 inline 模式：双 CDN fallback
├── renderers/node/                   offline 模式
│   ├── package.json
│   ├── render-mermaid.mjs
│   ├── render-echarts.mjs
│   └── batch.mjs
└── examples/
    ├── inline-terminal.html          完整 demo（终端风内联）
    ├── inline-deck.html              完整 demo（讲演风内联）
    ├── kg-doc-demo.html              3D 文档 KG 演示
    └── kg-code-demo.html             3D 代码 KG 演示
```

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
