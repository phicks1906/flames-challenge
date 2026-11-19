from pathlib import Path
import re
lines=Path('index.html').read_text('utf-8').splitlines()
patterns=[
 r'fc-ob-theme-preview-v1103',
 r'onboarding_completed_at',
 r'onboarding_version',
 r'function.*[Oo]nboard',
 r'fc-ob-v1103',
 r'onboarding.*completed',
 r'onboarding.*interest',
 r'fc-ob-theme-'
]
for term in patterns:
 inds=[i for i,l in enumerate(lines) if re.search(term,l,re.I)]
 print('A36_ONBOARD_ANCHOR',term,'total',len(inds))
 for i in inds[:8]:
  for j in range(max(0,i-2),min(len(lines),i+4)):
   line=lines[j].strip()
   line=re.sub(r'eyJ[A-Za-z0-9._-]{30,}','[JWT]',line)
   line=re.sub(r'sb_(?:publishable|secret)_[A-Za-z0-9_-]{12,}','[KEY]',line)
   print('A36_ONBOARD_SOURCE',j+1,line[:230])
