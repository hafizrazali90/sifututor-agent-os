const assert=require('node:assert/strict'),path=require('node:path');
const {chromium}=require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
const root=path.resolve(__dirname,'..');
(async()=>{const browser=await chromium.launch({channel:'chrome'});try{
for(const width of [1920,390])for(const language of ['en','ms']){
 const page=await browser.newPage({viewport:{width,height:width===1920?1080:844}}),errors=[];page.on('pageerror',e=>errors.push(String(e)));
 await page.goto('file://'+path.join(root,'kota-buku-deck.html'));await page.evaluate(()=>document.fonts.ready);await page.click(`button[data-lang="${language}"]`);await page.keyboard.press('Home');await page.keyboard.press('ArrowRight');await page.waitForTimeout(500);
 await page.screenshot({path:path.join(root,`screenshots/roles-${width}-${language}-overview.png`),fullPage:true});
 for(const role of [1,2,3]){
  await page.click(`#b01 [data-p="${role}"]`);assert(await page.$eval('#rolePreview',d=>d.open));
  if(role===1){await page.click('[data-rp="reveal"]');assert(await page.locator('.rp-result').isVisible());assert((await page.textContent('.rp-result')).includes('Aiman'));}
  if(role===2){await page.click('[data-rp="online"]');await page.click('[data-rp="quarter"]');assert(await page.locator('.rp-result').isVisible());await page.click('[data-rp="half"]');assert((await page.textContent('.rp-result')).startsWith(language==='en'?'Yes.':'Betul.'));}
  if(role===3){await page.click('[data-rp="next"]');assert((await page.textContent('.rp-result')).includes('Aiman'));}
  const overflow=await page.$eval('#rolePreview',d=>({x:d.scrollWidth>d.clientWidth+1,viewport:d.getBoundingClientRect().right>innerWidth}));assert(!overflow.x&&!overflow.viewport);
  await page.screenshot({path:path.join(root,`screenshots/roles-${width}-${language}-${role}.png`)});
  const before=await page.textContent('#count');await page.keyboard.press('ArrowRight');assert.equal(await page.textContent('#count'),before);
  await page.keyboard.press('Escape');assert(!(await page.$eval('#rolePreview',d=>d.open)));
 }
 await page.locator('#b01 [data-p="1"]').focus();await page.keyboard.press('Enter');assert(await page.$eval('#rolePreview',d=>d.open));await page.click('[data-rp="reveal"]');await page.keyboard.press('r');assert(!(await page.locator('.rp-result').isVisible()));await page.click('#rpBack');assert(!(await page.$eval('#rolePreview',d=>d.open)));
 await page.click('#b01 [data-p="3"]');await page.evaluate(()=>pdfMode(true));assert(!(await page.$eval('#rolePreview',d=>d.open)));await page.evaluate(()=>pdfMode(false));assert.deepEqual(errors,[]);
 console.log('PASS',width,language,'all roles, answers, back, Escape, reset, navigation isolation, PDF closure');await page.close();
}}finally{await browser.close();}})().catch(e=>{console.error(e);process.exitCode=1;});
