#!/usr/bin/env python3
"""
validate-type.py — regression guard for supporting label typography.

NARROW BY DESIGN. This does not police the whole site's typography. It exists to
stop the one failure mode we actually hit: a new article copying an old page's
CSS and re-introducing undersized supporting labels.

FAILS on:
  1. A production page missing the assets/type/type.css link.
  2. A page re-declaring a GOVERNED label class below the 13px floor with
     !important (which would defeat the shared layer).

REPORTS (does not fail) legacy ungoverned labels below 13px, so the backlog stays
visible without forcing a site-wide redesign. Headings, lede, body and navigation
are out of scope entirely — see docs/ERM-TYPOGRAPHY-STANDARD.md.
"""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TYPE_CSS = ROOT / "assets" / "type" / "type.css"
LINK = '<link rel="stylesheet" href="/assets/type/type.css">'
FLOOR = 13.0
SKIP = {"_drafts", "node_modules", ".git", "visual-library", "partials"}

def production(p: Path) -> bool:
    if any(x in SKIP for x in p.parts): return False
    n = p.name
    return not (n.endswith((".bak", ".backup")) or ".pre-" in n
                or "-working" in n or "-preview" in n or n == "404.html")

def governed() -> set:
    css = re.sub(r"/\*.*?\*/", "", TYPE_CSS.read_text(encoding="utf-8"), flags=re.S)
    out = set()
    for m in re.finditer(r"([^{}@]+)\{", css):
        for s in m.group(1).replace("\n", ",").split(","):
            s = s.strip()
            if s and s[0] in ".[#": out.add(s)
    return out

def main() -> int:
    if not TYPE_CSS.exists():
        print("FAIL: assets/type/type.css missing — the supporting-label SSOT."); return 1
    gov = governed(); missing = []; defeated = []; legacy = set(); pages = 0
    for f in sorted(ROOT.rglob("*.html")):
        if not production(f): continue
        html = f.read_text(encoding="utf-8", errors="replace")
        if "<style>" not in html and 'http-equiv="refresh"' in html: continue
        pages += 1
        if LINK not in html: missing.append(str(f.relative_to(ROOT)))
        css = re.sub(r"/\*.*?\*/", "",
                     "\n".join(re.findall(r"<style>(.*?)</style>", html, re.S)), flags=re.S)
        for m in re.finditer(r"([^{}]*)\{([^{}]*)\}", css):
            body = m.group(2).replace(" ", "")
            if "text-transform:uppercase" not in body: continue
            fs = re.search(r"font-size:([\d.]+)rem(!important)?", body)
            if not fs: continue
            px, bang = float(fs.group(1)) * 16, bool(fs.group(2))
            if px >= FLOOR: continue
            for sel in [x.strip() for x in m.group(1).replace("\n", ",").split(",")]:
                if not sel or sel.startswith("@"): continue
                if sel in gov:
                    if bang:
                        defeated.append((str(f.relative_to(ROOT)), sel, round(px, 2)))
                else:
                    legacy.add((sel, round(px, 2)))

    print(f"Checked {pages} production pages. Governed label selectors: {len(gov)}.")
    if missing:
        print(f"FAIL: {len(missing)} page(s) missing the type.css link:")
        for p in missing[:12]: print("   ", p)
    if defeated:
        print(f"FAIL: {len(defeated)} page-level !important override(s) defeating the shared layer:")
        for p, s, px in defeated[:12]: print(f"    {px:5.2f}px  {s}  in {p}")
        print("  Fix: remove the page-level rule; change the token in assets/type/type.css.")
    if legacy:
        print(f"NOTE: {len(legacy)} legacy ungoverned label selector(s) still below {FLOOR:.0f}px.")
        print("      Out of scope for this release; tracked for a future pass. Not a failure.")
    if missing or defeated: return 1
    print("PASS: shared layer linked and not overridden.")
    return 0
if __name__ == "__main__": sys.exit(main())
