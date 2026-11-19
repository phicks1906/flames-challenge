#!/usr/bin/env python3
"""Staging CI-only retrofit: two Auth members create fixtures using their JWTs."""
from pathlib import Path
p=Path("devtools/a36_auth_signup_and_e2e.js")
s=p.read_text("utf8")
def replace(old,new):
 global s
 if s.count(old)!=1: raise SystemExit("STOP: anchor changed")
 s=s.replace(old,new,1)
replace("const headers={apikey,Accept:'application/json'};",
        "const headers={apikey,Accept:'application/json',Prefer:'return=representation'};")
beg=" const fixture=await poll('CHALLENGE_ENTRIES_SEEDED',async()=>{"
end=" const ballot=await call('GET','/rest/v1/entries?"
if s.count(beg)!=1 or s.count(end)!=1: raise SystemExit("STOP: fixture boundaries changed")
a=s.index(beg);b=s.index(end,a)
seed=""" // Two signed-in members seed their own fixture; no SQL preloading.
 for(const member of members) {
  const rows=await must(call('POST','/rest/v1/profiles',{
   id:member.id,name:'A36 '+member.role,avatar:'🔥',appearance:'dark',
   interests:['Music'],onboarding_version:1,
   onboarding_completed_at:new Date().toISOString()
  },logins[member.role]),'profile '+member.role);
  if(rows.length!==1)throw Error('Profile creation did not return a row');
 }
 const soon=n=>new Date(Date.now()+n*60000).toISOString();
 const fresh=async(name,subMinutes,endMinutes)=>{
  const rows=await must(call('POST','/rest/v1/challenges',{
   creator_id:voter.id,title:name,category:'Music',media_type:'text',
   submission_deadline:soon(subMinutes),voting_end:soon(endMinutes),
   status:'submitting',is_public:true,entry_limit:20
  },token),'create '+name);
  if(rows.length!==1)throw Error('Challenge creation missing row');
  return rows[0].id;
 };
 const fixture={live:await fresh(title,6,25),future:await fresh(nextTitle,8,35)};
 const addEntry=async(challengeId,member,caption)=>{
  await must(call('POST','/rest/v1/entries',{
   challenge_id:challengeId,user_id:member.id,media_type:'text',
   caption,moderation_status:'clear'
  },logins[member.role]),'create '+caption);
 };
 await addEntry(fixture.live,competitor,'A36 live competitor '+run);
 await addEntry(fixture.live,voter,'A36 live alternative '+run);
 await addEntry(fixture.future,competitor,'A36 future competitor '+run);
 await must(call('PATCH','/rest/v1/challenges?id=eq.'+fixture.live,{
  submission_deadline:new Date(Date.now()-10000).toISOString(),
  status:'voting'
 },token),'open voting');
 console.log('A36_SIGNED_IN_FIXTURE_READY');
"""
s=s[:a]+seed+s[b:]
anchor=" console.log('STAGING_REAL_FOLLOW_OFF_FEED_OK');"
replace(anchor,anchor+"""
 await must(call('PATCH','/rest/v1/challenges?id=eq.'+fixture.live,{
  voting_end:new Date(Date.now()-10000).toISOString(),status:'closed'
 },token),'close competition');
 console.log('A36_SIGNED_IN_VOTE_CLOSED');
""")
helper="""async function must(task,label) {
 const result=await task;
 if(!result.ok)throw Error(label+' HTTP '+result.status+' code '+
  String(result.data?.code||result.data?.message||result.data?.error||'unknown').slice(0,110));
 return result.data;
}
"""
replace("const sleep=t=>new Promise(r=>setTimeout(r,t));",helper+"const sleep=t=>new Promise(r=>setTimeout(r,t));")
if "STAGING_REAL_FOLLOW_OFF_FEED_OK" not in s or s.count("A36_SIGNED_IN_FIXTURE_READY")!=1:
 raise SystemExit("STOP: unexpected result")
p.write_text(s,encoding="utf8")
print("PASS: 2-member authenticated self-seeding E2E staged script ready")
