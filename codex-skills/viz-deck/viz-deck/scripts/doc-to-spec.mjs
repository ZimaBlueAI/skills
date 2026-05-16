#!/usr/bin/env node
/**
 * viz-deck · Doc → pptx-deck-spec converter
 *
 * Reads a long-form document (Markdown today; DOCX/PDF via pandoc preflight)
 * and emits a pptx-deck-spec JSON suitable for `scripts/make-pptx-deck.mjs`.
 *
 * Inspired by odin-slides (long Word → structured PPT) and colloquium
 * (markdown-native lecture slides). Optimised for "I wrote a long
 * report, now make a 25-page deck out of it" workflows.
 *
 * Usage:
 *   node doc-to-spec.mjs --input report.md --output deck.json
 *   node doc-to-spec.mjs --input report.md --output deck.json \
 *        --theme deep-space --max-slides 25 --target-min 30
 *
 * For DOCX/PDF input, run pandoc first:
 *   pandoc report.docx -o report.md --wrap=none
 *   pandoc report.pdf  -o report.md --wrap=none   # needs pdftotext
 *
 * Spec schema: see templates/pptx-deck-spec.example.json
 */

import fs from 'node:fs';
import path from 'node:path';

const argv = process.argv.slice(2);
function arg(k, fb=null) {
  const i = argv.indexOf(`--${k}`);
  return (i>=0 && argv[i+1] && !argv[i+1].startsWith('--')) ? argv[i+1] : fb;
}
function flag(k) { return argv.includes(`--${k}`); }

const input    = arg('input');
const output   = arg('output', './deck.json');
const theme    = arg('theme', 'deep-space');
const maxSlides = parseInt(arg('max-slides', '25'), 10);
const targetMin = parseInt(arg('target-min', '30'), 10);
const format   = arg('format', 'ppt169');
const verbose  = flag('verbose');

if (!input) {
  console.error('Need --input <file.md>. For .docx/.pdf, first run pandoc to .md.');
  process.exit(1);
}

const ext = path.extname(input).toLowerCase();
if (ext !== '.md' && ext !== '.markdown') {
  console.error(`Only .md/.markdown supported natively. For ${ext}, run:`);
  console.error(`  pandoc ${input} -o intermediate.md --wrap=none`);
  console.error(`  node doc-to-spec.mjs --input intermediate.md --output ${output}`);
  process.exit(2);
}

const raw = fs.readFileSync(input, 'utf-8');

// ===== Parser: walk markdown by heading levels =====
// Outline rule:
//   # H1     → title slide (or cover if first)
//   ## H2    → section-divider + 1-3 content slides
//   ### H3   → sub-section within a section
//   bullets  → become title-bullets or two-column slides
//   table    → becomes kpi-grid
//   > quote  → becomes pullquote

function parseMarkdown(md) {
  const blocks = [];
  const lines = md.split(/\r?\n/);
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    // Heading
    const h = line.match(/^(#{1,6})\s+(.+?)\s*$/);
    if (h) {
      blocks.push({ type: 'heading', level: h[1].length, text: h[2].trim(), line: i });
      i++; continue;
    }
    // Block quote (multi-line until blank or non->)
    if (/^\s*>\s+/.test(line)) {
      const parts = [];
      while (i < lines.length && /^\s*>\s*/.test(lines[i])) {
        parts.push(lines[i].replace(/^\s*>\s?/, ''));
        i++;
      }
      blocks.push({ type: 'quote', text: parts.join(' ').trim() });
      continue;
    }
    // Bullet list
    if (/^\s*[-*+]\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*+]\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*+]\s+/, '').trim());
        i++;
      }
      blocks.push({ type: 'bullets', items });
      continue;
    }
    // Ordered list
    if (/^\s*\d+\.\s+/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*\d+\.\s+/.test(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+\.\s+/, '').trim());
        i++;
      }
      blocks.push({ type: 'bullets', items, ordered: true });
      continue;
    }
    // Table (simple GFM: | a | b |\n|---|---|\n| 1 | 2 |)
    if (/^\s*\|.+\|\s*$/.test(line) && i+1 < lines.length && /^\s*\|[\s\-:|]+\|\s*$/.test(lines[i+1])) {
      const head = parseTableRow(line);
      const rows = [];
      i += 2;
      while (i < lines.length && /^\s*\|.+\|\s*$/.test(lines[i])) {
        rows.push(parseTableRow(lines[i]));
        i++;
      }
      blocks.push({ type: 'table', head, rows });
      continue;
    }
    // Paragraph (everything until blank)
    if (line.trim()) {
      const parts = [];
      while (i < lines.length && lines[i].trim() && !/^#{1,6}\s+/.test(lines[i]) && !/^\s*[-*+\d]/.test(lines[i]) && !/^\s*>\s+/.test(lines[i]) && !/^\s*\|.+\|\s*$/.test(lines[i])) {
        parts.push(lines[i]);
        i++;
      }
      const text = parts.join(' ').replace(/\s+/g, ' ').trim();
      if (text) blocks.push({ type: 'paragraph', text });
      continue;
    }
    i++;
  }
  return blocks;
}

function parseTableRow(line) {
  return line.trim().replace(/^\||\|$/g, '').split('|').map(s => s.trim());
}

const blocks = parseMarkdown(raw);
if (verbose) console.error(`[doc-to-spec] parsed ${blocks.length} blocks`);

// ===== Group blocks into chapters =====
// Chapter = H1 (or H2 if no H1) + everything until next same-level heading
function groupChapters(blocks) {
  // Heading level histogram
  const counts = { 1: 0, 2: 0, 3: 0 };
  for (const b of blocks) if (b.type === 'heading' && b.level <= 3) counts[b.level]++;

  // Pick the chapter level: deepest heading level that has >=2 instances; fall back to whatever is present
  let chapterLevel;
  if (counts[2] >= 2) chapterLevel = 2;
  else if (counts[1] >= 2) chapterLevel = 1;
  else if (counts[3] >= 2) chapterLevel = 3;
  else chapterLevel = counts[2] >= 1 ? 2 : (counts[1] >= 1 ? 1 : 3);

  // Doc title = first heading strictly shallower than chapterLevel; else first chapter title; else fallback
  let docTitle = null;
  for (const b of blocks) {
    if (b.type === 'heading' && b.level < chapterLevel) { docTitle = b.text; break; }
  }

  const chapters = [];
  let cur = null;
  let docSubtitle = null;
  for (const b of blocks) {
    if (b.type === 'heading' && b.level < chapterLevel) {
      // Doc-level heading — skip into doc title (already captured); contents fold into next chapter
      continue;
    }
    if (b.type === 'heading' && b.level === chapterLevel) {
      if (cur) chapters.push(cur);
      cur = { title: b.text, blocks: [] };
      if (!docTitle) docTitle = b.text;
    } else if (cur) {
      cur.blocks.push(b);
    } else {
      // Material before first chapter heading — doc-level intro
      if (!docSubtitle && b.type === 'paragraph') docSubtitle = b.text;
    }
  }
  if (cur) chapters.push(cur);

  return { docTitle: docTitle || 'Untitled deck', docSubtitle: docSubtitle || '', chapters };
}

const { docTitle, docSubtitle, chapters } = groupChapters(blocks);

if (verbose) console.error(`[doc-to-spec] doc title: ${docTitle}; chapters: ${chapters.length}`);

// ===== Slide budget =====
// budget = maxSlides; reserve 3 (cover + agenda + closing). Distribute rest across chapters.
const fixed = 3; // cover + agenda + closing
const available = Math.max(chapters.length * 2, maxSlides - fixed);
const perChapterTarget = Math.floor(available / Math.max(1, chapters.length));

if (verbose) console.error(`[doc-to-spec] per-chapter budget: ${perChapterTarget}`);

// ===== Render chapter into slides =====
function renderChapter(ch, idx, budget) {
  const slides = [];
  const sectionNum = String(idx + 1).padStart(2, '0');

  // 1. Section divider
  slides.push({
    id: `section-${sectionNum}`,
    layout: 'section-divider',
    section: sectionNum,
    title: ch.title,
    subtitle: firstParagraphSnippet(ch.blocks),
    notes: '',
  });

  // 2. Content slides — group blocks intelligently
  let used = 1;
  let curBullets = [];
  let pendingPara = null;
  let pendingH3 = null;

  function flushBullets() {
    if (curBullets.length === 0) return;
    if (used >= budget) { curBullets = []; return; }
    slides.push({
      id: `${ch.title.toLowerCase().replace(/\W+/g,'-').slice(0,20)}-${used}`,
      layout: curBullets.length >= 4 ? 'title-bullets' : 'title-bullets',
      eyebrow: pendingH3 ? pendingH3.toUpperCase() : `${ch.title}`,
      title: pendingH3 || ch.title,
      lead: pendingPara || '',
      bullets: curBullets.map(b => typeof b === 'string' ? { text: b } : b),
      notes: pendingPara || '',
    });
    used++;
    curBullets = [];
    pendingPara = null;
    pendingH3 = null;
  }

  for (const b of ch.blocks) {
    if (used >= budget) break;

    if (b.type === 'heading' && b.level >= 3) {
      flushBullets();
      pendingH3 = b.text;
    } else if (b.type === 'paragraph') {
      if (curBullets.length > 0) {
        // Paragraph after bullets ends the slide
        flushBullets();
      }
      pendingPara = b.text;
    } else if (b.type === 'bullets') {
      curBullets.push(...b.items);
      if (curBullets.length >= 6) flushBullets();
    } else if (b.type === 'quote') {
      flushBullets();
      slides.push({
        id: `${ch.title.toLowerCase().replace(/\W+/g,'-').slice(0,20)}-quote-${used}`,
        layout: 'pullquote',
        quote: b.text,
        author: '',
        role: '',
      });
      used++;
    } else if (b.type === 'table') {
      flushBullets();
      slides.push(...tableToSlides(b, ch.title, used));
      used++;
    }
  }
  flushBullets();

  // If chapter is empty (just a heading), give it a single intro slide
  if (slides.length === 1) {
    slides.push({
      id: `${ch.title.toLowerCase().replace(/\W+/g,'-').slice(0,20)}-overview`,
      layout: 'title-bullets',
      eyebrow: `${ch.title}`,
      title: ch.title,
      lead: 'Overview of this section.',
      bullets: [{ text: 'Add content here' }],
    });
  }

  return slides;
}

function firstParagraphSnippet(blocks) {
  for (const b of blocks) {
    if (b.type === 'paragraph') return b.text.slice(0, 200);
  }
  return '';
}

function tableToSlides(table, chapterTitle, idx) {
  // If table looks like KPIs (2-3 columns, <= 6 rows) → kpi-grid
  if (table.head.length <= 3 && table.rows.length <= 6) {
    return [{
      id: `${chapterTitle.toLowerCase().replace(/\W+/g,'-').slice(0,15)}-kpis-${idx}`,
      layout: 'kpi-grid',
      eyebrow: 'METRICS',
      title: chapterTitle,
      kpis: table.rows.map(r => ({
        label: r[0] || '',
        value: r[1] || '',
        note: r[2] || '',
      })),
    }];
  }
  // Else flatten to two-column
  return [{
    id: `${chapterTitle.toLowerCase().replace(/\W+/g,'-').slice(0,15)}-table-${idx}`,
    layout: 'two-column',
    eyebrow: chapterTitle.toUpperCase(),
    title: 'Comparison',
    left:  { heading: table.head[0] || '', items: table.rows.map(r => r[0]) },
    right: { heading: table.head[1] || '', items: table.rows.map(r => r[1]) },
  }];
}

// ===== Build the spec =====
const slides = [];

// Cover
slides.push({
  id: 'cover',
  layout: 'title-cover',
  eyebrow: 'KEYNOTE · ' + new Date().getFullYear(),
  title: docTitle,
  subtitle: docSubtitle.slice(0, 200) || 'Generated from a source document.',
  author: '',
  date: new Date().toISOString().slice(0,10),
  notes: `Welcome. Today we'll cover ${chapters.length} sections in roughly ${targetMin} minutes.`,
});

// Agenda
slides.push({
  id: 'agenda',
  layout: 'agenda',
  eyebrow: 'AGENDA',
  title: `${chapters.length} items, ${targetMin} minutes`,
  items: chapters.map(c => c.title),
  notes: 'High-level shape of the talk.',
});

// Body
const totalBudget = maxSlides - fixed;
const budgetEach = Math.max(2, Math.floor(totalBudget / Math.max(1, chapters.length)));
chapters.forEach((c, i) => {
  slides.push(...renderChapter(c, i, budgetEach));
});

// Closing
slides.push({
  id: 'closing',
  layout: 'closing',
  title: 'Thank you',
  subtitle: 'Q & A',
  contacts: [],
  notes: 'Open the floor.',
});

// Truncate if over budget (preserve cover + agenda + last closing)
if (slides.length > maxSlides) {
  const head = slides.slice(0, 2);
  const tail = slides.slice(-1);
  const body = slides.slice(2, -1);
  const keep = body.slice(0, maxSlides - 3);
  slides.length = 0;
  slides.push(...head, ...keep, ...tail);
}

const spec = {
  name: docTitle.toLowerCase().replace(/[^\w]+/g, '_').slice(0, 40) || 'imported_deck',
  theme,
  format,
  slides,
};

// ===== Write =====
fs.writeFileSync(output, JSON.stringify(spec, null, 2), 'utf-8');
console.log('[doc-to-spec] wrote:', output);
console.log('[doc-to-spec] chapters:', chapters.length, '| slides:', slides.length);
console.log('[doc-to-spec] next:');
console.log(`  ~/.claude/skills/viz-deck/scripts/export-editable-pptx.sh ${output} --theme ${theme}`);
