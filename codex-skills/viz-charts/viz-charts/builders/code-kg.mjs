#!/usr/bin/env node
/**
 * code-kg.mjs · 从代码仓库提取 3D KG
 *
 * 抽取目标：
 *   - 文件 → 节点（含 LOC、语言、目录层级）
 *   - import / require / use / from 关系 → 边
 *
 * 支持语言：JS/TS/Go/Python/Rust（通过正则，不引重型 AST）
 *
 * 用法：
 *   node code-kg.mjs --repo ./my-project --output code-kg.json
 *
 * 选项：
 *   --repo / -r       仓库根目录 (默认 cwd)
 *   --output / -o     输出 JSON (默认 ./code-kg.json)
 *   --include         glob 模式（默认按语言推断）
 *   --exclude         排除（默认 node_modules / dist / build / .git / vendor）
 *   --group-by        node | language | dir | depth (默认 dir)
 *   --max-files       上限，默认 800（防爆炸）
 *
 * 输出契约见 templates/kg3d/code-graph.html
 */

import { readdir, readFile, stat, writeFile } from 'node:fs/promises';
import { join, relative, extname, dirname, basename, sep } from 'node:path';
import { resolve } from 'node:path';

// ---- CLI ----
function parseArgs(argv) {
  const args = { repo: process.cwd(), output: 'code-kg.json', groupBy: 'dir', maxFiles: 800 };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i], v = argv[i + 1];
    if (k === '--repo'   || k === '-r') { args.repo = v; i++; }
    else if (k === '--output' || k === '-o') { args.output = v; i++; }
    else if (k === '--include')              { args.include = v; i++; }
    else if (k === '--exclude')              { args.exclude = v; i++; }
    else if (k === '--group-by')             { args.groupBy = v; i++; }
    else if (k === '--max-files')            { args.maxFiles = parseInt(v); i++; }
    else if (k === '--help' || k === '-h')   { args.help = true; }
  }
  return args;
}

const args = parseArgs(process.argv);
if (args.help) {
  console.log(`
code-kg · 从代码仓库提取 3D KG

用法：
  node code-kg.mjs --repo <path> --output <file.json> [options]

选项：
  --repo / -r        仓库根目录（默认 cwd）
  --output / -o      输出 JSON
  --group-by         node | language | dir | depth (默认 dir)
  --max-files        上限 800
  --exclude          额外排除模式

支持语言：JS/TS, Go, Python, Rust

示例：
  node code-kg.mjs -r ../my-app -o my-app-kg.json --group-by language
`);
  process.exit(0);
}

// ---- 默认排除 ----
const DEFAULT_EXCLUDE = [
  'node_modules', 'dist', 'build', '.git', '.next', '.nuxt',
  'vendor', 'target', '__pycache__', '.venv', 'venv', 'env',
  '.cache', 'coverage', '.idea', '.vscode',
];
const extraExclude = (args.exclude || '').split(',').filter(Boolean);
const excludeSet = new Set([...DEFAULT_EXCLUDE, ...extraExclude]);

// ---- 语言定义 ----
const LANG_BY_EXT = {
  '.ts': 'ts', '.tsx': 'ts', '.mts': 'ts', '.cts': 'ts',
  '.js': 'js', '.jsx': 'js', '.mjs': 'js', '.cjs': 'js',
  '.go': 'go',
  '.py': 'py', '.pyx': 'py',
  '.rs': 'rust',
};

// 各语言 import 正则。捕获到的字符串视为"被引用的相对路径或包名"
const IMPORT_PATTERNS = {
  js: [
    /(?:^|\n)\s*import\s+(?:[\w*\s{},$]+\s+from\s+)?["']([^"']+)["']/g,
    /(?:^|\n|;)\s*(?:const|let|var)\s+[\w{}\s,$]+\s*=\s*require\(["']([^"']+)["']\)/g,
    /(?:^|\W)import\(\s*["']([^"']+)["']\s*\)/g,
  ],
  ts: null, // 同 js
  go: [
    /(?:^|\n)\s*import\s+"([^"]+)"/g,
    /(?:^|\n)\s*import\s*\(([^)]+)\)/g, // 多行 import 块单独处理
  ],
  py: [
    /(?:^|\n)\s*from\s+([.\w]+)\s+import/g,
    /(?:^|\n)\s*import\s+([.\w][.\w,\s]*)(?:\s+as\s+\w+)?/g,
  ],
  rust: [
    /(?:^|\n)\s*use\s+([\w:]+)/g,
    /(?:^|\n)\s*extern\s+crate\s+(\w+)/g,
  ],
};
IMPORT_PATTERNS.ts = IMPORT_PATTERNS.js;

// ---- 收集文件 ----
async function* walk(dir, root) {
  let entries;
  try { entries = await readdir(dir, { withFileTypes: true }); }
  catch { return; }
  for (const e of entries) {
    if (excludeSet.has(e.name)) continue;
    if (e.name.startsWith('.') && !['.github', '.claude'].includes(e.name)) continue;
    const full = join(dir, e.name);
    if (e.isDirectory()) yield* walk(full, root);
    else if (e.isFile()) {
      const ext = extname(e.name).toLowerCase();
      if (LANG_BY_EXT[ext]) yield { full, rel: relative(root, full), lang: LANG_BY_EXT[ext] };
    }
  }
}

// ---- 解析 import ----
function extractImports(content, lang) {
  const set = new Set();
  const patterns = IMPORT_PATTERNS[lang] || [];

  for (const re of patterns) {
    let m;
    re.lastIndex = 0;
    while ((m = re.exec(content)) !== null) {
      let target = m[1];
      // Go 多行 import 块特殊处理
      if (lang === 'go' && target.includes('\n')) {
        const inner = target.match(/"([^"]+)"/g) || [];
        inner.forEach(s => set.add(s.slice(1, -1)));
        continue;
      }
      // Python 可能是 "a, b, c"
      if (lang === 'py' && target.includes(',')) {
        target.split(',').forEach(t => {
          const tt = t.trim().split(/\s+as\s+/)[0].trim();
          if (tt) set.add(tt);
        });
        continue;
      }
      target = target.trim();
      if (target) set.add(target);
    }
  }
  return [...set];
}

// ---- 路径解析：把 import 字符串映射到本仓库内的文件 ----
function resolveImport(importStr, fromFile, allFiles, lang) {
  // 跳过外部包（不以 . 或 / 开头的）
  if (lang === 'js' || lang === 'ts') {
    if (!importStr.startsWith('.') && !importStr.startsWith('/')) return null;
  } else if (lang === 'go') {
    // 简化：只解析当前 go module 内的（含 / 但不含 .com / .org / 标准库）
    if (importStr.includes('.') && !importStr.startsWith('.')) {
      // 形如 github.com/x/y —— 跨 module，跳过
      // 但若属于同一 module，需要 go.mod parser，这里先简化保守
      return null;
    }
    if (!importStr.includes('/') && !importStr.startsWith('.')) return null; // 标准库
  } else if (lang === 'py') {
    if (!importStr.startsWith('.')) return null; // 绝对 import 跳过
  } else if (lang === 'rust') {
    if (importStr.startsWith('std') || importStr.startsWith('core')) return null;
  }

  const fromDir = dirname(fromFile);
  let candidate;

  if (importStr.startsWith('.')) {
    candidate = resolve(fromDir, importStr);
  } else {
    // 当作相对路径补全
    candidate = resolve(fromDir, importStr);
  }

  // 尝试匹配实际文件（带各种扩展名）
  const baseRel = relative(args.repo, candidate);
  const tryExts = ['', '.ts', '.tsx', '.js', '.jsx', '.mjs', '.go', '.py', '.rs', '/index.ts', '/index.js', '/__init__.py', '/mod.rs'];

  for (const ext of tryExts) {
    const tryPath = baseRel + ext;
    if (allFiles.has(tryPath)) return tryPath;
    const norm = tryPath.replace(/\\/g, '/');
    if (allFiles.has(norm)) return norm;
  }
  return null;
}

// ---- 主流程 ----
async function main() {
  const root = resolve(args.repo);
  console.log(`▶ Scanning ${root}...`);

  // 收集
  const files = [];
  for await (const f of walk(root, root)) {
    files.push(f);
    if (files.length >= args.maxFiles) {
      console.warn(`⚠ Reached max-files=${args.maxFiles}, stopping scan.`);
      break;
    }
  }

  if (files.length === 0) {
    console.error('No source files found.');
    process.exit(1);
  }

  console.log(`  found ${files.length} source files`);

  const allFilesSet = new Set(files.map(f => f.rel.replace(/\\/g, '/')));

  // 节点
  const nodes = [];
  const importsByFile = new Map();

  for (const f of files) {
    let content;
    try { content = await readFile(f.full, 'utf-8'); }
    catch { continue; }

    const loc = content.split('\n').length;
    const imports = extractImports(content, f.lang);
    importsByFile.set(f.rel.replace(/\\/g, '/'), imports);

    const dir = dirname(f.rel.replace(/\\/g, '/'));
    const depth = dir === '.' ? 0 : dir.split('/').length;

    let group;
    if (args.groupBy === 'language') group = f.lang;
    else if (args.groupBy === 'dir')   group = (dir === '.' ? 'root' : dir.split('/')[0]);
    else if (args.groupBy === 'depth') group = `L${depth}`;
    else                                group = 'all';

    nodes.push({
      id: f.rel.replace(/\\/g, '/'),
      name: basename(f.rel),
      group,
      size: Math.max(2, Math.min(20, Math.round(Math.log2(loc + 1) * 2))),
      desc: `${f.lang.toUpperCase()} · ${loc} LOC · ${dir}`,
      _meta: { lang: f.lang, loc, dir, depth },
    });
  }

  // 边
  const links = [];
  const linkSet = new Set();
  for (const f of files) {
    const fromId = f.rel.replace(/\\/g, '/');
    const imports = importsByFile.get(fromId) || [];
    for (const imp of imports) {
      const target = resolveImport(imp, f.full, allFilesSet, f.lang);
      if (target && target !== fromId) {
        const key = fromId + '→' + target;
        if (!linkSet.has(key)) {
          linkSet.add(key);
          links.push({ source: fromId, target, type: 'imports', value: 1 });
        }
      }
    }
  }

  // 计算入度作为参考 size
  const inDegree = new Map();
  links.forEach(l => inDegree.set(l.target, (inDegree.get(l.target) || 0) + 1));
  nodes.forEach(n => {
    const deg = inDegree.get(n.id) || 0;
    n.size = Math.max(n.size, Math.min(24, 4 + deg * 1.5));
  });

  // 移除 _meta 字段（仅内部用）
  nodes.forEach(n => delete n._meta);

  // 统计 group
  const groupCount = new Map();
  nodes.forEach(n => groupCount.set(n.group, (groupCount.get(n.group) || 0) + 1));

  const result = {
    nodes,
    links,
    meta: {
      title: `${basename(root)} · Code KG`,
      subtitle: `${nodes.length} files · ${links.length} imports · grouped by ${args.groupBy}`,
      stats: { nodes: nodes.length, edges: links.length, groups: groupCount.size },
      generated: new Date().toISOString(),
      repo: root,
      groupBy: args.groupBy,
    },
  };

  await writeFile(resolve(args.output), JSON.stringify(result, null, 2), 'utf-8');
  console.log(`\n✓ Wrote ${args.output}`);
  console.log(`  ${nodes.length} nodes · ${links.length} edges · ${groupCount.size} groups`);
  console.log(`\n  Top groups:`);
  [...groupCount.entries()].sort((a, b) => b[1] - a[1]).slice(0, 8).forEach(([g, c]) => {
    console.log(`    ${g.padEnd(20)} ${c} files`);
  });
  console.log(`\nNext: open templates/kg3d/code-graph.html, replace {{KG_DATA_JSON}} with the contents of ${args.output}, and open in browser.`);
}

main().catch(e => { console.error(e); process.exit(1); });
