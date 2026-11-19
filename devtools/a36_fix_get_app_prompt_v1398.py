#!/usr/bin/env python3
"""A3.6 staging v1398: one-time Get App prompt cannot inert an open native Ember.
Preserve prompt's one-time localStorage key and existing user controls.
"""
from pathlib import Path
p=Path("index.html")
s=p.read_text("utf8")
before='<meta content="v1397 · a36-ember-after-onboarding" name="fc-build"/>'
after='<meta content="v1398 · a36-safe-get-app-after-ember" name="fc-build"/>'
if s.count(before)!=1 or s.count(after):
 raise SystemExit("STOP: expected staged v1397")
anchor="""function maybeShowGetAppPrompt() {
  try {
    if (!state.profile?.id) return;
    try { if (localStorage.getItem(GETAPP_PROMPT_KEY)) return; } catch(e) {}"""
new="""function maybeShowGetAppPrompt() {
  try {
    if (!state.profile?.id) return;
    try { if (localStorage.getItem(GETAPP_PROMPT_KEY)) return; } catch(e) {}
    // v1398: a DOM modal above a native showModal() dialog makes the native
    // Ember dialog inert. Give Ember and mandatory first-run screens priority.
    const dailyEmberV1398 = document.getElementById('fcEmberDailyBriefingV1221');
    if (dailyEmberV1398?.open) {
      if (dailyEmberV1398.dataset.fcGetAppAfterEmberV1398 !== '1') {
        dailyEmberV1398.dataset.fcGetAppAfterEmberV1398 = '1';
        dailyEmberV1398.addEventListener('close', () => {
          delete dailyEmberV1398.dataset.fcGetAppAfterEmberV1398;
          setTimeout(maybeShowGetAppPrompt, 600);
        }, {once:true});
      }
      return;
    }
    // Optional install help must never supersede mandatory Guidelines,
    // required appearance/interests or any other active dialog.
    if (Number(state.profile.onboarding_version || 0) < 1103 ||
        Number(state.profile.walkthrough_seen_version || 0) < 1103 ||
        (typeof guidelinesAcked === 'function' && !guidelinesAcked()) ||
        document.querySelector('#fcOnboardingV1103.open, #guidelinesModal.open, ' +
          '.modal-backdrop.open, dialog[open]')) return;"""
if s.count(anchor)!=1:raise SystemExit("STOP: Get App opening function changed")
s=s.replace(anchor,new,1).replace(before,after,1)
assert s.count('dailyEmberV1398.addEventListener(')==1
assert s.count(after)==1
p.write_text(s,"utf8")
print("STAGED v1398: one-time Get App waits for native Ember close and completed first-run steps; install prompt preserved")
