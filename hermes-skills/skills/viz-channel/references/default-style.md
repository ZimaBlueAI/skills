# 默认视觉风格 · ZimaBlue Editorial(暖纸编辑风)

> **频道里生成的 HTML 和 PPTX,默认走这套风格。** 专业、简洁、克制、出片。
> 这是 viz-channel 的**默认设计系统**,套在 viz-deck / viz-charts 之上——
> 除非用户明确要求别的风格(深空风 / 终端风 / 指定品牌色),否则一律用它。
>
> 参考母版:`D1-破局与进化.html`(暖纸背景 + 深青主色 + 金/赭点缀 + 顶部三色条)。

---

## 1. 设计基调(一句话)

**暖白纸张底 + 深青权威主色 + 金/赭克制点缀 + 发丝级描边卡片 + 大号粗体数字。**
不是深色科技风,不是终端黑;是**高端咨询/编辑排版**的轻盈、专业、可信。

要点:留白充足、层级清晰、强调用颜色而非装饰、动效克制(只做入场,不炫技)。

## 2. 颜色令牌(直接抄进 `:root`)

```css
:root{
  --ink:#15211f;        /* 正文/标题主色,近黑带青 */
  --muted:#5e6b64;      /* 次要文字 */
  --faint:#758078;      /* 脚注/来源/页脚 */
  --bg:#f7f4ee;         /* 页面底,暖纸 */
  --paper:#fffdf8;      /* 卡片底,更亮的纸 */
  --line:#d9ded6;       /* 发丝描边 */
  --teal:#1b5e5a;       /* 主强调色(深青) */
  --green:#2c7a66;      /* 正向/增长 */
  --gold:#d59a3a;       /* 高亮/关注 */
  --red:#a24e3e;        /* 风险/下降(赭红,非刺眼红) */
  --cream:#efe8da;      /* hover/底纹 */
  --soft-teal:#eef7f4;  /* 青色软底 */
  --soft-gold:#fbf3e2;  /* 金色软底 */
  --soft-red:#fdf0ea;   /* 赭色软底 */
}
```

**用色纪律**:一页里强调色不超过 2 种;teal 是默认主色,gold 用于"看这里",
red 只给风险/下降,green 只给正向。大面积铺色是反模式——靠留白和描边撑结构。

## 3. 字体与字号

```css
font-family:"Microsoft YaHei","PingFang SC","Noto Sans CJK SC",Arial,sans-serif;
```
- 标题 `h1` `clamp(32px,4.4vw,64px)` / `font-weight:800` / `line-height:1.05`
- 副标题 `h2` `clamp(26px,3.4vw,46px)`
- 引导小标(kicker):`--teal`、`font-weight:700`、`letter-spacing:.05em`、12–15px
- 正文/副文:`--muted`、14–19px、`line-height:1.45`
- 数字(metric/price):`font-weight:800`、`font-variant-numeric:tabular-nums`、用强调色
- 脚注/来源:`--faint`、11–13px

## 4. 签名元素(让它一眼可辨)

1. **顶部三色条**(每页顶):`linear-gradient(90deg,var(--teal),var(--gold),var(--red))`,高 6–7px。
2. **发丝卡片**:`background:var(--paper); border:1px solid var(--line); border-radius:10px;
   padding:18px; box-shadow:0 14px 38px rgba(39,45,42,.06);`
3. **底部进度条**:`linear-gradient(90deg,var(--teal),var(--gold))`。
4. **大号强调数字** + 灰色小标签的 metric 块。

## 5. 组件配方(复制即用)

```css
.kicker{color:var(--teal);font-weight:700;font-size:clamp(12px,1.05vw,15px);letter-spacing:.05em;margin-bottom:6px}
.card{background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:18px;box-shadow:0 14px 38px rgba(39,45,42,.06)}
.grid{display:grid;gap:14px}.cols-2{grid-template-columns:repeat(2,minmax(0,1fr))}.cols-3{grid-template-columns:repeat(3,minmax(0,1fr))}.cols-4{grid-template-columns:repeat(4,minmax(0,1fr))}
.metric strong{color:var(--teal);font-size:clamp(30px,3.4vw,48px);line-height:1;font-weight:800;font-variant-numeric:tabular-nums}
.metric span{margin-top:8px;color:var(--muted);font-size:clamp(13px,1.15vw,16px)}
.metric.red strong{color:var(--red)}.metric.gold strong{color:var(--gold)}.metric.green strong{color:var(--green)}
.pill{display:inline-flex;align-items:center;height:28px;padding:0 11px;border-radius:999px;background:#e7f0ec;color:var(--teal);font-weight:700;font-size:12px;margin:0 6px 6px 0}
.pill.gold{background:#f6ecd5;color:#8a6212}.pill.red{background:#f4e0d8;color:#7a2e2e}
.bar{display:grid;grid-template-columns:150px 1fr 60px;gap:10px;align-items:center;margin:10px 0}
.track{height:11px;background:#e3e8e1;border-radius:99px;overflow:hidden}
.fill{height:100%;border-radius:99px;background:var(--teal);transition:width 1.2s cubic-bezier(.2,.8,.2,1)}
table.tbl{width:100%;border-collapse:collapse;font-size:13px}
table.tbl th{color:var(--teal);font-weight:700;text-align:left}
table.tbl th,table.tbl td{padding:7px 10px;border-bottom:1px solid var(--line);text-align:left}
.source{font-size:11px;color:var(--faint);margin-top:8px}
```
组件清单:`.metric`(KPI 数字)·`.pill`(标签)·`.card`·`.bar`(条形对比,动画填充)·
`.timeline`/`.day`(顶部色条)·`.compare`(左右对照)·`table.tbl`(青色表头+发丝行)·`.source`(出处)。

## 6. 图表(Chart.js,统一调性)

```js
Chart.defaults.font.family='"Microsoft YaHei","PingFang SC","Noto Sans CJK SC",Arial,sans-serif';
Chart.defaults.color='#5e6b64';
const C={teal:'#1b5e5a',green:'#2c7a66',gold:'#d59a3a',red:'#a24e3e',muted:'#cfd6cd'};
// 柱:borderRadius:6;网格:grid.color 'rgba(0,0,0,.06)';常隐藏 legend;
// 标题 13px/700 ink(#15211f);responsive:true, maintainAspectRatio:false。
// 多 series 配色顺序:teal → gold → green → red → muted。
```
- 折线:`tension:.35`,主线 teal,面积填充用对应 soft 色低透明度。
- 饼/环:teal/gold/green/red/muted 顺序,描边白色 2px。
- viz-charts 出图时把上面这套 palette 作为默认主题传入。

## 7. 动效(克制)

- 页面/卡片:仅入场——`opacity` + `translateX(36px)` + `scale(.985)` → 归位,`.42s ease`。
- 条形:宽度 `0 → var(--w)`,`1.2s cubic-bezier(.2,.8,.2,1)`,进入视口才触发。
- **不要**:无限循环、霓虹辉光、粒子、视差滥用。专业 = 安静。

## 8. PPTX 的同款映射(默认主题)

走 viz-deck 模式5(pptx-deck)时,**不要用深空/终端主题**,用本风格映射的"暖纸"主题:

| 元素 | 取值 |
|---|---|
| 幻灯片背景 | `#fffdf8`(或 `#f7f4ee`) |
| 标题/正文色 | 标题 `#15211f` / 正文 `#5e6b64` |
| 主强调 / 高亮 / 风险 | teal `#1b5e5a` / gold `#d59a3a` / red `#a24e3e` |
| 字体 | 微软雅黑 / 思源黑体(无衬线),标题加粗 |
| 页顶 | 一条 teal→gold→red 渐变色块(对应 HTML 三色条) |
| 卡片/色块 | 白纸底 + 发丝描边(`#d9ded6`),圆角,极淡阴影 |
| 数据图表 | 原生 chart 用同一 palette(teal/gold/green/red) |
| 装饰 | 零动效保留可读;封面/章节页可用大号数字 + kicker |

传给 ppt-master 时把主题色板设为以上 token;若它只接受预设主题名,选最接近的
浅色主题再覆盖主色为 `#1b5e5a`、强调为 `#d59a3a`、背景为 `#fffdf8`。

## 9. 自检(交付前对照)

- [ ] 背景是暖纸 `#f7f4ee`,不是白也不是深色?
- [ ] 顶部有 teal→gold→red 三色条?
- [ ] 主色是深青 `#1b5e5a`,强调色 ≤2 种?
- [ ] 卡片是发丝描边 + 极淡阴影,不是重边框 / 重阴影?
- [ ] 数字用 800 粗体 + tabular-nums + 强调色?
- [ ] 图表配色走 teal/gold/green/red,网格极淡?
- [ ] 动效只有入场,没有循环/炫技?
- [ ] PPTX 用了暖纸主题而非深空/终端?

> **起步模板**:`templates/zima-editorial-deck.html` 已内置全部令牌、组件与 Chart.js 默认值。
> 默认 HTML 直接以它为骨架填内容,最省事、最稳出片。
