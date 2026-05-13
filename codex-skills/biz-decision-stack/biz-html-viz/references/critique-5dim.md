# critique-5dim: 5 维设计评审（决策报告版）

> v2 新增。给 7 份决策报告做"出片质量"把关。规则原文在 `~/.claude/skills/huashu-design/references/critique-guide.md`，本文件做的是**终端风（biz-html-viz）的适配**。

## 5 维一句话

| # | 维度 | 一句话（终端风视角） |
|---|---|---|
| 1 | **哲学一致性** | 是否遵循终端风设计系统（黑底 / 酸黄 / 等宽 / 零动效）？混搭 deck 主题或加渐变 = 扣 |
| 2 | **视觉层级** | h1（serif）/ section（mono uppercase）/ data（mono）三档对比是否足够 |
| 3 | **细节执行** | meta 4 项齐全 / 数字单位一致 / 章节间横线对齐 / 占位符全部替换 |
| 4 | **功能性** | 每段是否服务决策——空章节、客套话、"以下是一些建议..."一律 -2 分 |
| 5 | **创新性** | 终端风**不鼓励炫技**——本维只检查是否避免了 cliché（紫渐变 / emoji 装饰 / 圆角 > 2px） |

## 与 viz-deck 5 维评审的区别

| 维度 | viz-deck 评审 | biz-html-viz 评审 |
|---|---|---|
| 哲学一致性 | 是否符合所选 20 哲学之一 | 是否符合**唯一的**终端风设计系统 |
| 视觉层级 | 标题字号比、对比度 WCAG AA | 三档字体（serif/mono/uppercase mono）分工 |
| 细节执行 | 8pt 网格、配色限定 | 占位符 / meta 4 项 / 横线对齐 / 责任人格式 |
| 功能性 | 元素删了变差吗 | 每段服务决策吗、有结论句吗、数字优先吗 |
| 创新性 | 是否避免 AI cliché 且有个人表达 | **只看反 cliché**，不鼓励个人表达 |

## 何时触发

| 场景 | 自动触发 |
|---|:---:|
| 用户在 orchestrator 流程末尾问"质量怎么样" | ✅ |
| 7 份报告中的任意一份首次生成完成 | ⚠️ 默认不弹；如果用户在过去 3 轮内有"再改改"信号则触发 |
| design-critic subagent 被显式召唤 | ✅ |
| 用户问"评一下这份 board-brief" | ✅ |

## 检查清单（先自评，再决定是否呈现）

每份决策报告产出后，按下表自评。任意一项扣到 6 分以下 → 必须返工。

### 1. 哲学一致性

```bash
# 自动检查：模板里不应出现的视觉关键词
grep -E "linear-gradient|backdrop-filter|emoji|border-radius:\s*[3-9]" report.html
# 应该 0 命中
```

人工检查：

- [ ] 配色只用 `#0a0a0a` / `#d4ff00` / 灰阶（design-system.md 限定）
- [ ] 字体只用 Newsreader / Inter Tight / JetBrains Mono
- [ ] 章节标题 mono uppercase（不是大字号 sans）
- [ ] 数据用 mono（不是 sans）
- [ ] 横线分隔 > 卡片分隔

### 2. 视觉层级

| 元素 | 字号比 | 客观红线 |
|---|---|---|
| h1（serif） vs body（sans） | ≥ 2.5× | < 2 倍 = ≤ 6 分 |
| section title（mono uppercase）vs body | ≥ 1.2× + letter-spacing 0.1em+ | 漏 letter-spacing = -1 分 |
| 重要数字（mono）vs body | ≥ 1.5× | < 1.2 倍 = ≤ 7 分 |

### 3. 细节执行

- [ ] meta 4 项齐全（TYPE / DATE / AUTHOR / VERSION）
- [ ] 所有 `{{占位符}}` 已替换
- [ ] 数字单位一致（不要 1.2M + 1,200k 混用）
- [ ] 估值标 `[ESTIMATED]`，缺失标 `[N/A]`，**没有捏造**
- [ ] 责任人格式统一（`@person · YYYY-MM-DD`）
- [ ] 文件名格式 `{date}-{type}-{slug}.html`

### 4. 功能性

- [ ] 每段不超过 3 句
- [ ] 每章节有结论句（顶部 或 `<blockquote>`）
- [ ] 没有"以下是一些建议..."这类引导废话
- [ ] 没有"暂无"/"待补充"空章节
- [ ] 数字比形容词多（"显著" → "+47%"）
- [ ] 每条风险/决议都有责任人 + 截止日

### 5. 创新性（反 cliché）

- [ ] 没有紫色渐变
- [ ] 没有玻璃拟态
- [ ] 没有 emoji 装饰（数据值里的 ↑↓ 例外）
- [ ] 没有圆角 > 2px
- [ ] 没有 keyframe 动画
- [ ] 没有"⭐重要"这类装饰符号

## 评审输出（用 design-critique.html 模板）

`templates/design-critique.html` 是终端风的评审报告模板——把 5 维评分 + Keep/Fix/Quick Wins 直接渲染成黑底酸黄等宽。

调用流程：

1. 自评填 scores.json（结构同 huashu critique-guide.md 标准格式）
2. 复制 `templates/design-critique.html`
3. 替换 `{{占位符}}` 写入评分、雷达、修复清单
4. 文件名：`{date}-critique-{slug}.html`

## 反模式

- ❌ 评审报告本身**用 deck 主题**——评决策报告必须沿用终端风
- ❌ 给"主观品味"打分（"觉得不够大气"）——只评 5 维客观项
- ❌ 5 项中给出 10 分——10 分留给真"无可挑剔"的产出
- ❌ Quick Wins 列 > 3 条——挑最影响力的 3 条
- ❌ 评审不写理由，只给分数——每项必须 1 句话说明
