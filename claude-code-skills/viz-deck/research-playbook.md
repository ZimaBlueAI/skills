# Research Playbook: 三档自适应竞品调研

`competitive-landscape.html` 模板的内容来源不是模板写死，而是**实时调研**。本文档定义三档行为。

## 决策树（在生成模板前先走一遍）

```
用户输入是什么？
│
├─ 提供了 git URL（github.com/.../...）
│      └─→ Tier 3: 深度源码分析
│
├─ 提供了竞品名 list（"对比 X, Y, Z"）
│      └─→ Tier 2: 多源公开资料调研
│
└─ 啥都没给（"做一份本项目的竞品对比"）
       └─→ Tier 1: 自动发现 + 公开资料调研
```

混合输入也允许（部分给 git、部分只给名字），按各自档位处理后合并矩阵。

---

## Tier 1: 自动发现 (用户未指定竞品)

### Step 1.1 — 推断项目类别

读取上下文（项目代号、之前对话、用户给的 README）找出**项目领域关键词**。例：

- "Mingjing AI 人生导师" → ai life coach, agent assistant, personal ai
- "Octarus" → ai agent runtime, agent orchestration, agent framework
- "finance-intel" → financial intelligence, multi-asset analysis, llm finance

**不要**只用项目名当查询词——项目名通常没有外部对手。要**抽出能力维度**当查询词。

### Step 1.2 — 三轮 web_search 发现对手

```
search 1: "{category} top platforms 2025 2026"   → 头部品牌
search 2: "{category} open source github"        → OSS 替代
search 3: "{category} 中国 国内"                 → 中文市场
```

每轮 1 次搜索，最多挑 4-5 个候选。

### Step 1.3 — 去重 + 分层

得到候选 list 后，标记每个：

- **Direct competitor**：与本项目目标用户/价值主张高度重合
- **Adjacent**：解决相邻问题，可能演变为对手
- **Reference**：技术参考，不是商业竞品但提供了能力对标

最终矩阵每类至少 1 个，总数 4-7 个。

---

## Tier 2: 公开资料调研 (用户给名单)

### Step 2.1 — 每个竞品 2-3 次 web_search

对每个竞品名，按以下顺序搜：

```
1. "{name} architecture documentation"     → 技术架构
2. "{name} pricing OR business model"      → 商业模式
3. "{name} 2025 OR 2026 release latest"    → 最新动态
```

如果有官方域名，直接 `web_fetch` 拿主页 + /docs + /pricing。

### Step 2.2 — 提取标准化字段

每个竞品至少抓到：

| 字段 | 来源优先级 |
|---|---|
| 一句话定位 | 官方主页 hero |
| 核心能力（3-5 项） | docs / features 页 |
| 商业模式（OSS / SaaS / 双重） | pricing 页 |
| 部署形态（云 / 本地 / 混合） | docs |
| 编程语言 / 主要技术栈 | github / docs |
| 最近一次重要发布 | blog / release notes |
| 已知客户 / 案例 | customers / case studies |
| 社区规模（GitHub stars / Discord / 用户数） | github / 官方披露 |

抓不到的字段写 `[N/A]`，**不要编**。

### Step 2.3 — 与本项目对照

抽 5-7 个**能力维度**做横向矩阵。维度选择原则：

- 必须包含本项目的差异化点（凸显本项目优势）
- 必须包含本项目的弱项（诚实，否则报告失信）
- 维度名要客观（"安全机制"而非"安全做得好不好"）

---

## Tier 3: 深度源码分析 (用户给 git URL)

### Step 3.1 — 沙箱可达性检查

⚠️ Claude 当前沙箱网络仅白名单 npm/pypi 等少数域名，**通常无法 git clone github.com**。

正确做法是：

```
1. 用 web_fetch 拉 README.md（github.com/{org}/{repo}/raw/main/README.md）
2. 用 web_fetch 拉 ARCHITECTURE.md / DESIGN.md / docs/index.md
3. 用 web_fetch 拉 package.json / pyproject.toml / Cargo.toml 看依赖
4. 用 web_fetch 拉关键模块入口（src/index.ts, src/main.py 等）
5. 用 web_search 找 "{repo} architecture deep dive" 第三方解读
```

如果 web_fetch 受限，明确告诉用户：

> "我无法直接 clone {repo}。我会基于公开 README + docs + 第三方解读做分析，标注每条结论的来源。如果你能粘贴关键文件内容，能做更深的对比。"

### Step 3.2 — 源码关键信号

从可获取的文件抽这些信号：

| 信号 | 在哪找 |
|---|---|
| 架构骨架 | README architecture diagram / ARCHITECTURE.md |
| 核心抽象 | src/core/, src/runtime/, lib/ 入口文件类名 |
| 扩展机制 | plugins/, extensions/, skills/ 目录是否存在 |
| 状态管理 | redux / zustand / 自研 store 还是 stateless |
| 测试覆盖姿态 | test/ 占比、CI 文件 |
| 依赖体量 | lock 文件行数 |
| 提交活跃度 | last commit 时间、近 30 天 PR 数（GitHub API 可见） |
| 治理姿态 | CODEOWNERS、SECURITY.md、CODE_OF_CONDUCT 是否齐 |

### Step 3.3 — 用对方的话描述对方

**关键纪律**：描述竞品时优先用它官方 README 的措辞，**不要用本项目术语去框对方**。

❌ 不好：「LangGraph 也实现了我们的 Risk Gate 功能」
✅ 好：「LangGraph 用 `interrupt_before` / `interrupt_after` 节点钩子做 human-in-loop，与本项目的 Risk Gate 对应同一类问题但实现路径不同」

---

## 资料引用格式

每条调研结论必须能追溯。在生成 HTML 时，每个外部断言加 `data-source="..."` 属性，并在文末"References"章节列出：

```html
<p data-source="ref-1">LangGraph 由 LangChain 团队 2024 年 1 月发布。</p>
...
<section id="references">
  <h2>References</h2>
  <ol>
    <li id="ref-1">LangChain Blog · "Introducing LangGraph" · 2024-01-08 · https://...</li>
    ...
  </ol>
</section>
```

引用的最低要求：来源名 + 日期 + URL。日期不详写 `[date unknown]`。

## 反模式（出现即返工）

- ❌ 没搜就写竞品分析（凭训练数据写）
- ❌ 写"据说"、"业内传闻"这类无来源断言
- ❌ 把竞品的弱点夸大、本项目优势粉饰
- ❌ 引用了来源但实际没读，混入幻觉
- ❌ 所有竞品都给同样的"评分高"或"评分低"——这是没认真分析
- ❌ 维度选成"创新性、用户体验、生态"这类无法度量的形容词
