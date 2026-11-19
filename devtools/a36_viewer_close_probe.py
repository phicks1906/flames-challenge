from pathlib import Path
import re
lines=Path("index.html").read_text("utf8").splitlines()
patterns=[r'function openFeedViewer\(',r'function closeFeedViewer\(',r'function openFeedViewer\w*\(',r'function close\w*Viewer\(',r'id=["\']feedViewer',r'feedViewerOverlay',r'closeFeedViewer\(',r'onclick=["\'][^"\']*closeFeedViewer',r'aria-label=["\'][^"\']*Close[^"\']*["\']']
for pat in patterns:
 ix=[i for i,s in enumerate(lines) if re.search(pat,s,re.I)]
 print("A36_VIEWER_CLOSE_PATTERN",pat,"total",len(ix))
 for i in ix[:10]:
  print("A36_VIEWER_CLOSE_LINE",i+1,lines[i].strip()[:300])
  for j in range(i+1,min(i+3,len(lines))):
   print("A36_VIEWER_CLOSE_NEXT",j+1,lines[j].strip()[:210])
