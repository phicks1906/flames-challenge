#!/usr/bin/env python3
"""Staging v1399 visual fix: primary bottom nav cannot cover Following sheet.
No app feature redesign, no database, no production deployment.
"""
from pathlib import Path
p=Path('index.html')
s=p.read_text('utf8')
before='<meta content="v1398 · a36-safe-get-app-after-ember" name="fc-build"/>'
after='<meta content="v1399 · a36-following-nav-clearance" name="fc-build"/>'
marker='<!-- FEED VIEWER SHEET -->'
if s.count(before)!=1 or s.count(after) or s.count(marker)!=1:
 raise SystemExit('STOP: staging v1398 baseline or Following markup changed')
css="""<style id="fc-a36-following-nav-v1399">
/* The Connections sheet is a modal. Never let persistent primary navigation
   obscure a followed competitor or the View entry action on small screens. */
body:has(#followingSheet.open) #bottomNav {
  visibility: hidden !important;
  pointer-events: none !important;
}
/* Keep the final followed entry clear of the iPhone home indicator. */
#followingSheet.open #followingList {
  padding-bottom: calc(32px + env(safe-area-inset-bottom, 0px)) !important;
}
</style>

"""
s=s.replace(marker,css+marker,1).replace(before,after,1)
assert s.count('id="fc-a36-following-nav-v1399"')==1
p.write_text(s,'utf8')
print('STAGED v1399: Following modal hides primary bottom navigation; preserves touch actions and bottom safe-area padding')
