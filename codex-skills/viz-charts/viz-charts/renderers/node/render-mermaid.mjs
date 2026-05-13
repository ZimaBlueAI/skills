#!/usr/bin/env node
/**
 * render-mermaid.mjs
 * 离线渲染 Mermaid 源文件为 SVG
 *
 * 用法：
 *   node render-mermaid.mjs --input arch.mmd --output arch.svg --theme terminal
 *
 * 选项：
 *   --input  / -i   .mmd 源文件
 *   --output / -o   输出 .svg
 *   --theme  / -t   terminal | deck（默认 deck）
 *   --bg            背景色（默认透明，可设 transparent / 或 css color）
 *   --width         画布宽度（默认 1000）
 *
 * 依赖：mermaid-isomorphic（轻量 SSR）
 *       如果 mermaid-isomorphic 失败，自动回退到 mmdc（@mermaid-js/mermaid-cli）
 */

import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));

// ---- CLI 参数解析 ----
function parseArgs(argv) {
  const args = { theme: 'deck', width: 1000, bg: 'transparent' };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i];
    const v = argv[i + 1];
    if (k === '--input'  || k === '-i') { args.input  = v; i++; }
    else if (k === '--output' || k === '-o') { args.output = v; i++; }
    else if (k === '--theme'  || k === '-t') { args.theme  = v; i++; }
    else if (k === '--width')               { args.width  = parseInt(v); i++; }
    else if (k === '--bg')                  { args.bg     = v; i++; }
    else if (k === '--help' || k === '-h')  { args.help   = true; }
  }
  return args;
}

const args = parseArgs(process.argv);

if (args.help || !args.input || !args.output) {
  console.log(`
render-mermaid · 离线渲染 Mermaid → SVG

用法：
  node render-mermaid.mjs --input <file.mmd> --output <file.svg> [--theme terminal|deck]

选项：
  --input  / -i   .mmd 源文件 (必填)
  --output / -o   输出 .svg   (必填)
  --theme  / -t   terminal | deck（默认 deck）
  --bg            背景色（默认 transparent）
  --width         画布宽度（默认 1000）
`);
  process.exit(args.help ? 0 : 1);
}

// ---- 主题变量 ----
const themeVars = {
  terminal: {
    theme: 'base',
    themeVariables: {
      darkMode: true,
      background: '#0a0a0a',
      primaryColor: '#141414',
      primaryTextColor: '#e8e8e8',
      primaryBorderColor: '#3a3a3a',
      secondaryColor: '#1c1c1c',
      lineColor: '#888',
      textColor: '#e8e8e8',
      mainBkg: '#141414',
      nodeBorder: '#3a3a3a',
      clusterBkg: '#0a0a0a',
      clusterBorder: '#2a2a2a',
      edgeLabelBackground: '#0a0a0a',
      fontFamily: 'JetBrains Mono, monospace',
      fontSize: '12px',
      taskBkgColor: '#d4ff00',
      taskTextColor: '#0a0a0a',
      activeTaskBkgColor: '#d4ff00',
      doneTaskBkgColor: '#44dd88',
      critBkgColor: '#ff4444',
      todayLineColor: '#d4ff00',
    },
  },
  deck: {
    theme: 'base',
    themeVariables: {
      darkMode: true,
      background: '#030711',
      primaryColor: '#07111f',
      primaryTextColor: '#edf7ff',
      primaryBorderColor: 'rgba(151, 209, 255, 0.34)',
      secondaryColor: '#0c1a2e',
      lineColor: '#a8bdd5',
      textColor: '#edf7ff',
      mainBkg: 'rgba(12, 26, 46, 0.92)',
      nodeBorder: 'rgba(151, 209, 255, 0.34)',
      clusterBkg: 'rgba(7, 17, 31, 0.6)',
      clusterBorder: 'rgba(151, 209, 255, 0.16)',
      edgeLabelBackground: '#030711',
      fontFamily: 'Inter, sans-serif',
      fontSize: '13px',
      taskBkgColor: '#42e8ff',
      taskTextColor: '#030711',
      activeTaskBkgColor: '#42e8ff',
      doneTaskBkgColor: '#78f7c5',
      critBkgColor: '#ff8c8c',
      todayLineColor: '#ffd987',
    },
  },
};

const cfg = themeVars[args.theme];
if (!cfg) {
  console.error(`Unknown theme: ${args.theme}. Use 'terminal' or 'deck'.`);
  process.exit(1);
}

// ---- 渲染主流程 ----
async function renderWithIsomorphic(source, mermaidConfig) {
  const { createMermaidRenderer } = await import('mermaid-isomorphic');
  const renderer = createMermaidRenderer({
    browser: undefined, // 让它自己选
  });
  const results = await renderer([source], { mermaidConfig });
  const r = results[0];
  if (r.status === 'rejected') throw r.reason;
  return r.value.svg;
}

async function renderWithMmdc(source, mermaidConfig) {
  // mmdc CLI fallback：写临时文件后调用
  const { execSync } = await import('node:child_process');
  const { writeFileSync, readFileSync, mkdtempSync, unlinkSync } = await import('node:fs');
  const { tmpdir } = await import('node:os');
  const { join } = await import('node:path');

  const tmpDir = mkdtempSync(join(tmpdir(), 'mmd-'));
  const tmpIn  = join(tmpDir, 'in.mmd');
  const tmpOut = join(tmpDir, 'out.svg');
  const tmpCfg = join(tmpDir, 'cfg.json');

  writeFileSync(tmpIn, source);
  writeFileSync(tmpCfg, JSON.stringify(mermaidConfig));

  try {
    const cmd = [
      'npx', '-y', '@mermaid-js/mermaid-cli', 'mmdc',
      '-i', tmpIn, '-o', tmpOut, '-c', tmpCfg,
      '-b', args.bg,
      '-w', String(args.width),
    ];
    execSync(cmd.map(a => `"${a}"`).join(' '), { stdio: 'pipe' });
    return readFileSync(tmpOut, 'utf-8');
  } finally {
    try { unlinkSync(tmpIn); unlinkSync(tmpOut); unlinkSync(tmpCfg); } catch {}
  }
}

/**
 * Placeholder fallback: 当浏览器不可用时，输出"占位 SVG + 嵌入 mermaid 源码"
 * 用户需在浏览器内查看时由 cdn-loader 渲染（即转回 inline 模式）
 */
function renderPlaceholder(source, themeName) {
  const isDeck = themeName === 'deck';
  const bg = isDeck ? '#030711' : '#0a0a0a';
  const fg = isDeck ? '#edf7ff' : '#e8e8e8';
  const accent = isDeck ? '#42e8ff' : '#d4ff00';
  const safe = source.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
  return `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${args.width} 320" width="${args.width}" height="320">
  <rect width="100%" height="100%" fill="${bg}"/>
  <text x="20" y="40" fill="${accent}" font-family="monospace" font-size="14" font-weight="700">⚠ Mermaid render unavailable in this environment</text>
  <text x="20" y="65" fill="${fg}" font-family="monospace" font-size="11" opacity="0.7">浏览器不可用 — 请使用 inline 模式（cdn-loader.js）渲染，或本地运行：</text>
  <text x="20" y="85" fill="${fg}" font-family="monospace" font-size="11" opacity="0.7">  npx playwright install chromium</text>
  <foreignObject x="20" y="100" width="${args.width - 40}" height="200">
    <pre xmlns="http://www.w3.org/1999/xhtml" style="color:${fg};font-family:monospace;font-size:11px;white-space:pre-wrap;opacity:0.8;margin:0">${safe}</pre>
  </foreignObject>
</svg>`;
}

async function main() {
  const inputPath = resolve(args.input);
  const outputPath = resolve(args.output);
  const source = await readFile(inputPath, 'utf-8');

  let svg;
  let strategy;

  // 策略 1: mermaid-isomorphic（首选，需 playwright + chromium）
  try {
    svg = await renderWithIsomorphic(source, cfg);
    strategy = 'mermaid-isomorphic';
  } catch (e1) {
    console.warn(`[render-mermaid] mermaid-isomorphic failed: ${e1.message.split('\n')[0]}`);
    console.warn(`[render-mermaid] falling back to mmdc...`);
    // 策略 2: mmdc（也需要 puppeteer 浏览器）
    try {
      svg = await renderWithMmdc(source, cfg);
      strategy = 'mmdc';
    } catch (e2) {
      console.warn(`[render-mermaid] mmdc failed: ${e2.message.split('\n')[0]}`);
      console.warn(`[render-mermaid] using placeholder SVG (browser unavailable)`);
      console.warn(`[render-mermaid] To enable real rendering, run once: npx playwright install chromium`);
      // 策略 3: placeholder svg（无浏览器环境兜底，便于占位）
      svg = renderPlaceholder(source, args.theme);
      strategy = 'placeholder';
    }
  }

  await writeFile(outputPath, svg, 'utf-8');
  console.log(`✓ rendered ${args.input} → ${args.output} (${(svg.length / 1024).toFixed(1)}KB) via ${strategy} · theme=${args.theme}`);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
