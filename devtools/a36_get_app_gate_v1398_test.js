'use strict';
// Regression of exact staged v1398 one-time Get App prompt gating.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const source=fs.readFileSync('index.html','utf8');
assert.match(source,/v1398 · a36-safe-get-app-after-ember/);
const start=source.indexOf('function maybeShowGetAppPrompt() {');
const stop=source.indexOf('// Nothing to ask for',start);
assert.ok(start>0&&stop>start,'Exact Get App gate source not found');
const prefix=source.slice(start,stop);
// The rest of the function is not executed: only actual gate statements are
// exercised. The sentinel represents reaching existing app install content.
const fn=new Function('state','localStorage','GETAPP_PROMPT_KEY','document','guidelinesAcked','setTimeout',
 prefix+'\n    return "allowed";\n  } catch(error){throw error;}\n}\nreturn maybeShowGetAppPrompt();');
const profile={id:'fixture',onboarding_version:1103,walkthrough_seen_version:1103};
const setup=({emberOpen=false,version=1103,walkthrough=1103,accepted=true,blocked=false}={})=>{
 const callbacks=[],scheduled=[];
 const daily={open:emberOpen,dataset:{},addEventListener(name,cb,opts){callbacks.push({name,cb,opts})}};
 const ctx={
  state:{profile:{...profile,onboarding_version:version,walkthrough_seen_version:walkthrough}},
  localStorage:{getItem(){return null}},
  document:{getElementById(){return daily},querySelector(){return blocked?{}:null}},
  guidelinesAcked(){return accepted},setTimeout(fn,delay){scheduled.push({fn,delay})}
 };
 return {run:()=>fn(ctx.state,ctx.localStorage,'getapp-test',ctx.document,ctx.guidelinesAcked,ctx.setTimeout),
   daily,callbacks,scheduled};
};
let t=setup({emberOpen:true});
assert.equal(t.run(),undefined,'Native Ember must block the install prompt');
assert.equal(t.run(),undefined,'Repeated check must still block Get App');
assert.equal(t.callbacks.length,1,'Exactly one resume listener per Ember instance');
assert.equal(t.callbacks[0].name,'close');
assert.equal(t.callbacks[0].opts.once,true);
t.callbacks[0].cb();
assert.equal(t.scheduled.length,1,'Get App should resume after native dialog closes');
assert.equal(t.scheduled[0].delay,600);
assert.equal(t.daily.dataset.fcGetAppAfterEmberV1398,undefined,'Resume marker reset');
assert.equal(setup({version:1}).run(),undefined,'Required account setup blocks install prompt');
assert.equal(setup({walkthrough:0}).run(),undefined,'First-run guide blocks install prompt');
assert.equal(setup({accepted:false}).run(),undefined,'Guidelines block install prompt');
assert.equal(setup({blocked:true}).run(),undefined,'Active DOM dialogs block install prompt');
assert.equal(setup().run(),'allowed','After all dialogs close, install prompt may appear normally');
assert.match(source,/localStorage\.setItem\(GETAPP_PROMPT_KEY, '1'\)/,
 'Original once-only Get App lifetime must remain');
console.log('PASS v1398: actual Get App gate waits for native Ember, first-run consent, and other modals; resumes once after close');
