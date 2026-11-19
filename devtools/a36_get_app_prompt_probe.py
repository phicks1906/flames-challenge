from pathlib import Path
import re
s=Path('index.html').read_text('utf8').splitlines()
patterns=[r'getAppPrompt',r'openGetApp|showGetApp|maybe.*AppPrompt|Get App',r'\.modal-backdrop\.open',r'fcEmberDailyBriefingV1221',r'const SELECTOR']
for pat in patterns:
 ids=[i for i,l in enumerate(s) if re.search(pat,l,re.I)]
 print('A36_APP_PROMPT_PATTERN',pat,'count',len(ids))
 for i in ids[:20]:
  print('A36_APP_PROMPT_HIT',i+1,repr(s[i].strip()[:360]))
  if pat in (r'getAppPrompt',r'const SELECTOR'):
   for j in range(max(0,i-3),min(len(s),i+8)):
    print('A36_APP_PROMPT_LINE',j+1,repr(s[j].strip()[:350]))
