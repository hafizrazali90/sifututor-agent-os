const path = require('node:path');
const puppeteer = require('/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/puppeteer');

const [htmlPath] = process.argv.slice(2);
if (!htmlPath) throw new Error('Usage: node check-executive-frontend-deck.cjs <deck.html>');

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  });
  const page = await browser.newPage();
  const failures = [];

  const inspectViewport = async (width, height) => {
    await page.setViewport({ width, height });
    await page.goto(`file://${path.resolve(htmlPath)}`, { waitUntil: 'networkidle0' });
    return page.evaluate(() => {
      const stage = document.querySelector('.deck-stage').getBoundingClientRect();
      const slides = [...document.querySelectorAll('.slide')];
      return {
        stage: { width: stage.width, height: stage.height, left: stage.left, top: stage.top },
        slides: slides.length,
        active: document.querySelectorAll('.slide.active.visible').length,
        controls: document.querySelectorAll('.deck-controls button[aria-label]').length,
        externalLinks: [...document.querySelectorAll('.source-links a')].map((link) => link.href),
        overflow: slides.map((slide, index) => ({
          slide: index + 1,
          vertical: slide.querySelector('.slide-body').scrollHeight > slide.querySelector('.slide-body').clientHeight + 2,
          horizontal: slide.querySelector('.slide-body').scrollWidth > slide.querySelector('.slide-body').clientWidth + 2,
        })).filter((item) => item.vertical || item.horizontal),
      };
    });
  };

  const desktop = await inspectViewport(1440, 900);
  if (desktop.slides !== 18) failures.push(`expected 18 slides, found ${desktop.slides}`);
  if (desktop.active !== 1) failures.push(`expected one active slide, found ${desktop.active}`);
  if (desktop.controls < 3) failures.push('presentation controls are incomplete');
  if (desktop.externalLinks.length < 8 || desktop.externalLinks.some((href) => !href.startsWith('https://'))) {
    failures.push('reader-facing public sources are missing valid HTTPS links');
  }
  if (desktop.overflow.length) failures.push(`desktop overflow: ${JSON.stringify(desktop.overflow)}`);
  if (Math.abs(desktop.stage.width / desktop.stage.height - 16 / 9) > 0.001) failures.push('desktop stage is not 16:9');

  await page.keyboard.press('ArrowRight');
  const activeAfterRight = await page.$eval('.slide.active', (slide) => Number(slide.dataset.slide));
  if (activeAfterRight !== 2) failures.push(`ArrowRight navigation reached slide ${activeAfterRight}`);
  await page.keyboard.press('ArrowLeft');
  const activeAfterLeft = await page.$eval('.slide.active', (slide) => Number(slide.dataset.slide));
  if (activeAfterLeft !== 1) failures.push(`ArrowLeft navigation reached slide ${activeAfterLeft}`);

  await page.keyboard.press('ArrowRight');
  await page.keyboard.press('ArrowRight');
  await page.click('.slide.active .source-trigger');
  const drawerOpen = await page.$eval('.slide.active .source-drawer', (drawer) => drawer.classList.contains('open'));
  if (!drawerOpen) failures.push('source drawer did not open');
  await page.keyboard.press('Escape');

  const phone = await inspectViewport(390, 844);
  if (phone.active !== 1) failures.push(`phone expected one active slide, found ${phone.active}`);
  if (phone.overflow.length) failures.push(`phone overflow: ${JSON.stringify(phone.overflow)}`);
  if (Math.abs(phone.stage.width / phone.stage.height - 16 / 9) > 0.001) failures.push('phone stage is not 16:9');
  if (phone.stage.width > 390.5 || phone.stage.height > 844.5) failures.push('phone stage exceeds viewport');

  await browser.close();
  if (failures.length) {
    console.log(JSON.stringify({ status: 'FAIL', failures, desktop, phone }, null, 2));
    process.exit(1);
  }
  console.log(JSON.stringify({
    status: 'PASS', slides: desktop.slides, externalLinks: desktop.externalLinks.length,
    desktopStage: desktop.stage, phoneStage: phone.stage, navigation: 'PASS', sourceDrawer: 'PASS', overflow: 'none',
  }, null, 2));
})();
