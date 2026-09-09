const fs = require('node:fs');
const HTMLtoDOCX = require('html-to-docx');
const JSZip = require('jszip');

const [htmlPath, outputPath] = process.argv.slice(2);

if (!htmlPath || !outputPath) {
  throw new Error('Usage: node render-docx.cjs <source.html> <output.docx>');
}

(async () => {
  const html = fs.readFileSync(htmlPath, 'utf8');
  const buffer = await HTMLtoDOCX(html, null, {
    title: 'TEKUN Corporation Integrated Collection Growth Partnership',
    creator: 'Sifututor',
    description: 'Platform, managed operations, governance and measurable growth capability sourcebook',
    pageSize: { width: '11906', height: '16838' },
    margins: { top: 850, right: 680, bottom: 850, left: 680 },
    table: { row: { cantSplit: true } },
    footer: true,
    pageNumber: true,
    font: 'Arial',
    fontSize: 21,
  });
  const zip = await JSZip.loadAsync(buffer);
  const documentPath = 'word/document.xml';
  const relationshipsPath = 'word/_rels/document.xml.rels';
  const documentXml = await zip.file(documentPath).async('string');
  let relationshipsXml = await zip.file(relationshipsPath).async('string');
  const usedRelationshipIds = new Set(
    [...documentXml.matchAll(/r:embed="([^"]+)"/g)].map((match) => match[1]),
  );

  const imageRelationshipPattern = /\s*<Relationship\b[^>]*\bType="[^"]*\/image"[^>]*\/>/g;
  relationshipsXml = relationshipsXml.replace(imageRelationshipPattern, (relationship) => {
    const id = relationship.match(/\bId="([^"]+)"/i)?.[1];
    const target = relationship.match(/\bTarget="([^"]+)"/i)?.[1];
    if (!id || !target || usedRelationshipIds.has(id)) return relationship;
    zip.remove(`word/${target}`);
    return '';
  });
  zip.file(relationshipsPath, relationshipsXml);

  const cleanedBuffer = await zip.generateAsync({
    type: 'nodebuffer',
    compression: 'DEFLATE',
    compressionOptions: { level: 9 },
  });
  fs.writeFileSync(outputPath, cleanedBuffer);
  console.log(outputPath);
})();
