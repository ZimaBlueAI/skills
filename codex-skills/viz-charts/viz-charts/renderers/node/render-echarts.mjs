#!/usr/bin/env node
/**
 * render-echarts.mjs
 * 离线渲染 ECharts JSON 配置为独立 SVG
 *
 * 用法：
 *   node render-echarts.mjs --input trend.json --output trend.svg --theme terminal
 *
 * 选项：
 *   --input  / -i   ECharts option JSON 文件
 *   --output / -o   输出 .svg
 *   --theme  / -t   terminal | deck
 *   --width         默认 800
 *   --height        默认 400
 *
 * 实现：
 *   ECharts 5+ 内置 server-side SVG renderer，无需 puppeteer。
 *   关键 API: echarts.init(canvas, theme, { renderer: 'svg', ssr: true, width, height })
 */

import { readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';

function parseArgs(argv) {
  const args = { theme: 'deck', width: 800, height: 400 };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i], v = argv[i + 1];
    if (k === '--input'  || k === '-i') { args.input  = v; i++; }
    else if (k === '--output' || k === '-o') { args.output = v; i++; }
    else if (k === '--theme'  || k === '-t') { args.theme  = v; i++; }
    else if (k === '--width')               { args.width  = parseInt(v); i++; }
    else if (k === '--height')              { args.height = parseInt(v); i++; }
    else if (k === '--help' || k === '-h')  { args.help   = true; }
  }
  return args;
}

const args = parseArgs(process.argv);

if (args.help || !args.input || !args.output) {
  console.log(`
render-echarts · 离线渲染 ECharts → SVG (SSR, 不需要浏览器)

用法：
  node render-echarts.mjs --input <file.json> --output <file.svg> [--theme terminal|deck]

选项：
  --input  / -i   ECharts option JSON (必填)
  --output / -o   输出 .svg (必填)
  --theme  / -t   terminal | deck（默认 deck）
  --width         默认 800
  --height        默认 400
`);
  process.exit(args.help ? 0 : 1);
}

// ---- 主题（与 themes/*.js 同步）----
const themes = {
  terminal: {
    color: ['#d4ff00', '#e8e8e8', '#888888', '#44dd88', '#ffaa00', '#44aaff', '#ff4444', '#b893ff'],
    backgroundColor: 'transparent',
    textStyle: { color: '#e8e8e8', fontFamily: 'JetBrains Mono, monospace' },
    title: { textStyle: { color: '#e8e8e8', fontFamily: 'JetBrains Mono, monospace', fontSize: 12, fontWeight: 700 }, subtextStyle: { color: '#888' } },
    line:  { itemStyle: { borderWidth: 1 }, lineStyle: { width: 2 }, symbolSize: 4, symbol: 'circle', smooth: false },
    bar:   { itemStyle: { barBorderWidth: 0 } },
    pie:   { itemStyle: { borderWidth: 1, borderColor: '#0a0a0a' } },
    categoryAxis: { axisLine: { lineStyle: { color: '#3a3a3a' } }, axisTick: { lineStyle: { color: '#3a3a3a' } }, axisLabel: { color: '#888', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }, splitLine: { show: false } },
    valueAxis:    { axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#888', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }, splitLine: { lineStyle: { color: '#2a2a2a', type: 'dashed' } } },
    legend:       { textStyle: { color: '#e8e8e8', fontFamily: 'JetBrains Mono, monospace', fontSize: 11 }, icon: 'rect', itemWidth: 10, itemHeight: 10 },
  },
  deck: {
    color: ['#42e8ff', '#6ca5ff', '#ffd987', '#78f7c5', '#b893ff', '#ff8c8c', '#d8e8f4'],
    backgroundColor: 'transparent',
    textStyle: { color: '#edf7ff', fontFamily: 'Inter, system-ui, sans-serif' },
    title: { textStyle: { color: '#edf7ff', fontSize: 16, fontWeight: 700 }, subtextStyle: { color: '#a8bdd5' } },
    line:  { itemStyle: { borderWidth: 2 }, lineStyle: { width: 2.5 }, symbolSize: 6, symbol: 'circle', smooth: true },
    bar:   { itemStyle: { barBorderWidth: 0, borderRadius: [3, 3, 0, 0] } },
    pie:   { itemStyle: { borderWidth: 2, borderColor: '#030711' } },
    categoryAxis: { axisLine: { lineStyle: { color: 'rgba(151, 209, 255, 0.34)' } }, axisLabel: { color: '#a8bdd5', fontSize: 11 }, splitLine: { show: false } },
    valueAxis:    { axisLine: { show: false }, axisLabel: { color: '#a8bdd5', fontSize: 11 }, splitLine: { lineStyle: { color: 'rgba(151, 209, 255, 0.16)', type: 'dashed' } } },
    legend:       { textStyle: { color: '#edf7ff', fontSize: 12 }, icon: 'roundRect', itemWidth: 12, itemHeight: 8 },
  },
};

async function main() {
  const inputPath = resolve(args.input);
  const outputPath = resolve(args.output);

  let optionRaw = await readFile(inputPath, 'utf-8');
  let option;
  try {
    option = JSON.parse(optionRaw);
  } catch (e) {
    console.error(`[render-echarts] Invalid JSON in ${args.input}: ${e.message}`);
    process.exit(1);
  }

  // 移除 _meta 字段（如果存在）
  delete option._meta;

  const theme = themes[args.theme];
  if (!theme) {
    console.error(`Unknown theme: ${args.theme}. Use 'terminal' or 'deck'.`);
    process.exit(1);
  }

  let echarts;
  try {
    echarts = await import('echarts');
  } catch (e) {
    console.error(`[render-echarts] echarts not installed. Run: npm install echarts`);
    process.exit(1);
  }

  // ECharts SSR 模式
  echarts.registerTheme(args.theme, theme);
  const chart = echarts.init(null, args.theme, {
    renderer: 'svg',
    ssr: true,
    width: args.width,
    height: args.height,
  });

  chart.setOption(option);

  const svg = chart.renderToSVGString();
  chart.dispose();

  await writeFile(outputPath, svg, 'utf-8');
  console.log(`✓ rendered ${args.input} → ${args.output} (${(svg.length / 1024).toFixed(1)}KB) · theme=${args.theme} · ${args.width}×${args.height}`);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
