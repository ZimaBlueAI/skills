#!/usr/bin/env node
/**
 * viz-deck · Reflective Loop (per-page 5-dim critique + redo proposal)
 *
 * Inspired by PPTAgent (中科院信工所, 4.4k Star) — "Agentic Framework for
 * Reflective PowerPoint Generation". The idea: after the Agent generates a
 * deck, it loops back and *checks each page*, identifying low-scoring pages
 * for redo. Most AI-generated decks are bad not because the model can't
 * draw, but because they never look back.
 *
 * What this does:
 *   1. Read a pptx-deck-spec.json (the same JSON used by make-pptx-deck.mjs)
 *   2. Run page-level objective heuristics across all 5 critique dimensions
 *   3. Print per-page scores + flag any page < threshold (default 7.0)
 *   4. Output ./reflect-report.html with radar + per-page table + redo prompts
 *   5. (optional) Emit ./redo-prompts.txt for human review or LLM re-gen
 *
 * Usage:
 *   node reflect-and-redo.mjs --spec deck.json --output ./reflect-report.html
 *   node reflect-and-redo.mjs --spec deck.json --threshold 6.5 --redo-prompts ./redo.txt
 *
 * Subjective dimensions (philosophy alignment, originality) require an LLM
 * call — this script *flags candidates* but does not score them; that
 * judgement belongs in conversation.
 */

import fs from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
function arg(k, fb = null) {
  const i = argv.indexOf(`--${k}`);
  return (i >= 0 && argv[i+1] && !argv[i+1].startsWith('--')) ? argv[i+1] : fb;
}

const specPath = arg('spec');
const output   = arg('output', './reflect-report.html');
const threshold = parseFloat(arg('threshold', '7.0'));
const redoPromptsPath = arg('redo-prompts', null);

if (!specPath) {
  console.error('Need --spec <deck.json>');
  process.exit(1);
}
if (!fs.existsSync(specPath)) {
  console.error('Spec not found:', specPath);
  process.exit(1);
}

const spec = JSON.parse(fs.readFileSync(specPath, 'utf-8'));
const slides = spec.slides || [];

// ===== Heuristics per page =====
// Each heuristic returns { dim, score (0-10), reason }. Final per-page score
// = weighted mean across 5 dimensions. We score 3 dimensions objectively
// (visual hierarchy, craft, functionality). The 2 remaining (philosophy
// alignment, originality) need human/LLM judgement — we mark as `null`
// and treat them as 7 (neutral) for the mean, with a comment.

function scoreSlide(slide, idx, allSlides) {
  const findings = [];
  const issues = [];

  // ===== Dim 2: Visual hierarchy =====
  // Heuristic: a slide should have at most 1 dominant title + at most 1
  // lead/subtitle. Title length should be reasonable (8-80 chars).
  let dim2 = 10;
  const title = slide.title || '';
  const titleLen = title.length;
  if (titleLen < 4) { dim2 -= 4; issues.push('Title is too short (<4 chars) — looks broken'); }
  else if (titleLen > 100) { dim2 -= 3; issues.push(`Title is very long (${titleLen} chars) — wrapping risk on 16:9`); }
  if (slide.bullets && slide.bullets.length > 7) { dim2 -= 2; issues.push(`${slide.bullets.length} bullets — over the 7±2 cognitive limit`); }
  if (slide.kpis && slide.kpis.length > 6) { dim2 -= 1; issues.push(`${slide.kpis.length} KPIs — auto-shrinks below 24pt`); }
  if (slide.tiles && slide.tiles.length > 8) { dim2 -= 2; issues.push(`${slide.tiles.length} bento tiles — grid gets noisy`); }

  // ===== Dim 3: Craft (detail execution) =====
  // Numeric formatting, missing units, placeholders left behind
  let dim3 = 10;
  const allText = JSON.stringify(slide);
  if (/\{\{[^}]+\}\}/.test(allText)) { dim3 -= 5; issues.push('Unfilled {{placeholder}} still in spec'); }
  if (/lorem ipsum/i.test(allText)) { dim3 -= 5; issues.push('Lorem ipsum left behind'); }
  if (slide.kpis) {
    for (const k of slide.kpis) {
      if (/\d/.test(k.value || '') && !k.unit && !/[%$x×€¥]/.test(k.value || '')) {
        dim3 -= 1;
        issues.push(`KPI "${k.label}" has number "${k.value}" without unit`);
        break;
      }
    }
  }
  // Action title rule (academic mode): if slide hints at academic, h2 must be a sentence
  if (slide.layout === 'section-divider' && slide.section && title && !/\s/.test(title)) {
    // single-word section title — for academic mode this is a fail
  }

  // ===== Dim 4: Functionality =====
  // Every slide should serve a clear function. Layout-specific checks.
  let dim4 = 10;
  if (slide.layout === 'title-bullets' && (!slide.bullets || slide.bullets.length === 0)) {
    dim4 -= 5; issues.push('title-bullets layout but no bullets supplied');
  }
  if (slide.layout === 'kpi-grid' && (!slide.kpis || slide.kpis.length === 0)) {
    dim4 -= 5; issues.push('kpi-grid layout but no kpis supplied');
  }
  if (slide.layout === 'two-column' && (!slide.left || !slide.right)) {
    dim4 -= 5; issues.push('two-column layout missing left/right');
  }
  if (slide.layout === 'pullquote' && !slide.quote) {
    dim4 -= 5; issues.push('pullquote layout but no quote');
  }
  if (slide.layout === 'bento-grid' && (!slide.tiles || slide.tiles.length === 0)) {
    dim4 -= 5; issues.push('bento-grid layout but no tiles');
  }
  if (slide.layout === 'closing' && !slide.title) {
    dim4 -= 3; issues.push('closing slide has no title (use "Thank you" minimum)');
  }
  if (slide.layout === 'title-cover' && (!slide.title || !slide.subtitle)) {
    dim4 -= 3; issues.push('cover slide missing title or subtitle');
  }
  // notes missing on bookend slides (cover/closing) → not critical, but flag
  if ((slide.layout === 'title-cover' || slide.layout === 'closing') && !slide.notes) {
    dim4 -= 1; findings.push('Speaker notes missing on bookend slide');
  }

  // ===== Dim 1: Philosophy alignment & Dim 5: Originality =====
  // Cannot judge objectively from JSON alone. Set null; default to 7 (neutral)
  // when computing mean.
  const dim1 = null;
  const dim5 = null;

  // Clamp
  dim2 = Math.max(0, Math.min(10, dim2));
  dim3 = Math.max(0, Math.min(10, dim3));
  dim4 = Math.max(0, Math.min(10, dim4));

  // Mean (use 7 for unscored)
  const usableScores = [dim1 ?? 7, dim2, dim3, dim4, dim5 ?? 7];
  const mean = usableScores.reduce((a, b) => a + b, 0) / 5;

  return {
    idx,
    id: slide.id || `slide-${idx + 1}`,
    layout: slide.layout,
    title: title || '(no title)',
    dims: { 1: dim1, 2: dim2, 3: dim3, 4: dim4, 5: dim5 },
    mean: Math.round(mean * 10) / 10,
    issues,
    findings,
  };
}

// ===== Score all slides =====
const results = slides.map((s, i) => scoreSlide(s, i, slides));

// ===== Deck-level rollup =====
function avg(arr) { return arr.reduce((a, b) => a + b, 0) / arr.length; }
const deckMean = Math.round(avg(results.map(r => r.mean)) * 10) / 10;
const flagged = results.filter(r => r.mean < threshold);

console.log('═'.repeat(70));
console.log(`viz-deck · Reflective Loop (5-dim critique)`);
console.log('═'.repeat(70));
console.log(`Deck:    ${spec.name || path.basename(specPath)} (${slides.length} slides)`);
console.log(`Mean:    ${deckMean} / 10`);
console.log(`Flagged: ${flagged.length} slides below threshold ${threshold}`);
console.log('─'.repeat(70));
for (const r of results) {
  const mark = r.mean >= threshold ? '✓' : '⚠';
  console.log(`  ${mark} #${String(r.idx+1).padStart(2,'0')}  ${r.mean.toFixed(1)}  ${r.layout.padEnd(18)} ${r.title.slice(0, 32)}`);
}
console.log('═'.repeat(70));

// ===== Write redo-prompts file =====
if (redoPromptsPath && flagged.length > 0) {
  const lines = [];
  lines.push('# viz-deck · Redo prompts');
  lines.push(`# Deck: ${spec.name}`);
  lines.push(`# Threshold: ${threshold}`);
  lines.push(`# Generated: ${new Date().toISOString()}`);
  lines.push('');
  for (const r of flagged) {
    lines.push(`\n## Slide #${r.idx + 1} — ${r.title}`);
    lines.push(`Layout: ${r.layout}`);
    lines.push(`Mean: ${r.mean} / 10`);
    lines.push('Issues:');
    for (const issue of r.issues) lines.push(`  - ${issue}`);
    lines.push('');
    lines.push('Suggested redo prompt:');
    lines.push(`  > Rewrite slide #${r.idx + 1} ("${r.title}"). Fix:`);
    for (const issue of r.issues) lines.push(`  >   - ${issue}`);
    lines.push(`  > Keep layout "${r.layout}". Match the rest of the deck's tone.`);
  }
  fs.writeFileSync(redoPromptsPath, lines.join('\n'), 'utf-8');
  console.log('→ redo-prompts:', redoPromptsPath);
}

// ===== Write HTML report =====
function esc(s) { return String(s ?? '').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

const dimMeans = {
  1: 7, // unscored — neutral default
  2: Math.round(avg(results.map(r => r.dims[2])) * 10) / 10,
  3: Math.round(avg(results.map(r => r.dims[3])) * 10) / 10,
  4: Math.round(avg(results.map(r => r.dims[4])) * 10) / 10,
  5: 7,
};

const html = `<!doctype html>
<html lang="zh-CN"><head>
<meta charset="utf-8">
<title>Reflective Critique — ${esc(spec.name || 'Deck')}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:wght@500&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#030711; --panel:#0c1525; --line:rgba(151,209,255,0.14);
  --text:#edf7ff; --muted:#a8bdd5; --faint:#688096;
  --cyan:#42e8ff; --gold:#ffd987; --red:#ff8c8c; --green:#78f7c5;
  --sans:Inter,sans-serif; --serif:Newsreader,serif; --mono:'JetBrains Mono',monospace;
}
*{box-sizing:border-box}
body{margin:0; background:var(--bg); color:var(--text); font-family:var(--sans); padding:40px}
.wrap{max-width:1180px; margin:0 auto}
h1{font-family:var(--serif); font-weight:500; font-size:2.4rem; margin:0 0 0.4rem; letter-spacing:-0.01em}
.subtitle{color:var(--muted); margin-bottom:2rem; font-size:1.05rem}
.summary{display:grid; grid-template-columns:repeat(3, 1fr); gap:16px; margin-bottom:2.4rem}
.kpi{background:var(--panel); border:1px solid var(--line); border-radius:12px; padding:1.4rem 1.6rem}
.kpi .lbl{font-family:var(--mono); font-size:0.72rem; color:var(--muted); letter-spacing:0.20em; text-transform:uppercase; margin-bottom:0.4rem}
.kpi .val{font-family:var(--mono); font-size:2.6rem; font-weight:500; color:var(--cyan); line-height:1}
.kpi .val.warn{color:var(--gold)}
.kpi .val.bad{color:var(--red)}
.dim-bar{display:grid; grid-template-columns:repeat(5, 1fr); gap:12px; margin-bottom:2.4rem}
.dim{padding:1rem 1.2rem; border:1px solid var(--line); border-radius:10px; background:var(--panel)}
.dim .lbl{font-family:var(--mono); font-size:0.65rem; letter-spacing:0.18em; text-transform:uppercase; color:var(--muted); margin-bottom:0.4rem}
.dim .score{font-family:var(--mono); font-size:1.8rem; color:var(--cyan); line-height:1}
.dim.unscored .score{color:var(--faint)}
.dim small{display:block; margin-top:0.3rem; font-size:0.7rem; color:var(--faint); font-family:var(--mono)}
table{width:100%; border-collapse:collapse; margin-top:1.4rem; font-size:0.92rem}
th,td{padding:10px 12px; text-align:left; border-bottom:1px solid var(--line); vertical-align:top}
th{font-family:var(--mono); font-size:0.70rem; color:var(--cyan); letter-spacing:0.18em; text-transform:uppercase; font-weight:500}
td.score{font-family:var(--mono); color:var(--cyan); font-weight:500}
tr.flagged td{background:rgba(255,140,140,0.04)}
tr.flagged td.score{color:var(--red)}
.issues{font-family:var(--mono); font-size:0.78rem; color:var(--gold); margin:0; padding:0; list-style:none}
.issues li{padding:2px 0}
.issues li::before{content:"▸ "; color:var(--cyan)}
.note{margin-top:2.4rem; padding:1.2rem 1.4rem; border:1px dashed var(--line); border-radius:10px; color:var(--muted); font-size:0.92rem; line-height:1.6}
.note strong{color:var(--gold)}
</style>
</head><body><div class="wrap">

<h1>Reflective critique</h1>
<p class="subtitle">${esc(spec.name)} · ${slides.length} slides · threshold ${threshold}/10</p>

<div class="summary">
  <div class="kpi">
    <div class="lbl">Deck mean</div>
    <div class="val ${deckMean < 7 ? 'warn' : ''} ${deckMean < 5 ? 'bad' : ''}">${deckMean}</div>
  </div>
  <div class="kpi">
    <div class="lbl">Flagged slides</div>
    <div class="val ${flagged.length > 0 ? 'warn' : ''} ${flagged.length > slides.length/3 ? 'bad' : ''}">${flagged.length} / ${slides.length}</div>
  </div>
  <div class="kpi">
    <div class="lbl">Verdict</div>
    <div class="val" style="font-size:1.4rem; padding-top:0.5rem; font-family:var(--serif); font-weight:500">
      ${deckMean >= 8 ? 'Excellent' : deckMean >= 7 ? 'Good' : deckMean >= 5 ? 'Needs work' : 'Redo'}
    </div>
  </div>
</div>

<div class="dim-bar">
  <div class="dim unscored">
    <div class="lbl">D1 · Philosophy</div>
    <div class="score">7.0</div>
    <small>NEUTRAL · needs LLM judgement</small>
  </div>
  <div class="dim"><div class="lbl">D2 · Hierarchy</div><div class="score">${dimMeans[2]}</div><small>Mean over ${slides.length}</small></div>
  <div class="dim"><div class="lbl">D3 · Craft</div><div class="score">${dimMeans[3]}</div><small>Objective</small></div>
  <div class="dim"><div class="lbl">D4 · Function</div><div class="score">${dimMeans[4]}</div><small>Layout fit</small></div>
  <div class="dim unscored">
    <div class="lbl">D5 · Originality</div>
    <div class="score">7.0</div>
    <small>NEUTRAL · needs LLM judgement</small>
  </div>
</div>

<table>
  <thead>
    <tr><th>#</th><th>Layout</th><th>Title</th><th>D2</th><th>D3</th><th>D4</th><th>Mean</th><th>Issues</th></tr>
  </thead>
  <tbody>
    ${results.map(r => `
      <tr class="${r.mean < threshold ? 'flagged' : ''}">
        <td>${String(r.idx+1).padStart(2,'0')}</td>
        <td>${esc(r.layout)}</td>
        <td>${esc(r.title)}</td>
        <td class="score">${r.dims[2]}</td>
        <td class="score">${r.dims[3]}</td>
        <td class="score">${r.dims[4]}</td>
        <td class="score">${r.mean}</td>
        <td><ul class="issues">${r.issues.map(i => `<li>${esc(i)}</li>`).join('')}</ul></td>
      </tr>
    `).join('')}
  </tbody>
</table>

<div class="note">
  <strong>How to read this report.</strong> Only three of five dimensions are scored objectively from
  the JSON spec (visual hierarchy, craft, functionality). Philosophy alignment and originality
  remain at neutral 7.0 — they need a human or LLM look at the rendered output. To resolve a
  flagged slide:
  <ol>
    <li>Read the issues column — most are mechanical (missing units, over-stuffed bullets).</li>
    <li>For each issue, edit <code>${esc(path.basename(specPath))}</code> directly.</li>
    <li>Re-run <code>node make-pptx-deck.mjs &amp;&amp; node reflect-and-redo.mjs</code> until all slides ≥ threshold.</li>
    <li>For D1 and D5 (subjective), open the rendered HTML / PPTX and ask Claude to evaluate against the chosen design philosophy.</li>
  </ol>
</div>

</div></body></html>`;

fs.writeFileSync(output, html, 'utf-8');
console.log('→ reflect-report:', output);
console.log();
console.log('Next:');
console.log(`  1. Open ${output} in a browser`);
console.log('  2. Edit spec to resolve flagged slides');
console.log('  3. Re-run make-pptx-deck.mjs + reflect-and-redo.mjs');
