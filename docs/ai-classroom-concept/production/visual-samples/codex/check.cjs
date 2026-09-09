// Local presentation QA only. Uses existing Playwright, no application server or data.
const { chromium } = require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
const path = require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 const page=await browser.newPage({deviceScaleFactor:1});
 const errors=[];page.on('pageerror',e=>errors.push(e.message));
 for(const [name,width,height] of [['desktop',1920,1080],['small',1280,720],['phone',390,844]]){for(const language of ['en','ms']){
  await page.setViewportSize({width,height});
  await page.goto('file://'+path.join(__dirname,'sample.html'));
  await page.evaluate(()=>document.fonts.ready);
  await page.locator(`[data-language="${language}"]`).click();
  await page.screenshot({path:path.join(__dirname,`sample-${name}-${language}.png`)});
  const parity=await page.evaluate(lang=>[...document.querySelectorAll('[data-ms][data-en]')].every(e=>e.textContent===e.dataset[lang]),language);
  if(!parity)throw Error('Mixed-language content');
  const result=await page.evaluate(()=>({
   active:document.querySelectorAll('.slide.active').length,
   stage:[document.querySelector('.slide').offsetWidth,document.querySelector('.slide').offsetHeight],
   overflow:[...document.querySelectorAll('.screen,.sheet,.caption,.heading,.delivery')].filter(e=>e.scrollWidth>e.clientWidth+1||e.scrollHeight>e.clientHeight+1).map(e=>e.className),
   externalAssets:performance.getEntriesByType('resource').filter(e=>/^https?:/.test(e.name)).length,
   placeholders:document.body.innerText.includes('{{'),
   verticalGaps:[['.heading','.visual'],['.caption','.delivery'],['.delivery','.footer']].map(([a,b])=>({pair:[a,b],gap:document.querySelector(b).getBoundingClientRect().top-document.querySelector(a).getBoundingClientRect().bottom})),
  }));
  if(result.active!==1||result.overflow.length||result.placeholders||result.externalAssets||result.verticalGaps.some(g=>g.gap<0))throw Error(JSON.stringify(result));
  await page.keyboard.press('ArrowRight');await page.keyboard.press('ArrowLeft');
  await page.keyboard.press('e');
  if(await page.locator('[contenteditable="true"]').count()!==3)throw Error('Edit toggle failed');
  await page.keyboard.press('e');
  console.log(name,language,JSON.stringify(result));
 }}
 if(errors.length)throw Error(errors.join(';'));
 console.log('PASS: render, fonts, bounds, offline assets, navigation, edit toggle, no JS errors');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
