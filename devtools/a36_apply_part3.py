#!/usr/bin/env python3
"""Stage A3.6 Part 3: connect existing Following people to eligible active entries.

Modify only root index.html, on staging branch. Fail closed if expected anchors drift.
No backend, navigation, or production changes.
"""
from pathlib import Path
sfile=Path('index.html')
s=sfile.read_text(encoding='utf-8')
old='<meta content="v1390 · a36-vote-history-part1" name="fc-build"/>'
new='<meta content="v1391 · a36-following-active-entries" name="fc-build"/>'
a="    renderFollowList(list, profiles, competingIds, 'following');"
b="    renderFollowList(list, profiles, competingIds, 'following');\n    fcA36AttachFollowingEntriesV1391(list, profiles);"
anchor="async function loadFollowersList() {"
if s.count(old)!=1 or s.count(new)!=0 or s.count(a)!=1 or s.count(anchor)!=1:
 raise SystemExit('STOP: staging anchors are missing, repeated or already changed')
block="""// A3.6 Part 3: link a followed person to an eligible PUBLIC active entry
// already hydrated by the production feed. Do not infer wins or request hidden entries.
function fcA36AttachFollowingEntriesV1391(list, profiles) {
  if (!list || !state.profile || !Array.isArray(state.feedEntries)) return;
  const challenges = new Map((state.challenges || []).map(ch => [String(ch.id), ch]));
  const entries = state.feedEntries;
  profiles.forEach((person, index) => {
    const latest = entries.filter(e => String(e.user_id) === String(person.id))
      .map(e => ({ entry:e, challenge:challenges.get(String(e.challenge_id)) }))
      .filter(item => item.challenge && item.challenge.is_public === true &&
        ['submitting','voting'].includes(computeChallengeStatus(item.challenge)))
      .sort((a,b) => Date.parse(b.entry.created_at || 0) - Date.parse(a.entry.created_at || 0))[0];
    if (!latest) return;
    const row = list.children[index];
    const details = row?.children?.[1];
    if (!details) return;
    const btn = document.createElement('button');
    btn.type='button';
    btn.className='fc-a36-following-entry-v1391';
    btn.textContent='View entry · ' + (latest.challenge.title || 'Competition');
    btn.style.cssText='display:block;margin-top:5px;padding:5px 0;border:0;background:transparent;color:var(--ember);font-size:12px;font-weight:700;text-align:left;max-width:100%;white-space:normal;cursor:pointer';
    btn.addEventListener('click', event => {
      event.stopPropagation();
      closeFollowingSheet();
      openFeedViewer(latest.challenge.id, latest.entry.id);
    });
    details.appendChild(btn);
  });
}

"""
s=s.replace(old,new,1).replace(a,b,1).replace(anchor,block+anchor,1)
if s.count('function fcA36AttachFollowingEntriesV1391')!=1 or s.count(new)!=1:
 raise SystemExit('STOP: post-change invariants failed')
sfile.write_text(s,encoding='utf-8')
print('STAGED v1391 Part 3 active public entry links; no production changes.')
