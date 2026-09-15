from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def one(old,new,label):
    global s
    c=s.count(old)
    if c!=1:
        raise SystemExit(f'{label}: expected 1, found {c}')
    s=s.replace(old,new,1)

one('<meta content="v1299 · closed-results-carousel-restored" name="fc-build"/>',
    '<meta content="v1300 · seamless-audio-handoff-and-stable-viewer-scroll" name="fc-build"/>','build meta')
one('<meta content="Restored post-result entry swiping so completed challenges still let members swipe through every finalist and see exactly who the winner beat." name="fc-whatsnew"/>',
    '<meta content="Removed audio handoff glitches when switching players and stabilized the swipe viewer so its height no longer shifts underneath an active scroll gesture." name="fc-whatsnew"/>','whatsnew')

one("""  if (list._fcHeightRafV1285) {
    try { cancelAnimationFrame(list._fcHeightRafV1285); } catch (_) {}
    list._fcHeightRafV1285 = 0;
  }
  list.style.removeProperty('height');
""","""  if (list._fcHeightRafV1285) {
    try { cancelAnimationFrame(list._fcHeightRafV1285); } catch (_) {}
    list._fcHeightRafV1285 = 0;
  }
  if (list._fcHeightSettleTimerV1300) {
    clearTimeout(list._fcHeightSettleTimerV1300);
    list._fcHeightSettleTimerV1300 = 0;
  }
  if (list._fcHeightScrollEndV1300) {
    try { list.removeEventListener('scrollend', list._fcHeightScrollEndV1300); } catch (_) {}
    list._fcHeightScrollEndV1300 = null;
  }
  if (list._fcHeightTouchStartV1300) {
    try { list.removeEventListener('touchstart', list._fcHeightTouchStartV1300); } catch (_) {}
    list._fcHeightTouchStartV1300 = null;
  }
  if (list._fcHeightTouchEndV1300) {
    try { list.removeEventListener('touchend', list._fcHeightTouchEndV1300); } catch (_) {}
    try { list.removeEventListener('touchcancel', list._fcHeightTouchEndV1300); } catch (_) {}
    list._fcHeightTouchEndV1300 = null;
  }
  list._fcHeightGestureV1300 = false;
  list.style.removeProperty('height');
""",'height reset cleanup')

old_wire="""function fcWireFeedViewerActiveHeightV1285(list = document.getElementById('fvEntries')) {
  if (!list) return;
  fcResetFeedViewerActiveHeightV1285(list);
  const queue = () => {
    if (list._fcHeightRafV1285) return;
    list._fcHeightRafV1285 = requestAnimationFrame(() => {
      list._fcHeightRafV1285 = 0;
      fcSyncFeedViewerActiveHeightV1285(list);
    });
  };
  list._fcHeightScrollV1285 = queue;
  list.addEventListener('scroll', queue, { passive:true });
  if (typeof ResizeObserver === 'function') {
    const ro = new ResizeObserver(queue);
    list.querySelectorAll('.fc-v1024-fv-slide').forEach(slide => ro.observe(slide));
    list._fcHeightROV1285 = ro;
  }
  requestAnimationFrame(queue);
  setTimeout(queue, 80);
  setTimeout(queue, 260);
}
"""
new_wire="""function fcWireFeedViewerActiveHeightV1285(list = document.getElementById('fvEntries')) {
  if (!list) return;
  fcResetFeedViewerActiveHeightV1285(list);

  // v1300 — never resize/reposition the sheet while the member is actively
  // swiping the horizontal entry rail. v1285 synchronized height on every
  // scroll frame, which could change the rail height and re-center the modal
  // underneath the finger. That produced the erratic second-screen swipe seen
  // in the recording. Height now updates only after the native scroll settles.
  const syncNow = () => {
    if (list._fcHeightRafV1285) return;
    list._fcHeightRafV1285 = requestAnimationFrame(() => {
      list._fcHeightRafV1285 = 0;
      if (!list._fcHeightGestureV1300) fcSyncFeedViewerActiveHeightV1285(list);
    });
  };
  const settle = (delay = 120) => {
    if (list._fcHeightSettleTimerV1300) clearTimeout(list._fcHeightSettleTimerV1300);
    list._fcHeightSettleTimerV1300 = setTimeout(() => {
      list._fcHeightSettleTimerV1300 = 0;
      syncNow();
    }, delay);
  };
  const onScroll = () => settle(140);
  const onScrollEnd = () => settle(0);
  const onTouchStart = () => {
    list._fcHeightGestureV1300 = true;
    if (list._fcHeightSettleTimerV1300) {
      clearTimeout(list._fcHeightSettleTimerV1300);
      list._fcHeightSettleTimerV1300 = 0;
    }
  };
  const onTouchEnd = () => {
    list._fcHeightGestureV1300 = false;
    settle(70);
  };

  list._fcHeightScrollV1285 = onScroll;
  list._fcHeightScrollEndV1300 = onScrollEnd;
  list._fcHeightTouchStartV1300 = onTouchStart;
  list._fcHeightTouchEndV1300 = onTouchEnd;
  list.addEventListener('scroll', onScroll, { passive:true });
  list.addEventListener('scrollend', onScrollEnd, { passive:true });
  list.addEventListener('touchstart', onTouchStart, { passive:true });
  list.addEventListener('touchend', onTouchEnd, { passive:true });
  list.addEventListener('touchcancel', onTouchEnd, { passive:true });

  if (typeof ResizeObserver === 'function') {
    const ro = new ResizeObserver(() => list._fcHeightGestureV1300 ? settle(140) : settle(40));
    list.querySelectorAll('.fc-v1024-fv-slide').forEach(slide => ro.observe(slide));
    list._fcHeightROV1285 = ro;
  }
  requestAnimationFrame(syncNow);
  setTimeout(syncNow, 90);
  setTimeout(syncNow, 280);
}
"""
one(old_wire,new_wire,'stable active-height wire')

one("""const _fcAudioControlFadeTimersV1172 = new WeakMap();
""","""const _fcAudioControlFadeTimersV1172 = new WeakMap();
// v1300 — authoritative pointer to the one deliberate audible media element.
// Avoid scanning/pausing every audio+video node on each play tap; that work was
// large enough on iOS to make player-to-player handoff stutter.
let _fcActiveAudibleMediaV1300 = null;
""",'active media pointer')

one("""function fcAudioPlayStateV1123(tile, audio) {
  if (!tile || !audio) return;
  tile.classList.add('playing');
""","""function fcAudioPlayStateV1123(tile, audio) {
  if (!tile || !audio) return;
  _fcActiveAudibleMediaV1300 = audio;
  _userAudioActive = true;
  tile.classList.add('playing');
""",'audio play state')

one("""function fcAudioPauseStateV1123(tile, audio) {
  if (!tile || !audio) return;
  tile.classList.remove('playing');
""","""function fcAudioPauseStateV1123(tile, audio) {
  if (!tile || !audio) return;
  if (_fcActiveAudibleMediaV1300 === audio) {
    _fcActiveAudibleMediaV1300 = null;
    _userAudioActive = false;
  }
  tile.classList.remove('playing');
""",'audio pause state')

one("""function toggleFccAudio(tile, ev) {
  if (ev) { ev.preventDefault(); ev.stopPropagation(); }
  showFccAudioControlV1172(tile, 1250);
  const audio = tile?.querySelector('audio');
  if (!audio) return;
  if (audio.paused) {
    _userAudioActive = true;
    document.querySelectorAll('audio,video').forEach(media => { if (media !== audio) { try { media.pause(); } catch (_) {} } });
    audio.play().catch(error => {
      fcAudioPauseStateV1123(tile, audio);
      toast('Audio could not start. Tap again.');
      dlog('audio', 'play-failed', { error: String(error?.message || error).slice(0,80) });
    });
  } else {
    audio.pause();
  }
}
""","""function toggleFccAudio(tile, ev) {
  if (ev) { ev.preventDefault(); ev.stopPropagation(); }
  showFccAudioControlV1172(tile, 1250);
  const audio = tile?.querySelector('audio');
  if (!audio) return;
  if (audio.paused) {
    // v1300 — prepare any analyser graph before playback begins. Creating a
    // MediaElementSource from the onplay callback rerouted the element after its
    // first samples had already started and could produce a brief skip on iOS.
    // Record/vinyl has no analyser at all, so it stays on the native media path.
    fcPrimeFccAudioGraphV1300(tile, audio);

    const prior = _fcActiveAudibleMediaV1300;
    if (prior && prior !== audio && !prior.paused) {
      try { prior.pause(); } catch (_) {}
    }
    _fcActiveAudibleMediaV1300 = audio;
    _userAudioActive = true;
    audio.play().catch(error => {
      if (_fcActiveAudibleMediaV1300 === audio) _fcActiveAudibleMediaV1300 = null;
      _userAudioActive = false;
      fcAudioPauseStateV1123(tile, audio);
      toast('Audio could not start. Tap again.');
      dlog('audio', 'play-failed', { error: String(error?.message || error).slice(0,80) });
    });
  } else {
    audio.pause();
  }
}
""",'audio toggle handoff')

old_start="""let _feqCtx = null;
function _feqStart(tile, a) {
  try {
    if (!_feqCtx) _feqCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (_feqCtx.state === 'suspended') _feqCtx.resume();
    if (!a._feqSrc) {
      a._feqSrc = _feqCtx.createMediaElementSource(a);
      a._feqAn = _feqCtx.createAnalyser();
      a._feqAn.fftSize = 256;
      a._feqSrc.connect(a._feqAn);
      a._feqAn.connect(_feqCtx.destination);
    }
    const an = a._feqAn;
"""
new_start="""let _feqCtx = null;
function fcPrimeFccAudioGraphV1300(tile, a) {
  if (!tile || !a) return false;
  // Record/vinyl animation is pure CSS. Routing it through WebAudio served no
  // visual purpose and was the main source of iOS handoff artifacts.
  if (tile.classList.contains('eq-vinyl')) return false;
  try {
    if (!_feqCtx) _feqCtx = new (window.AudioContext || window.webkitAudioContext)();
    if (_feqCtx.state === 'suspended') {
      const resume = _feqCtx.resume();
      if (resume?.catch) resume.catch(() => {});
    }
    if (!a._feqSrc) {
      a._feqSrc = _feqCtx.createMediaElementSource(a);
      a._feqAn = _feqCtx.createAnalyser();
      a._feqAn.fftSize = 256;
      a._feqSrc.connect(a._feqAn);
      a._feqAn.connect(_feqCtx.destination);
    }
    return !!a._feqAn;
  } catch (err) {
    dlog('feq', 'prime-fail', { e: String(err && err.message || err).slice(0, 60) });
    return false;
  }
}
function _feqStart(tile, a) {
  try {
    if (tile.classList.contains('eq-vinyl')) return;
    if (!fcPrimeFccAudioGraphV1300(tile, a)) {
      tile.classList.add('feq-fallback');
      return;
    }
    const an = a._feqAn;
"""
one(old_start,new_start,'prime analyser before play')

old_single="""(function wireSinglePlayback() {
  if (window._singlePlayWired) return;
  window._singlePlayWired = true;
  document.addEventListener('play', function (e) {
    const el = e.target;
    if (!(el instanceof HTMLMediaElement) || el.muted) return;
    document.querySelectorAll('audio, video').forEach(m => {
      if (m !== el && !m.muted && !m.paused) {
        try { m.pause(); } catch (_) {}
      }
    });
  }, true);
})();
"""
new_single="""(function wireSinglePlayback() {
  if (window._singlePlayWired) return;
  window._singlePlayWired = true;
  document.addEventListener('play', function (e) {
    const el = e.target;
    if (!(el instanceof HTMLMediaElement) || el.muted) return;
    const prior = _fcActiveAudibleMediaV1300;
    if (prior && prior !== el && !prior.paused) {
      try { prior.pause(); } catch (_) {}
    }
    _fcActiveAudibleMediaV1300 = el;
  }, true);
  const clear = function (e) {
    const el = e.target;
    if (el instanceof HTMLMediaElement && _fcActiveAudibleMediaV1300 === el) {
      _fcActiveAudibleMediaV1300 = null;
      if (el.tagName === 'AUDIO') _userAudioActive = false;
    }
  };
  document.addEventListener('pause', clear, true);
  document.addEventListener('ended', clear, true);
})();
"""
one(old_single,new_single,'single playback pointer')

marker='<script>window.FC_V1299_VALIDATION={build:\'v1299\',closedResultKeepsEntryCarousel:true,finalSummaryBeforeEntryRail:true,allFinalistsSwipeableAfterResult:true,closedCounterAndDotsRestored:true,noDuplicateWinnerMedia:true,v1298ResultClarityPreserved:true};</script>'
insert="""<style id="fc-v1300-stable-viewer-audio-css">
/* v1300 — keep native swipe physics; geometry is committed only after settle. */
#feedViewerModal #fvEntries{
  overscroll-behavior-x:contain!important;
  scroll-behavior:auto!important;
}
#feedViewerModal #fvEntries>.fc-v1024-fv-slide{
  scroll-snap-align:center!important;
}
</style>
<script>window.FC_V1300_VALIDATION={build:'v1300',singleAudibleMediaPointer:true,recordAudioBypassesWebAudio:true,analyserPrimedBeforePlay:true,viewerHeightDefersUntilScrollSettles:true,noSheetRepositionDuringSwipe:true,v1299ClosedCarouselPreserved:true};</script>
"""+marker
one(marker,insert,'append v1300 validation')

p.write_text(s,encoding='utf-8')
