'use strict';
// A3.6 staging only: real Supabase Auth sign-up/sign-in and RLS-backed REST.
// Credentials are provided as private GitHub Actions secrets, never committed or logged.
const assert=require('node:assert/strict');
const base=process.env.FC_A36_STAGING_URL;
const apiKey=process.env.FC_A36_STAGING_PUBLISHABLE_KEY;
const runId=String(process.env.GITHUB_RUN_ID||'').trim();
assert.equal(base,'https://pcmobielrhdfzivrwvuu.supabase.co','STOP: wrong project target');
assert.ok(apiKey&&apiKey.startsWith('sb_publishable_'),'STOP: missing publishable key');
assert.match(runId,/^\d{6,15}$/,'STOP: require CI run ID');
const email=process.env.FC_A36_TEST_EMAIL;
const password=process.env.FC_A36_TEST_PASSWORD;
assert.ok(email && email.includes('@') && password && password.length>=16,
  'STOP: configure private staging-only test-account email and password');
const title='FC_A36_E2E_'+runId+'_LIVE';
const nextTitle='FC_A36_E2E_'+runId+'_FOLLOW_NEXT';
const started=Date.now();
async function req(method,url,body,token){
 const headers={apikey:apiKey,Accept:'application/json'};
 if(body!==undefined)headers['Content-Type']='application/json';
 if(token)headers.Authorization='Bearer '+token;
 const response=await fetch(base+url,{method,headers,body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(12000)});
 const raw=await response.text();
 let data;try{data=JSON.parse(raw)}catch{data={}};
 return {ok:response.ok,status:response.status,data};
}
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
async function waitFor(label,fn,timeout=140){
 for(let elapsed=0;elapsed<=timeout;elapsed+=4){
  const found=await fn();if(found!==null)return found;
  if(elapsed%24===0)console.log('A36_WAIT_'+label+' elapsed='+elapsed+'s');
  await sleep(4000);
 }
 throw new Error('Timed out waiting for '+label);
}
(async()=>{
 // Use a dedicated staging-only account, created through supported Supabase Auth.
 // Do not attempt email signup or issue repetitive logins without credentials.
 const session=await waitFor('SEEDED_AUTH_LOGIN',async()=>{
  const auth=await req('POST','/auth/v1/token?grant_type=password',{email,password});
  if(auth.ok&&auth.data.access_token)return auth.data;
  if([400,401,404,422,429].includes(auth.status))return null;
  throw new Error('Staging signin status='+auth.status+' code='+String(auth.data.code||auth.data.error_code||'unknown'));
 },220);
 const userId=session.user?.id;
 if(!userId)throw new Error('GoTrue login returned no user identity');
 const token=session.access_token;
 const who=await req('GET','/auth/v1/user',undefined,token);
 assert.ok(who.ok&&who.data.id===userId,'Real Auth session did not resolve to voter');
 console.log('A36_REAL_AUTH_SESSION_OK');
 const fixture=await waitFor('FIXTURE_SEEDED',async()=>{
  const profile=await req('GET','/rest/v1/profiles?select=id&id=eq.'+userId,undefined,token);
  const challenges=await req('GET','/rest/v1/challenges?select=id,title&title=eq.'+title,undefined,token);
  const next=await req('GET','/rest/v1/challenges?select=id,title&title=eq.'+nextTitle,undefined,token);
  if(!profile.ok||!challenges.ok||!next.ok)
   throw new Error('Authenticated staging PostgREST read unavailable');
  if(profile.data.length&&challenges.data.length&&next.data.length)
   return {challengeId:challenges.data[0].id,nextChallengeId:next.data[0].id};
  return null;
 },220);
 const ballot=await req('GET','/rest/v1/entries?select=id,user_id,challenge_id,moderation_status&challenge_id=eq.'+fixture.challengeId,undefined,token);
 assert.ok(ballot.ok&&ballot.data.length>=2,'Member cannot read competition entries');
 const choice=ballot.data.find(x=>['clear','approved'].includes(x.moderation_status));
 assert.ok(choice,'No authorized eligible entry');
 const beforeFollow=await req('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+userId,undefined,token);
 assert.ok(beforeFollow.ok&&beforeFollow.data.length===0,'Follow already present');
 const voted=await req('POST','/rest/v1/entry_votes',{challenge_id:fixture.challengeId,entry_id:choice.id,voter_id:userId},token);
 assert.ok(voted.ok,'Real authenticated ballot insert failed status='+voted.status+' code='+String(voted.data.code||'unknown'));
 const voteHistory=await req('GET','/rest/v1/entry_votes?select=id,entry_id,challenge_id&voter_id=eq.'+userId,undefined,token);
 assert.ok(voteHistory.ok&&voteHistory.data.some(v=>v.entry_id===choice.id),'Vote history absent');
 const stillNoFollow=await req('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+userId,undefined,token);
 assert.ok(stillNoFollow.ok&&stillNoFollow.data.length===0,'Vote created implicit Follow');
 console.log('A36_REAL_VOTE_WITHOUT_FOLLOW_OK');
 const followed=await req('POST','/rest/v1/follows',{follower_id:userId,followee_id:choice.user_id},token);
 assert.ok(followed.ok,'Explicit Follow insert failed status='+followed.status+' code='+String(followed.data.code||'unknown'));
 const verifiedFollow=await req('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+userId,undefined,token);
 assert.ok(verifiedFollow.ok&&verifiedFollow.data.some(f=>f.followee_id===choice.user_id),'Follow not persisted');
 const discover=await req('GET','/rest/v1/entries?select=id,user_id,challenge_id,moderation_status,challenge:challenges!entries_challenge_id_fkey(id,title,is_public,status,submission_deadline,voting_end,sd_phase,sd_round,voided_at,sd_submit_end,sd_vote_end)&user_id=eq.'+choice.user_id+'&moderation_status=in.(clear,approved)',undefined,token);
 assert.ok(discover.ok,'Following joined query failed status='+discover.status+' code='+String(discover.data.code||'unknown'));
 assert.ok(discover.data.some(e=>e.challenge_id===fixture.nextChallengeId&&e.challenge?.is_public===true),'Following failed to discover off-feed newer entry');
 console.log('A36_REAL_FOLLOW_OFFFEED_DISCOVERY_OK');
 const settled=await waitFor('OFFICIAL_SETTLEMENT',async()=>{
  const res=await req('GET','/rest/v1/challenge_results?select=challenge_id,resolution,winner_count&challenge_id=eq.'+fixture.challengeId,undefined,token);
  if(!res.ok)throw new Error('Official results select denied status='+res.status);
  return res.data.length===1?res.data[0]:null;
 },220);
 const winners=await req('GET','/rest/v1/challenge_result_winners?select=challenge_id,user_id,entry_id&challenge_id=eq.'+fixture.challengeId,undefined,token);
 assert.ok(winners.ok&&winners.data.length===settled.winner_count,'Official winner rows inaccessible or incorrect');
 console.log('A36_REAL_RESULT_RETURN_OK pick_won='+winners.data.some(x=>x.entry_id===choice.id));
 console.log('PASS A3.6 ACTUAL STAGING AUTH: login, own votes, no automatic Follow, explicit Follow, off-feed entry, official result');
})().catch(e=>{console.error('FAIL A3.6 STAGING: '+String(e.message||e).slice(0,500));process.exitCode=1;});
