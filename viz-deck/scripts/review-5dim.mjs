#!/usr/bin/env node
/**
 * viz-deck · 5-dimension design critique
 *
 * Inputs a scoring JSON, emits an HTML critique report with embedded radar chart.
 * Scoring source of truth: ~/.claude/skills/huashu-design/references/critique-guide.md
 *
 * Usage:
 *   node review-5dim.mjs --input scores.json --output critique.html
 *
 * scores.json format:
 * {
 *   "subject": "Project Mingjing keynote",
 *   "mode": "keynote-report" | "prototype" | "slide-deck" | "motion-stage",
 *   "philosophy": "18 Kenya Hara",
 *   "dimensions": {
 *     "philosophy_alignment": { "score": 8, "note": "..." },
 *     "visual_hierarchy":      { "score": 8, "note": "..." },
 *     "craft_quality":         { "score": 7, "note": "..." },
 *     "functionality":         { "score": 8, "note": "..." },
 *     "originality":           { "score": 7, "note": "..." }
 *   },
 *   "keep":  ["…", "…"],
 *   "fix":   [{ "severity": "critical|important|polish", "name": "…", "current": "…", "issue": "…", "fix": "…" }],
 *   "quick_wins": ["…", "…", "…"]
 * }
 */
import fs from 'node:fs';
import path from 'node:path';

const args = Object.fromEntries(
  process.argv.slice(2).reduce((acc, a, i, arr) => {
    if (a.startsWith('--')) acc.push([a.slice(2), arr[i + 1]]);
    return acc;
  }, [])
);

const input  = args.input  || 'scores.json';
const output = args.output || 'critique.html';

if (!fs.existsSync(input)) {
  console.error(`[review-5dim] scores file not found: ${input}`);
  process.exit(1);
}

const data = JSON.parse(fs.readFileSync(input, 'utf8'));
const d = data.dimensions;
const scores = [
  d.philosophy_alignment?.score ?? 0,
  d.visual_hierarchy?.score ?? 0,
  d.craft_quality?.score ?? 0,
  d.functionality?.score ?? 0,
  d.originality?.score ?? 0,
];
const overall = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1);
const verdict =
  overall >= 8   ? '优秀' :
  overall >= 6   ? '良好' :
  overall >= 4   ? '需改进' : '不合格';

const severityRank = { critical: '⚠️致命', important: '⚡重要', polish: '💡优化' };

const html = `<!doctype html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>设计评审报告 · ${data.subject}</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Newsreader:wght@400;500&display=swap" rel="stylesheet">
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
  :root { --bg:#030711; --fg:#e7efff; --muted:#8898b6; --accent:#42e8ff; --gold:#ffd987; --red:#ff5577; }
  * { box-sizing: border-box; }
  body { margin:0; background:var(--bg); color:var(--fg); font-family:Inter, system-ui, sans-serif; padding:64px 12vw; }
  .eyebrow { color:var(--accent); font-family:ui-monospace, monospace; font-size:13px; letter-spacing:.22em; text-transform:uppercase; }
  h1 { font-family:Newsreader, serif; font-size:56px; font-weight:500; line-height:1.1; margin:16px 0 8px; }
  .meta { color:var(--muted); font-family:ui-monospace, monospace; font-size:13px; letter-spacing:.06em; margin-bottom:48px; }
  .meta span+span:before { content:" · "; color:var(--muted); margin:0 6px; }
  .overall { display:flex; align-items:baseline; gap:16px; margin-bottom:32px; }
  .overall .score { font-family:ui-monospace, monospace; font-size:88px; font-weight:600; color:var(--gold); line-height:1; }
  .overall .verdict { font-size:24px; color:var(--accent); }
  .grid { display:grid; grid-template-columns: 1fr 1fr; gap:48px; margin-bottom:64px; align-items:start; }
  #radar { width:100%; height:420px; }
  table { width:100%; border-collapse:collapse; font-size:15px; }
  th, td { padding:14px 12px; text-align:left; border-bottom:1px solid rgba(255,255,255,.08); vertical-align:top; }
  th { color:var(--muted); font-weight:500; font-size:12px; letter-spacing:.14em; text-transform:uppercase; }
  td.score-cell { font-family:ui-monospace, monospace; color:var(--gold); width:60px; }
  section.block { margin-bottom:48px; }
  section.block h2 { font-family:ui-monospace, monospace; font-size:14px; letter-spacing:.22em; color:var(--accent); text-transform:uppercase; margin:0 0 16px; }
  ul { margin:0; padding-left:18px; line-height:1.7; }
  .fix-item { padding:16px 0; border-bottom:1px solid rgba(255,255,255,.06); }
  .fix-item:last-child { border:0; }
  .fix-item strong { font-size:18px; }
  .fix-item .row { color:var(--muted); margin-top:6px; }
  .fix-item .row b { color:var(--fg); font-weight:500; }
  .qw label { display:flex; gap:12px; padding:12px 0; align-items:center; }
  .qw input[type=checkbox] { transform:scale(1.4); accent-color:var(--gold); }
</style>
</head>
<body>

<div class="eyebrow">5-DIMENSION DESIGN CRITIQUE</div>
<h1>${data.subject}</h1>
<div class="meta">
  <span>MODE · ${data.mode}</span>
  <span>哲学 · ${data.philosophy || '—'}</span>
  <span>${new Date().toISOString().slice(0,10)}</span>
</div>

<div class="overall">
  <span class="score">${overall}</span>
  <span class="verdict">${verdict}</span>
  <span style="color:var(--muted)">/ 10</span>
</div>

<div class="grid">
  <div id="radar"></div>
  <table>
    <tr><th>维度</th><th>分</th><th>简评</th></tr>
    <tr><td>哲学一致性</td><td class="score-cell">${d.philosophy_alignment?.score ?? 0}/10</td><td>${d.philosophy_alignment?.note || ''}</td></tr>
    <tr><td>视觉层级</td>   <td class="score-cell">${d.visual_hierarchy?.score ?? 0}/10</td>     <td>${d.visual_hierarchy?.note || ''}</td></tr>
    <tr><td>细节执行</td>   <td class="score-cell">${d.craft_quality?.score ?? 0}/10</td>       <td>${d.craft_quality?.note || ''}</td></tr>
    <tr><td>功能性</td>     <td class="score-cell">${d.functionality?.score ?? 0}/10</td>      <td>${d.functionality?.note || ''}</td></tr>
    <tr><td>创新性</td>     <td class="score-cell">${d.originality?.score ?? 0}/10</td>        <td>${d.originality?.note || ''}</td></tr>
  </table>
</div>

<section class="block">
  <h2>Keep · 做对的事</h2>
  <ul>${(data.keep || []).map(k => `<li>${k}</li>`).join('')}</ul>
</section>

<section class="block">
  <h2>Fix · 待修复</h2>
  ${(data.fix || []).map(f => `
    <div class="fix-item">
      <strong>${severityRank[f.severity] || ''} · ${f.name}</strong>
      <div class="row"><b>当前：</b>${f.current}</div>
      <div class="row"><b>问题：</b>${f.issue}</div>
      <div class="row"><b>修复：</b>${f.fix}</div>
    </div>`).join('')}
</section>

<section class="block qw">
  <h2>Quick Wins · 5 分钟必修</h2>
  ${(data.quick_wins || []).map(qw => `<label><input type="checkbox"> ${qw}</label>`).join('')}
</section>

<script>
  echarts.init(document.getElementById('radar')).setOption({
    backgroundColor: 'transparent',
    radar: {
      indicator: [
        { name: '哲学一致性', max: 10 },
        { name: '视觉层级',   max: 10 },
        { name: '细节执行',   max: 10 },
        { name: '功能性',     max: 10 },
        { name: '创新性',     max: 10 }
      ],
      axisName: { color: '#8898b6', fontSize: 12 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.08)' } },
      splitArea: { areaStyle: { color: ['rgba(66,232,255,0.03)', 'rgba(255,255,255,0.02)'] } },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.12)' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: ${JSON.stringify(scores)},
        name: '当前评分',
        symbol: 'circle',
        symbolSize: 8,
        itemStyle: { color: '#ffd987' },
        lineStyle: { color: '#42e8ff', width: 2 },
        areaStyle: { color: 'rgba(66, 232, 255, 0.18)' }
      }]
    }]
  });
</script>

</body>
</html>
`;

fs.writeFileSync(output, html, 'utf8');
console.log(`[review-5dim] wrote ${output} (overall ${overall} / ${verdict})`);
