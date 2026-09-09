const path = require('node:path');
const puppeteer = require('/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/puppeteer');

const [htmlPath, outputPath] = process.argv.slice(2);

if (!htmlPath || !outputPath) {
  throw new Error('Usage: node render-pdf.cjs <source.html> <output.pdf>');
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
    format: 'A4',
    printBackground: true,
    preferCSSPageSize: true,
    displayHeaderFooter: true,
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:8px;color:#64748b;text-align:center"><span class="pageNumber"></span> / <span class="totalPages"></span></div>',
    margin: { top: '18mm', right: '14mm', bottom: '20mm', left: '14mm' },
  });
  await browser.close();
  console.log(outputPath);
})();
