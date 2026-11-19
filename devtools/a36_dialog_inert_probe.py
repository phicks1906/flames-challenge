from pathlib import Path
import re
s=Path('index.html').read_text('utf-8').splitlines()
patterns={
 'dialog_inert':r'fc-dialog-root-v1100|fc-dialog-open-v1100|\.inert\s*=|setAttribute\(["\']inert|removeAttribute\(["\']inert',
 'guidelines':r'guidelinesModal|acknowledgeGuidelines|guidelinesAcked',
 'dialog_open':r'function\s+fc.*Dialog|MutationObserver.*dialog|dialog.*top.layer|showModal\(|\.showModal\(',
 'css_root':r'html\s*\{|body\s*\{|pointer-events\s*:\s*none|inert\s*\{',
}
for label,pattern in patterns.items():
 hits=[i for i,line in enumerate(s) if re.search(pattern,line,re.I)]
 print('A36_DIALOG_PATTERN',label,'COUNT',len(hits))
 for i in hits[:65 if label=='dialog_inert' else 16]:
  t=s[i].strip()
  print('A36_DIALOG',label,'LINE',i+1,repr(t[:380]))
  if label in ('dialog_inert','dialog_open'):
   for j in range(i+1,min(i+3,len(s))):
    print('A36_DIALOG_CONTEXT',j+1,repr(s[j].strip()[:320]))
