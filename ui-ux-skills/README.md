# ui-ux-skills · v0.4 设计提案

> **这是设计提案，尚未实现。** 与 v0.3 已发布的 biz-decision-stack / viz-deck / viz-charts **互补**，不替代。

---

## TL;DR

18 款 UI/UX skill 的精选目录，按 7 个设计阶段排列。基于 [Pasquale Pillitteri 的 18 款推荐](https://pasqualepillitteri.it/zh/news/889/claude-code-18-zuijia-skill-ui-ux-sheji-zhinan) 做了**有见解的取舍**：

- **保留** 5 条原文条目（其中 3 条做了扩展）
- **删除** 10 条因重叠 / 过窄 / 非 skill 范畴的条目
- **新增** 13 条填补 repo 关键空白（特别是 a11y、PRD→mockup、responsive、states library 等原文章完全没碰的维度）

---

## 浏览方式

| 文件 | 用途 |
|---|---|
| [`catalog.html`](./catalog.html) | **主要交付物** · 深空主题视觉化目录，含 18 张卡片 + 汇总表 + 下一步行动 |
| [`catalog.md`](./catalog.md) | 同内容的 markdown 版本——给 git diff / 代码 review / 复制粘贴用 |
| `README.md` | 本文件——索引页 |

> `catalog.html` 是 viz-deck 深空风（cyan/blue/gold 配色 + Inter typography + 微动效），与仓库其它 HTML 报告视觉一致。

---

## 6 个 P0 优先建议

| # | Skill | 为什么先做 |
|---|---|---|
| 04 | `prd-to-mockup` 🔥 | PRD → 低保真 wireframe，**产品 / 设计协作的真实断层**——v0.3 viz-deck prototype 从 hi-fi 起步 |
| 05 | `design-tokens-generator` | 品牌输入 → 完整 tokens（颜色 / 字号 / 间距），合并了原文章 3 个弱预设 |
| 11 | `refactoring-ui-audit` | 视觉细节审计——Refactoring UI 框架（hierarchy / spacing / shadow / color） |
| 12 | `multi-heuristic-audit` | Nielsen + Shneiderman + ISO 9241 三套启发式合并审计 |
| 13 | `a11y-audit` 🔥 | WCAG 2.2 AA 全维度——**企业 / 政府客户的 must-have**，repo 完全没有 |
| 16 | `responsive-foldability` 🔥 | desktop / tablet / phone / fold / watch / TV 6 端 reflow——**原文章完全没提响应式** |

🔥 = 特别重要 / 不可或缺。

---

## 与现有 skill 的关系

```
┌────────────────────────────────────────────────────────────────────┐
│                    v0.3 已发布                                       │
│  biz-decision-stack  ·  viz-deck  ·  viz-charts                    │
│  (决策链 HTML/PPTX)  ·  (5 模产出)  ·  (图表 + 3D KG)               │
└────────────────────────────────────────────────────────────────────┘
                              ↓ 互补 ↓
┌────────────────────────────────────────────────────────────────────┐
│                    v0.4 提案（本目录）                                │
│  ui-ux-skills · 18 款覆盖 7 个设计阶段                              │
│  Discover → Define → Ideate → Critique → Adapt → State → Meta      │
└────────────────────────────────────────────────────────────────────┘
```

**总指导原则**：ui-ux-skills 不重复 v0.3 任何一个 skill 的能力——只填覆盖空白。

---

## 推荐组合（选其一开搞）

**组合 A · 设计前置打通**（解决"从想法到能演示的原型"这条路）

```
prd-to-mockup → design-tokens-generator → responsive-foldability
```

**组合 B · 设计审计三件套**（直接产生 value，不依赖前置链）

```
refactoring-ui-audit + multi-heuristic-audit + a11y-audit
```

各自实现完整后可走 v0.3 标准发布流程——`SKILL.md` + `references/*.md` + `templates/*.html` + `scripts/*.mjs` + `samples/` + 双 harness（Claude + Codex）zip。

---

## 下一步

打开 `catalog.html` 在浏览器里浏览（同 `skills-install-guide.html` 设计语言）→ 告诉我挑哪个组合 / 哪几个 skill → 我按 v0.3 工程标准实现 → 进入 v0.4 release。

---

<sub>v0.4 design proposal · 2026-05-13 · Apache 2.0</sub>
