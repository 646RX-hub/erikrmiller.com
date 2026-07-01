#!/usr/bin/env python3
"""
validate-search-index.py — CI guard for the client-side search index
(assets/search/search-index.json), the document set consumed by the Cmd+K
search on the site.

Fails the build if the index is malformed, internally inconsistent, references
unpublished (draft) content, or lists a blog post that has no card on the blog
index (/blog/).

Checks:
  1. The file parses cleanly as JSON and has the expected shape
     (a top-level object with an integer "count" and a list "documents").
  2. "count" equals the number of documents.
  3. No indexed document URL references drafts (i.e. contains "_drafts").
  4. Every indexed blog-post URL (/blog/<slug>/) has a card on /blog/,
     using the SAME link-detection rule as validate-blog-cards.py.

Exit code 0 = all checks pass; 1 = one or more failures.
Run from the repo root:  python3 scripts/validate-search-index.py

Testing aid: set SEARCH_INDEX_PATH to point the checks at an alternate file.
When unset (the CI default) the canonical index path is used, so CI behavior
is unchanged.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.environ.get("SEARCH_INDEX_PATH",
                       os.path.join(ROOT, "assets", "search", "search-index.json"))
BLOG_INDEX = os.path.join(ROOT, "blog", "index.html")


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


# ---- Check 1: parses cleanly + expected shape ----
try:
    with open(INDEX, encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    fail(f"search index not found at {INDEX}")
except json.JSONDecodeError as e:
    fail(f"search index is not valid JSON: {e}")

if not isinstance(data, dict) or "count" not in data or "documents" not in data:
    fail('search index must be a JSON object with "count" and "documents" keys')
docs = data["documents"]
if not isinstance(docs, list):
    fail('"documents" must be a list')
if not isinstance(data["count"], int):
    fail('"count" must be an integer')

# ---- Check 2: count matches documents length ----
if data["count"] != len(docs):
    fail(f'"count" ({data["count"]}) does not match number of documents ({len(docs)})')

# ---- Check 3: no draft URLs ----
drafts = [d.get("url", "") for d in docs if "_drafts" in d.get("url", "")]
if drafts:
    fail("draft/unpublished URL(s) present in search index:\n  " + "\n  ".join(drafts))


# ---- Check 4: every indexed blog post is carded on /blog/ ----
# Mirror validate-blog-cards.py's link detection so the two guards agree.
def carded_slugs():
    html = open(BLOG_INDEX, encoding="utf-8").read()
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


carded = carded_slugs()
uncarded = []
for d in docs:
    url = d.get("url", "").split("#", 1)[0]
    m = re.fullmatch(r"/blog/([^/]+)/", url)
    if not m:
        continue                     # not a single-slug blog post (hub/anchor/other section)
    slug = m.group(1)
    if slug == "category":           # taxonomy, not an article
        continue
    if slug not in carded:
        uncarded.append(url)
if uncarded:
    fail("indexed blog URL(s) with no card on /blog/:\n  " + "\n  ".join(sorted(set(uncarded))))

print(f"PASS: search index valid — {data['count']} documents, count matches, "
      f"no drafts, all blog entries carded.")
