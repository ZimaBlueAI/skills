# viz-charts

报告内嵌图表 + 3D 知识图谱能力 skill。为姊妹 skill `biz-html-viz`（终端风）和 `viz-deck`（讲演风）提供视觉表达层。

## 能力一览

| 类型 | 数量 | 路径 |
|---|---|---|
| Mermaid 流程/关系图 | 11 | `templates/mermaid/` |
| ECharts 数据图表 | 25 | `templates/echarts/` |
| 自研轻量组件（KPI/Sparkline/Gauge/Progress/TagCloud） | 5 | `components/` |
| 3D 知识图谱 viewer | 3 | `templates/kg3d/` |
| KG builder（代码 + 文档） | 2 | `builders/` |

**两种渲染模式**：inline live（CDN，jsdelivr→unpkg fallback）+ offline SVG（Node.js）。
**两套主题**：`terminal`（biz-html-viz）+ `deck`（viz-deck）。

## 安装

```bash
# 1. 把整个 .claude 目录复制到你的项目根
cp -r .claude /path/to/your/project/

# 2. 离线渲染需要 Node 18+（仅 Mermaid + ECharts，3D KG 不走离线）
cd /path/to/your/project/.claude/skills/viz-charts/renderers/node
npm install --silent

# 3. Mermaid 离线渲染需要 chromium（仅首次）
npx playwright install chromium

# 4. 3D KG builder 不需任何依赖（纯 Node 标准库 + 内置正则）
```

## 快速开始

### 嵌入图表到现有 HTML 报告（inline 模式）

参见 `examples/inline-terminal.html`（22KB 完整 demo）— 含 5 自研组件、2 个 Mermaid、4 个 ECharts。直接 `<script>` 内联 CDN loader 渲染。

### 离线渲染图表为 SVG

```bash
cd renderers/node
node render-mermaid.mjs --input arch.mmd --output arch.svg --theme terminal
node render-echarts.mjs --input trend.json --output trend.svg --theme deck
node batch.mjs --input-dir ../charts --output-dir ../svgs --theme terminal
```

### 生成 3D 项目代码 KG

```bash
node builders/code-kg.mjs --repo /path/to/project --output project-kg.json --group-by dir

# 渲染：把 JSON 替换进模板的 {{KG_DATA_JSON}}
python3 -c "
import json
viewer = open('templates/kg3d/code-graph.html').read()
data = json.dumps(json.load(open('project-kg.json')), ensure_ascii=False, indent=2)
out = (viewer
  .replace('{{TITLE}}', 'My Project')
  .replace('{{SUBTITLE}}', 'Code structure')
  .replace('{{REPORT_TYPE}}', 'CODE KG')
  .replace('{{KG_DATA_JSON}}', data)
  .replace('{{THEME}}', 'terminal'))
open('project-kg.html', 'w').write(out)
"

# 浏览器打开 project-kg.html
```

### 生成 3D 文档概念 KG

```bash
node builders/doc-kg.mjs --input ./docs --output docs-kg.json --min-mentions 2

# 渲染同上，把 viewer 换成 doc-graph.html
```

## 文件结构

```
viz-charts/
├── SKILL.md                    skill 入口元数据
├── README.md                   这份
├── references/                 必读文档
│   ├── decision-tree.md        图表选型决策树（必读）
│   ├── chart-cookbook.md       数据契约速查
│   ├── integration-guide.md    集成进姊妹 skill
│   └── kg-builder-guide.md     3D KG 构建指南
├── themes/                     terminal.js / deck.js
├── components/                 5 自研轻量组件
├── templates/
│   ├── mermaid/                11 .mmd 模板
│   ├── echarts/                25 .json 模板
│   └── kg3d/                   3 viewer 模板
├── builders/                   code-kg.mjs / doc-kg.mjs
├── vendor/loaders/             CDN loader（双 fallback）
├── renderers/node/             离线 SVG 渲染
└── examples/                   4 个完整 demo
    ├── inline-terminal.html    终端风 22KB
    ├── inline-deck.html        讲演风 23KB
    ├── kg-doc-demo.html        viz-charts 自身文档 KG（92 节点 180 边）
    └── kg-code-demo.html       echarts/lib/chart 代码 KG（80 节点 82 边）
```

## 依赖矩阵

| 模式 | 需要 | 沙箱可跑？ |
|---|---|---|
| inline 模式 | 浏览器 + 联网（CDN） | ✓ 用户本地 |
| ECharts 离线 SVG | `echarts` npm 包 | ✓ 已实测 |
| Mermaid 离线 SVG | `mermaid-isomorphic` 或 `@mermaid-js/mermaid-cli` + chromium | 需 `npx playwright install chromium` |
| Mermaid 离线 placeholder | 仅 Node | ✓ 兜底自动启用 |
| 3D KG 渲染 | 浏览器 + WebGL + 联网（CDN） | ✓ 用户本地 |
| 3D KG builders | 仅 Node 18+（无外部依赖） | ✓ 已实测 |

## 与姊妹 skill 的关系

```
┌─────────────────┐  ┌──────────────┐
│  biz-html-viz   │  │  viz-deck    │       ← 报告生产 skill（不动）
│  (terminal)     │  │  (deck)      │
└────────┬────────┘  └───────┬──────┘
         │                   │
         │  调用图表能力       │
         ▼                   ▼
       ┌────────────────────────┐
       │     viz-charts          │           ← 图表 + KG 能力 skill
       │  (本 skill)             │
       └────────────────────────┘
```

姊妹 skill 渲染报告时遇到"这里需要一张图"，按以下步骤调用本 skill：

1. 读 `references/decision-tree.md` 选图表类型
2. 读 `references/chart-cookbook.md` 拿数据契约
3. 选定主题（biz-html-viz → terminal · viz-deck → deck）
4. 嵌入对应模板，主题保持一致

详见 `references/integration-guide.md`。

## 反模式速查

- ❌ 同一报告混用 terminal + deck 主题
- ❌ Mermaid 节点 > 30 还硬画 → 改 ECharts graph 或 3D KG
- ❌ 用 ECharts gauge 表达单个 KPI → 改用 kpi-card 组件
- ❌ 用 3D 图表（炫技）—— 仅在信息密度需要时用 3D KG
- ❌ 跳过 decision-tree.md 凭直觉选图

## 维护

模板内的所有视觉契约和 SKILL.md 同步。改主题色时**同步改三处**：
1. `themes/{terminal,deck}.js`
2. `vendor/loaders/cdn-loader.js`（如果含内联主题）
3. `components/*/`（每个组件的 CSS 变量）
4. `templates/kg3d/*.html`（CSS root 变量）
