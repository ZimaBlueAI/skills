#!/usr/bin/env node
// biz-decision-stack → ppt-master bridge (terminal-themed editable PPTX)
// JSON decision-report spec → SVG per slide → native DrawingML PPTX
//
// Distinct from viz-deck's make-pptx-deck.mjs:
//   - Locked to "terminal" theme (black bg + acid-yellow + JetBrains Mono)
//   - Decision-report layouts: verdict-cover, kpi-roster, decision-matrix,
//     roadmap-phases, risks-grid, retro-3col, action-list, summary-stack
//   - Zero motion philosophy: --anim defaults to "appear" (no entrance choreography)
//   - For scan-only print/archive — every shape clickable for sign-off edits
//
// Usage:
//   node make-decision-pptx.mjs <spec.json> [--out PATH] [--no-build]
//
// Spec example: specs/board-brief-decision-pptx.example.json

import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import os from "node:os";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const HOME = os.homedir();

// ppt-master detection: $PPT_MASTER_HOME -> ~/.codex/skills/ppt-master (Codex) -> ~/.agents/skills/ppt-master (legacy Codex) -> ~/.claude/skills/ppt-master (Claude Code)
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
  return candidates[1];
}
const PPT_MASTER = findPptMaster();
const PYTHON = process.platform === "win32"
  ? path.join(PPT_MASTER, ".venv", "Scripts", "python.exe")
  : path.join(PPT_MASTER, ".venv", "bin", "python");
const SVG_TO_PPTX = path.join(PPT_MASTER, "skills", "ppt-master", "scripts", "svg_to_pptx.py");

// Locked terminal theme — biz-decision-stack signature aesthetic
const THEME = {
  bg: "#0A0A0A", surface: "#101010", panel: "#161616",
  border: "#262626", text: "#F5F5F5", muted: "#9CA3AF",
  accent: "#D4FF00",        // acid yellow — verdict, KPIs, decisions
  accent2: "#FFFFFF",
  go: "#D4FF00",            // GO / proceed / approved
  hold: "#FFB800",          // HOLD / re-examine
  stop: "#EF4444",          // STOP / blocker
  font: "'JetBrains Mono', 'Cascadia Code', 'Source Code Pro', monospace",
  titleFont: "'JetBrains Mono', monospace"
};

const FMT = { w: 1280, h: 720 };

// ─── SVG primitives ─────────────────────────────────────────────────────────

const esc = s => String(s ?? "")
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
  .replace(/"/g, "&quot;");

const svgOpen = () => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${FMT.w} ${FMT.h}" width="${FMT.w}" height="${FMT.h}">
  <rect width="${FMT.w}" height="${FMT.h}" fill="${THEME.bg}"/>`;

const svgClose = () => `</svg>`;

const txt = (x, y, content, o = {}) => {
  const fz = o.size || 20;
  const fw = o.weight || 400;
  const fill = o.color || THEME.text;
  const family = o.font || THEME.font;
  const anchor = o.anchor || "start";
  const lh = o.lh || 1.35;
  const lines = String(content ?? "").split("\n");
  return lines.map((line, i) =>
    `<text x="${x}" y="${y + i * fz * lh}" font-family="${family}" font-size="${fz}" font-weight="${fw}" fill="${fill}" text-anchor="${anchor}">${esc(line)}</text>`
  ).join("\n  ");
};

const rect = (x, y, w, h, o = {}) =>
  `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${o.fill || "transparent"}" stroke="${o.stroke || "none"}" stroke-width="${o.strokeWidth || 0}" rx="${o.rx || 0}" opacity="${o.opacity ?? 1}"/>`;

const line = (x1, y1, x2, y2, o = {}) =>
  `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${o.stroke || THEME.border}" stroke-width="${o.strokeWidth || 1}" stroke-dasharray="${o.dash || "none"}"/>`;

// ─── chrome (terminal header bar) ───────────────────────────────────────────

const chrome = (label, sub) => [
  rect(0, 0, FMT.w, 44, { fill: THEME.surface }),
  rect(0, 44, FMT.w, 1, { fill: THEME.border }),
  txt(40, 28, `▍ ${label}`, { size: 14, color: THEME.accent, weight: 700, font: THEME.titleFont }),
  sub ? txt(FMT.w - 40, 28, sub, { size: 12, color: THEME.muted, anchor: "end", weight: 500 }) : ""
].filter(Boolean).join("\n  ");

// ─── layouts ────────────────────────────────────────────────────────────────

function verdictCover(s) {
  const verdict = (s.verdict || "GO").toUpperCase();
  const verdictColor = verdict === "GO" ? THEME.go : verdict === "STOP" ? THEME.stop : THEME.hold;
  const parts = [svgOpen()];
  parts.push(chrome(s.kind || "BOARD BRIEF", s.date || ""));
  parts.push(txt(60, 120, `# ${s.code || s.brief_id || "DEC-001"}`, { size: 14, color: THEME.muted, weight: 500 }));
  parts.push(txt(60, 200, s.title || "Decision Brief", { size: 42, color: THEME.text, weight: 700, font: THEME.titleFont, lh: 1.15 }));
  if (s.subtitle) parts.push(txt(60, 270, s.subtitle, { size: 22, color: THEME.muted, weight: 400, lh: 1.4 }));
  // Verdict band
  parts.push(rect(60, 340, FMT.w - 120, 110, { fill: THEME.panel, rx: 4 }));
  parts.push(rect(60, 340, 6, 110, { fill: verdictColor }));
  parts.push(txt(90, 380, "VERDICT", { size: 12, color: THEME.muted, weight: 600 }));
  parts.push(txt(90, 430, verdict, { size: 38, color: verdictColor, weight: 700, font: THEME.titleFont }));
  if (s.verdict_note) parts.push(txt(320, 410, s.verdict_note, { size: 18, color: THEME.text, weight: 400, lh: 1.4 }));
  // Footer
  parts.push(rect(60, FMT.h - 80, FMT.w - 120, 1, { fill: THEME.border }));
  parts.push(txt(60, FMT.h - 40, s.author || "ZimaBlueAI · biz-decision-stack", { size: 13, color: THEME.muted, weight: 500 }));
  if (s.ref) parts.push(txt(FMT.w - 60, FMT.h - 40, s.ref, { size: 13, color: THEME.muted, weight: 500, anchor: "end" }));
  parts.push(svgClose());
  return parts.join("\n");
}

function kpiRoster(s) {
  const parts = [svgOpen()];
  parts.push(chrome(s.kind || "KPI ROSTER", s.date || ""));
  parts.push(txt(60, 100, "$", { size: 14, color: THEME.accent, weight: 700 }));
  parts.push(txt(78, 100, s.title || "Quarterly metrics", { size: 26, color: THEME.text, weight: 700, font: THEME.titleFont }));
  if (s.lead) parts.push(txt(60, 138, s.lead, { size: 14, color: THEME.muted, weight: 400 }));
  const kpis = s.kpis || [];
  const cols = kpis.length <= 4 ? kpis.length : Math.ceil(kpis.length / 2);
  const rows = Math.ceil(kpis.length / cols);
  const cellW = (FMT.w - 120 - (cols - 1) * 16) / cols;
  const cellH = Math.min(160, (FMT.h - 220 - (rows - 1) * 16) / rows);
  kpis.forEach((k, i) => {
    const col = i % cols, row = Math.floor(i / cols);
    const x = 60 + col * (cellW + 16);
    const y = 180 + row * (cellH + 16);
    parts.push(rect(x, y, cellW, cellH, { fill: THEME.panel, rx: 2 }));
    parts.push(rect(x, y, 3, cellH, { fill: THEME.accent }));
    parts.push(txt(x + 16, y + 30, k.label || "", { size: 11, color: THEME.muted, weight: 600 }));
    parts.push(txt(x + 16, y + 78, k.value || "—", { size: 36, color: THEME.accent, weight: 700, font: THEME.titleFont }));
    if (k.unit) parts.push(txt(x + 16 + String(k.value || "").length * 22, y + 78, k.unit, { size: 16, color: THEME.muted, weight: 500 }));
    if (k.target) parts.push(txt(x + 16, y + 105, `target ${k.target}`, { size: 11, color: THEME.muted, weight: 500 }));
    if (k.status) {
      const sc = String(k.status).toLowerCase();
      const colr = sc.includes("ahead") || sc === "go" ? THEME.go : sc.includes("behind") || sc === "stop" ? THEME.stop : THEME.hold;
      parts.push(rect(x + cellW - 16 - 8, y + 16, 8, 8, { fill: colr }));
    }
    if (k.note) parts.push(txt(x + 16, y + cellH - 16, k.note, { size: 11, color: THEME.muted, weight: 500 }));
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function decisionMatrix(s) {
  const parts = [svgOpen()];
  parts.push(chrome(s.kind || "DECISION MATRIX", s.date || ""));
  parts.push(txt(60, 100, "$", { size: 14, color: THEME.accent, weight: 700 }));
  parts.push(txt(78, 100, s.title || "Options × Criteria", { size: 26, color: THEME.text, weight: 700, font: THEME.titleFont }));
  if (s.lead) parts.push(txt(60, 138, s.lead, { size: 14, color: THEME.muted, weight: 400 }));
  const options = s.options || [];
  const criteria = s.criteria || [];
  const tableX = 60, tableY = 180, tableW = FMT.w - 120, tableH = FMT.h - 240;
  const headerH = 50;
  const optW = 220;
  const colW = (tableW - optW) / criteria.length;
  const rowH = (tableH - headerH) / options.length;
  // Header row
  parts.push(rect(tableX, tableY, tableW, headerH, { fill: THEME.panel }));
  parts.push(txt(tableX + 20, tableY + 32, "Option", { size: 12, color: THEME.muted, weight: 700 }));
  criteria.forEach((c, i) => {
    const x = tableX + optW + i * colW;
    parts.push(line(x, tableY, x, tableY + tableH, { stroke: THEME.border }));
    parts.push(txt(x + colW / 2, tableY + 32, c, { size: 12, color: THEME.muted, weight: 700, anchor: "middle" }));
  });
  // Body rows
  options.forEach((opt, i) => {
    const y = tableY + headerH + i * rowH;
    if (i > 0) parts.push(line(tableX, y, tableX + tableW, y, { stroke: THEME.border }));
    if (opt.recommended) parts.push(rect(tableX, y, tableW, rowH, { fill: THEME.accent, opacity: 0.05 }));
    parts.push(txt(tableX + 20, y + rowH / 2 + 6, opt.label, { size: 16, color: opt.recommended ? THEME.accent : THEME.text, weight: 600, font: THEME.titleFont }));
    if (opt.sublabel) parts.push(txt(tableX + 20, y + rowH / 2 + 28, opt.sublabel, { size: 11, color: THEME.muted, weight: 400 }));
    (opt.scores || []).forEach((sc, j) => {
      const x = tableX + optW + j * colW + colW / 2;
      const val = typeof sc === "object" ? sc.value : sc;
      const txtColor = sc?.weight === "high" ? THEME.accent : THEME.text;
      parts.push(txt(x, y + rowH / 2 + 8, val ?? "—", { size: 22, color: txtColor, weight: 700, font: THEME.titleFont, anchor: "middle" }));
      if (sc?.note) parts.push(txt(x, y + rowH / 2 + 30, sc.note, { size: 10, color: THEME.muted, weight: 400, anchor: "middle" }));
    });
  });
  parts.push(rect(tableX, tableY, tableW, tableH, { stroke: THEME.border, strokeWidth: 1 }));
  parts.push(svgClose());
  return parts.join("\n");
}

function roadmapPhases(s) {
  const parts = [svgOpen()];
  parts.push(chrome(s.kind || "ROADMAP", s.date || ""));
  parts.push(txt(60, 100, "$", { size: 14, color: THEME.accent, weight: 700 }));
  parts.push(txt(78, 100, s.title || "Roadmap", { size: 26, color: THEME.text, weight: 700, font: THEME.titleFont }));
  if (s.lead) parts.push(txt(60, 138, s.lead, { size: 14, color: THEME.muted, weight: 400 }));
  const phases = s.phases || [];
  const startX = 60, startY = 200, totalW = FMT.w - 120;
  const colW = totalW / phases.length;
  // Timeline line
  parts.push(line(startX, startY + 40, startX + totalW, startY + 40, { stroke: THEME.border, strokeWidth: 2 }));
  phases.forEach((p, i) => {
    const cx = startX + i * colW + colW / 2;
    parts.push(rect(cx - 60, startY, 120, 80, { fill: THEME.panel, rx: 2 }));
    parts.push(rect(cx - 60, startY, 3, 80, { fill: THEME.accent }));
    parts.push(txt(cx - 50, startY + 24, p.phase || `P${i + 1}`, { size: 11, color: THEME.muted, weight: 600 }));
    parts.push(txt(cx - 50, startY + 54, p.range || "", { size: 16, color: THEME.accent, weight: 700, font: THEME.titleFont }));
    // Milestones below
    (p.milestones || []).forEach((m, j) => {
      const y = startY + 120 + j * 40;
      parts.push(rect(cx - 80, y, 160, 32, { fill: THEME.surface, rx: 2 }));
      parts.push(txt(cx - 70, y + 21, m, { size: 12, color: THEME.text, weight: 500 }));
    });
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function risksGrid(s) {
  const parts = [svgOpen()];
  parts.push(chrome(s.kind || "RISKS & MITIGATIONS", s.date || ""));
  parts.push(txt(60, 100, "$", { size: 14, color: THEME.accent, weight: 700 }));
  parts.push(txt(78, 100, s.title || "Risks & mitigations", { size: 26, color: THEME.text, weight: 700, font: THEME.titleFont }));
  if (s.lead) parts.push(txt(60, 138, s.lead, { size: 14, color: THEME.muted, weight: 400 }));
  const colW = (FMT.w - 140) / 2;
  const colY = 180, colH = FMT.h - 240;
  // Left = risks
  parts.push(rect(60, colY, colW, colH, { fill: THEME.panel, rx: 2 }));
  parts.push(rect(60, colY, 3, colH, { fill: THEME.stop }));
  parts.push(txt(80, colY + 30, "RISKS", { size: 12, color: THEME.stop, weight: 700 }));
  (s.risks || []).forEach((r, i) => {
    const y = colY + 70 + i * 70;
    parts.push(rect(80, y - 16, 8, 8, { fill: THEME.stop }));
    parts.push(txt(98, y, r.label || r, { size: 16, color: THEME.text, weight: 600 }));
    if (r.impact) parts.push(txt(98, y + 22, r.impact, { size: 12, color: THEME.muted, weight: 500 }));
    if (r.severity) parts.push(txt(60 + colW - 20, y, r.severity, { size: 11, color: THEME.muted, weight: 700, anchor: "end" }));
  });
  // Right = mitigations
  const x2 = 80 + colW;
  parts.push(rect(x2, colY, colW, colH, { fill: THEME.panel, rx: 2 }));
  parts.push(rect(x2, colY, 3, colH, { fill: THEME.go }));
  parts.push(txt(x2 + 20, colY + 30, "MITIGATIONS", { size: 12, color: THEME.go, weight: 700 }));
  (s.mitigations || []).forEach((m, i) => {
    const y = colY + 70 + i * 70;
    parts.push(rect(x2 + 20, y - 16, 8, 8, { fill: THEME.go }));
    parts.push(txt(x2 + 38, y, m.label || m, { size: 16, color: THEME.text, weight: 600 }));
    if (m.owner) parts.push(txt(x2 + 38, y + 22, `owner: ${m.owner}`, { size: 12, color: THEME.muted, weight: 500 }));
    if (m.due) parts.push(txt(x2 + colW, y, m.due, { size: 11, color: THEME.muted, weight: 700, anchor: "end" }));
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function retro3col(s) {
  const parts = [svgOpen()];
  parts.push(chrome(s.kind || "RETROSPECTIVE", s.date || ""));
  parts.push(txt(60, 100, "$", { size: 14, color: THEME.accent, weight: 700 }));
  parts.push(txt(78, 100, s.title || "Retrospective", { size: 26, color: THEME.text, weight: 700, font: THEME.titleFont }));
  if (s.lead) parts.push(txt(60, 138, s.lead, { size: 14, color: THEME.muted, weight: 400 }));
  const cols = [
    { label: "WORKED", color: THEME.go, items: s.worked || [] },
    { label: "DIDN'T", color: THEME.stop, items: s.didnt || [] },
    { label: "CHANGE", color: THEME.accent, items: s.change || [] }
  ];
  const colW = (FMT.w - 140) / 3;
  const colY = 180, colH = FMT.h - 240;
  cols.forEach((c, idx) => {
    const x = 60 + idx * (colW + 10);
    parts.push(rect(x, colY, colW, colH, { fill: THEME.panel, rx: 2 }));
    parts.push(rect(x, colY, 3, colH, { fill: c.color }));
    parts.push(txt(x + 20, colY + 30, c.label, { size: 12, color: c.color, weight: 700 }));
    c.items.forEach((item, i) => {
      const y = colY + 70 + i * 50;
      const text = typeof item === "string" ? item : item.text;
      const note = typeof item === "object" ? item.note : null;
      parts.push(rect(x + 20, y - 14, 6, 6, { fill: c.color }));
      parts.push(txt(x + 36, y, text, { size: 14, color: THEME.text, weight: 500 }));
      if (note) parts.push(txt(x + 36, y + 18, note, { size: 11, color: THEME.muted, weight: 500 }));
    });
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function actionList(s) {
  const parts = [svgOpen()];
  parts.push(chrome(s.kind || "ACTIONS", s.date || ""));
  parts.push(txt(60, 100, "$", { size: 14, color: THEME.accent, weight: 700 }));
  parts.push(txt(78, 100, s.title || "Action items", { size: 26, color: THEME.text, weight: 700, font: THEME.titleFont }));
  if (s.lead) parts.push(txt(60, 138, s.lead, { size: 14, color: THEME.muted, weight: 400 }));
  // Header
  const headerY = 200, rowH = 56;
  parts.push(rect(60, headerY, FMT.w - 120, 36, { fill: THEME.panel }));
  parts.push(txt(80, headerY + 24, "#", { size: 11, color: THEME.muted, weight: 700 }));
  parts.push(txt(140, headerY + 24, "ACTION", { size: 11, color: THEME.muted, weight: 700 }));
  parts.push(txt(820, headerY + 24, "OWNER", { size: 11, color: THEME.muted, weight: 700 }));
  parts.push(txt(1000, headerY + 24, "DUE", { size: 11, color: THEME.muted, weight: 700 }));
  parts.push(txt(1180, headerY + 24, "STATUS", { size: 11, color: THEME.muted, weight: 700, anchor: "end" }));
  // Rows
  (s.actions || []).forEach((a, i) => {
    const y = headerY + 36 + i * rowH;
    parts.push(line(60, y, FMT.w - 60, y, { stroke: THEME.border }));
    parts.push(txt(80, y + 35, String(i + 1).padStart(2, "0"), { size: 16, color: THEME.accent, weight: 700, font: THEME.titleFont }));
    parts.push(txt(140, y + 30, a.text || a.label || "", { size: 15, color: THEME.text, weight: 500 }));
    if (a.note) parts.push(txt(140, y + 48, a.note, { size: 11, color: THEME.muted, weight: 400 }));
    parts.push(txt(820, y + 35, a.owner || "—", { size: 14, color: THEME.text, weight: 500 }));
    parts.push(txt(1000, y + 35, a.due || "—", { size: 14, color: THEME.text, weight: 500 }));
    const stat = (a.status || "TODO").toUpperCase();
    const sc = stat.includes("DONE") ? THEME.go : stat.includes("BLOCK") ? THEME.stop : THEME.hold;
    parts.push(txt(1180, y + 35, stat, { size: 13, color: sc, weight: 700, anchor: "end" }));
  });
  parts.push(svgClose());
  return parts.join("\n");
}

function summaryStack(s) {
  const parts = [svgOpen()];
  parts.push(chrome(s.kind || "SUMMARY", s.date || ""));
  parts.push(txt(60, 100, "$", { size: 14, color: THEME.accent, weight: 700 }));
  parts.push(txt(78, 100, s.title || "Summary", { size: 26, color: THEME.text, weight: 700, font: THEME.titleFont }));
  if (s.lead) parts.push(txt(60, 138, s.lead, { size: 14, color: THEME.muted, weight: 400 }));
  const items = s.items || [];
  const startY = 200;
  items.forEach((item, i) => {
    const y = startY + i * 60;
    parts.push(rect(60, y, FMT.w - 120, 50, { fill: THEME.panel, rx: 2 }));
    parts.push(rect(60, y, 3, 50, { fill: THEME.accent }));
    parts.push(txt(80, y + 22, item.key, { size: 12, color: THEME.muted, weight: 700 }));
    parts.push(txt(80, y + 42, item.value, { size: 16, color: THEME.text, weight: 600 }));
    if (item.note) parts.push(txt(FMT.w - 80, y + 32, item.note, { size: 12, color: THEME.muted, weight: 500, anchor: "end" }));
  });
  parts.push(svgClose());
  return parts.join("\n");
}

const LAYOUTS = {
  "verdict-cover": verdictCover,
  "kpi-roster": kpiRoster,
  "decision-matrix": decisionMatrix,
  "roadmap-phases": roadmapPhases,
  "risks-grid": risksGrid,
  "retro-3col": retro3col,
  "action-list": actionList,
  "summary-stack": summaryStack
};

// ─── main ───────────────────────────────────────────────────────────────────

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
    console.error("Usage: make-decision-pptx.mjs <spec.json> [--out PATH] [--no-build]");
    process.exit(2);
  }
  const specPath = path.resolve(positional[0]);
  const spec = JSON.parse(fs.readFileSync(specPath, "utf8"));
  const baseName = (spec.name || path.basename(specPath, ".json")).replace(/[^A-Za-z0-9_-]/g, "_");
  const outRoot = path.resolve(flags.out || path.join(path.dirname(specPath), `${baseName}_pptx_build`));
  const svgDir = path.join(outRoot, "svg_output");
  fs.mkdirSync(svgDir, { recursive: true });

  const slides = spec.slides || [];
  slides.forEach((slide, idx) => {
    const layout = LAYOUTS[slide.layout];
    if (!layout) { console.error(`slide ${idx + 1}: unknown layout "${slide.layout}". Available: ${Object.keys(LAYOUTS).join(", ")}`); return; }
    const svg = layout(slide);
    const id = (slide.id || `slide${idx + 1}`).replace(/[^A-Za-z0-9_-]/g, "_");
    const file = path.join(svgDir, `slide_${String(idx + 1).padStart(2, "0")}_${id}.svg`);
    fs.writeFileSync(file, svg);
  });

  fs.writeFileSync(
    path.join(outRoot, "design_spec.md"),
    `# ${spec.name || "decision report"}\n\nTerminal theme (black + acid-yellow), ${slides.length} slides. biz-decision-stack.\n`
  );

  console.log(`[biz-decision] wrote ${slides.length} SVGs → ${svgDir}`);

  if (flags["no-build"]) return;

  const pptxOut = flags.pptx || path.join(outRoot, "exports", `${baseName}.pptx`);
  fs.mkdirSync(path.dirname(pptxOut), { recursive: true });

  const cliArgs = [SVG_TO_PPTX, outRoot, "-o", pptxOut, "-f", "ppt169", "-a", "appear", "-t", "none", "--no-notes"];
  console.log(`[biz-decision] running ppt-master:`, PYTHON, cliArgs.join(" "));
  try {
    execFileSync(PYTHON, cliArgs, { stdio: "inherit" });
    console.log(`[biz-decision] ✓ editable PPTX (terminal theme): ${pptxOut}`);
  } catch (err) {
    console.error(`[biz-decision] ppt-master failed:`, err.message);
    process.exit(1);
  }
}

main();
