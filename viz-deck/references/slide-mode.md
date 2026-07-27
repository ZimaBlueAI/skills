# slide-mode: HTML 幻灯片 + PPTX 导出协议

> v2 新增。viz-deck 的第 3 种产出模式——HTML 演示用幻灯片，可一键导出为可编辑 PPTX。

## 何时启用

| 用户说什么 | 启用 |
|---|:---:|
| "做个幻灯片"、"做个 PPT"、"PPT 风"、"keynote 风" | ✅ |
| "做个分页演示"、"按页讲" | ✅ |
| "做个可编辑的 PPT"、"导出 PPTX" | ✅ |
| "做个 keynote" / "TED 风" | ✅ |
| "做个汇报"（含演示意图但未指定形态） | ❓ 询问：单页 keynote-report 还是分页 slide-deck？ |

## 与 keynote-report 的区别

| 维度 | keynote-report | slide-deck |
|---|---|---|
| 结构 | 单 HTML，长滚动 | 单 HTML，分页（每屏 100vh） |
| 翻页 | 滚动 | 键盘 ← → / 空格 / 滑动 |
| 字号 | 适合 13" 屏阅读（16-24px） | 适合投影（32-64px） |
| 文字密度 | 中等 | 低（每页 1 个核心观点） |
| 导出 | HTML / 打印 PDF | HTML / 可编辑 PPTX / 横版 PDF |
| 模板 | `stage-report.html` 等 | `slide-deck.html` |

## 工作流

### 1. 选模板

`templates/slide-deck.html` 是基础模板。包含：

- `<section class="slide">` × N（每页一屏）
- 键盘翻页 JS（← → 空格 Esc）
- 进度指示器（右下角 N/N）
- **Speaker Mode（按 `s`）**——独立演讲者窗口弹出，4 张磁吸卡片（当前页缩略图 / 下一页预览 / 提词器 / 计时器），BroadcastChannel 双窗同步
- **Inline Notes（按 `n`）**——演讲者备注全屏覆盖层，适合单屏调试
- 双视图：演示模式 / overview 模式（按 `o` 切换，缩略图列表）
- `?present=true` URL 参数自动打开演讲者窗口

### Speaker Mode 工作机制

`slide-deck.html` 通过 BroadcastChannel `'viz-deck-presenter'` 广播状态（当前页 + 总页 + 所有页 metadata）。`speaker-window.html` 是单文件预制的演讲者窗口，监听同一 channel：

- **CURRENT 卡片**：1920×1080 iframe 等比缩放显示当前页
- **NEXT UP 卡片**：同样 iframe，显示下一页（不透明度 70%）
- **SPEAKER NOTES 卡片**：自动抓取 `<aside class="speaker-notes">` 内容，serif 大字号提词器
- **TIMER 卡片**：elapsed / countdown 双模式（按 ↔ MODE 切换），> 90% 黄色警告，> 100% 红色告警
- 上方 LAYOUT 按钮：GRID（2×2 默认）/ PROMPTER（提词器占 70%）/ DUO（双屏对比）
- 卡片头部可拖动 + 右下角 resize，松手后磁吸到三分网格

**前提**：投影屏 + 笔记本双屏。slide-deck.html 全屏在投影屏；演讲者窗口在笔记本。两个窗口必须同源（即从同一个文件路径或同一 origin 服务的）。本地直接双击打开走 `file://` 协议时 BroadcastChannel 仍可用——但有些浏览器（如 Safari 严格模式）会拦截 popup，此时 hint 会提示。

**输出物**：`templates/slide-deck.html` 旁边永远生成一份 `speaker-window.html`（同目录），无需配置。`export-pptx.sh` 等导出脚本会忽略 speaker-window.html（不进 PPTX 包）。

### 2. 内容结构（每页）

```html
<section class="slide" data-bg="default" data-title="问题与机会">
  <div class="eyebrow">CHAPTER 01 · MARKET</div>
  <h1>问题与机会</h1>
  <p class="lead">2026 年中国本地化 LLM 应用渗透率仅 12%</p>

  <!-- 一页一图或一图组（不要堆 5 个图） -->
  <figure class="chart-echarts">
    <div data-echarts-option='...' style="width:100%;height:480px"></div>
  </figure>

  <!-- 演讲者备注（不显示在主屏，按 s 显示） -->
  <aside class="speaker-notes">
    讲解时强调：这个 12% 数字来自 IDC 2026Q1 报告，
    与同期 SaaS 渗透率 38% 对比，机会窗口明显。
  </aside>
</section>
```

### 3. 章节节奏

| 单元 | 数量 | 规则 |
|---|---|---|
| 总页数 | 12-25 | 少于 12 显得没料；超过 25 观众累 |
| 章节 | 3-5 | 每章 3-6 页 |
| 章节封面 | 每章 1 页 | eyebrow + 章节大标题 |
| 数据页 | 占 30%-50% | 必有图表（用 viz-charts skill） |
| 文字页 | 单页 ≤ 60 字 | 不能堆文字段 |
| 总结页 | 1 页 | 一句话 takeaway + CTA |

### 4. 导出 PPTX（桥接 huashu-design）

**关键能力**：导出**真实文本框**，不是图片嵌入——客户可以打开 PowerPoint 编辑。

```bash
HUASHU="$HOME/.claude/skills/huashu-design"

# 方式 1：通用 html2pptx（适合任意 HTML）
node "$HUASHU/scripts/html2pptx.js" \
  --input ./output/deck.html \
  --output ./output/deck.pptx

# 方式 2：deck 专属优化版（识别 .slide / .eyebrow / .speaker-notes）
node "$HUASHU/scripts/export_deck_pptx.mjs" \
  --input ./output/deck.html \
  --output ./output/deck.pptx \
  --width 1920 --height 1080
```

输出验证：

```bash
# 打开 .pptx 检查：
# 1. 每页 = 1 个 PPT slide
# 2. 标题/正文是真实文本框（可双击编辑）
# 3. 图表是真实图表（如果数据契约对齐）或 PNG 嵌入（fallback）
# 4. Speaker Notes 进入 PPT 的备注栏
```

### 5. 导出 PDF（横版 keynote）

```bash
node "$HUASHU/scripts/export_deck_pdf.mjs" \
  --input ./output/deck.html \
  --output ./output/deck.pdf \
  --landscape --width 1920 --height 1080
```

### 6. 导出 MP4（演示录屏 / 自动播放视频）

幻灯片也能录成视频（每页停留 5s + transition）：

```bash
# 用 deck_stage.js 提供的 autoplay 模式
node "$HUASHU/scripts/render-video.js" \
  --input ./output/deck.html?autoplay=true&per-slide=5 \
  --output ./output/deck.mp4 \
  --duration $(($SLIDE_COUNT * 5 + 5))
```

**注意**：录视频用的不是 motion 动画，是定时翻页——这是 slide-mode 与 motion-mode 的区别。

## 字号与对比度（投影标准）

| 元素 | 字号（投影） | 对比度（WCAG AA） |
|---|---|---|
| h1 | 64-80px | ≥ 4.5:1 |
| h2 | 40-48px | ≥ 4.5:1 |
| lead | 28-32px | ≥ 4.5:1 |
| body | 20-24px | ≥ 4.5:1 |
| caption / source | 14-16px | ≥ 3:1 |

不要按 13" MBP 屏的阅读距离设字号——观众离投影至少 5 米。

## 反模式

- ❌ 一页堆 5 个 bullet point + 2 个图（PPT 不是文档）
- ❌ 用 transition 过度（fade 即可，不要"翻书"、"立方体"）
- ❌ 不分章节封面（观众不知道讲到哪了）
- ❌ 数据图用 emoji 装饰
- ❌ 字号 < 20px（投影看不清）
- ❌ 导出 PPTX 后没人工抽查（默认都要打开看一眼是不是真编辑框）
- ❌ Speaker Notes 写"待补充"——直接删掉
- ❌ 配色超出 design system 限定（哲学一致性会扣分）
