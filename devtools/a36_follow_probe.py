#!/usr/bin/env python3
from pathlib import Path
import re
lines=Path('index.html').read_text(encoding='utf-8').splitlines()
patterns=[
 r'function loadFollows',r'function renderFollowing',r'function loadFollowing',
 r'function switchFeedTab',r'function renderFeed',r'function renderFollowingAvatar',
 r'function openFollowing',r'function loadFollow',r'followingAvatarScroll',
 r'feedTab\s*===\s*[\'"]following',r'feedTab\s*==\s*[\'"]following',
 r'function openFeedViewer',r'function renderProfileSheet',r'function renderProfileTab',
 r'function switchFollowTab',r'function loadFollowSheet',r'function renderFollow',
 r'function toggleFollow'
]
seen=set()
for p in patterns:
 matches=[i for i,l in enumerate(lines) if re.search(p,l,re.I)]
 print('PATTERN',p,'TOTAL',len(matches),'FIRST',','.join(map(lambda n:str(n+1),matches[:20])))
 for i in matches[:2]:
  for j in range(max(i-5,0),min(i+18,len(lines))):
   if j not in seen:
    print(f'{j+1}: {lines[j][:230]}');seen.add(j)
