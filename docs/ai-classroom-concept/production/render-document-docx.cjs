// Narrow Markdown-to-OOXML renderer for this document. No new dependencies.
// Keeps semantic headings, editable tables, lists and working source hyperlinks.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const {execFileSync}=require('node:child_process');
const {marked}=require('/Users/hafizrazali/.nvm/versions/node/v20.20.2/lib/node_modules/md-to-pdf/node_modules/marked');
const x=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
module.exports=function renderDOCX(md,lang,title,destination){
 const relationships=[],nums=[];let rid=2;
 function run(text,props=''){text=String(text).replace(/&#(x[0-9a-f]+|\d+);/gi,(_,n)=>String.fromCodePoint(n[0].toLowerCase()==='x'?parseInt(n.slice(1),16):Number(n))).replace(/&quot;/g,'"').replace(/&apos;/g,"'").replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&amp;/g,'&');return `<w:r>${props?'<w:rPr>'+props+'</w:rPr>':''}<w:t xml:space="preserve">${x(text)}</w:t></w:r>`;}
 function inline(tokens,props='') {return (tokens||[]).map(t=>{
  if(t.type==='strong')return inline(t.tokens,props+'<w:b/>');
  if(t.type==='em')return inline(t.tokens,props+'<w:i/>');
  if(t.type==='link'){const id='rId'+(++rid);relationships.push(`<Relationship Id="${id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="${x(t.href)}" TargetMode="External"/>`);return `<w:hyperlink r:id="${id}">${inline(t.tokens,props+'<w:color w:val="216854"/><w:u w:val="single"/>')}</w:hyperlink>`;}
  if(t.type==='br')return '<w:r><w:br/></w:r>';
  if(t.tokens)return inline(t.tokens,props);
  return run(t.text||t.raw||'',props);
 }).join('');}
 function paragraph(tokens,style='Normal',extra=''){return `<w:p><w:pPr><w:pStyle w:val="${style}"/>${extra}</w:pPr>${inline(tokens)}</w:p>`;}
 function table(t){const cols=t.header.length,widths=cols===3?[2150,3500,3550]:[2700,6500];
  function row(cells,header){return `<w:tr><w:trPr><w:cantSplit/>${header?'<w:tblHeader/>':''}</w:trPr>${cells.map((c,i)=>`<w:tc><w:tcPr><w:tcW w:w="${widths[i]||Math.floor(9200/cols)}" w:type="dxa"/>${header?'<w:shd w:fill="EDF3EE"/>':''}</w:tcPr><w:p><w:pPr><w:pStyle w:val="TableText"/></w:pPr>${inline(c.tokens,header?'<w:b/>':'')}</w:p></w:tc>`).join('')}</w:tr>`;}
  return `<w:tbl><w:tblPr><w:tblW w:w="9200" w:type="dxa"/><w:tblLayout w:type="fixed"/><w:tblBorders><w:top w:val="single" w:sz="4" w:color="DCE3DF"/><w:bottom w:val="single" w:sz="4" w:color="DCE3DF"/><w:insideH w:val="single" w:sz="4" w:color="DCE3DF"/></w:tblBorders><w:tblCellMar><w:top w:w="100" w:type="dxa"/><w:left w:w="100" w:type="dxa"/><w:bottom w:w="100" w:type="dxa"/><w:right w:w="100" w:type="dxa"/></w:tblCellMar></w:tblPr><w:tblGrid>${Array.from({length:cols},(_,i)=>`<w:gridCol w:w="${widths[i]||Math.floor(9200/cols)}"/>`).join('')}</w:tblGrid>${row(t.header,true)}${t.rows.map(r=>row(r,false)).join('')}</w:tbl><w:p/>`;}
 function blocks(tokens,quote=false){return tokens.map(t=>{
  if(t.type==='space')return '';
  if(t.type==='heading'){const isChapter=t.depth===2&&/^(\d+\.|Appendix |Lampiran )/.test(t.text);const style=t.depth===1?'Title':isChapter?'Heading1':t.depth===2?'Subtitle':'Heading2';return paragraph(t.tokens,style,isChapter?'<w:pageBreakBefore/>':'');}
  if(t.type==='paragraph'||t.type==='text')return paragraph(t.tokens||marked.lexer(t.text)[0]?.tokens,quote?'Quote':'Normal');
  if(t.type==='blockquote')return blocks(t.tokens,true);
  if(t.type==='table')return table(t);
  if(t.type==='list'){const id=nums.length+1;nums.push({id,ordered:t.ordered,start:t.start||1});return t.items.map(item=>item.tokens.filter(a=>a.type!=='space').map(a=>paragraph(a.tokens||marked.lexer(a.text)[0]?.tokens,'Normal',`<w:numPr><w:ilvl w:val="0"/><w:numId w:val="${id}"/></w:numPr>`)).join('')).join('');}
  throw Error('Unsupported DOCX token '+t.type);
 }).join('');}
 const body=blocks(marked.lexer(md));
 const numbering=nums.map(n=>`<w:abstractNum w:abstractNumId="${n.id}"><w:multiLevelType w:val="singleLevel"/><w:lvl w:ilvl="0"><w:start w:val="${n.start}"/><w:numFmt w:val="${n.ordered?'decimal':'bullet'}"/><w:lvlText w:val="${n.ordered?'%1.':'•'}"/><w:lvlJc w:val="left"/><w:pPr><w:tabs><w:tab w:val="num" w:pos="360"/></w:tabs><w:ind w:left="360" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum><w:num w:numId="${n.id}"><w:abstractNumId w:val="${n.id}"/></w:num>`).join('');
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'kota-buku-docx-'));
 function write(file,data){const p=path.join(dir,file);fs.mkdirSync(path.dirname(p),{recursive:true});fs.writeFileSync(p,data);}
 const wns='http://schemas.openxmlformats.org/wordprocessingml/2006/main',rns='http://schemas.openxmlformats.org/officeDocument/2006/relationships';
 write('[Content_Types].xml',`<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/><Override PartName="/word/numbering.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml"/><Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/></Types>`);
 write('_rels/.rels',`<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="${rns}/officeDocument" Target="word/document.xml"/><Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/></Relationships>`);
 write('docProps/core.xml',`<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>${x(title)}</dc:title><dc:creator>Sifututor</dc:creator><dc:language>${lang==='en'?'en-GB':'ms-MY'}</dc:language><dc:description>Discussion draft, 7 September 2026. Not approved for distribution.</dc:description></cp:coreProperties>`);
 write('word/document.xml',`<?xml version="1.0" encoding="UTF-8" standalone="yes"?><w:document xmlns:w="${wns}" xmlns:r="${rns}"><w:body>${body}<w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1000" w:right="1353" w:bottom="1000" w:left="1353" w:header="400" w:footer="400"/></w:sectPr></w:body></w:document>`);
 write('word/_rels/document.xml.rels',`<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="${rns}/styles" Target="styles.xml"/><Relationship Id="rId2" Type="${rns}/numbering" Target="numbering.xml"/>${relationships.join('')}</Relationships>`);
 write('word/numbering.xml',`<w:numbering xmlns:w="${wns}">${numbering}</w:numbering>`);
 function style(id,size,bold,spacing,extra='',color='20332F'){return `<w:style w:type="paragraph" w:styleId="${id}"><w:name w:val="${id}"/><w:basedOn w:val="Normal"/><w:pPr><w:spacing w:after="${spacing}"/>${extra}</w:pPr><w:rPr><w:sz w:val="${size}"/>${bold?'<w:b/>':''}<w:color w:val="${color}"/></w:rPr></w:style>`;}
 write('word/styles.xml',`<w:styles xmlns:w="${wns}"><w:docDefaults><w:rPrDefault><w:rPr><w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="22"/><w:lang w:val="${lang==='en'?'en-GB':'ms-MY'}"/></w:rPr></w:rPrDefault><w:pPrDefault><w:pPr><w:spacing w:after="160" w:line="300" w:lineRule="auto"/><w:widowControl/></w:pPr></w:pPrDefault></w:docDefaults><w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/></w:style>${style('Title',64,true,480,'<w:keepNext/>')}${style('Subtitle',32,false,350,'<w:keepNext/>')}${style('Heading1',36,true,300,'<w:keepNext/><w:outlineLvl w:val="0"/>')}${style('Heading2',26,true,220,'<w:keepNext/><w:outlineLvl w:val="1"/>')}${style('Quote',22,false,180,'<w:ind w:left="300" w:right="200"/><w:shd w:fill="F0F5EF"/>','294438')}${style('TableText',20,false,100)}</w:styles>`);
 const archive=path.join(os.tmpdir(),path.basename(dir)+'.docx');
 execFileSync('/usr/bin/zip',['-q','-r',archive,'.'],{cwd:dir});
 fs.copyFileSync(archive,destination);
 return {tables:(body.match(/<w:tbl>/g)||[]).length,headings:(body.match(/w:val="Heading1"/g)||[]).length};
};
