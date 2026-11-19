#!/usr/bin/env python3
"""Read-only A3.6 audit: show redacted config definitions, never secret values."""
from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
for pattern in (r'sioalvawzayfphwzqctq\.supabase\.co',r'const\s+SUPABASE_[A-Z_]+\s*=',r'createClient\('):
 found=list(re.finditer(pattern,s))
 print('A36_CONFIG_ANCHOR',pattern,'count',len(found))
 for m in found[:5]:
  before=s[max(0,m.start()-170):m.end()+180]
  before=re.sub(r'eyJ[A-Za-z0-9._-]{30,}','[JWT_REDACTED]',before)
  before=re.sub(r'sb_(?:publishable|secret)_[A-Za-z0-9_-]{12,}','[KEY_REDACTED]',before)
  before=re.sub(r'(?:api[_-]?key|token|secret)\s*[:=]\s*[^\s;]+','[KEY_VALUE_REDACTED]',before,flags=re.I)
  print('  SOURCE_CONTEXT:',repr(before[:320]))
