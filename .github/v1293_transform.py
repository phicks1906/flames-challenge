from pathlib import Path
p=Path('index.html')
s=p.read_text(encoding='utf-8')
repls=[
('<meta content="v1292 · admin-entry-controls-and-adaptive-video-viewer" name="fc-build"/>','<meta content="v1293 · home-next-move-routing-fix" name="fc-build"/>'),
('<meta content="Added direct Admin moderation controls to the entry viewer and made played videos use their actual orientation instead of forcing every video into a small 16:9 stage." name="fc-whatsnew"/>','<meta content="Fixed Your Next Move routing so Home recommendations perform their own action instead of being intercepted by the daily Ember briefing. The daily briefing still opens automatically on first login each day." name="fc-whatsnew"/>')
]
for old,new in repls:
    c=s.count(old)
    if c!=1: raise SystemExit(f'replacement count {c}: {old[:90]}')
    s=s.replace(old,new,1)
old='''  let homeTileOpeningV1275 = false;\n  function wireHomeTileV1221() {\n    const tile = byId('emberHomeCard');\n    if (!tile || tile.dataset.fcDailyBriefingV1221 === '1') return;\n    tile.dataset.fcDailyBriefingV1221 = '1';\n    tile.addEventListener('click', async event => {\n      if (!event.target.closest('#emberHomeCard')) return;\n      event.preventDefault();\n      event.stopImmediatePropagation();\n\n      // v1275 root-cause fix: when there were no daily-briefing items, the old\n      // fallback called action.click(). That synthetic click re-entered THIS\n      // capture handler, failed again, clicked again, and created an unbounded\n      // async click loop that made the entire Home surface appear frozen.\n      if (homeTileOpeningV1275) return;\n      homeTileOpeningV1275 = true;\n      try {\n        if (!(await openDailyEmberV1221(true))) {\n          const run = tile.__fcGuidanceRunV1275;\n          if (typeof run === 'function') run();\n        }\n      } finally {\n        homeTileOpeningV1275 = false;\n      }\n    }, true);\n  }\n'''
new='''  // v1293 — Your Next Move is a recommendation/action surface, not the\n  // launcher for the daily Ember briefing. The old capture-phase listener\n  // intercepted every Home recommendation tap before the recommendation's own\n  // click handler could run. Daily Ember remains automatic once per day below;\n  // the Home tile now owns its tap again.\n'''
if s.count(old)!=1: raise SystemExit(f'capture block count {s.count(old)}')
s=s.replace(old,new,1)
old2='''  const observer = new MutationObserver(() => wireHomeTileV1221());\n  const home = byId('emberHomeCard');\n  if (home) observer.observe(home,{childList:true,subtree:true});\n  wireHomeTileV1221();\n\n  let attempts = 0;\n  const timer = setInterval(() => {\n    attempts++;\n    wireHomeTileV1221();\n    if (state?.profile && !state?.loading) {\n'''
new2='''  let attempts = 0;\n  const timer = setInterval(() => {\n    attempts++;\n    if (state?.profile && !state?.loading) {\n'''
if s.count(old2)!=1: raise SystemExit(f'wire loop count {s.count(old2)}')
s=s.replace(old2,new2,1)
marker="<script>window.FC_V1293_VALIDATION={build:'v1293',homeNextMoveOwnsTap:true,dailyBriefingCaptureInterceptorRemoved:true,dailyBriefingAutomaticFirstLoginPreserved:true,directGuidanceRunPreserved:true,v1292AdminViewerPreserved:true};</script>\n"
if '</body>' not in s: raise SystemExit('body marker missing')
s=s.replace('</body>',marker+'</body>',1)
p.write_text(s,encoding='utf-8')
