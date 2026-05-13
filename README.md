# ZimaBlueAI Agent Skills

> **可交付的 AI agent 能力包，一次编写、多 harness 复用。**
> Production-grade skill packs for modern AI coding agents.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.3.0-2b6cb0.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-public_preview-orange.svg)](#九路线图--roadmap)
[![Harness](https://img.shields.io/badge/harness-Claude_Code-7c3aed.svg)](./claude-code-skills/)
[![Maintainer](https://img.shields.io/badge/maintainer-ZimaBlueAI-111.svg)](https://github.com/ZimaBlueAI)

[English version](./README_en.md) · [Install guide](./claude-code-skills/skills-install-guide.md) · [Changelog](./CHANGELOG.md) · [Contributing](./CONTRIBUTING.md)

---

## 一、它是什么

**ZimaBlueAI Agent Skills** 是一组为现代 AI 编码 agent（**Claude Code + OpenAI Codex CLI** 双 harness 首发，后续移植到 OpenClaw / Hermes / Octarus）设计的**声明式能力包**。

每个 skill 是一份独立的 `.zip` 归档，**同一份内容**通过两个 harness 的目录约定分别落到位：

```
Claude Code:                          Codex CLI:
.claude/                              .agents/
├── agents/         subagents (.md)   └── skills/<name>/   # skill 本体（同 Claude）
└── skills/<name>/  skill 本体        .codex/
    ├── SKILL.md    触发条件 + 工作流  └── agents/         subagents (.toml)
    ├── references/ 参考资料
    ├── templates/  产出物模板
    └── scripts/    可选工具脚本
```

skill 内容（SKILL.md / references / templates / scripts）**一字不差**两个 harness 共享。差的只是落点路径与 subagent 序列化格式。

agent 在用户说出特定意图时按需加载，完成一次结构化交付。**不是开发库**，**不是 npm 包**——是给 agent 用的能力声明。

---

## 二、当前发布

v0.3.0 起共三个 skill，覆盖**从董事会简报到对外讲演视频再到真正可编辑 PPT**的全链路；**Claude Code 与 OpenAI Codex CLI 双 harness 并发布**。所有 skill 相互独立，按需取用。

| Skill | 一句话 | 输出 | 包大小 |
|---|---|---|---|
| **biz-decision-stack** | 7 subagents · 投资人 → CEO → 架构 → MRD → 交付 → 验收 → 评审 决策链；v3 加 8 layout 终端风可编辑 PPTX | 8 份终端风 HTML + 编辑级 PPTX（黑底 + 酸黄 + 等宽 + 零动效） | 73 KB |
| **viz-deck** | 5 模产出 · keynote-report / hi-fi prototype / slide-deck / motion-stage / **pptx-deck**（v3 新增 真正 DrawingML） | HTML / 可编辑 PPTX（每元素可点） / MP4 / GIF / PDF（深空蓝紫青） | 81 KB |
| **viz-charts** | 6 类视觉表达 · Mermaid · ECharts · SVG 组件 · 3D 知识图谱 · Motion 视频 · **Native PPTX 图表**（v3 数据可在 PPT 里改） | 内嵌 HTML / 离线 SVG / MP4 / 数据绑定 PPTX 图表 | 156 KB |

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
bash install.sh                    # Linux/macOS — 装到 ~/.agents/skills/ + ~/.codex/agents/
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
├── claude-code-skills/            ★ Claude Code harness（已发布 v0.3）
│   ├── skills-install-guide.md    覆盖三 skill 的端到端安装/配置/使用手册
│   ├── skills-install-guide.html
│   │
│   ├── biz-decision-stack/
│   │   ├── biz-decision-stack.zip 安装包
│   │   ├── README.md              skill 单独说明
│   │   └── samples/               可视化产出样例（v0.2 评审 + v0.3 决策 PPTX）
│   │
│   ├── viz-deck/
│   │   ├── viz-deck.zip
│   │   ├── viz-deck-README.md
│   │   ├── design-system-deck.md  视觉规范公开版
│   │   ├── research-playbook.md   竞品调研三档协议
│   │   ├── sample-board-brief.html
│   │   └── samples/               5 模产出样例（v0.2 motion + v0.3 editable-deck）
│   │
│   └── viz-charts/
│       ├── viz-charts.zip
│       ├── demo-*.html            4 个演示页
│       └── samples/               motion 图表（v0.2）+ native PPTX chart（v0.3）
│
├── codex-skills/                  ★ OpenAI Codex CLI harness（已发布 v0.3，与 claude 同源同构）
│   ├── README.md                  Codex 版说明（强烈建议先读）
│   ├── INSTALL.md                 Codex 完整安装手册
│   ├── install.sh / install.ps1   一键脚本
│   ├── biz-decision-stack/        含 biz-decision-stack.zip（.agents/skills/ + 8 TOML agents）
│   ├── viz-deck/                  含 viz-deck.zip（.agents/skills/viz-deck/）
│   └── viz-charts/                含 viz-charts.zip（.agents/skills/viz-charts/）
│
├── openclaw-skills/               ☐ OpenClaw（规划中）
├── hermes-skills/                 ☐ Hermes（规划中）
└── octarus-skills/                ☐ Octarus（规划中）
```

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

---

## 九、路线图 · Roadmap

| 阶段 | 内容 | 状态 |
|---|---|---|
| v0.1 | claude-code-skills 三件套首发 | ✅ 已发布 |
| v0.2 | 4 模产出 · 20 哲学 · 5 维评审 · huashu-design 桥接 · samples | ✅ 已发布 |
| **v0.3** | **ppt-master 软桥接 · viz-deck 模式 5 pptx-deck · 决策 PPTX · 数据绑定原生 chart · TTS 旁白嵌入 · codex-skills 双 harness 首发** | ✅ **已发布（当前）** |
| v0.4 | openclaw-skills 移植 + 三 harness 一致性测试 | 🟡 规划中 |
| v0.5 | hermes-skills 移植 | ⚪ 规划中 |
| v0.6 | octarus-skills 移植 | ⚪ 规划中 |
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
