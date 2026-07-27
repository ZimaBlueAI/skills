# NOTICE · gzh-design

本 skill 源自上游开源仓库，并由 ZimaBlueAI 继续扩展为多平台可安装版本。

| 项 | 值 |
|---|---|
| 上游仓库 | https://github.com/isjiamu/gzh-design-skill |
| 上游 commit | `67c079e`（2026-07-07，甲木 × 摸鱼小李 联名首发） |
| 原作者 | [@isjiamu](https://github.com/isjiamu)（甲木） × [「摸鱼小李」](https://mp.weixin.qq.com/s/EMahAzgfAbRQrYukWE7_IQ) 联名共建 |
| License | AGPL-3.0（全文见本目录 `LICENSE`，随上游一并复制） |
| 初始移植日期 | 2026-07-07 |

## 当前范围

本目录包含：`SKILL.md` + `LICENSE` + `references/`（主题索引 / 13 套主题组件库 + 通用增量库 + 主题生成器 + 格式归一化 + 回归与 demo 用例）+ `scripts/`（双关卡校验 / docx 提取 / 预览包装 / demo 渲染 / showcase 渲染）+ `assets/`（预览模板 / 样例文章 / demo-cases / 带一键复制按钮的 demo-html / 主题预览示例）。

**未移植**（非 skill 运行所需）：上游 `archive/`（v1 旧版主题与图库归档）、`docs/`（效果展示长图库）、`.github/`、`CONTRIBUTING.md`、上游 README。

## ZimaBlueAI 新增贡献（非上游）

- `NOTICE.md`（本文件）
- `gzh-design-README.md`（中文使用说明）
- Codex CLI 版安装包与安装脚本：`codex-skills/gzh-design/gzh-design.zip`、`codex-skills/install.*`
- OpenClaw / Hermes 平台目录同步版本：`openclaw-skills/skills/gzh-design`、`hermes-skills/skills/gzh-design`
- “一键复制”预览页：浏览器打开后可直接复制富文本并粘贴到微信公众号编辑器
- 7 套新增主题：科技蓝图、极客终端风、AI 星云风、文艺杂志风、自媒体栏目风、产品宣发风、公益倡议风
- demo 用例与预生成 HTML：`assets/demo-cases/`、`assets/demo-html/`
- 设计感增强 showcase：AI 产品、产品发布、课程训练营、活动邀请、案例复盘、公益行动、周报内刊等场景模板
- demo/showcase 生成脚本：`scripts/render_demo_html.py`、`scripts/render_showcase_html.py`

> 升级上游版本时：重新 `git clone https://github.com/isjiamu/gzh-design-skill`，先对比其
> `SKILL.md` / `references/` / `scripts/` / `assets/` / `LICENSE`，再合并到本目录。不要直接覆盖
> ZimaBlueAI 新增主题、demo、showcase、预览页和多平台安装适配。
> 合并后跑一遍 `PYTHONIOENCODING=utf-8 python scripts/component_lint.py .` 确认 ERROR×0。
