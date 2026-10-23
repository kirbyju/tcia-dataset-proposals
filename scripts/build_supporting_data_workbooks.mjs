// Build matching Excel preparation materials from the guide's generated data.
// Requires @oai/artifact-tool; see README for runtime setup. Never reads user data.
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL, fileURLToPath } from 'node:url';
const artifactModule = process.env.ARTIFACT_TOOL_MODULE;
const {Workbook, SpreadsheetFile} = await import(artifactModule ? pathToFileURL(artifactModule).href : '@oai/artifact-tool');
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.resolve(process.argv[2] || path.join(root, 'docs/supporting-data'));
const guide = JSON.parse(await fs.readFile(path.join(output, 'guide-data.json'), 'utf8'));
const instructions = await fs.readFile(path.join(output, 'downloads/README.txt'), 'utf8');
const dictHeaders=['Table','Field','Basis','Type','Expectation','Description','Fictional example','Notes','Source','CDE references'];
const dictionary=guide.fields.map(f=>[f.table,f.name,f.basis,f.type,f.required,f.description,f.example,f.note,f.source,f.terms.map(t=>`${t.Origin||''}:${t.Code||''} v${t.Version||''}`).join('; ')]);
function style(sheet, columns, rows, input=false){
  const r=sheet.getRangeByIndexes(0,0,Math.max(rows,2),columns);
  r.format.font={name:'Arial',size:10,color:'#222222'};
  r.format.verticalAlignment='center';r.format.columnWidth=25;r.format.rowHeight=23;
  const header=sheet.getRangeByIndexes(0,0,1,columns);
  header.format={fill:'#042B5B',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:44};
  sheet.showGridLines=false;sheet.freezePanes.freezeRows(1);
  if(columns>5)sheet.freezePanes.freezeColumns(1);
  if(input)sheet.tabColor='#2467A8';
}
for(const kind of ['templates','examples']){
  const wb=Workbook.create();
  const intro=wb.worksheets.add('Instructions');
  const lines=instructions.split('\n\n').map((text,i)=>[i===0?'TCIA supporting data':`Preparation note ${i}`,text.replaceAll('\n',' ')]);
  intro.getRange('A1:B1').values=[['Topic','Instructions']];
  intro.getRangeByIndexes(1,0,lines.length,2).values=lines;
  style(intro,2,lines.length+1);intro.getRange('A:A').format.columnWidth=26;
  intro.getRange('B:B').format.columnWidth=110;
  intro.getRangeByIndexes(1,1,lines.length,1).format.wrapText=true;
  intro.getRangeByIndexes(1,0,lines.length,2).format.autofitRows();
  for(const t of guide.tables){
    const sheet=wb.worksheets.add(t.name);
    sheet.getRangeByIndexes(0,0,1,t.columns.length).values=[t.columns];
    const rows=kind==='examples'?t.rows:[];
    if(rows.length)sheet.getRangeByIndexes(1,0,rows.length,t.columns.length).values=rows;
    style(sheet,t.columns.length,Math.max(rows.length+1,12),true);
    sheet.getRangeByIndexes(1,0,Math.max(rows.length,10),t.columns.length).setNumberFormat('@');
    // Numbers in additional acquisition tables remain typed numeric values.
    for(let r=0;r<rows.length;r++)for(let c=0;c<t.columns.length;c++)if(typeof rows[r][c]==='number')sheet.getCell(r+1,c).setNumberFormat('0.########');
    if(t.basis==='additional')sheet.tabColor='#FDB835';
    wb.notes.add({id:`${t.name}:A1`,target:{cell:{sheetName:sheet.name,sheetId:sheet.sheetId,address:'A1'}},authorId:'',createdAt:'',body:{plainText:`${t.description} ${t.basis==='additional'?'Additional recommended metadata outside the MDF model.':'Submission model preparation table.'}`}});
  }
  const dict=wb.worksheets.add('Dictionary');
  dict.getRangeByIndexes(0,0,1,dictHeaders.length).values=[dictHeaders];
  dict.getRangeByIndexes(1,0,dictionary.length,dictHeaders.length).values=dictionary;
  style(dict,dictHeaders.length,dictionary.length+1);
  for(const col of ['F','H']){dict.getRange(`${col}:${col}`).format.columnWidth=70;dict.getRangeByIndexes(1,col==='F'?5:7,dictionary.length,1).format.wrapText=true;}
  dict.getRangeByIndexes(1,0,dictionary.length,dictHeaders.length).format.autofitRows();
  wb.recalculate();
  console.log((await wb.inspect({kind:'region',sheetId:'subject',range:'A1:G3',maxChars:1200,tableMaxRows:3,tableMaxCols:7})).ndjson);
  const file=await SpreadsheetFile.exportXlsx(wb);await file.save(path.join(output,'downloads',`${kind}.xlsx`));
  await fs.rm(path.join(output,'downloads',`${kind}.xlsx.inspect.ndjson`),{force:true});
  if(process.env.GUIDE_PREVIEW_DIR){
    await fs.mkdir(process.env.GUIDE_PREVIEW_DIR,{recursive:true});
    const preview=await wb.render({sheetName:'subject',range:'A1:G4',scale:1,format:'png'});
    await fs.writeFile(path.join(process.env.GUIDE_PREVIEW_DIR,`${kind}-subject.png`),new Uint8Array(await preview.arrayBuffer()));
  }
  console.log(`Exported ${kind}.xlsx with ${guide.tables.length} data sheets`);
}
