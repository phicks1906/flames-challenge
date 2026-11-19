/* A3.6 Part 4: unit-level following-to-entry test, using a mocked authenticated DB.
   Explicitly verifies an entry never present in state.feedEntries.
   Does not claim physical-iPhone or live authenticated Supabase validation. */
'use strict';
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const source=fs.readFileSync('index.html','utf8');
const start=source.indexOf('async function fcA36AttachFollowingEntriesV1391(list, profiles) {');
const end=source.indexOf('\nasync function loadFollowersList() {',start);
assert.ok(start>0&&end>start,'Following component must be present in canonical staged index');
assert.equal(source.includes('    await fcA36AttachFollowingEntriesV1391(list, profiles);'),true,'Following loader must await independent discovery');
assert.match(source,/(?:v139[45] · a36-following-(?:active-only|authoritative-rings)|v1396 · a36-guidelines-before-welcome-guide|v1397 · a36-ember-after-onboarding)/);
const code=source.slice(start,end);
const fresh={id:'c-new',title:'Live Showcase',is_public:true,status:'voting',sd_round:0};
const privateChallenge={id:'c-private',title:'Private',is_public:false,status:'voting',sd_round:0};
const hidden={id:'c-hidden',title:'Hidden Tiebreaker',is_public:true,status:'voting',sd_phase:'submitting',sd_round:1};
const closed={id:'c-closed',title:'Old event',is_public:true,status:'closed',sd_round:0};
const allEntries=[
 {id:'e-private',user_id:'followed2',challenge_id:'c-private',created_at:'2026-11-18T14:00:00Z',moderation_status:'approved',sd_round:0,challenge:privateChallenge},
 {id:'e-hidden',user_id:'followed2',challenge_id:'c-hidden',created_at:'2026-11-18T13:00:00Z',moderation_status:'approved',sd_round:1,challenge:hidden},
 {id:'e-rejected',user_id:'followed2',challenge_id:'c-new',created_at:'2026-11-18T12:00:00Z',moderation_status:'rejected',sd_round:0,challenge:fresh},
 {id:'e-pending',user_id:'followed2',challenge_id:'c-new',created_at:'2026-11-18T11:00:00Z',moderation_status:'pending',sd_round:0,challenge:fresh},
 {id:'e-closed',user_id:'followed2',challenge_id:'c-closed',created_at:'2026-11-18T10:00:00Z',moderation_status:'clear',sd_round:0,challenge:closed},
 {id:'e-new',user_id:'followed',challenge_id:'c-new',created_at:'2026-11-18T09:00:00Z',moderation_status:'clear',sd_round:0,challenge:fresh},
 {id:'e-stranger',user_id:'notfollowed',challenge_id:'c-new',created_at:'2026-11-18T10:00:00Z',moderation_status:'approved',sd_round:0,challenge:fresh},
];
const queryLog=[];
let failDiscovery=false;
let failOpening=false;
function from(table) {
  const opts={table,filters:[],select:null};
  queryLog.push(opts);
  const q={
    select(s){opts.select=s;return q;},
    in(k,v){opts.filters.push(['in',k,v]);return q;},
    eq(k,v){opts.filters.push(['eq',k,v]);return q;},
    order(k,o){opts.order=k;return q;},
    limit(v){opts.limit=v;return q;},
    maybeSingle(){return run(true);},
    then(ok,bad){return run(false).then(ok,bad);}
  };
  function run(single) {
    const isDiscovery=table==='entries'&&opts.filters.some(x=>x[0]==='in'&&x[1]==='user_id');
    if ((isDiscovery&&failDiscovery)||(!isDiscovery&&failOpening))return Promise.resolve({data:null,error:new Error('simulated network failure')});
    let data=table==='entries'?allEntries:table==='challenges'?[fresh,privateChallenge,hidden,closed]:[];
    for(const [op,k,v] of opts.filters){
      data=data.filter(x=>op==='eq'?x[k]===v:v.includes(x[k]));
    }
    if(opts.order==='created_at')data=[...data].sort((a,b)=>b.created_at.localeCompare(a.created_at));
    if(opts.limit)data=data.slice(0,opts.limit);
    return Promise.resolve({data:single?(data[0]||null):data,error:null});
  }
  return q;
}
function details(){return {buttons:[],appendChild(btn){this.buttons.push(btn);}};}
const profiles=[{id:'followed',name:'Creator A'},{id:'followed2',name:'Creator B'}];
const rows=profiles.map(()=>({children:[{},details(),{}]}));
const list={children:rows};
const opened=[],toasts=[],closedSheets=[],renderSnapshots=[];
const state={profile:{id:'me'},challenges:[],feedEntries:[],myVotes:{pollVoted:true}};
const document={
 getElementById(id){return id==='followingList'?list:null;},
 createElement(type){assert.equal(type,'button');return {handlers:{},style:{},disabled:false,addEventListener(k,cb){this.handlers[k]=cb;}};}
};
const ctx={db:{from},document,state,
 renderFollowList: (el,ordered,active,mode)=>{renderSnapshots.push({ordered:Array.from(ordered,p=>p.id),active:Array.from(active),mode});},
 computeChallengeStatus(ch){return ch.status;},
 fcWithTimeoutV1099:async q=>await q,
 toast:s=>toasts.push(s),
 closeFollowingSheet:()=>closedSheets.push(true),
 openFeedViewer:async (challengeId,entryId)=>{
   assert.equal(state.challenges.some(ch=>ch.id===challengeId),true,'Challenge must be loaded before opening viewer');
   opened.push([challengeId,entryId]);
 },
 console,Map,Number,Promise,String};
vm.createContext(ctx);
vm.runInContext(code,ctx);
(async()=>{
 await ctx.fcA36AttachFollowingEntriesV1391(list,profiles);
 assert.deepEqual(renderSnapshots[0],{ordered:['followed','followed2'],active:['followed'],mode:'following'},'Only verified eligible users receive Competing now');
 assert.equal(rows[0].children[1].buttons.length,1,'Off-feed followed new entry must be discoverable');
 assert.equal(rows[1].children[1].buttons.length,0,'Private, hidden, rejected, pending and closed entries must not appear as active');
 assert.match(rows[0].children[1].buttons[0].textContent,/Live Showcase/);
 assert.equal(state.feedEntries.length,0,'Discovery must not depend on feed cache');
 assert.ok(queryLog.some(q=>q.table==='entries'&&q.filters.some(f=>f[0]==='in'&&f[1]==='user_id'&&f[2].includes('followed'))),'Must query followed users independently');
 assert.ok(queryLog.some(q=>q.table==='entries'&&q.filters.some(f=>f[0]==='in'&&f[1]==='moderation_status'&&f[2].includes('clear'))),'Must exclude unapproved media');
 const btn=rows[0].children[1].buttons[0];
 await btn.handlers.click({stopPropagation(){}});
 assert.deepEqual(opened,[['c-new','e-new']]);
 assert.equal(closedSheets.length,1);
 assert.equal(state.challenges[0].id,'c-new');
 assert.equal(state.myVotes.pollVoted,true,'Poll history unchanged');
 assert.equal(btn.disabled,false);
 const beforeQueries=queryLog.length;
 failDiscovery=true;
 await ctx.fcA36AttachFollowingEntriesV1391(list,profiles);
 assert.equal(queryLog.length,beforeQueries+1);
 assert.equal(toasts.length,1,'Lookup failure must not misrepresent no matches');
 failDiscovery=false;
 failOpening=true;
 await btn.handlers.click({stopPropagation(){}});
 assert.equal(opened.length,1,'Failed revalidation must not open a stale entry');
 assert.equal(toasts.length,2);
 console.log('PASS A3.6 Part 4: off-feed followed entry, RLS-shaped filters, eligibility, direct viewer hydration, error handling, poll isolation');
})().catch(e=>{console.error(e);process.exitCode=1;});
