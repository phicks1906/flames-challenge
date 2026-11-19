'use strict';
// A3.6 staging-only: verify actual PostgREST select contracts used by v1395.
// Read-only. No auth signup, no database writes, no production calls.
const assert=require('node:assert/strict');
const base=process.env.FC_A36_STAGING_URL;
const key=process.env.FC_A36_STAGING_PUBLISHABLE_KEY;
assert.equal(base,'https://pcmobielrhdfzivrwvuu.supabase.co');
assert.ok(key?.startsWith('sb_publishable_'));
const queries=[
 ['following-entry-query', "/rest/v1/entries?select=id,user_id,challenge_id,created_at,moderation_status,sd_round,challenge:challenges!entries_challenge_id_fkey(id,title,is_public,status,created_at,submission_deadline,voting_end,voided_at,is_championship,sd_phase,sd_round,sd_submit_end,sd_vote_end)&moderation_status=in.(approved,clear)&order=created_at.desc&limit=1"],
 ['followed-challenge-hydration', "/rest/v1/challenges?select=*,creator:profiles!challenges_creator_id_fkey(id,name,avatar)&is_public=eq.true&limit=1"],
 ['followed-entry-hydration', "/rest/v1/entries?select=id,challenge_id,moderation_status,sd_round&limit=1"],
 ['official-winners', "/rest/v1/challenge_result_winners?select=challenge_id,user_id&limit=1"],
 ['official-results', "/rest/v1/challenge_results?select=challenge_id,resolution,winner_count&limit=1"],
 ['following-relations', "/rest/v1/follows?select=follower_id,followee_id&limit=1"]
];
(async()=>{
 for(const [label,path] of queries){
  const resp=await fetch(base+path,{headers:{apikey:key,Accept:'application/json'},signal:AbortSignal.timeout(13000)});
  const payload=await resp.text();
  if(!resp.ok) {
   let code='unknown';try{const parsed=JSON.parse(payload);code=parsed.code||parsed.message||code}catch{}
   throw Error(label+' POSTGREST HTTP '+resp.status+' '+String(code).slice(0,160));
  }
  const json=JSON.parse(payload);
  assert.ok(Array.isArray(json),'Expected array from '+label);
  console.log('PASS_A36_STAGING_API '+label+' contract_valid');
 }
 console.log('PASS A3.6 LIVE STAGING POSTGREST READ CONTRACTS: 6 queries, no users or writes');
})().catch(e=>{console.error('FAIL_A36_STAGING_API '+String(e.message).slice(0,260));process.exitCode=1});
