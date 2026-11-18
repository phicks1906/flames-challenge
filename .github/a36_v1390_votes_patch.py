from pathlib import Path
import re, hashlib

p=Path("index.html")
s=p.read_text(encoding="utf-8")
def gitblob(x):
    import hashlib
    b=x.encode("utf-8")
    return hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
EXPECTED="6ac3a54842e15bb8a554194160ef2e673f51ee17"
if gitblob(s)!=EXPECTED:
    raise SystemExit("Refusing to patch: production source does not match main v1389 blob")
old='<meta content="v1389 · continuous-championship-medal-rings" name="fc-build"/>'
new='<meta content="v1390 · a36-votes-readonly-candidate" name="fc-build"/>'
if s.count(old)!=1:raise SystemExit("Expected exactly one source build tag")
s=s.replace(old,new,1)
old='<meta content="Championship gold, silver and bronze portrait rings now form complete, uninterrupted circles." name="fc-whatsnew"/>'
new='<meta content="A3.6 candidate: real vote history and settled-result access. Not a production release." name="fc-whatsnew"/>'
if s.count(old)!=1:raise SystemExit("Expected exactly one what is new tag")
s=s.replace(old,new,1)

css=r"""
<style id="fc-a36-v1390-votes-style">
/* A3.6: own profile only, preserving existing public profile tabs. */
#profileSheet .ps-tab[data-pstab="votes"][hidden]{display:none!important}
#profileSheet.fc-own-profile-page-v1075 .ps-tab[data-pstab="votes"]{min-height:44px}
.fc-a36-votes{display:flex;flex-direction:column;gap:11px;padding:8px 0 calc(30px + env(safe-area-inset-bottom,0px))}
.fc-a36-votes-header{display:flex;align-items:center;gap:12px;justify-content:space-between}
.fc-a36-votes-header h3{margin:0;font:800 18px var(--font-dm,system-ui);color:var(--text)}
.fc-a36-votes button{min-height:44px;touch-action:manipulation}
.fc-a36-vote-card{border:1px solid var(--border);border-radius:15px;padding:14px;background:var(--surface-2,rgba(125,125,125,.08));min-width:0}
.fc-a36-vote-card h4{font:800 15px/1.25 var(--font-dm,system-ui);color:var(--text);margin:5px 0 8px;overflow-wrap:anywhere}
.fc-a36-vote-card p{font:500 12.5px/1.45 var(--font-dm,system-ui);color:var(--text-muted);margin:3px 0 9px}
.fc-a36-vote-status{font:800 10.5px/1.4 var(--font-dm,system-ui);letter-spacing:.05em;color:var(--ember);text-transform:uppercase}
.fc-a36-vote-open,.fc-a36-vote-refresh{border:1px solid var(--border);border-radius:100px;padding:10px 16px;background:var(--surface-interactive,var(--surface-2));color:var(--text);font:800 12px var(--font-dm,system-ui)}
.fc-a36-vote-open{width:100%}
.fc-a36-vote-note{font:500 11.5px/1.45 var(--font-dm,system-ui);color:var(--text-muted);padding:5px 2px}
@media(max-width:359px){#profileSheet.fc-own-profile-page-v1075 .ps-tab{font-size:11px!important;padding-inline:7px!important}}
</style>
"""
js=r"""
<script id="fc-a36-v1390-votes-script">
/* Read-only vote/result integration. No new SQL, votes or fabricated outcomes. */
(function(){
'use strict';
var serial=0,cache=null;
function own(){return !!(window.state&&state.profile&&window.psState&&psState.profile&&
 String(state.profile.id)===String(psState.userId)&&String(state.profile.id)===String(psState.profile.id));}
function escapeIt(v){return typeof escapeHtml==='function'?escapeHtml(String(v??'')):String(v??'').replace(/[&<>"']/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]});}
function content(){return document.getElementById('psContent');}
function current(user,n){return own()&&serial===n&&psState.tab==='votes'&&
 String(state.profile.id)===String(user)&&document.getElementById('profileSheet')?.classList.contains('open');}
function installTab(){
 var group=document.querySelector('#profileSheet .ps-tabs');if(!group)return;
 var b=group.querySelector('[data-pstab="votes"]');
 if(!b){b=document.createElement('button');b.type='button';b.className='ps-tab';b.dataset.pstab='votes';b.textContent='Votes';group.appendChild(b);
  b.addEventListener('click',function(){if(!own())return;psState.tab='votes';
   group.querySelectorAll('.ps-tab').forEach(function(x){x.classList.toggle('active',x===b)});
   loadVotes(true);
  });
 }
 b.hidden=!own();b.classList.toggle('active',own()&&psState.tab==='votes');
}
async function batch(table,fields,key,ids){
 var out=[];
 for(var i=0;i<ids.length;i+=80){var r=await db.from(table).select(fields).in(key,ids.slice(i,i+80));
  if(r.error)throw r.error;out.push.apply(out,r.data||[]);
 }
 return out;
}
async function query(user){
 var vr=await db.from('entry_votes').select('challenge_id,entry_id,created_at')
   .eq('voter_id',user).order('created_at',{ascending:false}).limit(1000);
 if(vr.error)throw vr.error;
 var unique=new Map();
 (vr.data||[]).forEach(function(x){if(x.challenge_id&&!unique.has(String(x.challenge_id)))unique.set(String(x.challenge_id),x)});
 var votes=Array.from(unique.values());
 var ids=Array.from(unique.keys());
 var eids=Array.from(new Set(votes.map(function(x){return x.entry_id}).filter(Boolean)));
 var records=ids.length?await Promise.all([
   batch('challenges','id,title,category,status,submission_deadline,voting_end,is_public,creator_id,sd_round,sd_phase','id',ids),
   batch('entries','id,user_id,challenge_id,submitter:profiles!entries_user_id_fkey(id,name)','id',eids),
   batch('challenge_results','challenge_id,resolution,resolved_at,winner_count,final_round','challenge_id',ids),
   batch('challenge_result_winners','challenge_id,entry_id,user_id,is_co_winner','challenge_id',ids)
 ]):[[],[],[],[]];
 var c=new Map(),e=new Map(),r=new Map(),w=new Map();
 records[0].forEach(function(x){c.set(String(x.id),x)});
 records[1].forEach(function(x){e.set(String(x.id),x)});
 records[2].forEach(function(x){r.set(String(x.challenge_id),x)});
 records[3].forEach(function(x){var k=String(x.challenge_id);if(!w.has(k))w.set(k,[]);w.get(k).push(x)});
 return {votes:votes,challenges:c,entries:e,results:r,winners:w,truncated:(vr.data||[]).length===1000};
}
function describe(v,d){
 var k=String(v.challenge_id),c=d.challenges.get(k),r=d.results.get(k),ws=d.winners.get(k)||[];
 if(!c)return ['UNAVAILABLE','This competition is no longer visible to your account.'];
 if(!r){
  var end=c.voting_end?Date.parse(c.voting_end):NaN;
  if(Number.isFinite(end)&&Date.now()<end)return ['RESULT PENDING','Your vote is recorded. Voting remains open.'];
  return ['RESULT PROCESSING','The database has not published a settled result yet.'];
 }
 if(!ws.length){
  return String(r.resolution||'').includes('tie')?['NO DECISIVE WINNER','The recorded result did not produce a decisive winner.']:
   ['NO WINNER RECORDED','The settled resolution is '+String(r.resolution||'unresolved').replace(/_/g,' ')+'.'];
 }
 var chose=ws.some(function(x){return String(x.entry_id)===String(v.entry_id)});
 if(chose)return ws.length>1?['YOUR PICK CO-WON','Your chosen entry is among the recorded co-winners.']:
   ['YOUR PICK WON','Your chosen entry is the recorded winner.'];
 return ['RESULT SETTLED',ws.length>1?'The competition has recorded co-winners.':'Another entry won this competition.'];
}
function paint(user,n,d){
 if(!current(user,n))return;
 var cards=d.votes.map(function(v){
  var k=String(v.challenge_id),c=d.challenges.get(k),entry=d.entries.get(String(v.entry_id)),status=describe(v,d);
  var who=entry?.submitter?.name||'the selected entry';
  return '<article class="fc-a36-vote-card"><div class="fc-a36-vote-status">'+escapeIt(status[0])+'</div>'+
   '<h4>'+escapeIt(c?.title||'Competition unavailable')+'</h4>'+
   '<p>You voted for '+escapeIt(who)+'. '+escapeIt(status[1])+'</p>'+
   (c?'<button class="fc-a36-vote-open" type="button" data-a36-open="'+escapeIt(k)+'">View competition →</button>':'')+'</article>';
 }).join('');
 content().innerHTML='<section class="fc-a36-votes"><header class="fc-a36-votes-header"><h3>Your Votes</h3>'+
  '<button class="fc-a36-vote-refresh" type="button" data-a36-refresh>Refresh</button></header>'+
  (cards||'<article class="fc-a36-vote-card"><h4>No current ballots found</h4><p>After you vote, this list can show the competition and its result.</p><button class="fc-a36-vote-open" type="button" data-a36-explore>Explore competitions</button></article>')+
  '<p class="fc-a36-vote-note">Historical limitation: votes deleted during a tiebreaker reset may not appear. This is not yet a lifetime vote history.'+
  (d.truncated?' Only the 1,000 most recent ballot rows were queried.':'')+'</p></section>';
 var refresh=content().querySelector('[data-a36-refresh]');if(refresh)refresh.onclick=function(){loadVotes(true)};
 content().querySelectorAll('[data-a36-open]').forEach(function(b){b.onclick=function(){
  if(!current(user,n))return;
  var c=d.challenges.get(b.dataset.a36Open);
  if(c&&typeof openChallenge==='function')openChallenge(c);
 }});
 var explore=content().querySelector('[data-a36-explore]');
 if(explore)explore.onclick=function(){if(typeof closeProfileSheet==='function')closeProfileSheet();if(typeof switchView==='function')switchView('challenges')};
}
function loadVotes(force){
 if(!own())return;
 var user=state.profile.id,n=++serial,root=content();if(!root)return;
 root.innerHTML='<section class="fc-a36-votes"><header class="fc-a36-votes-header"><h3>Your Votes</h3></header>'+
  '<article class="fc-a36-vote-card"><p>Loading your recorded votes…</p></article></section>';
 if(cache?.user===user&&!force){paint(user,n,cache.data);return}
 query(user).then(function(d){if(!current(user,n))return;cache={user:user,data:d};paint(user,n,d)})
 .catch(function(err){if(!current(user,n))return;
  root.innerHTML='<section class="fc-a36-votes"><article class="fc-a36-vote-card"><h4>Could not load your votes</h4><p>'+
   escapeIt(err?.message||'Please try again.')+'</p><button class="fc-a36-vote-refresh" data-a36-refresh>Try again</button></article></section>';
  root.querySelector('[data-a36-refresh]')?.addEventListener('click',function(){loadVotes(true)});
 });
}
var originalTab=window.renderProfileTab;
if(typeof originalTab==='function')window.renderProfileTab=function(){
 if(psState?.tab==='votes'&&own()){loadVotes(false);return}
 return originalTab.apply(this,arguments);
};
var originalSheet=window.renderProfileSheet;
if(typeof originalSheet==='function')window.renderProfileSheet=function(){
 var out=originalSheet.apply(this,arguments);requestAnimationFrame(installTab);return out;
};
var originalOwn=window.openOwnCompetitiveProfile;
if(typeof originalOwn==='function')window.openOwnCompetitiveProfile=function(){
 var out=originalOwn.apply(this,arguments);Promise.resolve(out).finally(function(){requestAnimationFrame(installTab)});return out;
};
document.addEventListener('click',function(e){
 if(e.target.closest('#profileSheet .ps-tab:not([data-pstab="votes"])'))serial++;
},true);
window.fcA36VotesV1390={refresh:function(){cache=null;if(own()&&psState.tab==='votes')loadVotes(true)},readOnly:true};
})();
</script>
"""
if s.count("</body>")!=1: raise SystemExit("Body close not unique")
s=s.replace("</body>",css+js+"\n</body>",1)
if s.count('name="fc-build"')<1 or s.count('fc-a36-v1390-votes-script')!=1:raise SystemExit("Candidate markers missing")
p.write_text(s,encoding="utf-8")
print("A3.6 v1390 integration candidate patched, source bytes",p.stat().st_size)
