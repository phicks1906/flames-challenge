#!/usr/bin/env python3
"""Apply A3.6 Part 1 against the exact v1389 baseline on the staging branch.

No database, service worker, or production deployment changes. Fail closed if
the source differs from the inspected baseline or if any anchor is ambiguous.
"""
from pathlib import Path
import hashlib
import re
import sys

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/"index.html"
COMPONENT=ROOT/"devtools/a36_votes_component.html"
BASE_SHA256="423de2ba89ef864f3b0af1bd903845fa839ebe80e59a9481f75b3c01d3b52f3a"
OLD_VERSION='<meta content="v1389 · continuous-championship-medal-rings" name="fc-build"/>'
NEW_VERSION='<meta content="v1390 · a36-vote-history-part1" name="fc-build"/>'
OLD_NEWS='<meta content="Championship gold, silver and bronze portrait rings now form complete, uninterrupted circles." name="fc-whatsnew"/>'
NEW_NEWS='<meta content="Your competitive votes are now listed on your own profile, with a path back to each competition." name="fc-whatsnew"/>'

def main():
    s=INDEX.read_text(encoding="utf-8")
    if hashlib.sha256(s.encode()).hexdigest()!=BASE_SHA256:
        sys.exit("FAILED: canonical v1389 checksum mismatch. Review new source first.")
    component=COMPONENT.read_text(encoding="utf-8")
    if component.count('<script id="fc-a36-v1390-votes-js">')!=1 or component.count('<style id="fc-a36-v1390-votes-css">')!=1:
        sys.exit("FAILED: component is incomplete or ambiguous")
    if "</body>" in component or "<html" in component:
        sys.exit("FAILED: invalid component wrapper")
    for old in (OLD_VERSION, OLD_NEWS, "</body>"):
        if s.count(old)!=1:
            sys.exit(f"FAILED: required unique anchor found {s.count(old)} times")
    if 'fc-a36-v1390-votes-js' in s:
        sys.exit("FAILED: Part 1 already present")
    s=s.replace(OLD_VERSION,NEW_VERSION,1).replace(OLD_NEWS,NEW_NEWS,1)
    s=s.replace("</body>",component+"\n</body>",1)
    INDEX.write_text(s,encoding="utf-8")
    assert s.count('fc-a36-v1390-votes-js')==1
    assert s.count(NEW_VERSION)==1 and OLD_VERSION not in s
    print("STAGED: v1390 Part 1 candidate. New size",len(s),"bytes",len(s.encode()))
    print("STAGED: retained root index.html, script count",len(re.findall(r"<script\b",s)))

if __name__=="__main__":
    main()
