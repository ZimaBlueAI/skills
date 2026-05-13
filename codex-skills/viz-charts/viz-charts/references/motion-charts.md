# motion-charts: 让数据图表动起来

> v2 新增。把静态 ECharts / Mermaid / KG 升级成"可被录制成 MP4"的动效图表，配合 `huashu-design` 的 `render-video.js` 出片。

## 何时启用 motion 模式

- 用户明确说 "做个动画版"、"导出 MP4"、"做成视频"、"加 reveal"、"做个 walkthrough"
- 上层 `viz-deck` skill 在 motion-mode（讲演动画）调用本 skill
- 数据本身有**时间维度**（time-series 演化、KG 节点逐级展开、流程逐步推进）

不要给静态决策报告（biz-html-viz / terminal 主题）加动效——那是反模式。

## 三类动效图表

| 类型 | 触发场景 | 时长建议 | 实现 |
|---|---|---|---|
| **frame-step reveal** | 数据点 1-by-1 出现，配解说 | 2-8s | ECharts `animationDelay` per series |
| **temporal sweep** | 时间轴扫过，柱/线增长 | 3-10s | ECharts `dataset.transform` + setOption 循环 |
| **graph orbit** | 3D KG 自动旋转 / 节点高亮巡游 | 6-12s | 3d-force-graph `cameraPosition` 轨迹 |

## 标准 motion 嵌入结构

每个 motion 图表是一个**独立 stage HTML 页**（不嵌进主报告），方便用 Playwright 录制：

```html
<!doctype html>
<html data-motion-stage data-record-seconds="6">
  <head>
    <meta charset="utf-8">
    <title>{{slug}} · motion stage</title>
    <style>
      html, body { margin: 0; padding: 0; background: var(--bg); overflow: hidden; }
      .stage { width: 1920px; height: 1080px; }  /* 录制画布 */
    </style>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
  </head>
  <body>
    <div class="stage" id="stage"></div>
    <script>
      // motion: 在 record-seconds 内完成全部动画，最后一帧 hold 0.5s
      const chart = echarts.init(document.getElementById('stage'));
      chart.setOption({/* ...含 animationDuration ... */});
    </script>
  </body>
</html>
```

**关键属性**：`data-motion-stage` 标记本页可录制，`data-record-seconds="N"` 告诉 huashu render-video.js 该录几秒。

## 录制成 MP4（桥接 huashu-design）

本 skill 不自己实现录屏。统一交给 `~/.claude/skills/huashu-design/scripts/render-video.js`：

```bash
# 录制单个 motion stage
node ~/.claude/skills/huashu-design/scripts/render-video.js \
  --input ./output/trend-motion.html \
  --output ./output/trend-motion.mp4 \
  --width 1920 --height 1080 --fps 25 --duration 6

# 60fps 插帧 + GIF 兜底
bash ~/.claude/skills/huashu-design/scripts/convert-formats.sh ./output/trend-motion.mp4
```

输出：`trend-motion.mp4`（25fps）+ `trend-motion-60fps.mp4`（插帧）+ `trend-motion.gif`（palette 优化）。

详细参数见 `references/mp4-export.md`。

## ECharts motion 三种典型动画

### 1. Series reveal（每个 series 错峰入场）

```js
{
  series: data.map((s, i) => ({
    ...s,
    animationDuration: 600,
    animationDelay: i * 250,            // 错峰
    animationEasing: 'cubicOut'
  }))
}
```

### 2. Dataset sweep（时间轴扫过）

```js
const frames = [...]; // 每帧一个 option snapshot
let i = 0;
const tick = setInterval(() => {
  chart.setOption(frames[i++]);
  if (i >= frames.length) clearInterval(tick);
}, 200);
```

### 3. Line draw-on（折线沿 x 轴绘出）

ECharts 5+ 默认支持，只需 `animationDuration: 2000` 且 `series.smooth = true`。

## Mermaid motion

Mermaid 自身不支持帧动画。如果场景需要"流程逐步揭示"——用 ECharts graph 类型代替，或用 CSS `@keyframes` 给 SVG 出口节点逐个 fade-in：

```css
.mermaid-output > svg .node {
  opacity: 0;
  animation: fadeIn 0.5s forwards;
}
.mermaid-output > svg .node:nth-child(1) { animation-delay: 0.1s; }
.mermaid-output > svg .node:nth-child(2) { animation-delay: 0.4s; }
/* ... */
@keyframes fadeIn { to { opacity: 1; } }
```

## 3D KG motion

3D 知识图谱用 `cameraPosition()` 做轨道运镜：

```js
const Graph = ForceGraph3D()(document.getElementById('graph'));
let angle = 0;
setInterval(() => {
  const distance = 400;
  angle += Math.PI / 300;
  Graph.cameraPosition({
    x: distance * Math.sin(angle),
    z: distance * Math.cos(angle)
  });
}, 30);
```

录制时长建议 ≥ 10s（一圈轨道运镜）。

## 反模式

- ❌ 在终端风（biz-html-viz / terminal 主题）下加动画——违反 `references/design-system.md` 的"零动效"禁令
- ❌ 一份报告里嵌 5+ motion stage —— 每多一个就多一次录制成本，挑 1-2 个核心数据点做动效
- ❌ 动画时长 > 15s —— 观众注意力不够，分段
- ❌ 用 motion 掩盖数据本身平淡 —— 数据无故事时，加动画不会更好
- ❌ 录制画布尺寸 ≠ 1920×1080 —— 上台投影 / 嵌入 keynote 容易拉伸
- ❌ 用 `prefers-reduced-motion` 之外的方式禁动画 —— 录制前用 `?motion=force` 强制启用
