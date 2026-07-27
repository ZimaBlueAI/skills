# Template Router · 三个真实路由案例

> v0.4 新增 `template-router` subagent（mckinsey-pptx lineage）。本文件展示 3 个用户含混请求 → 路由器打分 + 辩护 → 最终生成 HTML 的完整路径。

---

## Case 1：含混请求 → 强匹配（直接路由）

### 用户输入

> "帮我做个 deck 给老板看，下周一汇报。我们 Q3 跑得不错，超了 14% 的 KPI。"

### 路由器打分

| 模板 | 受众×3 | 决策×3 | 时间×2 | 密度×1 | 关键词×1 | 总分 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| board-brief | 4 | 3 | 3 | 4 | 1 | **38** |
| ceo-canvas | 4 | 2 | 3 | 4 | 1 | 32 |
| **project-board** | 3 | 5 | 5 | 4 | 4 | **47** ← |
| dev-report | 2 | 4 | 5 | 4 | 1 | 28 |
| retro-report | 3 | 1 | 1 | 4 | 0 | 19 |

### 路由器输出（呈现给用户）

```
ROUTING DECISION

  Template ▸ project-board
  Score    ▸ 47 / 50   (runner-up: board-brief at 38)

WHY

  · 受众"老板"+ 上下文"汇报进展" → 偏 PM 受众，权重 ×3
  · 决策类型 = "汇报状态"而非"求决策" → project-board.html 是状态卡片，权重 ×3
  · 时间节点 = 季度中，没说要做季度收尾 → 当行 project-board
  · 触发关键词 "Q3 进展 / KPI / 超 14%" 全是 project-board 的强信号

NEXT

  生成 project-board.html — 数据缺什么？需要补：
  · sprint 编号 / 当前 WIP 数量 / 阻塞清单
```

### 生成的 HTML 头部注释

`{date}-project-board-q3-progress.html` 顶部自动写入：

```html
<!--
  ROUTED BY template-router · 2026-05-16
  Picked: project-board (score 47/50, runner-up: board-brief at 38)
  Why: User mentioned "做个 deck 给老板" + "Q3 跑得不错" + "超了 14%" — pure
       progress reporting signal, not a decision ask. project-board layout is
       optimized for kanban + KPI scan; board-brief would force a verdict that
       the user didn't ask for.
-->
```

---

## Case 2：双候选冲突（让用户裁决）

### 用户输入

> "给董事会做一份东西，我们要批 1200 万美元 B 轮，但同时也要解释为什么选 A 不选 C。"

### 路由器打分

| 模板 | 总分 |
|---|:---:|
| **board-brief** | **43** |
| **ceo-canvas** | **41** |
| mrd-report | 22 |

board-brief vs ceo-canvas 仅差 2 分 → **触发用户裁决**（差距 < 3）。

### 路由器输出

```
TWO CANDIDATES — please pick:

  A) board-brief  (43/50)
     · best for: 董事会签字的融资决议 — verdict + 资金用途 + 风险
     · trade-off: 战略取舍论证空间不如 ceo-canvas

  B) ceo-canvas  (41/50)
     · best for: "为什么选 A 不选 C" 的战略辩护 — bet 矩阵 + 资源分配
     · trade-off: 没有 verdict 签字栏，董事会还得自己整理结论

Your call:
```

### 用户回复 "A"

→ 生成 board-brief.html，但在第二屏插入 `<section class="bet-matrix">` 把 A/C 对比纳入。**双候选不浪费**：router 保留两个洞察，落进最终产物。

```html
<!--
  ROUTED BY template-router · 2026-05-16
  Picked: board-brief (user override; A=43/50, B=41/50)
  Why: Top-1 and Top-2 were within 3 points. User chose A for the verdict
       structure. Added a bet-matrix section borrowing ceo-canvas's
       comparison layout — best of both.
-->
```

---

## Case 3：明确路由（**不**触发路由器）

### 用户输入

> "我要做 retro。这个 sprint 跑完了，做个 retro 报告。"

### 路由器决策

**不启动**。用户已明确说 "retro"，路由器不应介入——直接走 retro-report.html。

```
(template-router skipped — user explicitly named the template)
NEXT ▸ retro-report.html
```

这是路由器的**收敛规则**：明确就让路。沉默路由不是要 always-on，是要 only-when-helpful。

---

## 三个案例的设计哲学

1. **不沉默**：每次路由都输出 ROUTING DECISION 块，不偷偷选
2. **不投机**：分数差 < 3 让用户裁决，不强行二选一
3. **不越权**：用户明确指定了模板就让路，不为了"显得智能"而干预
4. **可追溯**：辩护文写进 HTML 注释头，下次 Claude 打开也能看到当初的判断

灵感来自 mckinsey-pptx subagent —— "AI 不仅做决策，还要为决策辩护"。在咨询场景下，能解释自己选择的工具，比沉默选择的工具更值得信任。

## 与 all-hands-orchestrator 的边界

| 触发 | 走哪个 |
|---|---|
| "走一遍全流程 / 一键全套" | all-hands-orchestrator（生成 7 份） |
| "做个 deck 给老板" / "做个汇报" | template-router（选 1 份） |
| "做 board brief 就够了" | 直接走 biz-html-viz，不用路由 |
