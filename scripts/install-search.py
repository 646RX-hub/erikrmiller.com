#!/usr/bin/env python3
"""
install-search.py

Idempotently wires the Cmd+K search modal into every HTML page on the site.
For each page:
  1. Ensures the GA4 tag (G-LDN7MBR58X) is in <head> — homepage, blog landing,
     and 404 were missing it; this closes that reporting hole as a side effect.
  2. Adds <link rel="stylesheet" href="/assets/search/search.css"> in <head>.
  3. Adds <script src="/assets/search/search.js" defer></script> in <head>.
  4. Adds a <li> with a search trigger button into the main nav <ul class="nav-links">.
  5. On pages with a mobile nav overlay (homepage + blog landing), also adds
     the trigger to <ul class="nav-links-mobile">.
  6. On the homepage only: extends the existing WebSite JSON-LD with a
     potentialAction:SearchAction so Google can render the Sitelinks Searchbox.

All edits check for existing markers before applying, so re-running is safe.

Run from repo root:
    python3 scripts/install-search.py
"""
import re, sys, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# --- Markers (used both to inject and to detect prior installs) -----------
GA_ID = "G-LDN7MBR58X"
GA_BLOCK = f"""<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>
"""

CSS_TAG = '<link rel="stylesheet" href="/assets/search/search.css">'
JS_TAG  = '<script src="/assets/search/search.js" defer></script>'

NAV_TRIGGER_LI = """    <li><button type="button" class="erm-search-trigger" data-erm-search-trigger aria-label="Open search (Cmd+K)"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>Search<kbd>⌘K</kbd></button></li>
"""

MOBILE_TRIGGER_LI = """  <li><button type="button" class="erm-search-trigger" data-erm-search-trigger onclick="closeMobileNav && closeMobileNav();" style="font-size:0.75rem;letter-spacing:0.2em;"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>Search</button></li>
"""

SEARCH_ACTION_JSONLD = """    ,
    {
      "@type": "WebSite",
      "@id": "https://erikrmiller.com/#website-search",
      "url": "https://erikrmiller.com/",
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "https://erikrmiller.com/?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    }"""

# --- Per-edit helpers -----------------------------------------------------
def has(text, marker):
    return marker in text

def inject_before_head_close(html, snippet, marker_check):
    """Insert snippet immediately before </head>, only if marker_check is not in html."""
    if marker_check in html:
        return html, False
    return html.replace("</head>", snippet + "\n</head>", 1), True

def inject_ga(html):
    if GA_ID in html:
        return html, False
    return html.replace("</head>", GA_BLOCK + "</head>", 1), True

def inject_nav_li(html):
    """Insert NAV_TRIGGER_LI inside the first <ul class="nav-links"> ... </ul>,
    immediately before the existing 'Work Together' / nav-cta <li>.
    Idempotent: skipped if 'erm-search-trigger' already in the nav-links block."""
    # Find first <ul class="nav-links"> (not nav-links-mobile)
    pattern = re.compile(
        r'(<ul class="nav-links"[^>]*>)(.*?)(</ul>)',
        re.DOTALL,
    )
    m = pattern.search(html)
    if not m:
        return html, False, "no <ul class=\"nav-links\"> found"
    inner = m.group(2)
    if "erm-search-trigger" in inner:
        return html, False, "already installed"
    # Insert before the nav-cta <li> (Work Together)
    cta_re = re.compile(r'(\s*<li><a [^>]*class="nav-cta"[^>]*>.*?</a></li>)', re.DOTALL)
    new_inner, n = cta_re.subn(NAV_TRIGGER_LI.rstrip("\n") + r"\1", inner, count=1)
    if n == 0:
        # Fallback: append before </ul>
        new_inner = inner + "\n" + NAV_TRIGGER_LI
    new_block = m.group(1) + new_inner + m.group(3)
    new_html = html[:m.start()] + new_block + html[m.end():]
    return new_html, True, None

def inject_mobile_nav_li(html):
    """For pages with <ul class="nav-links-mobile">."""
    pattern = re.compile(
        r'(<ul class="nav-links-mobile"[^>]*>)(.*?)(</ul>)',
        re.DOTALL,
    )
    m = pattern.search(html)
    if not m:
        return html, False, "no mobile nav"
    inner = m.group(2)
    if "erm-search-trigger" in inner:
        return html, False, "already installed"
    cta_re = re.compile(r'(\s*<li><a [^>]*class="nav-cta"[^>]*>.*?</a></li>)', re.DOTALL)
    new_inner, n = cta_re.subn(MOBILE_TRIGGER_LI.rstrip("\n") + r"\1", inner, count=1)
    if n == 0:
        new_inner = inner + "\n" + MOBILE_TRIGGER_LI
    new_block = m.group(1) + new_inner + m.group(3)
    new_html = html[:m.start()] + new_block + html[m.end():]
    return new_html, True, None

def inject_search_action(html):
    """Extend the existing @graph in index.html's WebSite schema with a SearchAction.
    Approach: find the closing ']\n  }\n}\n</script>' of the first ld+json block on
    homepage and inject a new graph node before the closing ]. Idempotent via marker."""
    if '"@id": "https://erikrmiller.com/#website-search"' in html:
        return html, False
    # Find the first ld+json block
    m = re.search(r'(<script type="application/ld\+json">)(.*?)(</script>)', html, re.DOTALL)
    if not m:
        return html, False
    body = m.group(2)
    # Inject before the closing ] of @graph
    # Look for the last "]" that's followed by closing brace of the outer object.
    new_body, n = re.subn(r'(\s*)\]\s*\}\s*$', SEARCH_ACTION_JSONLD + r"\1]\n}", body.rstrip(), count=1)
    if n == 0:
        return html, False
    new_html = html[:m.start()] + m.group(1) + new_body + "\n" + m.group(3) + html[m.end():]
    return new_html, True

# --- Per-page driver ------------------------------------------------------
PAGES_WITH_MOBILE_NAV = {"index.html", "blog/index.html"}
SKIP_FILES = {"blog.html"}  # pure redirect stub

def process(path: Path):
    rel = path.relative_to(ROOT).as_posix()
    if rel in SKIP_FILES:
        return f"  · skipped {rel} (redirect stub)"
    html = path.read_text(encoding="utf-8")
    orig = html
    changes = []

    # 1. GA (only adds where missing)
    html, did = inject_ga(html)
    if did: changes.append("GA4")

    # 2. CSS link (skip if 'search.css' already referenced)
    html, did = inject_before_head_close(html, CSS_TAG, "/assets/search/search.css")
    if did: changes.append("css")

    # 3. JS script
    html, did = inject_before_head_close(html, JS_TAG, "/assets/search/search.js")
    if did: changes.append("js")

    # 4. Nav trigger (main nav)
    html, did, msg = inject_nav_li(html)
    if did: changes.append("nav")
    elif msg and msg != "already installed":
        changes.append(f"nav!{msg}")

    # 5. Mobile nav trigger
    if rel in PAGES_WITH_MOBILE_NAV:
        html, did, msg = inject_mobile_nav_li(html)
        if did: changes.append("mobile-nav")

    # 6. SearchAction JSON-LD (homepage only)
    if rel == "index.html":
        html, did = inject_search_action(html)
        if did: changes.append("schema")

    if html != orig:
        path.write_text(html, encoding="utf-8")
        return f"  ✓ {rel} — {', '.join(changes)}"
    return f"  · {rel} — already up to date"

def main():
    targets = [
        ROOT / "index.html",
        ROOT / "blog.html",
        ROOT / "404.html",
        ROOT / "blog" / "index.html",
        ROOT / "icp" / "index.html",
    ]
    for child in sorted((ROOT / "blog").iterdir()):
        if child.is_dir():
            f = child / "index.html"
            if f.exists():
                targets.append(f)
    for p in targets:
        if not p.exists():
            print(f"  ! missing: {p.relative_to(ROOT)}")
            continue
        print(process(p))

if __name__ == "__main__":
    main()
