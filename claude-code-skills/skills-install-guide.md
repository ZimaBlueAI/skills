# Skill 套件 · 安装、配置、使用说明

**三个 Claude Code skill 的统一文档** · v3.0 · 2026-05-13

> **v3.0** 起新增第二个软桥接 [`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master) 获得真正可编辑的 native DrawingML PPTX：viz-deck 增加第 5 模 `pptx-deck`、biz-decision-stack 增加终端风决策 PPTX 出口、viz-charts 增加数据绑定原生 chart。详见 [第 13 节 · ppt-master 桥接](#13--ppt-master-桥接v3-真正可编辑-pptx)。
>
> v2.0 起：viz-deck 从 1 模产出扩展到 **4 模产出**（keynote-report / hi-fi prototype / slide-deck / motion-stage），引入 **20 设计哲学** 与 **5 维专家评审**，并通过软依赖桥接 [`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design) 获得 HTML→MP4/PPTX 导出能力。详见 [第 11 节 · v2 新能力速查](#11--v2-新能力速查) 与 [第 12 节 · huashu-design 桥接](#12--huashu-design-桥接)。

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
11. [v2 新能力速查](#11--v2-新能力速查)
12. [huashu-design 桥接](#12--huashu-design-桥接)

---

## 01 · 三个 skill 是什么、谁负责什么

### biz-decision-stack
商业决策角色思考链 + 终端风 HTML 报告生成器。**v2 起：7 subagents + 1 skill**：

| 组件 | 角色 | 输出 |
|---|---|---|
| `00-all-hands-orchestrator` | 总调度 | 协调其他 6 个角色按顺序产出 + 末尾可选触发 design-critic |
| `01-board-advisor` | 董事会顾问 | 战略立场 + 备选方案 |
| `02-ceo-decision` | CEO | 决策画布 + 资源分配 |
| `03-chief-architect` | 首席架构师（合并 CTO/CAIO/CAO） | 技术路线图 |
| `04-product-manager` | PM（MRD + Delivery 双模） | 产品需求文档 + 交付路径 |
| `05-dev-test-lead` | 开发测试 lead（SD + TD） | 系统设计 + 测试设计 |
| `06-acceptance-retro` | 验收复盘 | 验收清单 + 复盘框架 |
| `07-design-critic` 🆕 v2 | 设计评审官 | 5 维评分 + Keep/Fix/Quick-Wins |
| `biz-html-viz`（skill） | HTML 输出能力 | **8 终端风模板**（含 v2 新增 `design-critique.html`） |

**输出风格**：终端风 — 黑底 #0a0a0a + 酸黄 #d4ff00 + JetBrains Mono + 零动效。**v3 起**：可选 ppt-master 桥接出口 8 个决策 layout 的可编辑 PPTX（同样的视觉哲学）。

**包大小**：73KB zip（v0.3，含决策 PPTX 出口）。

---

### viz-deck
讲演风深度报告 skill。**v3 起：5 模产出**：

| 模式 | 模板 | 适合场景 | 产出形态 |
|---|---|---|---|
| **1 · keynote-report** | `stage-report.html` | 项目阶段汇报、季度成果展示 | HTML |
| | `architecture-deep.html` | 技术架构深度讲解、客户技术方案 | HTML |
| | `competitive-landscape.html` | 竞品分析、市场地图、投融对话 | HTML（含 web_search 实时调研） |
| **2 · prototype** 🆕 v2 | `prototype-shell.html` | iOS / Android / macOS / 浏览器高保真原型 | HTML + AppPhone 状态管理 |
| **3 · slide-deck** 🆕 v2 | `slide-deck.html` | 演讲幻灯片、TED 风、客户路演 | HTML + 快速 PPTX + 横版 PDF |
| **4 · motion-stage** 🆕 v2 | `motion-stage.html` | hero video、概念视频、解说视频 | HTML + MP4（25/60 fps）+ GIF + BGM |
| **5 · pptx-deck** 🆕 v3 | `pptx-deck-spec.example.json` | 给 stakeholder 在 PowerPoint 里改的 deck、母版继承、TTS 旁白 | **真正可编辑 PPTX**（native DrawingML，每元素可点）+ MP4 |

**输出风格**：讲演风 — 深空 #030711 + 青蓝金 + Inter + 微动效（含 reduced-motion 降级）。

**核心配套**：
- `references/design-system-deck.md` — 从 Octarus 真实样本提炼的视觉系统
- `references/research-playbook.md` — 竞品调研 Tier 1/2/3 自适应方法论
- `references/huashu-bridge.md` 🆕 v2 — 与 huashu-design 的桥接协议
- `references/design-philosophies.md` 🆕 v2 — 20 设计哲学到 4 模产出的适配
- `references/critique-5dim.md` 🆕 v2 — 5 维专家评审协议
- `references/prototype-mode.md` 🆕 v2 — 高保真原型工作流
- `references/slide-mode.md` 🆕 v2 — 幻灯片 + PPTX 导出工作流
- `references/motion-mode.md` 🆕 v2 — 动画 + MP4 导出工作流
- `references/pptx-master-bridge.md` 🆕 v3 — 与 ppt-master 桥接（v3 真编辑 PPTX）
- `references/editable-pptx.md` 🆕 v3 — PPTX 里哪些可编辑、哪些不可
- `references/master-templates.md` 🆕 v3 — 母版/模板继承（导入公司模板）
- `references/narration-pptx.md` 🆕 v3 — TTS 旁白嵌入 + PowerPoint 自动导出 MP4

**包大小**：81KB zip（v0.3，含 pptx-deck 模式）。

---

### viz-charts
图表 + 3D 知识图谱 + 动效视频 + 原生 PPTX 图表能力 skill。**被前两个 skill 调用**。**v3 起：6 类视觉**：

| 类型 | 数量 | 路径 |
|---|---|---|
| Mermaid 流程/关系图 | 11 | `templates/mermaid/` |
| ECharts 数据图表 | 25 | `templates/echarts/` |
| 自研轻量组件 | 5 | `components/` |
| 3D 知识图谱 viewer | 3 | `templates/kg3d/` |
| KG builder | 2 | `builders/` |
| **Motion stage** 🆕 v2 | 1 模板 | `templates/motion/motion-stage-template.html` |
| **Native PPTX chart** 🆕 v3 | 8 chart 类型 | `scripts/echarts_to_pptx.py` |

**双模渲染**：inline live（CDN，jsdelivr→unpkg fallback）+ offline SVG（Node.js）+ motion 录屏（v2 桥接 huashu）+ **原生 PPTX chart**（v3 桥接 ppt-master）。
**三主题**：terminal（biz-decision-stack 报告用）+ deck（viz-deck 报告用）+ deck-light（v3 公司模板友好）。

**v2 新增 references**：
- `references/motion-charts.md` — motion 图表三类模式（frame-step / temporal sweep / graph orbit）
- `references/mp4-export.md` — MP4 / 60fps / GIF 导出工具链桥接

**v3 新增 references**：
- `references/pptx-charts.md` — ECharts→python-pptx 数据绑定 chart 导出协议

**包大小**：156KB zip（v0.3，含 pptx-charts 出口）。

---

### zima-html-ppt 🆕

ZimaBlueAI **现场讲演 deck** skill —— 暖纸编辑风（ZimaBlue Editorial）单文件 HTML 幻灯片 +
招牌**演讲者模式**。提炼自实战母版 `D1-破局与进化` / `D2-三场战役` / `D3-训练方案`。

| 组件 | 内容 |
|---|---|
| `SKILL.md` | 何时用/不用（与终端风 biz-html-viz、深空风 viz-deck 划清边界）、工作流、反模式 |
| `references/design-system.md` | ZimaBlue Editorial 规范：令牌、字体层级、6 个签名元素、组件、Chart.js 调性、自检 |
| `references/speaker-mode.md` | 演讲者模式：`.notes` 逐字稿 + 5 标签语义（cue/say/do/data/bridge）+ `data-min` 计时 + 提词器窗口 |
| `templates/zima-ppt-starter.html` | 全引擎单文件骨架，复制即用（S 键提词器、F 全屏、键盘翻页、配额计时、数字滚动、品牌签名） |

**输出风格**：暖纸 #f7f4ee + 深青 #1b5e5a + 金/赭点缀 + 发丝卡片 + 顶部 teal→gold→red 三色条。
**现场操作标识**：右上角常驻 `按 F 全屏 · 按 S 演讲者模式 · ← → 翻页 · 空格 下一页`。
**包大小**：约 23 KB（纯文件夹，无需 zip；安装 = 直接放进 `.claude/skills/`）。**零运行时依赖**（仅 Chart.js 走 CDN）。

> 安装：把 `zima-html-ppt/` 整个文件夹放进 `~/.claude/skills/`（全局）或项目根 `.claude/skills/`（项目级）即可，
> `claude /skills` 列表里应能看到 `zima-html-ppt`。

---

### web-shader-extractor 🆕（移植 · 非 ZimaBlue 套件）

网页 **WebGL / WebGPU / Canvas 着色器动效抠取与本地复现** skill —— **原样移植**自
[`lixiaolin94/skills`](https://github.com/lixiaolin94/skills)（MIT）。与上面 4 个「生成型」
skill 互补：它是**逆向侦察型**——从真实 URL 抠 shader 证据 → 证据匹配复现 → 工程化。

| 组件 | 内容 |
|---|---|
| `SKILL.md` | 路由索引 + Recon Kernel 状态机 + 六条铁律（目标绑定/证据优先/基线优先/诚实标签…） |
| `references/`（13 篇） | 按状态加载：operating-contract / recon-kernel / capture-backends / replay-policy / three-shader-reconstruction … |
| `scripts/`（2 个） | `fetch-rendered-dom.mjs`（Playwright 清单助手）+ `scan-bundle.sh`（bundle 切片扫描） |
| `templates/`（6 个） | schema 而非自由笔记：`replay-manifest.json`（v3）/ `extraction-report.md` / `scout-card.json` … |
| demo（本仓库追加） | 3 个自包含样例复现：`demo-webgl-fragment.html` / `demo-canvas2d-flow.html` / `demo-three-reconstruct.html` |

**何时用**：给定 URL + shader/canvas 目标想抠取复现。**何时不用**：DOM/CSS 克隆、或「只想要好看动效」（那是生成需求，走 huashu-design / viz-deck motion）。
**包大小**：纯文件夹，零必需依赖（高阶帧捕获可选 Playwright）。详见 `web-shader-extractor/web-shader-extractor-README.md` 与 `NOTICE.md`。

---

### gzh-design 🆕（移植 · 非 ZimaBlue 套件）

**微信公众号文章排版** skill —— **原样移植**自
[`isjiamu/gzh-design-skill`](https://github.com/isjiamu/gzh-design-skill)（AGPL-3.0，甲木 × 摸鱼小李联名共建）。
与「生成型」skill 互补：它是**渠道排版型**——Markdown / docx / PDF / 纯文本 →
粘贴进公众号编辑器不掉格式的 HTML（样式全内联 + `<span leaf="">` 包裹）。

| 组件 | 内容 |
|---|---|
| `SKILL.md` | 流程与决策：输入归一化 → 选主题 → 组件装配 → 校验清零 → 输出正文 + 预览页 |
| `references/`（11 篇） | 主题索引 + 6 套主题组件库（摸鱼绿/红白/石墨极简/留白禅意/摸鱼票据/橄榄手记）+ 通用增量库 + **主题生成器** + 格式归一化 + 回归用例 |
| `scripts/`（4 个） | `component_lint.py` + `validate_gzh_html.py`（双关卡校验）· `extract_docx.py`（Word 提取）· `wrap_preview.py`（一键复制预览页） |
| `assets/`（3 个） | 预览模板 + 样例文章 + 主题预览示例 |

**何时用**：「公众号排版 / 微信排版 / 一键排版」、把文章转公众号 HTML、按描述或参考图生成新主题。**何时不用**：普通网页 / 落地页 / PPT（走 huashu-design / viz-deck / biz-html-viz）。
**包大小**：纯文件夹，零必需依赖（脚本仅 Python 标准库；Windows 下建议 `PYTHONIOENCODING=utf-8`）。详见 `gzh-design/gzh-design-README.md` 与 `NOTICE.md`。

---

### zima-design 🆕（自有 · 设计合奏引擎）

**设计合奏引擎** —— 原创路由协议编排三个内置引擎 + 三个外部体系，
目标是每次交付都涌现不同的、贴近人类审美的设计方案，而不是单一风格或 AI 模板味。
三引擎逐字节收编自 MIT 开源项目（溯源见 `zima-design/NOTICE.md`）。

| 组件 | 内容 |
|---|---|
| `SKILL.md`（原创） | 三条铁律（多样性优先 / 诚实 / 验收前置）+ 任务路由表 + **五轴多样性协议**（宏结构 × 主题 × 动效人格 × 卡片物理 × 密度节奏，设计签名盖章台账）+ 四级验收栈 |
| `engines/anti-slop/`（源自 nutlope/hallmark） | Design flow + 四动词（建站 / audit / redesign / study）· `slop-test.md`（57 关卡）· 21 种宏结构 · 20 主题 + OKLCH custom · 组件 cookbook |
| `engines/motion/`（源自 emilkowalski/skills） | 动画决策框架（频率门 → 目的 → 缓动 → 时长）· 弹簧物理 / 手势 · 性能铁律 · Apple 设计十七则 · 动效评审十条 · 动效词汇表 |
| `engines/database/`（源自 ui-ux-pro-max） | 84 风格 / 192 配色 / 74 字体搭配 / 98 UX 准则 / 22 技术栈 CSV 数据库 + Python 检索（零第三方依赖） |
| `demos/` | 反面教材（12 处 slop 标本）→ audit 报告（24 项抽查 17 FAIL）→ Hum 主题重设计对照 |
| 外部联动 | impeccable（工程动词）· huashu-design（3 方向 + 5 维评审）· taste-engine（口味档位），装了即征用，不装不阻塞 |

**何时用**：落地页 / 官网 / 产品 UI 的从零设计、「别做成 AI 味」、反 AI 味审计与重设计、多方向探索、动效专项、风格/配色/字体选型。
**何时不用**：终端风决策报告（biz-html-viz）、讲演 deck（viz-deck / zima-html-ppt）、公众号排版（gzh-design）——
这些 skill 已内联六大纪律硬闸，装了 zima-design 会自动桥接全量 57 关卡。
**包大小**：纯文件夹（约 9 MB，含 database CSV）；database 检索需 Python 3（零第三方依赖）。详见 `zima-design/zima-design-README.md` 与 `NOTICE.md`。

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
| Node.js | 18.0+ | viz-charts 离线渲染、3D KG builders、v2 evaluator/exporters、v3 PPTX bridge driver | 仅 viz-charts / v2 / v3 模式需要 |
| npm | 9.0+ | 装 echarts / mermaid 离线包、huashu 运行时 | 仅 viz-charts 离线模式 / v2 模式 |
| Chromium | — | Mermaid 离线 SVG 渲染、MP4 录制、PPTX 导出 | 仅 Mermaid 离线模式 / v2 模式（通过 playwright 自动装） |
| **ffmpeg** 🆕 v2 | 4.0+ | MP4 编码 / 60fps 插帧 / GIF palette / BGM 混音 | 仅 v2 viz-deck motion-stage 模式 |
| **huashu-design** 🆕 v2 | latest | 4 模产出（prototype/slide/motion）的工具链承载 | 仅 viz-deck v2 模式 + viz-charts motion |
| **ppt-master** 🆕 v3 | latest | 真正可编辑 PPTX / TTS 旁白 / 母版 / 数据绑定 chart | 仅 viz-deck 模式 5 / biz-decision 决策 PPTX / viz-charts 原生 chart |
| **Python 3** 🆕 v3 用途扩展 | 3.10+ | v3 ppt-master 运行时 + 可选 3D KG 数据填充 | v3 模式必需 |
| 现代浏览器 | Chrome 90+ / Safari 14+ / Firefox 90+ | 预览报告、3D KG 交互、最终 PPTX 打开 | 用户端 |

### 各模式依赖矩阵

| 使用模式 | 需要 | 不需要 |
|---|---|---|
| biz-decision-stack 生成报告 | Claude Code | Node.js 不需 |
| biz-decision-stack 5 维评审（终端风）🆕 v2 | 仅 Claude Code | huashu 不需（评分标准已内嵌） |
| viz-deck 生成报告（v1 模式 = keynote-report） | Claude Code | Node.js 不需 |
| viz-deck 5 维评审（讲演风）🆕 v2 | Node 18+ | huashu 不需 |
| **viz-deck prototype 模式** 🆕 v2 | Claude Code + 浏览器联网（React/Babel CDN） | huashu 非必须（Playwright 验证脚本来自 huashu） |
| **viz-deck slide-deck 模式** 🆕 v2 | Claude Code（HTML） | PPTX 导出额外需要 huashu + Node + sharp |
| **viz-deck motion-stage 模式** 🆕 v2 | **huashu-design + Node 18+ + Chromium + ffmpeg** | — |
| viz-deck slide-deck 导出 PPTX 🆕 v2 | huashu + Node + sharp + pptxgenjs | — |
| viz-deck slide-deck 导出 PDF 🆕 v2 | huashu + Node + Chromium + pdf-lib | — |
| viz-charts inline 模式 | 浏览器联网（CDN） | Node.js 不需 |
| viz-charts 离线 ECharts SVG | Node 18+ + `npm i echarts` | Chromium 不需 |
| viz-charts 离线 Mermaid SVG | Node + Chromium | — |
| viz-charts 离线 Mermaid 兜底 | 仅 Node | Chromium 不需（自动走 placeholder） |
| **viz-charts motion 模式** 🆕 v2 | **huashu-design + Node 18+ + Chromium + ffmpeg** | — |
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

---

## 11 · v2 新能力速查

> v2 在 v1 基础上叠加，**不破坏向后兼容**。原有 keynote-report / 决策链 / 静态图表全部继续可用。

### 11.1 viz-deck 4 模产出

| 模式 | 触发词 | 模板 | 关键依赖 |
|---|---|---|---|
| **1 · keynote-report**（v1 原模式） | "讲演 / 阶段汇报 / 架构深研 / 竞品" | `stage-report.html` 等三个 | Claude Code |
| **2 · prototype**（v2 新增） | "做原型 / iOS 原型 / hi-fi / 可点击 demo" | `prototype-shell.html` | huashu 设备外壳（非必须）+ Playwright（验证） |
| **3 · slide-deck**（v2 新增） | "做幻灯片 / 做 PPT / 导出 PPTX" | `slide-deck.html` | huashu + Node + sharp + pptxgenjs |
| **4 · motion-stage**（v2 新增） | "导出 MP4 / 60fps / hero video / 解说视频" | `motion-stage.html` | huashu + Node + Chromium + ffmpeg |

### 11.2 20 设计哲学 × viz-deck 适配

通过 `references/design-philosophies.md` 把 huashu-design 的 5 流派 × 20 哲学映射到 viz-deck 的 4 模产出：

- 信息建筑派（Pentagram / Stamen / Information Architects / Fathom）
- 运动诗学派（Locomotive / Active Theory / Field.io / Resn）
- 极简主义派（Experimental Jetset / Müller-Brockmann / Build / Sagmeister & Walsh）
- 实验先锋派（Zach Lieberman / Raven Kwok / Ash Thorp / Territory Studio）
- 东方哲学派（Takram / Kenya Hara / Irma Boom / Neo Shen）

**用法**：

```
> 用 18 Kenya Hara 风格做一份 Mingjing 阶段报告
> 用 04 Fathom 风格做一份数据 deck
> 不知道选哪个，给我推荐 3 个差异化方向
```

最后一句会触发**设计方向顾问模式**——并行生成 3 个视觉 demo 供用户选。

### 11.3 5 维专家评审

| 维度 | 一句话 |
|---|---|
| 1 · 哲学一致性 | 是否真按所选哲学执行，每个细节都有依据 |
| 2 · 视觉层级 | 用户视线是否按设计者意图自然流动 |
| 3 · 细节执行 | 像素级精确——对齐、间距、颜色、字体 |
| 4 · 功能性 | 每个元素都服务目标，零冗余 |
| 5 · 创新性 | 在哲学框架内有独特表达（biz-html-viz 版只评"反 cliché"） |

**两套实现**：

| 评的对象 | 用谁 | 脚本 |
|---|---|---|
| 决策报告（biz-decision-stack 出品） | `07-design-critic` subagent → `design-critique.html`（终端风） | 手动填模板 |
| 讲演产出（viz-deck 出品） | `viz-deck/scripts/review-5dim.mjs` → critique.html（讲演风） | `node review-5dim.mjs --input scores.json --output critique.html` |

两套都生成 ECharts radar 图 + Keep / Fix（按严重度 critical/important/polish）/ Quick-Wins。

### 11.4 v2 完整调用矩阵

| 你想要 | 触发什么 | 跑什么命令 |
|---|---|---|
| 8 份决策报告 + 评审 | "走一遍全流程并做 5 维评审" | orchestrator + design-critic |
| iOS 高保真原型 | "做个 iOS 原型" | viz-deck prototype-mode |
| 可编辑 PPT | "做幻灯片并导出 PPTX" | viz-deck slide-mode + `scripts/export-pptx.sh` |
| 8 秒 hero video | "做个 8 秒动画并导出 60fps MP4" | viz-deck motion-mode + `scripts/export-mp4.sh` |
| 带解说的科普视频 | "5 分钟讲清楚 XX" | huashu narrate-pipeline.mjs |
| 5 维评审讲演 deck | "评一下" | `scripts/review-5dim.mjs` |
| ECharts reveal 动画 MP4 | "把营收 4 季度趋势做成动效视频" | viz-charts motion + huashu render-video.js |

---

## 12 · huashu-design 桥接

### 12.1 何时需要

| 需求 | 需要 huashu？ |
|---|:---:|
| 用 v1 阶段报告 / 决策链 / 静态图表 | ❌ |
| 5 维评分本身（评分标准已内嵌） | ❌ |
| 5 维评审 HTML 生成（review-5dim.mjs） | ❌（脚本本身只依赖 Node + ECharts CDN） |
| HTML → MP4 / GIF | ✅ |
| HTML → 可编辑 PPTX | ✅ |
| 设备外壳（iPhone/Android/macOS/browser） | ⚠️ 可选（也可自己画，但 huashu 现成） |
| 20 哲学的完整提示词 DNA / 代表作 | ✅（viz-deck 文件只做适配引用） |
| TTS 解说视频 pipeline | ✅ + 豆包 TTS 凭据 |

### 12.2 安装

```bash
# 1. clone 到 ~/.claude/skills/
git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.claude/skills/huashu-design
cd ~/.claude/skills/huashu-design

# 2. huashu 自身不带 package.json，用本仓库推荐清单
cat > package.json <<'JSON'
{
  "name": "huashu-design-runtime",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "playwright": "^1.48.0",
    "sharp": "^0.33.5",
    "pptxgenjs": "^3.12.0",
    "pdf-lib": "^1.17.1"
  }
}
JSON

npm install
npx playwright install chromium

# 3. ffmpeg 必须在 PATH
ffmpeg -version
```

### 12.3 桥接调用约定

- 所有调用用 `~/.claude/skills/huashu-design/scripts/...` 绝对路径
- render-video.js 是 **CommonJS**（用 `require`），所以 huashu 目录的 `package.json` **不要**加 `"type": "module"`
- render-video.js 的 CLI 风格：`node render-video.js <html-file> --duration=N --width=W --height=H`（位置参数 + `--key=value`）
- HTML stage 必须在首次渲染后设 `window.__ready = true`，这是 huashu 录制的 t=0 起点
- 输出 MP4 自动命名为 `<html-file>.mp4`，在同目录下

### 12.4 探测脚本

每次进入 v2 模式前，agent 应做轻量探测：

```bash
HUASHU="$HOME/.claude/skills/huashu-design"
test -f "$HUASHU/SKILL.md" && \
test -f "$HUASHU/scripts/render-video.js" && \
test -f "$HUASHU/references/design-styles.md" && \
echo "OK" || echo "huashu-design MISSING — install via the guide section 12.2"
```

如果 `MISSING`：

1. **不要 silently fallback** — 告诉用户 v2 高级模式需要 huashu-design
2. 给出 12.2 节的安装命令
3. 询问是否仍要继续 v1 模式

---

## 13 · ppt-master 桥接（v3 真正可编辑 PPTX）

### 13.1 何时需要

| 用户意图 | 路由 | 必装组件 |
|---|---|---|
| "做个真正能在 PowerPoint 里改的 PPT" | viz-deck 模式 5 + ppt-master | ✅ |
| "决策报告做成可编辑 PPT" | biz-decision-stack PPTX 出口 + ppt-master | ✅ |
| "图表数据 stakeholder 要能在 PPT 里改" | viz-charts 原生 chart 出口 + ppt-master | ✅ |
| "PPT 里嵌入旁白音频" | viz-deck 模式 5 + embed-narration.sh + ppt-master | ✅ |
| "用公司模板生成 PPT" | viz-deck 模式 5 + register_template.py + ppt-master | ✅ |
| "PPT 自动导出 MP4 带旁白和动画" | viz-deck 模式 5 narrated + PowerPoint File → Export → Video | ✅（PowerPoint 是免费的 export 工具）|

**不需要**：HTML 报告 / 静态图表 / motion MP4（这些是 v1 / v2 能力，不依赖 ppt-master）。

### 13.2 安装

```bash
git clone --depth=1 https://github.com/hugohe3/ppt-master.git ~/.claude/skills/ppt-master
cd ~/.claude/skills/ppt-master

# 隔离的 Python 3.10+ venv，避免污染系统 Python
python -m venv .venv

# Windows
.venv/Scripts/pip install python-pptx edge-tts svglib reportlab Pillow numpy
# macOS/Linux
# .venv/bin/pip install python-pptx edge-tts svglib reportlab Pillow numpy

# 验证
.venv/Scripts/python -c "import pptx, edge_tts; print('ok')"
```

可选附加（图像生成、语音克隆）：

```bash
.venv/Scripts/pip install openai google-genai elevenlabs
```

### 13.3 三个 skill 的调用约定

| Skill | 入口 | 输入 | 输出 |
|---|---|---|---|
| viz-deck 模式 5 | `scripts/export-editable-pptx.sh <spec.json>` | JSON deck spec（8 layout） | `<base>_pptx_build/exports/<base>.pptx`（每元素可点） |
| viz-deck 旁白 | `scripts/embed-narration.sh <build_dir>` | speaker_notes/*.txt | `<base>_narrated.pptx`（嵌入 MP3，时长同步） |
| biz-decision-stack | `scripts/export-decision-pptx.sh <spec.json>`（在 biz-html-viz 内） | JSON 决策 spec（8 layout） | 终端风 PPTX（零动效） |
| viz-charts | `scripts/export-chart-pptx.sh <spec.json>` | chart spec 或 ECharts option | 单页含 `<c:chart>` 的 PPTX（数据可在 PPT 里改） |

### 13.4 探测脚本

每次进入 v3 模式前，agent 应做轻量探测：

```bash
PPTM="$HOME/.claude/skills/ppt-master"
PY="$PPTM/.venv/Scripts/python.exe"
[ -f "$PY" ] || PY="$PPTM/.venv/bin/python"

test -f "$PY" && \
test -f "$PPTM/skills/ppt-master/scripts/svg_to_pptx.py" && \
"$PY" -c "import pptx, edge_tts" 2>/dev/null && \
echo "OK" || echo "ppt-master MISSING — install via the guide section 13.2"
```

如果 `MISSING`：**不要 silently fallback** — 给用户 13.2 节的安装命令，询问是否走 v2 的快速 PPTX 出口（huashu html2pptx）替代。

### 13.5 可编辑性验证

生成 PPTX 后用 `unzip` 探测内部 OOXML 结构：

```bash
# 看每张 slide 的 native shape 数量 — 应该是数十个 <p:sp>
unzip -p deck.pptx ppt/slides/slide1.xml | grep -c "<p:sp>"

# 看是否有真正的 chart 对象 — viz-charts native 输出特有
unzip -l deck.pptx | grep "ppt/charts/chart"
```

如果 `<p:sp>` 数量是 1 或 0 → 失败，输出退化成单张图片。改用 `--only native` 重新生成：

```bash
~/.claude/skills/ppt-master/.venv/Scripts/python ~/.claude/skills/ppt-master/skills/ppt-master/scripts/svg_to_pptx.py \
  <project_dir> --only native -o <out>.pptx
```

### 13.6 边界

- ppt-master **不**用于：HTML keynote（viz-deck 模式 1）、motion MP4（viz-deck 模式 4，走 huashu）、HTML 报告（biz-decision-stack 主流程）
- ppt-master **跟** huashu-design 是并列的两个软桥接，**不互相替代**——huashu 管动画/视频/设计哲学/评审，ppt-master 管可编辑 PPT/旁白/母版/数据绑定图表
- ppt-master 是 MIT 协议，无商用限制；huashu-design 个人免费但商用需独立授权

---

**Skill Suite v3.0** · 2026-05-13 · biz-decision-stack + viz-deck + viz-charts + huashu-design (bridge v2) + ppt-master (bridge v3)
