# SVG 知识图谱 — 环形 Context Graph + Circos 弦图

两种纯 SVG（无 WebGL、无第三方图库）的关系可视化，可直接嵌进 HTML 报告或 deck 的
`<section>`，矢量可缩放、可打印、可导出。共用同一份数据模型。

## 数据模型（data/render 解耦）

```js
const GRAPH = {
  categories: [ { id:'core', label:'核心 CORE', color:'#f2b34b' }, /* … */ ],
  entities:   [ { id:'zima', category:'core', label:'ZimaBlueAI', val:18, desc:'…' }, /* … */ ],
  relationships: [ { from:'zima', to:'deck', type:'own' }, /* … */ ]
};
const ELINK = { own:'#f2b34b', run:'#bfe6ff', deliver:'#46c98b', bridge:'#9d8cff', emit:'#e3795f' };
```

- `categories` 定义分组与配色；`entities` 挂 `category` + `val`（权重，用于节点大小 / track 高度）。
- `relationships` 是 `from→to→type`；`type` 映射到一组连线/丝带颜色。
- 改数据不动渲染，改渲染不动数据。

辅助：`const NS='http://www.w3.org/2000/svg'; function svgEl(t,a){const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);return e;}`

---

## 形态 A — 环形 Context Graph

每个 category 一个独立的环（网格排布），节点按角度均匀排在环周；跨类关系画贝塞尔曲线、
同类关系画指向环心的内弧。

**布局**
- `catCenter(cat)` → 网格中心（如 3 列 × 2 行）；`ringR(cat)` 随节点数缩放（clamp）。
- 节点角 `a = -π/2 + i/n * 2π`，坐标 `cx+cos(a)*R, cy+sin(a)*R`。
- 每环画一圈淡虚线 + 类标签 + 一层极淡填充 disc，让"不同的环"一眼可辨。
- 节点标签沿径向朝外摆放（`text-anchor` 按 `cos(a)` 取 start/middle/end），避开环心连线团。

**交互（必备）**
- **拖拽节点**：`pointerdown` 记 `dragNode`、`pointermove` 用 `toGraph(ev)` 换算坐标、`pointerup` 释放；`moved` 标记区分拖拽与点击。
- **滚轮缩放**：对 `scene` group 施 `translate()+scale()`，向光标位置缩放。
- **拖背景平移**：在空白处 `pointerdown` 起 pan。
- **点节点 BFS**：高亮 1 跳邻域 + 入射边，其余压暗，弹信息卡。
- **搜索定位**：匹配 label/id → 居中 + 选中。
- **环形 ↔ 力导向切换**：force 模式跑一个轻量斥力 + 弹簧 + 居中的 `requestAnimationFrame` 迭代。
- **按类过滤**：chips 切换某类显隐，重排。

坐标换算（含缩放/平移）：
```js
function toGraph(ev){ const r=svg.getBoundingClientRect(), sx=W/r.width, sy=H/r.height;
  return { x:((ev.clientX-r.left)*sx-view.tx)/view.k, y:((ev.clientY-r.top)*sy-view.ty)/view.k }; }
```

**何时用**：要读"类内结构 + 跨类关系密度"，且要嵌进报告主流可交互。

---

## 形态 B — Circos 弦图（ideogram + track + ribbon）

基因组学经典圆形布局：一个大环按类切成扇区，外圈柱状 track 记每实体权重，内部 ribbon
（跨弦）连关系。

**画法**
- `polar(r,deg)` + `arcPath(r,a0,a1)`：每类一段弧（粗 stroke 当 ideogram），角宽 ∝ 实体数。
- 实体在本段内均匀取角 `entAngle[id]`；外圈画一根 `R+7 → R+7+val/maxVal*TRACK` 的柱（histogram track）。
- ribbon：从 `from` 角到 `to` 角画一条二次贝塞尔，控制点拉向圆心（`cpx=cx+((x0+x1)/2-cx)*0.16`），按 `type` 着色、低透明。
- 圆心放总览标签（实体数 / 关系数）。

**交互**
- 悬停某实体的 track 柱（用一根透明加宽 line 当 hit target）→ 高亮其全部 ribbon、压暗其余、弹 tooltip。
- 悬停扇区 / 类标签 → 高亮该类全部 ribbon。

**何时用**：要在一张静态友好的图里读"全局关系 + 每实体权重"，适合封面/总览页与打印。

---

## 一致性

- 配色走 `categories[].color` 与 `ELINK`，与报告主题（terminal / deck）同源。
- 一页一个交互式 SVG KG 为宜；多个并存时关掉其中的全局 `pointermove`/`wheel` 监听以免互抢。
- 两形态都带 `<title>`/说明；嵌入 `<figure>` 时给 `<figcaption>`。

## 参考实现

完整可跑的两形态（含全部交互）见仓库 `taste-engine/demo/taste-demo.html` 的
`buildContextGraph()` 与 `buildCircos()`——可直接对照移植。
