from pathlib import Path
import re
lines=Path('index.html').read_text('utf8').splitlines()
for p in [r'#followingSheet',r'\bid="bottomNav"',r'#bottomNav',r'\.bottom-nav',r'\.modal-backdrop\s*\{',r'\.modal-backdrop\.open',r'fc-dialog-root-v1100']:
 hits=[i for i,s in enumerate(lines) if re.search(p,s,re.I)]
 print('A36_LAYOUT_PATTERN',p,'count',len(hits))
 for i in hits[:15]:
  print('A36_LAYOUT_LINE',i+1,repr(lines[i].strip()[:400]))
  if p==r'#followingSheet' or p==r'\.modal-backdrop\s*\{':
   for j in range(i+1,min(i+8,len(lines))):print('A36_LAYOUT_CONTEXT',j+1,repr(lines[j].strip()[:300]))

for a,b in [(6168,6193),(44478,44504),(11004,11023),(1413,1425)]:
 print('A36_EXACT_LAYOUT',a,b)
 for i in range(a-1,b):
  print('A36_LAYOUT_EXACT_LINE',i+1,repr(lines[i].strip()[:360]))
