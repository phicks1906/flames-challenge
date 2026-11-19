from pathlib import Path
import re
s=Path('index.html').read_text('utf-8').splitlines()
patterns=[
r'id=.*guidelinesModal',
r'guidelinesModal',
r'function.*[Gg]uidelines',
r'guidelines.*accept',
r'accept.*guidelines',
r'guidelines.*agree',
r'guidelines.*version'
]
for pattern in patterns:
 inds=[i for i,l in enumerate(s) if re.search(pattern,l,re.I)]
 print('A36_GUIDELINES_PATTERN',pattern,'MATCHES',len(inds))
 for i in inds[:12]:
  print('A36_GUIDELINES_LINE',i+1,' '.join(s[i].strip().split())[:275])
  for line in s[i+1:i+3]:
   print('A36_GUIDELINES_CONTEXT',' '.join(line.strip().split())[:220])

for a,b in [(12860,12912),(45575,45634),(28982,29005)]:
 print('A36_GUIDELINES_SECTION',a,b)
 for i in range(a-1,min(b,len(s))):
  print('A36_GUIDELINES_SOURCE',i+1,' '.join(s[i].strip().split())[:340])
for i,line in enumerate(s):
 if 'fcMaybeOpenOptionalGuideV1103' in line:
  print('A36_GUIDELINES_OPTIONAL',i+1,' '.join(line.split())[:360])
