const { chromium, devices } = require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
const out = '/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/screenshots/deck/';
const url = 'file:///Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/kota-buku-deck.html';
(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const ctx = await browser.newContext({ ...devices['iPhone 13'] });
  const page = await ctx.newPage();
  const errors = []; page.on('pageerror', e => errors.push(String(e)));
  await page.goto(url); await page.waitForTimeout(500); await page.evaluate(() => document.documentElement.classList.add('capture'));
  const ids = await page.$$eval('.slide', s => s.map(x => x.id));
  const check = (label) => page.evaluate((label) => {
    const bad = []; const W = window.innerWidth;
    const active = document.querySelector('.slide.active');
    const vis = el => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && cs.opacity !== '0'; };
    if (document.documentElement.scrollWidth > W + 1) bad.push('hscroll:' + document.documentElement.scrollWidth);
    [active, ...document.querySelectorAll('.chrome')].forEach(root => root.querySelectorAll('*').forEach(el => {
      if (!vis(el) || el.closest('.mini')) return; const r = el.getBoundingClientRect(); if (!r.width) return;
      if (r.right > W + 1 || r.left < -1) bad.push('offscreen:' + (el.className || el.tagName) + ':' + el.textContent.trim().slice(0, 24) + ' ' + Math.round(r.left) + '-' + Math.round(r.right));
      const cs = getComputedStyle(el);
      if (el.children.length === 0 && el.textContent.trim() && parseFloat(cs.fontSize) < 12) bad.push('tiny:' + (el.className || el.tagName) + ':' + el.textContent.trim().slice(0, 20) + ' ' + cs.fontSize);
      if ((cs.overflow === 'hidden' || cs.overflowY === 'hidden') && el.scrollHeight > el.clientHeight + 2 && !el.classList.contains('slide') && !el.classList.contains('pcard') && !el.classList.contains('photo')) bad.push('innerOverflow:' + (el.className || el.tagName) + ' ' + el.scrollHeight + '>' + el.clientHeight);
    }));
    const leaves = [...active.querySelectorAll('*')].filter(el => vis(el) && !el.closest('.mini') && el.children.length === 0 && el.textContent.trim() && el.getBoundingClientRect().width);
    const isInl = el => /^inline/.test(getComputedStyle(el).display);
    const topInl = el => { let top = null; for (let p = el; p && p.tagName !== 'SECTION'; p = p.parentElement) if (isInl(p)) top = p; return top; };
    const blockOf = el => { const t = topInl(el); return t ? t.parentElement : el; };
    const sameLine = (a, b) => (topInl(a) || topInl(b)) && blockOf(a) === blockOf(b);
    for (let i = 0; i < leaves.length; i++) for (let j = i + 1; j < leaves.length; j++) { if (sameLine(leaves[i], leaves[j])) continue; if (leaves[i].closest('#b05 .sheet2') && leaves[j].closest('#b05 .sheet2')) continue; const a = leaves[i].getBoundingClientRect(), b = leaves[j].getBoundingClientRect(); if (a.left < b.right - 2 && b.left < a.right - 2 && a.top < b.bottom - 2 && b.top < a.bottom - 2) bad.push('textOverlap:' + (leaves[i].className || leaves[i].tagName) + '[' + leaves[i].textContent.trim().slice(0, 14) + ']|' + (leaves[j].className || leaves[j].tagName) + '[' + leaves[j].textContent.trim().slice(0, 14) + ']'); }
    return { label, mobile: document.documentElement.classList.contains('mobile'), bad: [...new Set(bad)], h: document.documentElement.scrollHeight };
  }, label);
  const results = [];
  for (const l of ['en', 'ms']) {
    await page.click(`button[data-lang="${l}"]`); await page.keyboard.press('Home'); await page.waitForTimeout(500);
    for (let i = 0; i < ids.length; i++) {
      if (i) { await page.click('#next'); await page.waitForTimeout(500); }
      await page.evaluate(() => window.scrollTo(0, 0));
      results.push(await check(`${l}-${ids[i]}`));
      if (l === 'en' || ['b01', 's2', 'b05', 'b06', 'b11'].includes(ids[i])) await page.screenshot({ path: `${out}m-${l === 'ms' ? 'bm' : 'en'}-${String(i + 1).padStart(2, '0')}-${ids[i]}.png`, fullPage: true });
    }
  }
  // tap tests on the phone
  const ix = {};
  await page.click('button[data-lang="en"]'); await page.keyboard.press('Home'); await page.waitForTimeout(300);
  const go = async (id) => { const i = ids.indexOf(id); await page.evaluate((i) => deck.show(i), i); await page.waitForTimeout(400); };
  await go('b01'); await page.tap('#b01 .card1[data-p="3"]'); await page.waitForTimeout(150); ix.b01 = await page.$eval('#b01 .card1.on', e => e.dataset.p); ix.rolePreview = await page.$eval('#rolePreview', e => e.open); await page.tap('#rpBack');
  await go('b05'); await page.tap('#capBtn'); await page.waitForTimeout(1800); ix.b05 = (await page.textContent('#camHint')).trim();
  await go('b10'); await page.tap('#netSwitch'); await page.waitForTimeout(200); ix.b10 = (await page.textContent('#netSt')).trim();
  await go('b06'); await page.tap('#b06 .info'); await page.waitForTimeout(200); ix.infoShown = await page.$eval('#infocard', e => e.classList.contains('show'));
  ix.infoFits = await page.evaluate(() => { const c = document.getElementById('infocard').getBoundingClientRect(); return c.left >= 0 && c.right <= window.innerWidth + 1 && c.top >= 0 && c.bottom <= window.innerHeight + 1; });
  await page.screenshot({ path: out + 'm-en-b06-info.png' });
  await page.tap('#infoClose'); await page.waitForTimeout(100); ix.infoClosed = await page.$eval('#infocard', e => !e.classList.contains('show'));
  console.log(JSON.stringify({ results: results.filter(r => r.bad.length).map(r => ({ l: r.label, bad: r.bad })), mobileFlag: results[0].mobile, heights: results.slice(0, ids.length).map(r => r.h), ix, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
