import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const markedPath = process.env.MARKED_MODULE
  || '/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/marked';
const { marked } = require(markedPath);

const [markdownPath, outputPath, diagramFormat = 'svg'] = process.argv.slice(2);
if (!markdownPath || !outputPath) throw new Error('Usage: node render-proposal.mjs <proposal.md> <output.html> [svg|png]');

const sourceDir = path.dirname(path.resolve(markdownPath));
let markdown = fs.readFileSync(markdownPath, 'utf8');
markdown = markdown.replace(/<!-- pagebreak -->/g, '<div class="pagebreak"></div>');
markdown = markdown.replace(/<!-- diagram: ([^>]+?) -->/g, (_match, rel) => {
  const svgPath = path.resolve(sourceDir, rel.trim());
  if (diagramFormat === 'png') {
    const pngPath = svgPath.replace(/\.svg$/i, '.png');
    const png = fs.readFileSync(pngPath).toString('base64');
    return `<figure class="diagram"><img src="data:image/png;base64,${png}" alt="Proposal diagram"></figure>`;
  }
  const svg = fs.readFileSync(svgPath, 'utf8').replace(/^<\?xml[^>]*>\s*/i, '').replace(/<!DOCTYPE[^>]*>\s*/i, '');
  return `<figure class="diagram">${svg}</figure>`;
});
const fragment = marked.parse(markdown, { gfm: true });

const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>TEKUN Corporation Integrated Collection Growth Partnership</title><style>
:root{--navy:#102f49;--teal:#00a896;--soft:#e8f6f3;--sand:#f7edcf;--ink:#172033;--muted:#637487;--line:#d8e1e8}*{box-sizing:border-box}html,body{margin:0;background:#edf2f5;color:var(--ink);font-family:Arial,sans-serif;line-height:1.48}main{max-width:210mm;margin:22px auto;padding:20mm 18mm 22mm;background:#fff;box-shadow:0 12px 38px #102f4924}h1{margin:0 0 12mm;padding:29mm 17mm 20mm;background:linear-gradient(135deg,var(--navy),#0b5964 68%,var(--teal));color:#fff;font-size:29pt;line-height:1.06;letter-spacing:-.5px}h1+blockquote{margin-top:-12mm;background:#eefaf8;border-left:0;color:var(--navy);font-size:15pt}h2{margin:14mm 0 5mm;padding-bottom:3mm;border-bottom:2px solid var(--teal);color:var(--navy);font-size:20pt;line-height:1.15;break-after:avoid}h3{margin:7mm 0 2mm;color:var(--navy);font-size:13.5pt;break-after:avoid}p,li,td,th{font-size:10.2pt}p{margin:0 0 4mm}ul,ol{margin:2mm 0 5mm;padding-left:7mm}li{margin:1.1mm 0}blockquote{margin:6mm 0;padding:5mm 6mm;border-left:4px solid var(--teal);background:var(--soft);color:var(--navy)}blockquote p{margin:0;font-size:13pt}table{width:100%;margin:5mm 0 7mm;border-collapse:collapse;break-inside:avoid}th{background:var(--navy);color:white;text-align:left;font-weight:700}th,td{border:1px solid var(--line);padding:2.2mm 2.5mm;vertical-align:top;font-size:8.8pt;line-height:1.34}tr:nth-child(even) td{background:#f3f6f8}figure.diagram{margin:7mm auto;padding:4mm;border:1px solid var(--line);background:#fbfdfd;text-align:center;break-inside:avoid}figure.diagram svg,figure.diagram img{max-width:100%;max-height:92mm;width:auto;height:auto}.pagebreak{break-before:page;height:0}strong{color:var(--navy)}body:after{content:'Confidential — controlled stakeholder use';position:fixed;bottom:5mm;left:18mm;color:#7b8895;font-size:7.5pt}@media print{@page{size:A4;margin:12mm 12mm 14mm}html,body{background:#fff}main{max-width:none;margin:0;padding:0;box-shadow:none}h1{margin-left:0;margin-right:0}.pagebreak{break-before:page}h2,h3{break-after:avoid}table,figure,blockquote{break-inside:avoid}}
</style></head><body><main>${fragment}</main></body></html>`;
fs.writeFileSync(outputPath, html);
console.log(outputPath);
