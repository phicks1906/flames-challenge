#!/usr/bin/env python3
"""A3.6 staging-only browser copy.

Read verified v1396 root index.html and rewrite only its Supabase client URL/key.
Never edits the checked-in root index.html or production data, never logs key.
Public static media assets intentionally remain production-hosted read-only.
"""
from pathlib import Path
import os
import re

src = Path('index.html')
raw = src.read_text(encoding='utf-8')
dest = Path('/tmp/fc-a36-staging-browser/index.html')
staging_url = 'https://pcmobielrhdfzivrwvuu.supabase.co'
staging_key = os.environ.get('FC_A36_STAGING_PUBLISHABLE_KEY', '')
if not staging_key.startswith('sb_publishable_') or len(staging_key) < 35:
    raise SystemExit('STOP: missing valid public staging publishable key')
if raw.count('v1396 · a36-guidelines-before-welcome-guide') != 1:
    raise SystemExit('STOP: unsupported staged build')
url_pattern = re.compile(r'(?m)^(const SUPABASE_URL = )"([^"]+)";$')
key_pattern = re.compile(r'(?m)^(const SUPABASE_KEY = )"([^"]+)";$')
url_matches = list(url_pattern.finditer(raw))
key_matches = list(key_pattern.finditer(raw))
if len(url_matches) != 1 or len(key_matches) != 1:
    raise SystemExit('STOP: expected exactly one Supabase client config pair')
if url_matches[0].group(2) != 'https://sioalvawzayfphwzqctq.supabase.co':
    raise SystemExit('STOP: production source connection target changed')
if len(key_matches[0].group(2)) < 40:
    raise SystemExit('STOP: production client key shape unexpectedly short')
rebound = url_pattern.sub(lambda m: m.group(1)+'"'+staging_url+'";', raw, count=1)
rebound = key_pattern.sub(lambda m: m.group(1)+'"'+staging_key+'";', rebound, count=1)
if rebound.count('const SUPABASE_URL = "'+staging_url+'";') != 1:
    raise SystemExit('STOP: staging URL not bound')
if rebound.count('const SUPABASE_KEY = "'+staging_key+'";') != 1:
    raise SystemExit('STOP: staging public key not bound')
if rebound.count('https://sioalvawzayfphwzqctq.supabase.co/storage/') != raw.count('https://sioalvawzayfphwzqctq.supabase.co/storage/'):
    raise SystemExit('STOP: read-only artwork URLs were altered')
if src.read_text('utf-8') != raw:
    raise SystemExit('STOP: canonical source modified unexpectedly')
dest.parent.mkdir(parents=True, exist_ok=True)
dest.write_text(rebound, encoding='utf-8')
print('PASS A3.6: generated ephemeral v1396 HTML bound to staging Supabase client')
print('PASS A3.6: preserved production-hosted public media links, not production database calls')
print('PASS A3.6: canonical staged root index.html unchanged; keys never logged')
