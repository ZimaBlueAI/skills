#!/usr/bin/env node
// viz-deck → ppt-master bridge
// JSON deck spec → SVG per slide → editable PPTX (DrawingML, clickable text frames)
//
// Usage:
//   node make-pptx-deck.mjs spec.json [--out PATH] [--theme deep-space|terminal|deck-light]
//        [--format ppt169|ppt43] [--anim fade|fly|zoom|wipe] [--trans fade|push|wipe]
//        [--no-build]     -> only write svg_output/, don't run ppt-master
//        [--with-notes]   -> emit per-slide speaker_notes.txt for TTS narration
//
// Spec schema: see templates/pptx-deck-spec.example.json

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import os from "node:os";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HOME = os.homedir();

// ppt-master can live in current or legacy harness install locations, or be pinned via env var.
// Detection order: $PPT_MASTER_HOME -> ~/.codex/skills/ppt-master (Codex) -> ~/.agents/skills/ppt-master (legacy Codex) -> ~/.claude/skills/ppt-master (Claude Code)
function findPptMaster() {
  const env = process.env.PPT_MASTER_HOME;
  if (env && fs.existsSync(env)) return env;
  const candidates = [
    path.join(HOME, ".codex", "skills", "ppt-master"),
    path.join(HOME, ".agents", "skills", "ppt-master"),
    path.join(HOME, ".claude", "skills", "ppt-master"),
  ];
  for (const c of candidates) {
    if (fs.existsSync(c)) return c;
  }
  return candidates[1]; // fall through to claude path so error messages stay useful
}
const PPT_MASTER = findPptMaster();
const PYTHON = process.platform === "win32"
  ? path.join(PPT_MASTER, ".venv", "Scripts", "python.exe")
  : path.join(PPT_MASTER, ".venv", "bin", "python");
const SVG_TO_PPTX = path.join(PPT_MASTER, "skills", "ppt-master", "scripts", "svg_to_pptx.py");
const NOTES_TO_AUDIO = path.join(PPT_MASTER, "skills", "ppt-master", "scripts", "notes_to_audio.py");

const THEMES = {
  "deep-space": {
    bg: "#030711", surface: "#0E1525", panel: "#141B2D",
    border: "#1F2937", text: "#E5E7EB", muted: "#94A3B8",
    accent: "#00D9FF", accent2: "#6366F1", gold: "#FFB800",
    font: "Inter, 'Helvetica Neue', sans-serif", titleFont: "Inter, sans-serif",
    accentBar: "#00D9FF"
  },
  "terminal": {
    bg: "#0A0A0A", surface: "#101010", panel: "#161616",
    border: "#262626", text: "#F5F5F5", muted: "#9CA3AF",
    accent: "#D4FF00", accent2: "#FFFFFF", gold: "#D4FF00",
    font: "'JetBrains Mono', 'Cascadia Code', monospace", titleFont: "'JetBrains Mono', monospace",
    accentBar: "#D4FF00"
  },
  "deck-light": {
    bg: "#FAFBFC", surface: "#FFFFFF", panel: "#F3F4F6",
    border: "#E5E7EB", text: "#0F172A", muted: "#475569",
    accent: "#6366F1", accent2: "#06B6D4", gold: "#F59E0B",
    font: "Inter, sans-serif", titleFont: "Inter, sans-serif",
    accentBar: "#6366F1"
  }
};

const FORMATS = {
  ppt169: { w: 1280, h: 720 },
  ppt43: { w: 1024, h: 768 }
};

// ─────────────────────────────────────────────────────────────────────────────
// SVG primitives
// ─────────────────────────────────────────────────────────────────────────────

const esc = s => String(s ?? "")
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");

function svgOpen(w, h, theme) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="${theme.bg}"/>
      <stop offset="100%" stop-color="${theme.surface}"/>
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="${theme.accent}"/>
      <stop offset="100%" stop-color="${theme.accent2}"/>
    </linearGradient>
  </defs>
  <rect width="${w}" height="${h}" fill="url(#bgGrad)"/>`;
}

function svgClose() { return `</svg>`; }

function txt(x, y, content, opts = {}) {
  const fz = opts.size || 22;
  const fw = opts.weight || 400;
  const fill = opts.color || "#E5E7EB";
  const family = opts.font || "Inter, sans-serif";
  const anchor = opts.anchor || "start";
  const lh = opts.lh || 1.35;
  const lines = String(content ?? "").split("\n");
  return lines.map((line, i) => `<text x="${x}" y="${y + i * fz * lh}" font-family="${family}" font-size="${fz}" font-weight="${fw}" fill="${fill}" text-anchor="${anchor}">${esc(line)}</text>`).join("\n  ");
}

function rect(x, y, w, h, opts = {}) {
  const fill = opts.fill || "transparent";
  const stroke = opts.stroke || "none";
  const sw = opts.strokeWidth || 0;
  const rx = opts.rx || 0;
  const opacity = opts.opacity ?? 1;
  return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}" rx="${rx}" opacity="${opacity}"/>`;
}

function line(x1, y1, x2, y2, opts = {}) {
  return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${opts.stroke || "#1F2937"}" stroke-width="${opts.strokeWidth || 1}"/>`;
}

function circle(cx, cy, r, opts = {}) {
  return `<circle cx="${cx}" cy="${cy}" r="${r}" fill="${opts.fill || "transparent"}" stroke="${opts.stroke || "none"}" stroke-width="${opts.strokeWidth || 0}" opacity="${opts.opacity ?? 1}"/>`;
}

// ─────────────────────────────────────────────────────────────────────────────
// Layouts
// ─────────────────────────────────────────────────────────────────────────────

function layoutTitleCover(slide, theme, fmt) {
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  // grid backdrop dots
  parts.push(circle(w - 180, 140, 220, { fill: theme.accent, opacity: 0.08 }));
  parts.push(circle(220, h - 160, 180, { fill: theme.accent2, opacity: 0.10 }));
  parts.push(rect(80, 78, 60, 6, { fill: theme.accentBar, rx: 3 }));
  parts.push(txt(80, 130, (slide.eyebrow || "VIZ DECK").toUpperCase(), { size: 16, color: theme.muted, font: theme.font, weight: 500 }));
  parts.push(txt(80, 280, slide.title || "Untitled", { size: 64, color: theme.text, font: theme.titleFont, weight: 700, lh: 1.1 }));
  if (slide.subtitle) parts.push(txt(80, 380, slide.subtitle, { size: 28, color: theme.muted, font: theme.font, weight: 400, lh: 1.3 }));
  parts.push(rect(80, h - 100, w - 160, 1, { fill: theme.border }));
  parts.push(txt(80, h - 60, slide.author || "ZimaBlueAI", { size: 16, color: theme.muted, font: theme.font, weight: 500 }));
  if (slide.date) parts.push(txt(w - 80, h - 60, slide.date, { size: 16, color: theme.muted, font: theme.font, weight: 500, anchor: "end" }));
  parts.push(svgClose());
  return parts.join("\n");
}

function layoutAgenda(slide, theme, fmt) {
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  parts.push(rect(80, 78, 60, 6, { fill: theme.accentBar, rx: 3 }));
  parts.push(txt(80, 130, (slide.eyebrow || "AGENDA").toUpperCase(), { size: 16, color: theme.muted, font: theme.font, weight: 500 }));
  parts.push(txt(80, 200, slide.title || "Agenda", { size: 56, color: theme.text, font: theme.titleFont, weight: 700 }));
  const items = slide.items || [];
  const startY = 290;
  items.forEach((item, i) => {
    const y = startY + i * 56;
    parts.push(txt(80, y, String(i + 1).padStart(2, "0"), { size: 28, color: theme.accent, font: theme.titleFont, weight: 700 }));
    parts.push(txt(150, y, item, { size: 26, color: theme.text, font: theme.font, weight: 400 }));
    parts.push(line(80, y + 16, w - 80, y + 16, { stroke: theme.border, strokeWidth: 1 }));
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function layoutSectionDivider(slide, theme, fmt) {
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  parts.push(rect(0, h / 2 - 1, w, 2, { fill: theme.border }));
  parts.push(rect(w / 2 - 100, h / 2 - 1, 200, 2, { fill: theme.accentBar }));
  parts.push(txt(w / 2, h / 2 - 90, slide.section || "01", { size: 140, color: theme.accent, font: theme.titleFont, weight: 700, anchor: "middle" }));
  parts.push(txt(w / 2, h / 2 + 90, slide.title || "Section", { size: 44, color: theme.text, font: theme.titleFont, weight: 600, anchor: "middle" }));
  if (slide.subtitle) parts.push(txt(w / 2, h / 2 + 140, slide.subtitle, { size: 20, color: theme.muted, font: theme.font, anchor: "middle" }));
  parts.push(svgClose());
  return parts.join("\n");
}

function layoutTitleBullets(slide, theme, fmt) {
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  parts.push(rect(80, 78, 60, 6, { fill: theme.accentBar, rx: 3 }));
  parts.push(txt(80, 130, (slide.eyebrow || "").toUpperCase(), { size: 14, color: theme.muted, font: theme.font, weight: 500 }));
  parts.push(txt(80, 180, slide.title || "Section", { size: 42, color: theme.text, font: theme.titleFont, weight: 700 }));
  if (slide.lead) parts.push(txt(80, 230, slide.lead, { size: 20, color: theme.muted, font: theme.font, weight: 400, lh: 1.4 }));
  const bullets = slide.bullets || [];
  const startY = slide.lead ? 310 : 270;
  bullets.forEach((b, i) => {
    const y = startY + i * 70;
    const text = typeof b === "string" ? b : b.text;
    const note = typeof b === "object" ? b.note : null;
    parts.push(rect(80, y - 24, 8, 8, { fill: theme.accent, rx: 2 }));
    parts.push(txt(110, y, text, { size: 22, color: theme.text, font: theme.font, weight: 500 }));
    if (note) parts.push(txt(110, y + 26, note, { size: 16, color: theme.muted, font: theme.font, weight: 400 }));
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function layoutTwoColumn(slide, theme, fmt) {
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  parts.push(rect(80, 78, 60, 6, { fill: theme.accentBar, rx: 3 }));
  parts.push(txt(80, 130, (slide.eyebrow || "").toUpperCase(), { size: 14, color: theme.muted, font: theme.font, weight: 500 }));
  parts.push(txt(80, 180, slide.title || "Comparison", { size: 38, color: theme.text, font: theme.titleFont, weight: 700 }));
  const colW = (w - 240) / 2;
  const colY = 250;
  const colH = h - 320;
  const cols = [
    { x: 80, data: slide.left || {} },
    { x: 80 + colW + 80, data: slide.right || {} }
  ];
  cols.forEach(({ x, data }) => {
    parts.push(rect(x, colY, colW, colH, { fill: theme.panel, rx: 8, opacity: 0.6 }));
    parts.push(rect(x, colY, 4, colH, { fill: theme.accent, rx: 2 }));
    parts.push(txt(x + 24, colY + 50, data.heading || "", { size: 24, color: theme.accent, font: theme.titleFont, weight: 700 }));
    parts.push(txt(x + 24, colY + 90, data.subheading || "", { size: 16, color: theme.muted, font: theme.font, weight: 400 }));
    const items = data.items || [];
    items.forEach((item, i) => {
      const y = colY + 140 + i * 44;
      parts.push(rect(x + 24, y - 16, 6, 6, { fill: theme.accent }));
      parts.push(txt(x + 40, y, item, { size: 18, color: theme.text, font: theme.font, weight: 400 }));
    });
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function layoutKpiGrid(slide, theme, fmt) {
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  parts.push(rect(80, 78, 60, 6, { fill: theme.accentBar, rx: 3 }));
  parts.push(txt(80, 130, (slide.eyebrow || "METRICS").toUpperCase(), { size: 14, color: theme.muted, font: theme.font, weight: 500 }));
  parts.push(txt(80, 180, slide.title || "Key Metrics", { size: 38, color: theme.text, font: theme.titleFont, weight: 700 }));
  const kpis = slide.kpis || [];
  const cols = kpis.length <= 3 ? kpis.length : Math.ceil(Math.sqrt(kpis.length));
  const rows = Math.ceil(kpis.length / cols);
  const cellW = (w - 160 - (cols - 1) * 24) / cols;
  const cellH = Math.min(180, (h - 280 - (rows - 1) * 24) / rows);
  kpis.forEach((kpi, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = 80 + col * (cellW + 24);
    const y = 250 + row * (cellH + 24);
    parts.push(rect(x, y, cellW, cellH, { fill: theme.panel, rx: 8, opacity: 0.7 }));
    parts.push(rect(x, y, 4, cellH, { fill: theme.accent, rx: 2 }));
    parts.push(txt(x + 24, y + 40, kpi.label || "", { size: 14, color: theme.muted, font: theme.font, weight: 500 }));
    parts.push(txt(x + 24, y + 95, kpi.value || "—", { size: 44, color: theme.accent, font: theme.titleFont, weight: 700 }));
    if (kpi.unit) parts.push(txt(x + 24 + (kpi.value || "").length * 26, y + 95, kpi.unit, { size: 20, color: theme.muted, font: theme.font, weight: 400 }));
    if (kpi.delta) {
      const deltaColor = String(kpi.delta).startsWith("-") ? "#EF4444" : "#10B981";
      parts.push(txt(x + 24, y + cellH - 24, kpi.delta, { size: 16, color: deltaColor, font: theme.titleFont, weight: 600 }));
    }
    if (kpi.note) parts.push(txt(x + cellW - 24, y + cellH - 24, kpi.note, { size: 13, color: theme.muted, font: theme.font, weight: 400, anchor: "end" }));
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function layoutPullquote(slide, theme, fmt) {
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  parts.push(txt(120, 210, "“", { size: 200, color: theme.accent, font: theme.titleFont, weight: 700, anchor: "start" }));
  parts.push(txt(w / 2, h / 2, slide.quote || "", { size: 38, color: theme.text, font: theme.titleFont, weight: 500, anchor: "middle", lh: 1.4 }));
  parts.push(rect(w / 2 - 40, h - 200, 80, 2, { fill: theme.accentBar }));
  parts.push(txt(w / 2, h - 150, slide.author || "—", { size: 20, color: theme.muted, font: theme.font, weight: 500, anchor: "middle" }));
  if (slide.role) parts.push(txt(w / 2, h - 118, slide.role, { size: 14, color: theme.muted, font: theme.font, weight: 400, anchor: "middle" }));
  parts.push(svgClose());
  return parts.join("\n");
}

function layoutBentoGrid(slide, theme, fmt) {
  // Apple-inspired bento grid: 3 columns × N rows of unequal-span tiles.
  // Tile spec: { span: 1|2|3, label, value, caption, accent?: "gold"|"accent"|"accent2", ratio?: number }
  // Auto-pack tiles row-by-row, wrapping when sum(span) > 3.
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  const pad = 80, gutter = 20, cols = 3;
  parts.push(rect(pad, 78, 60, 6, { fill: theme.accentBar, rx: 3 }));
  parts.push(txt(pad, 130, (slide.eyebrow || "FEATURES").toUpperCase(), { size: 14, color: theme.muted, font: theme.font, weight: 500 }));
  parts.push(txt(pad, 180, slide.title || "Highlights", { size: 36, color: theme.text, font: theme.titleFont, weight: 700 }));

  const tiles = (slide.tiles || []).map(t => ({
    span: Math.min(cols, Math.max(1, parseInt(t.span || 1, 10))),
    label: t.label || "",
    value: t.value || "",
    caption: t.caption || "",
    accent: t.accent || "accent",  // "accent" | "accent2" | "gold"
  }));
  if (tiles.length === 0) {
    parts.push(svgClose());
    return parts.join("\n");
  }

  // Greedy row packing
  const rows = []; let row = []; let used = 0;
  for (const t of tiles) {
    if (used + t.span > cols) { if (row.length) rows.push(row); row = []; used = 0; }
    row.push(t); used += t.span;
  }
  if (row.length) rows.push(row);

  const gridTop = 240;
  const gridBottom = h - pad;
  const cellW = (w - 2*pad - (cols-1)*gutter) / cols;
  const rowH = Math.min(180, (gridBottom - gridTop - (rows.length-1)*gutter) / Math.max(1, rows.length));

  rows.forEach((r, ri) => {
    let x = pad;
    const y = gridTop + ri * (rowH + gutter);
    r.forEach((t) => {
      const tw = cellW * t.span + gutter * (t.span - 1);
      const accentClr = t.accent === "gold" ? theme.gold : (t.accent === "accent2" ? theme.accent2 : theme.accent);
      parts.push(rect(x, y, tw, rowH, { fill: theme.panel, rx: 14, opacity: 0.85 }));
      parts.push(rect(x, y, 4, rowH, { fill: accentClr, rx: 2 }));
      parts.push(txt(x + 24, y + 36, t.label.toUpperCase(), { size: 12, color: theme.muted, font: theme.font, weight: 600 }));
      // Value: bigger when tile spans more cells
      const vSize = t.span === 1 ? 40 : (t.span === 2 ? 58 : 76);
      parts.push(txt(x + 24, y + rowH/2 + vSize/3, t.value, { size: vSize, color: accentClr, font: theme.titleFont, weight: 700 }));
      if (t.caption) parts.push(txt(x + 24, y + rowH - 22, t.caption, { size: 14, color: theme.text, font: theme.font, weight: 400 }));
      x += tw + gutter;
    });
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function layoutClosing(slide, theme, fmt) {
  const { w, h } = fmt;
  const parts = [svgOpen(w, h, theme)];
  parts.push(circle(w / 2, h / 2 - 60, 240, { stroke: theme.accent, strokeWidth: 2, opacity: 0.4 }));
  parts.push(circle(w / 2, h / 2 - 60, 160, { stroke: theme.accent, strokeWidth: 2, opacity: 0.6 }));
  parts.push(circle(w / 2, h / 2 - 60, 80, { fill: theme.accent, opacity: 0.15 }));
  parts.push(txt(w / 2, h / 2 - 40, slide.title || "Thank You", { size: 64, color: theme.text, font: theme.titleFont, weight: 700, anchor: "middle" }));
  if (slide.subtitle) parts.push(txt(w / 2, h / 2 + 30, slide.subtitle, { size: 20, color: theme.muted, font: theme.font, weight: 400, anchor: "middle" }));
  const contacts = slide.contacts || [];
  contacts.forEach((c, i) => {
    parts.push(txt(w / 2, h - 220 + i * 32, c, { size: 18, color: theme.accent, font: theme.font, weight: 500, anchor: "middle" }));
  });
  parts.push(svgClose());
  return parts.join("\n");
}

const LAYOUTS = {
  "title-cover": layoutTitleCover,
  "agenda": layoutAgenda,
  "section-divider": layoutSectionDivider,
  "title-bullets": layoutTitleBullets,
  "two-column": layoutTwoColumn,
  "kpi-grid": layoutKpiGrid,
  "pullquote": layoutPullquote,
  "bento-grid": layoutBentoGrid,
  "closing": layoutClosing
};

// ─────────────────────────────────────────────────────────────────────────────
// Main
// ─────────────────────────────────────────────────────────────────────────────

function parseArgs(argv) {
  const args = { positional: [], flags: {} };
  for (let i = 2; i < argv.length; i++) {
    const a = argv[i];
    if (a.startsWith("--")) {
      const eq = a.indexOf("=");
      if (eq > 0) args.flags[a.slice(2, eq)] = a.slice(eq + 1);
      else if (argv[i + 1] && !argv[i + 1].startsWith("--")) { args.flags[a.slice(2)] = argv[++i]; }
      else args.flags[a.slice(2)] = true;
    } else args.positional.push(a);
  }
  return args;
}

function main() {
  const { positional, flags } = parseArgs(process.argv);
  if (positional.length === 0) {
    console.error("Usage: make-pptx-deck.mjs <spec.json> [--out PATH] [--theme deep-space|terminal|deck-light] [--format ppt169|ppt43] [--anim ANIM] [--trans TRANS] [--no-build] [--with-notes]");
    process.exit(2);
  }
  const specPath = path.resolve(positional[0]);
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const theme = THEMES[flags.theme || spec.theme || "deep-space"];
  if (!theme) { console.error("Unknown theme. Pick: deep-space | terminal | deck-light"); process.exit(2); }
  const fmt = FORMATS[flags.format || spec.format || "ppt169"];
  if (!fmt) { console.error("Unknown format. Pick: ppt169 | ppt43"); process.exit(2); }

  const baseName = (spec.name || path.basename(specPath, ".json")).replace(/[^A-Za-z0-9_-]/g, "_");
  const outRoot = path.resolve(flags.out || path.join(path.dirname(specPath), `${baseName}_pptx_build`));
  const svgDir = path.join(outRoot, "svg_output");
  const notesDir = path.join(outRoot, "speaker_notes");
  fs.mkdirSync(svgDir, { recursive: true });
  if (flags["with-notes"]) fs.mkdirSync(notesDir, { recursive: true });

  const slides = spec.slides || [];
  slides.forEach((slide, idx) => {
    const layout = LAYOUTS[slide.layout];
    if (!layout) { console.error(`slide ${idx + 1}: unknown layout "${slide.layout}". Skipping.`); return; }
    const svg = layout(slide, theme, fmt);
    const id = (slide.id || `slide${idx + 1}`).replace(/[^A-Za-z0-9_-]/g, "_");
    const file = path.join(svgDir, `slide_${String(idx + 1).padStart(2, "0")}_${id}.svg`);
    fs.writeFileSync(file, svg);
    if (flags["with-notes"] && slide.notes) {
      fs.writeFileSync(path.join(notesDir, `slide_${String(idx + 1).padStart(2, "0")}_${id}.txt`), slide.notes);
    }
  });

  // Write a minimal design_spec.md so ppt-master can locate the project
  fs.writeFileSync(
    path.join(outRoot, "design_spec.md"),
    `# ${spec.name || "viz-deck export"}\n\nGenerated by viz-deck (theme: ${flags.theme || spec.theme || "deep-space"}, format: ${flags.format || spec.format || "ppt169"}).\n\n${slides.length} slides.\n`
  );

  console.log(`[viz-deck] wrote ${slides.length} SVGs → ${svgDir}`);

  if (flags["no-build"]) { console.log(`[viz-deck] --no-build set; skipping pptx assembly.`); return; }

  const pptxOut = flags.pptx || path.join(outRoot, "exports", `${baseName}.pptx`);
  fs.mkdirSync(path.dirname(pptxOut), { recursive: true });

  const cliArgs = [SVG_TO_PPTX, outRoot, "-o", pptxOut, "-f", flags.format || spec.format || "ppt169"];
  if (flags.anim) cliArgs.push("-a", flags.anim);
  if (flags.trans) cliArgs.push("-t", flags.trans);
  if (flags["animation-trigger"]) cliArgs.push("--animation-trigger", flags["animation-trigger"]);
  if (flags["narration-audio-dir"]) cliArgs.push("--narration-audio-dir", flags["narration-audio-dir"]);
  if (flags["use-narration-timings"]) cliArgs.push("--use-narration-timings");

  console.log(`[viz-deck] running ppt-master:`, PYTHON, cliArgs.join(" "));
  try {
    execFileSync(PYTHON, cliArgs, { stdio: "inherit" });
    console.log(`[viz-deck] ✓ editable PPTX written: ${pptxOut}`);
  } catch (err) {
    console.error(`[viz-deck] ppt-master failed:`, err.message);
    process.exit(1);
  }
}

main();
