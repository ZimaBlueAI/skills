# biz-decision-stack

一套 Claude Code 配置，覆盖**投资人会 → CEO 决策 → 架构会 → MRD → 项目管理 → 开发测试 → 验收复盘**的完整决策链。

每个角色一个 subagent（思考方式），共享一个 skill（HTML 输出能力）。

## 设计原则

1. **角色与产出解耦**——subagents 负责"以什么身份思考"，skill 负责"用什么形态产出"
2. **视觉统一**——7 份报告共享一套终端风设计系统，深色 + 等宽 + 零动效
3. **少废话**——每份报告头部 4 项 meta，章节标题 mono 大写，结论先行
4. **决策可追溯**——orchestrator 模式可以一键生成全链路 + index 总览

## 安装

把整个 `.claude/` 目录放到你 Claude Code 项目的根目录下（与 `.git` 同级）：

```
your-project/
├── .claude/
│   ├── agents/
│   │   ├── 00-all-hands-orchestrator.md
│   │   ├── 01-board-advisor.md
│   │   ├── 02-ceo-decision.md
│   │   ├── 03-chief-architect.md
│   │   ├── 04-product-manager.md
│   │   ├── 05-dev-test-lead.md
│   │   └── 06-acceptance-retro.md
│   └── skills/
│       └── biz-html-viz/
│           ├── SKILL.md
│           ├── references/
│           │   └── design-system.md
│           └── templates/
│               ├── board-brief.html
│               ├── ceo-canvas.html
│               ├── tech-roadmap.html
│               ├── mrd-report.html
│               ├── project-board.html
│               ├── dev-report.html
│               ├── retro-report.html
│               └── index.html
├── .git/
└── ...
```

如果你想全局可用（所有项目都能调），放到 `~/.claude/` 即可。

## 使用

### 单角色模式

直接在 Claude Code 里用自然语言唤起：

| 你说什么 | 触发哪个 agent | 产出什么 |
|---|---|---|
| "给瑞林项目做一份董事会简报" | board-advisor | board-brief.html |
| "我要决定 Q3 押什么" | ceo-decision | ceo-canvas.html |
| "Mingjing 的技术架构帮我整理" | chief-architect | tech-roadmap.html |
| "做一份 finance-intel 的 MRD" | product-manager (MRD) | mrd-report.html |
| "本周项目进度看板" | product-manager (Delivery) | project-board.html |
| "上周开发测试汇报" | dev-test-lead | dev-report.html |
| "ArkClaw 项目复盘" | acceptance-retro | retro-report.html |

### 全流程模式（推荐）

```
> 走一遍全流程，项目是 Mingjing AI 人生导师
```

orchestrator 会按顺序调用所有 6 个 agent，最后生成一份 index.html 把 7 份串起来。

### 直接调用 skill（不走 agent）

```
> 用 biz-html-viz skill，board-brief 模板，把以下数据渲染成 HTML：[数据...]
```

## 视觉规范概要

- **配色**：黑底（#0a0a0a）+ 酸黄强调色（#d4ff00），仿 Bloomberg 终端
- **字体**：标题 Newsreader（serif），正文 Inter Tight（sans），数据 JetBrains Mono
- **结构**：横线分隔 > 卡片分隔；信息密度 > 留白美学
- **禁令**：渐变 / 玻璃拟态 / emoji 装饰 / 圆角 > 2px / 任何 keyframe 动画

完整规范见 `.claude/skills/biz-html-viz/references/design-system.md`。

## 与 garrytan/gstack 的关系

灵感来自 gstack，但做了三个简化：

1. **6 个角色而非 23 个工具**——通过合并 CTO/CAIO/CAO 和 PM 双模式减少角色冲突
2. **一个 skill 复用 7 个模板**——而非每种产出一个独立 skill，保证视觉一致
3. **HTML 优先于 Markdown**——参考 Thariq 的"HTML 之于 Claude Code 的非理性效用"，决策类内容更适合结构化 HTML

## License

MIT

## 来源参考

- [garrytan/gstack](https://github.com/garrytan/gstack) — 多角色编排灵感
- [Thariq on HTML for Claude Code](https://x.com/trq212/status/2052809885763747935) — HTML 输出哲学
- [Lum1104/Understand-Anything](https://github.com/Lum1104/Understand-Anything) — 知识图谱式可视化思路
