---
name: taste-engine
description: A shared "taste layer" for HTML/PPT deliverables — three tunable dials (DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY) plus an anti-slop preflight and material/copy rules that elevate color, layout, motion, sourcing and wording. Not a renderer; a small set of design tokens and constraints applied on top of any generated page or deck. Use when the user asks to make output "更有口味 / 更高级 / less AI-slop / 调风格档位 / 加动效但要克制 / 选材与文案更讲究", or when a sister deliverable (web report, slide deck, chart, knowledge graph) needs a consistent, tasteful finish. Ships a worked web demo (dark cinematic, live dials, animation + chart + 3D/ring/Circos KG) and a worked deck demo (warm-paper editorial, speaker mode).
---

# Taste Engine — the shared taste layer

A deliverable is "有口味" when its **color, layout, motion, material and copy** all pull
in the same direction and nothing is generic. This module encodes that as three things
you can apply on top of any HTML page or deck:

1. **Three dials** — `DESIGN_VARIANCE` · `MOTION_INTENSITY` · `VISUAL_DENSITY`, set on
   `<html data-variance data-motion data-density>` and read by both CSS and JS.
2. **Anti-slop preflight** — a kill-list you run before shipping.
3. **Material & copy rules** — how to source assets and write words that don't read as AI.

It is **not** a renderer and **not** a dependency. It is a set of tokens and constraints.
Apply it; it does not run anything.

---

## 1. The three dials

| Dial | 0 | 1 | 2 |
|---|---|---|---|
| **DESIGN_VARIANCE** | 居中 · 对称 · 安全栅格 | 非对称黄金分割 · 错位标题 | 编辑式破格 · 对角流向 · 超大字 |
| **MOTION_INTENSITY** | 静止（reduced-motion） | 入场揭示 · 数字滚动 · 条形填充 | 滚动视差 · 弹簧物理 · 3D 漂移 · 流动渐变 |
| **VISUAL_DENSITY** | 一屏一念 · 大留白 | Bento 平衡 | 仪表盘密度 · 多面板 · 紧行距 |

Each dial maps to concrete CSS tokens (`--pad`, `--gap`, `--type-scale`, `--reveal`) and
behavior flags. Full token table + the copy-paste CSS/JS recipe: `references/taste-dials.md`.

### Per-deliverable defaults

Taste is **added, not imposed** — start each deliverable at its house default so existing
identities are preserved, then tune.

| 交付物 | variance / motion / density | 说明 |
|---|---|---|
| 终端决策报告 | `0 / 0 / 1` | 守零动效扫读，密度偏高 |
| 现场讲演 deck | `1 / 1 / 1` | 克制入场动效，编辑式留白 |
| keynote / 发布 | `2 / 2 / 1` | 出片优先，电影感动效 |
| 落地 / hero | `2 / 2 / 0` | 一屏一念 + 满级动效 |

---

## 2. Workflow

```
选默认档（按交付物） → 写 data-variance/motion/density 到 <html>
  → 套 references/taste-dials.md 的 token 配方
  → 内容用 references/material-and-copy.md 的选材/文案规则
  → 交付前跑 references/anti-slop-preflight.md 清单
  → ship
```

A live dial implementation (three sliders that re-theme a whole page in real time) is in
the web demo below — copy its `applyMotion()` / attribute-selector pattern.

---

## 3. Worked demos

`demo/taste-demo.html` — **dark cinematic** web report, single file, CDN-only:
- live three-dial panel re-theming the page
- scroll-driven entrance + parallax (gated by the motion dial)
- charts (radar + stacked growth)
- three knowledge-graph forms: **3D force-directed**, **SVG 环形 Context Graph**
  (拖拽 / 滚轮缩放 / 拖背景平移 / 点节点 BFS / 搜索), and **Circos 弦图**
  (ideogram + 外圈 track + 内部 ribbon，可悬停高亮)

`demo/zima-ppt-demo.html` — **warm-paper editorial deck**, single file:
- tri-color bar, hairline cards, tabular-nums metrics, per-slide 超时计时条
- **speaker mode (按 S)** — separate window with 逐字稿 / 下一页 / 计时 / 议程, postMessage-synced
- export-ready as the input态 for HTML→MP4/GIF and HTML→可编辑 PPTX pipelines

Both are the canonical reference for "what tasteful looks like" in this repo.

---

## 4. References

- `references/taste-dials.md` — the three dials → token/behavior mapping + CSS/JS recipe
- `references/anti-slop-preflight.md` — the pre-ship kill-list（含 zima-design（anti-slop 引擎）六大纪律硬闸）
- `references/material-and-copy.md` — 选材 + 文案 taste rules

## 5. zima-design bridge — 升级到全量设计合奏

本层的 preflight 是**轻量 kill-list**；当交付物是对外页面（落地页 / 官网 / 作品集），
或用户要求「彻底反 AI 味 / audit / redesign」时，升级到姊妹 skill
**zima-design**（本仓库自有设计合奏引擎，其 anti-slop 引擎源自 [nutlope/hallmark](https://github.com/nutlope/hallmark)，MIT）：

- `zima-design/engines/anti-slop/references/slop-test.md` — 57 条验收关卡，逐条过闸；
- `zima-design/engines/anti-slop/references/anti-patterns.md` — 反模式全清单（编造指标 / 假 chrome / 斜体标题…）；
- `zima-design/engines/anti-slop/references/structure.md` + `macrostructures/` — 结构多样性：21 种页面宏结构轮换。

分工：**taste-engine 管「已有产出的口味档位」**（dial + 预检，轻叠加）；
**zima-design 管「从零设计的完整合奏」**（宏结构选型 → 主题路由 → slop-test）。
两者同向不冲突：其六大纪律已蒸馏进本层 `anti-slop-preflight.md`。

## 参考（可选搭配）

This layer is self-contained. It composes naturally with this repo's generation skills —
apply it on top of a **现场讲演 deck**, a **keynote / 图表 / 知识图谱** deliverable, or a
**终端决策报告** to give each a consistent, tasteful finish. None of them are required to
use the dials.
