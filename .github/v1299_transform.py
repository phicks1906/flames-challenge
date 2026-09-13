from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def one(old,new,label):
    global s
    c=s.count(old)
    if c!=1:
        raise SystemExit(f'{label}: expected 1, found {c}')
    s=s.replace(old,new,1)

one('<meta content="v1298 · unmistakable-final-results-and-entry-access" name="fc-build"/>','<meta content="v1299 · closed-results-carousel-restored" name="fc-build"/>','build meta')
one('<meta content="Made finished challenges unmistakably complete and made every competitor in Final Results tappable so members can open the exact winning or losing entry after voting ends." name="fc-whatsnew"/>','<meta content="Restored post-result entry swiping so completed challenges still let members swipe through every finalist and see exactly who the winner beat." name="fc-whatsnew"/>','whatsnew')

one("""    if (viewerModeV1193 === 'results') {
      fcResetFeedViewerActiveHeightV1285(list);
      // Closed challenges lead with the winner and final standings. The entry
      // carousel remains available through View Details, but is not rendered as
      // a large obsolete stage above the result.
      list.innerHTML = '';
      list.style.display = 'none';
      empty.style.display = 'none';
      if (counterV1193) {
        counterV1193.textContent = '';
        counterV1193.style.display = 'none';
      }
      if (dotsV1193) {
        dotsV1193.innerHTML = '';
        dotsV1193.style.display = 'none';
      }
      if (scrollRegionV1193) scrollRegionV1193.dataset.viewerModeV1193 = 'results';
      renderFvStandings(chId, _validVotesV1047, _eligibleVisibleV1047);
    } else {
""","""    if (viewerModeV1193 === 'results') {
      // v1299 — A settled result must not erase the matchup. Keep the final
      // result summary first, but restore the same horizontal entry rail used
      // before the winner is decided so members can swipe through every final
      // competitor and see exactly who the winner beat.
      list.style.display = 'flex';
      list.innerHTML = _eligibleVisibleV1047.map(e => renderFvEntry(e, ch, false, myVoteEntryId, status)).join('');
      fcWireFeedViewerActiveHeightV1285(list);
      _checkFreshVideoEncoding(list);
      empty.style.display = 'none';
      if (counterV1193) counterV1193.style.display = '';
      if (dotsV1193) dotsV1193.style.display = '';
      if (scrollRegionV1193) scrollRegionV1193.dataset.viewerModeV1193 = 'results';
      renderFvStandings(chId, _validVotesV1047, _eligibleVisibleV1047);
    } else {
""",'results branch')

one("""    // Dots + counter belong only to entry/voting modes.
    const counter = document.getElementById('fvCounter');
    const dotsEl  = document.getElementById('fvDots');
    if (viewerModeV1193 !== 'results') {
      if (counter) counter.textContent = total > 1 ? `1 of ${total}` : '';
      if (dotsEl) {
        dotsEl.innerHTML = total > 1
          ? _eligibleVisibleV1047.map((_, i) => `<span style="width:7px;height:7px;border-radius:50%;background:${i===0?'var(--ember)':'var(--border-bright)'};transition:background 0.2s,transform 0.2s;display:inline-block;${i===0?'transform:scale(1.3)':''}"></span>`).join('')
          : '';
        list.addEventListener('scroll', () => {
          const idx = Math.round(list.scrollLeft / list.offsetWidth);
          if (counter) counter.textContent = total > 1 ? `${idx+1} of ${total}` : '';
          if (dotsEl) dotsEl.querySelectorAll('span').forEach((d,i) => {
            d.style.background = i===idx ? 'var(--ember)' : 'var(--border-bright)';
            d.style.transform  = i===idx ? 'scale(1.3)' : 'scale(1)';
          });
        }, { passive: true });
      }
    }
""","""    // v1299 — The counter/dots stay active after the challenge closes too.
    // A winner is a result state, not the end of entry browsing.
    const counter = document.getElementById('fvCounter');
    const dotsEl  = document.getElementById('fvDots');
    if (list.style.display !== 'none') {
      if (counter) counter.textContent = total > 1 ? `Entry 1 of ${total}` : '';
      if (dotsEl) {
        dotsEl.innerHTML = total > 1
          ? _eligibleVisibleV1047.map((_, i) => `<span style="width:7px;height:7px;border-radius:50%;background:${i===0?'var(--ember)':'var(--border-bright)'};transition:background 0.2s,transform 0.2s;display:inline-block;${i===0?'transform:scale(1.3)':''}"></span>`).join('')
          : '';
        list.addEventListener('scroll', () => {
          const idx = Math.round(list.scrollLeft / list.offsetWidth);
          if (counter) counter.textContent = total > 1 ? `Entry ${idx+1} of ${total}` : '';
          if (dotsEl) dotsEl.querySelectorAll('span').forEach((d,i) => {
            d.style.background = i===idx ? 'var(--ember)' : 'var(--border-bright)';
            d.style.transform  = i===idx ? 'scale(1.3)' : 'scale(1)';
          });
        }, { passive: true });
      }
    }
""",'counter and dots')

one("""  panel.innerHTML = `<div class="fc-v1024-final-standings fc-v1298-final-standings">
    ${completeHeroV1298}
    ${winnerHtmlV1203}
    ${winningMediaHtmlV1203}
    <div class="fc-v1024-final-title">${status === 'closed' ? 'Final results' : 'Live standings'}</div>
""","""  panel.innerHTML = `<div class="fc-v1024-final-standings fc-v1298-final-standings">
    ${completeHeroV1298}
    ${winnerHtmlV1203}
    ${status === 'closed' ? '' : winningMediaHtmlV1203}
    <div class="fc-v1024-final-title">${status === 'closed' ? 'Final results' : 'Live standings'}</div>
""",'avoid duplicate winner media')

marker="<script>window.FC_V1298_VALIDATION={build:'v1298',completeStateHero:true,closedJourneyAllDone:true,finalRowsOpenExactEntry:true,losingEntriesRemainAccessible:true,winnerSummaryBeforeMedia:true,closedActionSaysViewFullDetails:true,v1297VideoAndRecordFixesPreserved:true};</script>"
insert="""<style id="fc-v1299-closed-carousel-css">
/* v1299 — completed challenge = compact result summary + preserved matchup rail. */
#feedViewerModal #fvScrollRegion[data-viewer-mode-v1193="results"]{display:flex!important;flex-direction:column!important}
#feedViewerModal #fvScrollRegion[data-viewer-mode-v1193="results"] #fvStandings{order:1!important;padding-top:12px!important;padding-bottom:6px!important}
#feedViewerModal #fvScrollRegion[data-viewer-mode-v1193="results"] > div:first-child{order:2!important;margin:0 16px 12px!important;border:1px solid rgba(255,196,76,.18)!important;border-radius:16px!important;overflow:hidden!important;background:rgba(255,255,255,.012)!important}
#feedViewerModal #fvScrollRegion[data-viewer-mode-v1193="results"] > div:first-child::before{content:'MATCHUP ENTRIES · SWIPE TO REVIEW';display:block;padding:11px 13px 8px;color:#c9b9ad;font-size:10px;font-weight:800;letter-spacing:.12em;border-bottom:1px solid rgba(255,255,255,.055)}
#feedViewerModal #fvScrollRegion[data-viewer-mode-v1193="results"] #fvEntries{border-radius:0!important}
#feedViewerModal #fvScrollRegion[data-viewer-mode-v1193="results"] #fvCounter{padding:8px 0 5px!important;color:#d8b97a!important}
#feedViewerModal #fvScrollRegion[data-viewer-mode-v1193="results"] #fvDots{display:flex!important;justify-content:center!important;gap:6px!important;padding:0 0 10px!important}
#feedViewerModal #fvScrollRegion[data-viewer-mode-v1193="results"] #fvEmpty{order:3!important}
</style>
<script>window.FC_V1299_VALIDATION={build:'v1299',closedResultKeepsEntryCarousel:true,finalSummaryBeforeEntryRail:true,allFinalistsSwipeableAfterResult:true,closedCounterAndDotsRestored:true,noDuplicateWinnerMedia:true,v1298ResultClarityPreserved:true};</script>
"""+marker
one(marker,insert,'v1299 styles')

p.write_text(s,encoding='utf-8')
