from pathlib import Path
import re
s=Path('index.html').read_text('utf8').splitlines()
pats=[r'function (?:open|show|load|render)\w*(?:Profile|Following|Votes|Result)\w*\s*\(',r'fcA36VotesTab',r'id=["\'](?:profileSheet|followingSheet|followingList|psContent|psTabs)["\']',r'data-pstab',r'openProfileSheet\s*\(',r'openFollowingSheet\s*\(']
for p in pats:
 matches=[i for i,l in enumerate(s) if re.search(p,l,re.I)]
 print('A36_FLOW_PATTERN',p,'COUNT',len(matches))
 for i in matches[:12]:
  print('A36_FLOW_LINE',i+1, ' '.join(s[i].strip().split())[:240])
  for l in s[i+1:i+4]:
   print('A36_FLOW_NEXT',' '.join(l.strip().split())[:220])
