const fs = require('node:fs');
const HTMLtoDOCX = require('html-to-docx');

const [htmlPath, outputPath] = process.argv.slice(2);

if (!htmlPath || !outputPath) {
  throw new Error('Usage: node render-docx.cjs <source.html> <output.docx>');
}

(async () => {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const buffer = await HTMLtoDOCX(html, null, {
    title: 'The Sifututor Ecosystem: Built to Operate, Ready to Scale',
    creator: 'Sifututor',
    description: 'End-to-end Sifututor ecosystem sourcebook',
    pageSize: { width: '11906', height: '16838' },
    margins: { top: 850, right: 680, bottom: 850, left: 680 },
    table: { row: { cantSplit: true } },
    footer: true,
    pageNumber: true,
    font: 'Arial',
    fontSize: 21
  });
  fs.writeFileSync(outputPath, buffer);
  console.log(outputPath);
})();
