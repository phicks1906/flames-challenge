from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
old='<meta content="v1286 · approved-scene-audio-restored" name="fc-build"/>'
new='<meta content="v1287 · waveform-style-retired" name="fc-build"/>'
assert s.count(old)==1
s=s.replace(old,new,1)
old2='<meta content="Restored Scene audio to the approved cinematic direction: large Crowned F, fiery landscape, one live reactive waveform, one modern play control, and one time pair while preserving the compact 16:9 player and all other audio styles." name="fc-whatsnew"/>'
new2='<meta content="Retired the redundant Waveform audio style. Existing Waveform/Curve preferences now migrate to Scene, leaving three distinct choices—Scene, Record, and Flame—across Home, winners, Challenge Detail, and entry viewers." name="fc-whatsnew"/>'
assert s.count(old2)==1
s=s.replace(old2,new2,1)
old3="const EQ_STYLES = ['scene', 'vinyl', 'flame', 'waveform'];\nconst EQ_LABELS = { scene: 'Scene', vinyl: 'Record', flame: 'Flame', waveform: 'Waveform' };"
new3="const EQ_STYLES = ['scene', 'vinyl', 'flame'];\nconst EQ_LABELS = { scene: 'Scene', vinyl: 'Record', flame: 'Flame' };"
assert s.count(old3)==1
s=s.replace(old3,new3,1)
old4="    if (v === 'gradient') { localStorage.setItem(EQ_KEY, 'scene'); return 'scene'; }\n    if (v === 'curve') { localStorage.setItem(EQ_KEY, 'waveform'); return 'waveform'; }\n    return EQ_STYLES.includes(v) ? v : 'scene';"
new4="    if (v === 'gradient' || v === 'curve' || v === 'waveform') { localStorage.setItem(EQ_KEY, 'scene'); return 'scene'; }\n    return EQ_STYLES.includes(v) ? v : 'scene';"
assert s.count(old4)==1
s=s.replace(old4,new4,1)
start=s.index("  } else if (style === 'waveform') {")
end=s.index("  } else if (style === 'flame') {", start)
s=s[:start]+"  } else if (style === 'flame') {"+s[end+len("  } else if (style === 'flame') {"):]
marker="<script>window.FC_V1286_VALIDATION={build:'v1286',sceneUsesApprovedCinematicArt:true,noBakedControlsVisible:true,oneLiveWaveform:true,onePlayControl:true,oneTimePair:true,compact169Preserved:true,recordFlameWaveformStylesPreserved:true,v1285ViewerHeightPreserved:true,v1283HallOfFamePreserved:true};</script>"
assert marker in s
insert=marker+"\n<script>window.FC_V1287_VALIDATION={build:'v1287',waveformStyleRetired:true,legacyWaveformMigratesToScene:true,legacyCurveMigratesToScene:true,audioStyles:['scene','vinyl','flame'],scenePreserved:true,recordPreserved:true,flamePreserved:true,resultsUseSelectedRemainingStyle:true,v1286ScenePreserved:true,v1285ViewerHeightPreserved:true};</script>"
s=s.replace(marker,insert,1)
p.write_text(s,encoding='utf-8')
