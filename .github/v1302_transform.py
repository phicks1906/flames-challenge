from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')

def one(old,new,label):
    global s
    c=s.count(old)
    if c!=1:
        raise SystemExit(f'{label}: expected 1, found {c}')
    s=s.replace(old,new,1)

one('<meta content="v1301 · native-audio-pitch-stability" name="fc-build"/>',
    '<meta content="v1302 · feed-swipe-popout-viewer" name="fc-build"/>','build meta')
one('<meta content="Kept competition audio on the native media path so it cannot drag or shift pitch, while preserving moving audio visuals without routing sound through Web Audio." name="fc-whatsnew"/>',
    '<meta content="Made Challenger swipes obvious on the feed and replaced the near-full-screen feed viewer with a quiet pop-out overlay that closes back to the same feed position." name="fc-whatsnew"/>','whatsnew')

one("""  sheet.classList.add('open');
  fcOpenImmersiveViewerV1198('feed-viewer');
  fcPositionFeedViewerV1199();
""","""  sheet.classList.add('open');
  // v1302 — this is a feed pop-out, not a destination screen. Keep the
  // underlying feed visually present while the existing immersive controller
  // still freezes body scroll and protects nested-viewer depth.
  document.body.classList.add('fc-feed-popout-active-v1302');
  fcOpenImmersiveViewerV1198('feed-viewer');
  fcPositionFeedViewerV1199();
""",'feed popout open state')

one("""  sheet.classList.remove('open');
  sheet.classList.remove('fc-viewer-centered-v1199','fc-viewer-bottom-v1199');
  fcCloseImmersiveViewerV1198('feed-viewer');
  _fvChallenge = null;
""","""  sheet.classList.remove('open');
  sheet.classList.remove('fc-viewer-centered-v1199','fc-viewer-bottom-v1199');
  document.body.classList.remove('fc-feed-popout-active-v1302');
  fcCloseImmersiveViewerV1198('feed-viewer');
  _fvChallenge = null;
""",'feed popout close state')

marker="<script>window.FC_V1301_VALIDATION={build:'v1301',nativeAudioOutputOnly:true,noCompetitionMediaElementSource:true,noCompetitionAudioContext:true,pitchRateLockedAtOne:true,pitchPreservationEnabled:true,visualsDrivenByCurrentTimeOnly:true,v1300ScrollFixPreserved:true};</script>"
insert="""<style id="fc-v1302-feed-swipe-popout-css">
/* v1302 — Eric feedback: feed Challenger changes must visibly travel.
   v1079 deliberately exposed the next card, but v1082 later reset every card
   to 100% width. Restore a meaningful peek without adding touch interception. */
#feedContainer .fc-entry-rail-v1079 .fcc-entries-scroll,
#challengesGrid .fc-entry-rail-v1079 .fcc-entries-scroll{
  gap:10px!important;
  scroll-snap-type:x mandatory!important;
  overscroll-behavior-x:contain!important;
}
#feedContainer .fc-entry-rail-v1079 .fcc-entry-card,
#challengesGrid .fc-entry-rail-v1079 .fcc-entry-card{
  flex:0 0 calc(100% - 42px)!important;
  min-width:calc(100% - 42px)!important;
  width:calc(100% - 42px)!important;
  scroll-snap-align:start!important;
  scroll-snap-stop:always!important;
}
#feedContainer .fc-entry-rail-v1079 .fcc-entries-scroll::after,
#challengesGrid .fc-entry-rail-v1079 .fcc-entries-scroll::after{
  content:'';
  flex:0 0 32px;
  width:32px;
}

/* Feed detail is now a contained pop-out over the feed, not a second screen. */
#feedViewerSheet.open,
#feedViewerSheet.open.fc-viewer-centered-v1199,
#feedViewerSheet.open.fc-viewer-bottom-v1199{
  align-items:center!important;
  justify-content:center!important;
  padding:calc(12px + env(safe-area-inset-top,0px)) 12px calc(12px + env(safe-area-inset-bottom,0px))!important;
  background:rgba(0,0,0,.38)!important;
  -webkit-backdrop-filter:blur(1.5px)!important;
  backdrop-filter:blur(1.5px)!important;
}
#feedViewerSheet.open #feedViewerModal{
  width:min(520px,calc(100vw - 24px))!important;
  height:auto!important;
  max-height:min(82dvh,760px)!important;
  margin:0 auto!important;
  border-radius:24px!important;
  border:1px solid rgba(255,255,255,.14)!important;
  border-top:1px solid rgba(255,118,54,.45)!important;
  box-shadow:0 24px 70px rgba(0,0,0,.62),0 0 0 1px rgba(255,106,44,.05)!important;
  overflow:hidden!important;
  animation:fcFeedPopV1302 .17s cubic-bezier(.2,.8,.2,1)!important;
}
/* A pop-out should not carry the visual language of a draggable bottom sheet. */
#feedViewerSheet.open #feedViewerModal>div:first-child{
  display:none!important;
}
#feedViewerSheet.open #fvScrollRegion{
  max-height:calc(min(82dvh,760px) - 154px - env(safe-area-inset-bottom,0px))!important;
  overscroll-behavior:contain!important;
}
@keyframes fcFeedPopV1302{
  from{opacity:.35;transform:scale(.975)}
  to{opacity:1;transform:scale(1)}
}
/* Keep the primary nav visible but inert underneath the dimmed overlay so the
   member can still see they never left Home/Compete. Nested viewers still hide it. */
body.fc-feed-popout-active-v1302[data-fc-immersive-depth-v1198="1"] #bottomNav{
  visibility:visible!important;
  opacity:1!important;
  pointer-events:none!important;
}
body.theme-light #feedViewerSheet.open{
  background:rgba(24,20,18,.28)!important;
}
@media (prefers-reduced-motion:reduce){
  #feedViewerSheet.open #feedViewerModal{animation:none!important}
}
</style>
<script>window.FC_V1302_VALIDATION={build:'v1302',feedCardsExposeNextChallenger:true,nativeFeedSwipePreserved:true,feedViewerIsCenteredPopout:true,feedRemainsVisibleUnderOverlay:true,feedScrollPositionPreserved:true,noSecondScreenAnimation:true,v1301NativeAudioPreserved:true};</script>
"""+marker
one(marker,insert,'append v1302 styles and validation')

p.write_text(s,encoding='utf-8')
