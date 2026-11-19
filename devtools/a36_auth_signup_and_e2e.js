'use strict';
/* One-run A3.6 staging Auth fixture: all accounts created via GoTrue signup,
 * never direct writes to auth.users. Secrets stay in this CI process.
 * The operator confirms email in staging, seeds public fixtures, then settles.
 * No backend production endpoint is addressed or modified. */
const assert=require('node:assert/strict');
const crypto=require('node:crypto');
const base=process.env.FC_A36_STAGING_URL;
const apikey=process.env.FC_A36_STAGING_PUBLISHABLE_KEY;
const run=String(process.env.GITHUB_RUN_ID||'');
assert.equal(base,'https://pcmobielrhdfzivrwvuu.supabase.co','STAGING TARGET REQUIRED');
assert.ok(apikey?.startsWith('sb_publishable_'),'PUBLISHABLE KEY REQUIRED');
assert.match(run,/^\d{7,15}$/);
const title='FC_A36_REAL_'+run+'_LIVE';
const nextTitle='FC_A36_REAL_'+run+'_NEXT';
const members=[];
async function call(method,url,body,token) {
 const headers={apikey,Accept:'application/json'};
 if(body!==undefined)headers['Content-Type']='application/json';
 if(token)headers.Authorization='Bearer '+token;
 const response=await fetch(base+url,{method,headers,
  body:body===undefined?undefined:JSON.stringify(body),signal:AbortSignal.timeout(12000)});
 let data;const raw=await response.text();try{data=JSON.parse(raw)}catch{data={}};
 return {ok:response.ok,status:response.status,data};
}
const sleep=t=>new Promise(r=>setTimeout(r,t));
async function poll(name,fn,maxSec) {
 for(let sec=0;sec<=maxSec;sec+=5) {
  const v=await fn();
  if(v!==null)return v;
  if(sec%30===0)console.log('STAGING_WAIT',name,'seconds='+sec);
  await sleep(5000);
 }
 throw new Error('Timed out awaiting '+name);
}
(async()=>{
 for(const role of ['voter','competitor1','competitor2']) {
  const email='fc-a36-'+run+'-'+role+'@flameschallenge.com';
  const password=crypto.randomBytes(30).toString('base64url')+'aA1!';
  const resp=await call('POST','/auth/v1/signup',{email,password,data:{full_name:'A36 Staging '+role}});
  const user=resp.data?.user?.id?resp.data.user:resp.data;
  if(!resp.ok||!user?.id) {
   console.log('STAGING_SIGNUP_STOP',role,'status='+resp.status,
    'code='+String(resp.data?.error_code||resp.data?.code||resp.data?.msg||'unknown').slice(0,120));
   break; // do not hammer a signup rate limiter
  }
  members.push({role,email,password,id:user.id});
  console.log('STAGING_AUTH_CREATED',role,'id='+user.id,'run_id='+run);
 }
 if(members.length<2)throw Error('Insufficient supported Auth signups for voter+competitor');
 console.log('STAGING_AUTH_ACCOUNT_COUNT',members.length,'required_requested=3');
 const logins={};
 for(const person of members) {
  const auth=await poll('CONFIRM_'+person.role,async()=>{
   const res=await call('POST','/auth/v1/token?grant_type=password',{email:person.email,password:person.password});
   if(res.ok&&res.data.access_token)return res.data;
   if([400,401,403,422,429].includes(res.status))return null;
   throw Error('Auth login error '+person.role+' HTTP '+res.status);
  },180);
  assert.equal(auth.user?.id,person.id);
  logins[person.role]=auth.access_token;
  console.log('STAGING_REAL_LOGIN',person.role,'OK');
 }
 const voter=members.find(m=>m.role==='voter');
 const competitor=members.find(m=>m.role==='competitor1');
 const token=logins.voter;
 const who=await call('GET','/auth/v1/user',undefined,token);
 assert.ok(who.ok&&who.data.id===voter.id,'WhoAmI did not validate member');
 console.log('STAGING_USER_JWT_VALIDATED');
 const fixture=await poll('CHALLENGE_ENTRIES_SEEDED',async()=>{
  const live=await call('GET','/rest/v1/challenges?select=id,title&title=eq.'+title,undefined,token);
  const future=await call('GET','/rest/v1/challenges?select=id,title&title=eq.'+nextTitle,undefined,token);
  const profile=await call('GET','/rest/v1/profiles?select=id&id=eq.'+voter.id,undefined,token);
  if(!live.ok||!future.ok||!profile.ok)
    throw Error('Authenticated PostgREST read failed status='+live.status+','+future.status+','+profile.status);
  if(live.data.length===1&&future.data.length===1&&profile.data.length===1)
    return {live:live.data[0].id,future:future.data[0].id};
  return null;
 },180);
 const ballot=await call('GET','/rest/v1/entries?select=id,user_id,challenge_id,moderation_status&challenge_id=eq.'+fixture.live,undefined,token);
 assert.ok(ballot.ok&&ballot.data.length>=2,'Voter cannot view two entries');
 const choice=ballot.data.find(x=>x.user_id===competitor.id&&['clear','approved'].includes(x.moderation_status));
 assert.ok(choice,'Competitor entry not visible');
 const beforeFollow=await call('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+voter.id,undefined,token);
 assert.ok(beforeFollow.ok&&beforeFollow.data.length===0,'Unexpected follow before vote');
 const vote=await call('POST','/rest/v1/entry_votes',{challenge_id:fixture.live,entry_id:choice.id,voter_id:voter.id},token);
 assert.ok(vote.ok,'Authenticated ballot insert failed status='+vote.status+' code='+String(vote.data.code||'unknown'));
 const history=await call('GET','/rest/v1/entry_votes?select=challenge_id,entry_id,voter_id&voter_id=eq.'+voter.id,undefined,token);
 assert.ok(history.ok&&history.data.some(x=>x.entry_id===choice.id),'Voter history did not load');
 const noFollow=await call('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+voter.id,undefined,token);
 assert.ok(noFollow.ok&&noFollow.data.length===0,'Voting improperly auto-followed');
 console.log('STAGING_REAL_VOTE_OK_NO_IMPLICIT_FOLLOW');
 const follow=await call('POST','/rest/v1/follows',{follower_id:voter.id,followee_id:competitor.id},token);
 assert.ok(follow.ok,'Authenticated Follow insert failed status='+follow.status+' code='+String(follow.data.code||'unknown'));
 const relation=await call('GET','/rest/v1/follows?select=followee_id&follower_id=eq.'+voter.id,undefined,token);
 assert.ok(relation.ok&&relation.data.some(x=>x.followee_id===competitor.id),'Follow relation absent');
 const discovery=await call('GET','/rest/v1/entries?select=id,user_id,challenge_id,moderation_status,challenge:challenges!entries_challenge_id_fkey(id,title,is_public,status,submission_deadline,voting_end,sd_phase,sd_round,voided_at,sd_submit_end,sd_vote_end)&user_id=eq.'+competitor.id+'&moderation_status=in.(clear,approved)',undefined,token);
 assert.ok(discovery.ok,'Joined off-feed query failed HTTP '+discovery.status+' code='+String(discovery.data.code||'unknown'));
 assert.ok(discovery.data.some(x=>x.challenge_id===fixture.future&&x.challenge?.is_public===true),'New followed entry not discovered');
 console.log('STAGING_REAL_FOLLOW_OFF_FEED_OK');
 const result=await poll('OFFICIAL_SETTLEMENT',async()=>{
  const r=await call('GET','/rest/v1/challenge_results?select=challenge_id,resolution,winner_count&challenge_id=eq.'+fixture.live,undefined,token);
  if(!r.ok)throw Error('Official result SELECT denied HTTP '+r.status);
  return r.data.length===1?r.data[0]:null;
 },180);
 const winners=await call('GET','/rest/v1/challenge_result_winners?select=challenge_id,user_id,entry_id&challenge_id=eq.'+fixture.live,undefined,token);
 assert.ok(winners.ok&&winners.data.length===result.winner_count,'Official winner read or count failed');
 console.log('STAGING_REAL_SETTLED_RESULT_OK pick_won='+winners.data.some(x=>x.entry_id===choice.id));
 console.log('PASS A3.6 authenticated staging: real signup, token, vote, history, optional Follow, off-feed discovery, official results');
})().catch(e=>{console.error('A36_STAGING_REAL_TEST_FAILED: '+String(e.message||e).slice(0,330));process.exitCode=1});
