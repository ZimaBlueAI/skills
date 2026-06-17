# Anti-slop preflight — the pre-ship kill-list

Run this before shipping any deliverable. Each line is a thing that makes output read as
generic AI work. Fix every hit.

## Color

- [ ] 一页强调色 ≤ 2 种。语义色只给语义：红=风险/下降、绿=正向、金="看这里"。不当装饰。
- [ ] 没有霓虹辉光 / 无来由的渐变文字堆叠 / 彩虹色乱用。
- [ ] 背景、强调、文字三层对比明确；不是"到处都在喊"。

## Layout & craft

- [ ] 靠留白和发丝描边撑结构，不是大面积铺色。
- [ ] 卡片是发丝描边 + 极淡阴影，不是重边框 / 重投影。
- [ ] 数字用 `tabular-nums` + 800 粗体 + 强调色。
- [ ] 没有"居中一切 + 三等分卡片"的默认布局偷懒（除非 variance=0 故意为之）。

## Motion

- [ ] 动效只做入场，不炫技。禁无限循环 / 粒子 / 视差滥用。
- [ ] 带 `prefers-reduced-motion` 降级。
- [ ] 内容默认可见——动画失败不会把元素留在 `opacity:0`。

## Material（见 material-and-copy.md）

- [ ] 没有 lorem ipsum / 占位灰块。真图真数据。
- [ ] emoji 不当图标用。
- [ ] 估值标 `[估]`，缺失标 `[N/A]`，**没有编造的数字**。

## Copy（见 material-and-copy.md）

- [ ] 标题用结论句不用名词（"营收四季翻倍" 而非 "营收分析"）。
- [ ] 没有 "不是 X 而是 Y" 句式。
- [ ] 没有黑话堆叠（赋能 / 抓手 / 闭环 / 痛点 / 打法）。
- [ ] 竞品 / 外部评价用对方的话，不用本项目术语去框。

## The one-line test

> 把品牌名和配色去掉，这页还认得出是谁做的吗？认得出 = 有口味；认不出 = slop。
