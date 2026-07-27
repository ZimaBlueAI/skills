# ppt-master bridge (editable PPTX export)

Soft bridge to [`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design) (motion / GIF / BGM) **plus**
[`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master) for editable .pptx assembly.
Without ppt-master installed, the v0.2 huashu PPTX exporter (`export_deck_pptx.mjs`)
still works — it produces a PPTX with one text frame per slide. With ppt-master
installed, you unlock real DrawingML output: every element is a clickable shape.

---

## What ppt-master gives you (vs huashu's html2pptx)

| Capability | huashu html2pptx (v0.2) | ppt-master bridge (v0.3) |
| --- | --- | --- |
| Open in PowerPoint 2016+ | ✓ | ✓ |
| Per-element edit (text, color, font) | partial — text only | ✓ — every shape, rect, line, circle, text |
| Real OOXML animations (`<p:timing>`) | ✗ | ✓ — `--anim fade\|fly\|zoom\|wipe` etc. |
| Page transitions (`<p:transition>`) | ✗ | ✓ — `--trans fade\|push\|wipe\|split` |
| Native chart objects (data-bound) | ✗ (images) | ✓ via viz-charts ECharts→PPTX bridge |
| Master / theme inheritance | flat per-slide | ✓ inherits from imported template |
| Speaker notes → narration audio | ✗ | ✓ via `embed-narration.sh` (edge-tts / ElevenLabs / Qwen / etc.) |
| MP4 with synced narration | external (ffmpeg) | ✓ native PowerPoint export after embed |
| Canvas formats (Xiaohongshu, A4, banner…) | ppt169 only | ✓ ppt169 / ppt43 / a4 / banner / wechat / xiaohongshu / story / moments |

---

## When to use which mode

```
Need scan-only static report (board brief, retro, decision report)?
    → biz-decision-stack (terminal aesthetic, prints clean)

Need an HTML keynote that demos in browser, no editing required?
    → viz-deck keynote-report mode (stage-report / architecture-deep / competitive-landscape)

Need a real PPTX that a stakeholder will open in PowerPoint and edit?
    → viz-deck pptx-deck mode (this file) — JSON spec → editable PPTX

Need to ship a video to YouTube / WeChat?
    → viz-deck motion-stage (huashu MP4) — OR pptx-deck + narration + PowerPoint MP4 export
```

---

## Pipeline

```
your-deck.spec.json
       │
       ▼
make-pptx-deck.mjs            # node — emits one SVG per slide (1280×720 native shapes)
       │
       ▼
<build_dir>/svg_output/       # slide_01_*.svg … slide_NN_*.svg
       │
       ▼
ppt-master svg_to_pptx.py     # python — SVG → DrawingML PPTX
       │   (--anim, --trans, --narration-audio-dir)
       ▼
<build_dir>/exports/deck.pptx # editable in PowerPoint, every element clickable
```

Optional second pass for narration:

```
<build_dir>/speaker_notes/    # one .txt per slide (auto-written if --with-notes)
       │
       ▼
embed-narration.sh            # ppt-master notes_to_audio.py + svg_to_pptx --narration-audio-dir
       │
       ▼
<build_dir>/exports/deck_narrated.pptx
       │
       ▼ (in PowerPoint: File → Export → Create a Video)
deck.mp4                      # with synced narration + animations
```

---

## Install check

```bash
# One-time
git clone https://github.com/hugohe3/ppt-master ~/.claude/skills/ppt-master
cd ~/.claude/skills/ppt-master
python -m venv .venv
.venv/Scripts/pip install python-pptx edge-tts svglib reportlab Pillow numpy
# Optional (image generation, voice cloning):
# .venv/Scripts/pip install openai google-genai elevenlabs

# Verify
~/.claude/skills/ppt-master/.venv/Scripts/python -c \
  "import pptx, edge_tts; print('ok')"
```

---

## Quick start

```bash
# 1) Author your deck as JSON (use templates/pptx-deck-spec.example.json as starting point)
cp ~/.claude/skills/viz-deck/templates/pptx-deck-spec.example.json my-deck.json
# edit my-deck.json — change title, slides, KPIs, etc.

# 2) Generate editable PPTX
~/.claude/skills/viz-deck/scripts/export-editable-pptx.sh my-deck.json \
  --theme deep-space --anim fade --trans fade
# → my-deck_pptx_build/exports/my_deck.pptx

# 3) (Optional) Add narration
~/.claude/skills/viz-deck/scripts/embed-narration.sh ./my-deck_pptx_build \
  --voice zh-CN-XiaoxiaoNeural
# → my-deck_pptx_build/exports/my_deck_narrated.pptx
```

---

## Spec schema

See `templates/pptx-deck-spec.example.json` for the canonical example.
Each slide has a `layout` field; supported values:

| Layout | Purpose | Required fields |
| --- | --- | --- |
| `title-cover` | Opening slide | `title` |
| `agenda` | Numbered agenda | `items[]` |
| `section-divider` | Chapter break | `section`, `title` |
| `title-bullets` | Standard content slide | `title`, `bullets[]` |
| `two-column` | Compare two items | `left.heading`, `right.heading`, `left.items[]`, `right.items[]` |
| `kpi-grid` | 3–9 metric tiles | `kpis[].label`, `kpis[].value` |
| `pullquote` | Attributed quote | `quote`, `author` |
| `closing` | Thank you / contact | `title` |

Every slide may include `notes` — those become speaker notes in the PPTX
(and the TTS source for `embed-narration.sh`).

See [`master-templates.md`](master-templates.md) for using your own corporate
PPTX template as a master.

See [`editable-pptx.md`](editable-pptx.md) for what's clickable and what's not
in the final output.
