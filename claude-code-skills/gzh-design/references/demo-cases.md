# gzh-design demo 用例

这些 demo 用于快速验证主题选择、排版链路和“一键复制”预览页。需要演示时，任选一个 `assets/demo-cases/*.md` 作为原文，让 Codex 使用 `$gzh-design` 或自然语言触发。

## 快速使用

示例请求：

```text
使用 $gzh-design，把 ~/.codex/skills/gzh-design/assets/demo-cases/03-ai-agent-workflow.md 排成公众号 HTML，直接排，不用问。
```

在 Windows 上也可以写成：

```text
使用 $gzh-design，把 C:\Users\BENM\.codex\skills\gzh-design\assets\demo-cases\03-ai-agent-workflow.md 排成公众号 HTML，直接排，不用问。
```

期望交付：

- 一个干净正文片段：`*_排版_{主题中文名}({主题标识}).html`
- 一个预览页：`*_预览.html`
- 打开预览页后点击“一键复制”，即可粘贴到微信公众号编辑器。

本 skill 已内置一批预生成 HTML，可直接打开。注意：根目录下的 demo HTML 都带“一键复制”按钮，适合用户打开；干净正文片段只放在 `clean/` 兜底目录。

- 带“一键复制”按钮的演示页：`assets/demo-html/*_一键复制_*.html`
- 干净正文兜底片段：`assets/demo-html/clean/*_正文片段_*.html`
- 重新生成命令：`python scripts/render_demo_html.py`

## 用例清单

| 文件 | 建议主题 | 覆盖能力 |
|---|---|---|
| `assets/demo-cases/01-saas-tech-roadmap.md` | 科技蓝图 | 技术方案、指标、架构判断 |
| `assets/demo-cases/02-cli-tool-tutorial.md` | 极客终端风 | 命令、代码块、步骤教程 |
| `assets/demo-cases/03-ai-agent-workflow.md` | AI 星云风 | Agent 能力、模型判断、流程自动化 |
| `assets/demo-cases/04-city-reading-note.md` | 文艺杂志风 | 随笔、引文、片段札记 |
| `assets/demo-cases/05-creator-growth-review.md` | 自媒体栏目风 | 栏目钩子、热点复盘、互动 CTA |
| `assets/demo-cases/06-product-launch-note.md` | 产品宣发风 | 卖点、对比、行动 CTA |
| `assets/demo-cases/07-public-welfare-action.md` | 公益倡议风 | 事实说明、温暖引言、参与方式 |

## 设计感增强 Showcase

`assets/demo-html/showcase/` 内置更多场景化模板，根目录同样都是带“一键复制”按钮的 HTML：

| 文件 | 使用场景 |
|---|---|
| `01-ai-agent-showcase_一键复制.html` | AI 产品解读、智能体方案 |
| `02-product-launch-showcase_一键复制.html` | 产品发布、版本更新、功能宣发 |
| `03-course-camp-showcase_一键复制.html` | 课程招募、训练营、社群活动 |
| `04-event-invite-showcase_一键复制.html` | 活动邀请、品牌故事、文化空间 |
| `05-case-study-showcase_一键复制.html` | 客户案例、项目复盘、解决方案 |
| `06-public-action-showcase_一键复制.html` | 公益倡议、志愿者招募、ESG |
| `07-weekly-digest-showcase_一键复制.html` | 周报、资讯合集、行业观察 |

重新生成 showcase：`python scripts/render_showcase_html.py`。

## 回归检查点

- 自动模式能按题材选到建议主题，或至少给出合理选择理由。
- 每个正文段落有 1-3 处关键词下划线标记。
- 代码块、图片占位、引用、列表都被转换，不遗漏原文内容。
- `validate_gzh_html.py` 对正文片段 0 ERROR。
- `wrap_preview.py` 生成的预览页有“一键复制”按钮，复制区域不包含工具栏和脚本。
