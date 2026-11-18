#!/usr/bin/env python3
"""FlamesChallenge source locator, guarded patcher, and structural validator.

All operations act locally on the checked-out canonical index.html.
They never push or deploy. Python 3.11+; Node.js needed for JS syntax checks.
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / "index.html"
OUT = ROOT / ".fc-tools" / "source-map.json"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def source():
    return HTML.read_text(encoding="utf-8")

def location(text, offset):
    return text.count("\n", 0, offset) + 1

def locate(text, pattern, max_results=1000):
    matches = []
    for m in re.finditer(pattern, text, re.MULTILINE):
        matches.append({"line": location(text, m.start()), "symbol": m.group(0)[:180].strip()})
        if len(matches) >= max_results:
            break
    return matches

PATTERNS = {
    "functions": r"\b(?:async\s+)?function\s+[A-Za-z_$][\w$]*\s*\(",
    "classes": r"\bclass\s+[A-Za-z_$][\w$]*",
    "event_listeners": r"\.addEventListener\s*\(\s*['\"][^'\"]+",
    "selectors": r"^\s*[.#][\w\-][^{\n]{0,140}\s*\{",
    "sections": r"<!--\s*[^>\n]{3,140}\s*-->",
}

def map_source(args):
    text = source()
    catalog = {key: locate(text, pat) for key, pat in PATTERNS.items()}
    result = {
        "file": "index.html", "sha256": digest(text.encode()),
        "characters": len(text), "lines": text.count("\n") + 1,
        "patterns": catalog
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"file": str(OUT.relative_to(ROOT)), "sha256": result["sha256"],
                      "lines": result["lines"],
                      "counts": {k: len(v) for k, v in catalog.items()}}))

def find(args):
    text = source()
    if not args.literal:
        raise ValueError("Provide a non-empty literal search string")
    matches = list(re.finditer(re.escape(args.literal), text))
    print(json.dumps({"matches": len(matches), "locations": [
        {"line": location(text, m.start()),
         "context": text[max(0, m.start()-args.context):m.end()+args.context]}
        for m in matches[:args.limit]
    ]}, indent=2))
    if not matches:
        sys.exit(2)

def patch(args):
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    if set(spec) - {"expected_sha256", "edits"}:
        raise ValueError("Unrecognized patch specification fields")
    edits = spec.get("edits")
    if not isinstance(edits, list) or not edits:
        raise ValueError("edits must be a nonempty list")
    text = source()
    if spec.get("expected_sha256") and digest(text.encode()) != spec["expected_sha256"]:
        raise ValueError("Source checksum mismatch; refresh patch against current source")
    original = text
    for i, edit in enumerate(edits, 1):
        if not isinstance(edit, dict) or set(edit) != {"old", "new"}:
            raise ValueError(f"Edit {i} requires only old and new")
        old, new = edit["old"], edit["new"]
        if not isinstance(old, str) or not isinstance(new, str) or not old or old == new:
            raise ValueError(f"Edit {i} has invalid or identical old/new")
        count = text.count(old)
        if count != 1:
            raise ValueError(f"Edit {i}: expected exactly one old anchor, found {count}")
        text = text.replace(old, new, 1)
    if text == original:
        raise ValueError("No change")
    if args.write:
        HTML.write_text(text, encoding="utf-8")
    print(json.dumps({"mode": "write" if args.write else "dry-run",
                      "edits": len(edits), "before": digest(original.encode()),
                      "after": digest(text.encode()), "delta_chars": len(text)-len(original)}))

def blocks(text, tag):
    pattern = re.compile(r"<" + tag + r"\b([^>]*)>(.*?)</" + tag + r"\s*>",
                         re.IGNORECASE | re.DOTALL)
    return list(pattern.finditer(text))

def validate(args):
    text = source()
    failures = []
    meta = re.findall(r'<meta\s+name=["\']fc-build["\'][^>]*>', text, re.IGNORECASE)
    if len(meta) != 1:
        failures.append(f"Expected one fc-build meta tag, found {len(meta)}")
    if re.search(r'>\s*Check for updates\s*<', text, re.IGNORECASE):
        failures.append("Manual Check for updates UI detected")
    scripts = blocks(text, "script")
    checked = skipped = 0
    for i, m in enumerate(scripts, 1):
        attributes = m.group(1)
        if re.search(r'\bsrc\s*=', attributes, re.I) or re.search(
            r'\btype\s*=\s*["\'](?:application/json|importmap|text/template|text/x-template)["\']', attributes, re.I
        ):
            skipped += 1
            continue
        code = m.group(2)
        if not code.strip():
            continue
        mode = "--input-type=module" if re.search(
            r'\btype\s*=\s*["\']module["\']', attributes, re.I
        ) else None
        cmd = ["node"]
        if mode: cmd.append(mode)
        cmd.extend(["--check", "-"])
        process = subprocess.run(cmd, input=code, text=True, capture_output=True)
        checked += 1
        if process.returncode:
            failures.append(f"JS block {i}, opening at line {location(text, m.start())}: "
                            + process.stderr[-500:])
    # A full CSS parser is preferable to naive brace counting; do not pretend
    # that literal braces in strings/data URIs constitute CSS errors.
    styles = blocks(text, "style")
    result = {"fc_build_meta_count": len(meta), "script_blocks": len(scripts),
              "javascript_checked": checked, "javascript_skipped": skipped,
              "style_blocks": len(styles), "css_parse_verified": False,
              "failures": failures}
    print(json.dumps(result, indent=2))
    if failures: sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("map").set_defaults(func=map_source)
    s = sub.add_parser("find")
    s.add_argument("literal")
    s.add_argument("--context", type=int, default=80)
    s.add_argument("--limit", type=int, default=12)
    s.set_defaults(func=find)
    s = sub.add_parser("patch")
    s.add_argument("spec", help="JSON containing optional expected_sha256 and ordered edits")
    s.add_argument("--write", action="store_true", help="Actually modify index.html; default dry run")
    s.set_defaults(func=patch)
    sub.add_parser("validate").set_defaults(func=validate)
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
