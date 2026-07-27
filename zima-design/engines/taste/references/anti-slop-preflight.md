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

## 六大纪律（硬闸 · 源自 zima-design 的 anti-slop 引擎，蒸馏自 [nutlope/hallmark](https://github.com/nutlope/hallmark)，MIT）

- [ ] **交付前六轴自评**：Philosophy / Hierarchy / Execution / Specificity / Restraint / Variety
      各打 1–5 分，任一 < 3 先返工；分数以注释盖在产物头部（`<!-- P5 H4 E5 S4 R5 V5 -->`）。
- [ ] **诚实文案**：用户没给的指标一律不编——"+47% conversion" / "50,000+ teams" /
      编造的 testimonial、logo 墙、案例数都是 slop；缺数据用 `—` + 「待确认」占位或换版式。
- [ ] **令牌锁定**：色值与 `font-family` 只引用 `:root` 令牌，禁内联 hex / OKLCH / 裸字体名。
- [ ] **禁手绘假 chrome**：不画假浏览器栏（红黄绿点）、假手机壳、假代码窗 / IDE 标题栏；
      真截图包 `<figure>` 或让内容裸站。
- [ ] **响应式硬底线**：320 / 375 / 414 / 768px 四档无横滚（根上 `overflow-x: clip`）；
      带图网格轨道 `minmax(0,1fr)`；可点击文本不折两行；超长词标题 `overflow-wrap: anywhere`。
- [ ] **标题禁斜体**：标题 / display 字一律 roman；强调用字重、强调色或下划线，斜体只留正文。

> 对外页面（落地页 / 官网 / 作品集）或用户要求「彻底反 AI 味」时，升级到 zima-design skill
> 的全量 57 关卡：`zima-design/engines/anti-slop/references/slop-test.md`（另含 21 种宏结构轮换与 20 主题目录）。

## The one-line test

> 把品牌名和配色去掉，这页还认得出是谁做的吗？认得出 = 有口味；认不出 = slop。
