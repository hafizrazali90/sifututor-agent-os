import fs from 'node:fs';
import path from 'node:path';

const [markdownPath, outputDir] = process.argv.slice(2);

if (!markdownPath || !outputDir) {
  throw new Error('Usage: node extract-mermaid.mjs <source.md> <output-directory>');
}

const markdown = fs.readFileSync(markdownPath, 'utf8');
const diagrams = [...markdown.matchAll(/```mermaid\n([\s\S]*?)\n```/g)].map(match => match[1]);
fs.mkdirSync(outputDir, { recursive: true });

diagrams.forEach((diagram, index) => {
  fs.writeFileSync(path.join(outputDir, `diagram-${index + 1}.mmd`), `${diagram}\n`);
});

console.log(diagrams.length);
