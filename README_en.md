# ZimaBlueAI Agent Skills

> **Production-grade skill packs for modern AI coding agents.**
> Write once, ship across harnesses.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.7.0-2b6cb0.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-public_preview-orange.svg)](#9-roadmap)
[![Harness](https://img.shields.io/badge/harness-Claude_Code_·_Codex-7c3aed.svg)](./packaging/build.py)
[![Source](https://img.shields.io/badge/source-single_tree-0E7C66.svg)](./packaging/build.py)
[![Maintainer](https://img.shields.io/badge/maintainer-ZimaBlueAI-111.svg)](https://github.com/ZimaBlueAI)

[中文版](./README.md) · [Install guide](./docs/install-guide.md) · [Changelog](./CHANGELOG.md) · [Contributing](./CONTRIBUTING.md)

---

## 1. What is this

**ZimaBlueAI Agent Skills** is a curated set of **declarative capability packs** for modern AI
agents, installable on both **Claude Code** and **OpenAI Codex CLI**. An agent loads a skill when
the user expresses the matching intent and produces a structured deliverable. This is **not a
library** and **not an npm package** — it's a capability declaration consumed by the agent.

**One source, two harnesses.** Each skill sits directly at the repository root;
`packaging/build.py` produces the installable archives for both:

```
<skill-name>/           ★ the only source — edit here
├── SKILL.md            trigger + workflow
├── references/         workflow references
├── templates/          deliverable templates
├── scripts/            optional tooling
└── samples/            openable sample output
        │
        │  python packaging/build.py
        ▼
dist/claude/*.zip  →  unzip into ~/  →  .claude/skills/<name>/ + .claude/agents/*.md
dist/codex/*.zip   →  unzip into ~/  →  .codex/skills/<name>/  + .codex/agents/*.toml
```

The two harnesses differ in exactly two ways, both declared in `packaging/harness.toml`: the
**install root** (`.claude/` vs `.codex/`) and a **shorter `description`** for three older skills
on the Codex side (Codex's frontmatter parsing prefers short prose, so the markdown bold and the
long Chinese trigger list are stripped). Skill bodies, references, templates, scripts and samples
are byte-for-byte identical — two trees can no longer drift apart.

---

## 2. Skills in this repository

From v0.4.0 onward, the suite covers the full chain from **board brief to outbound keynote video to truly editable PPT** and ships for both **Claude Code and OpenAI Codex CLI**. **v0.7 adds the in-house design ensemble engine `zima-design`**. The latest pass gives `zima-html-ppt` a governance layer and turns `produce-cinematic-video` into a release-hardened ZimaBlueAI production skill with recoverable projects and explicit privacy, rights, cost, and publication gates. All skills are independent — pick what you need.

This tree contains **10 skills**. Eight have Claude Code and Codex ZIP archives in `dist/`. The two Zima Anima skills below are available from source.

| Skill | When to use it | Getting started |
|---|---|---|
| **zima-anima-light** | A young filmmaker or teacher wants a local browser studio for scripts, illustrated style packs, shot review and a dual-monitor editor. | Follow the [local quickstart](./zima-anima-light/README.md). Use Python 3.11+ to launch and FFmpeg/FFprobe to export MP4. |
| **zima-anima-video-editor** | An editor wants an agent to turn a brief or supplied footage into a shot plan, edit and delivery QC report using the tools available to the agent. | Start with the [production playbook](./zima-anima-video-editor/SKILL.md). Provide the audience, target runtime, aspect ratio and available footage. |

**Packaged skills**

| Skill | One line | Output | Zip size |
|---|---|---|---|
| **biz-decision-stack** | 8 subagents · investor → CEO → architect → MRD → delivery → retro → critique + **template router** (v4) | 8 terminal-grade HTML reports + editable PPTX (black + acid-yellow + mono + zero-motion) | ≈226 KB |
| **viz-deck** | 5 production modes + 6 v4 enhancements (Speaker Mode / 3-variant preview / Doc→Deck / academic talk / bento grid / reflective loop) | HTML / editable PPTX (every element clickable) / MP4 / GIF / PDF (deep-space cyan/blue/gold) | ≈432 KB |
| **viz-charts** | 7 visual layers · Mermaid · ECharts · SVG widgets · 3D KG · **interactive SVG ring/Circos KG** · motion video · native PPTX charts | Inline HTML / offline SVG / interactive SVG KG / MP4 / data-bound PPTX charts | ≈453 KB |
| **zima-html-ppt** | ZimaBlueAI live-talk deck · warm-paper editorial + **Speaker Mode** (S key → teleprompter / script / timer / agenda) · masters D1/D2/D3 · **v2 governance layer**: proposal-first deck-plan + `deck.json ↔ HTML` build/extract round-trip + **seven gates** + missing-evidence discipline | single-file HTML slides (warm paper + deep teal + gold + tri-color bar) · deck.json source of truth · JSON gate report | ≈101 KB · Python 3 for build/validate |
| **produce-cinematic-video** | Recoverable ZimaBlueAI media-production skill: research and planning → 7 specialist stations → generation/edit/sound → QC and performance diagnosis, with separate gates for upload, spend, and voice cloning | plans, scripts, storyboards, character packs, project dashboard, masters/stems, QC and evaluation reports | ≈330 KB · Python 3 + full FFmpeg; models optional |
| **web-shader-extractor** 🆕 (ported · not ZimaBlue suite) | **Extract & evidence-matched local replay** of webpage WebGL/WebGPU/Canvas shader effects (Recon Kernel state machine + 6 core rules) · ported from [lixiaolin94/skills](https://github.com/lixiaolin94/skills) (MIT) | extraction/replay project + 4 self-contained demos (incl. a logo-vectorized generative-fold 3D use case) | ≈603 KB · zero hard deps |
| **gzh-design** 🆕 (ported · not ZimaBlue suite) | **WeChat Official Account article typesetting**: Markdown/docx/PDF/plain text → paste-safe WeChat-editor HTML (6 themes + theme generator + dual-gate validation + one-click copy preview) · ported from [isjiamu/gzh-design-skill](https://github.com/isjiamu/gzh-design-skill) (AGPL-3.0) | clean body HTML + a preview page with a "copy to WeChat" button | ≈221 KB · zero hard deps |
| **zima-design** 🆕 | **Design ensemble engine**: an original routing protocol conducting three built-in engines — anti-slop (21 macrostructures × 20 themes × **57 slop-test gates**, from [nutlope/hallmark](https://github.com/nutlope/hallmark)) + motion (animation decision framework / spring physics / performance rules, from [emilkowalski/skills](https://github.com/emilkowalski/skills)) + database (**84 styles / 192 palettes / 74 font pairings / 98 UX guidelines / 22 stacks** searchable, from [ui-ux-pro-max](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill)) — bridging impeccable / huashu-design / taste-engine · **a five-axis diversity protocol guarantees no two deliveries share a skeleton** | pages double-stamped with a design signature + six-axis self-critique / audit reports / stack-aware style picks + a 3-piece demo set | ≈3.6 MB · Python 3 for database search |

### 🆕 zima-html-ppt v2: from "fork the template" to a governed delivery chain

A deck you can't edit isn't finished. v1 only produced the file — revising it meant re-reading
eight hundred lines of single-file HTML, there was no source of truth, and correctness rested on
one human scanning a checklist before delivery. v2 borrows the workflow skeleton and gate ladder
from [joeseesun/qiaomu-bento-ppt](https://github.com/joeseesun/qiaomu-bento-ppt) (MIT · 向阳乔木) —
**the discipline only, not its bundled 600 KB bento shell**. The visual system and Speaker Mode
remain ZimaBlue Editorial's own (attribution in `zima-html-ppt/NOTICE.md`).

| Capability | What it means |
|---|---|
| **Source of truth + round-trip** | Every output embeds its own `deck.json` in a trailing `<script id="zima-doc">`. Revising is `extract` → edit JSON → `build` — **no re-reading HTML**; `extract(build(x)) == x` byte-for-byte, guarded by a regression case |
| **Identity preservation** | `deckId` is minted once at creation; on revision a mismatched `--identity-source` refuses the build outright. Output defaults to a sibling file — the source HTML is never touched |
| **Seven gates** | Route / Structure / Identity / Shell / Quality / Browser / Rollback. The structure gate carries 38 errors + 14 warnings, split by one test: not "is this important" but "if this is missing, what happens on stage" |
| **Evidence discipline** | Every report ships carrying `missing evidence: browser visual review` — until a human actually opens the browser, you may not write "verified" |
| **Proposal first** | Intent card → three directions (`1a` persuade / `2b` decide / `3c` train) → a per-slide plan table with a **visual owner** column: each fact is owned by exactly one layer (title / chart / card / body / script), and what's on screen may never be what's in your mouth |
| **31 regressions** | 15 gate cases (good deck passes, bad deck caught by category, round-trip identical) + 16 routing-boundary cases (10 of which must be handed off to sibling skills) |

**The new discipline paid for itself immediately**: running the fresh browser-review checklist
surfaced three rendering defects that had been in the D1/D2/D3 masters all along — the comparison-bar
component **had never rendered at all** (an `<i>` defaults to `display:inline`, so the bar was 0×0),
the footer's right side sat under the fixed pager control, and the desktop view could still be
dragged 25px sideways. All three are fixed; the first is now a shell-gate signature so it can't regress.

The skill ships an `examples/` folder with one delivery that walked the whole chain (plan +
`deck.json` + a 14-slide deck + gate report). Its subject is this very upgrade, and every number
traces back to a code count or test output.

### 🆕 zima-design: the design ensemble engine + anti-AI-slop upgrade across the line

New in-house skill **`zima-design`** — three complementary design intelligences conducted by one original routing protocol: **structural & thematic variety** (anti-slop engine: 21 rotating macrostructures + 57 slop-test gates + audit/redesign verbs), **motion & feel** (motion engine: the frequency → purpose → easing → duration decision framework; "should it animate" comes before "how"), and **data-backed selection** (database engine: 84 styles / 192 palettes / 98 UX guidelines searched locally). A **five-axis diversity protocol** (macrostructure × theme × motion personality × card physics × density rhythm) forces consecutive deliveries to never share a template skeleton — the ensemble answer to AI-template sameness. All three engines are byte-for-byte MIT imports (provenance in `zima-design/NOTICE.md`), with external bridges to impeccable / huashu-design / taste-engine. Ships a 3-piece demo: a deliberately sloppy specimen page (12 tagged slop tells) → an audit report (17/24 gates FAIL) → the redesigned counterpart. In the same pass, every generating skill in this repo — `viz-deck` / `viz-charts` / `biz-html-viz` (biz-decision-stack) / `zima-html-ppt` / `viz-channel` — now inlines a **hard anti-slop gate** in its SKILL.md: six disciplines (pre-emit six-axis self-critique / no invented metrics / locked color+font tokens / no re-drawn fake chrome / 320–768 px responsive floor / no italic headers), auto-bridging to the full 57 gates when zima-design is installed. `taste-engine`'s preflight absorbs the same distillation.

### Channel delivery layer · retired

v0.5 shipped a channel-delivery layer on the OpenClaw / Hermes IM gateways (`viz-channel` /
`gzh-channel` — converse in a Feishu group, generate, and get the artifact back in-thread).
It has been removed: **both of those harnesses can install this repo's Claude / Codex packages
directly**, so maintaining a thin bridge on top was duplicated work. The implementation lives on
in git history.

### What's new in v0.4 (vs v0.3 — 26-skill cross-pollination)

After studying [a comprehensive survey of 26 open-source PPT-generation Agent Skills](https://mp.weixin.qq.com/s/gaNsToTe33IPXIddesJs1g) (≈70k+ aggregate stars), this release imports the highest-value patterns from peer skills. **All v0.3 workflows preserved** — every addition is additive.

- ✨ **viz-deck · Speaker Mode** (from [html-ppt-skill](https://github.com/lewislulu/html-ppt-skill) 3.8k★): press **S** to pop an independent presenter window with 4 magnetic cards (current / next preview / teleprompter / timer). BroadcastChannel keeps both windows in sync. Three layout presets (GRID / PROMPTER / DUO).
- ✨ **viz-deck · Show-Don't-Tell 3-variant preview** (from [frontend-slides](https://github.com/zarazhangrui/frontend-slides) 17.5k★): when input is ambiguous, render 3 contrasting hero mockups side-by-side so users can pick a visual direction by sight. 5 scene presets pick a cross-school philosophy triple.
- ✨ **viz-deck · Doc→Deck converter** (from [odin-slides](https://github.com/leonid20000/odin-slides) 147★ + [colloquium](https://github.com/natolambert/colloquium) 190★): convert `.md` / `.docx` / `.pdf` (via pandoc pre-flight) directly into `pptx-deck-spec.json`. Auto-detects chapters, tables → KPI grid, quote blocks → pullquote.
- ✨ **viz-deck · Academic Talk template** (from [academic-pptx-skill](https://github.com/Gabberflast/academic-pptx-skill) 387★): mode-1 sub-template with mandatory action titles (verb-driven, not noun phrases), numbered citations, anticipated Q&A, and limitations.
- ✨ **viz-deck · Bento Grid layout** (from [apple-bento-grid](https://github.com/hubeiqiao/apple-bento-grid) 171★): Apple-inspired feature-overview page, plus a 9th native PPTX layout `bento-grid` with 3-column responsive packing and three accent variants.
- ✨ **viz-deck · Reflective Loop** (from [PPTAgent](https://github.com/icip-cas/PPTAgent) 4.4k★): after spec generation, auto-run per-page 5-dim critique. Pages below threshold get listed in `redo-prompts.txt`. HTML report includes radar + per-slide score table.
- ✨ **biz-decision-stack · Template Router** (from [mckinsey-pptx](https://github.com/seulee26/mckinsey-pptx) 426★): the 9th subagent. Scores ambiguous user input against an 8-template, 5-dimension routing rubric, then writes a one-paragraph justification into the chosen HTML's header comment — never silent, always defended.

### What was new in v0.3 (vs v0.2)

- ✨ **ppt-master soft bridge**: via [`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master)'s python-pptx + SVG→DrawingML pipeline, every skill now exports `.pptx` files where **every visual element is an independently clickable native shape** — not flattened images
- ✨ **viz-deck mode 5 · pptx-deck**: JSON deck spec → per-slide SVG → ppt-master → `.pptx`. 8 layouts (cover / agenda / section / bullets / two-column / kpi-grid / pullquote / closing), three themes (deep-space / terminal / deck-light)
- ✨ **TTS narration embedding**: free edge-tts + paid ElevenLabs / MiniMax / Qwen / CosyVoice voice-clone backends. PowerPoint File → Export → Video produces an MP4 with narration + animations auto-synced
- ✨ **biz-decision-stack editable PPTX**: 8 decision-specific layouts (verdict-cover / kpi-roster / decision-matrix / roadmap-phases / risks-grid / retro-3col / action-list / summary-stack), zero motion preserves the scan-and-sign philosophy
- ✨ **viz-charts native data-bound charts**: ECharts spec → `.pptx` containing a real `<c:chart>` object. Stakeholder right-clicks → "Edit Data" → spreadsheet editor opens with the underlying values
- ✨ Every skill ships a v3 sample PPTX in `samples/`

### What was new in v0.2 (vs v0.1)

- ✨ viz-deck expanded from 1 output mode to 4 (hi-fi prototype / slide deck / motion MP4 / original stage report)
- ✨ 20 design philosophies and 5-dimension expert critique integrated
- ✨ HTML → MP4 / 60fps / GIF toolchain via huashu-design bridge
- ✨ biz-decision-stack 7th subagent `design-critic` + `design-critique.html`

Full notes in the [CHANGELOG](./CHANGELOG.md).

---

## 3. Two soft bridges

v0.2 added the first soft bridge: [`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design) (motion / video / design philosophies / critique). v0.3 adds a second: [`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master) (python-pptx + SVG→DrawingML — truly editable native PPTX).

**v0.2 · huashu-design** (Node + Playwright + ffmpeg):
- **viz-deck** modes 2-4 (prototype / slide-deck / motion-stage) use it for MP4/PPTX export, device frames, animation engine, 20 philosophies, 5-dim critique
- **biz-decision-stack** only borrows the critique standard (decisions stay zero-motion by principle — no motion / BGM / device frames imported)
- **viz-charts** motion mode calls `render-video.js` directly for screen recording

**v0.3 · ppt-master** (Python + python-pptx + svglib + edge-tts):
- **viz-deck** mode 5 (pptx-deck): JSON spec → SVG → true DrawingML PPTX with optional TTS narration
- **biz-decision-stack**: 8 decision-specific layouts as terminal-themed editable PPTX
- **viz-charts**: ECharts spec → data-bound native `<c:chart>` object

Both bridges are **soft dependencies**: without them, v1 / v2 capabilities (HTML reports / decision chain / static charts) remain fully functional. ppt-master is MIT-licensed; huashu-design is free for personal use, **commercial use requires a separate license** from its author — see each project's LICENSE.

```
        ┌──────────────────────────┐     ┌────────────────────────────┐
        │ huashu-design (v0.2)     │     │ ppt-master (v0.3)          │
        │ - MP4 / 60fps / GIF      │     │ - python-pptx              │
        │ - HTML→PPTX (text-only)  │     │ - SVG→DrawingML (clickable)│
        │ - 20 design philosophies │     │ - master/template inherit  │
        │ - 5-dim critique std     │     │ - TTS narration embed      │
        │ - iOS/Android frames     │     │ - native data-bound charts │
        └────────────┬─────────────┘     └──────────────┬─────────────┘
                     │                                  │
       ┌─────────────┼──────────────┐    ┌──────────────┼─────────────┐
       ▼             ▼              ▼    ▼              ▼             ▼
┌─────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌─────────────┐
│ viz-charts  │ │   viz-deck   │ │ biz-decision-    │ │   shared    │
│ (motion +   │ │ (modes 2-4 + │ │     stack        │ │  install    │
│  pptx chart)│ │   mode 5)    │ │ (critique+pptx)  │ │             │
└─────────────┘ └──────────────┘ └──────────────────┘ └─────────────┘
```

---

## 4. Five-minute quickstart

### 4.1 Build and install

Use the source links above for the two Zima Anima skills. To install the eight existing packages, use the checked-in archives with the installer. Rebuilding all archives from this tree requires adding the two new skills to `packaging/harness.toml` first; the build checks every root skill against that manifest.

```bash
git clone --depth=1 https://github.com/ZimaBlueAI/skills.git
cd skills

bash packaging/install.sh            # auto-detects ~/.claude / ~/.codex and installs
```

Common installer flags:

```bash
bash packaging/install.sh --harness claude          # Claude Code only
bash packaging/install.sh --harness both            # both harnesses
bash packaging/install.sh --skill viz-deck          # a single package
bash packaging/install.sh --project /path/to/repo   # install into a project, not $HOME
bash packaging/install.sh --dry-run                 # print only
```

On Windows use `.\packaging\install.ps1` with the same switches (`-Harness` / `-Skill` /
`-Project` / `-DryRun`). Prefer doing it by hand? `unzip -o dist/claude/viz-deck.zip -d ~/`
(or into a project root, next to `.git`).

> `dist/` holds **build output** generated from `skills/`. To change anything, edit
> `skills/<name>/` and re-run the build — edits inside `dist/` are overwritten next time.

For project-vs-global installs and the optional bridges, see
[`docs/install-guide.md`](./docs/install-guide.md); Codex-specific notes are in
[`docs/install-guide-codex.md`](./docs/install-guide-codex.md).

### 4.2 Optional · install huashu-design to unlock v2 (motion / video / philosophies / critique)

```bash
git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.claude/skills/huashu-design
cd ~/.claude/skills/huashu-design

# Node runtime (playwright + sharp + pptxgenjs + pdf-lib)
cat > package.json <<'JSON'
{
  "name": "huashu-design-runtime",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "playwright": "^1.48.0",
    "sharp": "^0.33.5",
    "pptxgenjs": "^3.12.0",
    "pdf-lib": "^1.17.1"
  }
}
JSON
npm install && npx playwright install chromium

# ffmpeg must be on PATH (used for MP4 encoding and 60fps interpolation)
ffmpeg -version || echo "Please install ffmpeg first"
```

### 4.3 Optional · install ppt-master to unlock v3 (truly editable PPTX)

```bash
git clone --depth=1 https://github.com/hugohe3/ppt-master.git ~/.claude/skills/ppt-master
cd ~/.claude/skills/ppt-master

# Isolated Python 3.10+ venv keeps the system Python clean
python -m venv .venv

# Windows
.venv/Scripts/pip install python-pptx edge-tts svglib reportlab Pillow numpy
# macOS/Linux
# .venv/bin/pip install python-pptx edge-tts svglib reportlab Pillow numpy

# Verify
.venv/Scripts/python -c "import pptx, edge_tts; print('ok')"   # Windows
# .venv/bin/python -c "import pptx, edge_tts; print('ok')"     # macOS/Linux
```

> Skipping either bridge is fine — v1 capabilities (HTML reports / static charts / decision chain) work unchanged. Install huashu to unlock v2 (4-mode output / 20 philosophies / 5-dim critique / MP4); also install ppt-master to unlock v3 (clickable native DrawingML PPTX / TTS narration / master inheritance / data-bound charts).

### 4.4 Verify Claude Code recognizes the skills

```
> /skills
```

You should see `biz-html-viz` · `viz-deck` · `viz-charts`. With huashu installed you'll see a fourth: `huashu-design`. ppt-master is loaded as an internal runtime by the three skills — it doesn't show as its own entry.

### 4.5 Trigger by natural language

| You say | Auto-routes to |
|---|---|
| "Write me a board brief for Rolin" | `01-board-advisor` + `biz-html-viz · board-brief` |
| "Run an all-hands flow" / "走一遍全流程" | `00-all-hands-orchestrator` (chain through 6 roles + critique) |
| "Build a stage-report deck for Mingjing" | `viz-deck · stage-report` (mode 1) |
| "Make an iOS hi-fi prototype" | `viz-deck · prototype` (mode 2) |
| "Build a slide deck" + "export to PPTX" | `viz-deck · slide-mode` (mode 3) + huashu `export_deck_pptx.mjs` |
| "Render this to MP4" / "60fps video" / "explainer with narration" | `viz-deck · motion-mode` (mode 4) + huashu `render-video.js` |
| **"Give me a truly editable PPT" / "something stakeholders can edit in PowerPoint"** | **`viz-deck · pptx-deck` (mode 5) + ppt-master** (v3) |
| **"Turn this decision report into a PPT"** | **biz-html-viz + ppt-master terminal-themed PPTX** (v3) |
| **"Chart data needs to be editable inside PowerPoint"** | **viz-charts + ppt-master native chart** (v3) |
| "Critique this" / "5-dim review" | `07-design-critic` or `viz-deck · review-5dim.mjs` |
| "Add an architecture diagram" / "Add a line chart" | `viz-charts` (auto-picks Mermaid/ECharts by data shape) |
| "Make a 3D code KG of this repo" | `viz-charts · code-kg.mjs` + `templates/kg3d/code-graph.html` |

---

## 5. Samples

Open the samples and example deliveries linked below. Skills that provide a sample catalog list it in `samples/SAMPLES.md`.

### v3 · PPTX samples (11 deliverables, each with `.spec.json` starter)

| Group | Files | One-liner |
|---|---|---|
| **biz-decision-stack · 4 decision PPTX** | [`decision-board-brief-sample.pptx`](./biz-html-viz/samples/decision-board-brief-sample.pptx) · [`decision-retro-report-sample.pptx`](./biz-html-viz/samples/decision-retro-report-sample.pptx) · [`decision-tech-roadmap-sample.pptx`](./biz-html-viz/samples/decision-tech-roadmap-sample.pptx) · [`decision-sprint-dev-sample.pptx`](./biz-html-viz/samples/decision-sprint-dev-sample.pptx) | Terminal-themed editable: board brief · quarterly retro · 4-quarter tech roadmap · weekly sprint. 15–55 independent clickable shapes per slide. See [SAMPLES.md](./biz-html-viz/samples/SAMPLES.md) |
| **viz-deck · 3 decks** (mode 5) | [`editable-deck-sample.pptx`](./viz-deck/samples/editable-deck-sample.pptx) · [`product-launch-deck-sample.pptx`](./viz-deck/samples/product-launch-deck-sample.pptx) · [`all-layouts-showcase-sample.pptx`](./viz-deck/samples/all-layouts-showcase-sample.pptx) | Deep-space board update (9 slides) · deck-light product launch (10 slides) · 8-layout reference (8 slides). See [SAMPLES.md](./viz-deck/samples/SAMPLES.md) |
| **viz-charts · 4 native data-bound charts** | [`native-chart-sample.pptx`](./viz-charts/samples/native-chart-sample.pptx) · [`chart-trend-line-sample.pptx`](./viz-charts/samples/chart-trend-line-sample.pptx) · [`chart-market-share-doughnut-sample.pptx`](./viz-charts/samples/chart-market-share-doughnut-sample.pptx) · [`chart-critique-radar-sample.pptx`](./viz-charts/samples/chart-critique-radar-sample.pptx) | column · line · doughnut · radar — four chart types. Right-click → "Edit Data" in PowerPoint opens the underlying spreadsheet. See [SAMPLES.md](./viz-charts/samples/SAMPLES.md) |

### v2 · HTML / video / critique samples

| Skill | Sample | What you see |
|---|---|---|
| biz-decision-stack | [`design-critique-sample.html`](./biz-html-viz/samples/design-critique-sample.html) | Terminal-style 5-dim critique with ECharts radar and a Keep / Fix / Quick-Wins list |
| viz-deck | [`motion-stage-sample.html`](./viz-deck/samples/motion-stage-sample.html) + [`.mp4`](./viz-deck/samples/motion-stage-sample.mp4) | Keynote-grade motion stage source HTML plus a recorded 1920×1080 MP4 |
| viz-deck | [`design-critique-sample.html`](./viz-deck/samples/design-critique-sample.html) | Keynote-style 5-dim critique (deep-space palette) |
| viz-charts | [`trend-motion-sample.html`](./viz-charts/samples/trend-motion-sample.html) + [`.mp4`](./viz-charts/samples/trend-motion-sample.mp4) | ECharts multi-series reveal animation with recorded MP4 |
| viz-charts | [`demo-3d-code-kg.html`](./viz-charts/demo-3d-code-kg.html) · [`demo-3d-doc-kg.html`](./viz-charts/demo-3d-doc-kg.html) | 3D code/doc knowledge graphs (80 / 92 nodes, interactive) |
| viz-charts | [`demo-terminal.html`](./viz-charts/demo-terminal.html) · [`demo-deck.html`](./viz-charts/demo-deck.html) | Full component showcase in both themes |

### 🆕 zima-html-ppt · one delivery that walked the whole chain

Not a single HTML file but **four artifacts that instantiate the output contract** — read them to
see what a complete delivery looks like:

| File | What you see |
|---|---|
| [`2026-07-27-zima-html-ppt-v2-deck.html`](./zima-html-ppt/examples/2026-07-27-zima-html-ppt-v2-deck.html) | A 14-slide warm-paper editorial deck you can **open and present** (23-minute budget). **S** opens the speaker teleprompter, **F** goes fullscreen. All 5 layouts, 11 of 12 block types (the `html` escape hatch deliberately unused). On slide 10, two bars — one stuck at 0, one filled — are the very bug this release fixed: **the motion is the argument** |
| [`zima-html-ppt-v2-deck-plan.md`](./zima-html-ppt/examples/zima-html-ppt-v2-deck-plan.md) | The proposal: intent card · three directions · per-slide plan (with the visual-owner column) · source inventory · **three items still marked missing evidence** |
| [`zima-html-ppt-v2.deck.json`](./zima-html-ppt/examples/zima-html-ppt-v2.deck.json) | The document source. Edit here and `build` — never touch the HTML |
| [`reports/deck-validation.json`](./zima-html-ppt/examples/reports/deck-validation.json) | The gate report: zero errors, zero warnings, all five machine gates passing |

---

## 6. Design principles

1. **Decouple thinking style from delivery format.**
   Subagents decide "with which identity to think"; skills decide "what shape the output takes." Each migrates to a new harness independently.
2. **HTML over Markdown for decisions.**
   Decision artifacts (board briefs, CEO canvases, retros) ship as HTML — structurally stable, signable, archivable, printable. Markdown is reserved for logs and annotations.
3. **Design system first.**
   Every skill nails its design system (palette / type / spacing / forbidden patterns) **before** writing templates. `references/design-system*.md` is the authoritative definition; templates only implement it.
4. **Less but better.**
   biz-decision-stack's 8 reports share **one** HTML rendering skill, not eight separate ones. One skill, one job, maximum reuse.
5. **Declarative over imperative.**
   A skill is Markdown + templates + optional scripts — not a pile of code. How the harness invokes it is up to the harness.
6. **Portability is a first-class citizen.**
   The core prompt of a skill must port to at least three harnesses (Claude Code / Codex / OpenClaw) without rewriting.
7. **Bridge over embed.**
   From v0.2 on, cross-stack assets (video / audio / device frames) live in a **soft-bridge** dependency rather than being vendored. No version drift, no license entanglement, no bundle bloat.

---

## 7. Repository layout

```
skills/                            ← repository root
├── biz-html-viz/                  ★ 8 decision templates + decision PPTX (ships 9 subagents)
├── viz-deck/                      ★ 5 output modes + design-system-deck.md + research-playbook.md
├── viz-charts/                    ★ 7 visual layers + 4 demo-*.html showcases
├── zima-html-ppt/                 ★ live-talk deck + seven gates + examples/ reference delivery
├── zima-design/                   ★ design ensemble engine (3 engines + five-axis diversity)
├── gzh-design/                    ★ WeChat Official Account typesetting
├── produce-cinematic-video/       ★ recoverable media production (7 stations + safety gates)
├── zima-anima-light/              youth filmmaking studio with a local browser interface
├── zima-anima-video-editor/       agent-led video editing and delivery QC
├── web-shader-extractor/          ★ webpage shader-effect extraction and replay
│      inside each: SKILL.md · references/ · templates/ · scripts/ · samples/
│      root SKILL.md files identify skills; harness.toml declares ZIP contents
│
├── packaging/                     build + install (the only place harness differences live)
│   ├── build.py                   root skills → dist/claude/*.zip + dist/codex/*.zip
│   ├── harness.toml               install-root mapping + Codex description variants
│   ├── agents/claude-md/          9 subagents in Claude Code's .md format
│   ├── agents/codex-toml/         9 subagents in Codex CLI's .toml format
│   └── install.sh / install.ps1   dual-harness installer
│
├── dist/                          build output — do not hand-edit
│   ├── claude/*.zip               unzip into ~/ → .claude/skills/ + .claude/agents/
│   └── codex/*.zip                unzip into ~/ → .codex/skills/  + .codex/agents/
│
├── docs/                          install-guide.md · install-guide-codex.md · codex-notes.md
├── LICENSE · NOTICE · README.md · README_en.md · CHANGELOG.md · CONTRIBUTING.md
└── _trash/                        archive area (retired dirs are moved here, never hard-deleted)
```

> **Edit once, both sides are right.** `claude-code-skills/` and `codex-skills/` used to evolve
> separately — with the result that three skills' sources existed *only* inside the claude-side
> zip (unreadable, undiffable), while `gzh-design` and `produce-cinematic-video` had quietly
> drifted apart. Now each skill has exactly one source.

## 8. Who should use what

| Role | Recommended bundle | Why |
|---|---|---|
| **Startup CEO** | biz-decision-stack (all) + viz-deck (stage-report) + ppt-master | Internal decision chain in HTML + outbound keynote + editable PPT for the board |
| **Product manager** | biz-decision-stack (PM modes) + viz-deck (prototype) + viz-deck (pptx-deck) | MRD as docs + hi-fi prototype to align engineering + PRD review PPT for business |
| **Chief architect** | biz-decision-stack (architect) + viz-deck (architecture-deep) + viz-charts | Internal ADRs + customer-facing technical decks + 3D code KG |
| **Investor / FA** | viz-deck (competitive-landscape) + viz-charts + viz-charts (native chart pptx) | Live competitive research + animated data for roadshows + LP monthly data PPT |
| **Design / brand lead** | viz-deck (all 5 modes) + huashu-design + ppt-master | One toolchain for prototype / slides / video / critique / shippable PPT |
| **Engineering lead** | biz-decision-stack (dev-test) + viz-charts (3D KG) | Status reporting + project structure visualization |
| **Trainer / evangelist** | zima-html-ppt + viz-charts | A single-file HTML deck you actually present, with a teleprompter and full script on **S**; when the course changes per cohort, revise via `deck.json` instead of re-reading HTML |
| **Director / editor / content team** | produce-cinematic-video | Research, script, storyboard, generate, edit, mix, validate, and evaluate in a recoverable project with explicit upload and spend approvals |

---

## 9. Roadmap

| Phase | Scope | Status |
|---|---|---|
| v0.1 | Initial release of the claude-code-skills trio | ✅ Released |
| v0.2 | 4 output modes · 20 philosophies · 5-dim critique · huashu-design bridge · samples | ✅ Released |
| v0.3 | ppt-master soft bridge · viz-deck mode 5 pptx-deck · decision PPTX · data-bound native chart · TTS narration embed · codex-skills dual-harness launch | ✅ Released |
| v0.4 | 26-skill cross-pollination · Speaker Mode · 3-variant preview · Doc→Deck · Academic Talk · Bento Grid · Reflective Loop · Template Router | ✅ Released |
| v0.5 | OpenClaw / Hermes channel-delivery layer · `viz-channel` | ⛔ Removed (both harnesses install this repo's packages directly; the bridge was duplicated maintenance) |
| v0.6 | `taste-engine` shared taste layer (three dials + anti-slop + material/copy) · `viz-charts` interactive SVG ring/Circos KG · `zima-html-ppt` live-talk deck (warm-paper editorial + Speaker Mode) | ✅ Released |
| **v0.7** | **`zima-design` design ensemble engine (three imported engines + five-axis diversity protocol) · hard anti-slop gate inlined across every generating skill** | ✅ **Released (current)** |
| **Unreleased** | **release-hardened `produce-cinematic-video` with a recoverable end-to-end media workflow** (user `.env.local` + TUI · image/video/TTS/source separation · dashboard/history · rights/cost/privacy gates) · **`zima-html-ppt` v2 governance** · **single-source dual-harness build** · channel layer retired | 🟢 Merged to main, awaiting release |
| v0.8 | viz-charts narrative chart explainer (TTS-narrated chart videos) + channel adapters (WeCom / Slack / Telegram) | 🟡 Planned |
| v0.9 | `octarus-skills/` + tri-harness consistency tests | ⚪ Planned |
| v1.0 | All 5 harnesses + skill registry (`skills.json` index) | ⚪ Planned |

---

## 10. Contributing

Issues and PRs are welcome. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) first.

We especially welcome:

- **New harness ports**: bring an existing skill to Codex / OpenClaw / Hermes / Octarus
- **New skill proposals**: open an issue first to scope it — must fit "declarative / portable / lean"
- **More design references**: real-world visual samples beyond the current design system
- **Richer samples**: domain-specific sample outputs (healthcare / finance / education / public sector)

---

## 11. License

Released under the [Apache License 2.0](./LICENSE). Copyright © 2026 ZimaBlueAI.

## 12. Acknowledgements

Standing on the shoulders of giants. The following projects made this repository possible — through ideas, runtimes, or tooling:

**Ideas & methodology**

- [garrytan/gstack](https://github.com/garrytan/gstack) — multi-agent orchestration
- [Lum1104/Understand-Anything](https://github.com/Lum1104/Understand-Anything) — knowledge-graph visualization
- Thariq's early writing on *HTML for Claude Code* — HTML-first for decision content

**v2 bridge dependency** (motion / video / philosophies / critique)

- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) — video / quick-PPTX / device-frame toolchain, 20-philosophy library, 5-dim critique standard

**v3 bridge dependency** (truly editable PPTX / TTS narration / master inheritance / data-bound charts)

- [hugohe3/ppt-master](https://github.com/hugohe3/ppt-master) — MIT · python-pptx + SVG→DrawingML pipeline, edge-tts narration, template import, native chart rendering

**Runtime libraries** (loaded via CDN or npm/pip at render time — not vendored)

- Node-side: [Mermaid](https://mermaid.js.org/) · [Apache ECharts](https://echarts.apache.org/) · [three.js](https://threejs.org/) · [3d-force-graph](https://github.com/vasturiano/3d-force-graph) · [Playwright](https://playwright.dev/) · [ffmpeg](https://ffmpeg.org/) · [pptxgenjs](https://gitbrent.github.io/PptxGenJS/) · [pdf-lib](https://pdf-lib.js.org/)
- Python-side (v3 new): [python-pptx](https://python-pptx.readthedocs.io/) · [edge-tts](https://github.com/rany2/edge-tts) · [svglib](https://github.com/deeplook/svglib) · [reportlab](https://www.reportlab.com/) · [Pillow](https://python-pillow.org/) · [NumPy](https://numpy.org/)

Each retains its upstream license — see [NOTICE](./NOTICE).

---

## Contact

- GitHub: <https://github.com/ZimaBlueAI/skills>
- Issues: <https://github.com/ZimaBlueAI/skills/issues>
- Security: see [CONTRIBUTING.md](./CONTRIBUTING.md)

---

<sub>Made by ZimaBlueAI · 2026</sub>
