import fs from 'node:fs';
import path from 'node:path';

const [fragmentPath, cssPath, outputPath, diagramDir, diagramFormat = 'svg'] = process.argv.slice(2);

if (!fragmentPath || !cssPath || !outputPath) {
  throw new Error('Usage: node render-sourcebook.mjs <fragment.html> <style.css> <output.html>');
}

let fragment = fs.readFileSync(fragmentPath, 'utf8');
const css = fs.readFileSync(cssPath, 'utf8');
const reviewed = '27 August 2026';

if (diagramDir) {
  let diagramIndex = 0;
  fragment = fragment.replace(
    /<pre><code class="language-mermaid">[\s\S]*?<\/code><\/pre>/g,
    () => {
      diagramIndex += 1;
      if (diagramFormat === 'png') {
        const pngPath = path.resolve(diagramDir, `diagram-${diagramIndex}.png`);
        const pngData = fs.readFileSync(pngPath).toString('base64');
        return `<figure class="diagram"><img src="data:image/png;base64,${pngData}" alt="Sourcebook diagram ${diagramIndex}"></figure>`;
      }
      const svgPath = path.join(diagramDir, `diagram-${diagramIndex}.svg`);
      const svg = fs.readFileSync(svgPath, 'utf8')
        .replace(/^<\?xml[^>]*>\s*/i, '')
        .replace(/<!DOCTYPE[^>]*>\s*/i, '');
      return `<figure class="diagram" aria-label="Sourcebook diagram">${svg}</figure>`;
    },
  );
}

const html = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="author" content="Sifututor">
  <meta name="description" content="The end-to-end Sifututor ecosystem sourcebook.">
  <title>The Sifututor Ecosystem — Built to Operate, Ready to Scale</title>
  <style>${css}</style>
</head>
<body>
  <div class="shell">
    <nav class="toc" aria-label="Document contents">
      <div class="toc-brand">Sifututor Ecosystem</div>
      <div id="toc-links"></div>
    </nav>
    <main id="sourcebook">
      ${fragment}
      <p class="print-note">Rendered from the governed Markdown source. Last reviewed ${reviewed}.</p>
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
console.log(outputPath);
