# Changelog

All notable changes to **ZimaBlueAI Agent Skills** are documented here.

This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
and the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.

---

## [Unreleased]

### Added — `zima-html-ppt` skill (ZimaBlueAI 现场讲演 deck)

A new generation skill capturing the **ZimaBlue Editorial (暖纸编辑风)** presentation
style and its signature **Speaker Mode**, distilled from the production decks
`D1-破局与进化` / `D2-三场战役` / `D3-训练方案`.

- `references/design-system.md` — full visual spec: warm-paper tokens, type scale,
  signature elements (top tri-color bar, hairline cards, tabular-nums numerals),
  component recipes, Chart.js tuning, restrained motion, anti-AI-slop rules.
- `references/speaker-mode.md` — the presenter engine: `.notes` speaker-script
  convention with a 5-tag taxonomy (cue / say / do / data / bridge, read-aloud lines
  auto-highlighted orange via `:has()`), per-slide `data-min` time budgeting, the
  keyboard map, and the postMessage-synced presenter window architecture.
- `templates/zima-ppt-starter.html` — one fork-ready single file with the whole
  engine baked in: deck/slide scaffold, top tri-color bar, progress + timer bars,
  on-screen hint badge (`按 F 全屏 · 按 S 演讲者模式 · ← → 翻页`), `✦ ZimaBlueAI`
  brand-mark, count-up numerals, Chart.js defaults, and the S-key presenter window.
- Replicated into all four ecosystems: `claude-code-skills/`, `codex-skills/`,
  `openclaw-skills/skills/`, `hermes-skills/skills/`. Cross-linked from
  `viz-channel/references/default-style.md` so the channel workflow can reach
  speaker mode when a deck needs to be presented live.

### Planned

- viz-charts narrative chart explainer (TTS-narrated chart video)
- Channel adapters beyond Feishu/Lark (WeCom / Slack / Telegram) in `viz-channel`
- Cross-harness consistency test suite
- Skill registry index (`skills.json`)

---

## [0.5.0] — 2026-05-29

### Added — channel delivery layer for OpenClaw & Hermes (`viz-channel`)

The three skills only ever **generated** artifacts. This release adds a
**conversational orchestration + channel-delivery** layer so the same
generation power works *inside an IM channel*: a user @-mentions the bot in
Feishu (or any gateway channel), and the agent **clarifies the request →
generates via viz-deck/viz-charts → sends the finished file back to the same
chat**. Feishu was the user's example; the transport is framed as a
pluggable adapter.

#### New top-level directories — `openclaw-skills/` & `hermes-skills/`

- Each ships the new **`viz-channel`** skill (frontmatter trigger + body =
  `clarify → generate → deliver` workflow), a one-command installer
  (`.sh` + `.ps1`), and a **`USAGE.md` case library** (OpenClaw: 9 cases;
  Hermes: 11, incl. 2 automation cases).
- **Thin-bridge packaging**: the heavy generators (`viz-deck` / `viz-charts`
  / optional `biz-html-viz`) are **not duplicated** — the installer vendors
  them from `claude-code-skills/*.zip` (or `--from-github`) into the target
  platform's skills dir. Single source of truth, no four-way drift.
- Installers **never hard-delete**: a re-install moves any existing skill to
  `.zima-replaced/` rather than removing it.

#### `viz-channel` skill

- **`SKILL.md`** — channel-agnostic trigger (做PPT / 做汇报 / 做图表 /
  知识图谱 / 发给我 / 发群里 …); default deliverable = **animated HTML**,
  with PPTX (editable) / MP4 (in-chat playback) / chart / 3D KG on demand.
- **`references/`**
  - `default-style.md` — **default visual system: ZimaBlue Editorial** (warm
    paper bg, deep-teal primary, gold/terracotta accents, hairline cards,
    teal→gold→red top rule, bold tabular-nums metrics; Chart.js palette +
    PPTX warm-paper theme mapping; modeled on `D1-破局与进化.html`). Applied
    by default to all channel HTML/PPTX; overridable per request.
  - `channel-protocol.md` — conversation state machine, ≤2-question clarify
    rule, multi-turn iteration, group-vs-DM, human-readable failure handling
  - `delivery-matrix.md` — form decision table (HTML / PPTX / MP4 / chart /
    3D KG), HTML-vs-PNG rules, Feishu size/permission limits, pre-send checklist
  - `openclaw-channel.md` / `hermes-channel.md` — platform specifics:
    chat_id resolution, skills load paths, why delivery shells out to a
    script; Hermes adds cron/webhook automation recipes
- **`scripts/`**
  - `channel_deliver.py` — the current channel adapter (**Feishu/Lark**):
    upload + send via open.feishu.cn REST; `--via auto` prefers a lark-cli
    token (reuses an existing `~/.lark-cli` config) and falls back to REST;
    `--to-current` resolves the active chat from injected env vars; ffprobe
    duration probing for nicer MP4 video messages
  - `channel_send.sh` / `.ps1` — one-line delivery entrypoint (wraps
    `channel_deliver.py --via auto`)
  - `resolve_chat.py` — prints/validates the current channel chat_id
- **`templates/zima-editorial-deck.html`** — ready-to-fill HTML skeleton in
  the default ZimaBlue Editorial style (tokens, components, Chart.js defaults
  pre-wired) so default channel HTML looks polished out of the box

#### Platform notes

- **OpenClaw**: native Feishu channel over WebSocket long-connection; skills
  load from `<workspace>/skills/` → `~/.openclaw/skills/`.
- **Hermes**: Feishu gateway adapter binds inbound messages to a session;
  the same generate→deliver chain can run unattended as a **cron or webhook
  routine** (e.g. auto weekly deck to a group, event-triggered chart push).

### Docs

- Top-level `README.md` / `README_en.md`: new "channel delivery layer"
  section, refreshed harness/badge framing, repo-structure block now lists
  the shipped `openclaw-skills/` & `hermes-skills/`, roadmap updated.

---

## [0.4.0] — 2026-05-16

### Added — 26-skill landscape cross-pollination (取长补短)

After a systematic review of the open-source Agent-Skill PPT landscape (26
projects ≈ 70k+ aggregate stars), this release imports the highest-value
patterns from peer skills into the three ZimaBlueAI skills. **All v0.3
workflows remain unchanged**; every upgrade is additive.

#### `claude-code-skills/viz-deck` — six v4 enhancements

- **Speaker Mode** (inspired by `lewislulu/html-ppt-skill` — 3.8k★)
  - New `templates/speaker-window.html`: independent draggable presenter
    window with 4 magnetic cards (current preview / next preview /
    teleprompter / timer)
  - `templates/slide-deck.html` rewired: press **S** to pop the window;
    BroadcastChannel `viz-deck-presenter` keeps both windows in sync;
    `?present=true` URL flag auto-opens
  - Timer has elapsed / countdown modes, >90% warn, >100% over-time alert
  - Three layout presets: GRID / PROMPTER / DUO
- **Show-Don't-Tell 3-variant preview** (inspired by `zarazhangrui/frontend-slides` — 17.5k★)
  - New `scripts/preview-shotgun.mjs`: takes a topic + scene preset and
    renders 3 contrasting hero mockups side-by-side
  - 5 scene presets (`investor-pitch`, `product-launch`, `tech-deepdive`,
    `academic`, `default`); each picks a cross-school triple from the
    20-philosophy library
  - New `templates/preview-board.example.html`: sample output
  - `references/design-philosophies.md` extended with the contrast-triple
    table and trigger rules
- **Doc → Deck converter** (inspired by `leonid20000/odin-slides` — 147★ + `natolambert/colloquium` — 190★)
  - New `scripts/doc-to-spec.mjs`: parses Markdown (and DOCX/PDF via pandoc
    pre-flight) and emits a valid `pptx-deck-spec.json` ready for
    `make-pptx-deck.mjs`
  - Heading-level histogram picks the chapter boundary intelligently
  - Tables → kpi-grid; bullet runs → title-bullets; quote blocks → pullquote
  - New `references/doc-to-deck.md` documenting input formats, conversion
    rules, and the difference from odin-slides / colloquium
- **Academic Talk template** (inspired by `Gabberflast/academic-pptx-skill` — 387★)
  - New `templates/academic-talk.html`: long-scroll keynote with action
    titles (verb-driven), numbered citations, exhibit headers, anticipated
    Q&A section, and a proper references bibliography
  - Newsreader serif typography for academic gravitas
  - New `references/academic-mode.md`: action-title rule, citation
    discipline, exhibit caption guidelines, limitations checklist
- **Bento Grid layout** (inspired by `hubeiqiao/apple-bento-grid` — 171★)
  - New `templates/bento-layout.html`: 12-col responsive bento with
    1×1 / 2×1 / 3×1 / 4×1 / 1×2 / 2×2 spans + hero accent halos
  - `make-pptx-deck.mjs` adds `bento-grid` as the 9th native PPTX layout
    (greedy row-packing, 3-col layout, accent variants `accent` / `accent2` /
    `gold`)
  - `templates/pptx-deck-spec.example.json` extended with a sample bento slide
- **Reflective Loop** (inspired by `icip-cas/PPTAgent` — 4.4k★)
  - New `scripts/reflect-and-redo.mjs`: per-page 5-dim critique pass; D2/D3/D4
    scored objectively from the JSON spec; D1/D5 flagged as neutral
    pending human/LLM review
  - HTML report includes deck mean, dimension means, per-slide score table
    (flagged rows red), and explicit issue list
  - Optional `--redo-prompts redo.txt` emits human-readable redo proposals
    per flagged slide
  - `references/critique-5dim.md` extended with the reflective-loop protocol
    and threshold rules

#### `claude-code-skills/biz-decision-stack` — Template Router subagent

- **Template Router** (inspired by `seulee26/mckinsey-pptx` — 426★)
  - New `.claude/agents/08-template-router.md`: 9th subagent in the
    biz-decision-stack
  - Routes ambiguous user input ("做个 deck 给老板"、"做个汇报") to one of 8
    templates by scoring against a 5-dimension rubric (audience fit ×3 /
    decision type ×3 / temporal fit ×2 / density ×1 / trigger keywords ×1)
  - Outputs a ROUTING DECISION block + writes a one-paragraph justification
    into the generated HTML's header comment block — every choice is
    defended, not silent
  - Routes to user pick when top-1 and top-2 scores are within 3 points
- **New reference**: `references/template-routing-rubric.md` — full scoring
  rubric, threshold table, dual-candidate handling

#### Repository-wide

- `.work/repack-v3.py` updated to include the new 9th subagent
  (`08-template-router.md`) in `biz-decision-stack.zip`
- `.work/build-codex.py` updated symmetrically — the 9 subagents are now
  converted to TOML and packaged into `codex-skills/biz-decision-stack.zip`
- All three skills' `SKILL.md` `description` fields extended with the new
  v4 trigger keywords (Speaker Mode, Doc→Deck, academic talk, bento, etc.)
  so the harness's keyword router can find them

### Compatibility

- v0.3 workflows are **fully preserved**. Every v4 addition is additive:
  - viz-deck: still 5 modes, all original templates/scripts intact
  - biz-html-viz: still 8 templates (the new template-router *picks* among
    them, doesn't replace any)
  - viz-charts: not touched in v0.4 (no PPT-landscape peer outperforms it)
- Speaker Mode requires same-origin context (both `slide-deck.html` and
  `speaker-window.html` served from the same path)
- Doc-to-spec for `.docx` / `.pdf` requires pandoc on PATH

### Known constraints

- Reflective Loop's D1 (philosophy alignment) and D5 (originality) cannot
  be scored from JSON alone — the script flags them as neutral 7.0 and
  delegates the actual judgement to an LLM review of the rendered output
- Speaker Mode pop-up requires browser pop-up permissions for the deck
  origin; the hint banner explains this when blocked
- The `preview-shotgun.mjs` philosophy registry is a representative subset
  (11 of the 20 huashu philosophies); the remaining 9 can still be invoked
  by explicit slug

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
  second flavor tailored to **OpenAI Codex CLI**'s `.codex/skills/` and
  `.codex/agents/` conventions. **Skill content (SKILL.md, references,
  templates, scripts, specs) is byte-for-byte identical** to the Claude
  Code version; only the install path and subagent serialization differ.
- 8 subagents converted from Claude Code's markdown frontmatter → Codex's
  TOML format (`name`, `description`, `developer_instructions`)
- `codex-skills/install.sh` + `codex-skills/install.ps1` — one-shot
  installer that extracts the three zips to `$HOME/.codex/skills/` and
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
$PPT_MASTER_HOME → ~/.codex/skills/ppt-master → ~/.claude/skills/ppt-master
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

[Unreleased]: https://github.com/ZimaBlueAI/skills/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/ZimaBlueAI/skills/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/ZimaBlueAI/skills/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/ZimaBlueAI/skills/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/ZimaBlueAI/skills/releases/tag/v0.1.0
