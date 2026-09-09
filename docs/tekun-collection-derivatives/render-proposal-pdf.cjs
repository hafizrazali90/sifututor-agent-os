const fs = require('node:fs');
const path = require('node:path');
const puppeteer = require('/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/puppeteer');
const [htmlPath, outputPath] = process.argv.slice(2);
if (!htmlPath || !outputPath) throw new Error('Usage: node render-proposal-pdf.cjs <input.html> <output.pdf>');
(async()=>{const browser=await puppeteer.launch({headless:'new',args:['--no-sandbox']});const page=await browser.newPage();await page.goto(`file://${path.resolve(htmlPath)}`,{waitUntil:'networkidle0'});await page.pdf({path:outputPath,format:'A4',printBackground:true,margin:{top:'12mm',right:'12mm',bottom:'14mm',left:'12mm'},displayHeaderFooter:true,headerTemplate:'<div></div>',footerTemplate:'<div style="font-size:7px;color:#7b8895;width:100%;text-align:right;padding-right:12mm"><span class="pageNumber"></span> / <span class="totalPages"></span></div>'});await browser.close();console.log(outputPath);})();
