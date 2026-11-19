from pathlib import Path
import re
lines=Path('index.html').read_text('utf-8').splitlines()
for i,line in enumerate(lines):
 if (i+1>=45225 and i+1<=45262) or (i+1>=45520 and i+1<=45595):
  if len(line)>400: line=line[:400]+' ...'
  print('A36_SETUP_SOURCE',i+1,line.strip())
for label in ['SETUP_VERSION','GUIDE_VERSION','function requiredMode','function shouldPromptOnboarding']:
 inds=[i for i,s in enumerate(lines) if label in s]
 print('A36_SETUP_IDENTIFIER',label,'COUNT',len(inds))
 for i in inds[:6]:print('A36_SETUP_MATCH',i+1,lines[i][:330].strip())
