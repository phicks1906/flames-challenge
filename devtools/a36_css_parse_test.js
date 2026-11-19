'use strict';
/* v1394 staging CSS parsing gate.
 * Parses every inline <style> block from the actual root index.html.
 * No production writes and no network calls from app code. */
const fs=require('node:fs');
const assert=require('node:assert/strict');
const postcss=require('/tmp/fc-a36-css/node_modules/postcss');
const html=fs.readFileSync('index.html','utf8');
const blocks=[...html.matchAll(/<style\b([^>]*)>([\s\S]*?)<\/style\s*>/gi)];
const failures=[];
let parsed=0, rules=0, declarations=0;
for (let i=0;i<blocks.length;i++) {
 const match=blocks[i], before=html.slice(0,match.index);
 const startLine=before.split('\n').length;
 try {
  const ast=postcss.parse(match[2],{from:'index.html:style-'+(i+1)});
  parsed++;
  ast.walkRules(()=>rules++);
  ast.walkDecls(()=>declarations++);
 } catch(err) {
  failures.push({
   styleBlock:i+1,approximateLine:startLine+(err.line||0),
   reason:err.reason||err.message,
   at:String(err.line||'?')+':'+String(err.column||'?'),
  });
 }
}
console.log(JSON.stringify({stylesFound:blocks.length,stylesParsed:parsed,
  cssRules:rules,cssDeclarations:declarations,parseErrors:failures.slice(0,25)},null,2));
assert.ok(blocks.length>=150,'Unexpected number of CSS blocks; parser may not be reviewing full app');
assert.equal(failures.length,0,'Structural CSS parsing failed');
console.log('PASS: all staged inline CSS style blocks parsed with PostCSS');
