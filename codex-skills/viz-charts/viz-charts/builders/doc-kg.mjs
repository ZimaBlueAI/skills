#!/usr/bin/env node
/**
 * doc-kg.mjs · 从 Markdown 文档集合提取概念图
 *
 * 抽取目标：
 *   - 文件 → 一个 "section" 节点（带标题、字数、所在路径）
 *   - 标题层级 → parent-of 边
 *   - markdown 链接 [...](relative.md) → references 边
 *   - 显式标注的概念（**concept** / `code-term` / 标题中的关键词）→ concept 节点
 *   - concept 在多个文件中出现 → mentioned-in 边
 *
 * 用法：
 *   node doc-kg.mjs --input ./docs --output doc-kg.json
 *
 * 选项：
 *   --input  / -i     文档目录或单文件 (默认 cwd)
 *   --output / -o     输出 JSON
 *   --include-pdf     是否包含 .pdf（需要安装 pdf-parse 包）默认 false
 *   --min-mentions    一个术语至少出现 N 次才算 concept（默认 2）
 *   --top-terms       自动抽取的高频术语数量上限（默认 40）
 *   --max-files       文件数上限（默认 200）
 */

import { readdir, readFile, writeFile, stat } from 'node:fs/promises';
import { join, relative, extname, basename, dirname, resolve } from 'node:path';

function parseArgs(argv) {
  const args = { input: process.cwd(), output: 'doc-kg.json', minMentions: 2, topTerms: 40, maxFiles: 200, includePdf: false };
  for (let i = 2; i < argv.length; i++) {
    const k = argv[i], v = argv[i + 1];
    if (k === '--input'  || k === '-i') { args.input = v; i++; }
    else if (k === '--output' || k === '-o') { args.output = v; i++; }
    else if (k === '--min-mentions')         { args.minMentions = parseInt(v); i++; }
    else if (k === '--top-terms')            { args.topTerms = parseInt(v); i++; }
    else if (k === '--max-files')            { args.maxFiles = parseInt(v); i++; }
    else if (k === '--include-pdf')          { args.includePdf = true; }
    else if (k === '--help' || k === '-h')   { args.help = true; }
  }
  return args;
}

const args = parseArgs(process.argv);
if (args.help) {
  console.log(`
doc-kg · 从 Markdown 提取文档概念 KG

用法：
  node doc-kg.mjs --input <dir-or-file> --output <file.json>

选项：
  --input          文档目录或单 md 文件
  --output         输出 JSON
  --min-mentions   术语至少出现 N 次才纳入（默认 2）
  --top-terms      高频术语上限（默认 40）
  --include-pdf    包含 PDF（需 npm i pdf-parse）

输出：data-graph.html viewer 可消费的 JSON 契约
`);
  process.exit(0);
}

const EXCLUDE_DIRS = new Set(['node_modules', '.git', 'dist', 'build', '.next', '.cache', 'coverage']);

// ---- 收集文件 ----
async function* walk(dir) {
  let entries;
  try { entries = await readdir(dir, { withFileTypes: true }); }
  catch { return; }
  for (const e of entries) {
    if (EXCLUDE_DIRS.has(e.name)) continue;
    if (e.name.startsWith('.') && !['.claude', '.github'].includes(e.name)) continue;
    const full = join(dir, e.name);
    if (e.isDirectory()) yield* walk(full);
    else if (e.isFile()) {
      const ext = extname(e.name).toLowerCase();
      if (ext === '.md' || ext === '.mdx' || ext === '.markdown') yield { full, ext };
      else if (ext === '.pdf' && args.includePdf) yield { full, ext };
    }
  }
}

// ---- PDF 文本（可选）----
async function readPdf(path) {
  try {
    const pdfParse = (await import('pdf-parse')).default;
    const buf = await readFile(path);
    const r = await pdfParse(buf);
    return r.text;
  } catch (e) {
    console.warn(`  ⚠ PDF skip ${path}: ${e.message}`);
    return null;
  }
}

// ---- Markdown 解析 ----
function parseMarkdown(content) {
  const lines = content.split('\n');
  const headings = []; // [{ level, text, idx }]
  const inlineLinks = []; // [{ text, target }]
  const concepts = new Set(); // 显式标记的概念
  const codeTerms = new Set();

  let inCode = false;
  lines.forEach((line, idx) => {
    if (/^```/.test(line.trim())) { inCode = !inCode; return; }
    if (inCode) return;

    // 标题
    const h = line.match(/^(#{1,6})\s+(.+?)(?:\s*\{#[\w-]+\})?$/);
    if (h) headings.push({ level: h[1].length, text: h[2].trim(), idx });

    // 链接
    const linkRe = /\[([^\]]+)\]\(([^)]+)\)/g;
    let m;
    while ((m = linkRe.exec(line)) !== null) {
      inlineLinks.push({ text: m[1], target: m[2] });
    }

    // 加粗术语作为 concept
    const boldRe = /\*\*([^*\n]{2,40})\*\*/g;
    while ((m = boldRe.exec(line)) !== null) concepts.add(m[1].trim());

    // 行内代码作为 codeTerm
    const codeRe = /`([^`\n]{2,40})`/g;
    while ((m = codeRe.exec(line)) !== null) {
      const t = m[1].trim();
      // 过滤太琐碎的：含空格的 phrase / 大写常量 / camelCase
      if (/^[A-Z_]+$/.test(t) || /[A-Z][a-z]/.test(t) || t.includes('::') || t.includes('.')) {
        codeTerms.add(t);
      }
    }
  });

  return { headings, inlineLinks, concepts: [...concepts], codeTerms: [...codeTerms], lineCount: lines.length };
}

// ---- 高频术语抽取（保留有意义的 phrase） ----
function extractFrequentTerms(allText) {
  // 提取 2-4 token 的英文短语 + 中文词组
  const phraseFreq = new Map();

  // 英文：连续 2-3 个 capitalized word 视为短语
  const enRe = /\b([A-Z][a-zA-Z0-9]+(?:\s+[A-Z][a-zA-Z0-9]+){0,2})\b/g;
  let m;
  while ((m = enRe.exec(allText)) !== null) {
    const p = m[1];
    if (p.length < 4) continue;
    // 排除"This is"等
    if (/^(This|That|These|Those|The|A|An|And|Or|But|For|To|Of|In|On|At|By|With|From)\b/i.test(p)) continue;
    phraseFreq.set(p, (phraseFreq.get(p) || 0) + 1);
  }

  // 中文：抽取连续 2-6 个汉字视为词组（粗暴但有用）
  const cnRe = /[\u4e00-\u9fa5]{2,6}/g;
  while ((m = cnRe.exec(allText)) !== null) {
    const p = m[0];
    phraseFreq.set(p, (phraseFreq.get(p) || 0) + 1);
  }

  return [...phraseFreq.entries()]
    .filter(([_, c]) => c >= args.minMentions)
    .sort((a, b) => b[1] - a[1])
    .slice(0, args.topTerms);
}

// ---- 主流程 ----
async function main() {
  const inputResolved = resolve(args.input);
  let inputStat;
  try { inputStat = await stat(inputResolved); }
  catch { console.error(`Input not found: ${inputResolved}`); process.exit(1); }

  // 收集文件
  const files = [];
  if (inputStat.isFile()) {
    files.push({ full: inputResolved, ext: extname(inputResolved).toLowerCase() });
  } else {
    for await (const f of walk(inputResolved)) {
      files.push(f);
      if (files.length >= args.maxFiles) {
        console.warn(`⚠ max-files=${args.maxFiles} reached`);
        break;
      }
    }
  }

  if (files.length === 0) {
    console.error('No markdown files found.');
    process.exit(1);
  }

  console.log(`▶ Processing ${files.length} files...`);

  const baseDir = inputStat.isFile() ? dirname(inputResolved) : inputResolved;
  const fileNodes = []; // 文件级节点
  const sectionNodes = []; // 二级标题级节点
  const links = [];
  const linkSet = new Set();
  const allConcepts = new Map(); // term → [fileId...]
  const fileContents = []; // for term extraction

  // Pass 1: 文件 + sections + 显式 concepts
  for (const f of files) {
    let content;
    if (f.ext === '.pdf') {
      content = await readPdf(f.full);
      if (!content) continue;
    } else {
      try { content = await readFile(f.full, 'utf-8'); }
      catch { continue; }
    }

    fileContents.push({ rel: relative(baseDir, f.full), content });

    const rel = relative(baseDir, f.full).replace(/\\/g, '/');
    const parsed = parseMarkdown(content);

    // 文件节点
    const fileTitle = parsed.headings.length > 0 && parsed.headings[0].level === 1
      ? parsed.headings[0].text
      : basename(f.full);
    fileNodes.push({
      id: 'file:' + rel,
      name: fileTitle,
      group: 'document',
      size: Math.max(4, Math.min(20, Math.round(Math.log2(parsed.lineCount + 1) * 1.8))),
      desc: `${rel} · ${parsed.lineCount} lines · ${parsed.headings.length} sections`,
    });

    // section 节点（仅 h2）
    parsed.headings.filter(h => h.level === 2).forEach((h, hi) => {
      const sId = `section:${rel}#${hi}`;
      sectionNodes.push({
        id: sId,
        name: h.text,
        group: 'section',
        size: 4,
        desc: `${rel} · §${hi + 1}`,
      });
      const k = `file:${rel}→${sId}`;
      if (!linkSet.has(k)) {
        linkSet.add(k);
        links.push({ source: 'file:' + rel, target: sId, type: 'parent-of', value: 1 });
      }
    });

    // 文件间链接
    parsed.inlineLinks.forEach(l => {
      if (!l.target) return;
      if (/^https?:/.test(l.target)) return; // 外链
      const targetPath = resolve(dirname(f.full), l.target.split('#')[0]);
      const targetRel = relative(baseDir, targetPath).replace(/\\/g, '/');
      const targetId = 'file:' + targetRel;
      if (fileContents.some(fc => fc.rel === targetRel) || files.some(ff => relative(baseDir, ff.full).replace(/\\/g, '/') === targetRel)) {
        const k = 'file:' + rel + '→' + targetId;
        if (!linkSet.has(k)) {
          linkSet.add(k);
          links.push({ source: 'file:' + rel, target: targetId, type: 'links-to', value: 1 });
        }
      }
    });

    // 显式 concepts
    const explicit = new Set([...parsed.concepts, ...parsed.codeTerms]);
    explicit.forEach(c => {
      if (!allConcepts.has(c)) allConcepts.set(c, new Set());
      allConcepts.get(c).add('file:' + rel);
    });
  }

  // Pass 2: 高频术语
  const allText = fileContents.map(fc => fc.content).join('\n\n');
  const frequent = extractFrequentTerms(allText);
  console.log(`  found ${frequent.length} frequent terms`);

  // 把高频术语补进 allConcepts（如果还没有）
  frequent.forEach(([term, freq]) => {
    if (!allConcepts.has(term)) {
      // 找它出现在哪些文件
      const inFiles = new Set();
      fileContents.forEach(fc => {
        if (fc.content.includes(term)) inFiles.add('file:' + fc.rel);
      });
      if (inFiles.size > 0) allConcepts.set(term, inFiles);
    }
  });

  // 生成 concept 节点（仅保留出现 ≥ minMentions 次）
  const conceptNodes = [];
  for (const [term, inFiles] of allConcepts.entries()) {
    if (inFiles.size < args.minMentions) continue;
    const id = 'concept:' + term.replace(/[^\w\u4e00-\u9fa5]/g, '_').slice(0, 60);
    conceptNodes.push({
      id,
      name: term,
      group: 'concept',
      size: Math.max(3, Math.min(16, 3 + inFiles.size * 1.5)),
      desc: `提及于 ${inFiles.size} 个文件`,
    });
    inFiles.forEach(fileId => {
      const k = id + '→' + fileId;
      if (!linkSet.has(k)) {
        linkSet.add(k);
        links.push({ source: id, target: fileId, type: 'mentioned-in', value: 1 });
      }
    });
  }

  const nodes = [...fileNodes, ...sectionNodes, ...conceptNodes];

  // 重算 size 基于入度
  const inDegree = new Map();
  links.forEach(l => inDegree.set(l.target, (inDegree.get(l.target) || 0) + 1));
  nodes.forEach(n => {
    const d = inDegree.get(n.id) || 0;
    n.size = Math.max(n.size, Math.min(22, 4 + d * 0.8));
  });

  const groupCount = new Map();
  nodes.forEach(n => groupCount.set(n.group, (groupCount.get(n.group) || 0) + 1));

  const result = {
    nodes,
    links,
    meta: {
      title: `${basename(inputResolved)} · Doc KG`,
      subtitle: `${fileNodes.length} files · ${sectionNodes.length} sections · ${conceptNodes.length} concepts`,
      stats: { nodes: nodes.length, edges: links.length, groups: groupCount.size },
      generated: new Date().toISOString(),
      input: inputResolved,
    },
  };

  await writeFile(resolve(args.output), JSON.stringify(result, null, 2), 'utf-8');
  console.log(`\n✓ Wrote ${args.output}`);
  console.log(`  ${fileNodes.length} files + ${sectionNodes.length} sections + ${conceptNodes.length} concepts = ${nodes.length} nodes`);
  console.log(`  ${links.length} edges · ${groupCount.size} groups`);
  console.log(`\nNext: open templates/kg3d/doc-graph.html, replace {{KG_DATA_JSON}} with the contents of ${args.output}.`);
}

main().catch(e => { console.error(e); process.exit(1); });
