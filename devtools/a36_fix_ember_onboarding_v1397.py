#!/usr/bin/env python3
"""v1397 staging-only: keep native Ember behind setup, Guidelines and guide.
Do not touch production, DB, service worker or other app logic.
"""
from pathlib import Path
p=Path("index.html")
s=p.read_text("utf8")
before='<meta content="v1396 · a36-guidelines-before-welcome-guide" name="fc-build"/>'
after='<meta content="v1397 · a36-ember-after-onboarding" name="fc-build"/>'
if s.count(before)!=1 or s.count(after):
 raise SystemExit("STOP: wrong staged baseline")
anchor="""  window.openDailyEmberV1221 = async function openDailyEmberV1221(force = false) {
    if (!state?.profile || state?.loading) return false;
    if (document.body.dataset.fcEmberGuidance === 'off') return false;"""
helper="""  // v1397 — Native dialog.showModal() makes the background untappable.
  // Finish mandatory setup, Guidelines and first-run guide before Ember.
  function fcA36EmberMustDeferV1397() {
    const p = state?.profile;
    if (!p || Number(p.onboarding_version || 0) < 1103 ||
        Number(p.walkthrough_seen_version || 0) < 1103) return true;
    if (typeof guidelinesAcked === 'function' && !guidelinesAcked()) return true;
    return !!document.querySelector(
      '#fcOnboardingV1103.open, #guidelinesModal.open, ' +
      '#fcCommercialModalV1103.open, .modal-backdrop.open, dialog[open]'
    );
  }
  let fcA36EmberDeferralsV1397 = 0;

  window.openDailyEmberV1221 = async function openDailyEmberV1221(force = false) {
    if (!state?.profile || state?.loading) return false;
    if (document.body.dataset.fcEmberGuidance === 'off') return false;
    if (fcA36EmberMustDeferV1397()) return false;"""
if s.count(anchor)!=1:raise SystemExit("STOP: Ember open anchor missing")
s=s.replace(anchor,helper,1)
race="""    if (!state?.profile || state?.loading || !document.body.classList.contains('fc-boot-ready-v1095') ||
        document.querySelector('#fcOnboardingV1103.open, #fcCommercialModalV1103.open, dialog[open]')) return false;
    const items = buildItemsV1221();"""
safer="""    if (!state?.profile || state?.loading || !document.body.classList.contains('fc-boot-ready-v1095') ||
        fcA36EmberMustDeferV1397()) return false;
    const items = buildItemsV1221();"""
if s.count(race)!=1:raise SystemExit("STOP: Ember async guard changed")
s=s.replace(race,safer,1)
pos=s.index('  async function maybeOpenDailyEmberV1221() {')
old="""    try { if (localStorage.getItem(key) === '1') return; } catch (_) {}

    try {"""
new="""    try { if (localStorage.getItem(key) === '1') return; } catch (_) {}

    // Preserve the once-daily reminder: defer it until first-run gates close.
    if (fcA36EmberMustDeferV1397()) {
      if (++fcA36EmberDeferralsV1397 <= 240)
        setTimeout(maybeOpenDailyEmberV1221, 1500);
      return;
    }
    fcA36EmberDeferralsV1397 = 0;

    try {"""
if s[pos:].count(old)!=1:raise SystemExit("STOP: Ember reminder retry guard changed")
s=s[:pos]+s[pos:].replace(old,new,1)
s=s.replace(before,after,1)
if s.count("function fcA36EmberMustDeferV1397()")!=1 or s.count(after)!=1:
 raise SystemExit("STOP: post-patch invariant failed")
p.write_text(s,"utf8")
print("STAGED v1397: Ember native modal waits for account setup, Guidelines and guide; deferred daily reminder preserved")
