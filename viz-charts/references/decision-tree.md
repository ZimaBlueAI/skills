# 图表选型决策树

**核心原则**：先看数据形态，再看你想表达什么。先表达，后修饰。

## 入口：你手上是什么？

```
你有什么数据？
│
├─ 关系/流程/层级（节点 + 边）→ 走 Mermaid
│
├─ 数值/类别/时间序列   → 走 ECharts
│
└─ 单个数字 + 趋势      → 走自研 KPI 组件
```

---

## 走 Mermaid 的情况

| 你想表达 | 用什么 | 模板 |
|---|---|---|
| 系统模块 + 调用关系 | **flowchart** TD/LR | `templates/mermaid/architecture-flowchart.mmd` |
| 数据从 A 流到 B 经过 N 步 | **flowchart** | `templates/mermaid/data-flow.mmd` |
| 多个角色之间的对话/调用顺序 | **sequenceDiagram** | `templates/mermaid/sequence.mmd` |
| 类/接口/继承结构（OO 设计） | **classDiagram** | `templates/mermaid/class.mmd` |
| 状态机（订单流转、工作流） | **stateDiagram-v2** | `templates/mermaid/state.mmd` |
| 数据库表结构关系 | **erDiagram** | `templates/mermaid/er.mmd` |
| 项目时间线/任务排期 | **gantt** | `templates/mermaid/gantt.mmd` |
| 用户旅程/情绪曲线 | **journey** | `templates/mermaid/journey.mmd` |
| 思维导图/概念发散 | **mindmap** | `templates/mermaid/mindmap.mmd` |
| 历史事件按年代排列 | **timeline** | `templates/mermaid/timeline.mmd` |
| 流量/资金/能量从源到汇 | **sankey-beta** | `templates/mermaid/sankey.mmd` |
| Git 分支演进 | **gitGraph** | `templates/mermaid/gitgraph.mmd` |

**纪律**：超过 ~30 节点的关系图换 ECharts graph，Mermaid 会变成意大利面。

---

## 走 ECharts 的情况

### 数值随时间变化

| 表达 | 图 | 模板 |
|---|---|---|
| 趋势（1-3 个系列） | **line** | `templates/echarts/line-trend.json` |
| 多个堆叠系列总和 | **stacked-area** | `templates/echarts/stacked-area.json` |
| 累积量随时间 | **area** | `templates/echarts/area.json` |
| K 线/价格区间 | **candlestick** | `templates/echarts/candlestick.json` |
| 几年内的逐日活跃度 | **calendar** | `templates/echarts/calendar-heatmap.json` |
| 多组分类随时间消长 | **themeRiver** | `templates/echarts/theme-river.json` |

### 类别比较

| 表达 | 图 | 模板 |
|---|---|---|
| 数值大小排序（≤12 项） | **bar** 横向 | `templates/echarts/bar-horizontal.json` |
| 多类别多维度对比 | **bar** 分组 | `templates/echarts/bar-grouped.json` |
| 总和 + 构成（多类别） | **bar** 堆叠 | `templates/echarts/bar-stacked.json` |
| 排名变化（1-5 个项目） | **lines** + step | `templates/echarts/bump-chart.json` |
| 6+ 维度对比 ≤4 主体 | **radar** | `templates/echarts/radar.json` |
| 异化对比（图标体量） | **pictorialBar** | `templates/echarts/pictorial-bar.json` |

### 占比与构成

| 表达 | 图 | 模板 |
|---|---|---|
| 整体的份额（≤6 块） | **pie / donut** | `templates/echarts/pie-donut.json` |
| 层级占比（树形） | **treemap** | `templates/echarts/treemap.json` |
| 多层环形占比 | **sunburst** | `templates/echarts/sunburst.json` |
| 漏斗转化（每步保留率） | **funnel** | `templates/echarts/funnel.json` |
| 流向分配（多对多） | **sankey** | `templates/echarts/sankey.json` |

### 关系与分布

| 表达 | 图 | 模板 |
|---|---|---|
| 二维相关性 | **scatter** | `templates/echarts/scatter.json` |
| 矩阵密度 | **heatmap** | `templates/echarts/heatmap.json` |
| 多维平行坐标对比 | **parallel** | `templates/echarts/parallel.json` |
| 大型网络/知识图谱 | **graph** force | `templates/echarts/graph-force.json` |
| 分布形态（中位数+箱体） | **boxplot** | `templates/echarts/boxplot.json` |

### 关键单值

| 表达 | 图 | 模板 |
|---|---|---|
| 进度/达成率（圆形） | **gauge** | `templates/echarts/gauge.json` |
| 仪表盘多指针 | **gauge** multi | `templates/echarts/gauge-multi.json` |
| 地理分布（中国） | **geo** | `templates/echarts/geo-china.json` |

---

## 走自研轻量组件的情况

这些是**不动 ECharts**的轻量 SVG 内联组件，零依赖、可独立用：

| 表达 | 组件 | 路径 |
|---|---|---|
| 大数字 + delta + sparkline 三件套 | **kpi-card** | `components/kpi/kpi-card.html` |
| 极简趋势线（数据≤30 点） | **sparkline** | `components/sparkline/sparkline.html` |
| 半圆达成度 | **mini-gauge** | `components/gauge/mini-gauge.html` |
| 横向进度条（≤5 项并列） | **progress-bar** | `components/progress/progress-bar.html` |
| 关键词云/技术栈展示 | **tag-cloud** | `components/tag-cloud/tag-cloud.html` |

**用纪律**：决策报告的"关键 KPI"区域必用 kpi-card，不要拿 ECharts gauge 凑数。

---

## 反模式（出现即返工）

- ❌ 用饼图展示 7+ 块（看不清）→ 改用横向 bar
- ❌ 用 3D 图表（炫技无意义）→ 一律改 2D
- ❌ 用 force-directed graph 展示 < 10 节点 → 改 Mermaid flowchart
- ❌ 用 line chart 展示 < 4 个数据点 → 改 KPI + delta
- ❌ 用 scatter 但只有一维数据 → 改 bar
- ❌ 把折线图刷成 12 个系列 → 拆成多个小 multiple
- ❌ 把所有图都做成深色滤镜（无对比层次）

---

## 风格映射

| 报告 skill | 用什么主题 | 调用方式 |
|---|---|---|
| biz-html-viz | terminal | `themes/terminal.js` |
| viz-deck | deck | `themes/deck.js` |

主题只换配色和字体，**图表选型不变**——决策树是设计语言中性的。
