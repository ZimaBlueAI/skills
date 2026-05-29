# ZimaBlueAI Agent Skills

> **Production-grade skill packs for modern AI coding agents.**
> Write once, ship across harnesses.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.5.0-2b6cb0.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-public_preview-orange.svg)](#9-roadmap)
[![Harness](https://img.shields.io/badge/harness-Claude_Code_·_Codex-7c3aed.svg)](./claude-code-skills/)
[![Channel](https://img.shields.io/badge/channel-OpenClaw_·_Hermes-0E7C66.svg)](./openclaw-skills/)
[![Maintainer](https://img.shields.io/badge/maintainer-ZimaBlueAI-111.svg)](https://github.com/ZimaBlueAI)

[中文版](./README.md) · [Install guide](./claude-code-skills/skills-install-guide.md) · [Channel delivery · OpenClaw](./openclaw-skills/USAGE.md) / [Hermes](./hermes-skills/USAGE.md) · [Changelog](./CHANGELOG.md) · [Contributing](./CONTRIBUTING.md)

---

## 1. What is this

**ZimaBlueAI Agent Skills** is a curated set of **declarative capability packs** for modern AI agents — launching with **Claude Code + OpenAI Codex CLI dual-harness** support, and **as of v0.5 a "channel delivery layer" on OpenClaw / Hermes** that lets the same generation power **converse, generate, and deliver the artifact back into an IM channel** (Feishu and friends). Octarus is still on the roadmap.

> Three ways to use it, one sentence: in **Claude Code / Codex** it's a capability pack for your coding agent; in **OpenClaw / Hermes** it's the Feishu-group bot that, when you @-mention it, builds an animated report / PPT / chart and sends it right back. Same generators, two delivery surfaces.

Each skill ships as a self-contained `.zip` archive. **The same content** is installed into each harness's expected directory:

```
Claude Code:                          Codex CLI:
.claude/                              .agents/
├── agents/         subagents (.md)   └── skills/<name>/   # skill body (identical to Claude)
└── skills/<name>/  skill body        .codex/
    ├── SKILL.md    trigger + workflow └── agents/        subagents (.toml)
    ├── references/ workflow refs
    ├── templates/  deliverable templates
    └── scripts/    optional scripts
```

Skill content (SKILL.md / references / templates / scripts) is **byte-for-byte identical** between the two harnesses. Only the install path and subagent serialization format differ.

The agent loads a skill when a user expresses the matching intent, and produces a structured deliverable. This is **not a library** and **not an npm package** — it's a capability declaration consumed by the agent.

---

## 2. What ships in v0.4.0

Three skills cover the full chain from **board brief to outbound keynote video to truly editable PPT**; **launches simultaneously on Claude Code and OpenAI Codex CLI**. All skills are independent — pick what you need.

| Skill | One line | Output | Zip size |
|---|---|---|---|
| **biz-decision-stack** | 8 subagents · investor → CEO → architect → MRD → delivery → retro → critique + **template router** (v4) | 8 terminal-grade HTML reports + editable PPTX (black + acid-yellow + mono + zero-motion) | 83 KB |
| **viz-deck** | 5 production modes + 6 v4 enhancements (Speaker Mode / 3-variant preview / Doc→Deck / academic talk / bento grid / reflective loop) | HTML / editable PPTX (every element clickable) / MP4 / GIF / PDF (deep-space cyan/blue/gold) | 130 KB |
| **viz-charts** | 6 visual layers · Mermaid · ECharts · SVG widgets · 3D KG · motion video · native PPTX charts | Inline HTML / offline SVG / MP4 / data-bound PPTX charts | 157 KB |

### 🆕 Channel delivery layer · OpenClaw / Hermes (new in v0.5)

The three skills above only **generate**. v0.5 adds a **conversation + delivery** layer on the **OpenClaw** and **Hermes** IM-gateway agents via the new **`viz-channel`** skill: a user says one line in a Feishu channel, and the agent **clarifies the request → generates with viz-deck/viz-charts → sends the file back into the same chat**.

```
User @-mentions the bot in Feishu: "make me an animated Q2 deck"
   → clarify in-channel (≤2 questions, sensible defaults)
   → viz-deck builds animated HTML (charts / 3D KG from viz-charts)
   → deliver deck.html back to the current chat ("download & open in a browser")
```

| | Details |
|---|---|
| **Default style** | **ZimaBlue Editorial** — warm paper background + deep-teal primary + gold/terracotta accents + hairline cards + a teal→gold→red top rule; clean, professional, presentation-ready (switchable in one sentence); see `viz-channel/references/default-style.md` |
| **Form** | Default animated HTML; "make it editable" → PPTX; "play it in the group" → MP4; "draw a chart / knowledge graph" → chart / 3D KG |
| **Transport** | Channel adapter, **current impl = Feishu / Lark** (prefers a lark-cli token, falls back to REST); seam left for WeCom / Slack / Telegram |
| **Packaging** | Thin bridge + installer: viz-deck/viz-charts bodies are vendored from `claude-code-skills/` into the target platform — no duplication |
| **Hermes-only** | The same chain can run as a **cron / webhook** routine (scheduled weekly deck to a group, event-triggered chart push) |

📦 [`openclaw-skills/`](./openclaw-skills/) · [`hermes-skills/`](./hermes-skills/) — each ships the `viz-channel` skill, one-command installers (`.sh`/`.ps1`), and a **[USAGE.md](./openclaw-skills/USAGE.md) case library** (quarterly deck / editable PPT / 3D knowledge graph / launch hero video / competitive landscape / in-group revisions / custom brand style; Hermes adds 2 automation cases).

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

### 4.1 Install skills into your harness of choice

```bash
git clone --depth=1 https://github.com/ZimaBlueAI/skills.git
cd skills
```

**A · Claude Code** (recommended for first validation, single project):

```bash
cd claude-code-skills
# Unzip into the root of your project (next to .git)
unzip -o biz-decision-stack/biz-decision-stack.zip -d /path/to/your-project/
unzip -o viz-deck/viz-deck.zip                       -d /path/to/your-project/
unzip -o viz-charts/viz-charts.zip                   -d /path/to/your-project/
# Or globally: unzip -o ... -d ~/
```

**B · OpenAI Codex CLI** (one-shot script):

```bash
cd codex-skills
bash install.sh                    # Linux/macOS — installs to ~/.agents/skills/ + ~/.codex/agents/
# Windows: .\install.ps1
```

For project-level vs global installs, optional bridge setup, etc. see [`claude-code-skills/skills-install-guide.md`](./claude-code-skills/skills-install-guide.md) and [`codex-skills/INSTALL.md`](./codex-skills/INSTALL.md).

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

Every skill ships a `samples/` directory with **real rendered deliverables** you can open immediately. Full catalog in each skill's `samples/SAMPLES.md`. Highlights:

### v3 · PPTX samples (11 deliverables, each with `.spec.json` starter)

| Group | Files | One-liner |
|---|---|---|
| **biz-decision-stack · 4 decision PPTX** | [`decision-board-brief-sample.pptx`](./claude-code-skills/biz-decision-stack/samples/decision-board-brief-sample.pptx) · [`decision-retro-report-sample.pptx`](./claude-code-skills/biz-decision-stack/samples/decision-retro-report-sample.pptx) · [`decision-tech-roadmap-sample.pptx`](./claude-code-skills/biz-decision-stack/samples/decision-tech-roadmap-sample.pptx) · [`decision-sprint-dev-sample.pptx`](./claude-code-skills/biz-decision-stack/samples/decision-sprint-dev-sample.pptx) | Terminal-themed editable: board brief · quarterly retro · 4-quarter tech roadmap · weekly sprint. 15–55 independent clickable shapes per slide. See [SAMPLES.md](./claude-code-skills/biz-decision-stack/samples/SAMPLES.md) |
| **viz-deck · 3 decks** (mode 5) | [`editable-deck-sample.pptx`](./claude-code-skills/viz-deck/samples/editable-deck-sample.pptx) · [`product-launch-deck-sample.pptx`](./claude-code-skills/viz-deck/samples/product-launch-deck-sample.pptx) · [`all-layouts-showcase-sample.pptx`](./claude-code-skills/viz-deck/samples/all-layouts-showcase-sample.pptx) | Deep-space board update (9 slides) · deck-light product launch (10 slides) · 8-layout reference (8 slides). See [SAMPLES.md](./claude-code-skills/viz-deck/samples/SAMPLES.md) |
| **viz-charts · 4 native data-bound charts** | [`native-chart-sample.pptx`](./claude-code-skills/viz-charts/samples/native-chart-sample.pptx) · [`chart-trend-line-sample.pptx`](./claude-code-skills/viz-charts/samples/chart-trend-line-sample.pptx) · [`chart-market-share-doughnut-sample.pptx`](./claude-code-skills/viz-charts/samples/chart-market-share-doughnut-sample.pptx) · [`chart-critique-radar-sample.pptx`](./claude-code-skills/viz-charts/samples/chart-critique-radar-sample.pptx) | column · line · doughnut · radar — four chart types. Right-click → "Edit Data" in PowerPoint opens the underlying spreadsheet. See [SAMPLES.md](./claude-code-skills/viz-charts/samples/SAMPLES.md) |

### v2 · HTML / video / critique samples

| Skill | Sample | What you see |
|---|---|---|
| biz-decision-stack | [`design-critique-sample.html`](./claude-code-skills/biz-decision-stack/samples/design-critique-sample.html) | Terminal-style 5-dim critique with ECharts radar and a Keep / Fix / Quick-Wins list |
| viz-deck | [`motion-stage-sample.html`](./claude-code-skills/viz-deck/samples/motion-stage-sample.html) + [`.mp4`](./claude-code-skills/viz-deck/samples/motion-stage-sample.mp4) | Keynote-grade motion stage source HTML plus a recorded 1920×1080 MP4 |
| viz-deck | [`design-critique-sample.html`](./claude-code-skills/viz-deck/samples/design-critique-sample.html) | Keynote-style 5-dim critique (deep-space palette) |
| viz-charts | [`trend-motion-sample.html`](./claude-code-skills/viz-charts/samples/trend-motion-sample.html) + [`.mp4`](./claude-code-skills/viz-charts/samples/trend-motion-sample.mp4) | ECharts multi-series reveal animation with recorded MP4 |
| viz-charts | [`demo-3d-code-kg.html`](./claude-code-skills/viz-charts/demo-3d-code-kg.html) · [`demo-3d-doc-kg.html`](./claude-code-skills/viz-charts/demo-3d-doc-kg.html) | 3D code/doc knowledge graphs (80 / 92 nodes, interactive) |
| viz-charts | [`demo-terminal.html`](./claude-code-skills/viz-charts/demo-terminal.html) · [`demo-deck.html`](./claude-code-skills/viz-charts/demo-deck.html) | Full component showcase in both themes |

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
skills/
├── LICENSE                        Apache 2.0 full text
├── NOTICE                         Copyright / trademark / third-party
├── README.md                      Chinese landing page
├── README_en.md                   English landing page (this file)
├── CHANGELOG.md                   Version history
├── CONTRIBUTING.md                Contribution guidelines
├── CODE_OF_CONDUCT.md             Community code of conduct
│
├── claude-code-skills/            ★ Claude Code harness (published)
│   ├── skills-install-guide.md    End-to-end install/config/usage covering all three
│   ├── skills-install-guide.html
│   │
│   ├── biz-decision-stack/
│   │   ├── biz-decision-stack.zip Installable archive
│   │   ├── README.md              Per-skill notes
│   │   └── samples/               5-dim critique + decision PPTX + v0.4 template-router cases
│   │
│   ├── viz-deck/
│   │   ├── viz-deck.zip
│   │   ├── viz-deck-README.md
│   │   ├── design-system-deck.md  Public design spec
│   │   ├── research-playbook.md   Tier 1/2/3 competitive research protocol
│   │   ├── sample-board-brief.html
│   │   └── samples/               5-mode samples + v0.4 Speaker / 3-variant / Doc→Deck / Academic / Bento / Reflect
│   │
│   └── viz-charts/
│       ├── viz-charts.zip
│       ├── demo-*.html            Four interactive showcases
│       └── samples/               motion chart (v0.2) + native PPTX chart (v0.3)
│
├── codex-skills/                  ★ OpenAI Codex CLI harness (v0.4, same content)
│   ├── README.md                  Codex-flavored intro
│   ├── INSTALL.md                 Codex install guide
│   ├── install.sh / install.ps1   One-shot install scripts
│   ├── biz-decision-stack/        Includes .agents/skills/ + 8 TOML agents
│   ├── viz-deck/                  Includes .agents/skills/viz-deck/
│   └── viz-charts/                Includes .agents/skills/viz-charts/
│
├── codex-skills/                  ★ OpenAI Codex CLI harness (released v0.4, same source as Claude)
│
├── openclaw-skills/               ★ OpenClaw channel-delivery layer (released v0.5)
│   ├── README.md · USAGE.md (9 cases)
│   ├── install-openclaw-skills.sh / .ps1   one-command installer (thin bridge)
│   └── skills/viz-channel/        conversation + channel delivery skill
│       ├── SKILL.md               trigger + clarify→generate→deliver workflow
│       ├── references/            channel-protocol · delivery-matrix · openclaw-channel
│       └── scripts/               channel_deliver.py · channel_send.sh/.ps1 · resolve_chat.py
│
├── hermes-skills/                 ★ Hermes channel-delivery layer (released v0.5, + cron/webhook)
│   ├── README.md · USAGE.md (11 cases)
│   ├── install-hermes-skills.sh / .ps1
│   └── skills/viz-channel/        same as OpenClaw; references use hermes-channel (+automation)
│
└── octarus-skills/                ☐ Octarus (planned)
```

> `viz-deck` / `viz-charts` / `biz-html-viz` bodies are **not** inside the openclaw/hermes dirs — the installer vendors them from `claude-code-skills/*.zip`, so the heavy skills stay single-source.

---

## 8. Who should use what

| Role | Recommended bundle | Why |
|---|---|---|
| **Startup CEO** | biz-decision-stack (all) + viz-deck (stage-report) + ppt-master | Internal decision chain in HTML + outbound keynote + editable PPT for the board |
| **Product manager** | biz-decision-stack (PM modes) + viz-deck (prototype) + viz-deck (pptx-deck) | MRD as docs + hi-fi prototype to align engineering + PRD review PPT for business |
| **Chief architect** | biz-decision-stack (architect) + viz-deck (architecture-deep) + viz-charts | Internal ADRs + customer-facing technical decks + 3D code KG |
| **Investor / FA** | viz-deck (competitive-landscape) + viz-charts + viz-charts (native chart pptx) | Live competitive research + animated data for roadshows + LP monthly data PPT |
| **Design / brand lead** | viz-deck (all 5 modes) + huashu-design + ppt-master | One toolchain for prototype / slides / video / critique / shippable PPT |
| **Engineering lead** | biz-decision-stack (dev-test) + viz-charts (3D KG) | Status reporting + project structure visualization |
| **Anyone in a Feishu group** (ops/sales/exec) | OpenClaw / Hermes + `viz-channel` | No CLI — @-mention the bot in chat and an animated report / PPT / chart comes back |

---

## 9. Roadmap

| Phase | Scope | Status |
|---|---|---|
| v0.1 | Initial release of the claude-code-skills trio | ✅ Released |
| v0.2 | 4 output modes · 20 philosophies · 5-dim critique · huashu-design bridge · samples | ✅ Released |
| v0.3 | ppt-master soft bridge · viz-deck mode 5 pptx-deck · decision PPTX · data-bound native chart · TTS narration embed · codex-skills dual-harness launch | ✅ Released |
| v0.4 | 26-skill cross-pollination · Speaker Mode · 3-variant preview · Doc→Deck · Academic Talk · Bento Grid · Reflective Loop · Template Router | ✅ Released |
| **v0.5** | **OpenClaw / Hermes channel-delivery layer · `viz-channel` (in-channel conversational generation + delivery · Feishu adapter · cron/webhook automation · USAGE case library)** | ✅ **Released (current)** |
| v0.6 | viz-charts narrative chart explainer (TTS-narrated chart videos) + channel adapters (WeCom / Slack / Telegram) | 🟡 Planned |
| v0.7 | `octarus-skills/` + tri-harness consistency tests | ⚪ Planned |
| v1.0 | All 5 harnesses + skill registry (`skills.json` index) | ⚪ Planned |

---

## 10. Contributing

Issues and PRs are welcome. Please read [CONTRIBUTING.md](./CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) first.

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
