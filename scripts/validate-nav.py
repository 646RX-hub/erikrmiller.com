#!/usr/bin/env python3
"""
validate-nav.py — CI guard: fail if any production page's navigation drifts from the
single source of truth (partials/nav.html) or is missing the shared nav assets.

Exit code 0 = all production pages identical; 1 = drift detected.
Run from the repo root:  python3 scripts/validate-nav.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTIAL = open(os.path.join(ROOT, "partials/nav.html"), encoding="utf-8").read().strip()
START, END = "<!-- NAV:START -->", "<!-- NAV:END -->"
re_between = re.compile(re.escape(START) + r"(.*?)" + re.escape(END), re.S)

EXCLUDE_NAMES = {"index-icp-working.html", "activation-loop-preview.html"}
EXCLUDE_DIRS  = {"_drafts", ".git", "node_modules", "partials", "scripts"}

def is_production(path, html):
    base = os.path.basename(path)
    if base in EXCLUDE_NAMES: return False
    if path.endswith(".backup"): return False
    if 'http-equiv="refresh"' in html: return False
    return ("nav-logo" in html) or (START in html)

def main():
    failures, checked = [], 0
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if not fn.endswith(".html"): continue
            path = os.path.join(dirpath, fn)
            html = open(path, encoding="utf-8").read()
            if not is_production(path, html): continue
            rel = os.path.relpath(path, ROOT)
            checked += 1
            m = re_between.search(html)
            if not m:
                failures.append((rel, "missing NAV:START/NAV:END markers")); continue
            if m.group(1).strip() != PARTIAL:
                failures.append((rel, "nav markup differs from partials/nav.html")); continue
            if html.count(START) != 1:
                failures.append((rel, "more than one nav block")); continue
            if "/assets/nav/nav.css" not in html:
                failures.append((rel, "missing nav.css link")); continue
            if "/assets/nav/nav.js" not in html:
                failures.append((rel, "missing nav.js script")); continue

    print(f"Validated {checked} production pages against partials/nav.html")
    if failures:
        print(f"\nNAV VALIDATION FAILED — {len(failures)} page(s) drifted:")
        for rel, why in failures: print(f"  ✗ {rel}: {why}")
        sys.exit(1)
    print("PASS — every production page has identical navigation.")
    sys.exit(0)

if __name__ == "__main__":
    main()
