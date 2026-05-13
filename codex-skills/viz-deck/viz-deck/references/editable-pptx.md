# Editable PPTX — what's clickable, what's not

The ppt-master bridge produces a `.pptx` where every visual element is a native
PowerPoint object, not a flattened image. This file documents exactly what a
stakeholder can edit when they open the output.

---

## What is editable (every one of these is clickable)

| Element | Output type | Editable in PowerPoint |
| --- | --- | --- |
| Slide title text | `<a:t>` inside `<p:sp>` | ✓ — double-click, retype |
| Body text / bullets | text frames with multiple paragraphs | ✓ — re-flow, restyle |
| Accent bars (60×6 strips) | `<p:sp>` rectangle | ✓ — drag, resize, recolor |
| KPI tiles | grouped rectangle + text frame | ✓ — each tile editable |
| Section number | text frame (large) | ✓ — retype "01" → "01.1" |
| Quote glyph (“) | text frame, large | ✓ — replace, restyle |
| Background grid dots | `<p:sp>` ellipses | ✓ — recolor, move |
| Dividers and horizontal rules | `<p:sp>` lines | ✓ — move, restyle |
| Speaker notes | `<p:notes>` | ✓ — visible in Outline / Notes view |

---

## What is NOT editable

Limitations of the SVG → DrawingML conversion:

| Element | Reason | Workaround |
| --- | --- | --- |
| Gradients with >2 stops | python-pptx only supports linear gradient stops 0/1 | Author with 2-stop gradients, or rasterize for fidelity |
| SVG filters (drop shadow, blur) | PowerPoint approximates only | Use PowerPoint's built-in shadow / soft-edge on the shape after import |
| Custom font files | PowerPoint uses what's installed on the viewer's machine | Stick to system fonts (Inter, JetBrains Mono, system-ui) or embed during PowerPoint export |
| Complex path morphing | path is preserved but not interactive | Use shapes (rect, circle, ellipse) where possible |

---

## Why this matters

A "PPTX" exported from html2pptx (huashu v0.2) is technically a .pptx, but
each slide is a single image with one text overlay. A stakeholder cannot:
- Recolor the accent bar
- Change a KPI value without retyping the whole text block
- Move a tile to a different position
- Apply their corporate template

A "PPTX" exported via ppt-master is what a stakeholder expects: real shapes
they can click, drag, restyle, and integrate into their corporate template.

---

## Verify yourself

After running `export-editable-pptx.sh`, open the output in PowerPoint and:

1. **Click on the title text** — handles appear around just the title, not the whole slide
2. **Right-click an accent bar** → "Format Shape" — fill, outline, size all editable
3. **Tab through elements** — PowerPoint walks through each shape independently
4. **View → Outline View** — text from every slide is selectable as outline

If any of the above fails, the bridge fell back to image-mode. Run again with
`--only native` to force native shapes:

```bash
~/.claude/skills/ppt-master/.venv/Scripts/python.exe \
  ~/.claude/skills/ppt-master/skills/ppt-master/scripts/svg_to_pptx.py \
  <build_dir> --only native -o <out>.pptx
```

---

## Theme adherence

The three viz-deck themes preserve their identity through conversion:

- **deep-space** (default) — bg `#030711`, accent `#00D9FF`, gold `#FFB800`, Inter font
- **terminal** — bg `#0A0A0A`, accent `#D4FF00`, JetBrains Mono (use for biz-decision-stack)
- **deck-light** — bg `#FAFBFC`, accent `#6366F1`, Inter (use for corporate-friendly decks)

If your corporate template uses different colors, see [`master-templates.md`](master-templates.md)
for the template import workflow.
