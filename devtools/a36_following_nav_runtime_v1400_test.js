'use strict';
/* Tests the actual staged v1400 Following nav implementation, including
   restoring inline styles after explicit or indirect dialog closure. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const src=fs.readFileSync('index.html','utf8');
assert.match(src,/v1400 · a36-following-nav-runtime/);
const start=src.indexOf('let fcA36FollowingNavPriorV1400 = null;');
const end=src.indexOf('async function openFollowingSheet()',start);
assert.ok(start>0&&end>start,'Actual runtime nav guard missing');
const original=src.slice(start,end);
const open=src.slice(end,src.indexOf('function switchFollowTab(',end));
const close=src.slice(src.indexOf('function closeFollowingSheet()',end),src.indexOf('// ── ENTRY BADGES',end));
assert.match(open,/fcA36WatchFollowingNavV1400\(\)/);
assert.match(open,/fcA36SyncFollowingNavV1400\(\)/);
assert.match(close,/fcA36SyncFollowingNavV1400\(\)/);
function fixture(init={}){
 const props={...init};
 const priority={visibility:init.visibility?'important':'', 'pointer-events':init['pointer-events']?'important':''};
 const style={
  getPropertyValue(p){return props[p]||''},
  getPropertyPriority(p){return priority[p]||''},
  setProperty(p,v,q=''){props[p]=v;priority[p]=q},
  removeProperty(p){delete props[p];delete priority[p]}
 };
 let open=false,observer=null,observerCount=0;
 const sheet={classList:{contains(name){return name==='open'&&open}},dataset:{}};
 const nav={style};
 const ctx={document:{getElementById(id){return id==='bottomNav'?nav:id==='followingSheet'?sheet:null}},
  MutationObserver:class{constructor(callback){observer=callback}observe(target,options){assert.equal(target,sheet);assert.deepEqual(Array.from(options.attributeFilter),['class']);observerCount++}}};
 vm.createContext(ctx);
 vm.runInContext(original+'\nthis.sync=fcA36SyncFollowingNavV1400;this.watch=fcA36WatchFollowingNavV1400;',ctx);
 return {ctx,sheet,nav,style,props,priority,setOpen(v){open=v;if(observer)observer()},getObserverCount(){return observerCount}};
}
let x=fixture();
x.ctx.watch();x.ctx.watch();assert.equal(x.getObserverCount(),1,'Only one class observer');
x.setOpen(true);
assert.equal(x.style.getPropertyValue('visibility'),'hidden');
assert.equal(x.style.getPropertyPriority('visibility'),'important');
assert.equal(x.style.getPropertyValue('pointer-events'),'none');
assert.equal(x.style.getPropertyPriority('pointer-events'),'important');
x.ctx.sync();x.setOpen(false);
assert.equal(x.style.getPropertyValue('visibility'),'');
assert.equal(x.style.getPropertyValue('pointer-events'),'');
x.setOpen(true);x.setOpen(false);
assert.equal(x.style.getPropertyValue('visibility'),'','All repeated opens must restore original nav');
x=fixture({visibility:'visible','pointer-events':'auto'});
x.ctx.watch();x.setOpen(true);x.setOpen(false);
assert.equal(x.style.getPropertyValue('visibility'),'visible','Preserve preexisting inline nav visibility');
assert.equal(x.style.getPropertyPriority('visibility'),'important');
assert.equal(x.style.getPropertyValue('pointer-events'),'auto','Preserve preexisting inline pointer handling');
console.log('PASS v1400: actual Following nav override hides primary nav and restores original styles on any close path');
