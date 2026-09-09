const {chromium}=require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
const path=require('node:path');
(async()=>{const browser=await chromium.launch({channel:'chrome',headless:true});const page=await browser.newPage();const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('file://'+path.join(__dirname,'sequence.html'));await page.evaluate(()=>document.fonts.ready);
for(const [name,width,height] of [['desktop',1920,1080],['small',1280,720],['phone',390,844]]){await page.setViewportSize({width,height});for(const lang of ['en','ms']){await page.locator(`[data-language=${lang}]`).click();await page.evaluate(()=>show(0));for(let i=0;i<3;i++){
await page.screenshot({path:path.join(__dirname,`sequence-${name}-${lang}-${i+1}.png`)});
const result=await page.evaluate(()=>{const active=document.querySelector('.slide.active');return{count:document.querySelectorAll('.slide.active').length,overflow:[...active.querySelectorAll('div,h1,h2,h3,p,aside')].filter(e=>e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+2).map(e=>e.className||e.tagName),mixed:[...document.querySelectorAll('[data-en][data-ms]')].filter(e=>e.textContent!==e.dataset[document.documentElement.lang].replaceAll('\\n',' ')).length}});
if(result.count!==1||result.overflow.length||result.mixed)throw Error(JSON.stringify({name,lang,i,result}));if(i<2)await page.keyboard.press('ArrowRight');
}console.log(name,lang,'3 slides PASS');}}
await page.keyboard.press('ArrowLeft');if(await page.locator('#progress').innerText()!=='2 / 3')throw Error('Back navigation');if(errors.length)throw Error(errors.join(';'));await browser.close();})().catch(e=>{console.error(e);process.exit(1)});
