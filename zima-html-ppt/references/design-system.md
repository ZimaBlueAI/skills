# ZimaBlueAI HTML-PPT 设计系统 · ZimaBlue Editorial（暖纸编辑风）

> 一眼能认出"这是 ZimaBlueAI 的现场 deck"。母版：`D1-破局与进化.html` /
> `D2-三场战役.html` / `D3-训练方案.html`。起步骨架：`templates/zima-ppt-starter.html`。

这套风格用于**现场讲演**——投影上台、客户路演、内训训战。不是落地页，也不是
终端决策报告（那是 `biz-html-viz` 的黑底酸黄）。基调：高端咨询 / 编辑排版的轻盈、
专业、可信——暖纸底 + 深青权威主色 + 金/赭克制点缀 + 发丝描边卡片 + 大号粗体数字。

---

## 1. 核心原则

1. **暖纸底，不是白，更不是深色**——`#f7f4ee`，纸张质感降低投影刺眼。
2. **一页强调色 ≤ 2 种**——teal 是默认主色；gold 给"看这里"；red 只给风险/下降；green 只给正向。
3. **靠留白和发丝描边撑结构**——大面积铺色是反模式。
4. **数字一律 tabular-nums + 800 粗体 + 强调色**——讲演靠数字砸人。
5. **动效只做入场，不炫技**——专业 = 安静。

## 2. 颜色令牌（复制进 `:root`）

```css
:root{
  --ink:#15211f;   --muted:#5e6b64; --faint:#758078;
  --bg:#f7f4ee;    --paper:#fffdf8; --line:#d9ded6;
  --teal:#1b5e5a;  --green:#2c7a66; --gold:#d59a3a; --red:#a24e3e;
  --cream:#efe8da; --soft-teal:#eef7f4; --soft-gold:#fbf3e2; --soft-red:#fdf0ea;
  --term-bg:#15211f; --term-fg:#d6e6e1; --term-accent:#f1c977;   /* 代码/终端块 */
}
```

| 令牌 | 用途 |
|---|---|
| `--ink` | 标题、正文主色（近黑带青） |
| `--muted` / `--faint` | 副文字 / 脚注·来源·页脚 |
| `--bg` / `--paper` | 页面暖纸底 / 卡片更亮纸底 |
| `--teal` | **主强调**：kicker、表头、主图色、主数字 |
| `--gold` | 高亮"看这里"：关注项、对比条次色 |
| `--red` / `--green` | 风险下降 / 正向增长，**只用于语义**，不当装饰 |
| `--term-*` | 代码块、终端演示（`pre.term`、`.pill.dark`） |

## 3. 字体与层级

```css
font-family:"Microsoft YaHei","PingFang SC","Noto Sans CJK SC",Arial,sans-serif;
```

| 角色 | 样式 |
|---|---|
| `h1` 主标题 | `clamp(32px,4.4vw,64px)` / 800 / line-height 1.05 |
| `h2` 页标题 | `clamp(26px,3.4vw,46px)` / 800 / 1.1 —— **用结论句，不用名词**（"营收四个季度翻倍" 而非 "营收分析"） |
| `.kicker` 引导小标 | `--teal` / 700 / `letter-spacing:.05em` / 12–15px |
| `.sub` 副文 | `--muted` / 14–19px / 1.45 |
| `.bigline` 收尾金句 | `clamp(26px,3.4vw,50px)` / 800 |
| 数字（metric） | 800 / `tabular-nums` / 强调色 |
| `.source` 出处 | `--faint` / 11–13px |

## 4. 签名元素（让它一眼可辨，缺一不可）

1. **顶部三色条**：每页 `::before`，高 7px，`linear-gradient(90deg,var(--teal),var(--gold),var(--red))`。
2. **发丝卡片**：`background:var(--paper);border:1px solid var(--line);border-radius:10px;
   padding:18px;box-shadow:0 14px 38px rgba(39,45,42,.06)`——极淡阴影，绝非重边框/重投影。
3. **底部进度条** + **超时计时条**：teal→gold 渐变进度；下方 2px 计时条，超配额变 `--red`。
4. **大号强调数字 + 灰色小标签**的 metric 块。
5. **底部居中品牌签名** `✦ ZimaBlueAI`（链 zimablueai.com）。
6. **右上角操作提示徽章** `.hint`：常驻 `按 F 全屏 · 按 S 演讲者模式 · ← → 翻页 · 空格 下一页`，
   按键字母用 teal 加粗高亮——让任何接手放映的人一眼知道有全屏和演讲者模式。封面副标题里再带一次。

## 5. 舞台骨架（每页结构）

```
.deck                         整屏容器
  └─ section.slide[data-min]   一页，绝对定位，opacity+translateX 入场
       ├─ header              .kicker + h1/h2 + .sub
       ├─ .stage             居中正文区（栅格/图表/卡片）
       └─ .footer            左来源 / 右页脚
  └─ div.notes[data-min]      逐字稿（紧跟在 section 之后，舞台隐藏）
```

栅格：`.grid` + `.cols-2/3/4`、`.split`（1.25:1）、`.compare`（1:1）。
窄屏（≤900px）自动降级为纵向单列滚动。

## 6. 组件清单（配方见 starter 模板）

`.card` 发丝卡片 · `.metric`（KPI 大数字，`.red/.gold/.green` 变体）· `.pill`（标签，
`.gold/.red/.dark` 变体）· `.bar`+`.track`+`.fill`（条形对比，进入当前页才 1.2s 填充）·
`.list`（发丝分隔列表）· `table.tbl`（青底表头 + 发丝行 + `td.num` 等宽数字）·
`pre.term`（终端/代码块）· `.quote`（gold 左边线引言）· `.chart-wrap`（Chart.js 容器）·
`.source`（出处）。

## 7. 图表（Chart.js，统一调性）

```js
Chart.defaults.font.family='"Microsoft YaHei","PingFang SC","Noto Sans CJK SC",Arial,sans-serif';
Chart.defaults.color='#5e6b64';
const COL={teal:'#1b5e5a',green:'#2c7a66',gold:'#d59a3a',red:'#a24e3e',muted:'#cfd6cd'};
// 柱:borderRadius:6 · 多 series 配色顺序 teal→gold→green→red→muted
// 折线:tension:.35,主线 teal,面积用对应 soft 色低透明
// 网格:grid.color 'rgba(0,0,0,.06)' · 常隐藏 legend · 标题 13px/700 ink
// responsive:true, maintainAspectRatio:false（容器给固定高度）
```

每页图表用 `data-chart="名"` 标在 `.slide` 上，`buildChart(name)` 进入该页时**懒建一次**。

## 8. 动效（克制）

- 翻页/卡片：仅入场——`opacity` + `translateX(36px)` + `scale(.985)` → 归位，`.42s ease`。
- 条形：宽度 `0 → var(--w)`，`1.2s cubic-bezier(.2,.8,.2,1)`，进入当前页触发。
- 数字：`data-count`/`data-suffix`/`data-dec` 触发 easeOutCubic 滚动（≈900ms）。
- **禁**：无限循环、霓虹辉光、粒子、视差滥用、emoji 当图标。
- 必带 `@media (prefers-reduced-motion:reduce)` 降级。

## 9. 反 AI 味文字（沿用项目规则）

- 不写"不是 X 而是 Y"句式；不堆黑话（赋能/抓手/闭环/痛点/打法）。
- emoji 不当图标用（正文引用原文里可出现）。
- 数字用真值：估值标 `[估]`，缺失标 `[N/A]`，**严禁编造**。
- 竞品/外部评价用对方的话，不用本项目术语去框。

## 10. 交付前自检

- [ ] 背景是暖纸 `#f7f4ee`？顶部有 teal→gold→red 三色条？
- [ ] 主色深青，一页强调色 ≤ 2 种？
- [ ] 卡片发丝描边 + 极淡阴影，不是重边框/重投影？
- [ ] 数字 800 + tabular-nums + 强调色？图表配色走 COL，网格极淡？
- [ ] 每页 `data-min` 配额齐全？每页有对应 `.notes` 逐字稿？
- [ ] 动效只有入场，无循环/炫技？带 reduced-motion 降级？
- [ ] 底部有 `✦ ZimaBlueAI` 品牌签名？
- [ ] **按 S 能弹出演讲者窗口，逐字稿、计时、议程都对？**（见 `speaker-mode.md`）
