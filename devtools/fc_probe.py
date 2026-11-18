#!/usr/bin/env python3
"""Print bounded, line-numbered matching source excerpts in CI logs, never the full app."""
import argparse, re
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "index.html"
DEFAULT = ["entry_votes", "state.myVotes", "You", "Following", "Votes",
           "myVotes", "renderYou", "challenge_results", "voteHistory"]

def main():
    p=argparse.ArgumentParser()
    p.add_argument("patterns", nargs="*", default=DEFAULT)
    p.add_argument("--before", type=int, default=6)
    p.add_argument("--after", type=int, default=12)
    p.add_argument("--max-matches", type=int, default=10)
    p.add_argument("--max-line-chars", type=int, default=230)
    a=p.parse_args()
    lines=SOURCE.read_text(encoding="utf-8").splitlines()
    for pat in a.patterns:
        indices = [i for i,line in enumerate(lines) if re.search(re.escape(pat), line, re.I)]
        print(f"\n=== {pat!r} count={len(indices)} showing={min(len(indices), a.max_matches)} ===")
        for i in indices[:a.max_matches]:
            lo=max(0,i-a.before); hi=min(len(lines), i+a.after+1)
            print(f"--- matched line {i+1} ---")
            for j in range(lo,hi):
                line=lines[j]
                print(f"{j+1}: {line[:a.max_line_chars]}"+(" [truncated]" if len(line)>a.max_line_chars else ""))
if __name__=="__main__": main()
