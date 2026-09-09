const { chromium } = require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const ctx = await browser.newContext({ viewport: { width: 1440, height: 900 }, offline: true });
  const page = await ctx.newPage(); const errs = []; const reqs = [];
  page.on('pageerror', e => errs.push(String(e))); page.on('requestfailed', r => reqs.push(r.url().slice(0, 80)));
  await page.goto('file:///Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/kota-buku-deck-share.html'); await page.waitForTimeout(800);
  const fonts = await page.evaluate(() => [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family + ' ' + f.weight));
  const count = await page.textContent('#count'); await page.keyboard.press('End'); const last = await page.textContent('#count');
  await page.click('button[data-lang="ms"]'); const bm = await page.textContent('.slide.active h1');
  console.log(JSON.stringify({ errs, failedRequests: reqs, fontsLoaded: fonts, first: count, last, bmHeadline: bm.slice(0, 40), hintPresent: await page.$$eval('[data-i="hintKey"]', e => e.length) }));
  await browser.close();
})();
