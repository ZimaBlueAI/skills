# 演讲者模式 · Speaker Mode（ZimaBlueAI deck 的招牌能力）

> 现场上台时按 **S**，弹出一个独立窗口：本页逐字稿（可直接念的部分高亮成橙色）、
> 下一页预告、大号计时、整场议程进度。投影上观众看干净的 deck，演讲者屏看完整提词器。
> 母版实现：`D1-破局与进化.html`（最完整，含逐字稿）。骨架：`templates/zima-ppt-starter.html`。

这套是 ZimaBlueAI deck 区别于普通 HTML 幻灯片的核心。**做 deck 必须把它带上**——
不是可选装饰，是上台能不能不慌的保障。

---

## 1. 现场快捷键（写进封面副标题，提醒自己）

| 键 | 作用 |
|---|---|
| `←` `→` / `空格` / `PageUp` `PageDown` | 翻页 |
| `Home` / `End` | 跳首页 / 末页 |
| `F` | 全屏切换 |
| `S` | 开/关演讲者窗口 |

输入框聚焦时（INPUT/TEXTAREA）快捷键自动让位，不抢输入。

## 2. 计时系统（两条线 + 配额）

每页 `<section class="slide" data-min="N">` 标注**计划讲 N 分钟**。引擎据此：

- **底部 2px 计时条**：当前页已用时间 / 配额；**超时变赭红**（`.timer-bar.over`）。
- **右下角 timer**：`已累计 mm:ss / 总配额 mm:ss`（总配额 = 所有 `data-min` 之和）。
- **演讲者窗口大号计时**：当前页进入后从 0 计起，赭红大字，一眼知道这页讲了多久。

> 配额是给自己的节奏锚，不是硬约束。超红了就知道该收。

## 3. 逐字稿约定（`.notes` 块）

每页 `section.slide` **后面紧跟**一个同级 `<div class="notes" data-min="N">`，舞台上
`display:none`，只在演讲者窗口渲染。引擎靠 `section.nextElementSibling` 取它。

逐字稿用**带标签的段落**，标签决定演讲者窗口里的配色，让你一眼分清"哪些念、哪些做"：

```html
<div class="notes" data-min="3">
  <p><b class="tag-cue">3 分钟 · 节奏</b> 自我介绍 30s → 金句 30s → 四个数字 90s。</p>
  <p><b class="tag-say">【开场话术】</b>"各位老总，欢迎……<b>核心命题</b>。"</p>
  <p><b class="tag-data">【数字 ①】</b>"先看一个数——<b>10 亿</b>，全球周活。"</p>
  <p><b class="tag-do">【动作】</b>指向 gold 那根条，停 2 秒，扫全场。</p>
  <p><b class="tag-bridge">【过渡 → 02】</b>"今天分五段，先从第一段开始。"</p>
</div>
```

### 标签语义

| 标签 | 颜色（窗口里） | 含义 | 念不念 |
|---|---|---|---|
| `tag-cue` | 灰底 | 节奏/时间分配 | 不念 |
| `tag-say` | 青底 | 开场/主话术 | 标签后的文字**直接念** |
| `tag-data` | 青底 | 数字解读话术 | 标签后的文字**直接念** |
| `tag-do` | 红底 | 肢体/操作动作（指、停、扫场） | 不念 |
| `tag-bridge` | 翠底 | 页间过渡承接 | 不念 |

**关键交互**：`tag-say` / `tag-data` 段落里的正文会自动变**橙色**（CSS `:has()` 选择器），
演讲者一眼就知道这段是要念出口的；标签徽章本身有底色，不会被误念。

## 4. 演讲者窗口结构（弹窗内容）

按 S 调用 `togglePresenter()`，`window.open` 一个 720×920 窗口（暖纸主题，与主屏一致），
内含：

```
顶部     当前页 kicker + 标题     |     大号计时 + 总配额
下一页   预告（gold 标签）
逐字稿   本页 .notes 全文（橙色 = 可念；标签徽章 = 不念）
图例     四种标签的颜色含义
议程     全部页码 · 标题 · 配额分钟，当前页高亮并自动滚入视野
```

主屏每次 `show(i)` 通过 `postMessage({type:'slide',i})` 通知窗口，窗口换页、重置本页计时、
高亮议程。**双向解耦**：关窗不影响主屏，主屏翻页窗口自动跟。

## 5. 移植到任意 deck（三步）

1. **结构**：每页 `section.slide` 后放一个同级 `div.notes`，两者都带 `data-min`。
2. **CSS**：拷 `.notes{display:none}` + starter 里 `.timer-bar` / `.progress` / `.nav .timer`。
3. **JS**：拷 starter 的 `show()` / `tick()` / `togglePresenter()` 与 keydown 绑定（含 `S` 分支）。

逐字稿窗口的 CSS（`.notes-panel`、`tag-*` 配色、`:has()` 橙字规则）整段写在
`togglePresenter()` 的 `document.write` 模板里，跟着拷即可，无需外部文件。

## 6. 反模式

- ❌ 做了 deck 不带演讲者模式——上台只能裸讲，节奏全凭记忆。
- ❌ `.notes` 放进 `section` 内部——会被 `slides` 选中或影响布局；必须是**同级、紧随其后**。
- ❌ 逐字稿不打标签——窗口里分不清哪句念哪句做，等于没有。
- ❌ 漏标 `data-min`——计时条和总配额失真。
- ❌ 把要念的话写成名词提纲——`tag-say`/`tag-data` 段就是要能照着念出口的完整句子。
