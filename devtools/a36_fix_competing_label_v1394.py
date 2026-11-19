#!/usr/bin/env python3
"""Guarded A3.6 v1394 staging-only fix for false 'Competing now' labels.
Reuse the existing independent eligible-entry query for both badge and View Entry.
No database changes. Production main remains unchanged.
"""
from pathlib import Path
path=Path('index.html')
s=path.read_text(encoding='utf-8')
before='<meta content="v1393 · a36-following-independent" name="fc-build"/>'
after='<meta content="v1394 · a36-following-active-only" name="fc-build"/>'
old_loader="""    const [profilesRes, competingRes] = await Promise.all([
      db.from('profiles').select('id,name,avatar').in('id', ids),
      db.from('entries').select('user_id').in('user_id', ids).gte('created_at', new Date(Date.now() - 7*24*60*60*1000).toISOString()),
    ]);
    const profiles = profilesRes.data || [];
    const competingIds = new Set((competingRes.data || []).map(e => e.user_id));
    profiles.sort((a, b) => (competingIds.has(b.id) ? 1 : 0) - (competingIds.has(a.id) ? 1 : 0) || a.name.localeCompare(b.name));
    renderFollowList(list, profiles, competingIds, 'following');
    await fcA36AttachFollowingEntriesV1391(list, profiles);"""
new_loader="""    const profilesRes = await db.from('profiles').select('id,name,avatar').in('id', ids);
    if (profilesRes.error) throw profilesRes.error;
    const profiles = profilesRes.data || [];
    profiles.sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    // Don't imply current competition based on a recent entry or an unchecked query.
    renderFollowList(list, profiles, new Set(), 'following');
    await fcA36AttachFollowingEntriesV1391(list, profiles);"""
old_attach="""    if (!eligible.has(entry.user_id)) eligible.set(entry.user_id,{entry,ch});
  }
  profiles.forEach((person,index) => {"""
new_attach="""    if (!eligible.has(entry.user_id)) eligible.set(entry.user_id,{entry,ch});
  }
  // The SAME eligible entries drive both the status badge and the View Entry link.
  // Keep active competitors first, retaining stable alphabetical ties.
  const activeIds = new Set(eligible.keys());
  const orderedProfiles = [...profiles].sort((a,b) =>
    (activeIds.has(b.id) ? 1 : 0) - (activeIds.has(a.id) ? 1 : 0) ||
    (a.name || '').localeCompare(b.name || ''));
  renderFollowList(list, orderedProfiles, activeIds, 'following');
  orderedProfiles.forEach((person,index) => {"""
for needle,count in [(before,1),(after,0),(old_loader,1),(old_attach,1),
                      ('async function fcA36AttachFollowingEntriesV1391',1)]:
    if s.count(needle)!=count:
        raise SystemExit('STOP: source anchor mismatch %s expected=%d found=%d'%(needle[:90],count,s.count(needle)))
s=s.replace(old_loader,new_loader,1).replace(old_attach,new_attach,1).replace(before,after,1)
assert s.count("renderFollowList(list, orderedProfiles, activeIds, 'following');")==1
assert s.count("renderFollowList(list, profiles, new Set(), 'following');")==1
assert 'competingRes' not in s[s.index('async function loadFollowingList()'):s.index('async function loadFollowersList()')]
assert s.count(after)==1
path.write_text(s,encoding='utf-8')
print('STAGED v1394: "Competing now" derives exclusively from the verified public active-entry eligibility query.')
