// Local document renderer, not an application build. Reuses the existing
// TEKUN pipeline's installed Markdown parser and the approved local browser.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const renderDOCX = require('./render-document-docx.cjs');
const { marked } = require('/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/marked');
const { chromium } = require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');

const root = __dirname;
const sourcePath = path.join(root, 'external-kota-buku-document.md');
const output = path.join(root, 'external-kota-buku-editions');
const source = fs.readFileSync(sourcePath, 'utf8');
if (/<script|file:\/\/|\/Users\/|fal\.env|SEPADU-v1|redONE|STNN|\bRM\s*\d|\$\s*\d/i.test(source)) throw Error('Source disclosure preflight failed');
const sections = [...source.matchAll(/<!-- language: (en|ms) -->\n([\s\S]*?)(?=<!-- language: |$)/g)];
if (sections.length !== 2) throw Error('Expected exactly two language sources');
const css = fs.readFileSync(path.join(root, 'external-document.css'), 'utf8');
// Only the three reviewed house-font rules are read from our own old sample.
// No slide markup, copy or Claude asset enters this document.
const fontSource = fs.readFileSync(path.join(root, 'visual-samples/codex/sequence.html'), 'utf8');
const fonts = (fontSource.match(/@font-face\{[^}]+\}/g) || []).slice(0, 3).join('\n');
if (!fonts.includes('base64')) throw Error('Offline house fonts missing');
const esc = s => s.replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const editions = {};
for (const [, lang, md] of sections) {
  const title = md.match(/^# (.+)$/m)[1];
  const start = md.indexOf('## 1. ');
  const prelude = md.slice(0, start);
  const chapters = md.slice(start).split(/(?=^## )/m).filter(Boolean);
  if (chapters.length !== 15) throw Error('Expected 12 chapters and 3 appendices: ' + lang);
  const nav = [];
  const body = chapters.map((chapter, i) => {
    const heading = chapter.match(/^## (.+)$/m)[1];
    const id = i < 12 ? `e${String(i + 1).padStart(2, '0')}` : `appendix-${'abc'[i - 12]}`;
    nav.push({ id, heading });
    return `<section class="chapter" id="${lang}-${id}" data-chapter="${id}">${marked.parse(chapter)}</section>`;
  }).join('\n');
  editions[lang] = { title, nav, md, html: `<article lang="${lang}" data-edition="${lang}"><header class="cover" id="${lang}-cover">${marked.parse(prelude)}</header>${body}</article>` };
}
function documentHTML(lang, bilingual) {
  const e = editions[lang];
  const labels = lang === 'en' ? ['Contents', 'Print / save PDF', 'Discussion draft · not approved for distribution'] : ['Kandungan', 'Cetak / simpan PDF', 'Draf perbincangan · belum diluluskan untuk edaran'];
  const navs = Object.entries(editions).filter(([l]) => bilingual || l === lang).map(([l, ed]) => `<nav data-nav="${l}" aria-label="${l === 'en' ? 'Contents' : 'Kandungan'}" ${l !== lang ? 'hidden' : ''}><a class="home" href="#${l}-cover">${l === 'en' ? 'Overview' : 'Gambaran keseluruhan'}</a>${ed.nav.map(n => `<a href="#${l}-${n.id}">${esc(n.heading)}</a>`).join('')}</nav>`).join('');
  const content = bilingual ? Object.values(editions).map(ed => ed.html).join('\n') : e.html;
  const controls = bilingual ? `<div class="languages" aria-label="Language / Bahasa"><button type="button" data-language="en" aria-pressed="${lang === 'en'}">English</button><button type="button" data-language="ms" aria-pressed="${lang === 'ms'}">BM</button></div>` : '';
  const script = bilingual ? `<script>
function setLanguage(lang) {
  if (!['en','ms'].includes(lang)) return;
  const old = document.documentElement.lang;
  const hash = location.hash.replace('#'+old+'-', '');
  document.documentElement.lang=lang;
  document.title=lang==='en'?'More time for teaching | Kota Buku':'Lebih masa untuk mengajar | Kota Buku';
  document.querySelectorAll('[data-edition]').forEach(a=>a.hidden=a.dataset.edition!==lang);
  document.querySelectorAll('[data-nav]').forEach(n=>n.hidden=n.dataset.nav!==lang);
  document.querySelectorAll('[data-language]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.language===lang)));
  document.querySelector('#contents-label').textContent=lang==='en'?'Contents':'Kandungan';
  document.querySelector('#print-button').textContent=lang==='en'?'Print / save PDF':'Cetak / simpan PDF';
  document.querySelector('#draft-label').textContent=lang==='en'?'Discussion draft · not approved for distribution':'Draf perbincangan · belum diluluskan untuk edaran';
  document.querySelector('.skip').textContent=lang==='en'?'Skip to document':'Terus ke dokumen';
  document.querySelector('.skip').href='#'+lang+'-cover';
  try {localStorage.setItem('kota-buku-document-language',lang)} catch(e) {}
  if(hash && !hash.startsWith('#')) {const target=document.getElementById(lang+'-'+hash);if(target){history.replaceState(null,'','#'+target.id);target.scrollIntoView();}}
}
document.querySelectorAll('[data-language]').forEach(b=>b.addEventListener('click',()=>setLanguage(b.dataset.language)));
document.querySelector('#print-button').addEventListener('click',()=>window.print());
let initial='${lang}';try{initial=localStorage.getItem('kota-buku-document-language')||initial}catch(e){}setLanguage(initial);
</script>` : '<script>document.querySelector("#print-button").addEventListener("click",()=>window.print());</script>';
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="author" content="Sifututor"><title>${esc(e.title)} | Kota Buku</title><style>${fonts}\n${css}\n${bilingual ? 'article[lang="ms"]{display:none}html[lang="ms"] article[lang="ms"]{display:block}html[lang="ms"] article[lang="en"]{display:none}' : ''}</style></head><body><a class="skip" href="#${lang}-cover">${lang==='en'?'Skip to document':'Terus ke dokumen'}</a><div class="toolbar"><span class="brand">Sifututor <span>×</span> Learnest Lab</span>${controls}<button id="print-button" type="button">${labels[1]}</button></div><aside class="toc"><details open><summary id="contents-label">${labels[0]}</summary>${navs}</details></aside><main>${content}</main><footer id="draft-label">${labels[2]}</footer>${script}</body></html>`;
}

(async () => {
  fs.mkdirSync(output, { recursive: true });
  fs.writeFileSync(path.join(output, 'kota-buku-document.html'), documentHTML('en', true));
  const browser = await chromium.launch({ channel: 'chrome', headless: true });
  try {
    for (const lang of ['en', 'ms']) {
      const filename = `kota-buku-document-${lang}`;
      const htmlPath = path.join(output, filename + '.html');
      fs.writeFileSync(htmlPath, documentHTML(lang, false));
      const page = await browser.newPage();
      await page.goto('file://' + htmlPath);
      await page.evaluate(() => document.fonts.ready);
      await page.pdf({ path: path.join(output, filename + '.pdf'), format: 'A4', printBackground: true, preferCSSPageSize: true, tagged: true, outline: true,
        displayHeaderFooter: true, headerTemplate: '<div></div>', footerTemplate: '<div style="font-family:Arial;font-size:8px;color:#626b73;width:100%;padding:0 16mm;display:flex;justify-content:space-between"><span>Sifututor · Learnest Lab · 07.09.2026</span><span><span class="pageNumber"></span> / <span class="totalPages"></span></span></div>' });
      // Keep an inspection HTML for the editable content; OOXML rendering
      // preserves tables/headings that the native text converter flattened.
      const docxInput = path.join(output, filename + '-editable.html');
      const editable = `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><title>${esc(editions[lang].title)}</title><style>body{font-family:Arial;font-size:11pt;line-height:1.4}h1{font-size:30pt;color:#153e3b}h2{font-size:18pt;color:#153e3b}h3{font-size:13pt}table{border-collapse:collapse;width:100%}th,td{border:1px solid #d9e0e0;padding:7px;font-size:10pt}th{background:#eaf1ee}blockquote{background:#f2f6f3;padding:12px}p{margin-bottom:10px}</style></head><body>${editions[lang].html}</body></html>`;
      fs.writeFileSync(docxInput, editable);
      const docxShape=renderDOCX(editions[lang].md,lang,editions[lang].title,path.join(output,filename+'.docx'));
      const expectedTables=marked.lexer(editions[lang].md).filter(t=>t.type==='table').length;
      if(docxShape.tables!==expectedTables||docxShape.headings!==15)throw Error('DOCX structural check: '+JSON.stringify(docxShape));
      await page.close();
      console.log(lang + ': HTML / PDF / DOCX generated');
    }
  } finally { await browser.close(); }
  const hash = p => crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
  const manifest = { source: path.basename(sourcePath), sourceSHA256: hash(sourcePath), rendererSHA256: hash(__filename), docxRendererSHA256: hash(path.join(root,'render-document-docx.cjs')), cssSHA256: hash(path.join(root, 'external-document.css')), generatedAt: new Date().toISOString(), outputSHA256: {} };
  for (const name of fs.readdirSync(output).filter(n => /\.(html|pdf|docx)$/.test(n))) manifest.outputSHA256[name] = hash(path.join(output,name));
  fs.writeFileSync(path.join(output,'build-manifest.json'),JSON.stringify(manifest,null,2)+'\n');
})().catch(e => { console.error(e); process.exit(1); });
