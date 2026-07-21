#!/usr/bin/env python3
"""
build-search-index.py

Walks the static site and produces /assets/search/search-index.json,
the document set consumed by the Cmd+K client-side search.

Indexes:
  - Each post in /blog/<slug>/index.html (one document per post)
  - The long-form /icp/ guide (one document for the page,
    plus one document per H2 anchor inside it for jump-to-section results)
  - Top-level homepage sections (one document per <section id="..."> on /)

Re-run after publishing new content:
    python3 scripts/build-search-index.py

The JSON file is keyed for MiniSearch: id, url, type, title, description,
tags, headings, body, date. The runtime is responsible for tokenization,
weighting, and snippet generation — we just give it clean text.
"""
import html as _html
import json, os, re, sys
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT  = ROOT / "assets" / "search" / "search-index.json"

# ---------- HTML helpers ----------
class TextExtractor(HTMLParser):
    """Collects visible text, dropping <script>/<style>/<nav>/<footer>."""
    SKIP = {"script", "style", "nav", "footer", "noscript", "svg"}
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip_depth = 0
    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip_depth += 1
    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip_depth > 0:
            self.skip_depth -= 1
    def handle_data(self, data):
        if self.skip_depth == 0:
            self.parts.append(data)
    def text(self):
        s = " ".join(self.parts)
        s = re.sub(r"\s+", " ", s).strip()
        return s

def extract_text(html: str) -> str:
    p = TextExtractor()
    p.feed(html)
    return p.text()

def meta(html: str, name: str) -> str:
    # name attr OR property attr (Open Graph)
    m = re.search(
        rf'<meta\s+(?:name|property)=["\']{re.escape(name)}["\']\s+content=["\']([^"\']*)["\']',
        html, re.I,
    )
    if m: return m.group(1).strip()
    m = re.search(
        rf'<meta\s+content=["\']([^"\']*)["\']\s+(?:name|property)=["\']{re.escape(name)}["\']',
        html, re.I,
    )
    return m.group(1).strip() if m else ""

def title_of(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

def first_h1(html: str) -> str:
    m = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.I | re.S)
    if not m: return ""
    # Replace tags with a space (not nothing) so <br> and inline tags do not
    # weld adjacent words together, then decode entities (&nbsp;, &rsquo;, ...)
    # and collapse the resulting whitespace.
    text = re.sub(r"<[^>]+>", " ", m.group(1))
    return re.sub(r"\s+", " ", _html.unescape(text)).strip()

def all_headings(html: str) -> list[str]:
    hs = re.findall(r"<h[2-3][^>]*>(.*?)</h[2-3]>", html, re.I | re.S)
    out = []
    for h in hs:
        t = re.sub(r"<[^>]+>", " ", h)
        out.append(re.sub(r"\s+", " ", _html.unescape(t)).strip())
    return out

def body_of(html: str) -> str:
    # Strip head entirely; we only want main content text.
    body_m = re.search(r"<body[^>]*>(.*)</body>", html, re.I | re.S)
    body = body_m.group(1) if body_m else html
    return extract_text(body)

# ---------- Document builders ----------
def doc_for_blog_post(post_dir: Path) -> dict | None:
    f = post_dir / "index.html"
    if not f.exists(): return None
    html = f.read_text(encoding="utf-8", errors="replace")
    slug = post_dir.name
    title = first_h1(html) or title_of(html).split("|")[0].strip()
    desc  = meta(html, "description")
    tag_m = re.search(r'<div class="blog-tag"[^>]*>(.*?)</div>', html, re.I | re.S)
    tag   = re.sub(r"<[^>]+>", "", tag_m.group(1)).strip() if tag_m else ""
    date_m= re.search(r'(\d{4}-\d{2}-\d{2})', meta(html, "article:published_time") or "")
    date  = date_m.group(1) if date_m else ""
    body  = body_of(html)
    # cap body length to keep the index lean
    body  = body[:8000]
    return {
        "id":    f"blog/{slug}",
        "url":   f"/blog/{slug}/",
        "type":  "post",
        "title": title,
        "description": desc,
        "tags":  tag,
        "headings": " · ".join(all_headings(html)[:8]),
        "body":  body,
        "date":  date,
    }

def docs_for_icp(icp_file: Path) -> list[dict]:
    html = icp_file.read_text(encoding="utf-8", errors="replace")
    title = first_h1(html) or "ICP Development: The Complete Guide"
    desc  = meta(html, "description")
    body  = body_of(html)[:10000]
    docs = [{
        "id": "icp",
        "url": "/icp/",
        "type": "guide",
        "title": title,
        "description": desc,
        "tags": "ICP · Framework Guide",
        "headings": " · ".join(all_headings(html)[:12]),
        "body": body,
        "date": "",
    }]
    # Jump-to-section docs for each H2 with an id.
    for m in re.finditer(
        r'<h2[^>]*\bid=["\']([^"\']+)["\'][^>]*>(.*?)</h2>',
        html, re.I | re.S
    ):
        anchor = m.group(1)
        h_text = re.sub(r"<[^>]+>", "", m.group(2)).strip()
        if not h_text: continue
        docs.append({
            "id": f"icp#{anchor}",
            "url": f"/icp/#{anchor}",
            "type": "section",
            "title": h_text,
            "description": f"Section of ICP Development: The Complete Guide",
            "tags": "ICP · Section",
            "headings": "",
            "body": "",  # title carries the weight; body is too noisy at section level
            "date": "",
        })
    return docs

def docs_for_homepage(home_file: Path) -> list[dict]:
    html = home_file.read_text(encoding="utf-8", errors="replace")
    docs = []
    # The homepage itself, as a top-level result.
    docs.append({
        "id": "home",
        "url": "/",
        "type": "page",
        "title": "Erik R. Miller — Marketing Leader. Builder. Operator.",
        "description": meta(html, "description"),
        "tags": "Home",
        "headings": "",
        "body": "Senior B2B marketing executive and fractional CMO. Built a $354M revenue marketing function across 4 continents. Based in New York.",
        "date": "",
    })
    # Section anchors.
    for m in re.finditer(
        r'<section[^>]*\bid=["\']([^"\']+)["\'][^>]*>(.*?)</section>',
        html, re.I | re.S
    ):
        sid = m.group(1)
        if sid in {"main-content"}: continue
        body = m.group(2)
        h = re.search(r"<h[12][^>]*>(.*?)</h[12]>", body, re.I | re.S)
        if not h: continue
        h_text = re.sub(r"<[^>]+>", " ", h.group(1))
        h_text = re.sub(r"\s+", " ", _html.unescape(h_text)).strip()
        if not h_text: continue
        # Surrounding paragraph or kicker for description
        kicker_m = re.search(r'class=["\']kicker[^"\']*["\'][^>]*>(.*?)<', body, re.I | re.S)
        kicker = re.sub(r"<[^>]+>", "", kicker_m.group(1)).strip() if kicker_m else ""
        snippet = re.sub(r"<[^>]+>", " ", body)
        snippet = re.sub(r"\s+", " ", snippet).strip()[:600]
        docs.append({
            "id": f"home#{sid}",
            "url": f"/#{sid}",
            "type": "section",
            "title": h_text,
            "description": kicker,
            "tags": "Home · Section",
            "headings": "",
            "body": snippet,
            "date": "",
        })
    return docs

# ---------- Main ----------
def main():
    docs = []

    # Homepage sections
    home = ROOT / "index.html"
    if home.exists():
        docs.extend(docs_for_homepage(home))

    # ICP guide + sections
    icp = ROOT / "icp" / "index.html"
    if icp.exists():
        docs.extend(docs_for_icp(icp))

    # Blog posts
    blog_dir = ROOT / "blog"
    if blog_dir.exists():
        for child in sorted(blog_dir.iterdir()):
            if child.is_dir():
                doc = doc_for_blog_post(child)
                if doc: docs.append(doc)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "count": len(docs),
        "documents": docs,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"Wrote {len(docs)} documents → {OUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
