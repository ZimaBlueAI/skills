# Design System: Terminal-Grade Business Reports

七份报告共享一套视觉语言。一眼能认出"这是同一套体系"。

## 核心原则

1. **信息密度优先于留白美学**——这是给决策者看的，不是落地页
2. **零动效**——`transition` 仅限 0.1s 的 hover 反馈，禁止任何 `@keyframes`
3. **黑底白字 + 一种强调色**——禁止渐变、禁止玻璃拟态、禁止 emoji 装饰图标
4. **等宽字体承载所有数据**——数字、ID、版本号、时间戳一律 mono
5. **横线分割 > 卡片分割**——卡片只在有交互或层级时使用

## CSS 变量（每个模板必须复制粘贴此段）

```css
:root {
  /* Colors — 终端风格 */
  --bg: #0a0a0a;
  --bg-elev: #141414;
  --bg-hover: #1c1c1c;
  --border: #2a2a2a;
  --border-strong: #3a3a3a;

  --fg: #e8e8e8;
  --fg-dim: #888;
  --fg-faint: #555;

  --accent: #d4ff00;        /* 仅一种强调色，类似 Bloomberg 终端的酸黄 */
  --accent-dim: #8a9e0a;
  --danger: #ff4444;
  --warn: #ffaa00;
  --ok: #44dd88;

  /* Typography */
  --font-mono: 'JetBrains Mono', 'SF Mono', 'Menlo', 'Consolas', monospace;
  --font-sans: 'Inter Tight', 'Söhne', system-ui, -apple-system, sans-serif;
  --font-serif: 'Newsreader', 'Source Serif 4', Georgia, serif;  /* 仅用于报告引言/复盘叙事 */

  /* Spacing */
  --gap-xs: 4px;
  --gap-sm: 8px;
  --gap-md: 16px;
  --gap-lg: 24px;
  --gap-xl: 48px;

  /* Layout */
  --max-width: 1200px;
  --content-width: 880px;   /* 正文阅读区，更窄以保证可读性 */
}
```

## 字体使用规则

| 字体 | 用途 | 字号 |
|------|------|------|
| `--font-mono` | 数据、ID、版本号、表头、所有数字、代码、标签 | 12-14px |
| `--font-sans` | 正文叙述、按钮、导航 | 14-16px |
| `--font-serif` | 报告标题（h1）、引言段、复盘叙事 | 28-48px |

**禁用字体**：Inter、Roboto、Arial、PingFang、思源黑体（除非 fallback）。

中文优先级：`'PingFang SC', 'Source Han Sans SC', sans-serif`，但仅在 `--font-sans` 中生效。

## 通用页面骨架

每个模板都用这个骨架，只填充 `<main>` 内部：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{REPORT_TITLE}}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter+Tight:wght@400;500;600;700&family=Newsreader:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
  <style>
    /* 粘贴上面的 :root 变量 */

    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body { background: var(--bg); color: var(--fg); }
    body {
      font-family: var(--font-sans);
      font-size: 14px;
      line-height: 1.6;
      padding: var(--gap-xl) var(--gap-lg);
    }

    /* 报告头：所有报告共用 */
    .report-header {
      max-width: var(--max-width);
      margin: 0 auto var(--gap-xl);
      border-bottom: 1px solid var(--border-strong);
      padding-bottom: var(--gap-lg);
    }
    .report-header .meta {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--fg-dim);
      text-transform: uppercase;
      letter-spacing: 0.1em;
      display: flex;
      gap: var(--gap-lg);
      margin-bottom: var(--gap-md);
    }
    .report-header h1 {
      font-family: var(--font-serif);
      font-size: 40px;
      font-weight: 600;
      line-height: 1.1;
      letter-spacing: -0.02em;
    }
    .report-header .subtitle {
      font-family: var(--font-sans);
      color: var(--fg-dim);
      margin-top: var(--gap-sm);
      font-size: 15px;
    }

    main {
      max-width: var(--max-width);
      margin: 0 auto;
    }

    /* 章节 */
    section { margin-bottom: var(--gap-xl); }
    h2 {
      font-family: var(--font-mono);
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.15em;
      color: var(--accent);
      padding-bottom: var(--gap-sm);
      border-bottom: 1px solid var(--border);
      margin-bottom: var(--gap-md);
    }
    h3 {
      font-family: var(--font-sans);
      font-size: 18px;
      font-weight: 600;
      margin-bottom: var(--gap-sm);
    }

    /* 数据表格：终端风 */
    table {
      width: 100%;
      border-collapse: collapse;
      font-family: var(--font-mono);
      font-size: 13px;
    }
    th {
      text-align: left;
      padding: var(--gap-sm);
      border-bottom: 1px solid var(--border-strong);
      font-weight: 500;
      color: var(--fg-dim);
      text-transform: uppercase;
      font-size: 10px;
      letter-spacing: 0.1em;
    }
    td {
      padding: var(--gap-sm);
      border-bottom: 1px solid var(--border);
    }
    tr:hover td { background: var(--bg-hover); }
    td.num { text-align: right; font-variant-numeric: tabular-nums; }

    /* 标签 / 状态 */
    .tag {
      display: inline-block;
      font-family: var(--font-mono);
      font-size: 10px;
      font-weight: 500;
      padding: 2px 6px;
      border: 1px solid var(--border-strong);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .tag.ok { color: var(--ok); border-color: var(--ok); }
    .tag.warn { color: var(--warn); border-color: var(--warn); }
    .tag.danger { color: var(--danger); border-color: var(--danger); }
    .tag.accent { color: var(--accent); border-color: var(--accent); }

    /* 关键数字 */
    .kpi {
      font-family: var(--font-mono);
      font-size: 36px;
      font-weight: 500;
      letter-spacing: -0.02em;
      font-variant-numeric: tabular-nums;
    }
    .kpi-label {
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--fg-dim);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }

    /* 网格 */
    .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: var(--gap-md); }
    .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--gap-md); }
    .grid-4 { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--gap-md); }

    /* 卡片：仅在有内部结构时使用 */
    .card {
      border: 1px solid var(--border);
      padding: var(--gap-md);
      background: var(--bg-elev);
    }
    .card:hover { border-color: var(--border-strong); }

    /* 横线分隔区块（首选） */
    .row {
      padding: var(--gap-md) 0;
      border-bottom: 1px solid var(--border);
      display: grid;
      grid-template-columns: 120px 1fr auto;
      gap: var(--gap-md);
      align-items: baseline;
    }
    .row .label {
      font-family: var(--font-mono);
      font-size: 11px;
      color: var(--fg-dim);
      text-transform: uppercase;
      letter-spacing: 0.1em;
    }

    /* 引言 / 摘要 */
    blockquote {
      font-family: var(--font-serif);
      font-size: 19px;
      font-style: italic;
      line-height: 1.5;
      color: var(--fg);
      padding: var(--gap-md) 0 var(--gap-md) var(--gap-md);
      border-left: 2px solid var(--accent);
      margin: var(--gap-lg) 0;
      max-width: var(--content-width);
    }

    /* 链接 */
    a { color: var(--accent); text-decoration: none; border-bottom: 1px solid var(--accent-dim); }
    a:hover { background: var(--accent); color: var(--bg); }

    /* 打印 */
    @media print {
      body { background: white; color: black; padding: 0; }
      :root { --bg: white; --fg: black; --border: #ddd; }
    }
  </style>
</head>
<body>
  <header class="report-header">
    <div class="meta">
      <span>REPORT // {{TYPE}}</span>
      <span>{{DATE}}</span>
      <span>{{AUTHOR}}</span>
      <span>REV {{VERSION}}</span>
    </div>
    <h1>{{TITLE}}</h1>
    <p class="subtitle">{{SUBTITLE}}</p>
  </header>
  <main>
    <!-- 模板特定内容 -->
  </main>
</body>
</html>
```

## 七种报告的差异化（仅内容结构差异，视觉一致）

| 报告类型 | 主体结构 | 决策落点 |
|---------|---------|---------|
| board-brief | KPI 仪表盘 + 风险矩阵 + 决议事项表 | 投票/批准 |
| ceo-canvas | 战略目标 + 资源分配 + 优先级矩阵 | 取舍 |
| tech-roadmap | 架构图（ASCII/SVG）+ 技术栈表 + 演进时间线 | 技术选型 |
| mrd-report | 市场规模 + 用户画像 + 竞品矩阵 + 需求清单 | 做不做 |
| project-board | 看板（todo/doing/done）+ 燃尽数据 + 里程碑 | 进度对齐 |
| dev-report | 提交统计 + 测试覆盖 + 缺陷分布 + 阻塞项 | 卡点解决 |
| retro-report | KPI 达成 + 时间线 + 经验教训 + 行动项 | 闭环 |

## 视觉禁令（违反即返工）

- ❌ 任何形式的渐变背景
- ❌ 玻璃拟态 / 模糊背景
- ❌ emoji 当图标用（仅可在引用原文里出现）
- ❌ 圆角超过 2px（终端没有圆角）
- ❌ box-shadow 任何柔光效果
- ❌ 紫色 / 粉色 / 多彩调色板
- ❌ 任何 keyframe 动画
- ❌ 装饰性插画 / 不携带信息的图标

## 视觉允许

- ✅ 1px 实线边框
- ✅ ASCII 字符绘制的图表（树形结构、流程箭头）
- ✅ 内联 SVG 数据图（柱状/折线/热力，但配色仅 `--accent` + `--fg-dim`）
- ✅ 单色 hover 反馈（背景从 `--bg` 到 `--bg-hover`）
