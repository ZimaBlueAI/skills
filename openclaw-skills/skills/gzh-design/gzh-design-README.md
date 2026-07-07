# gzh-design · 微信公众号文章排版

把 Markdown / Word / PDF / 纯文本一键排成**可直接粘贴进微信公众号编辑器、粘贴后样式不丢失**的 HTML。源自 [isjiamu/gzh-design-skill](https://github.com/isjiamu/gzh-design-skill)（AGPL-3.0，甲木 × 摸鱼小李联名共建），由 ZimaBlueAI 扩展 Codex/OpenClaw/Hermes 安装适配、一键复制预览页、13 套主题、demo/showcase 模板与生成脚本。来源与升级方式见 `NOTICE.md`。

## 何时用

- 「公众号排版」「微信排版」「把这篇文章排成公众号 HTML」「gzh」
- 「一键排版 / 自动排版」（全自动模式：自动推断结构 + 自选主题，不逐步提问）
- 「按这张参考图 / 这段描述生成一套新主题」（自定义主题生成器）

**不用于**：普通网页 / 落地页 / PPT（走 huashu-design / viz-deck / biz-html-viz 等生成型 skill）。

## 核心能力

| 能力 | 说明 |
|---|---|
| 13 套内置主题 | 摸鱼绿（默认）· 红白色系 · 石墨极简 · 留白禅意 · 摸鱼票据 · 橄榄手记 · 科技蓝图 · 极客终端风 · AI 星云风 · 文艺杂志风 · 自媒体栏目风 · 产品宣发风 · 公益倡议风，每套自成体系（设计变量 + 组件 + 骨架 + 文章类型配方表），清单见 `references/theme-index.md` |
| 主题生成器 | 一句话描述或参考图 → 生成全新组件库并登记本地复用（`references/theme-generator.md`） |
| 输入全兼容 | Markdown / `.docx`（`scripts/extract_docx.py`）/ PDF / 纯文本，非 Markdown 先按 `references/format-normalize.md` 归一化 |
| 智能排版 | 章节自动编号（末章 ∞）、每段主动标 1–3 处关键词下划线、引言卡 + 目录提炼、作者签名占位去重、中文全角标点 |
| 平台合规 | 样式全内联、文字 `<span leaf="">` 包裹，规避 `<style>/<div>/class/grid/position` 等公众号过滤项 |
| 双关卡校验 | `scripts/component_lint.py`（组件库源头）+ `scripts/validate_gzh_html.py`（最终产物），ERROR 清零才交付 |
| 一键复制预览 | `scripts/wrap_preview.py` 生成带「一键复制」按钮的预览页，点一下把富文本进剪贴板，可直接粘贴到微信公众号编辑器 |
| Demo 用例 | `references/demo-cases.md` + `assets/demo-cases/*.md` + `assets/demo-html/*_一键复制_*.html` + `assets/demo-html/showcase/*.html` 覆盖科技、极客、AI、文艺、自媒体、产品宣发、公益、课程、活动、案例、周报等场景 |

## 工作流（SKILL.md 内置）

输入归一化 → 选主题（按题材自动推荐）→ 读主题组件库 + 通用增量库 → 解析结构、判定文章类型 → 按配方装配 HTML → 校验脚本清零 → 输出干净正文 + 预览页。

## 目录结构

```
gzh-design/
├── SKILL.md                    # 流程与决策（HTML 一律取自组件库，不手写）
├── references/                 # 主题索引 + 13 套主题库 + 通用库 + 生成器 + 归一化 + 回归/Demo 用例
├── scripts/                    # component_lint / validate_gzh_html / extract_docx / wrap_preview / render_demo_html / render_showcase_html
├── assets/                     # 预览模板 + 样例文章 + demo-cases + demo-html + 主题预览示例
├── LICENSE                     # AGPL-3.0（随上游）
└── NOTICE.md                   # 来源 / 移植范围 / 升级方式
```

## 安装

```bash
# 项目级
cp -r claude-code-skills/gzh-design .claude/skills/

# 或全局
cp -r claude-code-skills/gzh-design ~/.claude/skills/

claude /skills    # 列表应出现 gzh-design
```

依赖：纯文件夹，零必需依赖（脚本仅用 Python 标准库；Windows 下运行脚本建议加 `PYTHONIOENCODING=utf-8`）。
