#!/usr/bin/env node
/**
 * viz-deck · Show-Don't-Tell shotgun preview generator
 *
 * Generates a side-by-side comparison board (3 hero variants from 3
 * contrasting design philosophies) so the user can pick the visual
 * direction by sight rather than by description.
 *
 * Usage:
 *   node preview-shotgun.mjs \
 *     --topic "AI Agent landscape report" \
 *     --scene "investor-pitch" \
 *     --output ./previews/
 *
 *   # Or pass an explicit triple (slugs from design-philosophies.md):
 *   node preview-shotgun.mjs \
 *     --topic "..." --triple "pentagram,build,takram" \
 *     --output ./previews/
 *
 * Output: <output>/preview-board.html (single file, no deps).
 */

import fs from 'node:fs';
import path from 'node:path';

// ===== Scene → contrast triple presets =====
// Each preset MUST cross design schools (no all-information-architecture trios).
const SCENE_PRESETS = {
  'investor-pitch':    ['pentagram',   'build',      'takram'],
  'investor':          ['pentagram',   'build',      'takram'],
  'product-launch':    ['fathom',      'sagmeister', 'kenya-hara'],
  'product':           ['fathom',      'sagmeister', 'kenya-hara'],
  'tech-deepdive':     ['mueller',     'fieldio',    'territory'],
  'tech':              ['mueller',     'fieldio',    'territory'],
  'academic':          ['pentagram',   'ia',         'kenya-hara'],
  'gov':               ['pentagram',   'ia',         'kenya-hara'],
  'default':           ['vizdeck-base','kenya-hara', 'fieldio'],
};

// ===== Philosophy registry (CSS palette + type + accent + tagline) =====
const REGISTRY = {
  'vizdeck-base': {
    label: 'viz-deck baseline',
    school: 'Active Theory · simplified',
    one_line: 'Deep-space cyan/gold — calm authority for stage reports.',
    bg: '#030711', fg: '#e7efff', muted: '#8898b6',
    accent: '#42e8ff', accent2: '#ffd987',
    serif: 'Newsreader, Times New Roman, serif',
    sans:  "Inter, system-ui, sans-serif",
    eyebrow_letter: '0.22em',
    h1_size: '88px', h1_weight: '500',
    hero_bg: 'radial-gradient(circle at 70% 30%, rgba(66,232,255,0.18), transparent 50%), radial-gradient(circle at 25% 75%, rgba(255,217,135,0.12), transparent 55%)',
  },
  'pentagram': {
    label: 'Pentagram',
    school: 'Information Architecture',
    one_line: 'Disciplined typography, dense information hierarchy, near-zero ornament.',
    bg: '#ffffff', fg: '#0a0a0a', muted: '#555',
    accent: '#d60000', accent2: '#0a0a0a',
    serif: 'Newsreader, Georgia, serif',
    sans:  "Inter, Helvetica Neue, sans-serif",
    eyebrow_letter: '0.32em',
    h1_size: '96px', h1_weight: '600',
    hero_bg: 'linear-gradient(180deg, #fff 0%, #fafafa 100%)',
  },
  'build': {
    label: 'Build',
    school: 'Swiss Minimalism (Modern)',
    one_line: 'Premium silence — generous whitespace, mono labels, dignified type.',
    bg: '#0e0e0e', fg: '#f5f0e6', muted: '#a89a85',
    accent: '#d5b572', accent2: '#f5f0e6',
    serif: 'Newsreader, serif',
    sans:  "Inter, sans-serif",
    eyebrow_letter: '0.28em',
    h1_size: '92px', h1_weight: '300',
    hero_bg: 'linear-gradient(135deg, #0e0e0e 0%, #1a1612 100%)',
  },
  'takram': {
    label: 'Takram',
    school: 'East-Asian Experimental',
    one_line: 'Research-grade minimalism with hidden structure — concept-design DNA.',
    bg: '#f7f5f1', fg: '#171312', muted: '#5a544f',
    accent: '#9c1e1e', accent2: '#171312',
    serif: 'Newsreader, "Noto Serif JP", serif',
    sans:  "Inter, sans-serif",
    eyebrow_letter: '0.30em',
    h1_size: '84px', h1_weight: '400',
    hero_bg: 'radial-gradient(circle at 80% 80%, rgba(156,30,30,0.08), transparent 50%)',
  },
  'fathom': {
    label: 'Fathom',
    school: 'Information Architecture · Data',
    one_line: 'Data-dense storytelling, every page earns its ink.',
    bg: '#0c1421', fg: '#e8eef7', muted: '#7c8aa3',
    accent: '#fad000', accent2: '#5ccfff',
    serif: 'Newsreader, serif',
    sans:  "Inter, sans-serif",
    eyebrow_letter: '0.22em',
    h1_size: '80px', h1_weight: '500',
    hero_bg: 'linear-gradient(180deg, #0c1421 0%, #131e30 100%)',
  },
  'sagmeister': {
    label: 'Sagmeister & Walsh',
    school: 'Experimental Avant-Garde',
    one_line: 'Bold, playful, hand-touched — for creative-industry keynotes.',
    bg: '#ff3e6c', fg: '#fff8e7', muted: '#ffd5d5',
    accent: '#fff43a', accent2: '#1a1a1a',
    serif: 'Newsreader, "Playfair Display", serif',
    sans:  "Inter, sans-serif",
    eyebrow_letter: '0.20em',
    h1_size: '108px', h1_weight: '700',
    hero_bg: 'radial-gradient(circle at 30% 30%, #ff3e6c 0%, #c91a48 100%)',
  },
  'kenya-hara': {
    label: 'Kenya Hara',
    school: 'East-Asian Minimalism',
    one_line: 'Whiteness as content — restraint, ma (negative space), serenity.',
    bg: '#fbfaf6', fg: '#1d1c19', muted: '#7e7a71',
    accent: '#bf2d2d', accent2: '#1d1c19',
    serif: 'Newsreader, "Noto Serif JP", serif',
    sans:  '"Hiragino Sans", "Noto Sans JP", Inter, sans-serif',
    eyebrow_letter: '0.40em',
    h1_size: '72px', h1_weight: '300',
    hero_bg: 'linear-gradient(180deg, #fbfaf6 0%, #f5f3ee 100%)',
  },
  'mueller': {
    label: 'Müller-Brockmann',
    school: 'Swiss Grid',
    one_line: 'Pure grid discipline — Akzidenz Grotesk, mathematical layout.',
    bg: '#e8e6df', fg: '#0c0c0c', muted: '#4a4a4a',
    accent: '#d60000', accent2: '#0c0c0c',
    serif: 'serif',
    sans:  "Inter, Helvetica, sans-serif",
    eyebrow_letter: '0.30em',
    h1_size: '96px', h1_weight: '700',
    hero_bg: 'linear-gradient(135deg, #e8e6df 0%, #f0eee7 100%)',
  },
  'fieldio': {
    label: 'Field.io',
    school: 'Motion Poetics',
    one_line: 'Algorithmic motion as content — generative aesthetic at rest.',
    bg: '#000814', fg: '#cae9ff', muted: '#5a7ba1',
    accent: '#00f5d4', accent2: '#fb6f92',
    serif: 'Newsreader, serif',
    sans:  '"Inter", sans-serif',
    eyebrow_letter: '0.18em',
    h1_size: '92px', h1_weight: '300',
    hero_bg: 'conic-gradient(from 220deg at 70% 30%, #00f5d4 0%, transparent 35%, #fb6f92 65%, transparent 100%)',
  },
  'territory': {
    label: 'Territory Studio',
    school: 'Experimental · FUI',
    one_line: 'Film-grade fictional UI — HUDs, scan-lines, scientific posture.',
    bg: '#080a0c', fg: '#c0ffea', muted: '#3a6b5e',
    accent: '#ff6b00', accent2: '#00d4ff',
    serif: 'monospace',
    sans:  '"JetBrains Mono", ui-monospace, monospace',
    eyebrow_letter: '0.40em',
    h1_size: '76px', h1_weight: '400',
    hero_bg: 'linear-gradient(180deg, #080a0c 0%, #0f1719 100%)',
  },
  'ia': {
    label: 'Information Architects',
    school: 'Information Architecture',
    one_line: 'Reading-first design — content as the only ornament.',
    bg: '#f7f4ed', fg: '#0a0a0a', muted: '#666',
    accent: '#0066cc', accent2: '#0a0a0a',
    serif: '"Newsreader", "IA Writer Duospace", Georgia, serif',
    sans:  '"Inter", sans-serif',
    eyebrow_letter: '0.28em',
    h1_size: '80px', h1_weight: '500',
    hero_bg: 'linear-gradient(180deg, #f7f4ed 0%, #f0ece2 100%)',
  },
};

// ===== Arg parsing =====
const argv = process.argv.slice(2);
function arg(k, fallback = null) {
  const i = argv.indexOf(`--${k}`);
  return (i >= 0 && argv[i+1] && !argv[i+1].startsWith('--')) ? argv[i+1] : fallback;
}

const topic = arg('topic', 'Untitled deck');
const scene = arg('scene', 'default');
const tripleArg = arg('triple', null);
const outDir = arg('output', './previews');

const triple = tripleArg
  ? tripleArg.split(',').map(s => s.trim())
  : (SCENE_PRESETS[scene] || SCENE_PRESETS.default);

if (triple.length !== 3) {
  console.error('Need exactly 3 philosophies. Got:', triple);
  process.exit(1);
}

const variants = triple.map(slug => {
  const p = REGISTRY[slug];
  if (!p) { console.error(`Unknown philosophy slug: ${slug}`); process.exit(1); }
  return { slug, ...p };
});

// ===== Render variant card =====
function renderVariantCard(v, idx) {
  return `
  <article class="variant" data-slug="${v.slug}" style="
    --bg:${v.bg}; --fg:${v.fg}; --muted:${v.muted};
    --accent:${v.accent}; --accent2:${v.accent2};
    --serif:${v.serif}; --sans:${v.sans};
  ">
    <header class="variant-meta">
      <div class="variant-num">0${idx+1}</div>
      <div class="variant-info">
        <div class="variant-school">${escapeHtml(v.school)}</div>
        <div class="variant-name">${escapeHtml(v.label)}</div>
      </div>
    </header>

    <!-- Mini hero — cover-page mockup of the chosen philosophy -->
    <div class="hero" style="background: ${v.hero_bg}; background-color: ${v.bg};">
      <div class="hero-inner">
        <div class="hero-eyebrow" style="font-family: ${v.sans}; letter-spacing: ${v.eyebrow_letter};">
          KEYNOTE · 2026
        </div>
        <h1 class="hero-title" style="
          font-family: ${v.serif};
          font-size: ${v.h1_size};
          font-weight: ${v.h1_weight};
          color: ${v.fg};
        ">${escapeHtml(topic)}</h1>
        <p class="hero-lead" style="color: ${v.muted}; font-family: ${v.sans};">
          One paragraph captures the case. Stage-grade typography only.
        </p>
        <div class="hero-meta" style="font-family: ${v.sans}; color: ${v.muted};">
          <span style="color:${v.accent}">●</span> 30 min
          &nbsp;·&nbsp; ${v.label}
        </div>
      </div>
    </div>

    <!-- Mini chapter inside-page mockup -->
    <div class="inside" style="background: ${v.bg}; color: ${v.fg};">
      <div class="inside-eyebrow" style="color:${v.accent}; font-family:${v.sans}; letter-spacing:${v.eyebrow_letter};">
        CHAPTER 01 · MARKET
      </div>
      <div class="inside-h" style="font-family:${v.serif}; color:${v.fg};">
        12% of Chinese SMBs adopt domestic LLM tooling.
      </div>
      <div class="inside-bar">
        <div class="inside-bar-fill" style="background:${v.accent}; width:62%"></div>
      </div>
      <div class="inside-row" style="color:${v.muted}; font-family:${v.sans};">
        <span style="color:${v.fg}; font-weight:600">62%</span> growth YoY
        &nbsp;·&nbsp; IDC 2026Q1
      </div>
    </div>

    <footer class="variant-tagline" style="color:${v.muted}; font-family:${v.sans};">
      ${escapeHtml(v.one_line)}
    </footer>

    <button class="pick-btn" data-slug="${v.slug}" data-label="${escapeAttr(v.label)}">
      PICK · ${escapeHtml(v.label.toUpperCase())}
    </button>
  </article>
  `;
}

function escapeHtml(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function escapeAttr(s) { return escapeHtml(s); }

// ===== Render full board =====
const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1920,initial-scale=1">
<title>viz-deck · Direction Preview — ${escapeHtml(topic)}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Newsreader:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --board-bg: #f4f4f0;
    --board-fg: #0a0a0a;
    --board-muted: #555;
    --rail: #d5d5d0;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--board-bg); color: var(--board-fg); font-family: "Inter", system-ui, sans-serif; }
  .topbar {
    padding: 28px 48px;
    border-bottom: 1px solid var(--rail);
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    background: var(--board-bg);
  }
  .topbar h1 {
    font-family: "Newsreader", serif;
    font-weight: 500;
    font-size: 28px;
    margin: 0;
  }
  .topbar .topic {
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    color: var(--board-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
  }
  .topbar .topic strong { color: var(--board-fg); }

  .board {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 24px;
    padding: 32px 48px 64px;
    max-width: 1920px;
    margin: 0 auto;
  }
  .variant {
    background: white;
    border: 1px solid var(--rail);
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transition: transform 0.2s, box-shadow 0.2s;
  }
  .variant:hover { transform: translateY(-4px); box-shadow: 0 16px 48px rgba(0,0,0,0.10); }
  .variant-meta {
    padding: 16px 20px;
    display: flex;
    gap: 14px;
    align-items: center;
    border-bottom: 1px solid var(--rail);
  }
  .variant-num {
    font-family: "JetBrains Mono", monospace;
    font-size: 36px;
    font-weight: 500;
    color: var(--board-fg);
    line-height: 1;
  }
  .variant-school {
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: var(--board-muted);
  }
  .variant-name {
    font-family: "Newsreader", serif;
    font-size: 22px;
    font-weight: 500;
    margin-top: 2px;
  }

  .hero, .inside {
    width: 100%;
    aspect-ratio: 16 / 9;
    padding: 24px 28px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    overflow: hidden;
    position: relative;
  }
  .hero-inner { transform: scale(0.62); transform-origin: 0 50%; width: 161%; }
  .hero-eyebrow { font-size: 18px; text-transform: uppercase; opacity: 0.9; margin-bottom: 20px; }
  .hero-title { line-height: 1.05; letter-spacing: -0.02em; margin: 0 0 18px; max-width: 90%; }
  .hero-lead { font-size: 22px; line-height: 1.4; margin: 0 0 22px; max-width: 80%; }
  .hero-meta { font-size: 13px; letter-spacing: 0.14em; text-transform: uppercase; }

  .inside { border-top: 1px solid var(--rail); }
  .inside-eyebrow { font-size: 11px; text-transform: uppercase; margin-bottom: 14px; }
  .inside-h { font-size: 28px; line-height: 1.2; margin-bottom: 22px; max-width: 92%; }
  .inside-bar { width: 100%; height: 6px; background: rgba(127,127,127,0.18); border-radius: 3px; overflow: hidden; margin-bottom: 12px; }
  .inside-bar-fill { height: 100%; }
  .inside-row { font-size: 14px; }

  .variant-tagline {
    padding: 16px 20px;
    font-size: 13px;
    line-height: 1.5;
    border-top: 1px solid var(--rail);
  }
  .pick-btn {
    background: var(--board-fg);
    color: var(--board-bg);
    border: 0;
    padding: 16px;
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    letter-spacing: 0.22em;
    cursor: pointer;
    transition: background 0.15s, color 0.15s;
  }
  .pick-btn:hover { background: #d60000; color: white; }
  .pick-btn.picked { background: #009966; color: white; }

  .picked-banner {
    position: fixed;
    bottom: 24px; left: 50%;
    transform: translateX(-50%);
    background: var(--board-fg);
    color: var(--board-bg);
    padding: 16px 28px;
    border-radius: 4px;
    font-family: "JetBrains Mono", monospace;
    font-size: 13px;
    letter-spacing: 0.15em;
    z-index: 100;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.2s;
  }
  .picked-banner.show { opacity: 1; }
  .picked-banner kbd {
    background: rgba(255,255,255,0.15);
    border-radius: 3px;
    padding: 2px 6px;
    margin: 0 4px;
  }

  .footnote {
    padding: 20px 48px 48px;
    color: var(--board-muted);
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    max-width: 1100px;
  }
</style>
</head>
<body>
  <div class="topbar">
    <h1>Direction Preview</h1>
    <div class="topic">TOPIC <strong>${escapeHtml(topic)}</strong> &nbsp;·&nbsp; SCENE <strong>${escapeHtml(scene)}</strong></div>
  </div>

  <div class="board">
    ${variants.map(renderVariantCard).join('')}
  </div>

  <p class="footnote">
    Each variant shows a cover + chapter inside-page mockup, rendered with the chosen philosophy's
    palette, typography, and rhythm. Click a "PICK" button to commit — the chosen slug is logged
    to the console (and stored to <code>window.__viz_deck_picked</code> for the orchestrator to read).
    To see the full design philosophy DNA, refer to <code>references/design-philosophies.md</code>.
  </p>

  <div class="picked-banner" id="banner">
    PICKED <strong id="banner-name"></strong> &nbsp;·&nbsp; SLUG <kbd id="banner-slug"></kbd>
  </div>

<script>
  document.querySelectorAll('.pick-btn').forEach(b => {
    b.onclick = () => {
      document.querySelectorAll('.pick-btn').forEach(x => x.classList.remove('picked'));
      b.classList.add('picked');
      const slug = b.dataset.slug, label = b.dataset.label;
      window.__viz_deck_picked = { slug, label, at: new Date().toISOString() };
      console.log('[viz-deck preview] picked:', window.__viz_deck_picked);
      const banner = document.getElementById('banner');
      document.getElementById('banner-name').textContent = label;
      document.getElementById('banner-slug').textContent = slug;
      banner.classList.add('show');
      // Try to write to clipboard so the orchestrator can paste back the slug
      if (navigator.clipboard) navigator.clipboard.writeText(slug).catch(()=>{});
    };
  });
</script>
</body>
</html>`;

fs.mkdirSync(outDir, { recursive: true });
const outPath = path.join(outDir, 'preview-board.html');
fs.writeFileSync(outPath, html, 'utf-8');

console.log('[preview-shotgun] wrote:', outPath);
console.log('[preview-shotgun] topic:', topic);
console.log('[preview-shotgun] scene:', scene);
console.log('[preview-shotgun] triple:', triple.join(' / '));
