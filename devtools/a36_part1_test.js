/* Unit-level integration harness for the exact A3.6 Part 1 component.
   Runs without external packages or real account credentials.
   Browser/iPhone and signed-in Supabase checks remain separately required. */
'use strict';
const fs=require('node:fs');
const vm=require('node:vm');
const assert=require('node:assert/strict');

const raw=fs.readFileSync('devtools/a36_votes_component.html','utf8');
const body=raw.match(/<script id="fc-a36-v1390-votes-js">([\s\S]*?)<\/script>/);
assert.ok(body,'Could not find A3.6 production script');
const rows={
  entry_votes:[{id:'v1',challenge_id:'c1',entry_id:'e1',created_at:'2026-11-17T10:00:00Z',voter_id:'me'},
               {id:'hidden',challenge_id:'c2',entry_id:'e2',created_at:'2026-11-16T10:00:00Z',voter_id:'someone-else'}],
  challenges:[{id:'c1',title:'The Live Vocal Challenge',category:'Music',voting_end:'2026-11-19T10:00:00Z',submission_deadline:'2026-11-15T10:00:00Z'}],
  entries:[{id:'e1',challenge_id:'c1',user_id:'nia',submitter:{id:'nia',name:'Nia Brooks',avatar:'N'}}]
};
const calls=[];
function query(table){
  const spec={table,filters:[],limit:null};
  calls.push(spec);
  const q={
    select(sel){spec.select=sel;return q;},
    eq(k,v){spec.filters.push(['eq',k,v]);return q;},
    in(k,v){spec.filters.push(['in',k,v]);return q;},
    order(k,o){spec.order=k;return q;},
    range(a,b){spec.range=[a,b];return q;},
    then(resolve,reject){
      let data=(rows[table]||[]).slice();
      for(const [op,k,v] of spec.filters) data=data.filter(x=>op==='eq'?x[k]===v:v.includes(x[k]));
      if(spec.order==='created_at')data.sort((a,b)=>b.created_at.localeCompare(a.created_at));
      if(spec.range)data=data.slice(spec.range[0],spec.range[1]+1);
      return Promise.resolve({data,error:null}).then(resolve,reject);
    }
  };
  return q;
}
class El{
  constructor(id){this.id=id;this.dataset={};this.handlers={};this.children=[];this.hidden=false;this.style={};
    this._html='';this.classSet=new Set();this.classList={
      contains:(x)=>this.classSet.has(x),add:(x)=>this.classSet.add(x),remove:(x)=>this.classSet.delete(x),
      toggle:(x,on)=>{if(on)this.classSet.add(x);else this.classSet.delete(x);}
    };
  }
  addEventListener(event,fn){(this.handlers[event]??=[]).push(fn);}
  click(){for(const fn of this.handlers.click||[])fn({target:this});}
  appendChild(el){this.children.push(el);if(el.id)nodes.set(el.id,el);}
  querySelectorAll(selector){
    if(selector==='.ps-tab')return this.children.filter(x=>x.className==='ps-tab');
    if(selector==='[data-fc-a36-ch]'){
      if(this._lastVoteMarkup!==this.innerHTML){
        const found=[...this.innerHTML.matchAll(/data-fc-a36-ch="([^"]+)"/g)];
        this._voteButtons=found.map(m=>{const e=new El('row'+m[1]);e.dataset.fcA36Ch=m[1];return e;});
        this._lastVoteMarkup=this.innerHTML;
      }
      return this._voteButtons||[];
    }
    return [];
  }
  querySelector(selector){
    if(selector==='#fcA36VotesRetry'&&this.innerHTML.includes('id="fcA36VotesRetry"'))return new El('retry');
    if(selector==='#fcA36VotesMore'&&this.innerHTML.includes('id="fcA36VotesMore"'))return new El('more');
    return null;
  }
  set innerHTML(x){this._html=x;}
  get innerHTML(){return this._html;}
}
const nodes=new Map();
const bar=new El('psTabs');
for(const x of ['challenges','entries','posts']){const b=new El(x);b.dataset.pstab=x;b.className='ps-tab';bar.appendChild(b);}
const profileSheet=new El('profileSheet');profileSheet.classList.add('open');
const content=new El('psContent');nodes.set('profileSheet',profileSheet);nodes.set('psContent',content);
const document={
  querySelector(k){return k==='#profileSheet .ps-tabs'?bar:null;},
  getElementById(k){return nodes.get(k)||null;},
  createElement(tag){return new El(tag);}
};
const pollState={poll1:2};
const state={profile:{id:'me'},currentView:'you',myVotes:pollState,challenges:[]};
const psState={userId:'me',profile:{id:'me'},tab:'challenges'};
let opened=[];
const ctx={state,psState,document,db:{from:query},
  window:{renderProfileSheet:()=>{},renderProfileTab:()=>{},openFeedViewer:()=>{}},
  openFeedViewer:async(id)=>opened.push(id),
  escapeHtml:(s)=>String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;'),
  fcWithTimeoutV1099:async(q)=>await q,toast:()=>{},
  console,Date,Intl,Map,Set,Promise
};
vm.createContext(ctx);
vm.runInContext(body[1],ctx,{filename:'a36_votes_component.js'});
const advance=async()=>{for(let i=0;i<12;i++)await new Promise(resolve=>setImmediate(resolve));};
(async()=>{
  ctx.window.renderProfileSheet();
  const btn=nodes.get('fcA36VotesTab');
  assert.ok(btn&&!btn.hidden,'Own profile must show Votes tab');
  assert.equal(btn.textContent,'Votes');
  btn.click();await advance();
  assert.equal(psState.tab,'votes');
  assert.match(content.innerHTML,/The Live Vocal Challenge/);
  assert.match(content.innerHTML,/Nia Brooks/);
  assert.doesNotMatch(content.innerHTML,/someone-else/);
  assert.equal(state.myVotes,pollState,'Poll voting state must not be replaced');
  assert.ok(calls.some(c=>c.table==='entry_votes'&&c.filters.some(f=>f[1]==='voter_id'&&f[2]==='me')),
    'History read must filter by the authenticated voter');
  assert.ok(!calls.some(c=>c.table==='votes'),'Poll table must never be used');
  assert.ok(calls.some(c=>c.table==='challenges')&&calls.some(c=>c.table==='entries'),
    'Must hydrate actual challenge and competitor records');

  const row=content.querySelectorAll('[data-fc-a36-ch]')[0];assert.ok(row);
  row.click();await advance();
  assert.deepEqual(opened,['c1']);
  assert.equal(state.currentView,'you','Viewer must not navigate away from You');
  assert.equal(state.challenges[0].id,'c1');

  psState.userId='other';psState.profile={id:'other'};
  ctx.window.renderProfileSheet();
  assert.ok(btn.hidden,'Votes tab must not appear on other members profiles');
  const readCount=calls.length;btn.click();await advance();
  assert.equal(calls.length,readCount,'Other profiles must not trigger vote history fetches');


  // Part 2 North Star outcome matrix: rely on settled records only, not local vote totals.
  psState.userId='me';psState.profile={id:'me'};psState.tab='votes';
  ctx.window.renderProfileSheet();
  const cases=[
    {id:'c3',entry:'e3',user:'u3',resolution:'decisive',winner_count:1,
      winners:[{challenge_id:'c3',entry_id:'e3',user_id:'u3',is_co_winner:false}]},
    {id:'c4',entry:'e4',user:'u4',resolution:'co_winners',winner_count:2,
      winners:[{challenge_id:'c4',entry_id:'e4',user_id:'u4',is_co_winner:true},
               {challenge_id:'c4',entry_id:'other4',user_id:'other4',is_co_winner:true}]},
    {id:'c5',entry:'e5',user:'u5',resolution:'no_contest',winner_count:0,winners:[]},
    {id:'c6',entry:'e6',user:'u6',resolution:'decisive',winner_count:1,
      winners:[{challenge_id:'c6',entry_id:'other6',user_id:'other6',is_co_winner:false}]},
  ];
  for(const c of cases){
    rows.entry_votes.push({id:'vote-'+c.id,challenge_id:c.id,entry_id:c.entry,
      created_at:'2026-11-18T12:00:00Z',voter_id:'me'});
    rows.challenges.push({id:c.id,title:'Official '+c.id,category:'Dance',voting_end:'2026-11-17T12:00:00Z'});
    rows.entries.push({id:c.entry,challenge_id:c.id,user_id:c.user,
      submitter:{id:c.user,name:'Competitor '+c.user,avatar:'X'}});
  }
  rows.challenge_results=cases.map(({id,resolution,winner_count})=>
    ({challenge_id:id,resolution,winner_count,resolved_at:'2026-11-18T12:30:00Z'}));
  rows.challenge_result_winners=cases.flatMap(x=>x.winners);
  rows.entry_votes.push({id:'pending',challenge_id:'c7',entry_id:'e7',
    created_at:'2026-11-18T10:00:00Z',voter_id:'me'});
  rows.challenges.push({id:'c7',title:'Pending official result',category:'Dance',
    voting_end:'2026-11-17T12:00:00Z'});
  rows.entries.push({id:'e7',challenge_id:'c7',user_id:'u7',
    submitter:{id:'u7',name:'Competitor u7',avatar:'X'}});
  await ctx.window.fcA36VotesPart1.refresh();
  await advance();
  assert.match(content.innerHTML,/Official result · Your pick won/);
  assert.match(content.innerHTML,/Official result · Your pick co-won/);
  assert.match(content.innerHTML,/Official result · No contest/);
  assert.match(content.innerHTML,/Official result · Another competitor won/);
  assert.match(content.innerHTML,/Official result not available/);
  assert.equal(state.myVotes,pollState,'Settlement outcomes must never overwrite poll state');
  assert.ok(calls.some(c=>c.table==='challenge_results'),'Must request authoritative result source');
  assert.ok(calls.some(c=>c.table==='challenge_result_winners'),'Must request authoritative winner source');
  console.log('PASS: own-only history, safe navigation, official win/co-win/loss/no-contest/pending states, poll isolation');
})().catch(e=>{console.error(e);process.exit(1)});
