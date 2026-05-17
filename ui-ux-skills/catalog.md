# UI/UX Skills · 18 款精选目录（v0.4 提案）

> 参考 [Pasquale Pillitteri 的 18 款 UI/UX skill 推荐](https://pasqualepillitteri.it/zh/news/889/claude-code-18-zuijia-skill-ui-ux-sheji-zhinan)，做了有见解的取舍。
>
> **本目录是设计提案，尚未实现。** 与 v0.3 已发布的 biz-decision-stack / viz-deck / viz-charts 互补，不替代。

---

## 策划框架

### 我们删了什么 · 为什么

| 原文章条目 | 删除原因 |
|---|---|
| Anthropic Frontend Design / UI/UX Pro Max / Taste Skill / Interface Design / Frontend Design Pro Demo | **5 个 Visual/Aesthetic 类别严重重叠**——本质都是"给点视觉灵感"。合并为 1 个 `design-direction-explorer` 即可。 |
| Designer Skills (63-skill bundle) | 63 个 skill 一捆走"大而全"，违背"少而精"原则。把每个值得保留的拆出来单独做。 |
| Bencium UX Designer | 28K 字的方法论是文档，不是 skill。能力可融入 `multi-heuristic-audit`。 |
| Vercel Agent Skills | 性能/可访问性混合体——可访问性归 `a11y-audit`，性能不在 UI/UX 范围（属于 SRE skill）。 |
| Hooked UX | Nir Eyal 的钩子模型适用面太窄（仅消费应用/留存场景），单独做 skill 不够普适。可作为 `ux-research-synthesizer` 的一个分析框架。 |
| Figma to Code | Figma plugin 范畴，不是 Claude Code skill 范畴。 |
| Theme Factory / Brand Guidelines / Canvas Design | 静态预设、AI 出图——不是声明式工作流。合并入 `design-tokens-generator`。 |
| App Store Screenshots | 太窄，属于 marketing asset 类——不在 UI/UX 设计核心。 |

**总共删了 14 个原文条目（含"额外提到"的），换成 13 个新设计 + 5 个原文保留 = 18 个。**

### 我们保留了什么（5 个，来自原文）

| Skill | 来源 | 保留原因 |
|---|---|---|
| `design-sprint-facilitator` | 原文 #13 | GV 5-day sprint 是真方法论，跨场景适用 |
| `refactoring-ui-audit` | 原文 #9 | Refactoring UI 框架精准聚焦视觉细节 |
| `multi-heuristic-audit` | 原文 #10 + Bencium | 扩展为多框架（Nielsen + Shneiderman + ISO 9241） |
| `platform-adaptation` | 原文 #11（扩展） | 单 iOS 太窄，扩展为 iOS HIG + Material 3 + Fluent + GNOME 四端 |
| `ui-ux-skill-creator` | 原文 #18 | meta-skill，把品牌系统蒸馏成 skill 的能力必须保留 |

### 我们新增了什么（13 个，对应你 repo 的能力缺口）

按设计流程的 7 个阶段排列：

---

## Phase 1 · Discover & Research（3 skills）

### 1. `ux-research-synthesizer` 🆕 P1

**Purpose**: 用户访谈逐字稿 / 问卷数据 / 客服 ticket → personas + Jobs-to-be-Done + opportunity map。

**Trigger keywords**: `用户研究 / 访谈整理 / personas / JTBD / opportunity map / user research synthesis / interview synthesis`

**When NOT to use**: 仅有定量数据（用 viz-charts 做图）；纯桌面研究（用 viz-deck competitive-landscape）。

**Implementation sketch**:
- references: `jtbd-framework.md`, `persona-template.md`, `affinity-mapping.md`, `hook-model-overlay.md`（吸收 Hooked UX 的核心）
- templates: `personas.html`, `jtbd-canvas.html`, `opportunity-tree.html`
- scripts: `cluster-quotes.mjs`（把访谈引述按主题聚类）

---

### 2. `design-sprint-facilitator` 🔁 原文 #13 P2

**Purpose**: GV 5-day sprint 编排——Understand → Sketch → Decide → Prototype → Test，五天每天产出物清单 + 时盒表 + 决策投票模板。

**Trigger keywords**: `design sprint / 5-day sprint / GV sprint / lightning decision jam / 设计冲刺`

**When NOT to use**: 已有明确需求（不需要 ideation）；时间 < 3 天（用 lightning version）。

**Implementation sketch**:
- references: `gv-sprint-playbook.md`, `day-by-day-agenda.md`, `decision-vote-protocols.md`
- templates: `sprint-board.html`（5 列看板）, `decision-doc.html`, `prototype-brief.html`

---

### 3. `info-architect` 🆕 P1

**Purpose**: 产品功能列表 → sitemap + navigation tree + taxonomy + URL/route 命名建议。

**Trigger keywords**: `信息架构 / IA / sitemap / 导航结构 / taxonomy / 信息分类 / navigation design`

**When NOT to use**: 单页应用（无导航）；已有 IA 想做评审（用 `multi-heuristic-audit`）。

**Implementation sketch**:
- references: `card-sorting-output-to-tree.md`, `ia-anti-patterns.md`（避免"More" 抽屉、深嵌套）, `naming-conventions.md`
- templates: `sitemap-tree.html`（接 viz-charts mermaid）, `route-table.html`
- scripts: `validate-depth.mjs`（标记 >3 层嵌套）

---

## Phase 2 · Define & Specify（3 skills）

### 4. `prd-to-mockup` 🆕 **P0** 🔥

**Purpose**: 文本 PRD / 用户故事 → 低保真 wireframe HTML（手绘风 SVG）。Bridge 设计前最关键的一步。

**Trigger keywords**: `PRD 出图 / 把需求画出来 / wireframe from PRD / 低保真原型 / 草图 / 线框图`

**When NOT to use**: 已有 wireframe 要做 hi-fi（用 `wireframe-to-hifi`）；纯 marketing landing（用 viz-deck）。

**Implementation sketch**:
- references: `prd-parsing-protocol.md`, `wireframe-vocabulary.md`（box / line / placeholder grammar）
- templates: `wireframe-mobile.html`, `wireframe-desktop.html`, `wireframe-tablet.html`
- scripts: `prd-to-elements.mjs`（NLP-light 提取 nouns → UI elements）

**Why P0**: 你 repo 里 viz-deck 的 prototype 模式是 **hi-fi** 起步，缺了从 PRD 到低保真这一步——这是产品经理 / 设计师协作的真正断层。

---

### 5. `design-tokens-generator` 🆕 P0

**Purpose**: 品牌输入（logo / 关键词 / 行业）→ 完整 design tokens JSON（颜色 / 字号 / 间距 / 圆角 / 阴影），可直接喂 Figma Tokens / Tailwind / CSS variables。

**Trigger keywords**: `design tokens / 设计 token / 主题变量 / brand guidelines / theme system / Tailwind 主题`

**When NOT to use**: 只是想换一两个颜色（直接改 CSS）；已有 tokens 要做 audit（用 `refactoring-ui-audit`）。

**Implementation sketch**:
- references: `tokens-schema.md`（W3C design-tokens-format-module）, `color-palette-generation.md`（perceptual uniform），`type-scale-systems.md`（modular scales 1.125 / 1.2 / golden）
- templates: `tokens.json`, `tokens.tailwind.config.js`, `tokens.css`, `tokens-preview.html`
- scripts: `palette-from-brand.mjs`（HSL hue rotation + accessibility check）, `validate-contrast.mjs`

**Why P0**: 原文有 Theme Factory + Brand Guidelines 两个弱预设——合并成一个**真正生成 tokens 的 skill** 更强。

---

### 6. `user-flow-mapper` 🆕 P1

**Purpose**: 用户故事 → user flow diagram（含决策分支 + 错误路径 + 状态机）。

**Trigger keywords**: `user flow / 用户流程图 / 决策分支 / state machine / 状态机 / flowchart from story`

**When NOT to use**: 纯展示性流程（用 viz-charts mermaid 即可，不需要这套语义）。

**Implementation sketch**:
- references: `flow-vocabulary.md`（start / action / decision / error / exit），`state-machine-patterns.md`
- templates: `user-flow.mmd`（mermaid），`state-machine.mmd`
- scripts: `story-to-flow.mjs`（语句 → mermaid 节点）

---

## Phase 3 · Ideate & Generate（4 skills）

### 7. `design-direction-explorer` 🆕（吸收原文 #1 #5 #15 #16） P1

**Purpose**: 一次性产出 3 个对比鲜明的视觉方向（Swiss Minimalism / Glassmorphism / Brutalist / Editorial / Tech-Noir 等），各含 hero shot + 配色 + 字体组合。

**Trigger keywords**: `设计方向 / 视觉风格 / 风格探索 / design exploration / 多版本设计 / 给我几个选项`

**When NOT to use**: 已有明确品牌系统（直接用 `design-tokens-generator`）；只要一份产出（用 viz-deck）。

**Implementation sketch**:
- references: `style-vocabulary.md`（12 种 cataloged style：每种含 typography signature / color discipline / spacing rhythm）, `direction-presentation-format.md`
- templates: `direction-card.html` × 12 种风格，`comparison-board.html`（3 方向并列）
- scripts: `render-three-directions.mjs`

**与原文章关系**：把原文章的 Pro Max + Taste + Interface + Pro Demo + Theme Factory 5 个 Visual 类合并成 1 个——**有选择有对比**比"66 种 preset 砸脸"更有用。

---

### 8. `ui-component-library` 🆕 P1

**Purpose**: 给定 design tokens + 框架（React / Vue / Svelte / plain HTML），生成完整 UI 组件库——button / input / select / modal / toast / tabs / nav，每个组件含全部状态（default / hover / focus / disabled / loading / error）。

**Trigger keywords**: `组件库 / component library / UI kit / shadcn 风格 / Radix-based / headless components`

**When NOT to use**: 一次性单个组件（直接让 Claude 写）；要的是 mockup 不是代码（用 `wireframe-to-hifi`）。

**Implementation sketch**:
- references: `component-checklist.md`（22 个核心组件清单 + 必备 states），`a11y-baseline.md`（每组件最低 ARIA 要求），`headless-vs-styled.md`
- templates: 22 个组件 × 3 框架 = 66 个起点文件（按需用）
- scripts: `gen-component.mjs --type button --framework react`

---

### 9. `wireframe-to-hifi` 🆕 P1

**Purpose**: 低保真 wireframe（来自 `prd-to-mockup`）+ design tokens → 高保真可点击 HTML mockup。

**Trigger keywords**: `wireframe to hi-fi / 高保真原型 / 把线框变成真的 / mockup polish / fill in the boxes`

**When NOT to use**: 从零开始（先用 `prd-to-mockup` 出线框）；要的是真代码（用 `ui-component-library`）。

**Implementation sketch**:
- references: `content-population-rules.md`（不能用 lorem ipsum——用真实候选），`image-sourcing.md`（Wikimedia / Met / Unsplash 优先）
- templates: `hifi-shell.html`（含 design-token CSS var 占位）
- scripts: `populate-content.mjs`, `swap-placeholders.mjs`

---

### 10. `prototype-interaction-flow` 🆕 P1

**Purpose**: 高保真 mockup × 多页 → 可点击交互原型（页面间跳转 + 表单状态 + modal / toast / loading 演示）。**比 viz-deck 的 prototype 模式更聚焦**——前者是设备外壳里的单页，这个是流程演示。

**Trigger keywords**: `interactive prototype / 点击原型 / 可交互 demo / 流程演示 / click-through`

**When NOT to use**: 单页 demo（用 viz-deck prototype 模式）；要的是真代码（用 `ui-component-library`）。

**Implementation sketch**:
- references: `interaction-grammar.md`（hover / focus / press / drag 的 visual signal），`microinteraction-patterns.md`
- templates: `prototype-shell.html`（含 state manager），`flow-controller.js`
- scripts: `link-pages.mjs`（多页 mockup 自动注入路由）

---

## Phase 4 · Critique & Refine（4 skills）

### 11. `refactoring-ui-audit` 🔁 原文 #9 P0

**Purpose**: 用 Refactoring UI 框架审计：视觉层级（hierarchy）、间距节奏（spacing rhythm）、阴影 / 边框（depth cues）、颜色用度（color usage）。生成 Keep / Fix / Quick-Win 清单。

**Trigger keywords**: `视觉评审 / Refactoring UI / 视觉细节 / 间距问题 / hierarchy review / "my UI looks off"`

**When NOT to use**: 哲学层面评审（用 viz-deck/biz-decision 的 5 维评审 `design-critic`）；可访问性问题（用 `a11y-audit`）。

**Implementation sketch**:
- references: `refactoring-ui-principles.md`（21 条 Adam Wathan + Steve Schoger 原则），`spacing-systems.md`, `shadow-elevation.md`
- templates: `audit-report.html`（按 4 维分组的检查清单）
- scripts: `audit-screenshot.mjs`（接 Playwright 截图 + 标注）

---

### 12. `multi-heuristic-audit` 🔁 原文 #10 扩展 P0

**Purpose**: 用 **三套启发式**（Nielsen 10 + Shneiderman 8 Golden Rules + ISO 9241-110）审计可用性，每条违反给严重度（Cosmetic / Minor / Major / Catastrophic）。

**Trigger keywords**: `usability audit / 启发式评审 / Nielsen / heuristic review / 可用性问题`

**When NOT to use**: 视觉问题（用 `refactoring-ui-audit`）；可访问性（用 `a11y-audit`）。

**Implementation sketch**:
- references: `nielsen-10.md`, `shneiderman-8.md`, `iso-9241-110.md`, `severity-scoring.md`
- templates: `heuristic-audit-report.html`（按 18 条原则的违反清单）

---

### 13. `a11y-audit` 🆕 **P0** 🔥

**Purpose**: WCAG 2.2 AA 全维度审计：色彩对比、ARIA 完整度、键盘导航、屏幕阅读器叙事、focus order、动效尊重 `prefers-reduced-motion`。每条违反给优先级 + 修复建议。

**Trigger keywords**: `a11y / accessibility / WCAG / 无障碍 / 残障可达 / screen reader / 屏幕阅读器 / 色彩对比`

**When NOT to use**: 仅想做色彩对比检查（用 `design-tokens-generator` 内置的 contrast checker）。

**Implementation sketch**:
- references: `wcag-22-aa-checklist.md`（50 条具体准则）, `aria-patterns.md`（按组件类型）, `screen-reader-stories.md`（VoiceOver / NVDA / TalkBack 实测脚本）
- templates: `a11y-audit-report.html`（按 4 大类——Perceivable / Operable / Understandable / Robust）
- scripts: `axe-integration.mjs`（Playwright + axe-core），`contrast-checker.mjs`

**Why P0**: 你 repo 里完全没有 a11y 专项 skill——这是企业 / 政府客户的 **must-have**。

---

### 14. `microcopy-polish` 🆕 P1

**Purpose**: UX writing 全篇过一遍——按钮文案、错误提示、空状态文字、tooltip、placeholder、loading 短语——用品牌语调一致化（Friendly / Formal / Playful / Authoritative）。

**Trigger keywords**: `microcopy / UX writing / 文案修改 / 错误提示文案 / 按钮文案 / tone of voice`

**When NOT to use**: marketing 长文案（找文案 skill，不是这个）；纯翻译（用 translation skill）。

**Implementation sketch**:
- references: `voice-tone-matrix.md`（4 tone × 5 emotion = 20 voice profiles），`error-message-patterns.md`（避免 "Error 500" 风），`button-microcopy.md`
- templates: `microcopy-audit.html`（按位置分组）
- scripts: `extract-strings.mjs`（从 HTML 抽出所有 user-visible text）

---

## Phase 5 · Platform & Adapt（2 skills）

### 15. `platform-adaptation` 🔁 原文 #11 扩展 P2

**Purpose**: 同一份设计，按 4 端规范输出差异版本：**iOS HIG / Material 3 / Fluent 2 / GNOME HIG**。每端给出 navigation / typography / spacing / motion 的差异点。

**Trigger keywords**: `iOS HIG / Material 3 / Fluent / 跨平台 / cross-platform / platform-specific`

**When NOT to use**: 单平台 web（用 `ui-component-library`）；只需 native 截图（用 `wireframe-to-hifi` + 设备外壳）。

**Implementation sketch**:
- references: `ios-hig-distilled.md`, `material-3-distilled.md`, `fluent-2-distilled.md`, `gnome-hig-distilled.md`
- templates: `cross-platform-comparison.html`（4 列对照）
- scripts: `adapt-spacing.mjs`（按平台 base unit 换算）

---

### 16. `responsive-foldability` 🆕 P0

**Purpose**: 单一设计 → desktop / tablet / phone / fold / watch / TV 6 端 reflow 规则。含 breakpoint 表 + 内容优先级降级路径 + 折叠屏 dual-screen 提示。

**Trigger keywords**: `响应式 / responsive / 多端适配 / fold / 折叠屏 / breakpoint / mobile-first / 适配多屏`

**When NOT to use**: 已用 `ui-component-library`（已内置 responsive）；纯 desktop-only 工具。

**Implementation sketch**:
- references: `breakpoint-systems.md`（Tailwind / Material / Bootstrap 对比）, `content-priority-degradation.md`, `foldable-patterns.md`（Samsung Galaxy Fold / Surface Duo）
- templates: `responsive-preview.html`（含 5 端 viewport 切换器）
- scripts: `simulate-foldback.mjs`

**Why P0**: 原文章完全没提响应式——这是 web 设计 ABC。

---

## Phase 6 · State & Interaction Library（1 skill）

### 17. `states-library` 🆕 P1

**Purpose**: 给定核心组件（Page / List / Table / Form / Chart），生成完整状态库——**Empty / Loading / Error / Partial data / Unauthenticated / Disabled / Locked**，每个状态含 illustration + microcopy + CTA。

**Trigger keywords**: `empty state / loading state / error state / 空状态 / 加载状态 / 错误状态 / 状态库`

**When NOT to use**: 只缺一个 empty state（直接让 Claude 画一个）。

**Implementation sketch**:
- references: `state-priority-matrix.md`（哪些状态对哪类组件强制）, `illustration-patterns.md`（避免 Corporate Memphis）, `state-microcopy.md`
- templates: `state-set-page.html`, `state-set-list.html`, `state-set-table.html`, `state-set-form.html`, `state-set-chart.html`
- scripts: `gen-state-pack.mjs`

---

## Phase 7 · Meta（1 skill）

### 18. `ui-ux-skill-creator` 🔁 原文 #18 P2

**Purpose**: meta-skill——把一个品牌 / 设计系统 / 客户视觉规范蒸馏成一个**新的 Claude Code skill**。输入是设计系统文档 + 几张样例截图，输出是完整的 `.claude/skills/<brand>/` 包。

**Trigger keywords**: `create skill / 蒸馏 skill / 把这套设计系统做成 skill / brand-to-skill / skill scaffolding`

**When NOT to use**: 改现有 skill（直接编辑文件）；通用 skill 创建（用 Claude Code 内置 `/skill-create`）。

**Implementation sketch**:
- references: `skill-anatomy.md`（SKILL.md frontmatter + references/ + templates/ + scripts/ 必备结构）, `frontmatter-protocol.md`（trigger keyword 起怎样的名才被 Claude 命中），`extraction-protocol.md`（从设计文档提取规则的提示模板）
- templates: `skill-skeleton/`（完整空 skill 骨架）
- scripts: `extract-from-design-system.mjs`, `validate-skill-structure.mjs`

---

## 18 款汇总表（优先级 + 来源）

| # | Phase | Skill | 优先级 | 来源 | 一句话定位 |
|---|---|---|---|---|---|
| 1 | Discover | `ux-research-synthesizer` | P1 | 🆕 | 访谈 → personas + JTBD |
| 2 | Discover | `design-sprint-facilitator` | P2 | 🔁 #13 | GV 5-day sprint 编排 |
| 3 | Discover | `info-architect` | P1 | 🆕 | 功能列表 → sitemap |
| 4 | Define | `prd-to-mockup` | **P0** 🔥 | 🆕 | PRD → 低保真 wireframe |
| 5 | Define | `design-tokens-generator` | **P0** | 🆕（合并原文弱预设） | 品牌输入 → 完整 tokens |
| 6 | Define | `user-flow-mapper` | P1 | 🆕 | 用户故事 → flow + 状态机 |
| 7 | Ideate | `design-direction-explorer` | P1 | 🆕（合并 5 个 Visual 类） | 3 方向并列对比 |
| 8 | Ideate | `ui-component-library` | P1 | 🆕 | 完整 UI kit（22 组件 × 3 框架） |
| 9 | Ideate | `wireframe-to-hifi` | P1 | 🆕 | 低保真 → 高保真 mockup |
| 10 | Ideate | `prototype-interaction-flow` | P1 | 🆕 | 多页可点击交互原型 |
| 11 | Critique | `refactoring-ui-audit` | **P0** | 🔁 #9 | 视觉层级 / 间距 / 阴影审计 |
| 12 | Critique | `multi-heuristic-audit` | **P0** | 🔁 #10 扩展 | Nielsen+Shneiderman+ISO 9241 |
| 13 | Critique | `a11y-audit` | **P0** 🔥 | 🆕 | WCAG 2.2 AA 全维度 |
| 14 | Critique | `microcopy-polish` | P1 | 🆕 | UX writing 一致化 |
| 15 | Adapt | `platform-adaptation` | P2 | 🔁 #11 扩展 | iOS+Material+Fluent+GNOME |
| 16 | Adapt | `responsive-foldability` | **P0** | 🆕 | 6 端 reflow 规则 |
| 17 | State Lib | `states-library` | P1 | 🆕 | Empty/Loading/Error 全状态 |
| 18 | Meta | `ui-ux-skill-creator` | P2 | 🔁 #18 | 设计系统 → skill 蒸馏器 |

**P0（6 个）**: 建议先实现——填了你 repo 上下文中的关键缺口（PRD-to-mockup、tokens、refactoring audit、heuristics、a11y、responsive）

**P1（9 个）**: 第二批——研究、信息架构、组件库、状态库等等

**P2（3 个）**: 第三批——sprint、platform、meta-skill creator（这些更"独立工具"，先有前两批的语境再做更顺）

---

## 与 v0.3 已发布 skill 的关系

| 已有 skill | ui-ux-skills 的互补点 |
|---|---|
| `biz-decision-stack` | UI/UX skill 不做决策类报告；当 a11y/heuristic 审计要交付给 stakeholder 时，可以走 biz-decision 的 design-critique HTML |
| `viz-deck` | viz-deck 的 prototype 模式（mode 2）是**单页**高保真；新 `prototype-interaction-flow` 是**多页**交互流。不冲突，互补。 |
| `viz-charts` | 新 `user-flow-mapper` 和 `info-architect` 直接调用 viz-charts 的 mermaid 渲染。 |

**总指导原则**：ui-ux-skills 不重复 v0.3 任何一个 skill 的能力——只填覆盖空白。

---

## 下一步

1. 浏览 `catalog.html` 看美化版（同样内容，深空主题 + 卡片视图）
2. 从 6 个 P0 里挑你最想要的 2-4 个，告诉我哪几个
3. 我按 v0.3 标准实现选中的 skill：`SKILL.md` + `references/*.md` + `templates/*.html` + `scripts/*.mjs` + `samples/` 全套
4. 实现完整可独立装 zip，加入双 harness 矩阵（claude-code-skills + codex-skills）

---

<sub>v0.4 design proposal · 2026-05-13 · 不是发布，是提案 · Apache 2.0</sub>
