# ZimaBlueAI Agent Skills

> **可交付的 AI agent 能力包，一次编写、多 harness 复用。**
> Production-grade skill packs for modern AI coding agents.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.2.0-2b6cb0.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-public_preview-orange.svg)](#九路线图--roadmap)
[![Harness](https://img.shields.io/badge/harness-Claude_Code-7c3aed.svg)](./claude-code-skills/)
[![Maintainer](https://img.shields.io/badge/maintainer-ZimaBlueAI-111.svg)](https://github.com/ZimaBlueAI)

[English version](./README_en.md) · [Install guide](./claude-code-skills/skills-install-guide.md) · [Changelog](./CHANGELOG.md) · [Contributing](./CONTRIBUTING.md)

---

## 一、它是什么

**ZimaBlueAI Agent Skills** 是一组为现代 AI 编码 agent（先发 Claude Code，后续移植到 Codex / OpenClaw / Hermes / Octarus）设计的**声明式能力包**。

每个 skill 是一份独立的 `.zip` 归档，结构是：

```
.claude/
├── agents/            # subagents（"以什么身份思考"）
└── skills/<name>/     # skill 本体
    ├── SKILL.md       # 触发条件 + 工作流（agent 主入口）
    ├── references/    # 工作流所需的参考资料（按需读）
    ├── templates/     # 产出物模板（HTML / mmd / json …）
    └── scripts/       # 可选工具脚本
```

agent 在用户说出特定意图时按需加载，完成一次结构化交付。**不是开发库**，**不是 npm 包**——是给 agent 用的能力声明。

---

## 二、当前发布

v0.2.0 起共三个 skill，覆盖**从董事会简报到对外讲演视频**的全链路。所有 skill 相互独立，按需取用。

| Skill | 一句话 | 输出 | 包大小 |
|---|---|---|---|
| **biz-decision-stack** | 7 subagents · 投资人 → CEO → 架构 → MRD → 交付 → 验收 → 评审 决策链 | 8 份终端风 HTML（黑底 + 酸黄 + 等宽 + 零动效） | 62 KB |
| **viz-deck** | 4 模产出 · keynote-report / hi-fi prototype / slide-deck / motion-stage | HTML / 可编辑 PPTX / MP4 / GIF / PDF（深空蓝紫青） | 65 KB |
| **viz-charts** | 5 类视觉表达 · Mermaid · ECharts · SVG 组件 · 3D 知识图谱 · Motion 视频 | 内嵌 HTML 或离线 SVG / MP4 | 153 KB |

### v0.2 升级要点（vs v0.1）

- ✨ **viz-deck 从 1 模产出扩展到 4 模产出**（高保真原型 / 幻灯片 / 动画 MP4 / 原阶段报告）
- ✨ **20 设计哲学** 整合到 viz-deck，按需切换风格（Pentagram / Kenya Hara / Sagmeister 等）
- ✨ **5 维专家评审** 一份终端风 + 一份讲演风，含 ECharts 雷达图与 Keep/Fix/Quick-Wins 修复清单
- ✨ **HTML → MP4 / 60fps / GIF** 工具链
- ✨ **HTML → 可编辑 PPTX** 真实文本框（非图片嵌入）
- ✨ biz-decision-stack 新增第 7 个 subagent `design-critic` 与 `design-critique.html` 模板
- ✨ 三个 skill 均提供 `samples/` 目录的真实可视产出示例

详见 [CHANGELOG](./CHANGELOG.md)。

---

## 三、与 huashu-design 的桥接关系

v0.2 引入了对 [`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design) 的**可选桥接**：

- **viz-deck** 的 *prototype / slide-deck / motion-stage* 三个 v2 模式需要 huashu-design 提供 MP4/PPTX 导出、设备外壳、动画引擎、20 设计哲学库与 5 维评审标准
- **biz-decision-stack** 只引用 huashu 的 5 维评审标准与可选 PDF 导出，**不引入** motion/BGM/设备外壳（决策报告坚持零动效原则）
- **viz-charts** 的 motion 模式直接调用 huashu 的 `render-video.js` 录屏

桥接为**软依赖**：未安装 huashu-design 时，v1 能力（原阶段报告 / 决策链 / 静态图表）完全不受影响。huashu-design 本身个人使用免费，**商用需独立授权**——详见其 [LICENSE](https://github.com/alchaincyf/huashu-design)。

```
                 ┌──────────────────────────────┐
                 │  huashu-design (软依赖)       │
                 │  - render-video.js (MP4)     │
                 │  - export_deck_pptx.mjs      │
                 │  - 20 design philosophies    │
                 │  - 5-dim critique standard   │
                 │  - ios/android/macos frames  │
                 └──────────┬───────────────────┘
                            │ optional bridge
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌─────────────┐  ┌─────────────────┐  ┌──────────────────┐
│ viz-charts  │  │    viz-deck     │  │ biz-decision-    │
│ (motion only│  │  (full bridge)  │  │     stack        │
│              │  │                 │  │ (critique only)  │
└─────────────┘  └─────────────────┘  └──────────────────┘
```

---

## 四、5 分钟上手

### 1. 安装 skill 到 Claude Code

**单项目**（推荐先这样验证）：

```bash
git clone --depth=1 https://github.com/ZimaBlueAI/skills.git
cd skills/claude-code-skills

# 解压到你的项目根目录（与 .git 同级）
unzip -o biz-decision-stack/biz-decision-stack.zip -d /path/to/your-project/
unzip -o viz-deck/viz-deck.zip                       -d /path/to/your-project/
unzip -o viz-charts/viz-charts.zip                   -d /path/to/your-project/
```

**全局**（所有项目共享）：

```bash
unzip -o biz-decision-stack/biz-decision-stack.zip -d ~/
unzip -o viz-deck/viz-deck.zip                       -d ~/
unzip -o viz-charts/viz-charts.zip                   -d ~/
```

### 2. 可选：装上 huashu-design 启用 v2 高级模式

```bash
git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.claude/skills/huashu-design
cd ~/.claude/skills/huashu-design

# Node 运行时（playwright + sharp + pptxgenjs + pdf-lib）
# huashu-design 本身不附带 package.json，建议用本仓库推荐的清单：
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

# ffmpeg 必须在 PATH，用于 MP4 编码与 60fps 插帧
ffmpeg -version || echo "请先安装 ffmpeg"
```

> 不装也行——只是 4 模产出会降级到 v1 单模，5 维评审用本地复述版评分标准。

### 3. 验证 Claude Code 已识别

```
> /skills
```

应能看到 `biz-html-viz` · `viz-deck` · `viz-charts` 三项。装了 huashu 还会多一项 `huashu-design`。

### 4. 触发自然语言

| 你说 | 自动路由到 |
|---|---|
| "给瑞林做一份董事会简报" | `01-board-advisor` + `biz-html-viz · board-brief` |
| "走一遍全流程" / "all hands" | `00-all-hands-orchestrator`（按顺序跑 6 个角色 + 评审） |
| "给 Mingjing 做阶段报告 deck" | `viz-deck · stage-report` |
| "做个 iOS 高保真原型" | `viz-deck · prototype-mode` |
| "做个演讲幻灯片" + "导出 PPTX" | `viz-deck · slide-mode` + `export-pptx.sh` |
| "做成 MP4" / "60fps 视频" | `viz-deck · motion-mode` + huashu `render-video.js` |
| "评一下这份" / "5 维评审" | `07-design-critic` 或 `viz-deck · review-5dim.mjs` |
| "做个架构图" / "加张折线图" | `viz-charts`（按数据形态自动选 Mermaid/ECharts） |
| "项目代码 3D KG" | `viz-charts · code-kg.mjs` + `templates/kg3d/code-graph.html` |

---

## 五、样例预览

每个 skill 的 `samples/` 目录都提供了**真实可视化产出**——可以直接打开看到效果：

| Skill | 样例 | 看什么 |
|---|---|---|
| biz-decision-stack | [`samples/design-critique-sample.html`](./claude-code-skills/biz-decision-stack/samples/design-critique-sample.html) | 终端风 5 维评审报告 · ECharts 雷达 · Keep/Fix/Quick-Wins |
| viz-deck | [`samples/motion-stage-sample.html`](./claude-code-skills/viz-deck/samples/motion-stage-sample.html) + [`.mp4`](./claude-code-skills/viz-deck/samples/motion-stage-sample.mp4) | 讲演风 motion stage 源 HTML + 录制好的 1920×1080 MP4 |
| viz-deck | [`samples/design-critique-sample.html`](./claude-code-skills/viz-deck/samples/design-critique-sample.html) | 讲演风 5 维评审（深空配色版） |
| viz-charts | [`samples/trend-motion-sample.html`](./claude-code-skills/viz-charts/samples/trend-motion-sample.html) + [`.mp4`](./claude-code-skills/viz-charts/samples/trend-motion-sample.mp4) | ECharts 多 series reveal 动效 + 录制 MP4 |
| viz-charts | [`demo-3d-code-kg.html`](./claude-code-skills/viz-charts/demo-3d-code-kg.html) · [`demo-3d-doc-kg.html`](./claude-code-skills/viz-charts/demo-3d-doc-kg.html) | 3D 代码/文档知识图谱（80/92 节点，可交互） |
| viz-charts | [`demo-terminal.html`](./claude-code-skills/viz-charts/demo-terminal.html) · [`demo-deck.html`](./claude-code-skills/viz-charts/demo-deck.html) | 双主题全组件演示 |

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
├── claude-code-skills/            ★ Claude Code harness（已发布）
│   ├── skills-install-guide.md    覆盖三 skill 的端到端安装/配置/使用手册
│   ├── skills-install-guide.html
│   │
│   ├── biz-decision-stack/
│   │   ├── biz-decision-stack.zip 安装包
│   │   ├── README.md              skill 单独说明
│   │   └── samples/               可视化产出样例（v0.2 新增）
│   │
│   ├── viz-deck/
│   │   ├── viz-deck.zip
│   │   ├── viz-deck-README.md
│   │   ├── design-system-deck.md  视觉规范公开版
│   │   ├── research-playbook.md   竞品调研三档协议
│   │   ├── sample-board-brief.html
│   │   └── samples/               4 模产出样例（v0.2 新增）
│   │
│   └── viz-charts/
│       ├── viz-charts.zip
│       ├── demo-*.html            4 个演示页
│       └── samples/               motion 图表样例（v0.2 新增）
│
├── codex-skills/                  ☐ OpenAI Codex CLI（规划中）
├── openclaw-skills/               ☐ OpenClaw（规划中）
├── hermes-skills/                 ☐ Hermes（规划中）
└── octarus-skills/                ☐ Octarus（规划中）
```

---

## 八、谁该用

| 角色 | 用哪个组合 | 为什么 |
|---|---|---|
| **创业团队 CEO** | biz-decision-stack 全套 + viz-deck (stage-report) | 内部用决策链对齐，对外用讲演 deck 路演 |
| **产品经理** | biz-decision-stack (PM 双模) + viz-deck (prototype) | MRD 文档化 + 高保真原型给开发对齐 |
| **首席架构师** | biz-decision-stack (architect) + viz-deck (architecture-deep) + viz-charts | 内部 ADR + 客户技术方案 + 3D 代码 KG |
| **投资人 / FA** | viz-deck (competitive-landscape) + viz-charts | 竞品调研可视化 + 数据动效路演 |
| **设计 / 品牌方** | viz-deck (4 模产出) + huashu-design | 一套工具覆盖原型 / 幻灯 / 视频 / 评审 |
| **工程 lead** | biz-decision-stack (dev-test) + viz-charts (3D KG) | 状态汇报 + 项目结构可视化 |

---

## 九、路线图 · Roadmap

| 阶段 | 内容 | 状态 |
|---|---|---|
| v0.1 | claude-code-skills 三件套首发 | ✅ 已发布 |
| **v0.2** | **4 模产出 · 20 哲学 · 5 维评审 · huashu-design 桥接 · samples** | ✅ **已发布（当前）** |
| v0.3 | codex-skills 移植（OpenAI Codex CLI 适配） | 🟡 规划中 |
| v0.4 | openclaw-skills / hermes-skills | ⚪ 规划中 |
| v0.5 | octarus-skills + 跨 harness 一致性测试 | ⚪ 规划中 |
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

**v2 桥接依赖**

- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) — 视频/PPTX 导出工具链、20 设计哲学、5 维评审标准

**运行时（CDN 或 npm 加载，不打包进本仓库）**

- [Mermaid](https://mermaid.js.org/) · [Apache ECharts](https://echarts.apache.org/) · [three.js](https://threejs.org/) · [3d-force-graph](https://github.com/vasturiano/3d-force-graph) · [Playwright](https://playwright.dev/) · [ffmpeg](https://ffmpeg.org/) · [pptxgenjs](https://gitbrent.github.io/PptxGenJS/) · [pdf-lib](https://pdf-lib.js.org/)

各项目保留其上游许可证，详见 [NOTICE](./NOTICE)。

---

## 联系

- GitHub: <https://github.com/ZimaBlueAI>
- Issues: <https://github.com/ZimaBlueAI/skills/issues>
- 安全问题: 见 [CONTRIBUTING.md](./CONTRIBUTING.md)

---

<sub>Made by ZimaBlueAI · 2026</sub>
