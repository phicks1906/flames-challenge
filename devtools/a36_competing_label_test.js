'use strict';
/* A3.6 v1394: the real staged Following loader must not infer "Competing now"
   from a seven-day-old entry. This is a mocked-DB unit test, not live browser auth. */
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('index.html','utf8');
assert.match(source,/(?:v139[45] · a36-following-(?:active-only|authoritative-rings)|v1396 · a36-guidelines-before-welcome-guide)/);
const begin=source.indexOf('async function loadFollowingList() {');
const attach=source.indexOf('async function fcA36AttachFollowingEntriesV1391(list, profiles) {');
const end=source.indexOf('\nasync function loadFollowersList() {',attach);
assert.ok(begin>0&&attach>begin&&end>attach);
const code=source.slice(begin,end);
const entries=[
 {id:'old-entry',user_id:'inactive',challenge_id:'c-old',created_at:'2026-11-18T12:00:00Z',moderation_status:'clear',sd_round:0,challenge:{id:'c-old',title:'Ended Yesterday',is_public:true,status:'closed',sd_round:0}},
 {id:'hidden',user_id:'inactive',challenge_id:'c-private',created_at:'2026-11-18T13:00:00Z',moderation_status:'clear',sd_round:0,challenge:{id:'c-private',title:'Private Event',is_public:false,status:'voting',sd_round:0}},
 {id:'active-entry',user_id:'active',challenge_id:'c-live',created_at:'2026-11-18T11:00:00Z',moderation_status:'approved',sd_round:0,challenge:{id:'c-live',title:'Public Live Event',is_public:true,status:'voting',sd_round:0}}
];
let failDiscovery=false, failProfiles=false;
const rendered=[],toasts=[],requests=[];
const profiles=[{id:'inactive',name:'Aaron Recent But Closed',avatar:'A'},{id:'active',name:'Zoe Active',avatar:'Z'}];
function from(table){
 const op={table,filters:[]};requests.push(op);
 const q={
  select(){return q},eq(k,v){op.filters.push(['eq',k,v]);return q},
  in(k,v){op.filters.push(['in',k,v]);return q},
  order(){return q},limit(){return q},
  then(ok,bad){
   if(table==='follows')return Promise.resolve({data:[{followee_id:'inactive'},{followee_id:'active'}],error:null}).then(ok,bad);
   if(table==='profiles')return Promise.resolve(failProfiles?{data:null,error:new Error('profiles failed')}:{data:profiles,error:null}).then(ok,bad);
   if(table==='entries')return Promise.resolve(failDiscovery?{data:null,error:new Error('simulated offline')}:{data:entries,error:null}).then(ok,bad);
   throw Error('Unexpected DB table '+table);
  }
 };
 return q;
}
const list={innerHTML:'',children:[]};
const document={getElementById(id){
 if(id==='followingList')return list;
 if(id==='fsFollowingCount')return {set textContent(v){},get textContent(){return ''}};
 return null;
},createElement(name){
 assert.equal(name,'button');
 return {style:{},handlers:{},addEventListener(kind,fn){this.handlers[kind]=fn;}};
}};
function renderFollowList(el, people, competingIds, mode){
 assert.equal(el,list);
 el.children=people.map(p=>({
  children:[{},{
   id:p.id,caption:p.name+(competingIds.has(p.id)?' ● Competing now':''),
   buttons:[],appendChild(btn){this.buttons.push(btn);}
  },{}]
 }));
 rendered.push({names:Array.from(people,p=>p.name),active:Array.from(people).filter(p=>competingIds.has(p.id)).map(p=>p.id),mode});
}
const ctx={state:{profile:{id:'fan'},feedEntries:[],challenges:[]},db:{from},document,renderFollowList,
 computeChallengeStatus:ch=>ch.status,fcWithTimeoutV1099:async q=>await q,
 toast:s=>toasts.push(s),closeFollowingSheet(){},openFeedViewer(){},
 console,Number,String,Promise,Map,Set,Date};
vm.createContext(ctx);vm.runInContext(code,ctx);
(async()=>{
 await ctx.loadFollowingList();
 assert.equal(rendered.length,2,'Initial neutral render then verified render');
 assert.deepEqual(rendered[0].active,[],'Do not show badges before verification');
 assert.deepEqual(rendered[1].active,['active'],'Only active approved public entry receives label');
 assert.deepEqual(rendered[1].names,['Zoe Active','Aaron Recent But Closed'],'Actually active competitor sorts first');
 assert.equal(list.children[0].children[1].buttons.length,1,'Active competitor has view entry');
 assert.equal(list.children[1].children[1].buttons.length,0,'Recent closed competitor lacks view entry');
 assert.equal(list.children[0].children[1].caption.includes('Competing now'),true);
 assert.equal(list.children[1].children[1].caption.includes('Competing now'),false);
 assert.equal(ctx.state.feedEntries.length,0,'Off-feed eligibility still works');
 assert.equal(requests.filter(r=>r.table==='entries').length,1,'Only one active-eligibility entries query');
 assert.ok(!source.slice(begin,attach).includes("gte('created_at', new Date(Date.now() - 7"),'Old seven-day shortcut removed from Following sheet');
 rendered.length=0;failDiscovery=true;
 await ctx.loadFollowingList();
 assert.equal(rendered.length,1,'On network failure show only neutral render');
 assert.deepEqual(rendered[0].active,[],'Network error must not leave stale badge');
 assert.equal(list.children.some(row=>row.children[1].caption.includes('Competing now')),false);
 assert.equal(list.children.some(row=>row.children[1].buttons.length>0),false);
 assert.equal(toasts.length,1,'Discovery failures reported');
 rendered.length=0;failDiscovery=false;failProfiles=true;
 await ctx.loadFollowingList();
 assert.equal(rendered.length,0,'Profile error must not imply verified activity');
 assert.match(list.innerHTML,/Could not load list/);
 assert.equal(ctx.state.feedEntries.length,0);
 console.log('PASS v1394: recent closed has no Competing now, verified active sort and link, one independent lookup, failures clear labels');
})().catch(e=>{console.error(e);process.exitCode=1;});
