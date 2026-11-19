from pathlib import Path
import re
s=Path('index.html').read_text('utf-8').splitlines()
patterns=[
r'id=["\\']guidelinesModal["\\']',
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
