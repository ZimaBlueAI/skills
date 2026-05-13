# Master slides & template reuse

ppt-master extracts master slides, themes, and reusable image sprites from any
existing .pptx and applies them to generated decks. This lets you ship slides in
your corporate template without authoring it from scratch.

---

## Workflow A — Use viz-deck's three built-in themes

Fast path. Pick a theme on the command line:

```bash
./export-editable-pptx.sh deck.json --theme deep-space    # default — cyan/blue/gold on near-black
./export-editable-pptx.sh deck.json --theme terminal      # acid-yellow on pure black, JetBrains Mono
./export-editable-pptx.sh deck.json --theme deck-light    # corporate-friendly, indigo on white
```

Each theme has consistent: background, accent colors, fonts, accent-bar style,
KPI tile color, divider color.

---

## Workflow B — Import a corporate template

If your company has a `.pptx` template:

```bash
# 1) Extract the template's master + theme into ppt-master's template registry
~/.claude/skills/ppt-master/.venv/Scripts/python.exe \
  ~/.claude/skills/ppt-master/skills/ppt-master/scripts/register_template.py \
  /path/to/corporate-template.pptx \
  --name corporate-q3-2026

# 2) Inspect what got extracted (master slides, theme colors, layout placeholders)
ls ~/.claude/skills/ppt-master/skills/ppt-master/templates/corporate-q3-2026/

# 3) Build your deck against that template
~/.claude/skills/viz-deck/scripts/export-editable-pptx.sh deck.json \
  --pptx-master-template corporate-q3-2026
```

Limitations of template extraction:
- **Animations** in the template's master are not preserved — re-apply with `--anim`
- **VBA macros** are stripped (a security boundary, not a bug)
- **Embedded fonts** must be re-embedded in PowerPoint after generation

---

## Workflow C — Reuse generated slides across decks

If you've generated slide 5 in deck A and want it in deck B:

```bash
# Each generated build keeps the source SVG. Copy it across:
cp deck-a_pptx_build/svg_output/slide_05_*.svg deck-b_pptx_build/svg_output/

# Re-run conversion on deck B
~/.claude/skills/ppt-master/.venv/Scripts/python.exe \
  ~/.claude/skills/ppt-master/skills/ppt-master/scripts/svg_to_pptx.py \
  deck-b_pptx_build -o deck-b.pptx
```

This is how you build a "decision library" — a folder of reusable slide SVGs
that mix into new decks without re-rendering.

---

## Why master / theme inheritance matters

Without a template:
- Every slide is a standalone shape group; changing brand color = manual edit of N slides

With a template:
- Change theme color in Slide Master → all generated slides update
- Change master title font → all generated slides inherit
- Logo on master → appears on every slide automatically

For board-level decks that get re-used quarterly, always use Workflow B.
