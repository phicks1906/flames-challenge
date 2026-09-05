from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='<meta content="v1282 · modern-pull-to-refresh" name="fc-build"/>'
new='<meta content="v1283 · hall-of-fame-ceremony-and-detail-nav" name="fc-build"/>'
assert s.count(old)==1, s.count(old)
s=s.replace(old,new,1)
old2='<meta content="Refined pull-to-refresh into a compact native-feeling interaction: less page travel, a small progress ring, spinner, brief checkmark confirmation, threshold haptic where supported, and the same confirmed data reload." name="fc-whatsnew"/>'
new2='<meta content="Redesigned Hall of Fame as a ceremonial legacy surface with personal progress reduced to a compact secondary strip, and made the persistent bottom navigation close open read-only detail screens before navigating." name="fc-whatsnew"/>'
assert s.count(old2)==1, s.count(old2)
s=s.replace(old2,new2,1)
start=s.index('function renderHallOfFame() {')
end=s.index('\n}\n\n// Returns the Nx Champion label', start)+2
newfn=r'''function renderHallOfFame() {
  const el=document.getElementById('lbHofContent');if(!el)return;
  const log=getHofLog(),myId=state.profile?.id;
  const counts={};
  log.forEach(r=>{if(!counts[r.userId])counts[r.userId]={...r,count:0};counts[r.userId].count++;});
  const myCount=counts[myId]?.count||0;
  const myLevel=getLadderStatus(myId);
  const hofLevel=myLevel?.isHallOfFame?myLevel:null;
  const next=HOF_LEVELS.find(x=>myCount<x.min);
  const remaining=next?next.min-myCount:0;
  const firstHallMin=HOF_LEVELS[0]?.min||5;
  const pathPct=Math.max(0,Math.min(100,Math.round((Math.min(myCount,firstHallMin)/firstHallMin)*100)));

  const hero=`<section class="fc-hof-hero-v1283" aria-label="FlamesChallenge Hall of Fame">
    <div class="fc-hof-hero-light-v1283" aria-hidden="true"></div>
    <div class="fc-hof-hero-crest-v1283" aria-hidden="true"></div>
    <div class="fc-hof-hero-copy-v1283">
      <small>FLAMESCHALLENGE HALL OF FAME</small>
      <h3>Championships become legacy.</h3>
      <p>Win 5 Championships to enter as a Legend. Keep winning to rise through Icon, Immortal, and G.O.A.T.</p>
    </div>
    <div class="fc-hof-levels-v1283" aria-label="Hall of Fame levels">
      ${HOF_LEVELS.map((lvl,i)=>`<div class="${myCount>=lvl.min?'reached':''}"><span>${lvl.name}</span><b>${lvl.min}</b><em>${i===0?'titles to enter':'titles'}</em></div>`).join('')}
    </div>
  </section>`;

  const pathText=hofLevel
    ? `${hofLevel.name} · ${myCount} Championship title${myCount===1?'':'s'}`
    : `${Math.min(myCount,firstHallMin)} of ${firstHallMin} titles toward Legend`;
  const pathSub=hofLevel
    ? (next?`${remaining} more title${remaining===1?'':'s'} to ${next.name}`:'Highest Hall of Fame level reached')
    : (remaining?`${remaining} more Championship title${remaining===1?'':'s'} to enter the Hall`:'Hall of Fame qualified');
  const record=`<section class="fc-hof-path-v1283">
    <div class="fc-hof-path-copy-v1283"><small>YOUR PATH</small><strong>${pathText}</strong><span>${pathSub}</span></div>
    <div class="fc-hof-path-meter-v1283" aria-hidden="true"><i style="width:${hofLevel?100:pathPct}%"></i></div>
    <div class="fc-hof-path-actions-v1283"><button type="button" onclick="openBadgeLegend()">Levels</button>${myLevel?.isFounder?'<span>Founder</span>':''}</div>
  </section>`;

  let groups='';
  [...HOF_LEVELS].reverse().forEach((lvl,i,arr)=>{
    const upper=i===0?Infinity:arr[i-1].min;
    const members=Object.values(counts).filter(u=>u.count>=lvl.min&&u.count<upper).sort((a,b)=>b.count-a.count);
    if(!members.length)return;
    groups+=`<section class="fc-hof-group-v1283">
      <header><div><small>HALL LEVEL</small><h4>${lvl.name}</h4></div><span>${lvl.min}+ titles · ${lvl.points} Opponent Points</span></header>
      <div class="fc-hof-members-v1283">${members.map((u,index)=>`<button type="button" class="fc-hof-member-v1283" data-hof-profile-v1283="${escapeHtml(u.userId)}">
        <span class="fc-hof-rank-v1283">${String(index+1).padStart(2,'0')}</span>
        <span class="fc-hof-avatar-v1283">${honoredAvatarHTML(u.userId,avatarInner(u.avatar),44)}</span>
        <span class="fc-hof-member-copy-v1283"><b>${escapeHtml(u.name)}${u.userId===myId?' <em>YOU</em>':''}</b><small>${u.count} Championship title${u.count===1?'':'s'}</small></span>
        <span class="fc-hof-member-level-v1283">${renderLadderChip(u.userId,{includeFounder:false})}</span>
      </button>`).join('')}</div>
    </section>`;
  });

  if(!groups)groups=`<section class="fc-hof-vacant-v1283">
    <div class="fc-hof-vacant-crest-v1283" aria-hidden="true"></div>
    <small>THE FIRST SEAT IS OPEN</small>
    <h4>No competitor has entered the Hall yet.</h4>
    <p>The first competitor to win 5 Championships becomes a Legend and takes the first place in FlamesChallenge history.</p>
  </section>`;

  const byMonth={};
  log.forEach(r=>{if(r.category==='All')return;(byMonth[r.month]||(byMonth[r.month]=[])).push(r);});
  const history=Object.keys(byMonth).sort().reverse().map(m=>{
    const [y,mo]=m.split('-'),label=new Date(Number(y),Number(mo)-1,1).toLocaleString('default',{month:'long',year:'numeric'});
    return `<section class="fc-hof-history-month-v1283"><h5>${label}</h5>${byMonth[m].map(r=>`<button type="button" class="fc-hof-history-row-v1283" data-hof-profile-v1283="${escapeHtml(r.userId)}"><span>${escapeHtml(r.category)}</span><span class="fc-hof-history-avatar-v1283">${avatarInner(r.avatar)}</span><b>${escapeHtml(r.name)}${r.userId===myId?' <em>YOU</em>':''}</b></button>`).join('')}</section>`;
  }).join('');

  const founders=FOUNDERS.map(fid=>{
    const p=(state.leaderboardData?.users||[]).find(u=>u.id===fid)||{id:fid,name:fid===FOUNDERS[0]?'Admin':'ehicks23',avatar:'🔥'};
    return `<button type="button" class="fc-hof-founder-v1283" data-hof-profile-v1283="${escapeHtml(p.id)}">
      <span class="fc-hof-founder-avatar-v1283">${avatarInner(p.avatar)}</span>
      <span class="fc-hof-founder-copy-v1283"><b>${escapeHtml(p.name)}${p.id===myId?' <em>YOU</em>':''}</b><small>Permanent platform recognition</small></span>
      <span class="fc-hof-founder-badge-v1283"><img class="hof-badge-img" src="${LADDER_BADGE_BASE}founder.png" width="24" height="24" alt="">Founder</span>
    </button>`;
  }).join('');

  el.innerHTML=`<div class="fc-hof-shell-v1283">${hero}${record}<div class="fc-hof-section-head-v1283"><small>IMMORTALIZED COMPETITORS</small><span>Championship titles determine Hall level</span></div>${groups}${history?`<div class="fc-hof-section-head-v1283 fc-hof-history-head-v1283"><small>CHAMPIONSHIP ARCHIVE</small><span>Every recorded category champion</span></div><div class="fc-hof-history-v1283">${history}</div>`:''}<div class="fc-hof-section-head-v1283 fc-hof-founders-head-v1283"><small>FOUNDERS OF FLAMESCHALLENGE</small><span>Separate from earned Hall levels</span></div><div class="fc-hof-founders-v1283">${founders}</div></div>`;

  el.querySelectorAll('[data-hof-profile-v1283]').forEach(btn=>btn.addEventListener('click',()=>{const id=btn.dataset.hofProfileV1283;if(id&&typeof openUserProfile==='function')openUserProfile(id)}));
}
'''
s=s[:start]+newfn+s[end:]
block=r'''
<style id="fc-v1283-hall-of-fame-and-detail-nav-css">
#lbMainTabs .feed-tab[data-lbtab="halloffame"].active{color:#17100a!important;border-color:rgba(255,220,139,.70)!important;background:linear-gradient(110deg,#a96a12 0%,#f4c85b 26%,#fff1ae 49%,#d89b27 72%,#8f5610 100%)!important;box-shadow:0 7px 20px rgba(201,136,29,.18),inset 0 1px 0 rgba(255,255,255,.55)!important;text-shadow:0 1px 0 rgba(255,255,255,.26)!important}
#lbTabHallOfFame{margin-top:2px}.fc-hof-shell-v1283{position:relative;padding-bottom:12px}
.fc-hof-hero-v1283{position:relative;overflow:hidden;border:1px solid rgba(224,176,72,.30);border-radius:22px;min-height:286px;padding:22px 18px 16px;background:radial-gradient(ellipse 72% 60% at 50% -8%,rgba(255,194,76,.16),transparent 64%),linear-gradient(180deg,#151006 0%,#0b0805 62%,#080605 100%);box-shadow:0 20px 48px rgba(0,0,0,.34),inset 0 1px 0 rgba(255,236,183,.08);isolation:isolate}.fc-hof-hero-v1283::before,.fc-hof-hero-v1283::after{content:"";position:absolute;top:-34px;width:160px;height:330px;background:linear-gradient(180deg,rgba(255,224,147,.18),rgba(255,184,63,.035) 45%,transparent 80%);filter:blur(1px);opacity:.48;pointer-events:none;z-index:-1}.fc-hof-hero-v1283::before{left:-44px;transform:rotate(18deg)}.fc-hof-hero-v1283::after{right:-44px;transform:rotate(-18deg)}.fc-hof-hero-light-v1283{position:absolute;left:50%;top:-8%;width:86%;height:74%;transform:translateX(-50%);background:radial-gradient(ellipse at center,rgba(255,197,82,.18),rgba(255,112,30,.045) 42%,transparent 72%);pointer-events:none}.fc-hof-hero-crest-v1283{width:92px;height:92px;margin:0 auto 5px;background-image:var(--fc-approved-crowned-f);background-size:contain;background-position:center;background-repeat:no-repeat;filter:brightness(1.12) contrast(1.05) drop-shadow(0 10px 25px rgba(255,146,36,.26));position:relative}.fc-hof-hero-copy-v1283{text-align:center;position:relative;z-index:1}.fc-hof-hero-copy-v1283 small{display:block;color:#d6a942;font:800 9px/1.2 var(--font-ui);letter-spacing:.19em;margin-bottom:7px}.fc-hof-hero-copy-v1283 h3{margin:0;color:#fff8e8;font-family:var(--font-bricolage);font-size:clamp(25px,6.4vw,34px);line-height:1.02;letter-spacing:-.025em}.fc-hof-hero-copy-v1283 p{max-width:500px;margin:9px auto 0;color:#bcae9f;font-size:12px;line-height:1.48}.fc-hof-levels-v1283{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:6px;margin-top:17px;position:relative;z-index:1}.fc-hof-levels-v1283 div{min-width:0;padding:9px 5px 8px;border:1px solid rgba(255,214,126,.12);border-radius:12px;background:rgba(255,255,255,.025);text-align:center}.fc-hof-levels-v1283 div.reached{border-color:rgba(255,204,91,.38);background:rgba(255,194,72,.075)}.fc-hof-levels-v1283 span,.fc-hof-levels-v1283 b,.fc-hof-levels-v1283 em{display:block}.fc-hof-levels-v1283 span{color:#d2b46b;font-size:9px;font-weight:850;letter-spacing:.05em}.fc-hof-levels-v1283 b{color:#fff7e6;font-size:16px;line-height:1.1;margin-top:3px}.fc-hof-levels-v1283 em{color:#806f60;font-size:7px;font-style:normal;text-transform:uppercase;letter-spacing:.08em;margin-top:2px}
.fc-hof-path-v1283{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:9px 12px;align-items:center;margin:10px 0 18px;padding:11px 12px;border:1px solid rgba(255,255,255,.08);border-radius:14px;background:rgba(255,255,255,.018)}.fc-hof-path-copy-v1283{min-width:0}.fc-hof-path-copy-v1283 small,.fc-hof-path-copy-v1283 strong,.fc-hof-path-copy-v1283 span{display:block}.fc-hof-path-copy-v1283 small{color:#8f8175;font-size:7.5px;font-weight:850;letter-spacing:.16em}.fc-hof-path-copy-v1283 strong{margin-top:3px;color:#efe8df;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.fc-hof-path-copy-v1283 span{margin-top:2px;color:#85786f;font-size:9.5px;line-height:1.3}.fc-hof-path-meter-v1283{grid-column:1/-1;height:3px;border-radius:999px;background:rgba(255,255,255,.07);overflow:hidden}.fc-hof-path-meter-v1283 i{display:block;height:100%;border-radius:inherit;background:linear-gradient(90deg,#b67616,#f5cc66);box-shadow:0 0 8px rgba(233,176,55,.24)}.fc-hof-path-actions-v1283{display:flex;align-items:center;gap:6px}.fc-hof-path-actions-v1283 button{appearance:none;border:1px solid rgba(255,255,255,.11);border-radius:999px;background:rgba(255,255,255,.025);color:#c8bdb3;padding:7px 9px;font:800 9px/1 var(--font-ui)}.fc-hof-path-actions-v1283>span{padding:6px 8px;border-radius:999px;border:1px solid rgba(255,191,73,.20);color:#c99a41;font-size:8px;font-weight:850}.fc-hof-section-head-v1283{display:flex;align-items:end;justify-content:space-between;gap:12px;margin:19px 2px 8px}.fc-hof-section-head-v1283 small{color:#d2a94a;font-size:8.5px;font-weight:900;letter-spacing:.16em}.fc-hof-section-head-v1283 span{color:#70665f;font-size:8.5px;text-align:right}
.fc-hof-vacant-v1283{position:relative;overflow:hidden;text-align:center;padding:25px 18px 23px;border:1px solid rgba(226,181,76,.17);border-radius:18px;background:radial-gradient(circle at 50% 0%,rgba(227,164,48,.08),transparent 58%),#0d0a07}.fc-hof-vacant-crest-v1283{width:66px;height:66px;margin:0 auto 4px;background-image:var(--fc-approved-crowned-f);background-size:contain;background-position:center;background-repeat:no-repeat;filter:grayscale(.2) brightness(.66) sepia(.22);opacity:.70}.fc-hof-vacant-v1283 small{display:block;color:#9b7d3c;font-size:8px;font-weight:900;letter-spacing:.18em}.fc-hof-vacant-v1283 h4{margin:8px 0 0;color:#efe8df;font-family:var(--font-bricolage);font-size:17px}.fc-hof-vacant-v1283 p{max-width:430px;margin:6px auto 0;color:#8f8278;font-size:10.5px;line-height:1.45}.fc-hof-group-v1283{overflow:hidden;margin-bottom:11px;border:1px solid rgba(226,181,76,.18);border-radius:17px;background:linear-gradient(160deg,#120e09,#0b0907)}.fc-hof-group-v1283>header{display:flex;align-items:end;justify-content:space-between;gap:12px;padding:12px 13px;border-bottom:1px solid rgba(255,255,255,.06)}.fc-hof-group-v1283 header small{display:block;color:#76695e;font-size:7px;font-weight:850;letter-spacing:.15em}.fc-hof-group-v1283 h4{margin:3px 0 0;color:#e8bf62;font-size:16px}.fc-hof-group-v1283 header>span{color:#766b62;font-size:8.5px;text-align:right}.fc-hof-member-v1283{appearance:none;width:100%;display:grid;grid-template-columns:28px 48px minmax(0,1fr) auto;align-items:center;gap:9px;padding:11px 13px;border:0;border-bottom:1px solid rgba(255,255,255,.055);background:transparent;color:inherit;text-align:left}.fc-hof-member-v1283:last-child{border-bottom:0}.fc-hof-member-v1283:active{background:rgba(255,196,75,.04)}.fc-hof-rank-v1283{color:#665c54;font:750 9px/1 var(--font-ui);letter-spacing:.08em}.fc-hof-avatar-v1283{width:44px;height:44px;display:grid;place-items:center}.fc-hof-avatar-v1283 img,.fc-hof-avatar-v1283 .avatar-img{width:100%;height:100%;object-fit:cover;border-radius:50%}.fc-hof-member-copy-v1283{min-width:0}.fc-hof-member-copy-v1283 b{display:block;color:#f4eee7;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.fc-hof-member-copy-v1283 b em,.fc-hof-history-row-v1283 b em,.fc-hof-founder-copy-v1283 b em{display:inline-block;margin-left:5px;color:#9d8755;font-size:7px;font-style:normal;letter-spacing:.08em}.fc-hof-member-copy-v1283 small{display:block;margin-top:3px;color:#84786f;font-size:9px}.fc-hof-member-level-v1283{display:flex;justify-content:flex-end}.fc-hof-member-level-v1283 .ladder-chip{font-size:8px!important;padding:4px 6px!important}
.fc-hof-history-v1283{display:grid;gap:8px}.fc-hof-history-month-v1283{overflow:hidden;border:1px solid rgba(255,255,255,.07);border-radius:14px;background:rgba(255,255,255,.018)}.fc-hof-history-month-v1283 h5{margin:0;padding:9px 11px;color:#9c8e81;font-size:9px;letter-spacing:.06em;border-bottom:1px solid rgba(255,255,255,.05)}.fc-hof-history-row-v1283{appearance:none;width:100%;display:grid;grid-template-columns:90px 28px minmax(0,1fr);align-items:center;gap:8px;padding:9px 11px;border:0;border-bottom:1px solid rgba(255,255,255,.045);background:transparent;color:inherit;text-align:left}.fc-hof-history-row-v1283:last-child{border-bottom:0}.fc-hof-history-row-v1283>span:first-child{color:#b49450;font-size:9px;font-weight:800}.fc-hof-history-avatar-v1283{width:28px;height:28px;overflow:hidden;border-radius:50%}.fc-hof-history-avatar-v1283 img,.fc-hof-history-avatar-v1283 .avatar-img{width:100%;height:100%;object-fit:cover;border-radius:50%}.fc-hof-history-row-v1283 b{color:#d8d0c8;font-size:10.5px;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.fc-hof-founders-v1283{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.fc-hof-founder-v1283{appearance:none;display:grid;grid-template-columns:38px minmax(0,1fr);gap:4px 9px;align-items:center;padding:10px;border:1px solid rgba(255,255,255,.07);border-radius:14px;background:rgba(255,255,255,.018);color:inherit;text-align:left}.fc-hof-founder-avatar-v1283{grid-row:1/3;width:38px;height:38px;overflow:hidden;border-radius:50%}.fc-hof-founder-avatar-v1283 img,.fc-hof-founder-avatar-v1283 .avatar-img{width:100%;height:100%;object-fit:cover;border-radius:50%}.fc-hof-founder-copy-v1283{min-width:0}.fc-hof-founder-copy-v1283 b{display:block;color:#d8d0c8;font-size:11px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.fc-hof-founder-copy-v1283 small{display:block;margin-top:2px;color:#746a62;font-size:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.fc-hof-founder-badge-v1283{grid-column:2;display:inline-flex;align-items:center;gap:4px;justify-self:start;color:#a88342;font-size:8px;font-weight:800}.fc-hof-founder-badge-v1283 .hof-badge-img{width:16px!important;height:16px!important}#profileSheet.open,#challengeDetailSheet.open,#entryViewerSheet.open,#feedViewerSheet.open,#postSheet.open,#recordSheet.open{padding-bottom:var(--fc-bottom-nav-bar-h)!important}@media(max-width:430px){.fc-hof-hero-v1283{min-height:272px;padding-inline:14px}.fc-hof-levels-v1283{gap:4px}.fc-hof-levels-v1283 span{font-size:8px}.fc-hof-levels-v1283 b{font-size:15px}.fc-hof-founders-v1283{grid-template-columns:1fr}.fc-hof-member-v1283{grid-template-columns:22px 44px minmax(0,1fr) auto;padding-inline:10px}.fc-hof-member-level-v1283 .ladder-chip{font-size:0!important;gap:0!important}.fc-hof-member-level-v1283 .hof-badge-img{width:25px!important;height:25px!important}}
</style>
<script id="fc-v1283-detail-nav-js">
(function(){'use strict';function isOpen(id){return document.getElementById(id)?.classList.contains('open')}function closeReadOnlyDetails(target){const profile=document.getElementById('profileSheet');if(profile?.classList.contains('open')){const own=profile.classList.contains('fc-own-profile-page-v1075');if(!(target==='you'&&own)){try{if(typeof closeProfileSheet==='function')closeProfileSheet(true)}catch(_){}}}const closers=[['challengeDetailSheet','closeChallengeDetail'],['entryViewerSheet','closeEntryViewer'],['feedViewerSheet','closeFeedViewer'],['postSheet','closePostView'],['recordSheet','closeRecordSheet'],['boostSheet','closeBoostSheet'],['badgeLegendSheet','closeBadgeLegend']];closers.forEach(([id,fn])=>{if(isOpen(id)&&typeof window[fn]==='function'){try{window[fn]()}catch(_){}}});const archive=document.getElementById('fcProfileArchiveV1036');if(archive?.classList.contains('open')){try{window.closeProfileArchiveV1036?.()}catch(_){archive.classList.remove('open')}}}function navTarget(btn){if(!btn)return null;if(btn.classList.contains('bnav-create'))return 'create';return btn.dataset.view||null}const nav=document.getElementById('bottomNav');if(nav&&!nav.dataset.fcDetailNavV1283){nav.dataset.fcDetailNavV1283='1';nav.addEventListener('click',e=>{const btn=e.target.closest('button');if(!btn||!nav.contains(btn))return;const target=navTarget(btn);if(!target)return;closeReadOnlyDetails(target)},true)}window.fcCloseReadOnlyDetailsV1283=closeReadOnlyDetails;window.FC_V1283_VALIDATION={build:'v1283',hallCeremonialHero:true,personalRecordSecondary:true,hofTierProgression:true,hofFoundersSecondary:true,detailNavClosesReadOnlySheets:true,bottomNavStillPersistent:true,entryEditorNavHidePreserved:true};})();
</script>
'''
assert 'id="fc-v1283-hall-of-fame-and-detail-nav-css"' not in s
assert '</body>' in s
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
