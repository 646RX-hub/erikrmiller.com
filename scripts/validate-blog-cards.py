#!/usr/bin/env python3
"""
validate-blog-cards.py — CI guard: fail the build if a production article exists
under /blog/ but has no corresponding card (link) on the blog index (/blog/).

A "production article" is any immediate subdirectory of blog/ that contains an
index.html, excluding the taxonomy dir `category/` and dirs beginning with "_" or ".".

An article is "covered" if blog/index.html links to it via any href of the form
  href="slug/"  |  href="./slug/"  |  href="/blog/slug/"   (trailing slash optional)
This counts both standard post-cards and the featured pillar tile.

Intentional omissions may be declared in scripts/blog-card-exemptions.txt
(one slug per line; blank lines and #-comments ignored). If that file is absent
or empty, the check is fully strict.

Exit code 0 = every production article is linked from the blog index (or exempt);
1 = one or more uncovered articles.
Run from the repo root:  python3 scripts/validate-blog-cards.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG = os.path.join(ROOT, "blog")
INDEX = os.path.join(BLOG, "index.html")
EXEMPT_FILE = os.path.join(ROOT, "scripts", "blog-card-exemptions.txt")

EXCLUDE_DIRS = {"category"}  # taxonomy, not an article

def article_slugs():
    slugs = []
    for name in sorted(os.listdir(BLOG)):
        if name in EXCLUDE_DIRS or name.startswith(("_", ".")):
            continue
        d = os.path.join(BLOG, name)
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "index.html")):
            slugs.append(name)
    return slugs

def linked_slugs():
    html = open(INDEX, encoding="utf-8").read()
    linked = set()
    for href in re.findall(r'href="([^"]+)"', html):
        v = href.split("#", 1)[0].split("?", 1)[0]
        if v.startswith("./"):
            v = v[2:]
        if v.startswith("/blog/"):
            v = v[len("/blog/"):]
        v = v.strip("/")
        if v and "/" not in v:
            linked.add(v)
    return linked

def exemptions():
    if not os.path.isfile(EXEMPT_FILE):
        return set()
    out = set()
    for line in open(EXEMPT_FILE, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            out.add(line)
    return out

def main():
    if not os.path.isfile(INDEX):
        print("FAIL: blog/index.html not found", file=sys.stderr)
        return 1
    articles = article_slugs()
    linked = linked_slugs()
    exempt = exemptions()

    missing = [s for s in articles if s not in linked and s not in exempt]
    # hygiene: exemptions that are stale (article gone) or unnecessary (already carded)
    stale = sorted(s for s in exempt if s not in articles)
    unnecessary = sorted(s for s in exempt if s in linked)

    print("Checked %d production article(s) under /blog/." % len(articles))
    print("Linked from blog index: %d ; exempt: %d ; missing: %d"
          % (len([s for s in articles if s in linked]), len(exempt), len(missing)))

    if unnecessary:
        print("NOTE: exemptions no longer needed (article is now carded): "
              + ", ".join(unnecessary))
    if stale:
        print("NOTE: exemptions reference non-existent articles: " + ", ".join(stale))

    if missing:
        print("\nFAIL: the following /blog/ article(s) have no card on /blog/:",
              file=sys.stderr)
        for s in missing:
            print("  - blog/%s/  (add a card to blog/index.html, or add the slug to "
                  "scripts/blog-card-exemptions.txt if intentionally unlisted)" % s,
                  file=sys.stderr)
        return 1

    print("PASS: every production /blog/ article has a corresponding card.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
