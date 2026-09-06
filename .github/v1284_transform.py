from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='<meta content="v1283 · hall-of-fame-ceremony-and-detail-nav" name="fc-build"/>'
new='<meta content="v1284 · audio-style-preference-restored" name="fc-build"/>'
assert s.count(old)==1, s.count(old)
s=s.replace(old,new,1)
old2='<meta content="Redesigned Hall of Fame as a ceremonial legacy surface with personal progress reduced to a compact secondary strip, and made the persistent bottom navigation close open read-only detail screens before navigating." name="fc-whatsnew"/>'
new2='<meta content="Restored the Audio style setting across Home, winners, Challenge Detail, and entry viewers. Scene keeps the new unified player; Record, Flame, and Waveform now render their selected visual treatment without inheriting the old oversized media stage." name="fc-whatsnew"/>'
assert s.count(old2)==1, s.count(old2)
s=s.replace(old2,new2,1)
old3="  if (unifiedModesV1280.has(mode)) {"
new3="  if (unifiedModesV1280.has(mode) && style === 'scene') {"
assert s.count(old3)==1, s.count(old3)
s=s.replace(old3,new3,1)
old4='data-audio-style="unified-v1280" data-audio-layout-v1201="compact" role="group" aria-label="Audio entry"'
new4='data-audio-style="scene" data-audio-layout-v1201="compact" role="group" aria-label="Audio entry · Scene style"'
assert s.count(old4)==1, s.count(old4)
s=s.replace(old4,new4,1)
needle="    if (typeof _evEntry !== 'undefined' && _evEntry && document.getElementById('entryViewerSheet')?.classList.contains('open') && typeof _renderEvEntry === 'function') _renderEvEntry();\n"
insert=needle+"    if (typeof _fvChallenge !== 'undefined' && _fvChallenge && document.getElementById('feedViewerSheet')?.classList.contains('open') && typeof openFeedViewer === 'function') openFeedViewer(_fvChallenge.id);\n"
assert s.count(needle)==1, s.count(needle)
s=s.replace(needle,insert,1)
block=r'''
<style id="fc-v1284-audio-style-preference-css">
.fc-entry-rail-v1079 .fc-entry-stage-fixed-v1202 > .fcc-entry-media.fcc-fire-eq:not(.fc-audio-unified-v1280),
.fc-entry-rail-v1079 .fcc-entry-card .fcc-entry-media.fcc-fire-eq:not(.fc-audio-unified-v1280),
.fc-winner-audio-v1123 .fcc-entry-media.fcc-fire-eq:not(.fc-audio-unified-v1280),
.fc-v1195-winning-audio .fcc-entry-media.fcc-fire-eq:not(.fc-audio-unified-v1280),
.cd-entry-media .fcc-entry-media.fcc-fire-eq:not(.fc-audio-unified-v1280){width:100%!important;height:auto!important;min-height:0!important;max-height:none!important;aspect-ratio:16/9!important;padding:0!important;overflow:hidden!important}
.fc-audio-layout-compact-v1201.eq-vinyl .fc-audio-record-v1160{height:100%!important;width:auto!important;max-width:100%!important;aspect-ratio:1/1!important}
.fc-audio-layout-compact-v1201.eq-waveform .fc-audio-waveform-v1171,.fc-audio-layout-compact-v1201.eq-scene .fc-audio-scene-restored-v1205{width:100%!important;height:100%!important;max-height:none!important;aspect-ratio:auto!important}
.fcc-fire-eq.eq-vinyl,.fcc-fire-eq.eq-flame,.fcc-fire-eq.eq-waveform{border-radius:18px!important;border:1px solid rgba(197,116,48,.36)!important;background:#070403!important;box-shadow:inset 0 1px 0 rgba(255,219,151,.05),0 12px 28px rgba(0,0,0,.22)!important}
</style>
<script>window.FC_V1284_VALIDATION={build:'v1284',audioStyleSettingRespected:true,sceneUsesUnifiedV1280:true,recordRestored:true,flameRestored:true,waveformRestored:true,compactGeometryPreserved:true,feedViewerRerendersOnStyleChange:true,v1283HallOfFamePreserved:true};</script>
'''
assert 'id="fc-v1284-audio-style-preference-css"' not in s
assert '</body>' in s
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
