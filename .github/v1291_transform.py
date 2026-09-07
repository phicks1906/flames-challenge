from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
repls=[
('<meta content="v1290 · ember-title-and-score-copy-fix" name="fc-build"/>','<meta content="v1291 · moderation-final-status-updates" name="fc-build"/>'),
('<meta content="Removed the Read prefix from Ember challenge titles and corrected Championship copy so Championship rounds do not add to the Championship Score." name="fc-whatsnew"/>','<meta content="Made video moderation final states explicit: automatic approvals, extra-review states, and rejections now notify entrants, and rejected videos no longer remain visually stuck under review." name="fc-whatsnew"/>'),
("    if (stateValue === 'escalated') return {state:'manual',label:'Extra safety check · Only visible to you',title:'We’re taking a closer look',detail:'The automated check could not make a clear decision. Your entry stays private while an administrator finishes the check. You do not need to resubmit.',retry:false};",
"    if (stateValue === 'approved') return {state:'approved',label:'APPROVED · LIVE',title:'Video approved',detail:'Your entry passed review and is now visible in the challenge.',retry:false};\n    if (stateValue === 'rejected') return {state:'rejected',label:'NOT APPROVED',title:'Video not approved',detail:'Your entry is saved but hidden. Replace the video before entries close to resubmit.',retry:false};\n    if (stateValue === 'escalated') return {state:'manual',label:'EXTRA REVIEW · PRIVATE',title:'We’re taking a closer look',detail:'The automated check could not make a clear decision. Your entry stays saved and private while an administrator finishes the check. You do not need to resubmit.',retry:false};"),
("    if (stateValue === 'flagged') return {state:'manual',label:'Extra safety check · Only visible to you',title:'We’re taking a closer look',detail:'The automated check was uncertain. Your entry stays private while an administrator finishes the check.',retry:false};",
"    if (stateValue === 'flagged') return {state:'manual',label:'EXTRA REVIEW · PRIVATE',title:'We’re taking a closer look',detail:'The automated check was uncertain. Your entry stays saved and private while an administrator finishes the check.',retry:false};"),
]
for old,new in repls:
    c=s.count(old)
    if c!=1: raise SystemExit(f'replacement count {c}: {old[:100]}')
    s=s.replace(old,new,1)
old="""  async function refreshEntry(entryId){
    const result = await fcWithTimeoutV1099("""
new="""  async function refreshEntry(entryId){
    const beforeEntryV1291 = (state?.currentEntries || []).find(item => String(item.id) === String(entryId)) || null;
    const beforeStatusV1291 = String(beforeEntryV1291?.moderation_status || '').toLowerCase();
    const result = await fcWithTimeoutV1099("""
if s.count(old)!=1: raise SystemExit('refreshEntry start mismatch')
s=s.replace(old,new,1)
old="""    if (typeof renderChallenges === 'function') renderChallenges();
    if (typeof renderFeed === 'function') renderFeed();
    return true;
  }"""
new="""    if (typeof renderChallenges === 'function') renderChallenges();
    if (typeof renderFeed === 'function') renderFeed();
    const afterStatusV1291 = String(result.data?.moderation_status || '').toLowerCase();
    if (afterStatusV1291 && afterStatusV1291 !== beforeStatusV1291) {
      if (afterStatusV1291 === 'approved' && typeof toast === 'function') toast('✅ Video approved — your entry is live.');
      else if (afterStatusV1291 === 'rejected' && typeof toast === 'function') toast('🚫 Video not approved — replace it before entries close.');
      else if (['flagged','escalated'].includes(afterStatusV1291) && typeof toast === 'function') toast('⏳ Extra safety review — your entry is saved and private.');
    }
    return true;
  }"""
if s.count(old)!=1: raise SystemExit('refreshEntry end mismatch')
s=s.replace(old,new,1)
old="""  notifyEntryModerated(entryId, 'rejected');
  toast('🚫 Entry rejected — hidden from everyone, submitter notified');"""
new="""  toast('🚫 Entry rejected — hidden from everyone, submitter notified');"""
if s.count(old)!=1: raise SystemExit('manual reject notify mismatch')
s=s.replace(old,new,1)
needle='.fc-review-badge-v1049[data-fc-mod-state="reviewing"]{background:rgba(255,150,50,.10)!important;color:var(--ember)!important}\n'
add=needle+'.fc-review-badge-v1049[data-fc-mod-state="rejected"]{background:rgba(224,68,68,.11)!important;color:#ff6565!important;border-color:rgba(224,68,68,.34)!important}\n.fc-review-badge-v1049[data-fc-mod-state="approved"]{background:rgba(47,190,93,.10)!important;color:#57d979!important;border-color:rgba(47,190,93,.30)!important}\n'
if s.count(needle)!=1: raise SystemExit('css marker mismatch')
s=s.replace(needle,add,1)
marker="<script>window.FC_V1291_VALIDATION={build:'v1291',rejectedPresentationFinal:true,approvedPresentationFinal:true,manualReviewPresentationFinal:true,transitionToasts:true,serverNotificationTriggerRequired:true,manualRejectDuplicateNotificationRemoved:true,v1290CopyPreserved:true};</script>\n"
if '</body>' not in s: raise SystemExit('body missing')
s=s.replace('</body>',marker+'</body>',1)
p.write_text(s,encoding='utf-8')
