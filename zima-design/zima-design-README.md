# zima-design · 设计合奏引擎

> 一个 skill 装下三种设计智能，每次交付都换一副面孔——治「AI 味模板脸」的合奏方案。

## 解决什么问题

单独用任何一个设计体系，产出都会收敛到该体系的舒适区：结构派做什么都像杂志，动效派满屏弹簧，数据派安全但平庸。而 AI 生成 UI 的最大顽疾恰恰是**同质化**——紫渐变居中 hero、三等卡、宣言 footer。

zima-design 的答案是**合奏**：三个内置引擎各管一层，一份原创路由协议决定谁主导、谁辅助，再用五轴多样性协议强制每次交付的「设计签名」不重样。

## 三个内置引擎

| 引擎 | 一句话 | 源自 |
|------|--------|------|
| `engines/anti-slop/` | 21 种页面宏结构 × 20 具名主题 × 57 条 slop-test 验收关卡，audit/redesign 动词 | nutlope/hallmark（MIT） |
| `engines/motion/` | 动画决策框架（频率→目的→缓动→时长）、弹簧物理、手势、性能铁律，6 个子协议 | emilkowalski/skills（MIT） |
| `engines/database/` | 84 风格 / 192 配色 / 74 字体搭配 / 98 UX 准则 / 22 技术栈，Python 本地检索 | nextlevelbuilder/ui-ux-pro-max-skill（MIT） |

外部联动（装了就征用）：impeccable（工程动词与 register 分流）、huashu-design（3 方向并行 demo + 5 维评审）、taste-engine（口味档位）。完整溯源见 `NOTICE.md`。

## 安装

**Claude Code**（整目录拷贝即可）：

```bash
# 全局
cp -r claude-code-skills/zima-design ~/.claude/skills/zima-design
# 或项目级
cp -r claude-code-skills/zima-design .claude/skills/zima-design
```

**Codex CLI**：

```bash
unzip -o codex-skills/zima-design/zima-design.zip -d ~
```

database 引擎的检索脚本需要 Python 3（无第三方依赖）。

## 怎么用

直接说人话即可，路由协议会接管：

- 「做一个 XX 产品的落地页，别做成 AI 味」→ anti-slop 主导（选主题×宏结构）+ database 校验选型 + motion 交互层
- 「这个页面帮我审一遍/重做」→ audit 动词逐关卡审计 → 修补或 redesign
- 「多给我几个设计方向」→ 联动 huashu 出 3 个差异化方向，每个方向不同的主题×宏结构组合
- 「给这个列表加点动效」→ motion 决策框架先问「该不该动」，再给缓动/时长精确值
- 「React 项目该用什么风格/配色/字体」→ database 检索给带理由的选型

每次交付头部会盖两个章：`zima-design signature`（五轴选择台账）和 `pre-emit critique`（六轴自评分）。

## Demo

`demos/` 三件套（虚构产品 Curio）：

1. `demo-before-ai-slop.html` — 反面教材，故意堆 12 处 AI-slop 特征，每处有 `[SLOP-N]` 注释
2. `demo-audit-report.md` — audit 动词输出：24 项抽查 17 FAIL，逐关卡证据
3. `demo-after-redesign-hum.html` — redesign 动词输出：Hum 主题 × Narrative Workflow 重做

并排打开两个 HTML，30 秒就能看懂这个 skill 在拦什么。

## 与本仓库其他 skill 的分工

- **viz-deck / viz-charts / biz-html-viz / zima-html-ppt**：垂直交付管线，SKILL.md 已内联「反 AI slop 硬闸」做底线；要完整设计智能时桥接本 skill
- **taste-engine**：已有产出的轻量口味叠加；本 skill 管从零设计的完整流程
