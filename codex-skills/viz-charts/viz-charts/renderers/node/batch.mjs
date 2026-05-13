#!/usr/bin/env node
/**
 * batch.mjs
 * 批量离线渲染整个目录的 mmd / json 文件
 *
 * 用法：
 *   node batch.mjs --input-dir ./charts --output-dir ./svgs --theme terminal
 *
 * 自动按扩展名分发：
 *   .mmd  → render-mermaid.mjs
 *   .json → render-echarts.mjs
 */

import { readdir, mkdir } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { resolve, basename, extname, join } from 'node:path';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';

const __dirname = dirname(fileURLToPath(import.meta.url));

function parseArgs(argv) {
  const args = { theme: 'deck', concurrency: 4 };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i], v = argv[i + 1];
    if (k === '--input-dir')  { args.inputDir  = v; i++; }
    else if (k === '--output-dir') { args.outputDir = v; i++; }
    else if (k === '--theme'  || k === '-t') { args.theme  = v; i++; }
    else if (k === '--concurrency')          { args.concurrency = parseInt(v); i++; }
    else if (k === '--width')                { args.width = parseInt(v); i++; }
    else if (k === '--height')               { args.height = parseInt(v); i++; }
    else if (k === '--help' || k === '-h')   { args.help = true; }
  }
  return args;
}

const args = parseArgs(process.argv);

if (args.help || !args.inputDir || !args.outputDir) {
  console.log(`
batch · 批量离线渲染 mmd/json → svg

用法：
  node batch.mjs --input-dir <dir> --output-dir <dir> [--theme terminal|deck]

选项：
  --input-dir   源目录（含 .mmd 和/或 .json）
  --output-dir  输出目录（不存在会自动创建）
  --theme  / -t 默认 deck
  --width       (echarts only) 默认 800
  --height      (echarts only) 默认 400
  --concurrency 并发数，默认 4
`);
  process.exit(args.help ? 0 : 1);
}

function runChild(script, cliArgs) {
  return new Promise((resolveP, rejectP) => {
    const child = spawn('node', [join(__dirname, script), ...cliArgs], { stdio: 'inherit' });
    child.on('exit', code => code === 0 ? resolveP() : rejectP(new Error(`${script} exited ${code}`)));
    child.on('error', rejectP);
  });
}

async function main() {
  const inputDir = resolve(args.inputDir);
  const outputDir = resolve(args.outputDir);

  if (!existsSync(outputDir)) {
    await mkdir(outputDir, { recursive: true });
  }

  const files = await readdir(inputDir);
  const tasks = [];

  for (const f of files) {
    const ext = extname(f);
    const name = basename(f, ext);
    const inputPath = join(inputDir, f);
    const outputPath = join(outputDir, `${name}.svg`);

    if (ext === '.mmd') {
      tasks.push({
        kind: 'mermaid',
        run: () => runChild('render-mermaid.mjs', [
          '--input', inputPath, '--output', outputPath, '--theme', args.theme,
        ]),
        name: f,
      });
    } else if (ext === '.json') {
      const cli = ['--input', inputPath, '--output', outputPath, '--theme', args.theme];
      if (args.width)  cli.push('--width', String(args.width));
      if (args.height) cli.push('--height', String(args.height));
      tasks.push({
        kind: 'echarts',
        run: () => runChild('render-echarts.mjs', cli),
        name: f,
      });
    }
  }

  if (tasks.length === 0) {
    console.warn(`No .mmd or .json files found in ${inputDir}`);
    process.exit(0);
  }

  console.log(`▶ Rendering ${tasks.length} charts (concurrency=${args.concurrency}, theme=${args.theme})\n`);

  // 简单并发池
  let cursor = 0;
  let failed = 0;
  async function worker() {
    while (cursor < tasks.length) {
      const t = tasks[cursor++];
      try {
        await t.run();
      } catch (e) {
        console.error(`✗ ${t.name}: ${e.message}`);
        failed++;
      }
    }
  }
  const workers = Array.from({ length: Math.min(args.concurrency, tasks.length) }, worker);
  await Promise.all(workers);

  console.log(`\n${tasks.length - failed}/${tasks.length} succeeded${failed ? ', ' + failed + ' failed' : ''}.`);
  process.exit(failed ? 1 : 0);
}

main().catch(e => { console.error(e); process.exit(1); });
