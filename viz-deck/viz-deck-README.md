# viz-deck

Claude Code 的**讲演级 HTML 报告**生成 skill。深空蓝紫青、玻璃拟态、轨道环主视觉、reveal 滚动入场——给客户路演、投资人 keynote、全员走读用。

> **不是给工程师扫读用的**。打印归档、决策签字、扫读式仪表盘，请用姊妹 skill `biz-html-viz`（终端风、黑底酸黄、零动效）。两者可同时存在，同一项目分别出 deck 版和 dashboard 版。

## 三个模板

| 模板 | 场景 | 字数 |
|---|---|---|
| `stage-report` | 阶段汇报 / Roadmap 走读 / 对外里程碑 | 1000-2000 字 |
| `architecture-deep` | 系统架构 / 治理模型 / 自进化路径纵深 | 1500-3000 字 |
| `competitive-landscape` | 竞品对比 / 技术雷达（**含实时 web 调研**） | 2000-3500 字 |

## 视觉 DNA

源自 Octarus stage-report 系列：

- **配色**：`#030711` 深空底 + `#42e8ff` 主青 + `#6ca5ff` 次蓝 + `#ffd987` 达成金 + `#b893ff` 远期紫
- **字体**：单一 Inter，800 / 700 / 600 / 400 四档权重
- **章节**：`eyebrow + kicker-num + h2 + lead` 四件套节奏
- **微动效**：背景 atmosphericSweep / pulseRing / orbitSpin / reveal-on-scroll，全部支持 `prefers-reduced-motion` 降级
- **主视觉**：每份报告一个（不是每章一个）—— orbit / canvas particle field / SVG knowledge graph / radar 选其一

完整规范在 `references/design-system-deck.md`。

## 安装

放到 Claude Code 项目的 `.claude/skills/` 下：

```
.claude/skills/viz-deck/
├── SKILL.md
├── references/
│   ├── design-system-deck.md
│   └── research-playbook.md
└── templates/
    ├── stage-report.html
    ├── architecture-deep.html
    └── competitive-landscape.html
```

或全局 `~/.claude/skills/`。

## 使用

### 触发关键词

> "讲演 / 演示 / keynote / 阶段报告 / 路演 / 给客户看 / 架构深研 / 竞品对比 / stage report / architecture deep dive / competitive landscape"

### 例

```
> 给 Mingjing 项目做一份阶段报告，讲演风
→ 用 stage-report.html

> Octarus 项目的架构深研报告，三个维度（记忆/治理/自进化）
→ 用 architecture-deep.html

> 对比 LangGraph、AutoGen、CrewAI，做一份竞品 landscape
→ 先 web_search 三家公开资料 → 用 competitive-landscape.html

> 帮我对比 https://github.com/langchain-ai/langgraph 和我们项目
→ Tier 3：web_fetch README/docs/source → 深度对比

> 我们项目的对手有谁？做一份 landscape
→ Tier 1：自动发现 → web_search 三轮 → 横向矩阵
```

## 竞品调研三档自适应

竞品模板**不写死内容**，按用户输入档位自动调研：

| 用户给了什么 | 档位 | 行为 |
|---|---|---|
| 啥都没给 | Tier 1 | 三轮 web_search 自动发现对手 |
| 竞品名 list | Tier 2 | 每家 2-3 次 web_search + web_fetch 官方 |
| git URL | Tier 3 | web_fetch README/docs/源码（沙箱网络受限时用 raw.githubusercontent） |

详见 `references/research-playbook.md`。所有外部断言**必须**带 `data-source` 引用，References 章节列全。

## 与 biz-html-viz 的关系

```
biz-html-viz                    viz-deck
─────────────                   ─────────────
终端风                          讲演风
黑 + 酸黄                       深空蓝 + 青 + 金
零动效                          有微动效（可降级）
密度优先                        节奏优先
扫读 5 分钟                     走读 60-90 分钟
打印归档                        屏幕展示
工程师 / CEO / 董事会签字       客户 / 投资人 / 全员 keynote

7 个模板（决策套件）            3 个模板（演示套件）
- board-brief                   - stage-report
- ceo-canvas                    - architecture-deep
- tech-roadmap                  - competitive-landscape
- mrd-report
- project-board
- dev-report
- retro-report
- index
```

同一项目可以两个 skill 各出一份。比如 Mingjing：
- `biz-html-viz` 出 board-brief + tech-roadmap → 给董事会签字、给 CTO 归档
- `viz-deck` 出 stage-report + architecture-deep + competitive-landscape → 给 D 轮路演、给 keynote

## 反模式

- ❌ 用 viz-deck 做内部周会汇报（用 biz-html-viz 的 dev-report）
- ❌ 用 biz-html-viz 给客户演示（用 viz-deck 的 stage-report）
- ❌ Competitive 模板凭训练数据写（必须 web_search）
- ❌ 一份报告塞两种主视觉（orbit + canvas + radar 全堆）
- ❌ 没读 design-system-deck 直接写
- ❌ 章节缺四件套（eyebrow + kicker-num + h2 + lead）

## License

MIT
