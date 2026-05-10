# ZimaBlueAI Agent Skills

> **Production-grade skill packs for AI coding agents** — one source of truth, multiple harnesses.
> 一套思考方式 + 一套产出能力，写一次，跑在不同 agent 里。

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Status: Public Preview](https://img.shields.io/badge/status-public--preview-orange.svg)](#roadmap--路线图)
[![Maintainer: ZimaBlueAI](https://img.shields.io/badge/maintainer-ZimaBlueAI-2b6cb0.svg)](https://github.com/ZimaBlueAI)

---

## English summary

This repository hosts the open-source skill suites built and maintained by **ZimaBlueAI** for modern AI coding agents. A "skill" here is a self-contained, declaratively-described capability bundle — instructions, templates, references, optional helper scripts — that an agent loads on demand to perform a structured job (write a board brief, render a 3D knowledge graph, run a competitive landscape, etc.).

Each suite is authored once against a portable mental model and ported to the target harnesses (Claude Code first, then Codex, OpenClaw, Hermes, Octarus). The first publicly released harness is `claude-code-skills/`.

Copyright © 2026 ZimaBlueAI. Licensed under Apache License 2.0. See [`LICENSE`](./LICENSE) and [`NOTICE`](./NOTICE).

---

## 中文导读

这是 **ZimaBlueAI** 维护的 AI 编码 agent skill 开源仓库。每个 skill 是一份"声明式能力包"——指令文件 + 模板 + 参考资料 + 可选脚本——agent 在需要时按需加载，做结构化工作（写一份董事会简报、渲染一张 3D 知识图谱、跑一次竞品 landscape，等等）。

我们的取舍很直接：

- **思考方式与产出能力解耦**——subagents 决定"以什么身份思考"，skill 决定"用什么形态产出"。
- **跨 harness 移植**——核心 prompt + 模板写一次，再分别适配到 Claude Code / Codex / OpenClaw / Hermes / Octarus。
- **决策类内容用 HTML 不用 Markdown**——结构化更稳，渲染更体面，归档更便利。
- **不堆 23 个工具**——少而精，每个 skill 都能独立交付一个完整可签字的产出。

---

## 仓库结构 · Repository layout

```
skills/
├── LICENSE                    Apache License 2.0 全文
├── NOTICE                     ZimaBlueAI 版权 / 商标 / 第三方致谢
├── README.md                  本文件
├── CONTRIBUTING.md            贡献指南
├── CHANGELOG.md               版本变更记录
├── CODE_OF_CONDUCT.md         社区行为准则
│
├── claude-code-skills/        ★ Claude Code harness（已发布）
│   ├── README.md
│   ├── skills-install-guide.md
│   ├── biz-decision-stack/    投资人 → CEO → 架构 → MRD → 交付 → 验收 决策链
│   ├── viz-deck/              讲演级 HTML 报告（深空蓝紫青）
│   └── viz-charts/            图表 + 3D 知识图谱（被前两者调用）
│
├── codex-skills/              ☐ OpenAI Codex CLI（规划中）
├── openclaw-skills/           ☐ OpenClaw（规划中）
├── hermes-skills/             ☐ Hermes（规划中）
└── octarus-skills/            ☐ Octarus（规划中）
```

---

## 已发布的 skill · Shipped skills

目前公开发布的是 **Claude Code** harness 下三个 skill。三者相互独立，按需取用：

| Skill | 一句话定位 | 输出风格 | 包大小 |
|---|---|---|---|
| **biz-decision-stack** | 6 subagents + 1 skill，覆盖董事会 → CEO → 架构 → MRD → 交付 → 验收的完整决策链 | 终端风（黑底 + 酸黄 + 等宽） | 57 KB |
| **viz-deck** | 3 模板讲演级 HTML 报告（stage-report / architecture-deep / competitive-landscape） | 讲演风（深空蓝紫青 + 微动效） | 35 KB |
| **viz-charts** | Mermaid + ECharts + 3D 知识图谱，双主题（terminal / deck） | 能力 skill，被前两个调用 | 150 KB |

📖 完整安装、配置、使用见 [`claude-code-skills/skills-install-guide.md`](./claude-code-skills/skills-install-guide.md)。

---

## 设计哲学 · Design principles

1. **少即是多**——一个 skill 干一件事，复用最大化。biz-decision-stack 的 7 份报告共用 1 个 HTML 渲染 skill，不是 7 个独立 skill。
2. **HTML 优先于 Markdown**——决策链产出走 HTML（结构化、可签字、可归档）。日志类、注解类才用 Markdown。
3. **视觉系统先行**——每个 skill 在动手之前先定 design system（配色 / 字体 / 间距 / 禁令清单），templates 只是落地。
4. **声明式 > 命令式**——skill 是一份 Markdown 描述 + 模板，不是一堆代码。harness 怎么 invoke 由 harness 自己决定。
5. **可移植性是头等公民**——skill 的核心 prompt 必须能在不重写的前提下，迁移到至少 3 个 harness。

---

## 快速开始 · Quick start (Claude Code)

```bash
# 1. clone 仓库
git clone https://github.com/ZimaBlueAI/skills.git
cd skills/claude-code-skills

# 2. 选一个 skill 解压到你的 Claude Code 项目
unzip biz-decision-stack/biz-decision-stack.zip -d /path/to/your-project/

# 3. 在 Claude Code 里直接用自然语言唤起
> 给瑞林项目做一份董事会简报
```

或全局安装到 `~/.claude/skills/`，所有项目共享。详细步骤见 [安装指南](./claude-code-skills/skills-install-guide.md)。

---

## 路线图 · Roadmap

| 阶段 | 内容 | 状态 |
|---|---|---|
| v0.1 | claude-code-skills 三件套首发 | ✅ 已发布 |
| v0.2 | codex-skills 移植（Codex CLI 适配） | 🟡 规划中 |
| v0.3 | openclaw-skills / hermes-skills | ⚪ 规划中 |
| v0.4 | octarus-skills + 跨 harness 一致性测试 | ⚪ 规划中 |
| v1.0 | 5 harness 全覆盖 + skill registry | ⚪ 规划中 |

---

## 贡献 · Contributing

欢迎 issue 和 PR。在动手之前请先读 [`CONTRIBUTING.md`](./CONTRIBUTING.md) 和 [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md)。

特别欢迎以下贡献：

- 把现有 skill 移植到新 harness（codex / openclaw / hermes / octarus）
- 提交新 skill 提案（先开 issue 讨论范围）
- 在 design-system 文档之外提供更多视觉 reference

---

## 知识产权 · Intellectual property

- **版权**：Copyright © 2026 ZimaBlueAI。本仓库源码、模板、文档均在 Apache License 2.0 下开源。
- **商标**：`ZimaBlueAI`、`biz-decision-stack`、`viz-deck`、`viz-charts` 等名称作为本仓库原始套件的标识，归 ZimaBlueAI 所有。Apache 2.0 授予的源码权利不包含商标使用权——衍生分发请改名。
- **第三方依赖**：所有 CDN 加载的运行时（Mermaid / ECharts / three.js / 3d-force-graph）保留各自的上游许可证，详见 [`NOTICE`](./NOTICE)。

完整声明见 [`NOTICE`](./NOTICE)。

---

## 参考与致谢 · Acknowledgements

- [garrytan/gstack](https://github.com/garrytan/gstack) — 多角色编排灵感（仅理念借鉴，无代码复用）
- [Lum1104/Understand-Anything](https://github.com/Lum1104/Understand-Anything) — 知识图谱式可视化思路
- Thariq 关于 *HTML for Claude Code* 的早期论述 — 决策类内容的 HTML 优先哲学

---

## 联系 · Contact

- GitHub: <https://github.com/ZimaBlueAI>
- 安全问题请走 [`SECURITY.md`](./CONTRIBUTING.md#安全问题--security)（暂收口于 CONTRIBUTING）

---

<sub>Made by ZimaBlueAI · Apache-2.0 · 写一次，跑在不同 agent 里。</sub>
