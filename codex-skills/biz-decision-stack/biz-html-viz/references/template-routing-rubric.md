# template-routing-rubric: 模板路由打分宪法

> v2.1 新增。`template-router` subagent 的评分依据。受 mckinsey-pptx subagent 启发：让 AI **既挑模板，又为自己的选择辩护**。

## 5 维评分卡

每个模板按以下 5 维 0-5 分，加权求和（满分 50）。

### 维度 1：受众匹配（权重 ×3）

> 用户提到的"看的人"匹配该模板的设计受众吗？

| 用户提到 | board-brief | ceo-canvas | tech-roadmap | mrd-report | project-board | dev-report | retro-report | design-critique |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| 股东 / 董事会 / LP / 投资人 | 5 | 3 | 1 | 2 | 0 | 0 | 1 | 0 |
| CEO / 创始人 / 战略合伙人 | 4 | 5 | 2 | 3 | 1 | 0 | 2 | 0 |
| 架构师 / CTO / 技术 lead | 1 | 2 | 5 | 1 | 2 | 4 | 2 | 1 |
| PM / 产品经理 / 业务方 | 2 | 3 | 2 | 5 | 5 | 1 | 3 | 1 |
| 开发 / QA / 工程团队 | 0 | 0 | 3 | 0 | 4 | 5 | 3 | 0 |
| 设计 / UX / 创意 lead | 0 | 0 | 0 | 1 | 1 | 0 | 1 | 5 |
| 老板（含混代指） | 4 | 4 | 2 | 3 | 3 | 2 | 3 | 1 |
| 客户 / 合作方 | 3 | 2 | 1 | 2 | 2 | 0 | 1 | 0 |

含糊"老板"→ 看上下文再判定 board / CEO / PM。

### 维度 2：决策类型（权重 ×3）

> 用户的真实意图是哪一种？

| 用户表达 | 适配模板 |
|---|---|
| "要做决策"、"go/no-go"、"批准/拒绝"、"签字" | board-brief（董事会决议） / ceo-canvas（CEO 取舍） |
| "汇报进展"、"现在到哪了"、"状态" | project-board / dev-report |
| "做战略 / 选方向 / 三选一" | ceo-canvas |
| "做市场 / 客户 / 竞品分析" | mrd-report |
| "讲架构 / 选技术栈 / 给方案" | tech-roadmap |
| "复盘 / 总结 / lessons / 验收" | retro-report |
| "评一下设计 / 出片质量 / 好不好看" | design-critique |
| "项目报告"（含混） | 看时间节点：建设中 → project-board；结束 → retro-report |

### 维度 3：时间节点（权重 ×2）

> 项目当前阶段决定哪些模板"合时令"。

| 阶段 | 当行模板 | 不适合 |
|---|---|---|
| 创意阶段（idea / proposal） | mrd-report, board-brief, ceo-canvas | dev-report, retro |
| 规划阶段（spec / design） | tech-roadmap, mrd-report, project-board | dev-report, retro |
| 建设阶段（build / sprint） | project-board, dev-report | retro |
| 上线阶段（launch / rollout） | board-brief, dev-report, project-board | mrd-report（已过期） |
| 结束阶段（post-launch / shutdown） | retro-report, board-brief | mrd-report, project-board |

匹配 = 5；相邻阶段 = 3；不合时令 = 0。

### 维度 4：信息密度暗示（权重 ×1）

> 用户对报告体量的表达。

| 表达 | 偏好密度 | 适配模板 |
|---|---|---|
| "一页纸"、"5 分钟"、"高度概括" | 低 | board-brief, ceo-canvas, design-critique |
| "详细"、"深度"、"全面" | 高 | tech-roadmap, mrd-report, dev-report |
| "看板"、"卡片"、"快速浏览" | 中 | project-board |

匹配 = 5；中性 = 3；冲突 = 0。

### 维度 5：触发关键词（权重 ×1）

> 是否出现该模板典型 jargon？

| 模板 | 强信号词 |
|---|---|
| board-brief | board / 董事会 / 股东 / LP / fundraising / runway / 投资简报 |
| ceo-canvas | 战略 / 取舍 / bet / 优先级 / OKR / 资源分配 / pivot |
| tech-roadmap | 架构 / ADR / tech stack / 技术选型 / 风险登记 / SLA / SLO |
| mrd-report | MRD / persona / 市场 / TAM / 竞品 / 用户画像 / journey |
| project-board | 看板 / kanban / sprint / 燃尽 / WIP / 阻塞 / 进度 |
| dev-report | bug / coverage / build / release / CI / regression / hotfix |
| retro-report | retro / 复盘 / 验收 / lessons / KPI 达成 / 改进 |
| design-critique | 评审 / critique / 出片 / 视觉 / 5 维 / 哲学一致性 |

出现 ≥ 2 个 → 5；出现 1 个 → 3；不出现 → 1。

## 总分阈值

| 总分（满分 50） | 处理 |
|:---:|---|
| 35-50 | 强匹配 → 直接路由 + 写辩护 |
| 20-34 | 中匹配 → 检查 runner-up |
| < 20 | 弱匹配 → 让用户裁决 / 推荐组合 |

## 双模板冲突处理

若 top-1 和 top-2 分数差 < 3：

1. 列出两个模板的"best for"和"trade-off"各一行
2. 提交用户选择
3. **不要**自作主张选 top-1（差距小说明信息不够）

## 辩护文写法

辩护放在生成的 HTML **第一个注释块**里（不显示给读者，但留给下次 Claude 看到）。格式：

```html
<!--
  ROUTED BY template-router · 2026-05-16
  Picked: ceo-canvas (score 41/50, runner-up: board-brief at 35)
  Why: User mentioned "我要选三个 bet 之一" — pure prioritization signal,
       weight ×3 on 决策类型. Audience "全员" tilted CEO over board.
       Timing: mid-sprint, no quarter close — CEO canvas fits.
-->
```

## 反模式

- ❌ 5 个维度都打满分（说明评分没在思考）
- ❌ 自动跑而不输出 ROUTING DECISION 块（沉默路由 = 失职）
- ❌ 让用户每次都裁决（弱化路由价值，本该自主时被动）
- ❌ 不读用户上下文就打分（路由必须基于真实输入，不是猜）
