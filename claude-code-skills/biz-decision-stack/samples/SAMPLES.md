# biz-decision-stack samples

Terminal-themed deliverables — HTML for scan-and-sign, editable PPTX for stakeholders who need to mark up in PowerPoint.

## v4 · Template Router examples (NEW)

| Sample | Demonstrates |
|---|---|
| **`template-router-examples.md`** | Three real routing cases — (1) strong-match route with full justification, (2) two-candidate tie kicked back to the user, (3) explicit user request that bypasses the router. Each case shows the 5-dim score breakdown, the ROUTING DECISION block users see, and the HTML comment header written into the chosen template. Inspired by [mckinsey-pptx](https://github.com/seulee26/mckinsey-pptx) (426★). |

Behaviour: the `template-router` subagent (the 9th subagent in this stack) **only** activates when input is ambiguous. If the user explicitly says "做 board brief" or "make a retro report", router yields. The point is not to always-intercept — it's to defend choices when a choice is being made.

---

## v3 · 决策 PPTX (终端风可编辑)

All four samples lock to the terminal theme (black `#0A0A0A` + acid-yellow `#D4FF00` + JetBrains Mono, **zero motion**). Each visual element is an independently clickable native DrawingML shape.

| Sample | Layouts used | Slides | Use case |
|---|---|---|---|
| **`decision-board-brief-sample.pptx`** + `.spec.json` | `verdict-cover` · `kpi-roster` · `decision-matrix` · `risks-grid` · `action-list` | 5 | Q3 board brief — verdict GO on $4.2M reallocation, with options table + risks + binding actions. |
| **`decision-retro-report-sample.pptx`** + `.spec.json` | `verdict-cover` · `kpi-roster` · `retro-3col` · `action-list` | 4 | Q2 retrospective — velocity / quality / customer KPIs, three keepers / drops / changes, two process actions. |
| **`decision-tech-roadmap-sample.pptx`** + `.spec.json` | `verdict-cover` · `kpi-roster` · `roadmap-phases` · `risks-grid` · `action-list` | 5 | Four-quarter tech roadmap (Q3 26 → Q2 27) with named owners, freeze window, five risks, five binding actions. |
| **`decision-sprint-dev-sample.pptx`** + `.spec.json` | `verdict-cover` · `kpi-roster` · `retro-3col` · `action-list` | 4 | Engineering sprint W22 report — velocity green / quality amber, sprint retro, W23 actions. |

### Verify they're truly editable

```bash
# verdict slide should have ≥15 native shapes; tables have many more
unzip -p decision-board-brief-sample.pptx ppt/slides/slide3.xml | grep -c "<p:sp>"
```

The decision-matrix slide typically contains 40–55 independent `<p:sp>` elements (header cells, body cells, option labels, score cells, dividers).

### Reuse the specs as templates

```bash
cp samples/decision-tech-roadmap-sample.spec.json my-roadmap.json
# edit my-roadmap.json — change phases, owners, risks
~/.claude/skills/biz-html-viz/scripts/export-decision-pptx.sh my-roadmap.json
```

**Important constraint**: this skill's PPTX path is intentionally **scope-limited**:
- ✅ Editable shapes, KPIs, options tables
- ❌ Animations, transitions, TTS narration

The "decision IS the document" philosophy stays — no motion, no narration. If a decision really needs narration (rare), generate it with viz-deck mode 5 in the `terminal` theme instead.

---

## v2 · 5-dim critique (HTML)

| Sample | Demonstrates |
|---|---|
| `design-critique-sample.html` | Terminal-style 5-dim critique with embedded ECharts radar + Keep / Fix (critical/important/polish) / Quick-Wins punch list |
