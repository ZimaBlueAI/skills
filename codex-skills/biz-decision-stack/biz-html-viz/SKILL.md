---
name: biz-html-viz
description: >-
  Generate terminal-style HTML reports for business decision workflows including board briefs, CEO strategy canvas, tech roadmaps, MRD and market analysis, project status boards, dev and QA reports, acceptance retrospectives, and 5-dimension design critiques. Use when the user asks for HTML business reports, decision briefs, roadmaps, MRD, project boards, retrospectives, acceptance reports, board decks, design critiques, 5D reviews, decision PPT, editable PPTX, or help choosing a business report template. Do not use for marketing landing pages, narrated slide decks, or playful UI. Use viz-deck for animated or keynote-style decks.
license: MIT
---

# biz-html-viz: 决策流 HTML 可视化

为投资人会、CEO 决策、架构会、PM/MRD、项目管理、开发测试、验收复盘 7 个商业流程节点生成统一视觉的 HTML 报告。

## 何时使用

被以下任一情况触发：

1. 用户直接要 HTML 形态的商业报告（"给我做一份 MRD 的 HTML"、"复盘报告做成网页"）
2. 一个 subagent（board-advisor / ceo-decision / chief-architect / product-manager / dev-test-lead / acceptance-retro）调用本 skill 来落地它的产出
3. 用户用 `/all-hands` 命令（或要求"走一遍全流程"）触发 orchestrator，最终需要把 6 份报告打包成 index

**不要用于**：营销页、PPT、playful UI、纯文本备忘录、Word 报告（用 docx skill）。

## 工作流程

### 第一步：读 design-system

**强制**先读 `references/design-system.md`。这份文档定义了所有 7 个模板共享的 CSS 变量、字体、骨架结构和视觉禁令。**未读 design-system 直接写 HTML = 视觉不统一 = 返工**。

### 第二步：选模板（v4 路由器）

> **v4 新增 template-router subagent**：用户表达含混（"做个 deck 给老板"、"做个项目报告"）→ 自动跑 8 模板路由 + 输出 ROUTING DECISION 块 + 写辩护文进 HTML 注释头。详见 `~/.claude/agents/08-template-router.md` + `references/template-routing-rubric.md`。
>
> 用户明确说"做 board brief"或"做 retro" → **不需要路由**，直接走对应模板。

| 用户意图 / agent 来源 | 模板 |
|---|---|
| 股东会 / 董事会 / 投资人简报 / board / shareholder | `board-brief.html` |
| CEO 决策 / 战略 / 取舍 / canvas | `ceo-canvas.html` |
| 架构会 / 技术路线 / tech roadmap / 技术选型 | `tech-roadmap.html` |
| MRD / 市场分析 / 需求文档 / 用户画像 / 竞品 | `mrd-report.html` |
| 项目管理 / 看板 / 进度 / 里程碑 / 燃尽 | `project-board.html` |
| 开发汇报 / 测试报告 / SD / TD / QA / 缺陷 | `dev-report.html` |
| 验收 / 复盘 / retro / 总结 / lessons | `retro-report.html` |
| 设计评审 / 出片质量 / 5 维评审（v2 新增） | `design-critique.html` |

### 第三步：填充内容

1. 复制 `templates/{name}.html` 到 `/home/claude/claude-config/output/`（或用户指定目录）
2. 用真实数据替换 `{{占位符}}`——**不要保留任何 `{{ }}`，不要写"示例数据"**
3. 数据不足时：从对话历史中提取；仍不足，主动列出缺什么、并给出**可信的占位估值**（标注 `[ESTIMATED]`），而不是编造
4. 每份报告**头部 meta 4 项必填**：TYPE、DATE、AUTHOR、VERSION
5. 标题用 serif，所有数字用 mono，章节标题用大写 mono——这是统一感来源

### 第四步：交付

- 单文件 HTML（CSS 内联），无外部依赖（除 Google Fonts）
- 文件名格式：`{date}-{type}-{slug}.html`，如 `2026-05-10-mrd-mingjing-v1.html`
- 用 `present_files` 交付，preamble 一句话说明"这是 {类型} 报告，含 N 个章节，关键决策点 X"

### 第五步（v3 可选）：导出可编辑 PPTX

如果 stakeholder 要在 PowerPoint 里打开并改 — 用 ppt-master 桥接：

```bash
# 1) 复制对应的 JSON spec 起点
cp ~/.claude/skills/biz-html-viz/specs/board-brief.example.json my-brief.json
# 或 specs/retro-report.example.json

# 2) 改字段（verdict / KPIs / options / risks / actions），与 HTML 报告同源同数据

# 3) 生成
~/.claude/skills/biz-html-viz/scripts/export-decision-pptx.sh my-brief.json
# → ./my_brief_pptx_build/exports/my_brief.pptx
```

8 个可用 layout：`verdict-cover`、`kpi-roster`、`decision-matrix`、`roadmap-phases`、`risks-grid`、`retro-3col`、`action-list`、`summary-stack`。

主题锁死为 terminal（黑 + 酸黄 + JetBrains Mono），**零动效、无旁白、无转场**——这是 biz-decision 的设计哲学，不要试图加。要动画/旁白？走 viz-deck 的 pptx-deck 模式。

详细协议见 `references/pptx-master-bridge.md`。

## 内容质量准则（少废话核心规则）

- **一段话不超过 3 句**——决策者扫读，不读散文
- **数字优先**——能用数字说的不用形容词（"显著增长" → "+47% MoM"）
- **每个章节有结论句**——放最上面或加 `<blockquote>`
- **风险/决议必带责任人和截止日期**——`@person · YYYY-MM-DD`
- **拒绝凑字数**——空章节直接删除，不要写"暂无"

## 全流程编排（orchestrator 模式）

当用户要"走一遍全流程"或 6 个 subagent 依次调用本 skill 后，再生成一份 `index.html`：

- 列出 6 份子报告链接
- 抽取每份报告的「关键决策」一行摘要
- 提供"统一打印"按钮（CSS `@media print` 已就绪，可直接 Ctrl+P 输出 PDF）
- index 的视觉风格与子报告完全一致

`templates/index.html` 是这个总览模板。

orchestrator 末尾可询问："要不要让 design-critic 给这 6 份报告做一次 5 维评审？"——用户同意则触发第 7 个 agent。

## v2 · 5 维设计评审（终端风版）

新增 design-critique.html 模板与 design-critic subagent，给本 skill 7 份决策报告做"出片质量"把关。

### 何时触发

| 场景 | 触发 |
|---|:---:|
| 用户问"评一下"、"好不好看"、"做对了吗"、"再优化" | ✅ |
| orchestrator 跑完全流程，用户问"质量怎么样" | ✅ |
| `design-critic` subagent 被显式召唤 | ✅ |

### 5 维一句话

1. **哲学一致性** — 是否遵循终端风设计系统（黑底/酸黄/等宽/零动效）
2. **视觉层级** — h1（serif）/ section（mono uppercase）/ data（mono）三档对比
3. **细节执行** — meta 4 项 / 占位符 / 数字单位 / 责任人格式 / 文件名
4. **功能性** — 每段服务决策，无废话，有结论句
5. **创新性（反 cliché）** — 无紫渐变 / emoji 装饰 / 玻璃拟态 / 大圆角 / 动画

详细评分宪法见 `references/critique-5dim.md`。

### 工作流

读 `references/critique-5dim.md` → 客观项自动 grep 检查 → 主观项人工评估 → 写 scores.json → 复制 `templates/design-critique.html` 替换占位 → 用 `present_files` 交付。

**不要**给 10/10。**不要**列 > 3 条 fix。**不要**用 deck 主题（评决策报告必须沿用终端风）。

### 与 huashu-design 的桥接

5 维评分标准源自 `~/.claude/skills/huashu-design/references/critique-guide.md`（如已安装）；未安装也 OK——`references/critique-5dim.md` 已把核心条款做了终端风适配版复述。详见 `references/huashu-bridge.md`。

biz-html-viz **不引入** huashu 的 motion / MP4 / BGM / 设备外壳——决策报告就是零动效终端风。需要那些能力的用户应该用 viz-deck。

## 模板清单

```
templates/
├── board-brief.html       股东/投资人会
├── ceo-canvas.html        CEO 战略决策画布
├── tech-roadmap.html      架构师技术路线
├── mrd-report.html        PM 市场需求文档
├── project-board.html     PM 项目管理看板
├── dev-report.html        SD/TD 开发测试汇报
├── retro-report.html      验收 + 复盘
├── design-critique.html   v2 · 5 维设计评审
└── index.html             全流程总览

references/
├── design-system.md       7 模板共享视觉规范（必读）
├── critique-5dim.md       v2 · 5 维评审宪法（design-critic 必读）
└── huashu-bridge.md       v2 · 与 huashu-design 的有限桥接
```

## 反模式（出现这些 = 失败）

- 出现紫色渐变、玻璃拟态、emoji 装饰
- 章节标题用大字号 sans 而不是 mono uppercase
- 数据用 sans 而不是 mono
- 写了"以下是一些建议..."这类引导废话
- 做出花哨动画或滚动视差
- 7 份报告视觉风格不一致
- 留下未填充的 `{{占位符}}`

---

## 反 AI slop 硬闸 · zima-design 联动

交付前除本 skill 自身规范与反模式清单外，再过一遍下面六条**硬闸**——蒸馏自
[nutlope/hallmark](https://github.com/nutlope/hallmark)（MIT · Anti-AI-slop design skill，
已收编为本仓库 `zima-design` 的 anti-slop 引擎）的六大纪律，任何 HTML / deck / 图表产出都适用：

1. **交付前六轴自评** — Philosophy / Hierarchy / Execution / Specificity / Restraint / Variety
   各打 1–5 分，任一 < 3 先返工再交付；把分数以注释盖在产物头部
   （`<!-- zima-design pre-emit critique: P5 H4 E5 S4 R5 V5 -->`）。
2. **诚实文案** — 用户没给的指标一律不编：禁止 "+47% conversion"、"50,000+ teams"、
   编造的 testimonial / logo 墙 / 案例数；缺数据用 `—` + 「待确认」灰块占位，或换一种版式。
3. **令牌锁定** — 主题选定后，色值与 `font-family` 只许引用 `:root` 令牌
   （`var(--color-accent)` / `var(--font-display)`）；禁止内联 hex / OKLCH / 裸字体名，
   需要新值先入令牌块再引用。
4. **禁手绘假 chrome** — 不画假浏览器栏（红黄绿点 + URL 胶囊）、假手机壳、
   假代码窗标题栏、假 IDE 窗口；要么真截图包 `<figure>`（至多发丝描边），要么让内容裸站。
5. **响应式硬底线** — 320 / 375 / 414 / 768px 四档无横向滚动（根上 `overflow-x: clip`，
   不用 `hidden`）；带图网格轨道用 `minmax(0,1fr)` 不用裸 `1fr`；可点击文本（按钮 / 导航 /
   CTA）不许折成两行；超长词标题加 `overflow-wrap: anywhere; min-width: 0`。
6. **标题禁斜体** — 标题与 display 字一律 roman（`font-style: normal`）；
   强调用字重 / 强调色 / 下划线承载，斜体只留正文强调。

**结构多样性**：同一会话连续产出多份同类交付物时，轮换章节节奏与版式骨架——
两份产出不允许共享同一套「hero → 三卡 → CTA」式模板节奏。

若本机装有 **zima-design** skill（`~/.claude/skills/zima-design/`、项目 `.claude/skills/zima-design/`
或 `.codex/skills/zima-design/`），交付前加载其 `engines/anti-slop/references/slop-test.md` 跑 **universal 子集**
（视觉 / 排版 / 文案 / 对比度 / a11y / 微交互关卡；报告与 deck 类产出跳过整页宏结构轮换与
`.hallmark/log.json` 项目记忆关卡）。口味档位与选材 / 文案细则见姊妹层 **taste-engine**
（`references/anti-slop-preflight.md`）。
