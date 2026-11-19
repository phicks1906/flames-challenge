'use strict';
const assert=require('node:assert/strict');
const base=process.env.FC_A36_STAGING_URL;
const key=process.env.FC_A36_STAGING_PUBLISHABLE_KEY;
assert.equal(base,'https://pcmobielrhdfzivrwvuu.supabase.co');
assert.ok(key?.startsWith('sb_publishable_'));
(async()=>{
 const response=await fetch(base+'/auth/v1/settings',{headers:{apikey:key},signal:AbortSignal.timeout(12000)});
 const data=await response.json().catch(()=>({}));
 const inspect=(obj,field)=>{const path=field.split('.');let v=obj;for(const p of path){v=v?.[p];}return v;};
 console.log('STAGING_AUTH_SETTINGS_HTTP',response.status);
 for(const field of ['disable_signup','mailer_autoconfirm','external.email','external.anonymous','external.phone','external.apple','external.google']) {
  const v=inspect(data,field);if(typeof v==='boolean')console.log('STAGING_AUTH_OPTION',field,v);
 }
 if(!response.ok)throw Error('Cannot inspect staging auth settings');
 console.log('PASS read-only staging Auth capabilities inspected; no users created');
})().catch(e=>{console.error('A36_AUTH_SETTINGS_PROBE_FAILED '+e.message);process.exitCode=1;});