#!/usr/bin/env python3
"""A3.6 read-only Supabase target audit; never print keys or tokens."""
from pathlib import Path
import re
s=Path('index.html').read_text(encoding='utf-8')
hosts=sorted(set(re.findall(r'(?:https?://)?([a-z0-9]{20}\.supabase\.co)',s,re.I)))
for host in hosts:
    role=('STAGING' if host.startswith('pcmobielrhdfzivrwvuu.') else
          'PRODUCTION' if host.startswith('sioalvawzayfphwzqctq.') else 'OTHER')
    print('A36_APP_BACKEND_HOST',role,host)
print('A36_APP_BACKEND_COUNT',len(hosts))
if not hosts:
    print('A36_APP_BACKEND_NOTE: no literal supabase.co URL; may be built dynamically')
