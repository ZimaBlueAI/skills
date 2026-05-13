# Native PPTX chart export (ECharts → python-pptx chart)

viz-charts v3 adds a bridge that converts a chart spec (or a raw ECharts
option) into a `.pptx` with a single slide containing a **native OOXML chart**
— not a screenshot, not an SVG. The chart has bound data; opening it in
PowerPoint exposes "Edit Data" which launches a spreadsheet panel with the
underlying values.

This is the difference between:
- **viz-charts inline SVG** (HTML deliverable, screenshot if exported) — pixel-perfect, no editability
- **viz-charts → PPTX chart bridge** (this file) — data-bound, every series/category editable

---

## When to use which output

| Need | Output |
| --- | --- |
| Embed a chart in viz-deck HTML keynote | `viz-charts` inline (ECharts CDN) |
| Embed a chart in biz-decision-stack HTML report | `viz-charts` inline (terminal theme) |
| Hand a chart to a stakeholder who wants to update the data later in PowerPoint | **PPTX chart bridge** (this file) |
| Hand a chart to a stakeholder who wants to add it to their own corporate deck | **PPTX chart bridge** + they paste into their template |
| Embed in a pptx-deck slide (viz-deck mode 5) | Use viz-deck's SVG layouts (KPI grid, etc.); for an actual chart, generate via this bridge and copy into the deck |

---

## Supported chart types

| Spec `type` | python-pptx chart type | Stacked variant |
| --- | --- | --- |
| `column` (default) | COLUMN_CLUSTERED | COLUMN_STACKED |
| `bar` (horizontal) | BAR_CLUSTERED | BAR_STACKED |
| `line` | LINE | LINE_STACKED |
| `area` | AREA | AREA_STACKED |
| `pie` | PIE | — |
| `doughnut` | DOUGHNUT | — |
| `scatter` | XY_SCATTER_LINES_NO_MARKERS | — |
| `radar` | RADAR | — |

Set `"stacked": true` for variants that support it.

---

## Quick start

```bash
# 1) Copy a starter spec
cp ~/.claude/skills/viz-charts/specs/revenue-by-quarter.example.json my-chart.json

# 2) Edit the JSON (title, categories, series)

# 3) Generate the editable PPTX
~/.claude/skills/viz-charts/scripts/export-chart-pptx.sh my-chart.json
# → ./my-chart_chart.pptx
```

Or feed a raw ECharts option object — the bridge auto-detects:

```bash
~/.claude/skills/viz-charts/scripts/export-chart-pptx.sh ./echarts-option.json
```

The bridge handles the common ECharts → python-pptx mapping:
- `xAxis.data` → categories
- `series[].name` → series name
- `series[].data` → data points
- `series[].stack` → enables stacked variant
- `series[0].type` → chart type (auto-normalizes `bar` → `column` since
   ECharts "bar" with vertical orientation = PPT column chart)

---

## Themes

Each PPTX gets a themed background, title, and series palette. Pick `theme`
in the spec JSON:

- `deep-space` — match viz-deck (cyan/blue/gold on near-black)
- `terminal` — match biz-decision-stack (acid-yellow on pure black)
- `deck-light` — corporate-friendly (indigo on white)

---

## What's editable when the user opens the .pptx

1. **Right-click the chart → "Edit Data"** opens a spreadsheet with your
   categories and series. Edit a number → the chart re-renders.
2. **Chart Design → Change Chart Type** swaps from column to line / pie /
   area without re-running this script.
3. **Right-click a series → "Format Data Series"** lets the user recolor,
   change marker style, add data labels.
4. **Add Trendline / Error Bars** — all built-in PowerPoint chart features
   work because the chart is a real `<c:chart>` object.

---

## Composing charts into a deck

A common pattern: build a deck with viz-deck mode 5 (pptx-deck), and inject
chart slides from this bridge.

```bash
# 1) Build the deck shell
~/.claude/skills/viz-deck/scripts/export-editable-pptx.sh deck.json

# 2) Build chart slides
~/.claude/skills/viz-charts/scripts/export-chart-pptx.sh chart-1.json
~/.claude/skills/viz-charts/scripts/export-chart-pptx.sh chart-2.json

# 3) In PowerPoint: open deck → Home → New Slide → Reuse Slides from chart-N.pptx
```

This keeps charts editable as data while the deck stays editable as shapes.

---

## Constraints

- One chart per output `.pptx` (by design — composability via reuse-slides)
- Source data is embedded as a small `.xlsx` inside the PPTX
   (this is how PowerPoint stores chart data natively). The data is editable
   directly within PowerPoint; no external `.xlsx` file is needed.
- Color overrides on individual series via `"color": "#hex"` in spec JSON.
- For multi-axis charts (combo chart), generate two PPTX files and overlay
   manually in PowerPoint (limitation of python-pptx's combo support).
