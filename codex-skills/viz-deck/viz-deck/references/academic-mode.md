# academic-mode: 学术报告 / 会议演讲专用协议

> v2.1 新增。viz-deck 模式 1（keynote-report）第 4 个子模板，灵感来自 academic-pptx-skill（387 Star）。强制 **action title + 引用规范 + Q&A 页**，把学术演讲的套路代码化。

## 何时启用

| 用户场景 | 触发 |
|---|:---:|
| 学术会议 / 研讨会 / 论坛主题演讲 | ✅ |
| 论文答辩 / 开题 / 期中 / 终期 | ✅ |
| 基金/课题汇报、研究简报 | ✅ |
| 投资人路演 / 产品发布 | ❌ 用 stage-report.html |
| 技术架构评审 | ❌ 用 architecture-deep.html |
| 政府工作汇报 | ❌ 用 stage-report.html（学术模式过于"学者"） |

## 与其他模板的区别

| 维度 | stage-report | architecture-deep | competitive-landscape | **academic-talk** |
|---|---|---|---|---|
| 标题语法 | 名词短语可 | 名词短语可 | 名词短语可 | **必须完整句子** |
| 引用规范 | 可选 | ADR 引用 | 必带 source | **强制 numbered references** |
| 结尾页 | takeaway | 实施路线 | 评分矩阵 | **anticipated Q&A** |
| 图表称谓 | "Figure" | "Diagram" | "Matrix" | **"Exhibit"** |
| 字体 | sans-serif 优先 | sans-serif | sans-serif | **serif（Newsreader）优先** |

## 核心规则 1：Action Title

**学术 PPT 与商业 PPT 最大区别**：

```
❌ Bad (noun phrase):
   "Market Analysis"
   "Technical Approach"
   "Results"

✅ Good (full sentence, verb-driven):
   "The agent market doubled in 2026, but ARPU stayed flat"
   "We test the alignment hypothesis via three controlled experiments"
   "Latency drops 47% under our caching layer; cost rises 8%"
```

每个 `<h2 class="action-title">` 必须是**一个完整句子**：主语 + 动词 + 受词。**不允许只用名词短语**。

**自检方法**：把 action-title 单独读出来，能不能让听众听到一个完整的论断（claim）？如果只听到一个领域名（"Market overview"），违反了规则。

## 核心规则 2：每个 claim 必须有引用

```html
<span>{{S01_ARG1_EVIDENCE}}<sup class="cite" data-ref="1">[1]</sup></span>
```

所有数字、所有引用、所有结论 → 必须挂引用编号 → references 段对应。

**citation 检查清单**：

- 数字（"47%"、"+38% YoY"）→ 必须 cite 来源
- 前人方法（"We adopt the X algorithm"）→ 必须 cite 原文
- 行业判断（"Most researchers agree"）→ 必须 cite 综述或 survey
- 自己的实验结果 → 在 figure caption 里写 N、period

**reference 格式**：作者 (年). *标题*. 期刊/会议. URL（可选）

## 核心规则 3：Exhibit（不是 Figure）

学术界用 "Exhibit" 表示图表，强调它是**证据**而非装饰。命名：

```
EXHIBIT 1: 商业市场的 ARPU vs 用户量散点图
EXHIBIT 2: 方法学流程图（N=384, 2026Q1-Q2）
EXHIBIT 3: 实验结果三组对比柱状图
```

每个 Exhibit 含：
- LABEL（左上角，eyebrow 风）
- TITLE（一句话标题，名词短语 OK）
- SOURCE 或 N（右上角）
- BODY（图表本体）
- CAPTION（图下方一句话**解释性**说明——不是描述"这是 X 图"，而是"这张图告诉我们 Y"）

## 核心规则 4：Q&A 页（强制）

学术演讲的固定环节。模板提供 3 个预设 question slot：

1. **方法学质疑**（"How did you measure X?" / "Your N is small."）
2. **结论延伸**（"Does this generalize to Y?" / "What about Z case?"）
3. **诚实局限性**（"What are the limitations?"）

**第 3 题必填**——主动暴露 limitations 比被问倒强 10 倍。

## 标准章节结构（4 节制）

```
SECTION 01 · CONTEXT          → 现象 / 痛点 / 文献空白
SECTION 02 · HYPOTHESIS       → 我们的假设 vs 对立假设
SECTION 03 · METHOD & RESULTS → 实验设计 + 数据
SECTION 04 · IMPLICATIONS     → 结论 + 开放问题
```

每节 1 个 action title + 1-2 个 exhibit + 3 个论点。

## 文件名

```
{YYYY-MM-DD}-{venue-slug}-{title-slug}-academic.html
```

例：`2026-06-15-cvpr-agent-alignment-academic.html`

## 与 viz-deck 默认风的关系

继承深空蓝紫青调色板，但把 **Inter sans-serif 让位给 Newsreader serif**——学术报告主标题、abstract、exhibit caption 都用 serif，给"严肃" 加分。

不要混合两种字体在同一行——要么全 serif 要么全 sans。

## 反模式

- ❌ Action title 写成名词短语（"市场分析"）
- ❌ 数字不挂引用（"市场翻倍" 没有 [1]）
- ❌ 不写 references 节
- ❌ 没有 Q&A 页（学术报告必备）
- ❌ Limitations 没写或写"无明显局限"（学术诚实底线）
- ❌ 用商业风的 cliché（"我们将颠覆这个行业"）

## 与 viz-deck 模式 3（slide-deck）的关系

academic-talk.html 是**长滚动 keynote-report**（mode 1），不是分页幻灯片。如果用户要分页 PPT 形式的学术演讲——

走 mode 3（slide-deck.html）+ 在 SKILL.md 标注 "academic mode"，speaker notes 严格写完整句子，章节封面标 action title。

或者走 mode 5（pptx-deck）+ JSON spec 的 layout 全用 `title-bullets`，每页 title 强制 action title 语法。

## 自检 checklist（提交前必跑）

- [ ] 所有 `<h2 class="action-title">` 都是完整句子（主语+动词+受词）
- [ ] 所有数字都挂 `<sup class="cite">`
- [ ] References 节至少 6 条
- [ ] Q&A 节有 3 题，第 3 题是 limitations
- [ ] Abstract 段 ≤ 200 字
- [ ] Exhibit caption 是解释性的（"X 告诉我们 Y"），不是描述性的（"这是 X 图"）
- [ ] 全文不出现 "可能"、"应该"、"也许" 的模糊语（学术写作要 specific）
- [ ] Speaker name + Affiliation + Date 在 hero byline 里都填了
