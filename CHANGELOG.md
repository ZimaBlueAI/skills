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

[Unreleased]: https://github.com/ZimaBlueAI/skills/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/ZimaBlueAI/skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ZimaBlueAI/skills/releases/tag/v0.1.0
