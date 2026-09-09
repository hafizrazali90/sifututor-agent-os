// Owner-approved two-line cover copy. Local document QA only.
const assert = require('node:assert/strict');
const path = require('node:path');
const {chromium} = require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
const root = path.resolve(__dirname, '..');
const copy = {
  en: 'An AI assistant to prepare lessons, understand students, handle daily tasks and keep parents informed.',
  ms: 'Pembantu AI untuk menyediakan pelajaran, memahami murid, mengurus tugas harian dan memaklumkan ibu bapa.'
};
(async () => {
  const browser = await chromium.launch({channel: 'chrome'});
  try {
    for (const [width, height] of [[1920,1080], [1280,720], [390,844]]) {
      const page = await browser.newPage({viewport: {width,height}});
      await page.goto('file://' + path.join(root,'kota-buku-deck.html'));
      await page.evaluate(() => document.fonts.ready);
      await page.keyboard.press('Home');
      for (const lang of ['en','ms']) {
        await page.click(`button[data-lang="${lang}"]`);
        await page.waitForTimeout(600);
        const result = await page.evaluate(() => {
          const el = document.querySelector('#t0 [data-i="t0s"]');
          const style = getComputedStyle(el);
          const range = document.createRange(); range.selectNodeContents(el);
          const rects = [...range.getClientRects()];
          const lines = new Set(rects.map(r => Math.round(r.top))).size;
          return {text: el.textContent, lines, font: style.fontSize,
            overflow: document.documentElement.scrollWidth > innerWidth,
            clipped: el.scrollHeight > el.clientHeight + 1};
        });
        assert.equal(result.text,copy[lang]);
        assert(!result.text.includes('\u2014'));
        assert(!result.overflow && !result.clipped);
        if (width > 820) { assert.equal(result.lines,2); assert.equal(result.font,'28px'); }
        await page.screenshot({path:path.join(root,'screenshots',`cover-copy-${width}-${lang}.png`),fullPage:width < 820});
        console.log(JSON.stringify({width,lang,...result}));
      }
      await page.close();
    }
  } finally { await browser.close(); }
})().catch(e => {console.error(e);process.exitCode=1;});
