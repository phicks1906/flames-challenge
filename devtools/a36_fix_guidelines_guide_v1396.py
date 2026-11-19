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
old="""window.fcMaybeOpenOptionalGuideV1103 = function(){
  clearTimeout(optionalTimer);
  if (!state?.profile || !profileComplete() || guideSeen()) return;
  optionalTimer = setTimeout(() => { if (state?.profile && !guideSeen()) openGuide(false); }, 900);
};"""
new="""window.fcMaybeOpenOptionalGuideV1103 = function(){
  clearTimeout(optionalTimer);
  // Guidelines are mandatory. Never put the optional guide on top of that gate.
  if (!state?.profile || !profileComplete() || guideSeen() ||
      !guidelinesAcked() || document.getElementById('guidelinesModal')?.classList.contains('open')) return;
  optionalTimer = setTimeout(() => {
    // Recheck when the timer fires: the Guidelines modal may have opened meanwhile.
    if (state?.profile && !guideSeen() && guidelinesAcked() &&
        !document.getElementById('guidelinesModal')?.classList.contains('open')) openGuide(false);
  }, 900);
};"""
for needle,count in [(before,1),(after,0),(old,1)]:
 actual=s.count(needle)
 if actual != count:
  raise SystemExit(f'STOP: staging source not expected for {needle[:90]!r}; wanted={count} found={actual}')
s=s.replace(old,new,1).replace(before,after,1)
assert s.count('!guidelinesAcked()')==1
assert s.count('&& guidelinesAcked()')==1
assert s.count(after)==1
path.write_text(s,encoding='utf-8')
print('STAGED v1396: Guidelines acknowledgement gates optional guide before scheduling and when timer fires')
