from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def one(old,new,label):
    global s
    c=s.count(old)
    if c!=1:
        raise SystemExit(f'{label}: expected 1, found {c}')
    s=s.replace(old,new,1)

one('<meta content="v1297 · detail-video-layer-and-record-swipe-identity" name="fc-build"/>',
    '<meta content="v1298 · unmistakable-final-results-and-entry-access" name="fc-build"/>','build meta')
one('<meta content="Stopped Challenge Detail video previews from painting over challenger identity, and made Record-style audio entries visibly distinct while swiping by putting each challenger’s profile image on the record label." name="fc-whatsnew"/>',
    '<meta content="Made finished challenges unmistakably complete and made every competitor in Final Results tappable so members can open the exact winning or losing entry after voting ends." name="fc-whatsnew"/>','whatsnew')

one("""  } else if (ps.key === 'closed') {
    wrap = 'closed'; s1 = 'done'; s2 = 'done'; s3 = 'live'; cd3 = 'Decided';
""",
"""  } else if (ps.key === 'closed') {
    wrap = 'closed'; s1 = 'done'; s2 = 'done'; s3 = 'done';
    cd1 = 'Closed'; cd2 = 'Closed'; cd3 = 'Decided';
""",'closed journey state')

one("""    } else {
      btn.textContent = '📋 View Details';
      btn.style.display = 'block';
    }
""",
"""    } else if (status === 'closed') {
      btn.textContent = '📋 View Full Details';
      btn.style.display = 'block';
    } else {
      btn.textContent = '📋 View Details';
      btn.style.display = 'block';
    }
""",'closed view full details label')

one("""    winnerHtmlV1203 = `<div class="fc-v1196-winner-summary">
      <span class="fc-v1196-winner-kicker">${coWinnerV1203 ? 'Co-winners' : 'Winner'}</span>
      <strong>${escapeHtml(namesV1203)}</strong>
      <small>${displayedVotesV1203} vote${displayedVotesV1203 === 1 ? '' : 's'} · ${winnerPctV1203}%</small>
    </div>`;
""",
"""    winnerHtmlV1203 = `<div class="fc-v1196-winner-summary fc-v1298-winner-summary">
      <span class="fc-v1298-winner-medal" aria-hidden="true">${coWinnerV1203 ? '🏆' : '🥇'}</span>
      <span class="fc-v1196-winner-kicker">${coWinnerV1203 ? 'Co-winners' : 'Winner'}</span>
      <strong>${escapeHtml(namesV1203)}</strong>
      <small>${displayedVotesV1203} vote${displayedVotesV1203 === 1 ? '' : 's'} · ${winnerPctV1203}%</small>
    </div>`;
""",'winner summary')

one("""      return `<div class="fc-v1024-final-row${isSettledWinnerV1203 ? ' leader' : ''}">
        <span class="rank">${icon}</span>
        <span class="avatar">${avatarInner(sub.avatar)}</span>
        <span class="name">${escapeHtml(sub.name || 'Unknown')}${pick ? ' <small>· your vote</small>' : ''}</span>
        <span class="votes">${v} · ${pct}%</span>
      </div>`;
""",
"""      return `<button type="button" class="fc-v1024-final-row fc-v1298-final-entry-row${isSettledWinnerV1203 ? ' leader' : ''}" data-fv-result-entry="${escapeHtml(e.id)}" data-fv-result-challenge="${escapeHtml(chId)}" aria-label="Open ${escapeHtml(sub.name || 'competitor')} entry">
        <span class="rank">${icon}</span>
        <span class="avatar">${avatarInner(sub.avatar)}</span>
        <span class="name">${escapeHtml(sub.name || 'Unknown')}${pick ? ' <small>· your vote</small>' : ''}</span>
        <span class="votes">${v} · ${pct}%</span>
        <span class="fc-v1298-result-chevron" aria-hidden="true">›</span>
      </button>`;
""",'final row button')

one("""  panel.innerHTML = `<div class="fc-v1024-final-standings">
    ${winningMediaHtmlV1203}
    ${winnerHtmlV1203}
    <div class="fc-v1024-final-title">${status === 'closed' ? 'Final results' : 'Live standings'}</div>
""",
"""  const completedAtV1298 = authoritativeResultV1203?.resolved_at || ch?.voting_end || null;
  const completedWhenV1298 = completedAtV1298 && typeof timeAgo === 'function' ? timeAgo(completedAtV1298) : '';
  const completeHeroV1298 = status === 'closed'
    ? `<div class="fc-v1298-complete-hero">
        <span class="fc-v1298-complete-icon" aria-hidden="true">🏆</span>
        <div class="fc-v1298-complete-copy">
          <strong>Challenge Complete</strong>
          <span>Final results are in. Voting is closed.${completedWhenV1298 ? ` · ${escapeHtml(completedWhenV1298)}` : ''}</span>
        </div>
      </div>`
    : '';

  panel.innerHTML = `<div class="fc-v1024-final-standings fc-v1298-final-standings">
    ${completeHeroV1298}
    ${winnerHtmlV1203}
    ${winningMediaHtmlV1203}
    <div class="fc-v1024-final-title">${status === 'closed' ? 'Final results' : 'Live standings'}</div>
""",'final panel hero reorder')

one("""  panel.querySelectorAll('.fc-v1195-winning-video-host').forEach(host => {
    host.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') playFvWinnerVideoV1195(host, ev);
    });
  });
  _checkFreshVideoEncoding(panel);
""",
"""  panel.querySelectorAll('.fc-v1195-winning-video-host').forEach(host => {
    host.addEventListener('keydown', ev => {
      if (ev.key === 'Enter' || ev.key === ' ') playFvWinnerVideoV1195(host, ev);
    });
  });
  panel.querySelectorAll('[data-fv-result-entry]').forEach(row => {
    row.addEventListener('click', () => {
      const entryId = row.dataset.fvResultEntry;
      const challengeId = row.dataset.fvResultChallenge || chId;
      if (entryId) openEntryViewer(entryId, challengeId);
    });
  });
  _checkFreshVideoEncoding(panel);
""",'wire result entry clicks')

marker="<script>window.FC_V1297_VALIDATION={build:'v1297',challengeDetailUsesStaticVideoPoster:true,noDetailVideoLayerOverIdentity:true,feedVideoPreviewPreserved:true,recordLabelUsesChallengerAvatar:true,recordOuterGeometryPreserved:true,v1296EmberPendingScopePreserved:true};</script>"
css="""
<style id="fc-v1298-complete-results-css">
.fvj.closed .fvj-node.done .fvj-ic{
  background:linear-gradient(135deg,var(--gold),#d89d21)!important;
  border-color:rgba(255,215,120,.72)!important;
  filter:none!important;
  box-shadow:0 0 11px rgba(255,200,87,.28)!important;
}
.fvj.closed .fvj-node.done .fvj-t{color:var(--gold)!important}
.fvj.closed .fvj-line.done{background:linear-gradient(90deg,#c88d22,var(--gold),#c88d22)!important}
.fvj.closed .fvj-cd{color:#d8c6a0!important}
#feedViewerModal #fvStandings .fc-v1298-final-standings{
  gap:12px!important;
  border-color:rgba(255,196,76,.22)!important;
  background:linear-gradient(180deg,rgba(255,193,73,.035),#100e0c 30%,#0d0c0b 100%)!important;
}
.fc-v1298-complete-hero{
  display:flex;align-items:center;gap:12px;padding:14px 14px;
  border:1px solid rgba(255,198,80,.32);border-radius:15px;
  background:radial-gradient(circle at 12% 10%,rgba(255,200,87,.18),transparent 38%),linear-gradient(135deg,rgba(255,178,46,.08),rgba(255,255,255,.015));
}
.fc-v1298-complete-icon{
  width:46px;height:46px;flex:0 0 46px;border-radius:50%;display:grid;place-items:center;
  background:linear-gradient(135deg,#3b2910,#191009);border:1px solid rgba(255,201,90,.42);
  font-size:24px;box-shadow:0 0 18px rgba(255,190,66,.16);
}
.fc-v1298-complete-copy{min-width:0}
.fc-v1298-complete-copy strong{
  display:block;color:#ffd06a;font-family:var(--font-competition),var(--font-bricolage),sans-serif;
  text-transform:uppercase;letter-spacing:.055em;font-size:18px;line-height:1.05;
}
.fc-v1298-complete-copy span{display:block;margin-top:5px;color:#b8aaa0;font-size:12px;line-height:1.35}
.fc-v1298-winner-summary{
  grid-template-columns:auto auto minmax(0,1fr) auto!important;padding:12px 13px!important;
  border-color:rgba(255,200,87,.40)!important;
  background:linear-gradient(90deg,rgba(255,187,55,.13),rgba(255,92,31,.025))!important;
}
.fc-v1298-winner-medal{font-size:24px;line-height:1}
.fc-v1298-winner-summary .fc-v1196-winner-kicker{white-space:nowrap}
#feedViewerModal #fvStandings .fc-v1298-final-entry-row{
  width:100%;grid-template-columns:30px 34px minmax(0,1fr) auto 18px;min-height:54px;
  margin:0;padding:9px 5px;border:0;border-bottom:1px solid rgba(255,255,255,.075);border-radius:0;
  background:transparent;color:var(--text);font:inherit;text-align:left;cursor:pointer;-webkit-tap-highlight-color:transparent;
}
#feedViewerModal #fvStandings .fc-v1298-final-entry-row:active{background:rgba(255,200,87,.06)}
#feedViewerModal #fvStandings .fc-v1298-final-entry-row:last-of-type{border-bottom:0}
#feedViewerModal #fvStandings .fc-v1298-final-entry-row .avatar{width:34px;height:34px}
#feedViewerModal #fvStandings .fc-v1298-final-entry-row .name{font-size:14px}
#feedViewerModal #fvStandings .fc-v1298-final-entry-row .votes{font-size:12px;white-space:nowrap}
.fc-v1298-result-chevron{font-size:25px;line-height:1;color:#d8b97a;transform:translateY(-1px)}
#feedViewerModal #fvStandings .fc-v1024-final-title{margin-top:4px!important;color:#c7b8ac!important;letter-spacing:.16em!important}
#feedViewerModal #fvChallengeBtn{font-weight:800!important;letter-spacing:.02em!important}
@media(max-width:380px){
  .fc-v1298-winner-summary{grid-template-columns:auto auto 1fr!important}
  .fc-v1298-winner-summary small{grid-column:3!important}
  .fc-v1298-complete-copy strong{font-size:16px}
}
</style>
<script>window.FC_V1298_VALIDATION={build:'v1298',completeStateHero:true,closedJourneyAllDone:true,finalRowsOpenExactEntry:true,losingEntriesRemainAccessible:true,winnerSummaryBeforeMedia:true,closedActionSaysViewFullDetails:true,v1297VideoAndRecordFixesPreserved:true};</script>
""" + marker
one(marker,css,'append v1298 styles')

p.write_text(s,encoding='utf-8')
