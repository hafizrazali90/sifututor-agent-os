// Local navigation/catalogue only. Never merges reader and restricted payloads.
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {marked}=require('/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/marked');
const root=path.resolve(__dirname,'..'), master=path.join(root,'START-HERE.md');
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
const esc=s=>s.replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const files=[];
function category(p){
 if(p.startsWith('partner/'))return 'Restricted partner source';
 if(p.startsWith('sources/'))return 'Preserved research source';
 if(p.includes('/claude/'))return /(?:kota-buku-deck(?:-share|-en|-bm)?|Kota-Buku-App-Proposal(?:-EN|-BM)?)\.(html|pdf)$/.test(p)?'Current full deck / partner copy':'Claude samples / authoring history';
 if(p.includes('/codex/'))return 'Superseded Codex samples';
 if(/-editions\//.test(p))return /editable\.html$/.test(p)?'Export intermediate':'Current document editions';
 if(/(?:research-findings|product-feature-spec|technical-build-blueprint|data-collection-spec|CODEX-HANDOFF)\.md$/.test(p))return 'Research / specification / decisions';
 return 'Document master / planning / review';
}
function walk(dir){for(const e of fs.readdirSync(dir,{withFileTypes:true}).sort((a,b)=>a.name.localeCompare(b.name))){
 if(e.name.startsWith('.')||e.isSymbolicLink())continue;
 const absolute=path.join(dir,e.name),relative=path.relative(root,absolute);
 if(e.isDirectory()){walk(absolute);continue;}
 if(['START-HERE.html','DOCUMENT-INVENTORY.json'].includes(relative))continue;
 const data=fs.readFileSync(absolute),ext=path.extname(e.name).toLowerCase();
 files.push({path:relative,bytes:data.length,sha256:sha(data),readerDocument:['.md','.html','.pdf','.docx','.txt'].includes(ext),category:category(relative)});
}}
walk(root);
const md=fs.readFileSync(master,'utf8');
for(const m of md.matchAll(/\]\((?!https?:|#|mailto:)([^)]+)\)/g)){
 const target=m[1].split('#')[0];if(target==='DOCUMENT-INVENTORY.json')continue;
 if(!fs.existsSync(path.resolve(root,target)))throw Error('Missing index link: '+target);
}
// Validate the current editions without altering their diagnostic screenshots.
for(const dir of ['external-kota-buku-editions','internal-team-sourcebook-editions']){
 const base=path.join(__dirname,dir),m=JSON.parse(fs.readFileSync(path.join(base,'build-manifest.json')));
 if(sha(fs.readFileSync(path.join(__dirname,m.source)))!==m.sourceSHA256)throw Error('Stale master: '+dir);
 for(const [p,h]of Object.entries(m.outputSHA256))if(sha(fs.readFileSync(path.join(base,p)))!==h)throw Error('Stale edition: '+p);
}
const docs=files.filter(f=>f.readerDocument);
const inventory={generatedAt:new Date().toISOString(),scope:'Owner-only local catalogue; no distribution approval; remote artifacts and outside-folder references not bundled',masterSHA256:sha(md),readerDocuments:docs.length,supportingFiles:files.length-docs.length,files};
fs.writeFileSync(path.join(root,'DOCUMENT-INVENTORY.json'),JSON.stringify(inventory,null,2)+'\n');
const links=docs.map(f=>`<li data-search="${esc((f.path+' '+f.category).toLowerCase())}"><a href="${f.path.split('/').map(encodeURIComponent).join('/')}">${esc(f.path)}</a><small>${esc(f.category)}</small></li>`).join('');
const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Kota Buku — document pack</title><style>
*{box-sizing:border-box}body{margin:0;background:#f4f7f4;color:#20332f;font:17px/1.65 system-ui,sans-serif}main{max-width:1100px;margin:38px auto;padding:48px 56px;background:white;border-radius:18px}h1{font-size:46px;line-height:1.12;letter-spacing:-1.5px}h2{font-size:26px;margin-top:48px;line-height:1.3}a{color:#216854;text-underline-offset:3px;overflow-wrap:anywhere}p,li{max-width:100%}li{margin:10px 0}table{border-collapse:collapse;width:100%;font-size:15px;line-height:1.5;margin:24px 0}th,td{text-align:left;vertical-align:top;padding:14px;border-bottom:1px solid #dce3df}th{background:#edf3ee}code{font-size:.85em;overflow-wrap:anywhere}input{width:100%;font:inherit;padding:14px;border:1px solid #b3c4b8;border-radius:8px}#inventory{padding:0;list-style:none}#inventory li{padding:12px 0;border-bottom:1px solid #e4ebe5}small{display:block;color:#617065}a:focus-visible,input:focus-visible{outline:3px solid #216854;outline-offset:3px}[hidden]{display:none!important}.notice{background:#edf3ee;padding:16px 22px;border-radius:10px}@media(max-width:650px){main{margin:12px;padding:24px 20px}h1{font-size:34px}h2{font-size:23px}body{font-size:16px}table{font-size:12px}th,td{padding:8px;overflow-wrap:anywhere}}@media print{main{margin:0;padding:0}input{display:none}h2{break-after:avoid}tr{break-inside:avoid}}
</style></head><body><main><div class="notice">Internal navigation only · not an external sharing bundle</div>${marked.parse(md)}<h2>Search every local document</h2><label for="search">Search by filename or category</label><input id="search" type="search" placeholder="Try: sourcebook, restricted, deck, research"><p id="count" aria-live="polite">${docs.length} documents</p><ul id="inventory">${links}</ul></main><script>const rows=[...document.querySelectorAll('#inventory li')];document.querySelector('#search').addEventListener('input',e=>{const q=e.target.value.toLowerCase().trim();let count=0;rows.forEach(r=>{r.hidden=!r.dataset.search.includes(q);if(!r.hidden)count++});document.querySelector('#count').textContent=count+' documents';});</script></body></html>`;
const responsiveHTML=html.replace('</style>','@media(max-width:650px){table,tbody,tr,td{display:block;width:100%}thead{display:none}tr{margin:18px 0;padding:12px 14px;background:#f5f8f5;border-radius:10px}td{font-size:15px;padding:8px 0;border:0}td:first-child{font-weight:700;font-size:17px}td a{overflow-wrap:break-word}}</style>');
fs.writeFileSync(path.join(root,'START-HERE.html'),responsiveHTML);
console.log(JSON.stringify({readerDocuments:docs.length,supportingFiles:files.length-docs.length,links:'PASS',editionHashes:'PASS',output:'START-HERE.html'}));
