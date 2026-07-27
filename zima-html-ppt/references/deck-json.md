# `deck.json` 文档契约 · v1.0

> `deck.json` 是 deck 的**唯一事实源**。`build` 把它渲染成单文件 HTML，同时把原文回写进
> 产物末尾的 `<script type="application/zima+json" id="zima-doc">` 块；`extract` 再从那里
> 原样读回来。`extract(build(x)) == x` 是有回归用例保证的（`evals/run_fixtures.py`）。
>
> 所有文本字段在渲染时统一做 HTML 转义，**唯一例外是 `html` 块**。

---

## 1. 顶层

```jsonc
{
  "zima": "1.0",                       // 必填，schema 版本，目前只有 1.0
  "deckId": "uuid4",                   // 必填；新建由 build --new-document 铸一次，之后永不变
  "title": "…",                        // 必填，写进 <title>
  "meta": {
    "speaker": "张三 · ZimaBlueAI",     // 页脚左侧兜底（当页没写 source 时）
    "footer":  "2026 内训 · D1",        // 页脚右侧兜底
    "date":    "2026-07-27",           // footer 缺省时的页脚右侧兜底
    "brand":   "✦ ZimaBlueAI",          // 底部居中品牌签名
    "brandUrl": "https://www.zimablueai.com"
  },
  "slides": [ /* 见下 */ ]              // 必填，非空
}
```

`deckId` 是身份闸门的锚：改稿时 `build --identity-source 原文件.html` 会校验两边一致，
对不上直接拒绝构建。**不要手改 `deckId`**，也不要把一份既有 deck 当"新文档"重铸。

---

## 2. 一页（slide）

```jsonc
{
  "id": "market-shift",        // 可选，页内锚点/调试用，同一份 deck 内唯一
  "min": 4,                    // 必填，正数，本页时间配额（分钟）→ data-min
  "layout": "split",           // cover | full | split | compare | closing
  "kicker": "DAY 1 · 第二段",   // 可选，标题上方的青色小标
  "title": "营收四个季度翻倍",   // 必填，**用结论句不用名词**
  "sub": "副标题 / 价值主张",    // 可选，仅 cover 常用
  "source": "来源：财报 2026Q2", // 可选，页脚左侧（带 .source 样式）
  "footerLeft":  "…",          // 可选，覆盖页脚左侧
  "footerRight": "…",          // 可选，覆盖页脚右侧
  "blocks": [ /* 主栏内容块 */ ],
  "right":  [ /* split / compare 的右栏，这两种版式必填 */ ],
  "notes":  [ /* 逐字稿，必填且不能为空 */ ]
}
```

版式：

| layout | 标题标签 | 舞台 |
|---|---|---|
| `cover` | `h1` | 单栏，通常放 `metrics` |
| `full` | `h2` | 单栏 |
| `split` | `h2` | 左 1.25 : 右 1，**必须给 `right`** |
| `compare` | `h2` | 左 1 : 右 1，**必须给 `right`** |
| `closing` | `h1` | 单栏，通常放 `bigline` + `quote` |

---

## 3. 逐字稿（notes）

```jsonc
"notes": [
  { "tag": "cue",    "text": "先念图表结论，再点三个要点。" },
  { "tag": "say",    "text": "「看这张图——营收四个季度翻倍。」" },
  { "tag": "data",   "text": "第二季度是拐点，环比 +38%。" },
  { "tag": "do",     "text": "指向金色那根条，停顿两秒。" },
  { "tag": "bridge", "text": "下一段讲成本。" }
]
```

| tag | 默认标签 | 演讲者窗口里的样子 |
|---|---|---|
| `cue` | `{min} 分钟 · 节奏` | 灰底，**不念** |
| `say` | `【话术】` | 青底 + 后文橙字，**直接念** |
| `data` | `【数据】` | 青底 + 后文橙字，**直接念** |
| `do` | `【动作】` | 红底，**不念**（走位、指屏、停顿） |
| `bridge` | `【过渡】` | 翠底，**不念** |

`label` 可覆盖默认标签。也允许直接写字符串（渲染成无标签的一行）。
**每页必须有非空 notes**——这是结构闸门的 error，不是警告。
没有 `say` 或 `data` 会告警：演讲者窗口里没有可直接念的橙字，台上会卡壳。

---

## 4. 内容块（blocks）

所有块共用两个可选字段：`bare`（去掉外层发丝卡片，部分块支持）、`source`（块内小字来源）。

### `metrics` —— KPI 大数字
```jsonc
{ "type": "metrics", "cols": 4, "items": [
  { "value": 3.7, "suffix": "×", "dec": 1, "label": "三年复合增长", "tone": "gold" },
  { "value": "N/A", "label": "缺口径", "count": false }
]}
```
`value` 是数字且 `count` 不为 `false` 时触发滚动动画（`data-count`/`data-suffix`/`data-dec`/`data-prefix`）。
`tone`：`teal`（默认）/ `gold` / `red` / `green`。

### `cards` —— 发丝卡片网格
```jsonc
{ "type": "cards", "cols": 3, "items": [
  { "title": "现状", "pills": [{ "text": "已验证", "tone": "gold" }],
    "body": "一句话概括。", "list": ["要点一", "要点二"], "source": "来源：…" }
]}
```

### `list` —— 发丝分隔列表
```jsonc
{ "type": "list", "bare": false, "items": ["要点一", "要点二", "要点三"] }
```

### `bars` —— 横向对比条（进入本页才填充）
```jsonc
{ "type": "bars", "bare": true, "items": [
  { "label": "自研", "pct": 72, "value": "72%", "tone": "teal" },
  { "label": "外采", "pct": 54, "value": "54%", "tone": "gold" }
]}
```
`pct` 必须是 0–100 的数字（越界是 error）。`value` 是右侧显示文本，缺省用 `{pct}%`。

### `table` —— 青底表头 + 发丝行
```jsonc
{ "type": "table", "head": ["方案", "周期", "成本"], "numCols": [1, 2],
  "rows": [["自研", "6 个月", "480 万"]], "source": "来源：…" }
```
`numCols` 是要走等宽数字样式的列下标。**每行列数必须等于表头列数**（否则 error）。

### `chart` —— Chart.js（纯 JSON 配置）
```jsonc
{ "type": "chart", "name": "revenue", "kind": "bar", "title": "营收（亿）",
  "height": 300, "labels": ["Q1", "Q2", "Q3", "Q4"],
  "datasets": [
    { "label": "营收", "data": [1.8, 2.3, 2.8, 3.2], "tones": ["muted","gold","green","teal"] }
  ],
  "options": { /* 可选，浅覆盖生成的 options */ },
  "source": "来源：…" }
```

- `kind`：`bar` / `hbar`（横向）/ `line` / `area` / `doughnut` / `pie` / `radar`。
- `name` 只允许字母数字下划线，**全 deck 唯一**——它同时是 `data-chart` 值和 `canvas` 的 `id="ch_{name}"`。
- `data` 必须是**纯数字**（`"1.8"` 这种字符串是 error）。
- `tone` 给整条 series 上色，`tones` 给逐个数据点上色；配色只能取 `teal/gold/green/red/muted`。
- `options` 必须是**纯 JSON**：包含 `function` 或 `=>` 会被判 error，因为它会在序列化时被吞掉。
- 一页可以有多个图表，构建时自动合成 `data-chart="a,b"`，进入该页时各懒建一次。

### `quote` / `bigline` / `term` / `text` / `pills`
```jsonc
{ "type": "quote",   "text": "「对方的原话。」", "cite": "—— 某客户 CTO，2026-06" }
{ "type": "bigline", "text": "一句话结论 / 行动号召" }
{ "type": "term",    "text": "$ zima build deck.json --output deck.html" }
{ "type": "text",    "text": "一段正文（超过 220 字会告警）" }
{ "type": "pills",   "items": [{ "text": "已验证" }, { "text": "待确认", "tone": "gold" }] }
```

### `html` —— 逃生口
```jsonc
{ "type": "html", "html": "<div class=\"card\">任意合法 HTML</div>" }
```
**不做转义、不做结构校验**，每用一次都会记一条警告。只在版式确实超出上述块型时用，
并在交付说明里点名——它是下一版改稿时最容易出问题的地方。

---

## 5. 校验会拦什么

**error（阻断构建）**：schema 版本不对 · 缺 `deckId` 或不是合法 UUID · `slides` 为空 ·
缺 `min` 或非正数 · 未知 `layout` · `split`/`compare` 缺 `right` · 缺 `title` · 缺逐字稿 ·
未知 note tag · 未知块型 · 图表缺 `name`/`labels`/`datasets` · 图表重名 · 图表数据非纯数字 ·
`options` 含函数 · 表格列数不齐 · `bars.pct` 越界 · 任意字段残留 `{{占位}}` 或 `%%ZIMA_…%%`。

**warning（不阻断，但要交代）**：名词式标题 · 逐字稿 < 40 字 · 缺 `say`/`data` 标签 ·
一页 > 2 种强调色 · 有数据块但无 `source` · 页数不在 12–25 · 总配额不在 10–180 分钟 ·
正文块 > 220 字 · 用了 `html` 逃生口 · `metrics` 非数字值仍要求滚动 · 数据点与 labels 数量对不齐。

完整闸门定义见 `references/gates.md`。
