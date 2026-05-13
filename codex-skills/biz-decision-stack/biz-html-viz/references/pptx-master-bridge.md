# ppt-master bridge — terminal-themed editable PPTX

biz-decision-stack v3 adds an **optional** PPTX export path for the 8 decision
templates. The bridge is intentionally narrower than viz-deck's: no entrance
animations, no transitions, no narration. Decision reports are scan-and-sign,
not perform-and-narrate.

---

## When to use the PPTX bridge

| Situation | Output |
| --- | --- |
| Board pack that gets printed and emailed | HTML (current default) |
| Board pack the chair will mark up in PowerPoint with sticky notes | **PPTX (this bridge)** |
| Internal retro Slack-posted as URL | HTML |
| Retro presented in a townhall + circulated as .pptx | **PPTX** |
| Decision archive (one-pagers searchable in Notion) | HTML |
| Decision archive (handed to corporate stakeholder system that requires .pptx) | **PPTX** |

If both forms are needed for the same decision, generate the HTML (existing
flow) AND run `export-decision-pptx.sh` on a JSON spec containing the same
content. The two outputs are siblings, not replacements.

---

## What's preserved from the terminal aesthetic

The PPTX bridge locks to a single theme — no `--theme` flag. The theme matches
the HTML templates exactly:

- Background: `#0A0A0A` (near-black)
- Accent: `#D4FF00` (acid yellow) for verdicts, KPIs, decisions
- Verdict colors: GO=`#D4FF00`, HOLD=`#FFB800`, STOP=`#EF4444`
- Font: JetBrains Mono throughout (titles, body, KPIs)
- Chrome: terminal header bar with `▍ KIND` left + date right
- Sigil: `$` before every slide title (terminal-style)
- Zero motion: `--anim appear --trans none --no-notes` enforced

If you want narration or animations, that's a different deliverable — re-route
to viz-deck's `pptx-deck` mode instead.

---

## Layouts (8)

| Layout | Maps to which HTML template |
| --- | --- |
| `verdict-cover` | board-brief one-pager (verdict band) |
| `kpi-roster` | dev-report KPI strip / mrd-report market sizing |
| `decision-matrix` | ceo-canvas option table |
| `roadmap-phases` | tech-roadmap phase strip |
| `risks-grid` | board-brief risks/mitigations · project-board blockers |
| `retro-3col` | retro-report worked/didn't/change |
| `action-list` | retro / project-board action items |
| `summary-stack` | board-brief footer summary · index aggregator |

A single board-brief PPTX typically uses: `verdict-cover` + `kpi-roster` +
`decision-matrix` + `risks-grid` + `action-list` (5 slides).

A single retro PPTX typically uses: `verdict-cover` + `kpi-roster` +
`retro-3col` + `action-list` (4 slides).

---

## Quick start

```bash
# 1) Copy the right starter spec
cp ~/.claude/skills/biz-html-viz/specs/board-brief.example.json my-brief.json

# 2) Edit the JSON (title, verdict, KPIs, options, actions)

# 3) Generate the editable terminal-themed PPTX
~/.claude/skills/biz-html-viz/scripts/export-decision-pptx.sh my-brief.json
# → ./my_brief_pptx_build/exports/my_brief.pptx
```

---

## Why no narration on decision PPTX?

biz-decision-stack's design philosophy is "the document IS the decision —
no walkthrough required". TTS narration would imply this is a presentation
deck that benefits from speaking. Decision artifacts get scanned, marked up,
and signed. Adding narration would:

- Encourage longer documents (defeats the one-pager principle)
- Create maintenance burden when decisions get amended (audio gets stale)
- Suggest the artifact is incomplete without a presenter (it must be self-contained)

If a decision REALLY needs narration (e.g., investor onboarding deck that
explains a quarter of decisions), generate it with viz-deck `pptx-deck` mode
in the `terminal` theme — same aesthetic, different intent.

---

## Install check

```bash
test -f "$HOME/.claude/skills/ppt-master/.venv/Scripts/python.exe" \
  -o -f "$HOME/.claude/skills/ppt-master/.venv/bin/python" \
  && echo "OK" || echo "Run install — see references/pptx-master-bridge.md in viz-deck"
```
