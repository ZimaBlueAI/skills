# viz-charts samples

Two categories: motion stage (v2) and **native PPTX charts with editable data (v3)**.

## v3 · 数据绑定的原生 PPTX 图表

Each `.pptx` contains a real `<c:chart>` OOXML object — open in PowerPoint, right-click → **"Edit Data"** to launch a spreadsheet panel and modify series/categories live. This is fundamentally different from a chart image: in PowerPoint the user can change the chart type (Chart Design → Change Chart Type), recolor series, add trendlines / error bars, etc., all via PowerPoint's native chart tooling.

| Sample | Chart type | Theme | Data shape | Demonstrates |
|---|---|---|---|---|
| **`native-chart-sample.pptx`** + `.spec.json` | column (clustered) | deep-space | 4 quarters × 3 regions | Canonical revenue-by-region chart; the reference spec for `revenue-by-quarter.example.json`. |
| **`chart-trend-line-sample.pptx`** + `.spec.json` | line (2 series) | deep-space | 12 months × 2 series (actual vs plan) | Temporal trend with parallel series — classic for KPI tracking. |
| **`chart-market-share-doughnut-sample.pptx`** + `.spec.json` | doughnut | **deck-light** | 6 categories (top 5 + Others) | Composition chart; deck-light theme suits corporate handoff decks. |
| **`chart-critique-radar-sample.pptx`** + `.spec.json` | radar | terminal | 5 axes × 3 series | 5-dim critique scores for the v3 release itself — meta visualisation. Pairs with the design-critic subagent. |

### Verify they're truly data-bound

```bash
# A real <c:chart> object lives inside the .pptx ZIP
unzip -l chart-trend-line-sample.pptx | grep "ppt/charts/chart"
# → 1 chart XML file = native chart object
```

If you see `ppt/charts/chart1.xml`, the chart is data-bound. The underlying data is stored as an embedded `.xlsx` inside the PPTX; PowerPoint opens it on demand when the user clicks "Edit Data".

### Reuse the specs as templates

```bash
cp samples/chart-trend-line-sample.spec.json my-chart.json
# edit my-chart.json — change categories, series, theme
~/.claude/skills/viz-charts/scripts/export-chart-pptx.sh my-chart.json -o my-chart.pptx
```

Or feed a raw ECharts option object — the bridge auto-detects `xAxis.data` → categories and `series[].data` → values.

---

## v2 · Motion chart (HTML + MP4)

| Sample | Format | Demonstrates |
|---|---|---|
| `trend-motion-sample.html` | HTML stage | 4-quarter ECharts reveal animation |
| `trend-motion-sample.mp4` | 1920×1080 H.264 8s | Same animation rendered to video via huashu `render-video.js` |

---

## Composability tip

Mix v3 chart PPTX into a v3 deck:

1. Build the deck shell:
   ```bash
   ~/.claude/skills/viz-deck/scripts/export-editable-pptx.sh my-deck.json
   ```
2. Build chart slides:
   ```bash
   ~/.claude/skills/viz-charts/scripts/export-chart-pptx.sh chart-1.json -o chart-1.pptx
   ```
3. In PowerPoint: open the deck → **Home → New Slide → Reuse Slides → from chart-1.pptx**.

This keeps charts editable as data while the deck stays editable as shapes — the best of both worlds.
