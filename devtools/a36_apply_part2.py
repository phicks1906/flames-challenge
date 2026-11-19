#!/usr/bin/env python3
"""Stage A3.6 Part 2: show official outcomes beside an authenticated member's votes.
Exact-match patch to v1391 only; does not change production, schema, or integrations.
"""
from pathlib import Path

index = Path('index.html')
component = Path('devtools/a36_votes_component.html')
s = index.read_text(encoding='utf-8')
old_version = '<meta content="v1391 · a36-following-active-entries" name="fc-build"/>'
new_version = '<meta content="v1392 · a36-voted-official-results" name="fc-build"/>'
old_news = 'Your competitive votes are now listed on your own profile, with a path back to each competition.'
new_news = 'Your competition votes now link to official settled results, including wins, co-wins and no-contests.'
anchor = '<!-- A3.6 Part 1: member-only competition vote history; no result calculation -->'
if s.count(old_version)!=1 or s.count(anchor)!=1 or s.count(old_news)!=1:
    raise SystemExit('STOP: v1391 staging baseline changed, or Part 2 already staged')
start = s.index(anchor)
end = s.index('</script>', start) + len('</script>')
old = s[start:end]
if old.count('id="fc-a36-v1390-votes-js"')!=1 or old.count('challenge_result_winners'):
    raise SystemExit('STOP: old Part 1 component no longer matches')
new = component.read_text(encoding='utf-8').strip().replace(
    anchor, '<!-- A3.6 Part 2: competition vote history with authoritative settled results -->',1)
if not all(k in new for k in (
    "db.from('entry_votes')", "db.from('challenge_results')",
    "db.from('challenge_result_winners')", "Official result · Your pick won",
    "Official result · Your pick co-won", "Official result not available")):
    raise SystemExit('STOP: component missing required authoritative outcome states')
if 'state.myVotes' in new or '<html' in new or '</body>' in new:
    raise SystemExit('STOP: invalid or poll-conflicting Part 2 component')
s = s[:start] + new + s[end:]
s = s.replace(old_version,new_version,1).replace(old_news,new_news,1)
if (s.count(new_version)!=1 or s.count('id="fc-a36-v1390-votes-js"')!=1 or
    s.count('function fcA36AttachFollowingEntriesV1391')!=1):
    raise SystemExit('STOP: post-patch invariants failed')
index.write_text(s,encoding='utf-8')
print('STAGED: v1392 Part 2 authoritative settled outcomes. Changed index.html only.')
