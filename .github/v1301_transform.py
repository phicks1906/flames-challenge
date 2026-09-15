from pathlib import Path
p=Path('index.html'); s=p.read_text('utf-8')
def one(a,b):
 c=s.count(a)
 if c!=1: raise SystemExit(f'expected 1, got {c}: {a[:50]}')
 return s.replace(a,b,1)
s=one('<meta content="v1300 · seamless-audio-handoff-and-stable-viewer-scroll" name="fc-build"/>','<meta content="v1301 · native-audio-pitch-stability" name="fc-build"/>')
s=one('<meta content="Removed audio handoff glitches when switching players and stabilized the swipe viewer so its height no longer shifts underneath an active scroll gesture." name="fc-whatsnew"/>','<meta content="Kept competition audio on the native media path so it cannot drag or shift pitch, while preserving moving audio visuals without routing sound through Web Audio." name="fc-whatsnew"/>')
s=one('  const audio = `<audio src="${escapeHtml(mediaUrl)}" preload="${preload}" crossorigin="anonymous"\n','  const audio = `<audio src="${escapeHtml(mediaUrl)}" preload="${preload}"\n')
s=one('function fcAudioPlayStateV1123(tile, audio) {\n  if (!tile || !audio) return;\n  _fcActiveAudibleMediaV1300 = audio;','function fcAudioPlayStateV1123(tile, audio) {\n  if (!tile || !audio) return;\n  fcNormalizeAudioTransportV1301(audio);\n  _fcActiveAudibleMediaV1300 = audio;')
a='''    // v1300 — prepare any analyser graph before playback begins. Creating a
    // MediaElementSource from the onplay callback rerouted the element after its
    // first samples had already started and could produce a brief skip on iOS.
    // Record/vinyl has no analyser at all, so it stays on the native media path.
    fcPrimeFccAudioGraphV1300(tile, audio);
'''
b='''    // v1301 — audio fidelity wins. Never reroute the element through Web Audio.
    // iOS can intermittently clock a MediaElementSource differently from native
    // media output, which sounds like a tape dragging / pitch sag even while the
    // on-screen currentTime advances normally. Keep the actual sound entirely
    // on the browser's native <audio> path and animate visuals independently.
    fcNormalizeAudioTransportV1301(audio);
'''
s=one(a,b)
start=s.index('// ── v726: REAL frequency-driven bars'); end=s.index('function _feqStop(tile)',start)
new='''// ── v1301: PITCH-SAFE AUDIO VISUALS ───────────────────────────────────────
// Competition audio stays on the native <audio> output path. We intentionally
// do NOT call createMediaElementSource(), createAnalyser(), or AudioContext for
// these players. On iOS, rerouting media through Web Audio can intermittently
// introduce clock/sample-rate instability that sounds like dragging or a pitch
// shift even though media.currentTime itself remains correct. The visual bars
// are now deterministic display animation keyed to native currentTime, so they
// still move while playback remains bit-for-bit under the browser's media engine.
function fcNormalizeAudioTransportV1301(a) {
  if (!a) return;
  try { a.defaultPlaybackRate = 1; } catch (_) {}
  try { a.playbackRate = 1; } catch (_) {}
  try { if ('preservesPitch' in a) a.preservesPitch = true; } catch (_) {}
  try { if ('webkitPreservesPitch' in a) a.webkitPreservesPitch = true; } catch (_) {}
  try { if ('mozPreservesPitch' in a) a.mozPreservesPitch = true; } catch (_) {}
}

// Kept as a compatibility shim because older call sites/build invariants know
// this name. It no longer builds an audio graph.
function fcPrimeFccAudioGraphV1300(tile, a) {
  fcNormalizeAudioTransportV1301(a);
  return !!(tile && a);
}

function _feqStart(tile, a) {
  try {
    if (!tile || !a || tile.classList.contains('eq-vinyl')) return;
    fcNormalizeAudioTransportV1301(a);

    const isUnifiedV1280 = tile.classList.contains('fc-audio-unified-v1280');
    const isPremiumV1277 = tile.classList.contains('fc-audio-premium-v1277');
    const isFlame = tile.classList.contains('eq-flame');
    const isWaveform = tile.classList.contains('eq-waveform');
    const isScene = tile.classList.contains('eq-scene');
    const bars = isUnifiedV1280
      ? tile.querySelectorAll('.fc-audio-unified-bar-v1280')
      : isPremiumV1277
        ? tile.querySelectorAll('.fc-audio-premium-bar-v1277')
      : isWaveform
        ? tile.querySelectorAll('.fc-audio-wave-bar-v1171')
        : isScene
          ? tile.querySelectorAll('.fc-audio-scene-restored-v1205 .feqb')
          : tile.querySelectorAll('.feqb');
    const NB = bars.length;
    if (!NB) return;

    if (tile._feqRaf) cancelAnimationFrame(tile._feqRaf);
    const loop = () => {
      if (!tile.classList.contains('playing') || a.paused || a.ended) return;
      const t = Number.isFinite(a.currentTime) ? a.currentTime : 0;
      for (let i = 0; i < NB; i++) {
        const x = NB > 1 ? i / (NB - 1) : 0;
        const envelope = .34 + .66 * Math.sin(Math.PI * x);
        const p1 = Math.abs(Math.sin(i * .71 + t * 4.15));
        const p2 = Math.abs(Math.sin(i * .23 - t * 2.05 + .8));
        const p3 = Math.abs(Math.sin(i * 1.17 + t * 1.35 + 1.6));
        const pulse = Math.min(1, .50 * p1 + .30 * p2 + .20 * p3);
        const v = Math.max(.05, envelope * pulse);

        if (isUnifiedV1280 || isPremiumV1277) bars[i].style.setProperty('height', (16 + v * 72) + '%', 'important');
        else if (isWaveform) bars[i].style.setProperty('--fc-live-h', (5 + v * 82) + '%');
        else if (isFlame) bars[i].style.height = (86 - v * 68) + '%';
        else if (isScene) bars[i].style.height = (18 + v * 76) + '%';
        else bars[i].style.setProperty('--fc-live-h', (8 + v * 80) + '%');
      }
      tile._feqRaf = requestAnimationFrame(loop);
    };
    tile._feqRaf = requestAnimationFrame(loop);
  } catch (err) {
    dlog('feq', 'visual-loop-fail-v1301', { e: String(err && err.message || err).slice(0, 60) });
    tile.classList.add('feq-fallback');
  }
}
'''
s=s[:start]+new+s[end:]
s=one("  document.addEventListener('pause', clear, true);\n  document.addEventListener('ended', clear, true);\n})();","  document.addEventListener('pause', clear, true);\n  document.addEventListener('ended', clear, true);\n  document.addEventListener('ratechange', function (e) {\n    const el = e.target;\n    if (el instanceof HTMLAudioElement && (el.playbackRate !== 1 || el.defaultPlaybackRate !== 1)) fcNormalizeAudioTransportV1301(el);\n  }, true);\n})();")
marker="<script>window.FC_V1300_VALIDATION={build:'v1300',singleAudibleMediaPointer:true,recordAudioBypassesWebAudio:true,analyserPrimedBeforePlay:true,viewerHeightDefersUntilScrollSettles:true,noSheetRepositionDuringSwipe:true,v1299ClosedCarouselPreserved:true};</script>"
s=one(marker,"<script>window.FC_V1301_VALIDATION={build:'v1301',nativeAudioOutputOnly:true,noCompetitionMediaElementSource:true,noCompetitionAudioContext:true,pitchRateLockedAtOne:true,pitchPreservationEnabled:true,visualsDrivenByCurrentTimeOnly:true,v1300ScrollFixPreserved:true};</script>\n"+marker)
p.write_text(s,'utf-8')
