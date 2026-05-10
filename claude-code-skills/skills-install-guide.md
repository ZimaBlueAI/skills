# Skill 套件 · 安装、配置、使用说明

**三个 Claude Code skill 的统一文档** · v1.0 · 2026-05-10

---

## 📋 目录

1. [三个 skill 是什么、谁负责什么](#01--三个-skill-是什么谁负责什么)
2. [前置要求](#02--前置要求)
3. [安装](#03--安装)
4. [配置](#04--配置)
5. [使用 biz-decision-stack](#05--使用-biz-decision-stack)
6. [使用 viz-deck](#06--使用-viz-deck)
7. [使用 viz-charts（图表 + 3D KG）](#07--使用-viz-charts图表--3d-kg)
8. [三 skill 协同工作流](#08--三-skill-协同工作流)
9. [疑难排查](#09--疑难排查)
10. [升级与维护](#10--升级与维护)

---

## 01 · 三个 skill 是什么、谁负责什么

### biz-decision-stack
商业决策角色思考链 + 终端风 HTML 报告生成器。**6 subagents + 1 skill**：

| 组件 | 角色 | 输出 |
|---|---|---|
| `00-all-hands-orchestrator` | 总调度 | 协调其他 6 个角色按顺序产出 |
| `01-board-advisor` | 董事会顾问 | 战略立场 + 备选方案 |
| `02-ceo-decision` | CEO | 决策画布 + 资源分配 |
| `03-chief-architect` | 首席架构师（合并 CTO/CAIO/CAO） | 技术路线图 |
| `04-product-manager` | PM（MRD + Delivery 双模） | 产品需求文档 + 交付路径 |
| `05-dev-test-lead` | 开发测试 lead（SD + TD） | 系统设计 + 测试设计 |
| `06-acceptance-retro` | 验收复盘 | 验收清单 + 复盘框架 |
| `biz-html-viz`（skill） | HTML 输出能力 | 7 终端风模板 |

**输出风格**：终端风 — 黑底 #0a0a0a + 酸黄 #d4ff00 + JetBrains Mono + 零动效。

**包大小**：57KB zip。

---

### viz-deck
讲演风深度报告 skill。**3 通用模板**：

| 模板 | 适合场景 |
|---|---|
| `stage-report.html` | 项目阶段汇报、季度成果展示 |
| `architecture-deep.html` | 技术架构深度讲解、客户技术方案 |
| `competitive-landscape.html` | 竞品分析、市场地图、投融对话 |

**输出风格**：讲演风 — 深空 #030711 + 青蓝金 + Inter + 微动效（含 reduced-motion 降级）。

**核心配套**：
- `references/design-system-deck.md` — 从 Octarus 真实样本提炼的视觉系统
- `references/research-playbook.md` — 竞品调研 Tier 1/2/3 自适应方法论

**包大小**：35KB zip。

---

### viz-charts
图表 + 3D 知识图谱能力 skill。**被前两个 skill 调用**。

| 类型 | 数量 | 路径 |
|---|---|---|
| Mermaid 流程/关系图 | 11 | `templates/mermaid/` |
| ECharts 数据图表 | 25 | `templates/echarts/` |
| 自研轻量组件 | 5 | `components/` |
| 3D 知识图谱 viewer | 3 | `templates/kg3d/` |
| KG builder | 2 | `builders/` |

**双模渲染**：inline live（CDN，jsdelivr→unpkg fallback）+ offline SVG（Node.js）。
**双主题**：terminal（biz-decision-stack 报告用）+ deck（viz-deck 报告用）。

**包大小**：150KB zip / 800KB 解压。

---

### 三者依赖关系

```
┌──────────────────────┐  ┌──────────────────┐
│  biz-decision-stack  │  │     viz-deck     │       ← 报告生产 skill
│  (终端风 · 决策套件)   │  │  (讲演风 · 演示)  │
└──────────┬───────────┘  └────────┬─────────┘
           │                       │
           │   need 图表/KG?       │
           ▼                       ▼
        ┌─────────────────────────────┐
        │        viz-charts            │           ← 能力 skill（被调用）
        │  (图表 + 3D KG · 双主题)     │
        └─────────────────────────────┘
```

**关键判断**：三个 skill **相互独立**，可只装其中任意一个或两个。但 biz-decision-stack 和 viz-deck 在嵌图表时会调用 viz-charts；只装报告 skill 不装 viz-charts，报告里需要图的地方会用纯文字或 ASCII 占位。

---

## 02 · 前置要求

| 组件 | 最低版本 | 用途 | 必装？ |
|---|---|---|---|
| Claude Code CLI | 最新版 | 跑 skill 的载体 | ✓ 必装 |
| Node.js | 18.0+ | viz-charts 离线渲染、3D KG builders | 仅 viz-charts 需要 |
| npm | 9.0+ | 装 echarts / mermaid 离线包 | 仅 viz-charts 离线模式 |
| Chromium | — | Mermaid 离线 SVG 渲染 | 仅 Mermaid 离线模式 |
| Python 3 | 3.8+ | 3D KG 数据填充辅助脚本（可选） | 用模板替换辅助脚本时 |
| 现代浏览器 | Chrome 90+ / Safari 14+ / Firefox 90+ | 预览报告、3D KG 交互 | 用户端 |

### 各模式依赖矩阵

| 使用模式 | 需要 | 不需要 |
|---|---|---|
| biz-decision-stack 生成报告 | Claude Code | Node.js 不需 |
| viz-deck 生成报告 | Claude Code | Node.js 不需 |
| viz-charts inline 模式 | 浏览器联网（CDN） | Node.js 不需 |
| viz-charts 离线 ECharts SVG | Node 18+ + `npm i echarts` | Chromium 不需 |
| viz-charts 离线 Mermaid SVG | Node + Chromium | — |
| viz-charts 离线 Mermaid 兜底 | 仅 Node | Chromium 不需（自动走 placeholder） |
| 3D KG builder 跑数据 | Node 18+（无外部依赖） | — |
| 3D KG 浏览器渲染 | WebGL + 联网（CDN） | — |

---

## 03 · 安装

### 步骤 1: 解压三个 zip 到项目根

每个 zip 内部都是 `.claude/` 结构，直接合并到你的项目根目录。

```bash
# 假设三个 zip 都在 ~/Downloads
cd /path/to/your/project

# biz-decision-stack 含 6 subagents + 1 skill
unzip -o ~/Downloads/biz-decision-stack.zip

# viz-deck（讲演风报告 skill）
unzip -o ~/Downloads/viz-deck.zip

# viz-charts（图表 + 3D KG 能力 skill）
unzip -o ~/Downloads/viz-charts.zip
```

解压后目录结构：

```
.claude/
├── agents/
│   ├── 00-all-hands-orchestrator.md
│   ├── 01-board-advisor.md
│   ├── 02-ceo-decision.md
│   ├── 03-chief-architect.md
│   ├── 04-product-manager.md
│   ├── 05-dev-test-lead.md
│   └── 06-acceptance-retro.md
└── skills/
    ├── biz-html-viz/      # biz-decision-stack 的 HTML 输出能力
    ├── viz-deck/           # 讲演风报告
    └── viz-charts/         # 图表 + 3D KG（被前两个调用）
```

### 步骤 2: 验证 skill 能被 Claude Code 看见

```bash
claude /skills
```

应该看到列表里有 `biz-html-viz`、`viz-deck`、`viz-charts`。subagent 用 `/agents` 命令查看（取决于 Claude Code 版本）。

### 步骤 3: （可选）装 viz-charts 离线渲染依赖

如果你需要把 Mermaid / ECharts 渲染成静态 SVG：

```bash
cd .claude/skills/viz-charts/renderers/node
npm install --silent

# Mermaid 离线渲染需要 chromium（仅首次）
npx playwright install chromium
```

> **说明**：跳过 chromium 安装，Mermaid 离线渲染会自动走 placeholder SVG（含错误提示），不会报错中断。ECharts 离线渲染不需要浏览器（用 SSR）。

### 步骤 4: （可选）跑通 demo 验证

双击打开任意一个 demo HTML：

- `demo-terminal.html` — 终端风全组件演示
- `demo-deck.html` — 讲演风全组件演示
- `demo-3d-doc-kg.html` — 3D 文档 KG（92 节点）
- `demo-3d-code-kg.html` — 3D 代码 KG（80 节点）

能看到图表渲染、3D KG 可拖动旋转点击高亮，则全部装好。

---

## 04 · 配置

### 无需配置即可用

三个 skill 都是**开箱即用**，不需要环境变量、API key、数据库。

### 可选：CDN self-host

viz-charts 默认从 jsdelivr → unpkg 加载库。断外网环境可 self-host：

```bash
# 1. 下载库到本地
mkdir -p .claude/skills/viz-charts/vendor/cdn-mirror
cd .claude/skills/viz-charts/vendor/cdn-mirror

wget https://cdn.jsdelivr.net/npm/echarts@5.5.1/dist/echarts.min.js
wget https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs
wget https://cdn.jsdelivr.net/npm/3d-force-graph@1.74.0/dist/3d-force-graph.min.js

# 2. 在生成的报告 HTML 里设全局变量指向本地
# 在 cdn-loader 加载之前加：
# <script>window.VIZ_CHARTS_SELFHOST_BASE = './vendor/cdn-mirror';</script>
```

cdn-loader 会优先尝试 self-host 路径，失败再走 jsdelivr/unpkg。

### 可选：默认主题

每个 skill 有自己的固定主题（biz-html-viz → terminal · viz-deck → deck），不需要改。**不建议**强制让 deck 报告用 terminal 主题——主题与排版语言是配套的。

---

## 05 · 使用 biz-decision-stack

### 触发方式

1. **显式调用 orchestrator**：让 Claude 跑 `00-all-hands-orchestrator` subagent
2. **单点调用某角色**：例如"用 ceo-decision 视角分析这个问题"
3. **关键词触发**：说"做一份董事会简报 / CEO 决策画布 / 技术路线图 / MRD / 项目看板 / 验收复盘"

### 典型用法 — 完整决策流

```
我要决策是否上线 Mingjing 的修仙境界系统。请用 all-hands 流程
完整跑一遍：Board → CEO → Architect → PM → Dev-Test → Acceptance。
每个角色独立写一份 HTML 报告。
```

Claude 会按顺序：
1. Board Advisor 写战略立场（董事会简报，3 个备选 + 推荐 + 风险）
2. CEO Decision 写决策画布
3. Chief Architect 写技术路线图
4. Product Manager 写 MRD + 交付路径
5. Dev-Test Lead 写 SD + TD
6. Acceptance-Retro 写验收清单 + 复盘框架

每份是独立 HTML，文件名形如 `report-board-brief-20260510.html`。

### 典型用法 — 单角色快速产出

```
用 board-advisor 视角，给我写一份关于"是否引入第二个云厂商"的董事会简报。
```

只产一份 HTML，比完整流程快 6 倍。

### 7 个 HTML 模板速查

| 模板 | 用于 | 关键章节 |
|---|---|---|
| `board-brief.html` | 董事会简报 | 立场 + 3 备选 + 推荐 + 风险表 |
| `ceo-canvas.html` | CEO 决策画布 | 问题 + 假设 + 决策 + 资源 + KPI |
| `tech-roadmap.html` | 技术路线图 | 3 季度路线 + 架构演进 + 风险 |
| `mrd-report.html` | MRD（市场需求文档） | 痛点 + 用户画像 + 功能清单 + 验收 |
| `project-board.html` | 项目看板 | 里程碑 + 任务 + 状态 + 阻塞 |
| `dev-report.html` | 开发/测试报告 | SD + TD + 覆盖率 + 风险评级 |
| `retro-report.html` | 验收复盘 | 事实 + 教训 + 行动项 + 制度沉淀 |

样本预览：`sample-board-brief.html`（用 Mingjing 项目真实数据）。

---

## 06 · 使用 viz-deck

### 触发方式

1. 关键词："做一份 deck / 讲演 / 演示 / 阶段汇报 / 架构深度报告 / 竞品景观分析"
2. 显式指定模板：`用 viz-deck 的 stage-report 模板写 ...`

### 3 个模板

| 模板 | 适合场景 | 关键能力 |
|---|---|---|
| `stage-report.html` | 项目阶段汇报、季度成果 | 章节四件套 + KPI 网格 + 时间线 + 风险象限 |
| `architecture-deep.html` | 技术架构讲解、客户方案 | 架构图 + 模块卡片 + 数据流 + ADR + 性能指标 |
| `competitive-landscape.html` | 竞品分析、市场地图 | 2x2 象限 + 雷达 + 能力对比 + Tier 1/2/3 调研指引 |

### 典型用法

```
# 阶段汇报
用 viz-deck 的 stage-report 模板，给 Mingjing 项目写一份 v0.3
里程碑汇报。包含三个核心 KPI（用户数、留存、核心功能完成度）、
关键决策时间线、下季度风险。

# 架构深度
用 architecture-deep 模板写 OpenClaw 的 Memory Spine 架构详解，
包含模块图、数据流、3 个 ADR、性能基线。

# 竞品景观
用 competitive-landscape 模板分析 AI 编程助手赛道。先按 research-playbook
跑 Tier 1 调研（公开渠道穷尽），再生成报告。
```

### research-playbook 是什么

`references/research-playbook.md` 是竞品调研的**方法论指引**：

- **Tier 1**：用户没给名单 → AI 从赛道全景挖掘 + 公开渠道扫描
- **Tier 2**：用户给了名单 → 按名单深挖每家
- **Tier 3**：用户给了 git URL → 直接读代码 + 文档分析

Claude 自动判断 Tier 并按方法论执行。

### design-system-deck.md 是什么

从 Octarus 真实样本提炼的设计系统：CSS 变量、版面网格、字号阶、动效曲线、章节结构。是讲演风的**权威定义**。

---

## 07 · 使用 viz-charts（图表 + 3D KG）

### 四类视觉表达

| 类型 | 数量 | 用什么 | 何时用 |
|---|---|---|---|
| Mermaid 流程/关系图 | 11 | `templates/mermaid/*.mmd` | 架构图、时序、状态机、Gantt、Mindmap… |
| ECharts 数据图表 | 25 | `templates/echarts/*.json` | 折线、柱、饼、雷达、热力、桑基、漏斗… |
| 自研轻量组件 | 5 | `components/*` | KPI 大数字、sparkline、gauge、progress、tag-cloud |
| 3D 知识图谱 | 3 viewer | `templates/kg3d/*.html` | 代码结构、文档概念、通用关系网络 |

### 三步选图

1. 读 `references/decision-tree.md` 选类型（数据形态 → 图表类型）
2. 读 `references/chart-cookbook.md` 拿数据契约（每种图的 JSON 怎么填）
3. 选主题（biz-decision-stack 报告 → terminal · viz-deck 报告 → deck）

### 用法 1: 让 Claude 直接嵌入图表

```
报告里有 Q1-Q4 的营收数据，用 ECharts line-trend 模板嵌一张趋势图，
深空主题。同时旁边放 3 个 KPI 大数字（YTD 总营收、MoM 增速、毛利率）。
```

Claude 会读 chart-cookbook 找模板，按数据契约填 `data-echarts-option`，并在报告 head 内联 cdn-loader。

### 用法 2: 离线渲染图表为 SVG

```bash
cd .claude/skills/viz-charts/renderers/node

# 单图
node render-mermaid.mjs --input arch.mmd --output arch.svg --theme terminal
node render-echarts.mjs --input trend.json --output trend.svg --theme deck

# 批量（按扩展名自动分发）
node batch.mjs \
  --input-dir ../../../report-charts \
  --output-dir ../../../report-svgs \
  --theme terminal
```

### 用法 3: 生成 3D 代码知识图谱

```bash
# 1. 跑 builder 抽数据
node .claude/skills/viz-charts/builders/code-kg.mjs \
  --repo /path/to/your/project \
  --output project-kg.json \
  --group-by dir              # 或 language / depth

# 2. 把数据填进 viewer 模板
python3 -c "
import json
viewer = open('.claude/skills/viz-charts/templates/kg3d/code-graph.html').read()
data   = json.dumps(json.load(open('project-kg.json')), ensure_ascii=False, indent=2)
out = (viewer
  .replace('{{TITLE}}', 'My Project')
  .replace('{{SUBTITLE}}', 'Code structure KG')
  .replace('{{REPORT_TYPE}}', 'CODE KG')
  .replace('{{KG_DATA_JSON}}', data)
  .replace('{{THEME}}', 'terminal'))
open('project-kg.html', 'w').write(out)
print('done: project-kg.html')
"

# 3. 浏览器打开 project-kg.html
```

### 用法 4: 生成 3D 文档知识图谱

```bash
node .claude/skills/viz-charts/builders/doc-kg.mjs \
  --input ./docs \
  --output docs-kg.json \
  --min-mentions 2

# 渲染同上，把 viewer 换成 doc-graph.html
```

### 3D KG 交互

- 鼠标拖动 — 旋转视角
- 滚轮 — 缩放
- 点击节点 — 高亮邻居 + 详情面板（左下）
- 右上角搜索框 — 按 name/id 搜节点
- 右上 legend — 点分组隐藏/显示
- FIT / PAUSE / RESET — 视图控制

### 主题选择

| 报告类型 | 用主题 | 调用方 |
|---|---|---|
| biz-decision-stack 决策报告 | `terminal` | biz-html-viz |
| viz-deck 讲演报告 | `deck` | viz-deck |
| 独立的 KG/图表（不嵌报告） | 看场景 | — |

> **纪律**：同一份报告内**所有图表用同一主题**。terminal 报告里出现 deck 配色的图，看起来错位且不专业。

---

## 08 · 三 skill 协同工作流

### 场景：完整的项目阶段评审

以 Mingjing 项目 v0.3 为例：

#### 步骤 1: 用 biz-decision-stack 跑决策流

```
用 all-hands 流程评审 Mingjing v0.3 是否进入 GA 准备期。
6 个角色各产一份终端风 HTML。
```

产出：6 份 board / ceo / arch / pm / dev / retro 报告。

#### 步骤 2: 用 viz-deck 做对外汇报版

```
把上一步的决策内容压缩成一份 stage-report 讲演风 deck，
适合发给投资人和合作伙伴看。
```

产出：1 份 deck.html，深空玻璃拟态。

#### 步骤 3: 用 viz-charts 做项目结构展示

```
跑 code-kg builder 抽 Mingjing 代码结构，生成 deck 主题的 3D 代码 KG。
作为 deck 报告里"附录·项目结构"章节的链接。
```

产出：1 份 mingjing-code-kg.html。

#### 步骤 4: 统一发布

```
mingjing-v03-review/
├── 01-board-brief.html        # 内部用 · 终端风
├── 02-ceo-canvas.html         # 内部用 · 终端风
├── 03-tech-roadmap.html       # 内部用 · 终端风
├── 04-mrd.html                # 内部用 · 终端风
├── 05-dev-report.html         # 内部用 · 终端风
├── 06-retro.html              # 内部用 · 终端风
├── public-deck.html           # 对外用 · 讲演风
└── code-kg.html               # 项目代码 3D KG · 讲演风
```

### 常见组合

| 需求 | 用哪些 skill | 产出 |
|---|---|---|
| 内部决策评审 | biz-decision-stack | 6 份角色报告（终端风） |
| 对外阶段汇报 | viz-deck | 1 份 deck（讲演风） |
| 客户技术方案 | viz-deck + viz-charts | 架构深度 deck + 嵌入图表/KG |
| 项目代码全景 | viz-charts | 3D 代码 KG |
| 项目知识体系 | viz-charts | 3D 文档 KG |
| 投资人路演 | viz-deck（competitive-landscape）+ viz-charts | 竞品景观 + 数据图表 |

---

## 09 · 疑难排查

### Claude 看不到 skill

- 检查 `.claude/skills/` 目录是否在**项目根**（不是子目录）
- 每个 skill 必须有 `SKILL.md` 含 frontmatter（`name:` + `description:`）
- Claude Code 是否在最新版本（`claude --version`）

### 报告里的 Mermaid / ECharts 不渲染

- 用浏览器开发者工具看 Console，看是否有 CDN 加载失败
- 右下角状态条会显示 `jsdelivr / unpkg` 哪个 CDN 在用
- 如果两个 CDN 都失败 → 设置 `VIZ_CHARTS_SELFHOST_BASE` 走本地
- 检查 `data-echarts-option` 属性是否是合法 JSON

### 3D KG 加载后空白

- 检查浏览器是否支持 WebGL（`chrome://gpu`）
- 检查 KG 数据 JSON 是否合法（`{{KG_DATA_JSON}}` 替换是否完整）
- 如果节点数 > 5000，会卡 — 拆图或换专业工具（Gephi）
- 状态条显示 `CDN load failed` → 网络问题

### 离线 Mermaid 渲染失败

- 第一次必须 `npx playwright install chromium`
- 沙箱/容器环境下载浏览器可能失败 — 走 placeholder SVG 兜底
- 看终端的 `[render-mermaid]` 输出诊断哪一档失败

### code-kg builder 跑出来 0 边

- builder 只解析**仓库内的相对 import**。如果项目用 monorepo workspace 或 path alias（如 `@/utils`），可能识别不到
- 试着 `--group-by language` 看节点是否齐全（边的问题不影响节点）
- 需要 99% 精确请等后续 tree-sitter 版本，或自己写 builder（统一数据契约）

### doc-kg 抽出来概念太杂

- 调高 `--min-mentions`（默认 2，可设 3-5 过滤低频）
- 调低 `--top-terms`（默认 40，可设 20）
- 在 markdown 里多用 `**显式加粗**` 和 `` `code-term` ``，builder 优先抽这些

### 报告字体看起来不对

- 检查网络是否能访问 Google Fonts（`fonts.googleapis.com`）
- 断网环境会自动走系统兜底链：JetBrains Mono → SF Mono → Menlo → Consolas → monospace（终端风）；Inter → ui-sans-serif → system-ui → PingFang SC（讲演风）

---

## 10 · 升级与维护

### 三 skill 各自独立升级

三个 zip 各自独立。如果只升级 viz-charts：

```bash
cd /path/to/your/project
rm -rf .claude/skills/viz-charts
unzip -o ~/Downloads/viz-charts-v1.1.zip
```

不影响 biz-decision-stack 和 viz-deck。

### 主题色调整

改主题色需**同步改三处**，否则会出现局部错位：

1. `themes/{terminal,deck}.js` — 主题对象（被 cdn-loader 读）
2. `vendor/loaders/cdn-loader.js` — 内联主题副本
3. `components/*/` — 每个组件的 CSS 变量
4. `templates/kg3d/*.html` — 3D KG viewer 的 root CSS 变量

### 添加新图表模板

1. 在 `templates/echarts/`（或 mermaid）新建 `.json/.mmd`
2. 必填 `_meta` 字段：`{name, use_when, data_shape}`
3. 更新 `references/decision-tree.md` 加进选型表
4. 更新 `references/chart-cookbook.md` 加进契约速查

### 添加新 builder（如 PDF KG / API KG）

1. 在 `builders/` 新建 `.mjs`
2. 输出符合 `references/kg-builder-guide.md` 的统一数据契约
3. 不需要新 viewer — 直接喂 `data-graph.html`

### 版本兼容

- CDN 版本固定（mermaid@10.9.1, echarts@5.5.1, 3d-force-graph@1.74.0）
- 升级时改 `vendor/loaders/cdn-loader.js` 的 `VERSIONS` 常量
- 升级前把 `examples/` 的 4 个 demo 跑一遍验证

---

**Skill Suite v1.0** · 2026-05-10 · biz-decision-stack + viz-deck + viz-charts
