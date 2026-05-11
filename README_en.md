# ZimaBlueAI Agent Skills

> **Production-grade skill packs for modern AI coding agents.**
> Write once, ship across harnesses.

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Release](https://img.shields.io/badge/release-v0.2.0-2b6cb0.svg)](./CHANGELOG.md)
[![Status](https://img.shields.io/badge/status-public_preview-orange.svg)](#9-roadmap)
[![Harness](https://img.shields.io/badge/harness-Claude_Code-7c3aed.svg)](./claude-code-skills/)
[![Maintainer](https://img.shields.io/badge/maintainer-ZimaBlueAI-111.svg)](https://github.com/ZimaBlueAI)

[中文版](./README.md) · [Install guide](./claude-code-skills/skills-install-guide.md) · [Changelog](./CHANGELOG.md) · [Contributing](./CONTRIBUTING.md)

---

## 1. What is this

**ZimaBlueAI Agent Skills** is a curated set of **declarative capability packs** for modern AI coding agents — starting with Claude Code, with planned ports to Codex / OpenClaw / Hermes / Octarus.

Each skill ships as a self-contained `.zip` archive with this layout:

```
.claude/
├── agents/            # subagents — "with which identity to think"
└── skills/<name>/     # the skill itself
    ├── SKILL.md       # trigger conditions + workflow (agent entry point)
    ├── references/    # workflow references (loaded on demand)
    ├── templates/     # deliverable templates (HTML / mmd / json …)
    └── scripts/       # optional tool scripts
```

The agent loads a skill when a user expresses the matching intent, and produces a structured deliverable. This is **not a library** and **not an npm package** — it's a capability declaration consumed by the agent.

---

## 2. What ships in v0.2.0

Three skills cover the full chain from **board brief to outbound keynote video**. All skills are independent — pick what you need.

| Skill | One line | Output | Zip size |
|---|---|---|---|
| **biz-decision-stack** | 7 subagents · investor → CEO → architect → MRD → delivery → retro → critique | 8 terminal-grade HTML reports (black + acid-yellow + mono + zero-motion) | 62 KB |
| **viz-deck** | 4 production modes · keynote-report / hi-fi prototype / slide-deck / motion-stage | HTML / editable PPTX / MP4 / GIF / PDF (deep-space cyan/blue/gold) | 65 KB |
| **viz-charts** | 5 visual layers · Mermaid · ECharts · SVG widgets · 3D knowledge graphs · motion video | Inline HTML or offline SVG / MP4 | 153 KB |

### What's new in v0.2 (vs v0.1)

- ✨ **viz-deck expanded from 1 output mode to 4** (hi-fi prototype / slide deck / motion MP4 / original stage report)
- ✨ **20 design philosophies** wired into viz-deck — switch style on demand (Pentagram / Kenya Hara / Sagmeister and more)
- ✨ **5-dimension expert critique** in both terminal and keynote skins, with ECharts radar chart and a Keep / Fix / Quick-Wins punch list
- ✨ **HTML → MP4 / 60fps / GIF** toolchain
- ✨ **HTML → editable PPTX** (real text frames, not flattened images)
- ✨ biz-decision-stack adds a 7th subagent `design-critic` and a `design-critique.html` template
- ✨ Every skill ships a `samples/` directory with real, rendered deliverables

Full notes in the [CHANGELOG](./CHANGELOG.md).

---

## 3. Bridge to huashu-design

v0.2 introduces an **optional soft-bridge** to [`alchaincyf/huashu-design`](https://github.com/alchaincyf/huashu-design):

- **viz-deck**'s *prototype / slide-deck / motion-stage* modes call into huashu-design for MP4/PPTX export, device frames, the animation engine, the 20-philosophy library, and the 5-dimension critique standard
- **biz-decision-stack** only borrows the critique scoring standard and optional PDF export; it deliberately **does not** import motion / BGM / device frames (decision reports stay zero-motion by principle)
- **viz-charts**'s motion mode calls huashu's `render-video.js` directly for screen recording

The bridge is a **soft dependency**: without huashu-design installed, v1 capabilities (the original stage report / decision chain / static charts) remain fully functional. huashu-design itself is free for personal use; **commercial use requires a separate license** — see its [LICENSE](https://github.com/alchaincyf/huashu-design).

```
                 ┌──────────────────────────────┐
                 │  huashu-design (soft bridge) │
                 │  - render-video.js (MP4)     │
                 │  - export_deck_pptx.mjs      │
                 │  - 20 design philosophies    │
                 │  - 5-dim critique standard   │
                 │  - ios/android/macos frames  │
                 └──────────┬───────────────────┘
                            │ optional bridge
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
┌─────────────┐  ┌─────────────────┐  ┌──────────────────┐
│ viz-charts  │  │    viz-deck     │  │ biz-decision-    │
│ (motion only│  │  (full bridge)  │  │     stack        │
│              │  │                 │  │ (critique only)  │
└─────────────┘  └─────────────────┘  └──────────────────┘
```

---

## 4. Five-minute quickstart

### 4.1 Install skills into Claude Code

**Single project** (recommended for first validation):

```bash
git clone --depth=1 https://github.com/ZimaBlueAI/skills.git
cd skills/claude-code-skills

# Unzip into the root of your project (next to .git)
unzip -o biz-decision-stack/biz-decision-stack.zip -d /path/to/your-project/
unzip -o viz-deck/viz-deck.zip                       -d /path/to/your-project/
unzip -o viz-charts/viz-charts.zip                   -d /path/to/your-project/
```

**Global** (shared across projects):

```bash
unzip -o biz-decision-stack/biz-decision-stack.zip -d ~/
unzip -o viz-deck/viz-deck.zip                       -d ~/
unzip -o viz-charts/viz-charts.zip                   -d ~/
```

### 4.2 Optional: install huashu-design to unlock the v2 advanced modes

```bash
git clone --depth=1 https://github.com/alchaincyf/huashu-design.git ~/.claude/skills/huashu-design
cd ~/.claude/skills/huashu-design

# Node runtime (playwright + sharp + pptxgenjs + pdf-lib).
# huashu-design ships without a package.json, so use this minimal one:
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
npm install
npx playwright install chromium

# ffmpeg must be on PATH (used for MP4 encoding and 60fps interpolation)
ffmpeg -version || echo "Please install ffmpeg first"
```

> Skipping this step is fine — you just lose the 4 advanced output modes and fall back to v1 single mode, and the 5-dim critique uses the locally mirrored standard instead.

### 4.3 Verify Claude Code recognizes the skills

```
> /skills
```

You should see `biz-html-viz` · `viz-deck` · `viz-charts`. With huashu installed you'll see a fourth: `huashu-design`.

### 4.4 Trigger by natural language

| You say | Auto-routes to |
|---|---|
| "Write me a board brief for Rolin" | `01-board-advisor` + `biz-html-viz · board-brief` |
| "Run an all-hands flow" / "走一遍全流程" | `00-all-hands-orchestrator` (chain through 6 roles + critique) |
| "Build a stage-report deck for Mingjing" | `viz-deck · stage-report` |
| "Make an iOS hi-fi prototype" | `viz-deck · prototype-mode` |
| "Build a slide deck" + "export to PPTX" | `viz-deck · slide-mode` + `export-pptx.sh` |
| "Render this to MP4" / "60fps video" | `viz-deck · motion-mode` + huashu `render-video.js` |
| "Critique this" / "5-dim review" | `07-design-critic` or `viz-deck · review-5dim.mjs` |
| "Add an architecture diagram" / "Add a line chart" | `viz-charts` (auto-picks Mermaid/ECharts by data shape) |
| "Make a 3D code KG of this repo" | `viz-charts · code-kg.mjs` + `templates/kg3d/code-graph.html` |

---

## 5. Samples

Every skill ships a `samples/` directory with **real rendered deliverables** you can open immediately:

| Skill | Sample | What you see |
|---|---|---|
| biz-decision-stack | [`samples/design-critique-sample.html`](./claude-code-skills/biz-decision-stack/samples/design-critique-sample.html) | Terminal-style 5-dim critique with ECharts radar and a Keep / Fix / Quick-Wins list |
| viz-deck | [`samples/motion-stage-sample.html`](./claude-code-skills/viz-deck/samples/motion-stage-sample.html) + [`.mp4`](./claude-code-skills/viz-deck/samples/motion-stage-sample.mp4) | Keynote-grade motion stage source HTML plus a recorded 1920×1080 MP4 |
| viz-deck | [`samples/design-critique-sample.html`](./claude-code-skills/viz-deck/samples/design-critique-sample.html) | Keynote-style 5-dim critique (deep-space palette variant) |
| viz-charts | [`samples/trend-motion-sample.html`](./claude-code-skills/viz-charts/samples/trend-motion-sample.html) + [`.mp4`](./claude-code-skills/viz-charts/samples/trend-motion-sample.mp4) | ECharts multi-series reveal animation, with recorded MP4 |
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
│   │   └── samples/               v0.2 — rendered output examples
│   │
│   ├── viz-deck/
│   │   ├── viz-deck.zip
│   │   ├── viz-deck-README.md
│   │   ├── design-system-deck.md  Public design spec
│   │   ├── research-playbook.md   Tier 1/2/3 competitive research protocol
│   │   ├── sample-board-brief.html
│   │   └── samples/               v0.2 — 4-mode output examples
│   │
│   └── viz-charts/
│       ├── viz-charts.zip
│       ├── demo-*.html            Four interactive showcases
│       └── samples/               v0.2 — motion chart examples
│
├── codex-skills/                  ☐ OpenAI Codex CLI (planned)
├── openclaw-skills/               ☐ OpenClaw (planned)
├── hermes-skills/                 ☐ Hermes (planned)
└── octarus-skills/                ☐ Octarus (planned)
```

---

## 8. Who should use what

| Role | Recommended bundle | Why |
|---|---|---|
| **Startup CEO** | biz-decision-stack (all) + viz-deck (stage-report) | Internal alignment via the decision chain; outbound pitch via the keynote deck |
| **Product manager** | biz-decision-stack (PM modes) + viz-deck (prototype) | MRD as docs + hi-fi prototype to align engineering |
| **Chief architect** | biz-decision-stack (architect) + viz-deck (architecture-deep) + viz-charts | Internal ADRs + customer-facing technical decks + 3D code KG |
| **Investor / FA** | viz-deck (competitive-landscape) + viz-charts | Live competitive research + animated data for roadshows |
| **Design / brand lead** | viz-deck (all 4 modes) + huashu-design | One toolchain for prototype / slides / video / critique |
| **Engineering lead** | biz-decision-stack (dev-test) + viz-charts (3D KG) | Status reporting + project structure visualization |

---

## 9. Roadmap

| Phase | Scope | Status |
|---|---|---|
| v0.1 | Initial release of the claude-code-skills trio | ✅ Released |
| **v0.2** | **4 output modes · 20 philosophies · 5-dim critique · huashu-design bridge · samples** | ✅ **Released (current)** |
| v0.3 | Port to OpenAI Codex CLI (`codex-skills/`) | 🟡 Planned |
| v0.4 | `openclaw-skills/` · `hermes-skills/` | ⚪ Planned |
| v0.5 | `octarus-skills/` + cross-harness consistency test suite | ⚪ Planned |
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

**v2 bridge dependency**

- [alchaincyf/huashu-design](https://github.com/alchaincyf/huashu-design) — video / PPTX / device frame toolchain, the 20-philosophy library, and the 5-dim critique standard

**Runtime libraries** (loaded via CDN or npm at render time — not vendored)

- [Mermaid](https://mermaid.js.org/) · [Apache ECharts](https://echarts.apache.org/) · [three.js](https://threejs.org/) · [3d-force-graph](https://github.com/vasturiano/3d-force-graph) · [Playwright](https://playwright.dev/) · [ffmpeg](https://ffmpeg.org/) · [pptxgenjs](https://gitbrent.github.io/PptxGenJS/) · [pdf-lib](https://pdf-lib.js.org/)

Each retains its upstream license — see [NOTICE](./NOTICE).

---

## Contact

- GitHub: <https://github.com/ZimaBlueAI>
- Issues: <https://github.com/ZimaBlueAI/skills/issues>
- Security: see [CONTRIBUTING.md](./CONTRIBUTING.md)

---

<sub>Made by ZimaBlueAI · 2026</sub>
