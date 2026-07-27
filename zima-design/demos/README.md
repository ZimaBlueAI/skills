# zima-design demos

两组示范：**反面教材 → 审计 → 重设计**闭环三件套，加上**多风格样片画廊**——四张页面四套「设计签名」，五轴（宏结构 × 主题 × 动效人格 × 卡片物理 × 密度节奏）零重叠，用来证明多样性协议不是口号。

## 闭环三件套（虚构产品 Curio）

| 文件 | 是什么 |
|------|--------|
| `demo-before-ai-slop.html` | **反面教材**。故意保留 12 处典型 AI-slop 特征（紫渐变居中 hero、✨ badge-pill、三等 emoji 卡、编造指标、虚构证言、宣言 footer……），每处有 `[SLOP-N]` 源码注释。 |
| `demo-audit-report.md` | **audit 动词输出示范**。对反面教材跑 slop-test 通用子集：24 项抽查 17 FAIL，附逐关卡证据，结论判定重做。 |
| `demo-after-redesign-hum.html` | **redesign 动词输出示范**。同一产品按 anti-slop 引擎协议重做（签名 1，见下表）。 |

## 多风格样片画廊（四套签名互不重叠）

| # | 文件 | 虚构产品 | 宏结构 | 主题 | 动效人格 | 卡片物理 | 密度 |
|---|------|----------|--------|------|----------|----------|------|
| 1 | `demo-after-redesign-hum.html` | Curio · 每日好奇心 app | Narrative Workflow | Hum（奶油纸 · 三重点缀色） | playful-bouncy | 柔影单层 | 通铺留白 |
| 2 | `demo-style-cobalt-devtool.html` | relay · webhook 调试 CLI | Dev-tool/CLI | Cobalt（冷白 · 单一钴蓝信号） | crisp-professional | hairline 扁平 | 一段刻意密集 |
| 3 | `demo-style-lumen-night.html` | cinder · 推理运行时 | Marquee Hero | Lumen·Night（暗紫 · 黄铜仪器） | calm-editorial | hairline + 内发光 | 通铺留白* |
| 4 | `demo-style-carnival-bento.html` | NIGHTDOCK · 深夜播客厂牌 | Bento（loud 变体） | Carnival·Studio Night（暮粉 · 青/梅对撞） | playful-bouncy* | 厚边硬影 4px4px0 | 杂志式混排 |

\* 签名允许单轴与历史重合，但五轴组合必须整体唯一（协议原文见顶层 SKILL.md「多样性协议」）。

各张的看点：

- **cobalt**：代码即 hero（题左码右）、**真的能用的 ⌘K 命令面板**（⌘K/Ctrl+K 开、Esc 关、方向键选、输入过滤）、一次性 type-in、整页唯一一条石墨暗带、钴蓝信号 <5% 视口。
- **lumen**：手工灯丝腔体仪器（拒绝发光球）+ 引线标注、蓝图网格 4%、正弦包络读数条（一次打印，永不流动）、全小写正文 × 全大写 mono 标签双声部、动词地标（珊瑚色 + 900ms 后划线，全页无斜体）。
- **carnival**：青/梅双色对撞（一格只用一色）、硬偏移阴影、Big Shoulders wdth110 巨字、半调网点占位、跑马灯（内容重复两遍，reduced-motion 冻结）、✱❋◆ 排印装饰符。

## 怎么用

1. 四张 HTML 一起打开，横向对比——同一个 skill，四副面孔，这就是多样性协议的产出形态；
2. 每张头部注释都有 `zima-design signature`（五轴台账）与 `pre-emit critique`（六轴自评）双盖章，以及逐条硬规则自查清单，可当作交付模板；
3. 反面教材 + 审计报告演示 audit 动词的输出形态；给自己的页面跑审计：对 Claude 说「用 zima-design audit 这个页面」。

> 所有产品均为虚构，页内数字均标注「示例数据」——诚实文案是三条铁律之一，demo 也不例外。
