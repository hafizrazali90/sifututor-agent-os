const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const {execFileSync}=require('node:child_process');
const {chromium}=require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
const {marked}=require('/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/marked');
const base=__dirname,dir=path.join(base,'internal-team-sourcebook-editions');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
const normal=s=>s.normalize('NFKC').replace(/[\s\u00ad]+/g,'');
function assert(ok,message){if(!ok)throw Error(message);}
(async()=>{
 const manifest=JSON.parse(fs.readFileSync(path.join(dir,'build-manifest.json')));
 assert(manifest.sourceSHA256===sha(path.join(base,manifest.source)),'Stale master');
 assert(manifest.rendererSHA256===sha(path.join(base,'render-internal-sourcebook.cjs')),'Stale renderer');
 assert(manifest.docxRendererSHA256===sha(path.join(base,'render-document-docx.cjs')),'Stale DOCX renderer');
 assert(manifest.cssSHA256===sha(path.join(base,'external-document.css')),'Stale CSS');
 assert(manifest.internalCSSSHA256===sha(path.join(base,'internal-sourcebook.css')),'Stale internal CSS');
 for(const [n,h]of Object.entries(manifest.outputSHA256))assert(sha(path.join(dir,n))===h,'Stale '+n);
 const browser=await chromium.launch({channel:'chrome',headless:true});const page=await browser.newPage();
 const errors=[],network=[];page.on('pageerror',e=>errors.push(e.message));
 await page.route('**/*',route=>{if(/^https?:/.test(route.request().url())){network.push(route.request().url());return route.abort();}return route.continue();});
 await page.goto('file://'+path.join(dir,'internal-team-sourcebook.html'));
 for(const [size,width,height]of [['desktop',1440,1000],['phone',390,844]]){
  await page.setViewportSize({width,height});
  for(const lang of ['en','ms']){
   await page.locator('[data-language='+lang+']').click();await page.evaluate(()=>document.fonts.ready);
   assert(await page.locator('article:visible').count()===1,'Mixed languages');
   assert(await page.locator('article:visible .chapter').count()===23,'Chapter count');


   const overflow=await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1);assert(!overflow,size+' '+lang+' horizontal overflow');
   for(const a of await page.locator('nav:visible a').all()){const h=await a.getAttribute('href');assert(await page.locator(h).count()===1,'Missing nav target '+h);}
   await page.locator('nav:visible .home').click();
   await page.screenshot({path:path.join(dir,`check-${size}-${lang}-cover.png`)});
   for(const chapter of ['i03','i05','i08','appendix-a']){
    await page.locator('#'+lang+'-'+chapter).scrollIntoViewIfNeeded();
    await page.screenshot({path:path.join(dir,`check-${size}-${lang}-${chapter}.png`)});
   }
   console.log(size,lang,'language/navigation/overflow PASS');
  }
 }
 const source=fs.readFileSync(path.join(base,'internal-team-sourcebook.md'),'utf8');
 for(const match of source.matchAll(/\]\((?!https?:|#|mailto:)([^)]+)\)/g))assert(fs.existsSync(path.resolve(base,match[1].split('#')[0])),'Missing local source '+match[1]);
 for(const [,lang,md]of source.matchAll(/<!-- language: (en|ms) -->\n([\s\S]*?)(?=<!-- language: |$)/g)){
  const html=fs.readFileSync(path.join(dir,`internal-team-sourcebook-${lang}.html`),'utf8');
  assert(!/\/Users\/|fal\.env|\bRM\s*\d|\$\s*\d/i.test(html),'Internal sensitive-string/amount scan');
  await page.goto('file://'+path.join(dir,`internal-team-sourcebook-${lang}.html`));
  const paras=await page.locator('article p, article h1, article h2, article h3, article td, article th').allTextContents();
  const xml=execFileSync('/usr/bin/unzip',['-p',path.join(dir,`internal-team-sourcebook-${lang}.docx`),'word/document.xml'],{encoding:'utf8'});
  const docxText=[...xml.matchAll(/<w:t(?:\s[^>]*)?>([\s\S]*?)<\/w:t>/g)].map(m=>m[1].replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"').replace(/&apos;/g,"'")).join('');
  const pdf=execFileSync('pdftotext',['-raw',path.join(dir,`internal-team-sourcebook-${lang}.pdf`),'-'],{encoding:'utf8'}).replace(/Sifututor · Learnest Lab · 07\.09\.2026\s*\d+\s*\/\s*\d+/g,'');
  assert((xml.match(/<w:tbl>/g)||[]).length===marked.lexer(md).filter(t=>t.type==='table').length,'DOCX table count');
  assert((xml.match(/w:val="Heading1"/g)||[]).length===23,'DOCX heading count');
  for(const p of paras){assert(normal(docxText).includes(normal(p)),'DOCX missing '+lang+': '+p.slice(0,100));assert(normal(pdf).includes(normal(p)),'PDF missing '+lang+': '+p.slice(0,100));}
  const headings=marked.lexer(md).filter(t=>t.type==='heading'&&t.depth===2&&/^\d+\./.test(t.text));assert(headings.length===16,'Master chapters');
  console.log(lang,'PDF and editable DOCX text/table/heading completeness PASS');
 }
 assert(!errors.length,'Browser errors '+errors.join(';'));assert(!network.length,'Unexpected external requests');
 await browser.close();console.log('PASS: local build freshness, content completeness and offline browser checks');
})().catch(e=>{console.error(e);process.exit(1)});
