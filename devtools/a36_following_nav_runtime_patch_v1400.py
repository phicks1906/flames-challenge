#!/usr/bin/env python3
"""A3.6 staged v1400: keep primary navigation hidden whenever Following is open.
Use scoped inline CSS properties with restoration because legacy navigation styles
override the standalone v1399 stylesheet in the actual browser.
"""
from pathlib import Path
p=Path("index.html")
s=p.read_text("utf8")
before='<meta content="v1399 · a36-following-nav-clearance" name="fc-build"/>'
after='<meta content="v1400 · a36-following-nav-runtime" name="fc-build"/>'
if s.count(before)!=1 or s.count(after):
 raise SystemExit("STOP: expected staged v1399 baseline")
anchor="""async function openFollowingSheet() {
  document.getElementById('profileModal')?.classList.remove('open');
  document.getElementById('followingSheet').classList.add('open');
  _fsActiveTab = 'following';"""
new="""// v1400: the primary nav has legacy high-priority visibility rules. During
// Connections, set the effective inline priority and restore it on exit.
// Observe all close paths, including backdrop and generic modal cleanup.
let fcA36FollowingNavPriorV1400 = null;
function fcA36SyncFollowingNavV1400() {
  const sheet = document.getElementById('followingSheet');
  const nav = document.getElementById('bottomNav');
  if (!sheet || !nav) return;
  if (sheet.classList.contains('open')) {
    if (!fcA36FollowingNavPriorV1400) {
      fcA36FollowingNavPriorV1400 = {
        visibility:nav.style.getPropertyValue('visibility'),
        visibilityPriority:nav.style.getPropertyPriority('visibility'),
        pointerEvents:nav.style.getPropertyValue('pointer-events'),
        pointerPriority:nav.style.getPropertyPriority('pointer-events')
      };
    }
    nav.style.setProperty('visibility','hidden','important');
    nav.style.setProperty('pointer-events','none','important');
  } else if (fcA36FollowingNavPriorV1400) {
    const prev = fcA36FollowingNavPriorV1400;
    if (prev.visibility) nav.style.setProperty('visibility',prev.visibility,prev.visibilityPriority);
    else nav.style.removeProperty('visibility');
    if (prev.pointerEvents) nav.style.setProperty('pointer-events',prev.pointerEvents,prev.pointerPriority);
    else nav.style.removeProperty('pointer-events');
    fcA36FollowingNavPriorV1400 = null;
  }
}
function fcA36WatchFollowingNavV1400() {
  const sheet = document.getElementById('followingSheet');
  if (!sheet || sheet.dataset.fcA36NavObservedV1400 === '1') return;
  sheet.dataset.fcA36NavObservedV1400 = '1';
  new MutationObserver(fcA36SyncFollowingNavV1400).observe(sheet,{
    attributes:true,attributeFilter:['class']
  });
}
async function openFollowingSheet() {
  document.getElementById('profileModal')?.classList.remove('open');
  document.getElementById('followingSheet').classList.add('open');
  fcA36WatchFollowingNavV1400();
  fcA36SyncFollowingNavV1400();
  _fsActiveTab = 'following';"""
if s.count(anchor)!=1:raise SystemExit("STOP: Following open anchor changed")
s=s.replace(anchor,new,1)
close="""function closeFollowingSheet() {
  document.getElementById('followingSheet').classList.remove('open');
}"""
close_new="""function closeFollowingSheet() {
  document.getElementById('followingSheet').classList.remove('open');
  fcA36SyncFollowingNavV1400();
}"""
if s.count(close)!=1:raise SystemExit("STOP: Following close anchor changed")
s=s.replace(close,close_new,1).replace(before,after,1)
if s.count("function fcA36SyncFollowingNavV1400()")!=1:
 raise SystemExit("STOP: runtime nav guard missing")
p.write_text(s,"utf8")
print("STAGED v1400: effective Following nav visibility and pointer-events gated with restoration across all close paths")
