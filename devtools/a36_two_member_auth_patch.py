#!/usr/bin/env python3
"""A3.6 staging E2E: keep only two supported authenticated fixtures.
Edits test harness locally in CI; canonical application remains unchanged.
"""
from pathlib import Path
p=Path('devtools/a36_auth_signup_and_e2e.js')
s=p.read_text('utf-8')
pairs=[
("['voter','competitor1','competitor2']","['voter','competitor1']"),
("if(members.length<2)throw Error('Insufficient supported Auth signups for voter+competitor');",
 "if(members.length!==2)throw Error('Two real authenticated members required');"),
("'required_requested=3'","'required_requested=2'")
]
for old,new in pairs:
 if s.count(old)!=1:
  raise SystemExit('STOP: staging test anchor mismatch')
 s=s.replace(old,new,1)
p.write_text(s,'utf-8')
print('PASS: E2E harness restricted to two hosted-Auth signup attempts')
