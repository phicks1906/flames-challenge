'use strict';
const fs=require('node:fs'),assert=require('node:assert/strict');
const s=fs.readFileSync('index.html','utf8');
assert.match(s,/v1399 · a36-following-nav-clearance/);
const tag='<style id="fc-a36-following-nav-v1399">';
assert.equal(s.split(tag).length-1,1,'One scoped Following layout override');
const start=s.indexOf(tag),end=s.indexOf('</style>',start);
assert.ok(start>0&&end>start);
const css=s.slice(start,end);
assert.match(css,/body:has\(#followingSheet\.open\)\s+#bottomNav\s*\{[\s\S]*?visibility:\s*hidden\s*!important\s*;[\s\S]*?pointer-events:\s*none\s*!important\s*;/,
 'Open Following must hide the fixed primary bottom navigation');
assert.match(css,/#followingSheet\.open\s+#followingList\s*\{[\s\S]*?env\(safe-area-inset-bottom,\s*0px\)/,
 'Following rows must clear iPhone home indicator');
assert.ok(s.indexOf('id="followingSheet"')<start,'Layout override must follow real Following sheet markup');
console.log('PASS v1399: Following bottom-nav exclusion and safe-area margin scoped to Connections modal');
