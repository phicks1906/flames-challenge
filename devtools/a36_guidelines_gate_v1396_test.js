'use strict';
// Verify the actual staged v1396 optional-guide gate; no mock replacement of source.
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');
const source=fs.readFileSync('index.html','utf8');
assert.match(source,/v139(?:6 · a36-guidelines-before-welcome-guide|7 · a36-ember-after-onboarding|8 · a36-safe-get-app-after-ember|9 · a36-following-nav-clearance)/);
const begin=source.indexOf('window.fcMaybeOpenOptionalGuideV1103 = function(){');
const end=source.indexOf('window.fcOpenHowItWorks =',begin);
assert.ok(begin>=0&&end>begin,'Real optional guide function absent');
const body=source.slice(begin,end).trim();
assert.match(body,/!guidelinesAcked\(\)/,'Must prevent scheduling before Guidelines acceptance');
assert.match(body,/&& guidelinesAcked\(\)/,'Must recheck at timer firing');
const callbacks=[];
let accepted=false,modalOpen=true,seen=false,complete=true,opened=0;
const ctx={
 window:{},state:{profile:{id:'staging-test'}},optionalTimer:0,
 clearTimeout(){},setTimeout(fn){callbacks.push(fn);return callbacks.length},
 profileComplete:()=>complete,guideSeen:()=>seen,guidelinesAcked:()=>accepted,
 document:{getElementById:()=>({classList:{contains:()=>modalOpen}})},
 openGuide:()=>opened++,
};
vm.createContext(ctx);
vm.runInContext(body,ctx);
const attempt=()=>ctx.window.fcMaybeOpenOptionalGuideV1103();
attempt();
assert.equal(callbacks.length,0,'Must not schedule a guide before Guidelines consent');
accepted=true;attempt();
assert.equal(callbacks.length,0,'Must not schedule over an open Guidelines modal');
modalOpen=false;attempt();
assert.equal(callbacks.length,1,'Accepted user should get optional guide');
modalOpen=true;callbacks.pop()();
assert.equal(opened,0,'A modal opened during timer must prevent guide');
modalOpen=false;attempt();
callbacks.pop()();
assert.equal(opened,1,'Optional guide should appear after mandatory modal closes');
seen=true;attempt();
assert.equal(callbacks.length,0,'Guide already seen should not reopen');
seen=false;complete=false;attempt();
assert.equal(callbacks.length,0,'Incomplete required onboarding should not get optional guide');
assert.match(source,/if \(wasUnacked\) maybeStartTour\(\)/,'Acknowledgement must continue optional guide');
console.log('PASS v1396: required Guidelines before guide, recheck timer, no overlap, one-time guide, incomplete account protected');
