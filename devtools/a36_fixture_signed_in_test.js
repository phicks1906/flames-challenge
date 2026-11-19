'use strict';
// A3.6: signed-in staging fixture test, no signup, no account changes or production calls.
const assert=require('node:assert/strict');
const host='https://pcmobielrhdfzivrwvuu.supabase.co';
const key=process.env.FC_A36_STAGING_PUBLISHABLE_KEY;
const email=process.env.FC_A36_TEST_EMAIL;
const password=process.env.FC_A36_TEST_PASSWORD;
if(!key?.startsWith('sb_publishable_')||!email||!password)
 throw Error('Private staging test credentials are not configured');
async function api(method,path,body,token) {
 const headers={apikey:key,Accept:'application/json'};
 if(body!==undefined){headers['Content-Type']='application/json';headers.Prefer='return=representation';}
 if(token)headers.Authorization='Bearer '+token;
 const response=await fetch(host+path,{method,headers,
  body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(13000)});
 const raw=await response.text();
 let data;try{data=JSON.parse(raw)}catch{data={}};
 if(!response.ok)throw Error('Staging '+method+' '+path.split('?')[0]+' HTTP '+response.status+
   ' code '+String(data?.code||data?.error_code||'unknown').slice(0,50));
 return data;
}
async function one(path,token) {
 const rows=await api('GET',path,undefined,token);
 assert.equal(rows.length,1,'Exactly one A3.6 fixture is required');
 return rows[0];
}
(async()=>{
 const signed=await api('POST','/auth/v1/token?grant_type=password',{email,password});
 assert.ok(signed.access_token&&signed.user?.id,'No signed-in session');
 const jwt=signed.access_token,member=signed.user.id;
 const who=await api('GET','/auth/v1/user',undefined,jwt);
 assert.equal(who.id,member,'JWT user does not match');
 console.log('PASS real staging Auth sign-in');
 const live=await one('/rest/v1/challenges?select=id,creator_id&title=eq.FC_A36_V1395_LIVE',jwt);
 const future=await one('/rest/v1/challenges?select=id&title=eq.FC_A36_V1395_FOLLOW_NEXT',jwt);
 const settled=await one('/rest/v1/challenges?select=id&title=eq.FC_A36_V1395_SETTLED',jwt);
 assert.equal(live.creator_id,member,'Secret must refer to the designated test voter');
 const entries=await api('GET','/rest/v1/entries?select=id,user_id,moderation_status&challenge_id=eq.'+live.id,undefined,jwt);
 assert.equal(entries.length,2,'Two competing entries should be visible');
 const opponent=entries.find(e=>e.user_id!==member&&['clear','approved'].includes(e.moderation_status));
 assert.ok(opponent,'Opponent entry missing');
 const followsBefore=await api('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+member,undefined,jwt);
 const voteBefore=await api('GET','/rest/v1/entry_votes?select=entry_id,challenge_id&voter_id=eq.'+member,undefined,jwt);
 const existing=voteBefore.find(v=>v.challenge_id===live.id);
 if(!existing){
  assert.equal(followsBefore.length,0,'Test voter already follows someone');
  await api('POST','/rest/v1/entry_votes',{challenge_id:live.id,entry_id:opponent.id,voter_id:member},jwt);
  const noFollow=await api('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+member,undefined,jwt);
  assert.equal(noFollow.length,0,'A vote incorrectly created a Follow');
  console.log('PASS real vote does not auto-follow');
 } else assert.equal(existing.entry_id,opponent.id,'Unexpected existing ballot');
 const history=await api('GET','/rest/v1/entry_votes?select=entry_id,challenge_id&voter_id=eq.'+member,undefined,jwt);
 assert.ok(history.some(v=>v.challenge_id===live.id&&v.entry_id===opponent.id));
 console.log('PASS signed-in voter history');
 if(!followsBefore.some(f=>f.followee_id===opponent.user_id))
  await api('POST','/rest/v1/follows',{follower_id:member,followee_id:opponent.user_id},jwt);
 const follows=await api('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+member,undefined,jwt);
 assert.ok(follows.some(f=>f.followee_id===opponent.user_id),'Follow not persisted');
 const discovered=await api('GET',
  '/rest/v1/entries?select=id,user_id,challenge_id,moderation_status,challenge:challenges!entries_challenge_id_fkey(id,title,is_public,status,created_at,submission_deadline,voting_end,voided_at,is_championship,sd_phase,sd_round,sd_submit_end,sd_vote_end)&user_id=eq.'+opponent.user_id+'&moderation_status=in.(clear,approved)',
  undefined,jwt);
 assert.ok(discovered.some(e=>e.challenge_id===future.id&&e.challenge?.is_public),'Off-feed future entry not found');
 console.log('PASS signed-in Following discovers off-feed entry');
 const result=await one('/rest/v1/challenge_results?select=challenge_id,resolution,winner_count&challenge_id=eq.'+settled.id,jwt);
 const winners=await api('GET','/rest/v1/challenge_result_winners?select=challenge_id,user_id,entry_id&challenge_id=eq.'+settled.id,undefined,jwt);
 assert.equal(winners.length,result.winner_count,'Official winner row count mismatch');
 assert.ok(winners.some(w=>w.user_id===opponent.user_id),'Test fixture official winner mismatch');
 console.log('PASS settled result and official winner readable');
 console.log('PASS A3.6 authenticated staging REST journey (not iPhone UI)');
})().catch(e=>{console.error('FAIL A3.6 staging Auth: '+String(e.message).slice(0,280));process.exitCode=1});
