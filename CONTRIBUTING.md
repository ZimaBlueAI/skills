# Contributing · 贡献指南

感谢你愿意为 **ZimaBlueAI Agent Skills** 做贡献！这份文档说明如何提交 issue、PR，以及我们对 skill 质量的硬性要求。

> 维护者：ZimaBlueAI · Apache License 2.0

---

## TL;DR

- **Bug / 文档错字** → 直接开 PR。
- **新 skill 提案 / 跨 harness 移植** → 先开 issue 对齐范围，再开 PR。
- 所有提交即视为同意以 Apache-2.0 授权（见下文 *Sign-off* 章节）。

---

## 1. 在动手之前

### 1.1 先开 issue 的场景

下列改动**必须**先开 issue 讨论，避免你写完 PR 才发现方向不对：

- 新增一个 skill（任何 harness）
- 把现有 skill 移植到新 harness（codex / openclaw / hermes / octarus）
- 修改 design system（配色、字体、模板结构）
- 修改 subagent 的角色定义或编排顺序
- 引入新的运行时依赖（CDN 或 npm）

### 1.2 直接开 PR 的场景

- 文档错字、链接死链
- 模板里明显的 HTML / CSS bug
- 显式标注 `good first issue` 的任务
- 跨平台兼容性 hotfix（Windows 路径分隔符、shell 差异）

---

## 2. PR 规范

### 2.1 提交信息

使用 [Conventional Commits](https://www.conventionalcommits.org/)：

```
feat(viz-deck): add timeline variant for stage-report
fix(biz-decision-stack): correct ceo-canvas markdown link
docs: clarify install path for global vs project-local
chore: bump CHANGELOG to v0.2.0
```

scope 用 skill 名或 `docs` / `meta` / `ci`。

### 2.2 PR 描述模板

```markdown
## What
一句话说清楚改了什么。

## Why
为什么要改，关联 issue 编号。

## How
关键设计决策，特别是会影响其他 skill 的部分。

## Tested
- [ ] 在 Claude Code 里跑过实际 invoke
- [ ] 视觉产出截图已贴在 PR 评论
- [ ] 没有破坏已有模板（grep 回归过）
```

### 2.3 我们会拒绝的 PR

- 未经 issue 讨论的大改（>200 行模板变更或新 skill）
- 把 design system 改成"看起来更漂亮但偏离规范"
- 引入未在 NOTICE 中声明的依赖
- 复制 garrytan/gstack 或其它项目的源代码（理念可借鉴，代码必须原创）
- 加 emoji 装饰 skill 模板（终端风 skill 严禁；讲演风 skill 限制使用）

---

## 3. Skill 质量基线

新 skill 或重大改动需要满足下列硬性要求：

| 维度 | 要求 |
|---|---|
| **SKILL.md** | 必须有 frontmatter（name / description / when-to-use / when-not-to-use） |
| **Templates** | 必须有 design system 文档对应（references/design-system*.md） |
| **可移植性** | 核心 prompt 不绑定 Claude Code 私有 API；harness 特性走 adapter |
| **Reproducibility** | 给一份 sample 数据 + sample 输出（HTML），让贡献者能本地比对 |
| **License header** | 新文件加 SPDX 头：`SPDX-License-Identifier: Apache-2.0` |
| **NOTICE 同步** | 新依赖必须在 NOTICE 中声明（含 SPDX 与 upstream URL） |

### 3.1 跨 harness 移植规则

- 同一 skill 在不同 harness 下，**核心 prompt 文本必须一致**（< 10% 差异）。
- harness 特定的胶水代码（agent invocation syntax、MCP 适配等）放在 `<harness>-skills/<skill-name>/adapter/` 子目录。
- 移植 PR 必须附上"在新 harness 里跑出的样本输出"作为视觉证据。

---

## 4. 法律与签署 · Legal & sign-off

### 4.1 许可证

提交 PR 即视为你以 **Apache License 2.0** 的条款授权 ZimaBlueAI 及任何下游用户使用、修改、再分发你的贡献。

### 4.2 Developer Certificate of Origin (DCO)

所有 commit 必须 sign-off：

```bash
git commit -s -m "feat(viz-deck): your change"
```

会自动追加 `Signed-off-by:` 行，表明你确认贡献符合 [DCO 1.1](https://developercertificate.org/)。

### 4.3 我们暂不要求 CLA

ZimaBlueAI 目前**不要求** Contributor License Agreement。Apache-2.0 + DCO 已经覆盖所需权利授予。如未来政策变化，会在仓库 root 单独公告，且不追溯既往。

---

## 5. 安全问题 · Security

请**不要**在公开 issue 里提交安全漏洞。请发邮件至维护者邮箱（见 GitHub profile），主题前缀 `[SECURITY]`，内容包含：

- 受影响 skill 与版本
- 复现步骤
- 影响范围（信息泄漏 / 任意 HTML 执行 / Path traversal 等）
- 建议修复方向（可选）

我们承诺：

- 7 天内首次响应
- 30 天内给出修复或缓解方案
- 修复后会在 CHANGELOG 致谢报告者（除非你要求匿名）

---

## 6. 行为准则

参与本项目即同意遵守 [`CODE_OF_CONDUCT.md`](./CODE_OF_CONDUCT.md)。简而言之：尊重彼此，对事不对人，反对一切骚扰行为。

---

## 7. 给新人的建议

如果你不知道从哪里开始：

1. 找一个标 `good first issue` 的 task。
2. 在 Claude Code 里把现有三个 skill 实际跑一遍，观察产出。
3. 在你最熟的领域里给一份 sample data，让 skill 跑出报告。
4. 把"发现的小问题"或"想到的新模板"开成 issue，会有人回应。

不要一上来就提"我要把整个 design system 改成 dark + purple"——这种 PR 会被关闭，但欢迎你先开 issue 讨论。

---

<sub>Maintained by ZimaBlueAI · Questions? Open a discussion or ping a maintainer in the issue thread.</sub>
