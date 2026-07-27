# Chart Cookbook · 数据契约与速查表

每种图的"数据要长什么样"。决策树告诉你**用哪种**，本表告诉你**怎么填**。

## Mermaid（11 种）

Mermaid 是文本描述语言，模板都在 `templates/mermaid/*.mmd`。直接复制对应文件、改 placeholder。

| 类型 | 文件 | 关键语法 |
|---|---|---|
| flowchart | flowchart.mmd | `flowchart LR` 或 `TD`，节点 `A[文字]`，边 `A --> B` |
| sequence | sequence.mmd | `sequenceDiagram`，`A->>B: msg`，`activate` / `deactivate` |
| class | class.mmd | `classDiagram`，`class X { +method() }`，`A <\|-- B` 继承 |
| state | state.mmd | `stateDiagram-v2`，`[*] --> A`，`A --> B: event` |
| ER | er.mmd | `erDiagram`，`A \|\|--o{ B : has`，可加字段 |
| gantt | gantt.mmd | `gantt`，`section X`，`task :crit, t1, after t2, 5d` |
| journey | journey.mmd | `journey`，`section X`，`task : 1: Actor` |
| mindmap | mindmap.mmd | `mindmap`，缩进表达层级 |
| timeline | timeline.mmd | `timeline`，`section`，`时间 : 事件` |
| sankey | sankey.mmd | `sankey-beta`，CSV `source,target,value` |
| gitgraph | gitgraph.mmd | `gitGraph`，`commit`、`branch`、`merge` |

**通用纪律**：超过 30 节点换 ECharts graph 或 3D KG。

## ECharts（25 种）

每个 `templates/echarts/*.json` 都含 `_meta.use_when` 和 `_meta.data_shape`。模板可直接 setOption。

### 时间序列

| 文件 | 何时用 | 关键字段 |
|---|---|---|
| line-trend.json | 1-3 系列趋势，≥6 点 | `xAxis.data` 时间数组，`series[].data` |
| stacked-area.json | 多系列累积总和 | 加 `series[].stack: 'total'` + `areaStyle:{}` |
| area.json | 单系列累积 | `series[0].areaStyle` |
| candlestick.json | 价格区间（OHLC） | `data: [[open, close, low, high]]` |
| calendar-heatmap.json | 全年逐日 | `series[0].coordinateSystem: 'calendar'` |
| theme-river.json | 多类别消长 | `data: [[date, value, category]]` |

### 类别比较

| 文件 | 何时用 | 关键字段 |
|---|---|---|
| bar-horizontal.json | 排序对比，≤12 项 | `yAxis: {type: 'category', inverse: true}` |
| bar-grouped.json | 多类 × 多维 | `series` 多项不加 stack |
| bar-stacked.json | 总和 + 构成 | `series[].stack: 'total'` |
| bump-chart.json | 排名变化 | `yAxis.inverse: true`, `min/max` 锁定 |
| radar.json | ≤4 主体 6 维度 | `radar.indicator: [{name,max}]` |
| pictorial-bar.json | 信息图风类别对比 | `type: 'pictorialBar'`, `symbolRepeat: 'fixed'` |

### 占比与构成

| 文件 | 何时用 | 关键字段 |
|---|---|---|
| pie-donut.json | ≤6 块 | `radius: ['48%','72%']` 是环图，`radius: '70%'` 是饼 |
| treemap.json | 层级占比 | `data: [{name, value, children}]` |
| sunburst.json | 多层环 | 同 treemap，`type: 'sunburst'` |
| funnel.json | 转化漏斗 | `sort: 'descending'`，按 value 自动排序 |
| sankey.json | 多对多流向 | `data: [{name}]`，`links: [{source,target,value}]` |

### 关系与分布

| 文件 | 何时用 | 关键字段 |
|---|---|---|
| scatter.json | 二维相关 | `data: [[x, y, label?]]` |
| heatmap.json | 二维矩阵密度 | `data: [[xIdx, yIdx, value]]`，加 `visualMap` |
| parallel.json | 5-12 维样本对比 | `parallelAxis: [{dim, name}]` |
| graph-force.json | 10-200 节点（>200 用 3D KG） | `categories`, `nodes`, `links` |
| boxplot.json | 分布形态 | `data: [[low, q1, median, q3, high]]` |

### 关键单值

| 文件 | 何时用 | 关键字段 |
|---|---|---|
| gauge.json | 进度/达成率 | `series[0].data: [{value, name}]` |
| gauge-multi.json | 多 KPI 同表盘 | `series[0].data` 多项，每项 `offsetCenter` 不同 |
| geo-china.json | 中国省份分布 | 需 `echarts.registerMap('china', json)` |

## 自研轻量组件（5 种）

### KPI Card

`components/kpi/kpi-card.html`

```html
<div class="kpi-card" data-kpi='{
  "label": "BURN RATE",        // 上方小标签（必填）
  "value": "¥1.06M",            // 大数字（必填，可含单位）
  "delta": "+12% vs Q2",        // 下方变化（选填）
  "direction": "down",          // up | down | "" 影响 value 颜色
  "sparkline": [1.0, 0.9, 1.1]  // 可选数值数组，渲染内嵌迷你趋势线
}'></div>
```

讲演风加 `class="kpi-card kpi-card--deck"`。

### Sparkline (inline)

`components/sparkline/sparkline.html`

```html
<span class="sparkline" data-spark='{
  "data": [3, 5, 2, 8, 4, 9, 7],
  "color": "auto",       // auto | up | down | "#xxx"
  "width": 80,           // 默认 80
  "height": 20,          // 默认 20
  "showDot": true,       // 末尾点
  "showFill": true       // 区域填充
}'></span>
```

### Mini Gauge

`components/gauge/mini-gauge.html`

```html
<div class="mini-gauge" data-gauge='{
  "value": 78,
  "max": 100,
  "label": "Sprint",
  "unit": "%"
}'></div>
```

### Progress Bar

`components/progress/progress-bar.html`

```html
<div class="progress-bar ok" data-progress='{
  "label": "M0 模块",
  "value": 78,
  "max": 100,
  "rightLabel": "78/100"
}'></div>
```

class 修饰：`ok | warn | danger`（影响填充色）。多项时外包 `<div class="progress-group">`。

### Tag Cloud

`components/tag-cloud/tag-cloud.html`

```html
<div class="tag-cloud" data-tags='[
  {"label": "Python", "weight": 10, "category": "lang"},
  {"label": "Go",     "weight": 8,  "category": "lang"},
  {"label": "Redis",  "weight": 5,  "category": "db"}
]'></div>
```

`weight: 1-10` 决定字号；`category` 分组渲染。

## 3D KG（3 种 viewer 模板）

数据契约统一，详见 `references/kg-builder-guide.md`。

| 模板 | 何时用 | builder |
|---|---|---|
| `templates/kg3d/code-graph.html` | 代码结构关系 | `builders/code-kg.mjs` |
| `templates/kg3d/doc-graph.html` | 文档概念图谱 | `builders/doc-kg.mjs` |
| `templates/kg3d/data-graph.html` | 通用 KG（任意来源） | 自定义 / 手填 |

统一节点契约：

```json
{
  "id": "唯一标识",
  "name": "显示名",
  "group": "分类",
  "size": 4,
  "desc": "鼠标悬浮 / 点击展示的描述"
}
```

统一边契约：

```json
{
  "source": "id1",
  "target": "id2",
  "type": "imports | mentions | parent-of | ...",
  "value": 1
}
```

## 反模式速查

- ❌ 饼图 ≥ 7 块 → 改横向 bar
- ❌ Mermaid ≥ 30 节点 → 改 ECharts graph 或 3D KG
- ❌ 折线 ≥ 4 系列同一图 → 拆 small multiples
- ❌ 同一报告混用 terminal + deck 主题
- ❌ 用 ECharts gauge 表达单个 KPI → 改用 kpi-card 组件（更轻、更聚焦）
- ❌ 散点只有一维 → 改 bar
- ❌ 自研组件不给 `data-rendered` 属性反复渲染（已在 JS 中防护，但人为干预可能破坏）
