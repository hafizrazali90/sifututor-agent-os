const { chromium } = require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
const dir = '/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/';
const url = 'file://' + dir + 'kota-buku-deck.html';
(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = []; page.on('pageerror', e => errors.push(String(e)));
  await page.goto(url); await page.waitForTimeout(400);
  const out = {};
  for (const l of ['en', 'ms']) {
    await page.evaluate((l) => { pdfMode(false); setLang(l); document.querySelector('.slide.active') || null; }, l);
    await page.keyboard.press('Home'); await page.waitForTimeout(200);
    await page.evaluate(() => pdfMode(true)); await page.waitForTimeout(600);
    // checks: every slide is laid out at 1920x1080 in flow, nothing hidden, no chrome
    const info = await page.evaluate(() => {
      const slides = [...document.querySelectorAll('.slide')];
      const bad = [];
      slides.forEach((sl, i) => { const r = sl.getBoundingClientRect(); if (Math.round(r.height) !== 1080 || Math.round(r.width) !== 1920) bad.push('size:' + sl.id + ':' + Math.round(r.width) + 'x' + Math.round(r.height)); if (getComputedStyle(sl).visibility === 'hidden' || getComputedStyle(sl).opacity === '0') bad.push('hidden:' + sl.id); if (sl.scrollHeight > sl.clientHeight + 2) bad.push('overflow:' + sl.id + ':' + sl.scrollHeight); });
      const chrome = [...document.querySelectorAll('.chrome, .hint-legend, .info, .infocard, .scrim')].filter(e => getComputedStyle(e).display !== 'none');
      if (chrome.length) bad.push('chromeVisible:' + chrome.length);
      const ap = document.getElementById('appendix');
      return { n: slides.length, bad, appendix: ap ? ap.textContent.trim().slice(0, 80) : null, credit: slides[1].getAttribute('data-credit') };
    });
    const name = dir + 'kota-buku-deck-' + (l === 'ms' ? 'bm' : 'en') + '.pdf';
    await page.emulateMedia({ media: 'screen' });
    await page.pdf({ path: name, width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: false, margin: { top: 0, right: 0, bottom: 0, left: 0 } });
    // page screenshots of the pdf-mode flow for a visual check (first, a middle one, appendix)
    await page.screenshot({ path: dir + 'screenshots/deck/pdfmode-' + (l === 'ms' ? 'bm' : 'en') + '-appendix.png', clip: { x: 0, y: 1080 * (info.n - 1), width: 1920, height: 1080 }, fullPage: true });
    await page.screenshot({ path: dir + 'screenshots/deck/pdfmode-' + (l === 'ms' ? 'bm' : 'en') + '-p05.png', clip: { x: 0, y: 1080 * 4, width: 1920, height: 1080 }, fullPage: true });
    out[l] = { ...info, file: name };
    await page.evaluate(() => pdfMode(false)); await page.waitForTimeout(200);
  }
  // after leaving pdf mode the deck must still work
  out.afterCount = await page.textContent('#count');
  out.afterVisible = await page.$$eval('.slide', s => s.filter(x => getComputedStyle(x).visibility === 'visible').length);
  out.errors = errors;
  console.log(JSON.stringify(out, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
