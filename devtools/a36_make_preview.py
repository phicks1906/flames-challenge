#!/usr/bin/env python3
"""Build a network-free, sample-data A3.6 Votes preview from the REAL staged component.
This is an isolated visual/interaction prototype, NOT a signed-in application deployment.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "devtools" / "a36_votes_component.html"
OUT = ROOT / "preview" / "a36-votes.html"

TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="robots" content="noindex,nofollow">
<title>FlamesChallenge A3.6 — Votes preview (sample data)</title>
<style>
*{box-sizing:border-box}
:root{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color-scheme:dark;--p-card:#1c1d20;--p-border:#383b40;--p-text:#f5f3f2;--p-muted:#aaaab1;--p-dim:#d2d0d0;--ember:#ff692b;--surface:#1c1d20;--text:#f5f3f2;--border:#383b40;--text-muted:#aaaab1}
body{margin:0;background:#101114;color:var(--p-text);min-height:100svh}
body.light{color-scheme:light;--p-card:#fff;--p-border:#dddfe4;--p-text:#202127;--p-muted:#60616c;--p-dim:#4c4d57;--surface:#fff;--text:#202127;--border:#dddfe4;--text-muted:#60616c;background:#f5f5f6}
button{cursor:pointer}
.demo-banner{background:#3e2619;border-bottom:1px solid #ad5e31;color:#ffe1ca;font-size:12px;padding:10px max(16px, env(safe-area-inset-right));line-height:1.45;text-align:center}
.light .demo-banner{background:#fff0df;color:#813c12}
.appbar{height:65px;padding:0 16px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--p-border);background:var(--p-card)}
.wordmark{letter-spacing:2px;font-weight:900;font-size:15px}
.controlrow{display:flex;gap:7px;flex-wrap:wrap;align-items:center}
.smallbtn{background:transparent;border:1px solid var(--p-border);border-radius:10px;color:var(--p-text);padding:8px 11px;font-size:12px}
.smallbtn.selected{border-color:var(--ember);color:var(--ember)}
.page{max-width:560px;margin:0 auto;padding:22px 14px 105px}
.kicker{text-transform:uppercase;font-size:10px;letter-spacing:1.8px;font-weight:800;color:var(--ember)}
h1{font-size:27px;margin:4px 0 8px}
.note{font-size:12px;line-height:1.5;color:var(--p-muted);margin:0 0 18px}
#profileSheet{background:var(--p-card);border:1px solid var(--p-border);border-radius:19px;overflow:hidden}
.profile-head{padding:18px 16px 14px;display:flex;gap:11px;align-items:center}
.avatar{width:45px;height:45px;border-radius:50%;display:grid;place-items:center;background:#4c2920;color:#fff;font-weight:900}
.person{font-size:16px;font-weight:800}.subtitle{color:var(--p-muted);font-size:12px;margin-top:3px}
.ps-tabs{padding:0 10px;display:flex;gap:3px;overflow-x:auto;border-bottom:1px solid var(--p-border)}
.ps-tab{flex:1;white-space:nowrap;min-width:66px;min-height:44px;border:0;background:transparent;color:var(--p-muted);font-size:12px;font-weight:750;border-bottom:2px solid transparent}
.ps-tab.active{color:var(--ember);border-bottom-color:var(--ember)}
#psContent{padding:16px;min-height:210px}
.demo-empty{padding:24px 8px;color:var(--p-muted);font-size:13px;line-height:1.6;text-align:center}
.footer-nav{position:fixed;bottom:0;left:0;right:0;display:flex;justify-content:center;background:var(--p-card);border-top:1px solid var(--p-border);padding:12px 10px calc(12px + env(safe-area-inset-bottom));font-size:12px;gap:28px;z-index:5}
.footer-nav .sel{color:var(--ember);font-weight:850}
#demoViewer[hidden]{display:none}
#demoViewer{position:fixed;inset:0;z-index:30;background:rgba(0,0,0,.7);display:flex;align-items:flex-end;justify-content:center;padding:15px 12px max(20px,env(safe-area-inset-bottom))}
.viewer-body{width:100%;max-width:520px;padding:20px;border-radius:18px;background:var(--p-card);border:1px solid var(--p-border)}
.viewer-body h2{font-size:19px;margin:7px 0 12px}
.viewer-body p{color:var(--p-muted);font-size:13px;line-height:1.55}
.closeviewer{width:100%;background:var(--ember);color:#161616;border:0;border-radius:10px;padding:13px;font-weight:800}
.preview-flag{margin-top:22px;font-size:11px;color:var(--p-muted);line-height:1.55}
@media(max-width:390px){.wordmark{font-size:12px;letter-spacing:1px}.appbar{padding:0 12px}.smallbtn{padding:7px 8px}.page{padding:17px 9px 105px}#psContent{padding:11px}.profile-head{padding:14px 12px}}
</style>
</head>
<body>
<div class="demo-banner"><strong>A3.6 BRANCH PREVIEW — SAMPLE DATA</strong><br>No sign-in, live votes, settled results or production changes. This page tests the staged Votes component only.</div>
<header class="appbar"><span class="wordmark">FLAMES CHALLENGE</span><div class="controlrow"><button id="viewSwitch" class="smallbtn" type="button" aria-label="Switch member view">Other profile</button><button id="themeSwitch" class="smallbtn" type="button">Light</button></div></header>
<main class="page">
<div class="kicker">You / voting history</div><h1>My activity</h1>
<p class="note">A3.6 Part 1: locate competitions you voted in. Results and Following will connect in later checkpoints.</p>
<section id="profileSheet" class="open" aria-label="Profile preview">
<div class="profile-head"><div class="avatar">F</div><div><div class="person" id="profileName">Preview member</div><div class="subtitle" id="profileDesc">Your competitions and activity</div></div></div>
<div class="ps-tabs" role="tablist">
<button class="ps-tab" type="button" data-pstab="challenges">Challenges</button>
<button class="ps-tab" type="button" data-pstab="entries">Entries</button>
<button class="ps-tab" type="button" data-pstab="posts">Posts</button>
</div>
<div id="psContent"></div>
</section>
<p class="preview-flag">This is a real HTML/JavaScript component preview using local sample records, not a working Supabase integration or pixel-for-pixel reproduction of production navigation. Sign-in is intentionally unavailable.</p>
</main>
<nav class="footer-nav" aria-label="Preview navigation"><span>Home</span><span>Compete</span><span>+</span><span>Titles</span><span class="sel">You</span></nav>
<div id="demoViewer" hidden role="dialog" aria-modal="true" aria-label="Sample challenge viewer"><div class="viewer-body"><div class="kicker">Challenge preview / sample</div><h2 id="viewerTitle"></h2><p id="viewerText"></p><button type="button" class="closeviewer" id="viewerClose">Back to You</button></div></div>
<script>
/* Small browser-only stand-ins for the actual app, using the same component script. */
const previewRows={
 entry_votes:[
 {id:'sample-v1',challenge_id:'sample-c1',entry_id:'sample-e1',voter_id:'preview-user',created_at:'2026-11-17T15:00:00Z'},
 {id:'sample-v2',challenge_id:'sample-c2',entry_id:'sample-e2',voter_id:'preview-user',created_at:'2026-11-11T17:00:00Z'},
 {id:'sample-v3',challenge_id:'sample-c3',entry_id:'sample-e3',voter_id:'preview-user',created_at:'2026-10-28T17:00:00Z'},
 {id:'hidden-example',challenge_id:'sample-hidden',entry_id:'sample-hidden-entry',voter_id:'another-user',created_at:'2026-10-29T17:00:00Z'}
 ],
 challenges:[
 {id:'sample-c1',title:'Live Vocal Challenge',category:'Music',status:'Open / sample'},
 {id:'sample-c2',title:'Street Photography Showdown',category:'Photography',status:'Closed / sample'},
 {id:'sample-c3',title:'Best Home-Cooked Meal',category:'Cooking',status:'Processing / sample'}
 ],
 entries:[
 {id:'sample-e1',challenge_id:'sample-c1',user_id:'sample-nia',submitter:{id:'sample-nia',name:'Nia Brooks',avatar:'N'}},
 {id:'sample-e2',challenge_id:'sample-c2',user_id:'sample-jordan',submitter:{id:'sample-jordan',name:'Jordan Lee',avatar:'J'}},
 {id:'sample-e3',challenge_id:'sample-c3',user_id:'sample-aria',submitter:{id:'sample-aria',name:'Aria Wells',avatar:'A'}}
 ]};
function previewQuery(table){
 const spec={table,filters:[],range:null,order:null};
 const q={
  select(){return q},
  eq(k,v){spec.filters.push(['eq',k,v]);return q},
  in(k,v){spec.filters.push(['in',k,v]);return q},
  order(k){spec.order=k;return q},
  range(a,b){spec.range=[a,b];return q},
  then(resolve,reject){
   let data=(previewRows[table]||[]).slice();
   for(const f of spec.filters)data=data.filter(x=>f[0]==='eq'?x[f[1]]===f[2]:f[2].includes(x[f[1]]));
   if(spec.order==='created_at')data.sort((a,b)=>b.created_at.localeCompare(a.created_at));
   if(spec.range)data=data.slice(spec.range[0],spec.range[1]+1);
   return Promise.resolve({data,error:null}).then(resolve,reject);
  }
 };
 return q;
}
const state={profile:{id:'preview-user'},currentView:'you',challenges:[],myVotes:{poll_example:true}};
const psState={userId:'preview-user',profile:{id:'preview-user'},tab:'votes'};
const db={from:previewQuery};
const fcWithTimeoutV1099=async q=>await q;
function escapeHtml(v){return String(v).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;')}
function toast(s){alert(s)}
function openFeedViewer(id){
 const ch=previewRows.challenges.find(x=>x.id===id);
 document.getElementById('viewerTitle').textContent=ch?ch.title:'Unavailable';
 document.getElementById('viewerText').textContent='Sample navigation from your vote history. The production challenge viewer is not part of this isolated preview; official results are not yet connected.';
 document.getElementById('demoViewer').hidden=false;
}
window.renderProfileSheet=function(){};
window.renderProfileTab=function(){
 if(psState.tab==='votes')return;
 document.getElementById('psContent').innerHTML='<div class="demo-empty">Sample '+escapeHtml(psState.tab)+' view. Use the Votes tab to try the A3.6 component.</div>';
};
</script>
<!-- INSERT THE ACTUAL STAGED A3.6 COMPONENT HERE -->
<script>
document.querySelectorAll('.ps-tabs [data-pstab]').forEach(b=>b.addEventListener('click',function(){
 psState.tab=b.dataset.pstab;
 window.renderProfileSheet();
 window.renderProfileTab();
}));
function refreshPreview(){
 window.renderProfileSheet();
 window.renderProfileTab();
 document.getElementById('profileName').textContent=psState.userId==='preview-user'?'Preview member':'Another member';
 document.getElementById('profileDesc').textContent=psState.userId==='preview-user'?'Your competitions and activity':'Public profile / votes hidden';
 document.getElementById('viewSwitch').textContent=psState.userId==='preview-user'?'Other profile':'My profile';
}
document.getElementById('viewSwitch').addEventListener('click',()=>{
 const other=psState.userId==='preview-user';
 psState.userId=other?'another-user':'preview-user';
 psState.profile={id:psState.userId};
 psState.tab=other?'challenges':'votes';
 refreshPreview();
});
document.getElementById('themeSwitch').addEventListener('click',()=>{
 const light=document.body.classList.toggle('light');
 document.getElementById('themeSwitch').textContent=light?'Dark':'Light';
});
document.getElementById('viewerClose').addEventListener('click',()=>document.getElementById('demoViewer').hidden=true);
document.getElementById('demoViewer').addEventListener('click',event=>{if(event.target.id==='demoViewer')event.currentTarget.hidden=true;});
document.addEventListener('keydown',event=>{if(event.key==='Escape')document.getElementById('demoViewer').hidden=true;});
refreshPreview();
</script>
</body></html>
'''

def main():
    component = COMPONENT.read_text(encoding="utf-8")
    assert component.count('<script id="fc-a36-v1390-votes-js">') == 1
    assert component.count('<style id="fc-a36-v1390-votes-css">') == 1
    assert TEMPLATE.count('<!-- INSERT THE ACTUAL STAGED A3.6 COMPONENT HERE -->') == 1
    output = TEMPLATE.replace('<!-- INSERT THE ACTUAL STAGED A3.6 COMPONENT HERE -->', component)
    assert output.count('fc-a36-v1390-votes-js') == 1
    assert output.count('SAMPLE DATA') == 1
    assert not re.search(r'https?://[^\s"\'<>]*supabase', output, re.I)
    assert 'createClient' not in output and 'service_role' not in output
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(output, encoding="utf-8")
    print(f"Built isolated preview: {OUT.relative_to(ROOT)} ({len(output)} chars)")

if __name__ == "__main__":
    main()
