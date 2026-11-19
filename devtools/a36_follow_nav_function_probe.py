from pathlib import Path
s=Path('index.html').read_text('utf8').splitlines()
for i,line in enumerate(s):
 if 'function openFollowingSheet(' in line or 'function closeFollowingSheet(' in line:
  print('A36_FOLLOW_NAV_FUNC',i+1)
  for j in range(max(0,i-3),min(len(s),i+19)):
   print('A36_FOLLOW_NAV_LINE',j+1,repr(s[j][:380]))
