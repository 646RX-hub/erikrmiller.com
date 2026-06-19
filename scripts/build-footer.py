#!/usr/bin/env python3
"""
build-footer.py — inject the single-source-of-truth footer into every production page.

Mirrors scripts/build-nav.py. Source of truth:
  - partials/footer.html       (canonical footer markup, root-relative links)
  - assets/footer/footer.css   (canonical footer styles, extracted from homepage)

For every production HTML page this script:
  1. Replaces the footer region (between <!-- FOOTER:START --> / <!-- FOOTER:END -->,
     or the existing <footer ...class="ft"...> block on first run) with the partial.
  2. Ensures <link rel="stylesheet" href="/assets/footer/footer.css"> is in <head>
     (inserted just before </head> so it loads last and governs the footer).

Run from the repo root:  python3 scripts/build-footer.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTIAL = open(os.path.join(ROOT, "partials/footer.html"), encoding="utf-8").read().strip()
START, END = "<!-- FOOTER:START -->", "<!-- FOOTER:END -->"
BLOCK = f"{START}\n{PARTIAL}\n{END}"
CSS_LINK = '<link rel="stylesheet" href="/assets/footer/footer.css">'

EXCLUDE_NAMES = {"index-icp-working.html", "activation-loop-preview.html"}
EXCLUDE_DIRS  = {"_drafts", ".git", "node_modules", "partials", "scripts"}

re_markers = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
re_footer  = re.compile(r"<footer\b[^>]*>.*?</footer>", re.S)

def is_production(path, html):
    base = os.path.basename(path)
    if base in EXCLUDE_NAMES: return False
    if path.endswith(".backup"): return False
    if 'http-equiv="refresh"' in html: return False          # redirect stub
    return ('class="ft"' in html) or (START in html)

def find_region(html):
    """Return (start, end) of the existing canonical footer (the <footer> that
    carries the .ft layout) on first run, else None."""
    for m in re_footer.finditer(html):
        if 'class="ft"' in m.group(0):
            return (m.start(), m.end())
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
        if not region: return ("SKIP-no-footer", path)
        html = html[:region[0]] + BLOCK + html[region[1]:]

    html, _ = ensure_asset(html, "/assets/footer/footer.css", CSS_LINK, "</head>")

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
    print(f"Updated: {len(updated)}  |  Already current: {len(ok)}  |  No-footer skipped: {len(skipped)}")
    for f in sorted(updated): print("  UPDATED  ", f)
    for f in sorted(skipped): print("  SKIPPED  ", f)

if __name__ == "__main__":
    main()
