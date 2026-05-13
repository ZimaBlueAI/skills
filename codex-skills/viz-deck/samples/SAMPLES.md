# viz-deck samples

Three categories: keynote HTML/MP4 (v2), 5-dim critique (v2), and editable PPTX decks (v3).

## v3 · pptx-deck mode (真正可编辑 PPTX)

Open any `.pptx` in PowerPoint — every text frame, accent bar, KPI tile, and divider is an independently clickable native shape. Tab through the slide to walk shapes individually.

| Sample | Theme | Slides | Demonstrates |
|---|---|---|---|
| **`editable-deck-sample.pptx`** + `.spec.json` | deep-space | 9 | Canonical Q3 board update — verdict, KPIs, options, tradeoff, pullquote, closing. The reference spec for `pptx-deck-spec.example.json`. |
| **`product-launch-deck-sample.pptx`** + `.spec.json` | **deck-light** | 10 | Product launch keynote (Mingjing AI public release). Shows the corporate-friendly indigo-on-white theme. |
| **`all-layouts-showcase-sample.pptx`** + `.spec.json` | deep-space | 8 | One slide per layout — `title-cover`, `agenda`, `section-divider`, `title-bullets`, `two-column`, `kpi-grid`, `pullquote`, `closing`. Use as visual reference when picking a layout. |

### Verify they're truly editable

```bash
# Each slide should contain ≥10 independent <p:sp> shapes
unzip -p editable-deck-sample.pptx ppt/slides/slide1.xml | grep -c "<p:sp>"
```

If you see a number ≥10, every visual element is clickable in PowerPoint.

### Reuse the specs as templates

```bash
cp samples/product-launch-deck-sample.spec.json my-launch.json
# edit my-launch.json — change title, slides, kpis
~/.claude/skills/viz-deck/scripts/export-editable-pptx.sh my-launch.json \
  --theme deck-light --anim fade --trans fade
```

---

## v2 · motion-stage (HTML + MP4)

| Sample | Format | Demonstrates |
|---|---|---|
| `motion-stage-sample.html` | HTML stage | 8s motion narrative with `window.__ready` signal |
| `motion-stage-sample.mp4` | 1920×1080 H.264 | The same stage rendered to video via huashu `render-video.js` |

---

## v2 · 5-dim critique

| Sample | Demonstrates |
|---|---|
| `design-critique-sample.html` | Keynote-style 5-dim critique (deep-space palette) — radar + Keep/Fix/Quick-Wins |
| `design-critique-sample.scores.json` | Source scores used to render the critique HTML |
