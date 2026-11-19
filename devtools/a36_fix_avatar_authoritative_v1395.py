#!/usr/bin/env python3
"""A3.6 v1395 staging-only: Following avatar rings use active eligibility and official wins.
Small guarded edit to root index.html; never touches main, RLS or production DB.
"""
from pathlib import Path
p=Path('index.html')
s=p.read_text('utf-8')
before='<meta content="v1394 · a36-following-active-only" name="fc-build"/>'
after='<meta content="v1395 · a36-following-authoritative-rings" name="fc-build"/>'
old="""    // Get their recent entries in active challenges
    const followingIds = following.map(u => u.id);
    const { data: entryData } = await db
      .from('entries')
      .select('id, user_id, challenge_id, challenge:challenges!entries_challenge_id_fkey(id, title, submission_deadline, voting_end, status)')
      .in('user_id', followingIds)
      .gte('created_at', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString())
      .order('created_at', { ascending: false })
      .limit(100);

    // Map: userId → { hasActive, hasWon, entryId, challengeId }
    const now = new Date();
    const activityMap = {};
    (entryData || []).forEach(e => {
      const ch = e.challenge;
      if (!ch) return;
      const subEnd = ch.submission_deadline ? new Date(ch.submission_deadline) : null;
      const voteEnd = ch.voting_end ? new Date(ch.voting_end) : null;
      const isActive = (subEnd && now < subEnd) || (voteEnd && now < voteEnd);
      const isDecided = voteEnd && now > voteEnd;

      if (!activityMap[e.user_id]) activityMap[e.user_id] = { hasActive: false, hasDecided: false, entryId: null, challengeId: null };
      if (isActive) {
        activityMap[e.user_id].hasActive = true;
        activityMap[e.user_id].entryId = e.id;
        activityMap[e.user_id].challengeId = e.challenge_id;
      }
      if (isDecided) activityMap[e.user_id].hasDecided = true;
    });

    // Sort: active first, then won recently, then rest
    const sorted = [...following].sort((a, b) => {
      const aActive = activityMap[a.id]?.hasActive ? 2 : activityMap[a.id]?.hasDecided ? 1 : 0;
      const bActive = activityMap[b.id]?.hasActive ? 2 : activityMap[b.id]?.hasDecided ? 1 : 0;
      return bActive - aActive;
    });

    scroll.innerHTML = sorted.map(u => {
      const act = activityMap[u.id];
      const ringClass = act?.hasActive ? 'ring-active' : act?.hasDecided ? 'ring-won' : 'ring-none';
      const hasActivity = act?.hasActive || act?.hasDecided;"""
new="""    // Query recent eligible entries independently of the feed; exclude private,
    // voided, hidden tiebreaker and unapproved media from activity indicators.
    const followingIds = following.map(u => u.id);
    const { data: entryData, error: entryError } = await db
      .from('entries')
      .select('id,user_id,challenge_id,sd_round,moderation_status,challenge:challenges!entries_challenge_id_fkey(id,title,is_public,status,submission_deadline,voting_end,voided_at,is_championship,sd_phase,sd_round,sd_submit_end,sd_vote_end)')
      .in('user_id', followingIds)
      .in('moderation_status', ['clear','approved'])
      .gte('created_at', new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString())
      .order('created_at', { ascending: false })
      .limit(100);
    if (entryError) throw entryError;
    const publicEntries = (entryData || []).filter(e => e.challenge?.is_public === true &&
      !e.challenge.voided_at && e.challenge.sd_phase !== 'submitting');
    const closedIds = [...new Set(publicEntries
      .filter(e => computeChallengeStatus(e.challenge) === 'closed')
      .map(e => e.challenge_id))];
    // Only authoritative result_winners can justify a gold/winner ring.
    // If this lookup fails, omit winner rings rather than implying a win.
    let winningKeys = new Set();
    if (closedIds.length) {
      try {
        const { data: winners, error: winnerError } = await db
          .from('challenge_result_winners')
          .select('challenge_id,user_id')
          .in('challenge_id',closedIds)
          .in('user_id',followingIds)
          .limit(200);
        if (winnerError) throw winnerError;
        winningKeys = new Set((winners || []).map(w => String(w.challenge_id)+'|'+String(w.user_id)));
      } catch (error) {
        console.warn('[A3.6] Recent official winners could not load', error);
      }
    }
    const activityMap = {};
    publicEntries.forEach(e => {
      const ch = e.challenge;
      const phase = computeChallengeStatus(ch);
      const isActive = ['submitting','voting'].includes(phase) &&
        Number(e.sd_round || 0) === Number(ch.sd_round || 0);
      const officiallyWon = phase === 'closed' &&
        winningKeys.has(String(e.challenge_id)+'|'+String(e.user_id));
      if (!activityMap[e.user_id])
        activityMap[e.user_id] = {hasActive:false,hasWon:false,entryId:null,challengeId:null};
      if (isActive && !activityMap[e.user_id].hasActive) {
        activityMap[e.user_id].hasActive = true;
        activityMap[e.user_id].entryId = e.id;
        activityMap[e.user_id].challengeId = e.challenge_id;
      }
      if (officiallyWon) activityMap[e.user_id].hasWon = true;
    });

    // Active competitors first, then verified recent winners, then everyone else.
    const sorted = [...following].sort((a, b) => {
      const aActive = activityMap[a.id]?.hasActive ? 2 : activityMap[a.id]?.hasWon ? 1 : 0;
      const bActive = activityMap[b.id]?.hasActive ? 2 : activityMap[b.id]?.hasWon ? 1 : 0;
      return bActive - aActive;
    });

    scroll.innerHTML = sorted.map(u => {
      const act = activityMap[u.id];
      const ringClass = act?.hasActive ? 'ring-active' : act?.hasWon ? 'ring-won' : 'ring-none';
      const hasActivity = act?.hasActive || act?.hasWon;"""
oldLink="""    scroll.querySelectorAll('[data-entry-open]').forEach(el => {
      el.addEventListener('click', () => openFeedViewer(el.dataset.entryOpen, el.dataset.entryId));
    });"""
newLink="""    scroll.querySelectorAll('[data-entry-open]').forEach(el => {
      el.addEventListener('click', () => {
        fcA36OpenFollowedEntryV1393(el.dataset.entryOpen, el.dataset.entryId, false)
          .catch(error => {
            console.warn('[A3.6] Following avatar entry unavailable', error);
            toast('This entry is unavailable. Try again.');
          });
      });
    });"""
for v,n in [(before,1),(after,0),(old,1),(oldLink,1)]:
 if s.count(v)!=n:raise SystemExit('STOP: staging mismatch %s expected=%d got=%d'%(v[:60],n,s.count(v)))
s=s.replace(before,after,1).replace(old,new,1).replace(oldLink,newLink,1)
assert s.count("const ringClass = act?.hasActive ? 'ring-active' : act?.hasWon ? 'ring-won' : 'ring-none';")==1
assert s.count(after)==1
p.write_text(s,'utf-8')
print('STAGED v1395: avatar rings only for eligible active entries and authoritative winners; off-feed viewer uses hydrated safe path.')
