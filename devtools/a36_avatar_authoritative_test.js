'use strict';
/* A3.6 v1395 regression: evaluate the ACTUAL avatar activity classifier from
   the staged canonical index.html, with mocked authorized Supabase responses. */
const assert=require('node:assert/strict');
const fs=require('node:fs');
const source=fs.readFileSync('index.html','utf8');
assert.match(source,/(?:v139[45] · a36-following-(?:active-only|authoritative-rings)|v1396 · a36-guidelines-before-welcome-guide)/);
const functionStart=source.indexOf('async function loadFollowingAvatarRow() {');
const snippetStart=source.indexOf('    const followingIds = following.map(u => u.id);',functionStart);
const snippetEndAnchor="    }).join('');";
const snippetEnd=source.indexOf(snippetEndAnchor,snippetStart);
assert.ok(functionStart>0&&snippetStart>functionStart&&snippetEnd>snippetStart,'Following avatar activity anchors absent');
const snippet=source.slice(snippetStart,snippetEnd+snippetEndAnchor.length);
const fullAvatar=source.slice(functionStart,source.indexOf('\n/* ----------',functionStart)>0?source.indexOf('\n/* ----------',functionStart):functionStart+9000);
assert.match(fullAvatar,/fcA36OpenFollowedEntryV1393\(el\.dataset\.entryOpen, el\.dataset\.entryId, false\)/,
 'Avatar link must safely hydrate off-feed challenge before viewer opens');
const make=(id,user,ch,moderation_status='clear',round=0)=>({
 id,user_id:user,challenge_id:ch.id,sd_round:round,moderation_status,challenge:ch
});
const live={id:'c-live',title:'Live Challenge',is_public:true,status:'voting',sd_round:0,voided_at:null,sd_phase:null};
const closed={id:'c-closed',title:'Closed Challenge',is_public:true,status:'closed',sd_round:0,voided_at:null};
const privateClosed={id:'c-private',title:'Private Closed',is_public:false,status:'closed',sd_round:0};
const hidden={id:'c-hidden',title:'Hidden Round',is_public:true,status:'voting',sd_phase:'submitting',sd_round:1};
const voided={id:'c-voided',title:'Voided',is_public:true,status:'voting',voided_at:'2026-11-18T17:00:00Z',sd_round:0};
const endRound={id:'c-round',title:'Final Round',is_public:true,status:'voting',sd_round:1};
const followees=[
 {id:'fan-winner',name:'Winner',avatar:'🏆'},
 {id:'fan-loser',name:'Loser',avatar:'👤'},
 {id:'fan-live',name:'Live',avatar:'🔥'},
 {id:'fan-private',name:'Private',avatar:'👤'},
 {id:'fan-hidden',name:'Hidden',avatar:'👤'},
 {id:'fan-voided',name:'Voided',avatar:'👤'},
 {id:'fan-rejected',name:'Rejected',avatar:'👤'},
 {id:'fan-oldround',name:'Oldround',avatar:'👤'}];
const entries=[
 make('e-live','fan-live',live),
 make('e-loser','fan-loser',closed),
 make('e-winner','fan-winner',closed),
 make('e-private','fan-private',privateClosed),
 make('e-hidden','fan-hidden',hidden,'approved',1),
 make('e-voided','fan-voided',voided),
 make('e-rejected','fan-rejected',live,'rejected'),
 make('e-old','fan-oldround',endRound,'clear',0)
];
let failWinnerFetch=false,failEntriesFetch=false;
const queries=[];
function from(table){
 const opts={table,filters:[]};queries.push(opts);
 const q={
  select(s){opts.columns=s;return q},
  in(field,values){opts.filters.push({field,values});return q},
  gte(field,value){opts.filters.push({field,values:[value]});return q},
  order(){return q},limit(){return q},
  then(resolve,reject){
   let data=table==='entries'?entries:table==='challenge_result_winners'?[{challenge_id:'c-closed',user_id:'fan-winner'},{challenge_id:'c-private',user_id:'fan-private'}]:[];
   for(const f of opts.filters.filter(f=>f.field!=='created_at')){
    data=data.filter(row=>f.values.includes(row[f.field]));
   }
   const error=(table==='entries'&&failEntriesFetch)||(table==='challenge_result_winners'&&failWinnerFetch)?new Error('simulated query fail'):null;
   return Promise.resolve({data:error?null:data,error}).then(resolve,reject);
  }
 };
 return q;
}
const escapeHtml=s=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
const evalActivity=new Function('following','db','computeChallengeStatus','scroll','escapeHtml','console','Date','Set','Number','String', 'return (async()=>{'+snippet+';return scroll.innerHTML;})()');
function ringMap(html){
 const map=new Map();
 const regex=/following-avatar-ring (ring-(?:active|none|won))[\s\S]*?following-avatar-name">([^<]+)/g;
 for(const m of html.matchAll(regex))map.set(m[2],m[1]);
 return map;
}
async function run(){
 return await evalActivity(followees,{from},ch=>ch.status,{innerHTML:''},escapeHtml,console,Date,Set,Number,String);
}
(async()=>{
 let html=await run(),rings=ringMap(html);
 assert.equal(rings.size,8,'All followed people appear');
 assert.equal(rings.get('Live'),'ring-active','Public current entry is active');
 assert.equal(rings.get('Winner'),'ring-won','Official winner receives winner ring');
 for(const name of ['Loser','Private','Hidden','Voided','Rejected','Oldround'])
  assert.equal(rings.get(name),'ring-none',name+' must not receive false activity or winner ring');
 assert.ok(queries.some(q=>q.table==='entries'&&q.filters.some(f=>f.field==='moderation_status'&&f.values.includes('clear'))),'Moderation filter required');
 assert.ok(queries.some(q=>q.table==='challenge_result_winners'&&q.filters.some(f=>f.field==='challenge_id'&&f.values.includes('c-closed'))),'Must consult authoritative winner table');
 assert.equal([...html.matchAll(/ring-won/g)].length,1,'Exactly one official winner ring');
 failWinnerFetch=true;html=await run();rings=ringMap(html);
 assert.equal(rings.get('Winner'),'ring-none','Failed official lookup must not fake a win');
 assert.equal(rings.get('Live'),'ring-active','Active ring independent of settled winner lookup');
 failWinnerFetch=false;failEntriesFetch=true;
 await assert.rejects(()=>run(),/simulated query fail/,'Activity fetch errors must not be represented as verified activity');
 console.log('PASS v1395: actual avatar classification — active, authoritative win, loss, private, hidden, void, rejected, wrong round and winner-fetch failure');
})().catch(e=>{console.error(e);process.exitCode=1;});
