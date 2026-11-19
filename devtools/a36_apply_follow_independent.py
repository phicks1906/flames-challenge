#!/usr/bin/env python3
"""A3.6 Part 4: connect Following to independently queried public eligible entries.
Guarded staging-only patch of root index.html. Does not touch databases or production.
"""
from pathlib import Path
src=Path("index.html")
s=src.read_text(encoding="utf-8")
before='<meta content="v1392 · a36-voted-official-results" name="fc-build"/>'
after='<meta content="v1393 · a36-following-independent" name="fc-build"/>'
start_token="function fcA36AttachFollowingEntriesV1391(list, profiles) {"
end_token="\nasync function loadFollowersList() {"
call="    fcA36AttachFollowingEntriesV1391(list, profiles);"
newcall="    await fcA36AttachFollowingEntriesV1391(list, profiles);"
checks=[(before,1),(after,0),(start_token,1),(end_token,1),(call,1)]
for needle, expected in checks:
    if s.count(needle)!=expected:
        raise SystemExit("STOP: staging anchor mismatch %r: expected %s, got %s"%(needle,expected,s.count(needle)))
start=s.index(start_token)
end=s.index(end_token,start)
old=s[start:end]
assert old.count("state.feedEntries")==2, "Original Following implementation unexpectedly changed"
block="""// A3.6 Part 4 — query followed people's entries independently from the feed.
// Only public, active, moderation-cleared entries are eligible for a direct link.
async function fcA36AttachFollowingEntriesV1391(list, profiles) {
  if (!list || !state.profile || !Array.isArray(profiles) || !profiles.length) return;
  const memberId = String(state.profile.id);
  const followeeIds = profiles.map(p => p.id).filter(Boolean);
  let entryData;
  try {
    const { data, error } = await fcWithTimeoutV1099(
      db.from('entries')
        .select('id,user_id,challenge_id,created_at,moderation_status,sd_round,challenge:challenges!entries_challenge_id_fkey(id,title,is_public,status,created_at,submission_deadline,voting_end,voided_at,is_championship,sd_phase,sd_round,sd_submit_end,sd_vote_end)')
        .in('user_id', followeeIds)
        .in('moderation_status', ['approved','clear'])
        .order('created_at', { ascending:false })
        .limit(500),
      7000, 'Following entries');
    if (error) throw error;
    entryData = data || [];
  } catch (error) {
    console.warn('[A3.6] Following entry lookup failed:', error);
    if (String(state.profile?.id || '') === memberId) toast('Could not check followed entries. Try reopening Following.');
    return;
  }
  if (String(state.profile?.id || '') !== memberId ||
      document.getElementById('followingList') !== list) return;
  const eligible = new Map();
  for (const entry of entryData) {
    if (!followeeIds.includes(entry.user_id)) continue;
    const ch = entry.challenge;
    if (!ch || ch.is_public !== true || ch.sd_phase === 'submitting') continue;
    if (!['submitting','voting'].includes(computeChallengeStatus(ch))) continue;
    if (Number(entry.sd_round || 0) !== Number(ch.sd_round || 0)) continue;
    if (!eligible.has(entry.user_id)) eligible.set(entry.user_id,{entry,ch});
  }
  profiles.forEach((person,index) => {
    const match=eligible.get(person.id);
    if (!match) return;
    const details=list.children[index]?.children?.[1];
    if (!details) return;
    const btn=document.createElement('button');
    btn.type='button';
    btn.className='fc-a36-following-entry-v1393';
    btn.textContent='View entry · ' + (match.ch.title || 'Competition');
    btn.style.cssText='display:block;margin-top:5px;padding:5px 0;border:0;background:transparent;color:var(--ember);font-size:12px;font-weight:700;text-align:left;max-width:100%;white-space:normal;cursor:pointer';
    btn.addEventListener('click',async event => {
      event.stopPropagation();
      if (btn.disabled) return;
      btn.disabled=true;
      try {
        await fcA36OpenFollowedEntryV1393(match.ch.id,match.entry.id,true);
      } catch (error) {
        console.warn('[A3.6] Could not open followed entry:',error);
        toast('This entry is unavailable. Try again.');
      } finally { btn.disabled=false; }
    });
    details.appendChild(btn);
  });
}

// Off-feed links must hydrate a current, authorized challenge before calling
// the unchanged production viewer, which otherwise returns on cache misses.
async function fcA36OpenFollowedEntryV1393(challengeId, entryId, fromSheet) {
  const [challengeRes,entryRes]=await Promise.all([
    fcWithTimeoutV1099(db.from('challenges')
      .select('*, creator:profiles!challenges_creator_id_fkey(id,name,avatar)')
      .eq('id',challengeId).eq('is_public',true).maybeSingle(),7000,'Followed challenge'),
    fcWithTimeoutV1099(db.from('entries')
      .select('id,challenge_id,moderation_status,sd_round')
      .eq('id',entryId).eq('challenge_id',challengeId).maybeSingle(),7000,'Followed entry')
  ]);
  if (challengeRes.error) throw challengeRes.error;
  if (entryRes.error) throw entryRes.error;
  const ch=challengeRes.data, entry=entryRes.data;
  if (!ch || ch.is_public !== true || !entry ||
      !['approved','clear'].includes(entry.moderation_status) ||
      ch.sd_phase === 'submitting' ||
      Number(ch.sd_round || 0) !== Number(entry.sd_round || 0)) {
    throw new Error('Followed competition entry is no longer available');
  }
  if (!Array.isArray(state.challenges)) state.challenges=[];
  const index=state.challenges.findIndex(item=>String(item.id)===String(ch.id));
  if (index>=0) state.challenges[index]=ch;
  else state.challenges.push(ch);
  if (fromSheet) closeFollowingSheet();
  await openFeedViewer(ch.id,entry.id);
}
"""
s=s[:start]+block+s[end:]
s=s.replace(before,after,1).replace(call,newcall,1)
if s.count('async function fcA36AttachFollowingEntriesV1391')!=1 or \
   s.count('async function fcA36OpenFollowedEntryV1393')!=1 or \
   s.count(newcall)!=1 or s.count(after)!=1:
    raise SystemExit("STOP: post-patch validation failed")
src.write_text(s,encoding="utf-8")
print('STAGED v1393: direct authorized followed-entry discovery; independent of feed cache.')
