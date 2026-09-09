const path = require('node:path');
const puppeteer = require('/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/puppeteer');

const [htmlPath, outputPath] = process.argv.slice(2);
if (!htmlPath || !outputPath) {
  throw new Error('Usage: node render-deck-pdf.cjs <deck.html> <deck.pdf>');
}

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  });
  const page = await browser.newPage();
  await page.goto(`file://${path.resolve(htmlPath)}`, { waitUntil: 'networkidle0' });
  await page.pdf({
    path: outputPath,
    width: '13.333in',
    height: '7.5in',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: false,
    margin: { top: '0', right: '0', bottom: '0', left: '0' },
  });
  await browser.close();
  console.log(outputPath);
})();

