#!/usr/bin/env python3
"""Guarded A3.6 v1396 staging-only modal order fix.
Mandatory Guidelines must be acknowledged before optional welcome guide opens.
Never modifies production, database policies, or service worker.
"""
from pathlib import Path
path=Path('index.html')
s=path.read_text(encoding='utf-8')
before='<meta content="v1395 · a36-following-authoritative-rings" name="fc-build"/>'
after='<meta content="v1396 · a36-guidelines-before-welcome-guide" name="fc-build"/>'
old_condition="if (!state?.profile || !profileComplete() || guideSeen()) return;"
new_condition=("if (!state?.profile || !profileComplete() || guideSeen() || "+
               "!guidelinesAcked() || document.getElementById('guidelinesModal')?.classList.contains('open')) return;")
old_timer="optionalTimer = setTimeout(() => { if (state?.profile && !guideSeen()) openGuide(false); }, 900);"
new_timer=("optionalTimer = setTimeout(() => { if (state?.profile && !guideSeen() && guidelinesAcked() && "+
           "!document.getElementById('guidelinesModal')?.classList.contains('open')) openGuide(false); }, 900);")
anchor='window.fcMaybeOpenOptionalGuideV1103 = function(){'
for needle,count in [(before,1),(after,0),(anchor,1),(old_condition,1),(old_timer,1)]:
 actual=s.count(needle)
 if actual != count:
  raise SystemExit(f'STOP: staging source not expected for {needle[:90]!r}; wanted={count} found={actual}')
segment=s[s.index(anchor):s.index(anchor)+500]
if old_condition not in segment or old_timer not in segment:
 raise SystemExit('STOP: optional guide anchors not inside intended function')
s=s.replace(old_condition,new_condition,1).replace(old_timer,new_timer,1).replace(before,after,1)
patched_function=s[s.index(anchor):s.index(anchor)+800]
assert patched_function.count('!guidelinesAcked()')==1
assert patched_function.count('&& guidelinesAcked()')==1
assert s.count(after)==1
path.write_text(s,encoding='utf-8')
print('STAGED v1396: Guidelines acknowledgement gates optional guide before and after timer')
