import fs from 'node:fs';
import path from 'node:path';
import { createRequire } from 'node:module';

const require = createRequire(import.meta.url);
const markedPath = process.env.MARKED_MODULE
  || '/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/marked';
const { marked } = require(markedPath);

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../..');
const SKILL_ROOT = path.join(ROOT, '.agents/skills/frontend-slides');
const FONT_ROOT = path.join(ROOT, '.claude/skills/doc-design/assets/fonts');
const [markdownPath, outputPath] = process.argv.slice(2);

if (!markdownPath || !outputPath) {
  throw new Error('Usage: node render-executive-frontend-deck.mjs <deck.md> <deck.html>');
}

const source = fs.readFileSync(markdownPath, 'utf8');
const sourceDir = path.dirname(path.resolve(markdownPath));
const viewportCss = fs.readFileSync(path.join(SKILL_ROOT, 'viewport-base.css'), 'utf8');
const font = (name) => fs.readFileSync(path.join(FONT_ROOT, name), 'utf8').trim();
const rawSlides = source.split(/\n---\n/g).map((slide) => slide.trim()).filter(Boolean);

const externalSources = {
  3: [
    ['Consumer Credit Act implementation', 'https://www.skp.gov.my/en/news/media-releases/enforcement-of-the-consumer-credit-act-2025-and-the-establishment-of-the-consumer-credit-commission'],
    ['SKP authorisation and conduct standards', 'https://www.skp.gov.my/en/news/media-releases/suruhanjaya-kredit-pengguna-issues-authorisation-standards-and-conduct-standards-to-guide-consumer-credit-sector'],
  ],
  4: [
    ['TEKUN Corporation collection service', 'https://www.tcorp.com.my/ejen-kutipan-hutang/'],
    ['MOCCIS appointment', 'https://www.tcorp.com.my/majlis-pelantikan-tekun-corporation-sebagai-agensi-pemulihan-kredit-bagi-koperasi-pegawai-pegawai-melayu-malaysia-berhad-%F0%9D%90%8C%F0%9D%90%8E%F0%9D%90%82%F0%9D%90%82%F0%9D%90%88%F0%9D%90%92/'],
    ['Awqaf Education appointment', 'https://www.tcorp.com.my/majlis-menandatangani-memorandum-persefahaman-mou-antara-awqaf-education-sdn-bhd-dengan-tekun-corporation-sdn-bhd-dan-pelantikan-tekun-corporation-sebagai-agensi-kutipan-hutang-untuk-awqaf-education/'],
  ],
  11: [
    ['SKP debt collection guidance', 'https://www.skp.gov.my/en/industries/debt-collection'],
    ['SKP Conduct Standards v1.0', 'https://www.skp.gov.my/clients/asset_491D1974-0435-41A4-B496-CE4A33AAED50/contentms/img/pdf/Conduct_Standards_v1.0.pdf'],
  ],
  15: [
    ['TEKUN Corporation collection service', 'https://www.tcorp.com.my/ejen-kutipan-hutang/'],
    ['MOCCIS contract announcement', 'https://www.tcorp.com.my/majlis-menandatangani-kontrak-perjanjian-perkhidmatan-pengurusan-dan-pemulihan-kredit-antara-koperasi-pegawai-pegawai-melayu-malaysia-berhad-moccis-dengan-tekun-corporation-sdn-bhd/'],
  ],
};

function commentValue(slide, key) {
  return slide.match(new RegExp(`<!--\\s*${key}:\\s*([\\s\\S]*?)\\s*-->`, 'i'))?.[1]?.trim() || '';
}

function escapeHtml(value) {
  return value.replace(/[&<>"']/g, (char) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[char]));
}

function decorate(body) {
  return body
    .replace(/<(h1|h2|p|ul|ol|table|blockquote|figure)(\s|>)/g, '<$1 class="reveal"$2')
    .replace(/<a /g, '<a target="_blank" rel="noopener noreferrer" ');
}

function sourceLinks(index) {
  return (externalSources[index] || [])
    .map(([label, url]) => `<a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`)
    .join('');
}

function nativeVisual(layout, number) {
  const arrows = (items, className = '') => `<div class="diagram-row ${className}">${items.map((item, index) => `${index ? '<span class="diagram-arrow" aria-hidden="true">→</span>' : ''}<div class="diagram-node">${item}</div>`).join('')}</div>`;
  const diagrams = {
    'impact-chain': arrows(['Connected intake', 'Guided work', 'Verified outcomes', 'Reconciled reporting', 'Sustainable contribution']),
    lifecycle: `<div class="diagram-stack">${arrows(['Intake', 'Validate', 'Segment', 'Assign', 'Notify'])}${arrows(['Verify', 'Engage', 'Outcome', 'Reconcile', 'Close and improve'])}<div class="diagram-branch">Protected routes: dispute · hardship · vulnerability · complaint · legal hold</div></div>`,
    architecture: `<div class="architecture-stack">${['Experience and authorised views', 'Portfolio, customer, case and policy records', 'Controlled interaction and workflow', 'Payment evidence and reconciliation', 'Performance, risk and service intelligence'].map((item, index) => `<div class="architecture-layer"><span>${index + 1}</span>${item}</div>`).join('')}<div class="architecture-spine">Trust, identity, access and audit support every layer</div></div>`,
    pilot: `<div class="diagram-stack">${arrows(['Discover', 'Baseline', 'Configure controls', 'Run bounded pilot', 'Measure evidence'])}<div class="pilot-outcomes"><div><strong>Expand</strong><span>Evidence accepted</span></div><div><strong>Adjust</strong><span>Re-baseline and repeat</span></div><div><strong>Stop safely</strong><span>Guardrail not met</span></div></div></div>`,
    roadmap: arrows(['H0<br>Align', 'H1<br>Foundation', 'H2<br>Pilot', 'H3<br>Scale', 'H4<br>Multi-principal', 'H5<br>Intelligence'], 'roadmap-diagram'),
    'value-ladder': `<div class="value-stair">${['Foundation value', 'Operating value', 'Growth value', 'Compounding value'].map((item, index) => `<div class="value-step step-${index + 1}"><span>${index + 1}</span>${item}</div>`).join('')}</div>`,
  };
  return diagrams[layout] ? `<figure class="visual native-diagram reveal" aria-label="Diagram for slide ${number}">${diagrams[layout]}</figure>` : '';
}

const wideLayouts = new Set(['impact-chain', 'lifecycle', 'pilot', 'roadmap', 'value-ladder']);
const slides = rawSlides.map((raw, index) => {
  const number = index + 1;
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
    body = `${h1}<div class="partnership-grid">${groups.map((group, groupIndex) => `<article class="partnership-col responsibility-${groupIndex + 1} reveal">${group}</article>`).join('')}</div>`;
  }

  if (layout === 'two-column') {
    const h1 = body.match(/<h1[\s\S]*?<\/h1>/)?.[0] || '';
    const remainder = body.slice(h1.length);
    const closingNote = remainder.match(/<p><strong>Important:<\/strong>[\s\S]*?<\/p>\s*$/)?.[0] || '';
    const sections = remainder
      .slice(0, closingNote ? -closingNote.length : undefined)
      .match(/<h2[\s\S]*?(?=<h2|$)/g) || [];
    body = `${h1}<div class="two-column-grid">${sections.map((section) => `<article class="two-column-panel reveal">${section}</article>`).join('')}</div>${closingNote}`;
  }

  let visualHtml = nativeVisual(layout, number);
  if (visual && !visualHtml) {
    const visualPath = path.resolve(sourceDir, visual);
    if (fs.existsSync(visualPath)) {
      const svg = fs.readFileSync(visualPath, 'utf8')
        .replace(/^<\?xml[^>]*>\s*/i, '')
        .replace(/<!DOCTYPE[^>]*>\s*/i, '');
      visualHtml = `<figure class="visual reveal" aria-label="Diagram for slide ${number}">${svg}</figure>`;
    }
  }

  const external = sourceLinks(number);
  const sourceDrawer = (sources || external) ? `
    <aside class="source-drawer" aria-label="Sources for slide ${number}">
      <div class="source-drawer-head"><strong>Evidence trail</strong><button class="source-close" type="button" aria-label="Close sources">Close</button></div>
      ${sources ? `<p>Governed source: ${escapeHtml(sources)}</p>` : ''}
      ${external ? `<div class="source-links">${external}</div>` : ''}
      <p class="source-note">Public sources reverified 1 September 2026. Final legal applicability remains portfolio-specific.</p>
    </aside>` : '';

  const classNames = [
    'slide',
    `layout-${layout}`,
    visualHtml ? 'has-visual' : '',
    wideLayouts.has(layout) ? 'visual-wide' : '',
    index === 0 ? 'active visible' : '',
  ].filter(Boolean).join(' ');

  return `<section class="${classNames}" data-slide="${number}" aria-label="Slide ${number} of ${rawSlides.length}">
    <div class="atmosphere" aria-hidden="true"></div>
    <header class="slide-header"><span>TEKUN Corporation</span><span>Integrated Collection Growth Partnership</span></header>
    <div class="slide-body"><div class="content">${decorate(body)}</div>${visualHtml}</div>
    <footer class="slide-footer">
      ${(sources || external) ? `<button class="source-trigger" type="button">Evidence and sources</button>` : '<span>Governed proposal</span>'}
      <span>${String(number).padStart(2, '0')} / ${String(rawSlides.length).padStart(2, '0')}</span>
    </footer>
    ${notes ? `<aside class="speaker-notes">${escapeHtml(notes)}</aside>` : ''}
    ${sourceDrawer}
  </section>`;
});

const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="description" content="TEKUN Corporation Integrated Collection Growth Partnership executive presentation">
<title>TEKUN Corporation | Integrated Collection Growth Partnership</title>
<style>
@font-face{font-family:Archivo;src:url(data:font/woff2;base64,${font('archivo-600.b64')}) format('woff2');font-weight:600;font-style:normal;font-display:swap}
@font-face{font-family:Archivo;src:url(data:font/woff2;base64,${font('archivo-700.b64')}) format('woff2');font-weight:700;font-style:normal;font-display:swap}
@font-face{font-family:Plex;src:url(data:font/woff2;base64,${font('plex-400.b64')}) format('woff2');font-weight:400;font-style:normal;font-display:swap}
@font-face{font-family:Plex;src:url(data:font/woff2;base64,${font('plex-600.b64')}) format('woff2');font-weight:600;font-style:normal;font-display:swap}
:root{
  --stage-bg:#071b29;--slide-bg:#fbfaf6;--navy:#102f49;--navy-2:#0a2030;
  --teal:#008d80;--teal-bright:#13b8a5;--teal-soft:#e6f5f1;--sand:#e9c96d;
  --paper:#fbfaf6;--ink:#172033;--muted:#64737d;--line:#cfdbdc;
  --display:Archivo,sans-serif;--body:Plex,sans-serif;--ease:cubic-bezier(.16,1,.3,1);
}
*{box-sizing:border-box}
${viewportCss}
button,a{font:inherit}
.slide{color:var(--ink);font-family:var(--body);padding:118px 130px 100px;background:
  linear-gradient(135deg,rgba(0,141,128,.045),transparent 34%),var(--paper)}
.slide::before{content:"";position:absolute;left:0;top:0;width:22px;height:100%;background:linear-gradient(180deg,var(--sand),var(--teal))}
.atmosphere{position:absolute;inset:0;pointer-events:none;background-image:
  linear-gradient(rgba(16,47,73,.035) 1px,transparent 1px),
  linear-gradient(90deg,rgba(16,47,73,.035) 1px,transparent 1px);background-size:48px 48px;
  mask-image:linear-gradient(135deg,transparent 15%,#000 80%)}
.slide-header{position:absolute;top:42px;left:130px;right:130px;display:flex;justify-content:space-between;
  padding-bottom:18px;border-bottom:2px solid rgba(16,47,73,.16);font:600 18px/1 var(--display);
  letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.slide-body{position:relative;height:100%;display:flex;flex-direction:column;justify-content:center;z-index:1}
.content{min-width:0;max-width:1640px}
h1{margin:0 0 38px;font:700 64px/1.03 var(--display);letter-spacing:-.035em;color:var(--navy);max-width:1520px}
h2{margin:22px 0 12px;font:600 31px/1.12 var(--display);color:var(--navy)}
p,li,td,th{font-size:25px;line-height:1.38}
p{margin:12px 0 22px}ul,ol{margin:14px 0 22px;padding-left:34px}li{margin:10px 0;padding-left:6px}
strong{color:var(--navy)}
blockquote{margin:26px 0;padding:26px 30px;background:var(--teal-soft);border-radius:18px;color:var(--navy);position:relative}
blockquote::before{content:"";position:absolute;left:0;top:0;bottom:0;width:8px;background:var(--teal);border-radius:18px 0 0 18px}
blockquote p{font:600 30px/1.35 var(--display);margin:0}
table{width:100%;border-collapse:separate;border-spacing:0;margin:18px 0;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#fff}
th{background:var(--navy);color:#fff;text-align:left;font-weight:600}th,td{padding:16px 19px;border-bottom:1px solid var(--line);vertical-align:top;font-size:19px;line-height:1.28}
tr:last-child td{border-bottom:0}tr:nth-child(even) td{background:#f0f6f4}
.slide-footer{position:absolute;left:130px;right:130px;bottom:34px;display:flex;justify-content:space-between;align-items:center;
  color:var(--muted);font:600 16px/1 var(--display);letter-spacing:.05em;text-transform:uppercase;z-index:4}
.source-trigger{border:0;background:none;color:var(--teal);padding:8px 0;cursor:pointer;border-bottom:1px solid currentColor}
.speaker-notes{display:none}
.reveal{opacity:0;transform:translateY(24px);transition:opacity .55s var(--ease),transform .55s var(--ease)}
.slide.visible .reveal{opacity:1;transform:translateY(0)}
.slide.visible .reveal:nth-child(2){transition-delay:.08s}.slide.visible .reveal:nth-child(3){transition-delay:.16s}.slide.visible .reveal:nth-child(4){transition-delay:.24s}
.has-visual .slide-body{display:grid;grid-template-columns:minmax(0,1.02fr) minmax(0,.98fr);gap:70px;align-items:center}
.visual{margin:0;display:flex;align-items:center;justify-content:center;padding:30px;background:rgba(255,255,255,.82);border:1px solid var(--line);border-radius:24px;box-shadow:0 24px 60px rgba(16,47,73,.1)}
.visual svg{width:100%;height:auto;max-height:620px}
.native-diagram{min-height:230px}.diagram-row{width:100%;display:flex;align-items:center;justify-content:center;gap:12px}
.diagram-node{min-width:0;flex:1;padding:20px 14px;border:1px solid #22aa9e;border-radius:12px;background:var(--teal-soft);color:var(--navy);font:700 19px/1.2 var(--display);text-align:center}
.diagram-arrow{flex:0 0 auto;color:var(--teal);font:700 27px/1 var(--display)}.diagram-stack{width:100%;display:grid;gap:15px}
.diagram-branch{padding:12px 18px;border-radius:10px;background:var(--sand-soft);color:var(--navy);font:700 17px/1.2 var(--display);text-align:center}
.architecture-stack{width:100%;display:grid;gap:10px}.architecture-layer{display:flex;align-items:center;gap:16px;padding:13px 18px;border:1px solid #22aa9e;border-radius:10px;background:linear-gradient(90deg,var(--teal-soft),#fff);font:700 18px/1.2 var(--display)}
.architecture-layer span{display:grid;place-items:center;width:31px;height:31px;border-radius:50%;background:var(--teal);color:#fff}.architecture-spine{padding:13px 18px;border-radius:10px;background:var(--navy);color:#fff;font:700 16px/1.2 var(--display);text-align:center}
.pilot-outcomes{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.pilot-outcomes>div{padding:14px;border-radius:10px;background:#fff;border:1px solid var(--line);text-align:center}.pilot-outcomes strong,.pilot-outcomes span{display:block}.pilot-outcomes strong{color:var(--teal);font:700 19px/1.1 var(--display)}.pilot-outcomes span{margin-top:5px;font-size:15px}
.roadmap-diagram .diagram-node{font-size:17px;padding:16px 9px}.value-stair{width:100%;height:210px;display:grid;grid-template-columns:repeat(4,1fr);gap:18px;align-items:end}.value-step{display:flex;flex-direction:column;justify-content:center;align-items:center;padding:14px;border-radius:12px 12px 3px 3px;background:linear-gradient(180deg,var(--teal-soft),#cdece7);border:1px solid #22aa9e;color:var(--navy);font:700 20px/1.2 var(--display);text-align:center}.value-step span{margin-bottom:8px;color:var(--teal);font-size:17px}.value-step.step-1{height:86px}.value-step.step-2{height:116px}.value-step.step-3{height:148px}.value-step.step-4{height:180px;background:linear-gradient(180deg,#d9f6f1,#a8ddd4)}
.visual-wide .slide-body{display:grid;grid-template-columns:1fr;grid-template-rows:auto 1fr;gap:24px;align-content:center}
.visual-wide .content{max-width:100%}.visual-wide .content h1{margin-bottom:20px}.visual-wide .content li{font-size:21px;margin:6px 0}
.visual-wide .visual{padding:20px 26px}.visual-wide .visual svg{max-height:350px}
.layout-cover{padding:150px 150px;background:radial-gradient(circle at 82% 18%,rgba(19,184,165,.42),transparent 30%),linear-gradient(135deg,#081c2b,#0c4c59 64%,#008d80);color:#fff}
.layout-cover::before{width:30px;background:var(--sand)}
.layout-cover .atmosphere{opacity:.24;background-size:64px 64px;mask-image:linear-gradient(90deg,transparent,#000)}
.layout-cover .slide-header{border-color:rgba(255,255,255,.22);color:rgba(255,255,255,.72)}
.layout-cover .slide-body{justify-content:center;max-width:1420px}.layout-cover h1{font-size:95px;color:#fff;max-width:1250px;margin-bottom:32px}
.layout-cover h2{font-size:46px;color:#d6fff8;max-width:1420px}.layout-cover .content>p{font-size:19px;line-height:1.55;color:rgba(255,255,255,.78);margin:52px 0 0}
.layout-cover .content>p:first-of-type{font-size:27px;max-width:1380px;color:#d6fff8}.layout-cover strong{color:inherit}
.layout-cover .slide-footer{color:rgba(255,255,255,.65)}
.layout-statement .slide-body{align-items:center;text-align:center}.layout-statement .content{max-width:1320px}.layout-statement h1{font-size:50px;margin:0 auto 50px}
.layout-statement blockquote{padding:54px 72px}.layout-statement blockquote p{font-size:43px;line-height:1.28}.layout-statement .content>p{font-size:22px;color:var(--muted)}
.layout-two-column .content{display:block}.two-column-grid{display:grid;grid-template-columns:1fr 1fr;gap:32px}
.two-column-panel{padding:26px 30px 28px;background:#fff;border:1px solid var(--line);border-radius:18px;box-shadow:0 16px 38px rgba(16,47,73,.06)}
.layout-two-column h2{margin:0 0 15px}.layout-two-column ul{margin:0;padding-left:28px}
.layout-two-column li{font-size:22px;line-height:1.3;margin:7px 0}
.layout-two-column .content>p{margin-top:32px;padding:18px 24px;background:var(--teal-soft);border-radius:14px;font-size:20px}
.layout-partnership .slide-body{display:block}.partnership-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:30px}
.partnership-col{min-height:510px;padding:34px 34px 30px;background:#fff;border:1px solid var(--line);border-radius:22px;position:relative;overflow:hidden}
.partnership-col::before{content:"";position:absolute;left:0;right:0;top:0;height:11px;background:var(--teal)}
.partnership-col.responsibility-2::before{background:var(--navy)}.partnership-col.responsibility-3::before{background:var(--sand)}
.partnership-col h2{font-size:31px}.partnership-col li{font-size:21px;line-height:1.34}
.layout-service ul,.layout-guardrails ul,.layout-proof ul{display:grid;grid-template-columns:1fr 1fr;gap:16px 22px;padding:0;list-style:none}
.layout-service li,.layout-guardrails li,.layout-proof li{margin:0;padding:20px 22px 20px 54px;background:#fff;border:1px solid var(--line);border-radius:14px;position:relative;font-size:22px}
.layout-service li::before,.layout-guardrails li::before,.layout-proof li::before{content:"✓";position:absolute;left:19px;color:var(--teal);font-weight:700}
.layout-ownership .content>ul{display:grid;grid-template-columns:1fr 1fr;gap:12px 24px}.layout-ownership blockquote{margin-top:30px}
.layout-milestone:not(:has(table)) .content>ul{list-style:none;padding:0;display:grid;grid-template-columns:repeat(4,1fr);gap:20px}
.layout-milestone:not(:has(table)) .content>ul li{padding:26px 24px;background:#fff;border:1px solid var(--line);border-top:8px solid var(--teal);border-radius:14px;font-size:21px;min-height:190px}
.layout-roadmap .content{display:grid;grid-template-columns:repeat(3,1fr);gap:18px 22px}.layout-roadmap h1{grid-column:1/-1}
.layout-roadmap .content>p{margin:0;padding:20px 22px;background:#fff;border:1px solid var(--line);border-radius:14px;font-size:19px}.layout-roadmap .content>p strong{display:block;font:700 23px/1.1 var(--display);margin-bottom:7px}
.layout-roadmap .visual{grid-row:2;padding:16px}.layout-roadmap .visual svg{max-height:260px}
.layout-decision{background:radial-gradient(circle at 86% 16%,rgba(19,184,165,.18),transparent 30%),linear-gradient(145deg,#fbfaf6,#edf8f4)}
.layout-decision .content{max-width:1480px}.layout-decision h1{font-size:72px}.layout-decision h2{font-size:37px;color:var(--teal)}
.layout-decision ol{display:grid;grid-template-columns:1fr 1fr;gap:10px 50px}.layout-decision li{font-size:21px}.layout-decision blockquote p{font-size:25px}
.source-drawer{position:absolute;right:0;top:0;width:720px;height:100%;padding:82px 64px;background:rgba(7,27,41,.98);color:#eafffb;z-index:20;transform:translateX(100%);transition:transform .45s var(--ease);box-shadow:-30px 0 80px rgba(0,0,0,.25)}
.source-drawer.open{transform:translateX(0)}.source-drawer-head{display:flex;justify-content:space-between;align-items:center;font:600 29px/1.2 var(--display);margin-bottom:40px}
.source-close{border:1px solid rgba(255,255,255,.35);border-radius:999px;padding:10px 18px;color:#fff;background:transparent;cursor:pointer}
.source-drawer p{font-size:21px;color:#d5e5e8}.source-links{display:grid;gap:16px;margin:28px 0}.source-links a{color:#87e7db;font-size:21px;line-height:1.32}
.source-note{padding-top:24px;border-top:1px solid rgba(255,255,255,.2);font-size:18px!important}
.deck-controls{display:flex;align-items:center;gap:10px;padding:9px 12px;background:rgba(7,27,41,.86);border:1px solid rgba(255,255,255,.18);border-radius:999px;backdrop-filter:blur(14px);color:#fff}
.deck-controls button{width:42px;height:42px;border:0;border-radius:50%;background:transparent;color:#fff;cursor:pointer;font-size:20px}.deck-controls button:hover{background:rgba(255,255,255,.13)}
.deck-controls .deck-count{min-width:76px;text-align:center;font:600 14px/1 var(--display);letter-spacing:.06em}
.progress-track{position:fixed;left:0;right:0;bottom:0;height:5px;background:rgba(255,255,255,.12);z-index:1001}.progress-bar{height:100%;width:0;background:linear-gradient(90deg,var(--sand),var(--teal-bright));transition:width .35s var(--ease)}
@media print{
  @page{size:13.333in 7.5in;margin:0}.slide{padding:118px 130px 100px}.reveal{opacity:1!important;transform:none!important}.source-drawer,.progress-track{display:none!important}
}
</style>
</head>
<body>
<div class="deck-viewport"><main class="deck-stage" id="deckStage">${slides.join('\n')}</main></div>
<nav class="deck-controls" aria-label="Presentation controls">
  <button id="prevSlide" type="button" aria-label="Previous slide">←</button>
  <span class="deck-count" id="deckCount">01 / ${String(rawSlides.length).padStart(2, '0')}</span>
  <button id="nextSlide" type="button" aria-label="Next slide">→</button>
  <button id="fullScreen" type="button" aria-label="Toggle full screen">⛶</button>
</nav>
<div class="progress-track" aria-hidden="true"><div class="progress-bar" id="progressBar"></div></div>
<script>
class SlidePresentation{
  constructor(){
    this.slides=[...document.querySelectorAll('.slide')];this.stage=document.getElementById('deckStage');
    this.current=Math.max(0,Math.min(this.slides.length-1,Number(location.hash.replace('#slide-',''))-1||0));
    this.wheelLocked=false;this.touchStart=null;this.bind();this.scale();this.show(this.current,false);
  }
  bind(){
    addEventListener('resize',()=>this.scale());
    document.getElementById('prevSlide').addEventListener('click',()=>this.show(this.current-1));
    document.getElementById('nextSlide').addEventListener('click',()=>this.show(this.current+1));
    document.getElementById('fullScreen').addEventListener('click',()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen());
    document.addEventListener('keydown',(event)=>{
      if(['ArrowRight','ArrowDown','PageDown',' '].includes(event.key)){event.preventDefault();this.show(this.current+1)}
      if(['ArrowLeft','ArrowUp','PageUp'].includes(event.key)){event.preventDefault();this.show(this.current-1)}
      if(event.key==='Home')this.show(0);if(event.key==='End')this.show(this.slides.length-1);
      if(event.key==='Escape')this.closeSources();
    });
    document.addEventListener('wheel',(event)=>{if(this.wheelLocked||Math.abs(event.deltaY)<20)return;this.wheelLocked=true;this.show(this.current+(event.deltaY>0?1:-1));setTimeout(()=>this.wheelLocked=false,550)},{passive:true});
    document.addEventListener('touchstart',(event)=>{this.touchStart=event.changedTouches[0].clientX},{passive:true});
    document.addEventListener('touchend',(event)=>{if(this.touchStart===null)return;const delta=event.changedTouches[0].clientX-this.touchStart;if(Math.abs(delta)>55)this.show(this.current+(delta<0?1:-1));this.touchStart=null},{passive:true});
    document.querySelectorAll('.source-trigger').forEach((button)=>button.addEventListener('click',(event)=>event.currentTarget.closest('.slide').querySelector('.source-drawer')?.classList.add('open')));
    document.querySelectorAll('.source-close').forEach((button)=>button.addEventListener('click',(event)=>event.currentTarget.closest('.source-drawer').classList.remove('open')));
  }
  scale(){const factor=Math.min(innerWidth/1920,innerHeight/1080);const x=(innerWidth-1920*factor)/2;const y=(innerHeight-1080*factor)/2;this.stage.style.transform=\`translate(\${x}px,\${y}px) scale(\${factor})\`}
  closeSources(){document.querySelectorAll('.source-drawer.open').forEach((drawer)=>drawer.classList.remove('open'))}
  show(index,updateHash=true){this.closeSources();this.current=Math.max(0,Math.min(index,this.slides.length-1));this.slides.forEach((slide,i)=>{slide.classList.toggle('active',i===this.current);slide.classList.toggle('visible',i===this.current)});const number=this.current+1;document.getElementById('deckCount').textContent=String(number).padStart(2,'0')+' / '+String(this.slides.length).padStart(2,'0');document.getElementById('progressBar').style.width=(number/this.slides.length*100)+'%';if(updateHash)history.replaceState(null,'','#slide-'+number)}
}
new SlidePresentation();
</script>
</body>
</html>`;

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, html);
console.log(`${outputPath}\nslides=${slides.length}\nmode=fixed-stage-interactive`);
