# Integration Guide · 集成到 biz-html-viz / viz-deck

viz-charts 是**纯能力 skill**，不直接产出报告——它被 `biz-html-viz` 和 `viz-deck` 调用，往报告里嵌图表。

## 决策流程

当姊妹 skill 渲染模板时遇到"这里需要一张图"：

```
1. 读 references/decision-tree.md → 选图表类型
2. 读 references/chart-cookbook.md → 拿数据契约
3. 选主题：biz-html-viz → terminal · viz-deck → deck
4. 选模式：浏览器看 → inline · 离线/打印 → offline
5. 拷贝模板 → 填数据 → 嵌入报告
```

## Inline 模式集成

### 步骤 1：选定主题

| 调用方 | 主题文件 | head 配色 |
|---|---|---|
| biz-html-viz | `themes/terminal.js` | 黑 #0a0a0a + 黄 #d4ff00 |
| viz-deck | `themes/deck.js` | 深空 #030711 + 青 #42e8ff |

### 步骤 2：嵌入图表块

**Mermaid**：

```html
<figure class="chart-mermaid">
  <pre class="mermaid-source">
flowchart LR
    A --> B
    B --> C
  </pre>
  <div class="mermaid-output"></div>
  <figcaption>图 N · 描述</figcaption>
</figure>
```

**ECharts**：

```html
<figure class="chart-echarts">
  <div data-echarts-option='{"xAxis":...,"yAxis":...,"series":[...]}'
       style="width:100%;height:320px"></div>
  <figcaption>图 N · 描述</figcaption>
</figure>
```

**自研组件**：直接复制对应组件的 HTML 块。

### 步骤 3：在 `</body>` 之前加 loader

```html
<script>
  // 主题对象——根据姊妹 skill 选定的主题填入
  window.VIZ_CHARTS_OPTS = {
    mermaidTheme: { /* 来自 themes/terminal.js 或 deck.js 的 mermaidTheme 对象 */ },
    echartsTheme: { /* 同上的 echartsTheme 对象 */ }
  };
</script>
<script src="vendor/loaders/cdn-loader.js"></script>
```

或者直接内联整段 cdn-loader.js 到 `<script>` 标签里（推荐——保持单文件 HTML 自包含）。

### 步骤 4：自研组件的 inline JS

KPI / sparkline / gauge / progress / tag-cloud 都是**HTML+CSS+inline JS**自包含。每个组件文件的 `<style>` 和 `<script>` 各取出来粘到主报告对应位置即可。

**纪律**：同一类型的组件 JS 只贴一次（即使页面有 100 个 KPI 卡也只贴一次脚本）。

## Offline 模式集成

适用：报告需要打印归档、邮件附件、完全离线展示。

### 步骤 1：把图表数据存为单独文件

报告项目根下建 `report-charts/`：

```
report-charts/
├── arch.mmd               (Mermaid 源)
├── trend.json             (ECharts 源)
└── ...
```

### 步骤 2：批量渲染成 SVG

```bash
cd .claude/skills/viz-charts/renderers/node
npm install --silent

# 首次需安装浏览器（仅 Mermaid 离线渲染需要）
npx playwright install chromium

# 批量渲染
node batch.mjs --input-dir ../../../../report-charts \
                --output-dir ../../../../report-svgs \
                --theme terminal
```

### 步骤 3：在报告 HTML 里 inline SVG

```html
<figure>
  <object data="report-svgs/arch.svg" type="image/svg+xml" style="width:100%"></object>
  <figcaption>图 N · 系统架构</figcaption>
</figure>
```

或直接读 SVG 内容贴入：

```html
<figure>
  <!-- 把 arch.svg 的内容粘到这里 -->
  <svg viewBox="..." xmlns="...">...</svg>
  <figcaption>图 N · 系统架构</figcaption>
</figure>
```

后者好处：完全自包含，单文件 HTML 可邮件发送、可打印、可归档。

## 3D KG 集成（仅 inline 模式）

3D KG 是 WebGL/THREE.js 渲染，**不能离线 SVG 化**——SVG 是 2D。所以 KG 总是 inline + CDN。

### 流程

```bash
# 1. 生成数据
node .claude/skills/viz-charts/builders/code-kg.mjs \
  --repo ./my-app --output ./report-charts/code-kg.json

# 2. 渲染
# 拷贝 templates/kg3d/code-graph.html 到 ./report-charts/
# 把 {{KG_DATA_JSON}} 替换为 code-kg.json 内容
# 把 {{TITLE}} {{SUBTITLE}} {{REPORT_TYPE}} 替换
# 把 {{THEME}} 设为 terminal 或 deck
```

### 嵌入方式选择

3D KG 通常单独占一页（全屏交互），**不建议**嵌入既有报告 main flow。两种集成姿势：

**姿势 A · 独立链接**：在主报告里放一个按钮跳转

```html
<a href="./code-kg.html" class="btn-card">
  <h3>项目代码 KG（3D 交互）</h3>
  <p>142 个文件 · 387 处依赖 · 点击在新窗口打开</p>
</a>
```

**姿势 B · iframe 嵌入**：占一个章节，固定高度

```html
<section>
  <h2>项目结构 KG</h2>
  <iframe src="./code-kg.html" style="width:100%;height:600px;border:none"></iframe>
</section>
```

姿势 A 更推荐——3D 交互需要完整视口，iframe 内部体验差。

## 兼容性矩阵

| 渲染目标 | terminal | deck | 离线 SVG |
|---|---|---|---|
| Mermaid | ✓ | ✓ | ✓ |
| ECharts | ✓ | ✓ | ✓ |
| KPI / Sparkline / Gauge / Progress / TagCloud | ✓ | ✓ | 自带 SVG，HTML 即离线 |
| 3D KG | ✓ | ✓ | ✗（WebGL 不能 SVG 化） |

## 反模式

- ❌ Inline 与 offline 混用（同一报告里既 CDN 又 SVG，主题易漂移）
- ❌ ECharts 一份报告超过 8 张图（loader 加载慢，建议拆页）
- ❌ 3D KG iframe 嵌入超过 2 个（同页多 WebGL canvas 性能崩）
- ❌ 不读 decision-tree.md 直接选图（违反核心纪律）
- ❌ 把姊妹 skill 的色不带过来（terminal 报告里出现 deck 配色的图，看起来错位）
