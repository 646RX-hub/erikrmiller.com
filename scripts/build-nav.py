#!/usr/bin/env python3
"""
build-nav.py — inject the single-source-of-truth navigation into every production page.

Source of truth:
  - partials/nav.html        (canonical nav markup, root-relative links)
  - assets/nav/nav.css       (canonical nav styles, extracted from homepage)
  - assets/nav/nav.js        (canonical nav behavior, extracted from homepage)

For every production HTML page this script:
  1. Replaces the nav region (between <!-- NAV:START --> / <!-- NAV:END -->, or the
     existing <nav ...nav-logo...> block + trailing mobile <ul> on first run) with the partial.
  2. Ensures <link rel="stylesheet" href="/assets/nav/nav.css"> is in <head>.
  3. Ensures <script src="/assets/nav/nav.js" defer></script> is before </body>.

Run from the repo root:  python3 scripts/build-nav.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTIAL = open(os.path.join(ROOT, "partials/nav.html"), encoding="utf-8").read().strip()
START, END = "<!-- NAV:START -->", "<!-- NAV:END -->"
BLOCK = f"{START}\n{PARTIAL}\n{END}"
CSS_LINK = '<link rel="stylesheet" href="/assets/nav/nav.css">'
JS_TAG   = '<script src="/assets/nav/nav.js" defer></script>'

EXCLUDE_NAMES = {"index-icp-working.html", "activation-loop-preview.html"}
EXCLUDE_DIRS  = {"_drafts", ".git", "node_modules", "partials", "scripts"}

re_markers = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
re_nav     = re.compile(r"<nav\b[^>]*>.*?</nav>", re.S)
re_logo    = "nav-logo"

def is_production(path, html):
    base = os.path.basename(path)
    if base in EXCLUDE_NAMES: return False
    if path.endswith(".backup"): return False
    if 'http-equiv="refresh"' in html: return False          # redirect stub
    return (re_logo in html) or (START in html)

def find_region(html):
    """Return (start, end) of the existing nav region on first run, else None."""
    for m in re_nav.finditer(html):
        if re_logo in m.group(0):
            end = m.end()
            tail = html[end:]
            mob = re.match(r"\s*(?:<!--.*?-->\s*)?<ul\b[^>]*nav-links-mobile[^>]*>.*?</ul>", tail, re.S)
            if mob: end += mob.end()
            return (m.start(), end)
    return None

def ensure_asset(html, needle, inject, before_tag):
    if needle in html: return html, False
    idx = html.rfind(before_tag)
    if idx == -1: return html, False
    return html[:idx] + inject + "\n" + html[idx:], True

def process(path):
    html = open(path, encoding="utf-8").read()
    if not is_production(path, html): return None
    orig = html

    if START in html:
        html = re_markers.sub(BLOCK, html, count=1)
    else:
        region = find_region(html)
        if not region: return ("SKIP-no-nav", path)
        html = html[:region[0]] + BLOCK + html[region[1]:]

    html, _ = ensure_asset(html, "/assets/nav/nav.css", CSS_LINK, "</head>")
    html, _ = ensure_asset(html, "/assets/nav/nav.js", JS_TAG, "</body>")

    if html != orig:
        open(path, "w", encoding="utf-8").write(html)
        return ("UPDATED", path)
    return ("OK", path)

def main():
    updated, ok, skipped = [], [], []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]
        for fn in filenames:
            if not fn.endswith(".html"): continue
            r = process(os.path.join(dirpath, fn))
            if r is None: continue
            rel = os.path.relpath(r[1], ROOT)
            if r[0] == "UPDATED": updated.append(rel)
            elif r[0] == "OK": ok.append(rel)
            else: skipped.append(rel)
    print(f"Updated: {len(updated)}  |  Already current: {len(ok)}  |  No-nav skipped: {len(skipped)}")
    for f in sorted(updated): print("  UPDATED  ", f)
    for f in sorted(skipped): print("  SKIPPED  ", f)

if __name__ == "__main__":
    main()
