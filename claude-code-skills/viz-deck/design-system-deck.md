# Design System: Keynote-Grade Presentation Reports

讲演型可视化报告的设计 DNA，源自 Octarus 系列报告的视觉语言。

> **与 biz-html-viz 的边界**：biz-html-viz 是终端风（黑黄、零动效、给工程师扫读），viz-deck 是讲演风（深空蓝紫青、玻璃拟态、含微动效，给客户/投资人/团队 keynote 走读）。
>
> 同一个项目可以两个 skill 各出一份——决策版打印归档，讲演版会上展示。

## 核心原则

1. **场域感优先于密度**——这是 keynote，不是仪表盘。允许留白、允许气氛
2. **微动效服务叙事节奏**——`reveal` 滚动入场、`orbitSpin` 主视觉、`flowLight` 流光，**禁止**纯装饰动画
3. **深空蓝紫青调色 + 一类强调金**——冷感为主，金色仅用于关键状态/达成
4. **Inter 一种字体，权重档分明**——不靠多字体，靠 weight + spacing
5. **每章一编号 + eyebrow + 口号 + lead**——四件套是讲演节奏感来源

## CSS 变量（每个模板必须复制此段）

```css
:root {
  /* Colors */
  --bg: #030711;
  --bg-2: #07111f;
  --panel: rgba(12, 26, 46, 0.72);
  --panel-strong: rgba(16, 36, 62, 0.92);
  --line: rgba(151, 209, 255, 0.16);
  --line-strong: rgba(151, 209, 255, 0.34);

  --text: #edf7ff;
  --muted: #a8bdd5;
  --faint: #688096;

  --cyan: #42e8ff;       /* 主强调 */
  --blue: #6ca5ff;       /* 次强调 */
  --silver: #d8e8f4;
  --gold: #ffd987;       /* 达成 / 关键里程碑 */
  --green: #78f7c5;      /* 进行中 / OK */
  --red: #ff8c8c;        /* 风险 / 阻塞 */
  --violet: #b893ff;     /* 远期 / 蓝图 */

  --shadow: 0 28px 90px rgba(0, 0, 0, 0.48);
  --radius-xl: 34px;
  --radius-lg: 24px;
  --radius-md: 16px;
  --max: 1200px;
  color-scheme: dark;
}
```

## 字体

```css
font-family: Inter, ui-sans-serif, system-ui, -apple-system,
             BlinkMacSystemFont, "Segoe UI",
             "Microsoft YaHei", "PingFang SC", sans-serif;
```

仅 Inter 一种。中文 fallback PingFang SC / Microsoft YaHei。

**字重档**：

| 用途 | weight | size |
|---|---|---|
| h1 标题 | 800 | 3.2-4rem |
| h2 章节 | 700 | 2.2-2.6rem |
| h3 卡片标题 | 600 | 1.2-1.45rem |
| eyebrow（章节小标） | 600，letter-spacing 0.18em，text-transform uppercase | 0.78rem |
| 章节编号（kicker-num） | 700 | 2.4-3.2rem，渐变填色 |
| 正文 lead | 400 | 1.05rem |
| 正文 body | 400 | 0.96rem |
| muted note | 400 | 0.85-0.9rem |

## 背景三层叠

每个模板 body 都用这套，是讲演风的"场域感"来源：

```css
body {
  background:
    radial-gradient(circle at 18% 5%, rgba(66, 232, 255, 0.2), transparent 32rem),
    radial-gradient(circle at 84% 12%, rgba(255, 217, 135, 0.12), transparent 30rem),
    radial-gradient(circle at 45% 52%, rgba(108, 165, 255, 0.12), transparent 36rem),
    linear-gradient(180deg, #02050c 0%, #06111f 48%, #02050c 100%);
}

/* 网格底纹 */
body::before {
  content: "";
  position: fixed; inset: 0; z-index: -3;
  opacity: 0.35;
  background-image:
    linear-gradient(rgba(151, 209, 255, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(151, 209, 255, 0.045) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: linear-gradient(to bottom, rgba(0, 0, 0, 0.9), rgba(0, 0, 0, 0.25) 35%, rgba(0, 0, 0, 0.1));
}

/* 缓慢扫光 */
body::after {
  content: "";
  position: fixed; inset: 0; z-index: -2; pointer-events: none;
  background:
    linear-gradient(120deg, transparent 0 20%, rgba(66, 232, 255, 0.045) 38%, transparent 56% 100%),
    radial-gradient(circle at 50% 0%, rgba(255, 255, 255, 0.06), transparent 38rem);
  animation: atmosphericSweep 18s linear infinite;
}

@keyframes atmosphericSweep {
  from { transform: translate3d(-8%, 0, 0); }
  to   { transform: translate3d(8%, 0, 0); }
}
```

## 通用组件库（必须保持视觉一致）

### `.section` 章节容器

```css
.section {
  width: min(var(--max), calc(100vw - 40px));
  margin: 0 auto;
  padding: 8rem 0 5rem;
  position: relative;
}
```

每章顶部留 8rem 是讲演节奏。

### `.eyebrow` 章节小标

```css
.eyebrow {
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: var(--cyan);
}
```

### `.kicker-num` 章节编号

```css
.kicker-num {
  font-size: 3rem;
  font-weight: 700;
  background: linear-gradient(135deg, var(--cyan), var(--silver));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  display: block;
  line-height: 1;
}
```

### `.headline-gradient` 标题渐变填色

```css
.headline-gradient {
  background: linear-gradient(135deg, var(--cyan), var(--silver));
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

### `.panel` 玻璃卡片（核心组件）

```css
.panel {
  border: 1px solid var(--line);
  border-radius: var(--radius-xl);
  background: linear-gradient(180deg, var(--panel-strong), var(--panel));
  box-shadow: var(--shadow);
  padding: 2rem 2.2rem;
  position: relative;
  overflow: hidden;
}
.panel::before {
  /* 顶部 1px 流光描边 */
  content: ""; position: absolute; inset: 0; border-radius: inherit;
  padding: 1px;
  background: linear-gradient(135deg, var(--line-strong), transparent 50%);
  -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
  -webkit-mask-composite: xor; mask-composite: exclude;
  pointer-events: none;
}
```

### `.tag` / `.pill` 状态标签

```css
.tag, .pill {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid var(--line-strong);
  background: rgba(12, 26, 46, 0.6);
  font-size: 0.78rem;
  color: var(--silver);
}
.status-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--faint);
}
.status-done     { background: var(--green); box-shadow: 0 0 12px var(--green); }
.status-progress { background: var(--blue);  box-shadow: 0 0 12px var(--blue); }
.status-future   { background: var(--gold);  box-shadow: 0 0 12px var(--gold); }
.status-risk     { background: var(--red);   box-shadow: 0 0 12px var(--red); }
```

### `.reveal` 滚动入场动画

```css
.reveal {
  opacity: 0;
  transform: translateY(28px);
  transition: opacity 0.7s ease, transform 0.7s ease;
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
@media (prefers-reduced-motion: reduce) {
  .reveal { opacity: 1; transform: none; transition: none; }
}
```

配套 IntersectionObserver 脚本（见模板底部 `<script>`）。

### `.deck-nav` 顶部章节导航

吸顶胶囊导航，列章节链接。点击锚点跳转。

### `.progress-line` 顶部进度条

```css
.progress-line {
  position: fixed; top: 0; left: 0;
  z-index: 80; width: 100%; height: 3px;
  background: rgba(255, 255, 255, 0.08);
}
.progress-line span {
  display: block; width: 0%; height: 100%;
  background: linear-gradient(90deg, var(--cyan), var(--blue), var(--gold));
  box-shadow: 0 0 24px rgba(66, 232, 255, 0.75);
}
```

### `.skip-link` 无障碍跳转

```css
.skip-link {
  position: fixed; left: 18px; top: 18px;
  z-index: 100;
  transform: translateY(-140%);
  padding: 10px 14px;
  border-radius: 999px;
  background: var(--cyan); color: #00121d;
  font-weight: 800;
  transition: transform 0.2s ease;
}
.skip-link:focus { transform: translateY(0); }
```

## 章节叙事节奏（每章四件套）

每个 `<section class="section">` 必须包含：

```html
<section class="section" id="...">
  <div class="section-intro reveal">
    <span class="kicker-num">01</span>          <!-- 编号 -->
    <span class="eyebrow">Current State</span>  <!-- 英文小标 -->
    <h2>我们已经站在哪里</h2>                   <!-- 中文主标 -->
    <p class="lead">...</p>                     <!-- 1-2 句导语 -->
  </div>
  <!-- 主体内容：grid / panels / 图表 -->
</section>
```

这是讲演节奏感的来源，不要省略。

## 主视觉（hero / orb-card 风格）

每份报告 opening 段建议有一个**主视觉装置**：

- **轨道环（orbit）**：3 圈不同角度/速度的圆环，承载 3 个核心标签
- **流光面板**：panel 加 `flowLight` keyframe
- **粒子场**：`<canvas id="field">` + 简单 connect 算法（最多 92 节点）
- **知识图谱**：SVG 路径 + arrow marker + `dash` 流动

四种里挑一个，不要全用。

## 关键动画（仅这几种允许）

```css
@keyframes atmosphericSweep { ... }  /* 18s 背景扫光 */
@keyframes pulseRing        { ... }  /* 主视觉脉冲 */
@keyframes orbitSpin        { ... }  /* 轨道环 */
@keyframes breathe          { ... }  /* 呼吸光 */
@keyframes flowLight        { ... }  /* 流光过桥 */
@keyframes dash             { ... }  /* SVG 路径流动 */
```

每个 keyframe 必须 ≥ 8s，避免视觉躁动。`prefers-reduced-motion` 必须降级。

## 视觉禁令

- ❌ 紫色作为主色（仅作 violet 远期标签）
- ❌ 圆角 < 16px（这是讲演风，硬角不合气场）
- ❌ 任何 emoji 当图标用
- ❌ 满屏粒子无主视觉锚点
- ❌ 多字体堆叠（Inter 一种就够）
- ❌ 多于 6 种 keyframe 动画并行
- ❌ 章节没有 eyebrow + kicker-num + lead 三件套

## 视觉允许

- ✅ 玻璃拟态（panel 半透 + 流光描边）
- ✅ 渐变填色文字（仅 h1 / kicker-num）
- ✅ 内联 SVG 知识图谱、流程图
- ✅ canvas 粒子场（节点 ≤ 92）
- ✅ IntersectionObserver 入场动画
- ✅ 状态点 + 标签胶囊体系

## 通用页面骨架

每个模板套这个骨架，主体在 `<main>` 里替换：

```html
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{TITLE}}</title>
  <meta name="description" content="{{DESCRIPTION}}" />
  <style>
    /* 粘贴 :root 变量 */
    /* 粘贴背景三层叠 */
    /* 粘贴所有通用组件 CSS */
    /* 模板特定 CSS 写在这之后 */
  </style>
</head>
<body>
  <a class="skip-link" href="#main">跳到主内容</a>
  <div class="progress-line" aria-hidden="true"><span></span></div>
  <canvas id="field" aria-hidden="true"></canvas>
  <nav class="deck-nav" aria-label="章节导航">
    <!-- 自动按章节生成链接 -->
  </nav>

  <main id="main">
    <!-- 模板特定章节 -->
  </main>

  <script>
    /* progress-line 滚动驱动 */
    /* IntersectionObserver 入场 */
    /* canvas particle field */
    /* nav active state */
  </script>
</body>
</html>
```
