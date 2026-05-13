# Changelog

All notable changes to **ZimaBlueAI Agent Skills** are documented here.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

---

## [Unreleased]

### Planned

- `codex-skills/` — port of the three claude-code skills to OpenAI Codex CLI
- Cross-harness consistency test suite
- Skill registry index (`skills.json`)

---

## [0.3.0] — 2026-05-13

### Added — ppt-master soft bridge (true native DrawingML PPTX)

This release adds a **second soft bridge** to
[`hugohe3/ppt-master`](https://github.com/hugohe3/ppt-master) — a
python-pptx + SVG-to-DrawingML pipeline that produces editable `.pptx`
files where **every visual element is an independently clickable native
shape**, not a flattened image. All three skills now expose a PPTX export
path on top of their existing HTML / motion deliverables.

#### `claude-code-skills/viz-deck` — new **mode 5 · pptx-deck**

Was 4 modes (keynote-report / prototype / slide-deck / motion-stage), now 5.

- `scripts/make-pptx-deck.mjs` — JSON deck spec → per-slide SVG (deep-space /
  terminal / deck-light themes) → ppt-master assembles `.pptx`
- `scripts/export-editable-pptx.sh` — entry point wrapper
- `scripts/embed-narration.sh` — TTS (edge-tts / ElevenLabs / MiniMax / Qwen /
  CosyVoice) writes per-slide MP3, then rebuilds `.pptx` with embedded audio
  and slide timings synced to narration length. PowerPoint File→Export→Video
  produces a `.mp4` with narration + animations.
- `templates/pptx-deck-spec.example.json` — 9-slide canonical spec with 8
  layouts (`title-cover`, `agenda`, `section-divider`, `title-bullets`,
  `two-column`, `kpi-grid`, `pullquote`, `closing`)
- `references/pptx-master-bridge.md`, `editable-pptx.md`, `master-templates.md`,
  `narration-pptx.md` — bridge protocol, what's-editable matrix, corporate
  template import via `register_template.py`, TTS provider catalog
- **3 sample PPTX** shipped (each paired with reusable `.spec.json`):
  - `editable-deck-sample.pptx` — Q3 board update, deep-space theme (9 slides, native DrawingML)
  - `product-launch-deck-sample.pptx` — Mingjing public launch, deck-light theme (10 slides)
  - `all-layouts-showcase-sample.pptx` — one slide per layout, layout reference deck (8 slides)
- `samples/SAMPLES.md` — catalog with verification commands and reuse instructions

#### `claude-code-skills/biz-decision-stack` — terminal-themed editable PPTX

- `scripts/make-decision-pptx.mjs` + `scripts/export-decision-pptx.sh` —
  JSON spec → per-slide SVG (locked terminal theme: black + acid-yellow +
  JetBrains Mono) → ppt-master `.pptx`. 8 decision-specific layouts:
  `verdict-cover`, `kpi-roster`, `decision-matrix`, `roadmap-phases`,
  `risks-grid`, `retro-3col`, `action-list`, `summary-stack`
- `specs/board-brief.example.json`, `specs/retro-report.example.json` —
  canonical spec starters mirroring the existing HTML templates
- `references/pptx-master-bridge.md` — narrow bridge protocol (zero motion,
  no narration, no animations — preserves the "decision IS the document"
  philosophy)
- **4 sample PPTX** shipped (each paired with reusable `.spec.json`):
  - `decision-board-brief-sample.pptx` — Q3 board brief, GO verdict (5 slides)
  - `decision-retro-report-sample.pptx` — Q2 retrospective with worked/didn't/change (4 slides)
  - `decision-tech-roadmap-sample.pptx` — 4-quarter tech roadmap with phases, risks, actions (5 slides)
  - `decision-sprint-dev-sample.pptx` — Weekly sprint dev report with KPIs + retro + actions (4 slides)
- `samples/SAMPLES.md` — catalog with verification commands and reuse instructions

#### `claude-code-skills/viz-charts` — native PPTX charts

- `scripts/echarts_to_pptx.py` + `scripts/export-chart-pptx.sh` — chart spec
  (or raw ECharts option) → `.pptx` with a real `<c:chart>` object. Opening in
  PowerPoint exposes "Edit Data" which launches a spreadsheet panel. Supports
  8 chart types (`column`, `bar`, `line`, `area`, `pie`, `doughnut`, `scatter`,
  `radar`) with stacked variants for the first 4
- `specs/revenue-by-quarter.example.json`, `specs/market-share-pie.example.json`,
  `specs/trend-line.example.json` — canonical chart spec starters
- `references/pptx-charts.md` — bridge protocol + when-to-use vs SVG inline,
  ECharts→python-pptx type mapping, composability with viz-deck mode 5
- Three themes (`deep-space`, `terminal`, `deck-light`) with matched series
  palettes
- **4 sample PPTX** shipped (each paired with reusable `.spec.json`):
  - `native-chart-sample.pptx` — quarterly revenue, column chart, deep-space (3 series × 4 quarters)
  - `chart-trend-line-sample.pptx` — 12-month workspaces trend, line chart, deep-space (actual vs plan)
  - `chart-market-share-doughnut-sample.pptx` — vendor market share, doughnut, deck-light (6 categories)
  - `chart-critique-radar-sample.pptx` — v3 release self-critique, radar, terminal (5 axes × 3 series)
- `samples/SAMPLES.md` — catalog with composability tip (mixing chart PPTX into deck PPTX via PowerPoint's "Reuse Slides")

#### `codex-skills/` — dual-harness launch (NEW top-level directory)

- All three skills (biz-decision-stack, viz-deck, viz-charts) now ship a
  second flavor tailored to **OpenAI Codex CLI**'s `.agents/skills/` and
  `.codex/agents/` conventions. **Skill content (SKILL.md, references,
  templates, scripts, specs) is byte-for-byte identical** to the Claude
  Code version; only the install path and subagent serialization differ.
- 8 subagents converted from Claude Code's markdown frontmatter → Codex's
  TOML format (`name`, `description`, `developer_instructions`)
- `codex-skills/install.sh` + `codex-skills/install.ps1` — one-shot
  installer that extracts the three zips to `$HOME/.agents/skills/` and
  TOML agents to `$HOME/.codex/agents/`
- `codex-skills/README.md` — explains the harness mapping
- `codex-skills/INSTALL.md` — Codex-flavored install / config / use guide
  (mirror of `claude-code-skills/skills-install-guide.md`)
- `codex-skills/agents-toml/` — pre-converted TOML subagents (reference copies)
- `.work/build-codex.py` — reproducible Codex-flavor builder

#### Bridge script portability (Claude Code + Codex shared scripts)

The four ppt-master bridge scripts now detect their backing install via a
three-tier search — same script runs on either harness:

```
$PPT_MASTER_HOME → ~/.agents/skills/ppt-master → ~/.claude/skills/ppt-master
```

Patched files: `make-pptx-deck.mjs`, `make-decision-pptx.mjs`,
`export-editable-pptx.sh`, `export-decision-pptx.sh`, `export-chart-pptx.sh`,
`embed-narration.sh`. No fork: a single bridge install serves both harnesses.

#### Repository-wide

- `README.md`, `README_en.md`, `skills-install-guide.md` (Claude) +
  `codex-skills/INSTALL.md` updated with §13 ppt-master bridge protocol
- All three skills' SKILL.md updated to expose the new mode/capability
- `.work/repack-v3.py` — reproducible Claude-flavor zip repacker (Python,
  no `zip` CLI dependency)
- `.work/build-codex.py` — reproducible Codex-flavor builder

### Compatibility

- v0.2 workflows are **fully preserved**. Mode 5 in viz-deck is purely
  additive; modes 1-4 untouched. biz-decision-stack HTML templates and
  viz-charts HTML/SVG rendering are unchanged.
- `ppt-master` is a **soft dependency** alongside `huashu-design`. Installing
  it unlocks the new editable-PPTX paths; without it, v0.2 workflows continue
  to work exactly as before.

### Known constraints

- ppt-master native bridge requires: Python 3.10+ with a venv at
  `~/.claude/skills/ppt-master/.venv/`, packages `python-pptx`, `edge-tts`,
  `svglib`, `reportlab`, `Pillow`, `numpy`
- Custom fonts: PowerPoint substitutes if the viewer's machine lacks the font.
  Stick to system fonts (Inter, JetBrains Mono) or use PowerPoint's font
  embedding before distribution
- SVG filters (drop-shadow, blur) approximate only — use PowerPoint's native
  shape effects after import for high fidelity
- ppt-master is MIT-licensed; this is a runtime soft bridge, not a fork —
  attribution lives in NOTICE and README

---

## [0.2.0] — 2026-05-11

### Added — v2 capability expansion + huashu-design soft bridge

This release reshapes `viz-deck` from a single-mode keynote skill into a
**four-mode delivery toolkit**, integrates a published 20-philosophy library
and a 5-dimension critique standard, and exposes a screen-recording / PPTX
export toolchain via a soft bridge to
[`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design).
All v0.1 capabilities remain backwards-compatible.

#### `claude-code-skills/viz-deck` — main upgrade target (35 KB → 65 KB)

- **4 production modes** (was 1):
  1. `keynote-report` — original v1 mode (stage / architecture-deep / competitive-landscape)
  2. `prototype` — hi-fi HTML prototypes with iOS / Android / macOS / browser device frames + AppPhone state manager
  3. `slide-deck` — keyboard-navigated HTML slides with speaker notes, overview, autoplay; exportable to **editable PPTX** (real text frames, not flattened images) and landscape PDF
  4. `motion-stage` — HTML animation stages with `window.__ready` recording signal; exports MP4 at 25 fps base + 60 fps interpolated + palette-optimized GIF + optional BGM (six scene-typed tracks via huashu)
- New starter templates: `prototype-shell.html`, `slide-deck.html`, `motion-stage.html`
- New scripts: `export-mp4.sh`, `export-pptx.sh`, `review-5dim.mjs`
- New references: `huashu-bridge.md`, `design-philosophies.md`, `critique-5dim.md`, `prototype-mode.md`, `slide-mode.md`, `motion-mode.md`
- `SKILL.md` rewritten to expose mode routing, philosophy picker, and critique trigger
- `samples/motion-stage-sample.html` + `.mp4` + `design-critique-sample.html` shipped as reference outputs

#### `claude-code-skills/biz-decision-stack` (57 KB → 62 KB)

- **7th subagent**: `07-design-critic.md` for 5-dimension critique of any decision report
- **8th template**: `design-critique.html` — terminal-style critique HTML with embedded ECharts radar + Keep / Fix (critical / important / polish) / Quick-Wins
- New references: `critique-5dim.md` (terminal-styled critique protocol), `huashu-bridge.md` (limited bridge — critique standard only; motion / BGM / device frames deliberately excluded to honor the zero-motion principle)
- Orchestrator `00-all-hands-orchestrator.md` adds an optional Phase 6 — offers to run a critique pass after the 6-role chain
- `samples/design-critique-sample.html` shipped as reference output

#### `claude-code-skills/viz-charts` (150 KB → 153 KB)

- **5th capability layer**: motion charts — frame-step reveal, temporal sweep, graph orbit
- New references: `motion-charts.md`, `mp4-export.md`
- New theme presets: `themes/motion.js` — animation duration / easing / fps consistency across stages
- New template: `templates/motion/motion-stage-template.html`
- `SKILL.md` updated to 5 capability layers + Step 5 (Motion → MP4) workflow
- `samples/trend-motion-sample.html` + `.mp4` shipped as reference outputs

#### Repository-wide

- `README.md` rewritten to delivery-grade open-source documentation, replacing v0.1 conversational tone
- `README_en.md` added — English-language landing page
- `claude-code-skills/skills-install-guide.md` upgraded to v2.0 with two new sections: §11 v2 capability cheatsheet and §12 huashu-design bridge protocol
- Every skill now ships a `samples/` directory with real rendered deliverables

### Compatibility

- v0.1 workflows are **fully preserved**. Users not adopting v2 modes need no changes.
- `huashu-design` is a **soft dependency** — installing it unlocks v2 advanced modes; without it, the v1 keynote-report / decision chain / static charts continue to work unchanged.

### Known constraints

- v2 motion / PPTX export modes require: Node 18+, Chromium (via Playwright), and ffmpeg on PATH
- huashu-design itself is free for personal use; **commercial deployments must obtain a separate license** from its author

---

## [0.1.0] — 2026-05-10

### Added — Initial public release

First open-source release under Apache License 2.0. Three skills shipped for
the **Claude Code** harness.

#### `claude-code-skills/biz-decision-stack` (57 KB)

- 6 subagents covering board → CEO → architect → MRD/PM → dev-test → retro
- 1 shared HTML rendering skill (`biz-html-viz`) with 7 terminal-style templates:
  `board-brief`, `ceo-canvas`, `tech-roadmap`, `mrd-report`, `project-board`,
  `dev-report`, `retro-report`, plus an `index` aggregator
- `00-all-hands-orchestrator` for one-shot full-chain generation
- Design system: black `#0a0a0a` + acid-yellow `#d4ff00`, JetBrains Mono,
  zero animation, print-ready

#### `claude-code-skills/viz-deck` (35 KB)

- 3 keynote-grade HTML templates: `stage-report`, `architecture-deep`,
  `competitive-landscape`
- Design system: deep-space `#030711` + cyan/blue/gold, Inter, scoped
  micro-animations with `prefers-reduced-motion` fallback
- Tier 1/2/3 adaptive competitive research playbook (web_search + web_fetch)

#### `claude-code-skills/viz-charts` (150 KB)

- Mermaid (11 diagram types), ECharts (25+ chart types), self-rolled SVG
  components (KPI, sparkline, gauge, progress bar, tag cloud)
- 3D knowledge graph viewer (3d-force-graph + three.js) with two builders:
  - `code-kg.mjs` — extracts file/import graph from JS/TS/Go/Python/Rust repos
  - `doc-kg.mjs` — extracts concept/section graph from markdown
- Dual render modes: inline live (CDN with jsdelivr→unpkg fallback) and offline SVG
- Dual themes: `terminal` (for biz-decision-stack) and `deck` (for viz-deck)

### Documentation

- Repository-wide `README.md` with bilingual project intro and roadmap
- `LICENSE` (Apache 2.0) and `NOTICE` (ZimaBlueAI copyright + trademark + third-party)
- `CONTRIBUTING.md` with PR conventions, DCO sign-off requirement, skill quality bar
- `CODE_OF_CONDUCT.md` (Contributor Covenant 2.1)
- `claude-code-skills/skills-install-guide.md` — end-to-end install/config/usage

---

[Unreleased]: https://github.com/ZimaBlueAI/skills/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/ZimaBlueAI/skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ZimaBlueAI/skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ZimaBlueAI/skills/releases/tag/v0.1.0
