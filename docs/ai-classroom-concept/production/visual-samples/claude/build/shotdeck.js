const { chromium } = require('/Users/hafizrazali/Projects/Sifututor/kelas/node_modules/playwright');
const out = '/Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/screenshots/deck/';
require('fs').mkdirSync(out, { recursive: true });
const url = 'file:///Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/production/visual-samples/claude/kota-buku-deck.html';
const ONLY = process.env.ONLY ? process.env.ONLY.split(',') : null;
(async () => {
  const browser = await chromium.launch({ channel: 'chrome' });
  const ctx = await browser.newContext({ viewport: { width: 1920, height: 1080 }, deviceScaleFactor: 1 });
  const page = await ctx.newPage();
  const errors = []; page.on('pageerror', e => errors.push(String(e))); page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto(url); await page.waitForTimeout(400);
  const blur = () => page.evaluate(() => document.activeElement && document.activeElement.blur());
  const ids = await page.$$eval('.slide', s => s.map(x => x.id));
  const check = (label) => page.evaluate((label) => {
    const bad = [];
    const stage = document.getElementById('deckStage').getBoundingClientRect();
    const active = document.querySelector('.slide.active');
    const vis = el => { const cs = getComputedStyle(el); return cs.display !== 'none' && cs.visibility !== 'hidden' && cs.opacity !== '0'; };
    const clipRect = el => { let r = el.getBoundingClientRect(); let x1 = r.left, y1 = r.top, x2 = r.right, y2 = r.bottom; for (let p = el.parentElement; p && p !== document.body; p = p.parentElement) { const cs = getComputedStyle(p); if (/hidden|clip/.test(cs.overflow + cs.overflowX + cs.overflowY)) { const pr = p.getBoundingClientRect(); x1 = Math.max(x1, pr.left); y1 = Math.max(y1, pr.top); x2 = Math.min(x2, pr.right); y2 = Math.min(y2, pr.bottom); } } return { left: x1, top: y1, right: x2, bottom: y2, width: Math.max(0, x2 - x1), height: Math.max(0, y2 - y1) }; };
    const shown = el => { const c = clipRect(el); return c.width > 1 && c.height > 1; };
    const scope = [active, ...document.querySelectorAll('.chrome'), document.getElementById('hintLegend')];
    scope.forEach(root => root.querySelectorAll('*').forEach(el => {
      if (!vis(el) || el.closest('.mini')) return;
      const r = el.getBoundingClientRect(); if (!r.width) return;
      if (r.right > stage.right + 1 || r.bottom > stage.bottom + 1 || r.left < stage.left - 1 || r.top < stage.top - 1) bad.push('outside:' + (el.className || el.tagName) + ':' + el.textContent.trim().slice(0, 30));
      if (el.children.length === 0 && el.textContent.trim() && el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflow !== 'visible') bad.push('clip:' + el.className + ':' + el.textContent.slice(0, 30));
      const cs = getComputedStyle(el);
      if ((cs.overflow === 'hidden' || cs.overflowY === 'hidden') && el.scrollHeight > el.clientHeight + 2 && !el.classList.contains('slide') && !el.classList.contains('crop')) bad.push('innerOverflow:' + (el.className || el.tagName) + ' ' + el.scrollHeight + '>' + el.clientHeight);
      if ((cs.overflow === 'hidden' || cs.overflowX === 'hidden') && el.scrollWidth > el.clientWidth + 2 && !el.classList.contains('slide') && !el.classList.contains('pcard')) bad.push('innerOverflowX:' + (el.className || el.tagName) + ' ' + el.scrollWidth + '>' + el.clientWidth);
      // text smaller than 13px anywhere on a slide
      if (el.children.length === 0 && el.textContent.trim() && parseFloat(cs.fontSize) < 13) bad.push('tiny:' + (el.className || el.tagName) + ':' + el.textContent.trim().slice(0, 20) + ' ' + cs.fontSize);
    }));
    // children escaping their parent box (flex/grid overflow) for cards and columns
    active.querySelectorAll('.stagebox, .stagebox *').forEach(p => { if (!vis(p) || p.closest('.crop')) return; const cs = getComputedStyle(p); if (cs.position === 'absolute' || cs.display === 'inline') return; const pr = p.getBoundingClientRect(); if (!pr.width) return; [...p.children].forEach(c => { if (!vis(c)) return; const cc = getComputedStyle(c); if (cc.position === 'absolute') return; const r = c.getBoundingClientRect(); if (!r.width) return; if (r.bottom > pr.bottom + 2 || r.right > pr.right + 2) bad.push('escapes:' + (c.className || c.tagName) + '[' + c.textContent.trim().slice(0, 16) + '] in ' + (p.className || p.tagName) + ' ' + Math.round(r.bottom - pr.bottom) + '/' + Math.round(r.right - pr.right)); }); });
    const blocks = [...active.querySelectorAll('.head,.blk'), ...document.querySelectorAll('.chrome')].filter(vis).map(e => ({ n: e.className, r: e.getBoundingClientRect() }));
    for (let i = 0; i < blocks.length; i++) for (let j = i + 1; j < blocks.length; j++) { const a = blocks[i].r, b = blocks[j].r; if (a.left < b.right - 1 && b.left < a.right - 1 && a.top < b.bottom - 1 && b.top < a.bottom - 1) bad.push('overlap:' + blocks[i].n + '|' + blocks[j].n); }
    const isInl = el => /^inline/.test(getComputedStyle(el).display);
    const topInl = el => { let top = null; for (let p = el; p && p.tagName !== 'SECTION'; p = p.parentElement) if (isInl(p)) top = p; return top; };
    const blockOf = el => { const t = topInl(el); return t ? t.parentElement : el; };
    const sameLine = (a, b) => (topInl(a) || topInl(b)) && blockOf(a) === blockOf(b);
    const leaves = [...active.querySelectorAll('*'), ...document.querySelectorAll('#hintLegend *, .chrome *')].filter(el => vis(el) && shown(el) && !el.closest('.mini') && el.children.length === 0 && el.textContent.trim() && el.getBoundingClientRect().width);
    const probes = [...active.querySelectorAll('.callout,.tag,.prov,.btn,.status,.gchip,.strip .st,.tray .chip,.pillnote,.mark,.info,.detail,.note'), document.getElementById('hintLegend'), ...document.querySelectorAll('.chrome .credits, .chrome .nav, .chrome .honest-line, .chrome .wordmark, .chrome .eyebrow, .chrome .lang')].filter(vis);
    probes.forEach(pr => { if (!shown(pr)) return; const a = clipRect(pr); if (!a.width) return; leaves.forEach(el => { if (pr === el || pr.contains(el) || el.contains(pr) || sameLine(pr, el)) return; const b = clipRect(el); const m = 6; if (a.left - m < b.right && b.left < a.right + m && a.top - m < b.bottom && b.top < a.bottom + m) bad.push('near:' + (pr.className || pr.tagName) + '[' + pr.textContent.trim().slice(0, 14) + ']|' + (el.className || el.tagName) + '[' + el.textContent.trim().slice(0, 14) + ']'); }); });
    // any two text leaves overlapping each other
    for (let i = 0; i < leaves.length; i++) for (let j = i + 1; j < leaves.length; j++) { if (sameLine(leaves[i], leaves[j])) continue; if (leaves[i].closest('#t0 .card') && leaves[j].closest('#t0 .card')) continue; /* rotated card: axis-aligned boxes overlap although the text does not */ if (leaves[i].closest('#b05 .sheet2') && leaves[j].closest('#b05 .sheet2')) continue; /* rotated sheet, same reason */ const a = clipRect(leaves[i]), b = clipRect(leaves[j]); if (a.left < b.right - 2 && b.left < a.right - 2 && a.top < b.bottom - 2 && b.top < a.bottom - 2) bad.push('textOverlap:' + (leaves[i].className || leaves[i].tagName) + '[' + leaves[i].textContent.trim().slice(0, 14) + ']|' + (leaves[j].className || leaves[j].tagName) + '[' + leaves[j].textContent.trim().slice(0, 14) + ']'); }
    active.querySelectorAll('.thread path').forEach(path => { const dAttr = path.getAttribute('d') || ''; if (!dAttr.trim()) return;
      const f = stage.width / 1920; const toks = dAttr.replace(/([MHVLZ])/g, ' $1 ').trim().split(/\s+/); let cx = 0, cy = 0, segs = [];
      for (let i = 0; i < toks.length; i++) { const t = toks[i]; if (t === 'M') { cx = +toks[++i]; cy = +toks[++i]; } else if (t === 'H') { const nx = +toks[++i]; segs.push({ x1: Math.min(cx, nx), x2: Math.max(cx, nx), y1: cy, y2: cy }); cx = nx; } else if (t === 'V') { const ny = +toks[++i]; segs.push({ x1: cx, x2: cx, y1: Math.min(cy, ny), y2: Math.max(cy, ny) }); cy = ny; } }
      segs.forEach(sg => leaves.forEach(el => { if (el.closest('.callout')) return; const b = el.getBoundingClientRect(); const bx1 = (b.left - stage.left) / f, bx2 = (b.right - stage.left) / f, by1 = (b.top - stage.top) / f, by2 = (b.bottom - stage.top) / f;
        if (sg.x1 - 3 < bx2 && bx1 < sg.x2 + 3 && sg.y1 - 3 < by2 && by1 < sg.y2 + 3) bad.push('threadCrossesText:' + (el.className || el.tagName) + '[' + el.textContent.trim().slice(0, 16) + ']'); })); });
    const headEl = active.querySelector('.head'), blkEl = active.querySelector('.blk');
    if (headEl && blkEl) { const head = headEl.getBoundingClientRect(), firstBlk = blkEl.getBoundingClientRect(); if (head.bottom > firstBlk.top - 8) bad.push('headTooClose ' + Math.round(head.bottom) + '>' + Math.round(firstBlk.top)); }
    // untranslated: any data-i element left empty
    active.querySelectorAll('[data-i]').forEach(el => { if (vis(el) && !el.textContent.trim() && !el.querySelector('svg')) bad.push('emptyText:' + el.getAttribute('data-i')); });
    // bottom chrome vs slide content: anything from the slide (not chrome) below y=1000 that is not chrome
    return { label, id: active.id, lang: document.documentElement.lang, title: document.title, count: document.getElementById('count').textContent, bad: [...new Set(bad)] };
  }, label);
  const results = [];
  for (const l of ['en', 'ms']) {
    const p = l === 'ms' ? 'bm' : 'en';
    await page.click(`button[data-lang="${l}"]`); await page.keyboard.press('Home'); await page.waitForTimeout(900);
    for (let i = 0; i < ids.length; i++) {
      if (i) { await page.keyboard.press('ArrowRight'); await page.waitForTimeout(900); }
      if (ONLY && !ONLY.includes(ids[i])) continue;
      results.push(await check(`${l}-${ids[i]}`)); await blur(); await page.screenshot({ path: `${out}${p}-${String(i + 1).padStart(2, '0')}-${ids[i]}.png` });
    }
  }
  // interactions (English)
  const ix = {};
  await page.click('button[data-lang="en"]'); await page.keyboard.press('Home'); await page.waitForTimeout(150);
  const go = async (id) => { const i = ids.indexOf(id); await page.click(`#marks button:nth-child(${i + 1})`); await page.waitForTimeout(700); };
  await go('b01'); await page.click('#b01 .card1[data-p="2"]'); await page.waitForTimeout(100); ix.b01 = await page.$eval('#b01 .card1.on', e => e.dataset.p); ix.rolePreview = await page.$eval('#rolePreview', e => e.open); await page.click('#rpBack');
  await go('b02'); await page.click('#b02 .tab[data-f="3"]'); await page.waitForTimeout(100); ix.b02 = (await page.textContent('#b02dt')).trim();
  await go('b05'); await page.click('#capBtn'); await page.waitForTimeout(200); ix.b05busy = (await page.textContent('#camHint')).trim(); await page.waitForTimeout(1600);
  ix.b05done = (await page.textContent('#camHint')).trim(); ix.b05read = await page.$eval('#cam', e => e.classList.contains('read'));
  await page.click('#fixBtn'); await page.waitForTimeout(100); ix.b05fix = (await page.textContent('#fixed')).trim(); await page.click('#confirmBtn'); await page.waitForTimeout(150); ix.b05status = (await page.textContent('#capStatus')).trim();
  results.push(await check('en-b05-interacted')); await blur(); await page.screenshot({ path: out + 'en-b05-interacted.png' });
  await go('b06'); await page.click('#b06 .tr[data-r="05"]'); await page.waitForTimeout(100); ix.b06row = (await page.textContent('#pd b')).trim();
  await page.click('#b06 .q[data-q="2"]'); await page.waitForTimeout(200); ix.askBusy = (await page.textContent('#ans')).trim().slice(0, 24); await page.waitForTimeout(1500); ix.askDone = (await page.textContent('#ans')).trim().slice(0, 40);
  await page.click('#b06 .aa[data-a="group"]'); await page.waitForTimeout(100); ix.askDec = (await page.textContent('#askSt')).trim();
  results.push(await check('en-b06-interacted')); await blur(); await page.screenshot({ path: out + 'en-b06-interacted.png' });
  await go('b06c'); ix.admRest = (await page.textContent('#drText')).trim().slice(0, 30); await page.click('#okBtn'); await page.waitForTimeout(150); ix.adm1 = (await page.textContent('#drSt')).trim();
  await page.click('#b06c .task[data-k="3"]'); await page.waitForTimeout(100); ix.adm3 = (await page.textContent('#drText')).trim().slice(0, 30);  await page.click('#againBtn'); await page.waitForTimeout(200); ix.adm3busy = (await page.textContent('#drText')).trim().slice(0, 20); await page.waitForTimeout(1400); ix.adm3again = (await page.textContent('#drText')).trim().slice(0, 20);
  results.push(await check('en-b06c-interacted')); await blur(); await page.screenshot({ path: out + 'en-b06c-interacted.png' });
  await go('b06d'); ix.dtRest = (await page.textContent('#dtOut')).trim().slice(0, 20); await page.click('#dtAsk'); await page.waitForTimeout(200); ix.dtBusy = (await page.textContent('#dtOut')).trim().slice(0, 20); await page.waitForTimeout(1500); ix.dtDone = (await page.textContent('#dtOut')).trim().slice(0, 20);
  results.push(await check('en-b06d-interacted'));
  await go('b09'); ix.b09rest = (await page.textContent('#pgOut')).trim().slice(0, 20); await page.click('#pgBtn'); await page.waitForTimeout(200); ix.b09busy = (await page.textContent('#pgOut')).trim().slice(0, 24); await page.waitForTimeout(1700); ix.b09done = (await page.textContent('#pgOut')).trim().slice(0, 20);
  await go('b10'); await page.click('#netSwitch'); await page.waitForTimeout(300); ix.b10 = (await page.textContent('#netSt')).trim() + ' off-rows:' + await page.$$eval('#b10 .row.need.off', r => r.length);
  await page.click('#b10 .rrow2[data-r="3"]'); await page.waitForTimeout(100); ix.b10role = (await page.textContent('#b10 .rrow2.on span')).trim().slice(0, 30);
  results.push(await check('en-b10-interacted')); await blur(); await page.screenshot({ path: out + 'en-b10-interacted.png' });
  await go('b11'); await page.click('#b11 .col2.trial'); await page.waitForTimeout(100); ix.b11 = await page.$eval('#b11 .col2.on', e => e.dataset.l);
  // info card
  await go('b06'); await page.click('#b06 .info'); await page.waitForTimeout(200); ix.infoShown = await page.$eval('#infocard', e => e.classList.contains('show')); ix.infoTitle = (await page.textContent('#infoH')).trim(); ix.infoLen = (await page.textContent('#infoP')).trim().length;
  ix.infoFits = await page.evaluate(() => { const c = document.getElementById('infocard').getBoundingClientRect(); const s = document.getElementById('deckStage').getBoundingClientRect(); return c.top >= s.top && c.bottom <= s.bottom && document.getElementById('infocard').scrollHeight <= document.getElementById('infocard').clientHeight + 2; });
  await blur(); await page.screenshot({ path: out + 'en-b06-info.png' });
  await page.keyboard.press('Escape'); await page.waitForTimeout(100); ix.infoHiddenAfterEsc = await page.$eval('#infocard', e => !e.classList.contains('show'));
  // longest info text fits the card (BM)
  await page.click('button[data-lang="ms"]'); await page.waitForTimeout(200);
  ix.infoOverflowBM = await page.evaluate(() => { const bad = []; document.querySelectorAll('.slide .info').forEach(b => { openInfo(b.dataset.info); const c = document.getElementById('infocard'); if (c.scrollHeight > c.clientHeight + 2) bad.push(b.dataset.info + ':' + c.scrollHeight); }); closeInfo(); return bad; });
  await page.click('button[data-lang="en"]'); await page.waitForTimeout(200);
  ix.infoOverflowEN = await page.evaluate(() => { const bad = []; document.querySelectorAll('.slide .info').forEach(b => { openInfo(b.dataset.info); const c = document.getElementById('infocard'); if (c.scrollHeight > c.clientHeight + 2) bad.push(b.dataset.info + ':' + c.scrollHeight); }); closeInfo(); return bad; });
  // reset
  await page.keyboard.press('r'); await page.waitForTimeout(200);
  ix.afterReset = { p: await page.$$eval('#b01 .card1.on', e => e.length), cap: (await page.textContent('#camHint')).trim(), net: (await page.textContent('#netSt')).trim(), adm: (await page.textContent('#tst1')).trim(), row: await page.$$eval('#b06 .tr.on', e => e.length), cues: await page.$$eval('.cue-dot', h => h.length) };
  // sample slide interactions still work
  await go('s1'); await page.click('#goals .goal[data-goal="g2"]'); await page.waitForTimeout(100); ix.s1goal = await page.$eval('#goals .goal.selected', e => e.dataset.goal);
  await go('s2'); await page.click('#assistBtn'); await page.waitForTimeout(2200); ix.s2crit = (await page.textContent('#critText')).trim().slice(0, 30);
  await go('s3'); await page.click('#segs .seg[data-row="quarter"][data-idx="1"] rect'); await page.waitForTimeout(100); ix.s3shaded = await page.$$eval('#segs .shade', s => s.length);
  await page.keyboard.press('r'); await page.waitForTimeout(150);
  // navigation and persistence
  const nav = {};
  await page.keyboard.press('Home'); nav.home = await page.textContent('#count'); await page.keyboard.press('End'); nav.end = await page.textContent('#count'); nav.nextDisabledAtEnd = await page.$eval('#next', b => b.disabled);
  nav.marks = await page.$$eval('#marks button', bs => bs.length); nav.hash = await page.evaluate(() => location.hash);
  await page.reload(); await page.waitForTimeout(400); nav.afterReload = await page.textContent('#count'); nav.langAfterReload = await page.evaluate(() => document.documentElement.lang);
  const grab = () => page.evaluate(() => { const a = {}; document.querySelectorAll('[data-i]').forEach(e => a[e.getAttribute('data-i')] = e.textContent.trim()); return a; });
  await page.click('button[data-lang="en"]'); const en = await grab(); await page.click('button[data-lang="ms"]'); const ms = await grab();
  const identical = Object.keys(en).filter(k => en[k] === ms[k]);
  await page.click('button[data-lang="en"]');
  // titles
  const titles = []; await page.keyboard.press('Home'); for (let i = 0; i < ids.length; i++) { if (i) await page.keyboard.press('ArrowRight'); titles.push(await page.title()); }
  console.log(JSON.stringify({ ids, results: results.map(r => ({ l: r.label, bad: r.bad })), ix, nav, identical, titles, errors }, null, 1));
  await browser.close();
})().catch(e => { console.error(e); process.exit(1); });
