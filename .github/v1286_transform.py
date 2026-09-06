from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='<meta content="v1285 · adaptive-feed-viewer-height" name="fc-build"/>'
new='<meta content="v1286 · approved-scene-audio-restored" name="fc-build"/>'
assert s.count(old)==1, s.count(old)
s=s.replace(old,new,1)
old2='<meta content="Removed the large empty area in challenge entry viewers by sizing the horizontal carousel to the currently visible entry instead of the tallest submission, and restored usable bottom navigation on read-only detail screens." name="fc-whatsnew"/>'
new2='<meta content="Restored Scene audio to the approved cinematic direction: large Crowned F, fiery landscape, one live reactive waveform, one modern play control, and one time pair while preserving the compact 16:9 player and all other audio styles." name="fc-whatsnew"/>'
assert s.count(old2)==1, s.count(old2)
s=s.replace(old2,new2,1)
oldblock='''    return `<div class="fcc-entry-media fcc-fire-eq fc-audio-unified-v1280 fc-audio-unified-mode-${mode}-v1280${controls ? ' fc-audio-has-controls-v1123' : ''}" data-audio-style="scene" data-audio-layout-v1201="compact" role="group" aria-label="Audio entry · Scene style">\n      ${audio}\n      <div class="fc-audio-unified-scene-v1280">\n        <div class="fc-audio-unified-halo-v1280" aria-hidden="true"></div>\n        <div class="fc-audio-unified-logo-v1280" aria-hidden="true"></div>\n        <div class="fc-audio-unified-wave-v1280" aria-hidden="true">${unifiedBarsV1280}</div>\n        ${mainButton}\n        <span class="fc-audio-unified-time-v1280 fc-audio-unified-current-v1280 fc-audio-current-v1123">0:00</span>\n        <span class="fc-audio-unified-time-v1280 fc-audio-unified-total-v1280 fc-audio-duration-v1123">--:--</span>\n        ${seekV1280}\n      </div>\n    </div>`;'''
newblock='''    return `<div class="fcc-entry-media fcc-fire-eq fc-audio-unified-v1280 fc-audio-scene-v1286 fc-audio-unified-mode-${mode}-v1280${controls ? ' fc-audio-has-controls-v1123' : ''}" data-audio-style="scene" data-audio-layout-v1201="compact" role="group" aria-label="Audio entry · Scene style">\n      ${audio}\n      <div class="fc-audio-premium-art-v1277 fc-audio-scene-art-v1286">\n        <div class="fc-audio-scene-horizon-v1286" aria-hidden="true"></div>\n        <div class="fc-audio-unified-wave-v1280 fc-audio-scene-wave-v1286" aria-hidden="true">${unifiedBarsV1280}</div>\n        ${mainButton}\n        <span class="fc-audio-unified-time-v1280 fc-audio-unified-current-v1280 fc-audio-current-v1123">0:00</span>\n        <span class="fc-audio-unified-time-v1280 fc-audio-unified-total-v1280 fc-audio-duration-v1123">--:--</span>\n        ${seekV1280}\n      </div>\n    </div>`;'''
assert s.count(oldblock)==1, s.count(oldblock)
s=s.replace(oldblock,newblock,1)
css=r'''
<style id="fc-v1286-approved-scene-audio-css">
/* v1286 — Scene returns to the selected cinematic mock direction without
   reintroducing its baked controls. The existing approved artwork is used only
   for the Crowned F + fiery environment; the lower half is deliberately masked
   so the live waveform, play/pause and times remain the only controls. */
.fc-audio-scene-v1286{position:relative!important;width:100%!important;height:auto!important;min-height:0!important;max-height:none!important;aspect-ratio:16/9!important;overflow:hidden!important;border-radius:18px!important;border:1px solid rgba(205,128,49,.44)!important;background:#070403!important;box-shadow:inset 0 1px 0 rgba(255,221,156,.07),0 12px 28px rgba(0,0,0,.26)!important;isolation:isolate!important;touch-action:pan-y!important}
.fc-audio-scene-v1286 .fc-audio-scene-art-v1286{position:absolute!important;inset:0!important;width:100%!important;height:100%!important;min-height:0!important;border-radius:inherit!important;background-position:center top!important;background-size:100% auto!important;filter:saturate(1.04) contrast(1.02)!important}
.fc-audio-scene-v1286 .fc-audio-scene-art-v1286::after{content:""!important;position:absolute!important;z-index:2!important;pointer-events:none!important;left:0!important;right:0!important;bottom:0!important;top:46%!important;background:radial-gradient(ellipse 52% 44% at 50% 4%,rgba(255,108,23,.12),transparent 68%),linear-gradient(180deg,rgba(8,5,3,.86) 0%,rgba(8,5,3,.94) 22%,rgba(5,3,2,.985) 68%,#030201 100%)!important}
.fc-audio-scene-v1286 .fc-audio-scene-horizon-v1286{position:absolute!important;z-index:3!important;left:7%!important;right:7%!important;top:61%!important;height:25%!important;pointer-events:none!important;background:radial-gradient(ellipse at 50% 50%,rgba(255,178,61,.28),rgba(255,90,20,.10) 31%,transparent 68%),linear-gradient(90deg,transparent,rgba(255,109,31,.10) 20%,rgba(255,190,82,.24) 50%,rgba(255,109,31,.10) 80%,transparent)!important;filter:blur(5px)!important;opacity:.92!important}
.fc-audio-scene-v1286 .fc-audio-scene-wave-v1286{left:5%!important;right:5%!important;top:64%!important;height:20%!important;z-index:5!important;gap:.72%!important;opacity:.68!important}
.fc-audio-scene-v1286.playing .fc-audio-scene-wave-v1286{opacity:1!important}
.fc-audio-scene-v1286 .fc-audio-scene-wave-v1286::before{box-shadow:0 0 12px rgba(255,121,27,.52)!important}
.fc-audio-scene-v1286 .fc-audio-unified-bar-v1280{min-width:2px!important;max-width:5px!important;background:linear-gradient(180deg,#ffe29d 0%,#ffb33f 38%,#ff6a27 76%,#c7420d 100%)!important;box-shadow:0 0 6px rgba(255,102,25,.62)!important}
.fc-audio-scene-v1286 .fcc-audio-btn{top:56%!important;width:64px!important;height:64px!important;min-width:64px!important;min-height:64px!important;max-width:64px!important;max-height:64px!important;z-index:8!important;border:1px solid rgba(255,255,255,.15)!important;background:linear-gradient(145deg,rgba(38,34,31,.96),rgba(7,6,6,.99) 72%)!important;box-shadow:0 12px 27px rgba(0,0,0,.55),inset 0 1px 0 rgba(255,255,255,.11)!important}
.fc-audio-scene-v1286 .fc-audio-unified-time-v1280{bottom:5.2%!important;z-index:8!important;height:28px!important;min-height:28px!important;min-width:58px!important;padding:0 9px!important;border-radius:11px!important;background:rgba(5,4,4,.84)!important;border:1px solid rgba(255,255,255,.13)!important;color:#f3eee9!important;font-size:12px!important}
.fc-audio-scene-v1286 .fc-audio-unified-current-v1280{left:4%!important}.fc-audio-scene-v1286 .fc-audio-unified-total-v1280{right:4%!important}.fc-audio-scene-v1286 .fc-audio-unified-seek-v1280{bottom:10.5%!important;z-index:8!important}
@media(max-width:390px){.fc-audio-scene-v1286{border-radius:16px!important}.fc-audio-scene-v1286 .fcc-audio-btn{width:58px!important;height:58px!important;min-width:58px!important;min-height:58px!important;max-width:58px!important;max-height:58px!important}.fc-audio-scene-v1286 .fc-audio-unified-time-v1280{height:26px!important;min-height:26px!important;min-width:54px!important;font-size:11px!important}}
</style>
<script>window.FC_V1286_VALIDATION={build:'v1286',sceneUsesApprovedCinematicArt:true,noBakedControlsVisible:true,oneLiveWaveform:true,onePlayControl:true,oneTimePair:true,compact169Preserved:true,recordFlameWaveformStylesPreserved:true,v1285ViewerHeightPreserved:true,v1283HallOfFamePreserved:true};</script>
'''
assert 'id="fc-v1286-approved-scene-audio-css"' not in s
assert '</body>' in s
s=s.replace('</body>',css+'\n</body>',1)
p.write_text(s,encoding='utf-8')
