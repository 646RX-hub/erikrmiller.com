#!/usr/bin/env python3
"""
install-type.py — link the shared typography layer on every production page.

assets/type/type.css is the SSOT for label, navigation, and button typography.
It must load AFTER each page's inline <style> so it governs without per-page
overrides. Idempotent. Re-run after adding a page.
"""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
LINK = '<link rel="stylesheet" href="/assets/type/type.css">'
SKIP = {"_drafts", "node_modules", ".git", "visual-library", "partials"}

def production(p: Path) -> bool:
    if any(x in SKIP for x in p.parts): return False
    n = p.name
    return not (n.endswith((".bak", ".backup")) or ".pre-" in n
                or "-working" in n or "-preview" in n or n == "404.html")

def main() -> int:
    added = present = skipped = 0
    for f in sorted(ROOT.rglob("*.html")):
        if not production(f): continue
        html = f.read_text(encoding="utf-8", errors="replace")
        if "<style>" not in html and 'http-equiv="refresh"' in html:
            skipped += 1; continue          # redirect stub: no styles to govern
        if LINK in html:
            present += 1; continue
        last = None
        for last in re.finditer(r'<link rel="stylesheet" href="/assets/[^"]+">', html): pass
        if last:
            html = html[:last.end()] + "\n" + LINK + html[last.end():]
        else:
            m = re.search(r"</style>", html)
            if not m: skipped += 1; continue
            html = html[:m.end()] + "\n" + LINK + html[m.end():]
        f.write_text(html, encoding="utf-8"); added += 1
    print(f"type.css — added {added}, already present {present}, skipped {skipped}")
    return 0
if __name__ == "__main__": sys.exit(main())
