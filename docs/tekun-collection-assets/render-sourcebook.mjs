import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const markedPath = process.env.MARKED_MODULE
  || '/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/marked';
const { marked } = require(markedPath);

const [markdownPath, cssPath, outputPath, diagramDir, diagramFormat = 'svg'] = process.argv.slice(2);

if (!markdownPath || !cssPath || !outputPath || !diagramDir) {
  throw new Error('Usage: node render-sourcebook.mjs <source.md> <style.css> <output.html> <diagram-dir>');
}

const markdown = fs.readFileSync(markdownPath, 'utf8');
const css = fs.readFileSync(cssPath, 'utf8');
let fragment = marked.parse(markdown, { gfm: true });
let diagramIndex = 0;

function diagramShape(svg) {
  const match = svg.match(/viewBox="[^\"]*?([\d.]+)\s+([\d.]+)"/i);
  if (!match) return 'diagram-balanced';
  const width = Number(match[1]);
  const height = Number(match[2]);
  const ratio = width / height;
  if (ratio >= 1.35) return 'diagram-landscape';
  if (ratio <= 0.75) return 'diagram-portrait';
  return 'diagram-balanced';
}

fragment = fragment.replace(
  /<pre><code class="language-mermaid">[\s\S]*?<\/code><\/pre>/g,
  () => {
    diagramIndex += 1;
    const svgPath = path.join(diagramDir, `diagram-${diagramIndex}.svg`);
    const svgSource = fs.readFileSync(svgPath, 'utf8');
    const shapeClass = diagramShape(svgSource);
    if (diagramFormat === 'png') {
      const pngPath = path.join(diagramDir, `diagram-${diagramIndex}.png`);
      const png = fs.readFileSync(pngPath).toString('base64');
      return `<figure class="diagram diagram-${diagramIndex} ${shapeClass}" aria-label="Collection partnership diagram ${diagramIndex}"><img src="data:image/png;base64,${png}" alt="Collection partnership diagram ${diagramIndex}"></figure>`;
    }
    const svg = svgSource
      .replace(/^<\?xml[^>]*>\s*/i, '')
      .replace(/<!DOCTYPE[^>]*>\s*/i, '');
    return `<figure class="diagram diagram-${diagramIndex} ${shapeClass}" aria-label="Collection partnership diagram ${diagramIndex}">${svg}</figure>`;
  },
);

fragment = fragment.replace(/<ol>([\s\S]*?)<\/ol>/g, (list, items) => {
  const itemCount = (items.match(/<li>/g) || []).length;
  if (itemCount < 8 || itemCount > 12) return list;
  return `<ol class="compact-ordered-list">${items}</ol>`;
});

fragment = fragment.replace(
  /(<h3\b[^>]*>[^<]+<\/h3>)\s*(<p\b[^>]*>(?:(?!<p\b|<\/?h[1-6]\b|<table\b|<figure\b|<ul\b|<ol\b|<blockquote\b|<section\b)[\s\S])*?<\/p>)\s*(<ol class="compact-ordered-list">[\s\S]*?<\/ol>)/g,
  '<section class="compact-list-section">$1$2$3</section>',
);

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="Sifututor">
  <meta name="description" content="TEKUN Corporation integrated collection growth partnership sourcebook.">
  <title>TEKUN Corporation Integrated Collection Growth Partnership</title>
  <style>${css}
  .print-page-break { display: none; }
  @media print {
    .print-note { display: none; }
    .print-page-break { display: block; height: 0; break-before: page; }
    h2 { font-size: 17pt; break-inside: avoid-page; }
    h3 { margin: 24px 0 10px; }
    h4 { margin: 20px 0 8px; }
    p { margin-bottom: 12px; }
    table { margin: 16px 0 24px; }
    ul, ol { margin: 10px 0 18px; }
    .compact-ordered-list {
      columns: 2;
      column-gap: 12mm;
      break-inside: avoid-page;
    }
    .compact-ordered-list li { break-inside: avoid; }
    .compact-list-section { break-inside: avoid-page; }
    .compact-list-section .compact-ordered-list { columns: 1; }
    figure.diagram { margin: 12px 0 18px; padding: 4px; }
    figure.diagram.diagram-landscape svg { max-height: 68mm; }
    figure.diagram.diagram-balanced svg { width: auto; height: 55mm; }
    figure.diagram.diagram-portrait svg { width: auto; height: 105mm; }
    figure.diagram.diagram-9 svg,
    figure.diagram.diagram-15 svg {
      max-height: 92mm;
    }
    figure.diagram.diagram-10 svg {
      max-height: 118mm;
    }
    figure.diagram.diagram-14 svg {
      max-height: 54mm;
    }
  }
  </style>
</head>
<body>
  <div class="shell">
    <nav class="toc" aria-label="Document contents">
      <div class="toc-brand">Collection Growth Partnership</div>
      <div id="toc-links"></div>
    </nav>
    <main id="sourcebook">
      ${fragment}
      <p class="print-note">Rendered from the governed Markdown source. Last reviewed 31 August 2026.</p>
    </main>
  </div>
  <script>
    const slugCounts = new Map();
    const headings = [...document.querySelectorAll('#sourcebook h1, #sourcebook h2')];
    for (const heading of headings) {
      const base = heading.textContent.toLowerCase()
        .normalize('NFKD').replace(/[^a-z0-9\\s-]/g, '')
        .trim().replace(/\\s+/g, '-').slice(0, 72) || 'section';
      const count = (slugCounts.get(base) || 0) + 1;
      slugCounts.set(base, count);
      heading.id = count === 1 ? base : base + '-' + count;
      if (heading !== headings[0]) {
        const link = document.createElement('a');
        link.href = '#' + heading.id;
        link.className = heading.tagName === 'H1' ? 'toc-h1' : 'toc-h2';
        link.textContent = heading.textContent;
        document.querySelector('#toc-links').appendChild(link);
      }
    }
  </script>
</body>
</html>`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, html);
console.log(`${outputPath}\ndiagrams=${diagramIndex}`);
