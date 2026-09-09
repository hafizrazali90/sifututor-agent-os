import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const markedPath = process.env.MARKED_MODULE
  || '/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/marked';
const { marked } = require(markedPath);

const [markdownPath, outputPath] = process.argv.slice(2);
if (!markdownPath || !outputPath) {
  throw new Error('Usage: node render-deck.mjs <deck.md> <deck.html>');
}

const source = fs.readFileSync(markdownPath, 'utf8');
const sourceDir = path.dirname(path.resolve(markdownPath));
const rawSlides = source.split(/\n---\n/g).map((slide) => slide.trim()).filter(Boolean);

function commentValue(slide, key) {
  return slide.match(new RegExp(`<!--\\s*${key}:\\s*([\\s\\S]*?)\\s*-->`, 'i'))?.[1]?.trim() || '';
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[char]));
}

const slides = rawSlides.map((raw, index) => {
  const layout = commentValue(raw, 'layout') || (index === 0 ? 'cover' : 'standard');
  const visual = commentValue(raw, 'visual');
  const notes = commentValue(raw, 'notes');
  const sources = commentValue(raw, 'sources');
  const cleaned = raw.replace(/<!--[\s\S]*?-->/g, '').trim();
  let body = marked.parse(cleaned, { gfm: true });
  if (layout === 'partnership') {
    const h1 = body.match(/<h1[\s\S]*?<\/h1>/)?.[0] || '';
    const remainder = body.slice(h1.length);
    const groups = remainder.match(/<h2[\s\S]*?(?=<h2|$)/g) || [remainder];
    body = `${h1}<div class="partnership-grid">${groups.map((group) => `<div class="partnership-col">${group}</div>`).join('')}</div>`;
  }
  let visualHtml = '';
  if (visual) {
    const visualPath = path.resolve(sourceDir, visual);
    if (fs.existsSync(visualPath)) {
      visualHtml = `<figure class="visual" aria-label="Slide visual">${fs.readFileSync(visualPath, 'utf8').replace(/^<\?xml[^>]*>\s*/i, '').replace(/<!DOCTYPE[^>]*>\s*/i, '')}</figure>`;
    }
  }
  return `<section class="slide layout-${escapeHtml(layout)}${visualHtml ? ' has-visual' : ''}" data-slide="${index + 1}">
    <div class="top-rule"></div>
    <div class="slide-body"><div class="content">${body}</div>${visualHtml}</div>
    ${sources ? `<div class="sources">Source: ${escapeHtml(sources)}</div>` : ''}
    <div class="slide-number">${index + 1} / ${rawSlides.length}</div>
    ${notes ? `<aside class="speaker-notes">${escapeHtml(notes)}</aside>` : ''}
  </section>`;
});

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>TEKUN Collection Partnership Presentation</title>
<style>
:root { --navy:#102f49; --teal:#00a896; --teal-soft:#e8f6f3; --sand:#f7edcf; --ink:#172033; --muted:#5c6b7a; --line:#d9e2ea; }
* { box-sizing:border-box; }
html,body { margin:0; padding:0; background:#dfe7ed; color:var(--ink); font-family:Inter,Arial,sans-serif; }
.slide { position:relative; width:13.333in; height:7.5in; margin:18px auto; padding:.46in .58in .42in; background:#fff; overflow:hidden; box-shadow:0 8px 32px rgba(16,47,73,.16); break-after:page; }
.top-rule { position:absolute; top:0; left:0; right:0; height:7px; background:linear-gradient(90deg,var(--navy),var(--teal)); }
.slide-body { height:100%; display:flex; flex-direction:column; }
.content { min-width:0; }
h1 { margin:.08in 0 .18in; color:var(--navy); font-size:28pt; line-height:1.08; letter-spacing:-.45px; }
h2 { margin:.18in 0 .08in; color:var(--navy); font-size:16pt; line-height:1.15; }
p,li,td,th { font-size:12.2pt; line-height:1.34; }
p { margin:.08in 0 .13in; }
ul,ol { margin:.08in 0 .14in; padding-left:.26in; }
li { margin:.045in 0; }
strong { color:var(--navy); }
blockquote { margin:.16in 0; padding:.16in .2in; border-left:5px solid var(--teal); background:var(--teal-soft); color:var(--navy); font-size:16pt; }
blockquote p { font-size:16pt; line-height:1.3; margin:0; }
table { width:100%; border-collapse:collapse; margin:.1in 0; }
th { background:var(--navy); color:#fff; font-weight:700; text-align:left; }
th,td { border:1px solid var(--line); padding:.07in .09in; vertical-align:top; font-size:9.8pt; }
tr:nth-child(even) td { background:#f3f6f8; }
.has-visual .slide-body { display:grid; grid-template-columns:minmax(0,58%) minmax(0,42%); gap:.24in; align-items:center; }
.visual { margin:0; width:100%; display:flex; align-items:center; justify-content:center; }
.visual svg { width:100%; max-height:5.45in; height:auto; }
.sources { position:absolute; left:.58in; bottom:.16in; max-width:10.8in; font-size:7.4pt; color:#718096; }
.slide-number { position:absolute; right:.35in; bottom:.14in; font-size:7.4pt; color:#718096; }
.speaker-notes { display:none; }
.layout-cover { background:linear-gradient(135deg,#102f49 0%,#0b5361 62%,#00a896 100%); color:#fff; padding:.72in .72in; }
.layout-cover .top-rule { display:none; }
.layout-cover h1,.layout-cover h2,.layout-cover strong { color:#fff; }
.layout-cover h1 { margin-top:1.25in; font-size:36pt; max-width:9in; }
.layout-cover h2 { font-size:25pt; max-width:10.2in; }
.layout-cover p { margin-top:.6in; color:#effffc; }
.layout-cover .slide-number { color:#d9fffa; }
.layout-statement .content { max-width:10.8in; margin:auto; text-align:center; }
.layout-statement h1 { font-size:26pt; }
.layout-statement blockquote { font-size:22pt; padding:.35in; }
.layout-statement blockquote p { font-size:22pt; }
.layout-two-column .content { columns:2; column-gap:.45in; }
.layout-two-column h1 { column-span:all; }
.layout-two-column h2 { break-after:avoid; }
.layout-partnership .partnership-grid { display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); gap:.34in; align-items:start; }
.layout-partnership .partnership-col { padding:.12in .15in .18in; border-top:4px solid var(--teal); background:linear-gradient(180deg,#f7fbfb 0%,#fff 100%); min-height:3.55in; }
.layout-partnership .partnership-col h2 { margin-top:.08in; }
.layout-roadmap .content { columns:2; column-gap:.35in; }
.layout-roadmap h1 { column-span:all; }
.layout-questions .content ol { columns:2; column-gap:.5in; padding-left:.28in; }
.layout-questions h1 { font-size:25pt; }
.layout-questions li { break-inside:avoid; font-size:11pt; line-height:1.25; margin:.04in 0; }
.layout-compact h1 { font-size:23pt; margin-bottom:.1in; }
.layout-compact th,.layout-compact td { font-size:8.3pt; padding:.045in .065in; }
.layout-compact p { font-size:10pt; line-height:1.28; }
.layout-decision { background:linear-gradient(180deg,#fff 0%,#edf8f6 100%); }
.layout-decision h1 { font-size:30pt; }
.layout-milestone table { margin-top:.14in; }
.layout-milestone th,.layout-milestone td { font-size:9pt; }
@media print {
  @page { size:13.333in 7.5in; margin:0; }
  html,body { background:#fff; }
  .slide { margin:0; box-shadow:none; }
}
</style>
</head>
<body>${slides.join('\n')}</body>
</html>`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, html);
console.log(`${outputPath}\nslides=${slides.length}`);
