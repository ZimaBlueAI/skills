# ZimaBlueAI Agent Skills

> **可交付的 AI agent 能力包，一次编写、多 harness 复用。**
> Production-grade skill packs for modern AI coding agents.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.7.0-2b6cb0.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-public_preview-orange.svg)](#九路线图--roadmap)
[![Harness](https://img.shields.io/badge/harness-Claude_Code_·_Codex-7c3aed.svg)](./claude-code-skills/)
[![Channel](https://img.shields.io/badge/channel-OpenClaw_·_Hermes-0E7C66.svg)](./openclaw-skills/)
[![Maintainer](https://img.shields.io/badge/maintainer-ZimaBlueAI-111.svg)](https://github.com/ZimaBlueAI)

[English version](./README_en.md) · [Install guide](./claude-code-skills/skills-install-guide.md) · [频道交付 · OpenClaw](./openclaw-skills/USAGE.md) / [Hermes](./hermes-skills/USAGE.md) · [Changelog](./CHANGELOG.md) · [Contributing](./CONTRIBUTING.md)

---

## 一、它是什么

**ZimaBlueAI Agent Skills** 是一组为现代 AI agent 设计的**声明式能力包**：**Claude Code + OpenAI Codex CLI** 双 harness 首发，**v0.5 起在 OpenClaw / Hermes 上新增「频道交付层」**——让同一套生成能力在飞书等 IM 频道里**对话式生成并把成品发回会话**（Octarus 仍在路线图上）。

> 一句话看懂三种用法:在 **Claude Code / Codex** 里它是 coding agent 的能力包;在 **OpenClaw / Hermes** 里它是飞书群里那个"@一下就把动效报告/PPT 做好发回来"的机器人。同一份生成能力,两种交付面。

每个 skill 是一份独立的 `.zip` 归档，**同一份内容**通过两个 harness 的目录约定分别落到位：

```
Claude Code:                          Codex CLI:
.claude/                              .codex/
├── agents/         subagents (.md)   ├── agents/         subagents (.toml)
└── skills/<name>/  skill 本体        └── skills/<name>/  skill 本体（同 Claude）
    ├── SKILL.md    触发条件 + 工作流
    ├── references/ 参考资料
    ├── templates/  产出物模板
    └── scripts/    可选工具脚本
```

skill 内容（SKILL.md / references / templates / scripts）**一字不差**两个 harness 共享。差的只是落点路径与 subagent 序列化格式。

agent 在用户说出特定意图时按需加载，完成一次结构化交付。**不是开发库**，**不是 npm 包**——是给 agent 用的能力声明。

---

## 二、当前发布

v0.4.0 起覆盖**从董事会简报到对外讲演视频再到真正可编辑 PPT**的全链路；**Claude Code 与 OpenAI Codex CLI 双 harness 并发布**。**v0.7 新增自有设计合奏引擎 `zima-design`**（三引擎收编 + 五轴多样性协议 + 四风格 demo 画廊），并为全线生成类 skills 内联反 AI slop 硬闸。所有 skill 相互独立，按需取用。

| Skill | 一句话 | 输出 | 包大小 |
|---|---|---|---|
| **biz-decision-stack** | 8 subagents · 投资人 → CEO → 架构 → MRD → 交付 → 验收 → 评审 + **路由器**（v4）决策链 | 8 份终端风 HTML + 编辑级 PPTX（黑底 + 酸黄 + 等宽 + 零动效） | 83 KB |
| **viz-deck** | 5 模产出 + 六项 v4 增强（演讲者模式 / 三变体预览 / 长文转 deck / 学术模板 / Bento / 反思循环） | HTML / 可编辑 PPTX（每元素可点） / MP4 / GIF / PDF（深空蓝紫青） | 130 KB |
| **viz-charts** | 7 类视觉表达 · Mermaid · ECharts · SVG 组件 · 3D 知识图谱 · **SVG 环形/Circos KG**（可交互）· Motion 视频 · Native PPTX 图表 | 内嵌 HTML / 离线 SVG / 交互 SVG KG / MP4 / 数据绑定 PPTX 图表 | 157 KB |
| **zima-html-ppt** | ZimaBlueAI 现场讲演 deck · 暖纸编辑风 + **演讲者模式**（S 键弹提词器 / 逐字稿 / 计时 / 议程）· 母版 D1/D2/D3 | 单文件 HTML 幻灯片（暖纸 + 深青 + 金赭 + 三色条），复制起步模板填内容 | 23 KB |
| **taste-engine** 🆕 | 共享"口味层"· 三档 dial（DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY）+ 反 slop 预检 + 选材/文案规则 | 设计令牌 + 自检清单 + 两支样片（暗色电影感 web · 暖纸编辑 deck） | 文档 + 样片 |
| **web-shader-extractor** 🆕（移植 · 非 ZimaBlue 套件） | 网页 WebGL/WebGPU/Canvas 着色器动效**抠取与本地证据匹配复现**（Recon Kernel 状态机 + 6 铁律）· 移植自 [lixiaolin94/skills](https://github.com/lixiaolin94/skills)（MIT） | 抠取/复现项目 + 4 个自包含 demo（含 logo 矢量化生灭折叠 3D 用例） | 纯文件夹 · 零必需依赖 |
| **gzh-design** 🆕（移植 · 非 ZimaBlue 套件） | **微信公众号文章排版**：Markdown/docx/PDF/纯文本 → 粘贴不掉格式的公众号 HTML（6 套主题 + 主题生成器 + 双关卡校验 + 一键复制预览）· 移植自 [isjiamu/gzh-design-skill](https://github.com/isjiamu/gzh-design-skill)（AGPL-3.0，甲木 × 摸鱼小李） | 干净正文 HTML + 带「复制到公众号」按钮的预览页 | 纯文件夹 · 零必需依赖 |
| **zima-design** 🆕 | **设计合奏引擎**：原创路由协议编排三个内置引擎——anti-slop（21 宏结构 × 20 主题 × **57 条 slop-test 关卡**，源自 [nutlope/hallmark](https://github.com/nutlope/hallmark)）+ motion（动画决策框架 / 弹簧物理 / 性能铁律，源自 [emilkowalski/skills](https://github.com/emilkowalski/skills)）+ database（**84 风格 / 192 配色 / 74 字体搭配 / 98 UX 准则 / 22 技术栈**可检索，源自 [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)），联动 impeccable / huashu-design / taste-engine · **五轴多样性协议保证每次交付不重样** | 带「设计签名 + 六轴自评」双盖章的页面 / audit 报告 / 选型建议 + demo 三件套 | 纯文件夹 · database 检索需 Python 3 |

### 🆕 zima-design：设计合奏引擎 + Anti-AI-slop 全线升级

新增自有 skill **`zima-design`**——把三种互补的设计智能合奏起来：**结构与主题多样性**（anti-slop 引擎：21 宏结构轮换 + 57 slop-test 关卡 + audit/redesign 动词）、**动效与手感**（motion 引擎：频率门 → 目的 → 缓动 → 时长的决策框架，"该不该动"先于"怎么动"）、**数据化选型**（database 引擎：84 风格 / 192 配色 / 98 UX 准则本地检索）。一份原创路由协议决定谁主导谁辅助，**五轴多样性协议**（宏结构 × 主题 × 动效人格 × 卡片物理 × 密度节奏）强制连续交付不共享同一套模板骨架——治「AI 味模板脸」的合奏方案。三引擎均逐字节收编自 MIT 开源项目（溯源见 `zima-design/NOTICE.md`），外部联动 impeccable / huashu-design / taste-engine。附 demo 三件套：反面教材（12 处 slop 特征标本）→ 审计报告（24 项抽查 17 FAIL）→ 重设计对照。
同时**全线升级**本仓库生成类 skills：`viz-deck` / `viz-charts` / `biz-html-viz`（biz-decision-stack）/
`zima-html-ppt` / `viz-channel` 的 SKILL.md 均内联「**反 AI slop 硬闸**」——六大纪律
（交付前六轴自评 / 禁编造指标 / 色值字体令牌锁定 / 禁手绘假 chrome / 320–768px 响应式硬底线 /
标题禁斜体），装有 zima-design 时自动桥接全量 57 关卡；`taste-engine` 的预检清单同步蒸馏收编。

### 🆕 Taste 层 + 交互 SVG 知识图谱

新增 **`taste-engine`**——一层可叠加在任何 HTML/PPT 产出之上的"口味层"：**三档 dial**
（`DESIGN_VARIANCE` / `MOTION_INTENSITY` / `VISUAL_DENSITY`，写在 `<html>` 上由 CSS + JS 读取）
+ **反 AI slop 预检清单** + **选材 / 文案规则**。它不是渲染器、不是依赖，是一组设计令牌与约束；
各交付物有默认档（报告 `0/0/1` · 讲演 `1/1/1` · 发布 `2/2/1`），口味是"加"出来的、不覆盖既有基调。

两支可跑样片：

- `taste-engine/demo/taste-demo.html` —— 暗色电影感 web 报告：实时三档面板 · 滚动动效 · 图表 ·
  **三种知识图谱**（3D 力导向 / **SVG 环形 Context Graph**：拖拽·滚轮缩放·拖背景平移·点节点 BFS·搜索 / **Circos 弦图**：ideogram + 外圈 track + 内部 ribbon，可悬停高亮）。
- `taste-engine/demo/zima-ppt-demo.html` —— 暖纸编辑风现场讲演 deck：三色条 · 发丝卡片 · 计时条 ·
  **演讲者模式（按 S）**，可作 MP4 / 可编辑 PPTX 导出的输入态。

其中两种**纯 SVG、可交互**的知识图谱（环形 Context Graph / Circos 弦图）已并入 **`viz-charts`**
的"七类视觉表达"，可矢量缩放、可嵌报告主流、可打印——见 `viz-charts/references/svg-kg-guide.md`。

### 🆕 频道交付层 · OpenClaw / Hermes（v0.5 新增）

上面的生成类 skill 只管**生成**。v0.5 在 **OpenClaw** 与 **Hermes** 两个 IM-gateway agent 上补齐了**对话编排 + 频道交付**——新增 **`viz-channel`** 技能,让用户在飞书等频道里说一句话,agent 就**问清需求 → 调 viz-deck/viz-charts 生成 → 把成品作为附件发回当前会话**。

```
用户在飞书 @机器人:「做个云度 Q2 的动效汇报发我」
   → 频道里问清需求(≤2 问,给默认)
   → viz-deck 生成动效 HTML(图表/3D KG 由 viz-charts 提供)
   → 把 deck.html 发回当前 chat,附"下载用浏览器打开"
```

| | 说明 |
|---|---|
| **默认风格** | **ZimaBlue Editorial(暖纸编辑风)**——暖白纸底 + 深青主色 + 金/赭点缀 + 发丝卡片 + 顶部三色条,专业简洁出片即用(可一句话切换);见 `viz-channel/references/default-style.md`。完整规范 + **演讲者模式** + 起步模板见 **`zima-html-ppt`** 技能 |
| **形态** | 默认动效 HTML;「要能改」→ 可编辑 PPTX;「群里直接播」→ MP4;「画张图/知识图谱」→ chart / 3D KG |
| **投递通道** | 频道适配器,**当前实现 = 飞书 / Lark**(优先复用 lark-cli 令牌,回退 REST);留有加企业微信 / Slack / Telegram 的 seam |
| **打包** | 瘦桥接 + 安装器:viz-deck/viz-charts 本体由安装器从 `claude-code-skills/` 灌入目标平台,不重复维护 |
| **Hermes 独有** | 同一链路可做成 **cron / webhook 自动化**(定时出周报发群 / 事件触发出图) |
| **公众号排版** 🆕 | 新增 **`gzh-channel`** 技能:频道里发来文章 → Markdown 草稿 **interactive 卡片(代码块)** 发回确认 → 确认后调 `gzh-design` 排版 → 发回带「复制到公众号」按钮的预览 HTML,本地浏览器打开一键复制粘贴进公众号编辑器 |

📦 [`openclaw-skills/`](./openclaw-skills/) · [`hermes-skills/`](./hermes-skills/) — 各含 `viz-channel` + `gzh-channel` 技能、一键安装器(`.sh`/`.ps1`)、以及 **[USAGE.md](./openclaw-skills/USAGE.md) 实战案例库**(季度汇报 / 可编辑 PPT / 3D 知识图谱 / 发布会动画 / 竞品格局 / 群里改稿 / 自定义品牌风格 / 公众号排版,Hermes 另含 2 个自动化案例)。

### v0.4 升级要点（vs v0.3 · 26-skill 取长补短）

读了一篇《[26 个 PPT 生成 Skill 系统梳理](https://mp.weixin.qq.com/s/gaNsToTe33IPXIddesJs1g)》后，把开源 PPT skill 生态里**真正能补的**精挑出 7 项整合进现有三个 skill。**所有 v0.3 工作流完全保留**，全为增量。

- ✨ **viz-deck · Speaker Mode**（抄 [html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) 3.8k★）：按 **S** 弹出独立演讲者窗口，4 张磁吸卡片（当前页 / 下一页 / 提词器 / 计时器），BroadcastChannel 双窗同步。三档 LAYOUT 预设（GRID / PROMPTER / DUO）
- ✨ **viz-deck · Show-Don't-Tell 三变体预览**（抄 [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 17.5k★）：用户输入含混时，从 20 哲学里取 3 个对比明显的方向并生 3 张 hero 缩略让用户挑（5 个场景预设：investor-pitch / product-launch / tech-deepdive / academic / default）
- ✨ **viz-deck · Doc→Deck 转换器**（抄 [odin-slides](https://github.com/leonid20000/odin-slides) 147★ + [colloquium](https://github.com/natolambert/colloquium) 190★）：把 `.md` / `.docx` / `.pdf`（经 pandoc 预处理）直接转为 `pptx-deck-spec.json`，自动识别章节、表格转 KPI、引用块转 pullquote
- ✨ **viz-deck · Academic Talk 模板**（抄 [academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill) 387★）：模式 1 第 4 个子模板，强制 action title（"市场翻倍" 而非"市场分析"）+ 引用规范 + Anticipated Q&A + Limitations
- ✨ **viz-deck · Bento Grid 布局**（抄 [apple-bento-grid](https://github.com/hubeiqiao/apple-bento-grid) 171★）：HTML 单页 + pptx-deck 第 9 个 layout `bento-grid`，3 列响应式 + 不等宽磁贴 + 三色 accent + Hero halo
- ✨ **viz-deck · Reflective Loop**（抄 [PPTAgent](https://github.com/icip-cas/PPTAgent) 4.4k★）：生成完 spec 后自动跑页面级 5 维评分，低于阈值的页列入 redo-prompts.txt，输出含雷达 + 表格的反思报告
- ✨ **biz-decision-stack · Template Router**（抄 [mckinsey-pptx](https://github.com/seulee26/mckinsey-pptx) 426★）：第 9 个 subagent，对用户含混输入打分 8 模板 + 写辩护文进 HTML 注释头，每个选择都有理由

### v0.3 升级要点（vs v0.2）

- ✨ **ppt-master 软桥接**：通过 [`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master) 的 python-pptx + SVG→DrawingML 管线，所有 skill 现在都能输出**每个元素都可点的真编辑 PPTX**——不是图片嵌入，是原生 OOXML shapes
- ✨ **viz-deck 模式 5 · pptx-deck**：JSON spec → SVG-per-slide → ppt-master → `.pptx`，8 个 layout（cover/agenda/section/bullets/two-column/kpi-grid/pullquote/closing），三主题（deep-space / terminal / deck-light）
- ✨ **TTS 旁白嵌入**：edge-tts 免费 + ElevenLabs / MiniMax / Qwen / CosyVoice 付费克隆；PowerPoint File→Export→Video 自动同步旁白+动画导出 MP4
- ✨ **biz-decision-stack 决策报告 PPTX**：8 个终端风 layout（verdict-cover / kpi-roster / decision-matrix / roadmap-phases / risks-grid / retro-3col / action-list / summary-stack），零动效保留扫读哲学
- ✨ **viz-charts 原生数据绑定图表**：ECharts spec → `.pptx` 含 `<c:chart>` 对象，stakeholder 在 PowerPoint 里右键 "Edit Data" 即可改数
- ✨ 三个 skill 均新增 v3 sample PPTX

### v0.2 升级要点（vs v0.1）

- ✨ **viz-deck 从 1 模扩展到 4 模**（高保真原型 / 幻灯片 / 动画 MP4 / 原阶段报告）
- ✨ **20 设计哲学** + **5 维专家评审** 整合到 viz-deck
- ✨ **HTML → MP4 / 60fps / GIF** 工具链（huashu-design 桥接）
- ✨ biz-decision-stack 第 7 subagent `design-critic` + `design-critique.html`

详见 [CHANGELOG](./CHANGELOG.md)。

---

## 三、两个软桥接

v0.2 引入第一个软桥接 [`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design)（动画 / 视频 / 设计哲学 / 评审）；v0.3 加入第二个软桥接 [`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master)（python-pptx + SVG→DrawingML，真正可编辑的原生 PPTX）。

**v0.2 · huashu-design**（Node + Playwright + ffmpeg）：
- **viz-deck** 模式 2-4（prototype / slide-deck / motion-stage）使用 MP4/PPTX 导出、设备外壳、动画引擎、20 哲学、5 维评审
- **biz-decision-stack** 只用其 5 维评审标准（决策报告坚持零动效，不引入 motion/BGM/设备外壳）
- **viz-charts** motion 模式直接调用 `render-video.js`

**v0.3 · ppt-master**（Python + python-pptx + svglib + edge-tts）：
- **viz-deck** 模式 5（pptx-deck）：JSON spec → SVG → 真 DrawingML PPTX，可嵌入 TTS 旁白
- **biz-decision-stack**：8 个决策 layout 的终端风可编辑 PPTX
- **viz-charts**：ECharts spec → 数据绑定的原生 `<c:chart>` 对象

桥接都是**软依赖**：未安装时 v1 / v2 能力完全不受影响。两个上游均按各自的许可证发布（ppt-master MIT；huashu-design 个人免费，商用独立授权）——详见各自 LICENSE。

```
        ┌──────────────────────────┐     ┌────────────────────────────┐
        │ huashu-design (v0.2)     │     │ ppt-master (v0.3)          │
        │ - MP4 / 60fps / GIF      │     │ - python-pptx              │
        │ - HTML→PPTX (text-only)  │     │ - SVG→DrawingML (clickable)│
        │ - 20 design philosophies │     │ - master/template inherit  │
        │ - 5-dim critique std     │     │ - TTS narration embed      │
        │ - iOS/Android frames     │     │ - native data-bound charts │
        └────────────┬─────────────┘     └──────────────┬─────────────┘
                     │                                  │
       ┌─────────────┼──────────────┐    ┌──────────────┼─────────────┐
       ▼             ▼              ▼    ▼              ▼             ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌─────────────┐
│ viz-charts  │ │   viz-deck   │ │ biz-decision-    │ │   shared    │
│ (motion +   │ │ (modes 2-4 + │ │     stack        │ │  install    │
│  pptx chart)│ │   mode 5)    │ │ (critique+pptx)  │ │             │
└─────────────┘ └──────────────┘ └──────────────────┘ └─────────────┘
```

---

## 四、5 分钟上手

### 1. 安装 skill 到目标 harness

```bash
git clone --depth=1 https://github.com/ZimaBlueAI/skills.git
cd skills
```

**A · Claude Code**（单项目，推荐先验证）：

```bash
cd claude-code-skills
# 解到项目根（与 .git 同级）
unzip -o biz-decision-stack/biz-decision-stack.zip -d /path/to/your-project/
unzip -o viz-deck/viz-deck.zip                       -d /path/to/your-project/
unzip -o viz-charts/viz-charts.zip                   -d /path/to/your-project/
# 或全局：unzip -o ... -d ~/
```

**B · OpenAI Codex CLI**（一键脚本最省事）：

```bash
cd codex-skills
bash install.sh                    # Linux/macOS — 装到 ~/.codex/skills/ + ~/.codex/agents/
# Windows: .\install.ps1
```

详细的项目级 vs 全局、桥接安装等，分别见 [`claude-code-skills/skills-install-guide.md`](./claude-code-skills/skills-install-guide.md) 和 [`codex-skills/INSTALL.md`](./codex-skills/INSTALL.md)。

### 2. 可选 · 装 huashu-design 启用 v2 高级模式（动画 / 视频 / 设计哲学 / 评审）

```bash
git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.claude/skills/huashu-design
cd ~/.claude/skills/huashu-design

# Node 运行时（playwright + sharp + pptxgenjs + pdf-lib）
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
npm install && npx playwright install chromium

# ffmpeg 必须在 PATH（用于 MP4 编码与 60fps 插帧）
ffmpeg -version || echo "请先安装 ffmpeg"
```

### 3. 可选 · 装 ppt-master 启用 v3 真正可编辑 PPTX

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
.venv/Scripts/python -c "import pptx, edge_tts; print('ok')"   # Windows
# .venv/bin/python -c "import pptx, edge_tts; print('ok')"     # macOS/Linux
```

> 两个桥接都不装也行——v1 能力（HTML 报告 / 静态图表 / 决策链）完全不受影响。装了 huashu 解锁 v2（4 模产出 / 20 哲学 / 5 维评审 / MP4），再装 ppt-master 解锁 v3（每个元素可点的原生 DrawingML PPTX / TTS 旁白 / 母版继承 / 数据绑定图表）。

### 4. 验证 Claude Code 已识别

```
> /skills
```

应能看到 `biz-html-viz` · `viz-deck` · `viz-charts` 三项。装了 huashu 多一项 `huashu-design`；装了 ppt-master 不会单独显示（作为 skill 内部 runtime 调用）。

### 5. 触发自然语言

| 你说 | 自动路由到 |
|---|---|
| "给瑞林做一份董事会简报" | `01-board-advisor` + `biz-html-viz · board-brief` |
| "走一遍全流程" / "all hands" | `00-all-hands-orchestrator`（按顺序跑 6 个角色 + 评审） |
| "给 Mingjing 做阶段报告 deck" | `viz-deck · stage-report`（模式 1） |
| "做个 iOS 高保真原型" | `viz-deck · prototype`（模式 2） |
| "做个演讲幻灯片" + "导出 PPTX" | `viz-deck · slide-mode`（模式 3） + huashu `export_deck_pptx.mjs` |
| "做成 MP4" / "60fps 视频" / "解说视频" | `viz-deck · motion-mode`（模式 4） + huashu `render-video.js` |
| **"做个真正可编辑的 PPT" / "PowerPoint 里能改的"** | **`viz-deck · pptx-deck`（模式 5） + ppt-master**（v3 新增） |
| **"决策报告做成 PPT"** | **biz-html-viz + ppt-master 终端风 PPTX**（v3 新增） |
| **"图表数据要能在 PPT 里改"** | **viz-charts + ppt-master 原生 chart**（v3 新增） |
| "评一下这份" / "5 维评审" | `07-design-critic` 或 `viz-deck · review-5dim.mjs` |
| "做个架构图" / "加张折线图" | `viz-charts`（按数据形态自动选 Mermaid/ECharts） |
| "项目代码 3D KG" | `viz-charts · code-kg.mjs` + `templates/kg3d/code-graph.html` |

---

## 五、样例预览

每个 skill 的 `samples/` 目录都提供了**真实可视化产出**——直接打开就能看。完整清单在每个 skill 的 `samples/SAMPLES.md`，下表是亮点：

### v3 · PPTX 样例（11 个，每个都附 `.spec.json` 起点）

| 类别 | 样例 | 一句话 |
|---|---|---|
| **biz-decision-stack · 4 个决策 PPTX** | [`decision-board-brief-sample.pptx`](./claude-code-skills/biz-decision-stack/samples/decision-board-brief-sample.pptx) · [`decision-retro-report-sample.pptx`](./claude-code-skills/biz-decision-stack/samples/decision-retro-report-sample.pptx) · [`decision-tech-roadmap-sample.pptx`](./claude-code-skills/biz-decision-stack/samples/decision-tech-roadmap-sample.pptx) · [`decision-sprint-dev-sample.pptx`](./claude-code-skills/biz-decision-stack/samples/decision-sprint-dev-sample.pptx) | 终端风可编辑：董事会简报 · 季度复盘 · 四季度技术路线 · 周冲刺。每片含 15-55 个独立可点 shape。详见 [SAMPLES.md](./claude-code-skills/biz-decision-stack/samples/SAMPLES.md) |
| **viz-deck · 3 个 deck**（模式 5） | [`editable-deck-sample.pptx`](./claude-code-skills/viz-deck/samples/editable-deck-sample.pptx) · [`product-launch-deck-sample.pptx`](./claude-code-skills/viz-deck/samples/product-launch-deck-sample.pptx) · [`all-layouts-showcase-sample.pptx`](./claude-code-skills/viz-deck/samples/all-layouts-showcase-sample.pptx) | 深空风董事会更新（9 页）· deck-light 风产品发布（10 页）· 8 个 layout 全展示（8 页）。详见 [SAMPLES.md](./claude-code-skills/viz-deck/samples/SAMPLES.md) |
| **viz-charts · 4 个原生数据图表** | [`native-chart-sample.pptx`](./claude-code-skills/viz-charts/samples/native-chart-sample.pptx) · [`chart-trend-line-sample.pptx`](./claude-code-skills/viz-charts/samples/chart-trend-line-sample.pptx) · [`chart-market-share-doughnut-sample.pptx`](./claude-code-skills/viz-charts/samples/chart-market-share-doughnut-sample.pptx) · [`chart-critique-radar-sample.pptx`](./claude-code-skills/viz-charts/samples/chart-critique-radar-sample.pptx) | column · line · doughnut · radar 四种。PowerPoint 里右键 "Edit Data" 即可改底层数据。详见 [SAMPLES.md](./claude-code-skills/viz-charts/samples/SAMPLES.md) |

### v2 · HTML / 视频 / 评审样例

| Skill | 样例 | 看什么 |
|---|---|---|
| biz-decision-stack | [`design-critique-sample.html`](./claude-code-skills/biz-decision-stack/samples/design-critique-sample.html) | 终端风 5 维评审 · ECharts 雷达 · Keep/Fix/Quick-Wins |
| viz-deck | [`motion-stage-sample.html`](./claude-code-skills/viz-deck/samples/motion-stage-sample.html) + [`.mp4`](./claude-code-skills/viz-deck/samples/motion-stage-sample.mp4) | 讲演风 motion stage 源 HTML + 1920×1080 录屏 |
| viz-deck | [`design-critique-sample.html`](./claude-code-skills/viz-deck/samples/design-critique-sample.html) | 讲演风 5 维评审（深空配色） |
| viz-charts | [`trend-motion-sample.html`](./claude-code-skills/viz-charts/samples/trend-motion-sample.html) + [`.mp4`](./claude-code-skills/viz-charts/samples/trend-motion-sample.mp4) | ECharts 多 series reveal 动效 + 录屏 |
| viz-charts | [`demo-3d-code-kg.html`](./claude-code-skills/viz-charts/demo-3d-code-kg.html) · [`demo-3d-doc-kg.html`](./claude-code-skills/viz-charts/demo-3d-doc-kg.html) | 3D 代码/文档知识图谱（80/92 节点，可交互） |
| viz-charts | [`demo-terminal.html`](./claude-code-skills/viz-charts/demo-terminal.html) · [`demo-deck.html`](./claude-code-skills/viz-charts/demo-deck.html) | 双主题全组件演示 |

> Codex 用户：以上所有样例 `codex-skills/<skill>/samples/` 下都有同名副本。

---

## 六、设计哲学

1. **思考方式与产出能力解耦**
   subagent 决定"以什么身份思考"，skill 决定"用什么形态产出"。换 harness 时各自迁移，不互相绑死。
2. **HTML 优先于 Markdown**
   决策类产出（董事会简报、CEO 决策、复盘）走 HTML——结构化稳定、可签字、可归档、可打印。Markdown 只用于日志/注解。
3. **视觉系统先行**
   每个 skill 在动手前先定 design system（配色 / 字体 / 间距 / 禁令清单）。`references/design-system*.md` 是权威定义，templates 只是落地。
4. **少而精**
   biz-decision-stack 的 8 份报告共用 1 个 HTML 渲染 skill，不是 8 个独立 skill。一个 skill 干一件事，复用最大化。
5. **声明式 > 命令式**
   skill 是 Markdown 描述 + 模板 + 可选脚本，不是一堆代码。harness 怎么调用，由 harness 自己决定。
6. **可移植性是头等公民**
   skill 的核心 prompt 必须能不重写就迁移到至少 3 个 harness（Claude Code / Codex / OpenClaw）。
7. **桥接 > 嵌入**
   v0.2 起，所有跨技术栈的资产（视频/音频/外壳）走**软依赖桥接**而非嵌入自己。版本不漂移、许可证不交叉、包体不膨胀。

---

## 七、仓库结构

```
skills/
├── LICENSE                        Apache 2.0 全文
├── NOTICE                         版权 / 商标 / 第三方致谢
├── README.md                      本文件（中文）
├── README_en.md                   英文版
├── CHANGELOG.md                   版本变更记录
├── CONTRIBUTING.md                贡献指南
├── CODE_OF_CONDUCT.md             社区行为准则
│
├── claude-code-skills/            ★ Claude Code harness（已发布 v0.4）
│   ├── skills-install-guide.md    覆盖三 skill 的端到端安装/配置/使用手册
│   ├── skills-install-guide.html
│   │
│   ├── biz-decision-stack/
│   │   ├── biz-decision-stack.zip 安装包
│   │   ├── README.md              skill 单独说明
│   │   └── samples/               5 维评审 + 决策 PPTX + v0.4 template-router 案例
│   │
│   ├── viz-deck/
│   │   ├── viz-deck.zip
│   │   ├── viz-deck-README.md
│   │   ├── design-system-deck.md  视觉规范公开版
│   │   ├── research-playbook.md   竞品调研三档协议
│   │   ├── sample-board-brief.html
│   │   └── samples/               5 模产出样例 + v0.4 Speaker / 三变体 / Doc→Deck / 学术 / Bento / Reflect
│   │
│   └── viz-charts/
│       ├── viz-charts.zip
│       ├── demo-*.html            4 个演示页
│       └── samples/               motion 图表（v0.2）+ native PPTX chart（v0.3）
│
├── codex-skills/                  ★ OpenAI Codex CLI harness（已发布 v0.4，与 claude 同源同构）
│   ├── README.md                  Codex 版说明（强烈建议先读）
│   ├── INSTALL.md                 Codex 完整安装手册
│   ├── install.sh / install.ps1   一键脚本
│   ├── biz-decision-stack/        含 biz-decision-stack.zip（.codex/skills/ + 9 TOML agents）
│   ├── viz-deck/                  含 viz-deck.zip（.codex/skills/viz-deck/）
│   ├── viz-charts/                含 viz-charts.zip（.codex/skills/viz-charts/）
│   └── zima-html-ppt/             含 zima-html-ppt.zip（.codex/skills/zima-html-ppt/）
│
├── openclaw-skills/               ★ OpenClaw 频道交付层（已发布 v0.5）
│   ├── README.md                  这是什么 / 安装 / 用法
│   ├── USAGE.md                   实战案例库（9 案例 + 话术 + 排错）
│   ├── install-openclaw-skills.sh / .ps1   一键安装（瘦桥接 + 灌入 viz-deck/charts）
│   └── skills/viz-channel/        对话编排 + 频道投递技能
│       ├── SKILL.md               触发器 + clarify→generate→deliver 工作流
│       ├── references/            channel-protocol · delivery-matrix · openclaw-channel
│       └── scripts/               channel_deliver.py · channel_send.sh/.ps1 · resolve_chat.py
│
├── hermes-skills/                 ★ Hermes 频道交付层（已发布 v0.5，含 cron/webhook 自动化）
│   ├── README.md · USAGE.md（11 案例）
│   ├── install-hermes-skills.sh / .ps1
│   └── skills/viz-channel/        同 OpenClaw，references 换 hermes-channel（+自动化）
│
└── octarus-skills/                ☐ Octarus（规划中）
```

> `viz-deck` / `viz-charts` / `biz-html-viz` 本体**不在** openclaw/hermes 目录里——安装器从 `claude-code-skills/*.zip` 灌入目标平台,大技能单一可维护、不四处复制。

---

## 八、谁该用

| 角色 | 用哪个组合 | 为什么 |
|---|---|---|
| **创业团队 CEO** | biz-decision-stack 全套 + viz-deck (stage-report) + ppt-master | 内部决策链 HTML + 对外讲演 deck + 给董事会的可编辑 PPT |
| **产品经理** | biz-decision-stack (PM 双模) + viz-deck (prototype) + viz-deck (pptx-deck) | MRD 文档化 + 高保真原型给开发 + PRD 评审 PPT 给业务方 |
| **首席架构师** | biz-decision-stack (architect) + viz-deck (architecture-deep) + viz-charts | 内部 ADR + 客户技术方案 + 3D 代码 KG |
| **投资人 / FA** | viz-deck (competitive-landscape) + viz-charts + viz-charts (native chart pptx) | 竞品调研可视化 + 数据动效路演 + LP 月报数据 PPT |
| **设计 / 品牌方** | viz-deck (5 模产出) + huashu-design + ppt-master | 一套工具覆盖原型 / 幻灯 / 视频 / 评审 / 可交付 PPT |
| **工程 lead** | biz-decision-stack (dev-test) + viz-charts (3D KG) | 状态汇报 + 项目结构可视化 |
| **飞书群里的任何人**（运营/销售/老板） | OpenClaw / Hermes + `viz-channel` | 不碰命令行——群里 @机器人 说句话,动效报告 / PPT / 图表就做好发回会话 |

---

## 九、路线图 · Roadmap

| 阶段 | 内容 | 状态 |
|---|---|---|
| v0.1 | claude-code-skills 三件套首发 | ✅ 已发布 |
| v0.2 | 4 模产出 · 20 哲学 · 5 维评审 · huashu-design 桥接 · samples | ✅ 已发布 |
| v0.3 | ppt-master 软桥接 · viz-deck 模式 5 pptx-deck · 决策 PPTX · 数据绑定原生 chart · TTS 旁白嵌入 · codex-skills 双 harness 首发 | ✅ 已发布 |
| v0.4 | 26-skill 取长补短 · Speaker Mode · 三变体预览 · Doc→Deck · 学术模板 · Bento Grid · Reflective Loop · Template Router | ✅ 已发布 |
| v0.5 | OpenClaw / Hermes 频道交付层 · `viz-channel`（IM 频道对话生成 + 投递 · 飞书 adapter · cron/webhook 自动化 · USAGE 案例库） | ✅ 已发布 |
| **v0.6** | **`taste-engine` 口味层（三档 dial + 反 slop + 选材/文案）· `viz-charts` 交互 SVG 环形/Circos 知识图谱 · `zima-html-ppt` 现场讲演 deck（暖纸编辑风 + 演讲者模式）** | ✅ **已发布（当前）** |
| v0.7 | viz-charts narrative chart explainer（TTS 解说图表视频）+ 频道适配器扩展（企业微信 / Slack / Telegram） | 🟡 规划中 |
| v0.8 | octarus-skills 移植 + 三 harness 一致性测试 | ⚪ 规划中 |
| v1.0 | 5 harness 全覆盖 + skill registry（`skills.json` 索引） | ⚪ 规划中 |

---

## 十、贡献

欢迎 issue 与 PR。在动手之前请先读 [CONTRIBUTING.md](./CONTRIBUTING.md) 与 [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md)。

特别欢迎以下贡献：

- **新 harness 移植**：把现有 skill 移植到 codex / openclaw / hermes / octarus
- **新 skill 提案**：先开 issue 讨论范围，符合"声明式 / 可移植 / 少而精"再实现
- **更多视觉 reference**：超出现有 design-system 之外的真实业务样本
- **样例丰富化**：为现有 skill 提供更多行业语境的 samples（医疗 / 金融 / 教育 / 政务）

---

## 十一、许可证

本项目以 [Apache License 2.0](./LICENSE) 发布。Copyright © 2026 ZimaBlueAI。

## 十二、致谢

站在巨人肩膀上。以下项目以理念、运行时或工具链的方式让本仓库成为可能：

**理念与方法论**

- [garrytan/gstack](https://github.com/garrytan/gstack) — 多角色编排思路
- [Lum1104/Understand-Anything](https://github.com/Lum1104/Understand-Anything) — 知识图谱式可视化
- Thariq 关于 *HTML for Claude Code* 的早期论述 — 决策类内容 HTML 优先

**v2 桥接依赖（动画 / 视频 / 设计哲学 / 评审）**

- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) — 视频/快速 PPTX 导出工具链、20 设计哲学、5 维评审标准

**v3 桥接依赖（真正可编辑 PPTX / TTS 旁白 / 母版继承 / 数据绑定图表）**

- [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) — MIT · python-pptx + SVG→DrawingML 管线、edge-tts 旁白、母版导入、原生 chart 渲染

**运行时（CDN 或 npm/pip 加载，不打包进本仓库）**

- Node 侧：[Mermaid](https://mermaid.js.org/) · [Apache ECharts](https://echarts.apache.org/) · [three.js](https://threejs.org/) · [3d-force-graph](https://github.com/vasturiano/3d-force-graph) · [Playwright](https://playwright.dev/) · [ffmpeg](https://ffmpeg.org/) · [pptxgenjs](https://gitbrent.github.io/PptxGenJS/) · [pdf-lib](https://pdf-lib.js.org/)
- Python 侧（v3 新增）：[python-pptx](https://python-pptx.readthedocs.io/) · [edge-tts](https://github.com/rany2/edge-tts) · [svglib](https://github.com/deeplook/svglib) · [reportlab](https://www.reportlab.com/) · [Pillow](https://python-pillow.org/) · [NumPy](https://numpy.org/)

各项目保留其上游许可证，详见 [NOTICE](./NOTICE)。

---

## 联系

- GitHub: <https://github.com/ZimaBlueAI/skills>
- Issues: <https://github.com/ZimaBlueAI/skills/issues>
- 安全问题: 见 [CONTRIBUTING.md](./CONTRIBUTING.md)

---

<sub>Made by ZimaBlueAI · 2026</sub>
