# ERM Advisory — /frameworks/ Strategy & Implementation Guide

**Project:** Frameworks Knowledge Center  
**URL:** https://www.erikrmiller.com/frameworks/  
**Author:** Erik R. Miller · ERM Advisory  
**Produced:** June 2026

---

## 1. Information Architecture

```
/frameworks/                          ← Hub page (CollectionPage schema)
├── buying-group-mapping/             ← Framework detail (CreativeWork schema)
├── buying-group-orchestration/       ← Framework detail
├── account-activation-gap/          ← Framework detail
├── signal-centric-abm/              ← Framework detail
├── ai-buying-committee/             ← Framework detail
└── marketing-execution-gap/         ← Framework detail
```

**Design principle:** Each framework lives at its own canonical URL with full SEO treatment — title, meta description, canonical tag, schema, OG/Twitter cards, breadcrumbs, and a dedicated SVG diagram optimised for Google Image Search.

**Adding new frameworks:** Copy any existing detail page `index.html`, replace the content data, update the schema JSON, add a card to `frameworks/index.html`, and register the new URL in `sitemap.xml`. No structural changes required.

---

## 2. Keyword Targets

### Hub Page (`/frameworks/`)
| Primary | Supporting |
|---------|-----------|
| B2B marketing frameworks | B2B growth frameworks |
| ABM frameworks | account-based marketing frameworks |
| B2B revenue frameworks | enterprise marketing frameworks |
| marketing operating model | B2B strategy frameworks |

### Individual Framework Pages
| Page | Primary Keyword | Supporting Keywords |
|------|----------------|-------------------|
| buying-group-mapping | buying group mapping framework | buying committee mapping, B2B buying group, ABM stakeholder mapping |
| buying-group-orchestration | buying group orchestration | multi-channel ABM, ABM orchestration framework, B2B buying committee engagement |
| account-activation-gap | account activation gap | ABM pipeline gap, account engagement framework, B2B activation |
| signal-centric-abm | signal-centric ABM | signal-centric ABM operating model, intent signal ABM, ABM intelligence model |
| ai-buying-committee | AI buying committee | AI in B2B buying, AI vendor research, buyer AI framework |
| marketing-execution-gap | marketing execution gap | marketing strategy execution, marketing operating model, GTM execution framework |

---

## 3. Schema Markup Reference

### Hub Page Schema Stack
```json
CollectionPage → indexes all 6 framework pages
ItemList → 6 ListItem entries, each pointing to a framework page
FAQPage → 3 FAQ pairs (AEO optimisation)
Organization → ERM Advisory entity
```

### Detail Page Schema Stack
```json
CreativeWork → the framework itself (name, description, author, keywords)
BreadcrumbList → Home › Frameworks › [Framework Name]
ImageObject → embedded in CreativeWork, describes the SVG diagram
```

### ImageObject Pattern (on every detail page)
```json
{
  "@type": "ImageObject",
  "url": "https://www.erikrmiller.com/frameworks/[slug]/og-[slug].png",
  "width": 1200,
  "height": 630,
  "name": "[Descriptive name of the diagram]",
  "description": "[Full alt text paragraph describing what the diagram shows]"
}
```

**Note:** Each framework page currently links its OG image to a PNG at the framework's directory path (e.g. `og-buying-group-mapping.png`). These PNG exports should be generated from the SVG diagrams and placed in each framework subfolder. See Section 7 for image SEO specifications.

---

## 4. AEO (Answer Engine Optimisation) Implementation

### What Is Already Built
- **FAQPage schema** on the hub page with 3 high-volume question/answer pairs
- **Clear definitions** at the start of every framework's "Overview" section
- **Pullquote highlights** (`<div class="fd-highlight">`) with concise, quotable statements
- **Structured headings** (`fd-section-label` + `fd-h2`) that map to likely AI-query patterns
- **Entity-rich content** — every page references relevant entities: ERM Advisory, Erik R. Miller, named frameworks, named methodologies
- **BreadcrumbList schema** on every page for navigation context in AI responses

### Recommended Additional AEO Actions

1. **Expand FAQ coverage** — add a 3-question FAQPage schema block to each individual framework page, not just the hub. Each FAQ should directly answer a question a buyer or researcher would ask an AI.

   Suggested questions per framework:
   - "What is [Framework Name]?"
   - "How does [Framework Name] work?"
   - "Who uses [Framework Name] and why?"

2. **Add HowTo schema** to the "How to Apply" section of each framework page. HowTo schema is surfaced prominently in both Google AI Overviews and ChatGPT responses.

3. **Claim entity status in Wikidata / Crunchbase / LinkedIn** — AI systems (especially Perplexity and Gemini) heavily weight entities that appear in external knowledge graphs. Ensure ERM Advisory and Erik R. Miller have consistent, complete profiles on LinkedIn, Crunchbase, and any industry directories.

4. **Publish framework citation pages** — create a brief "About This Framework" section on each page that states:
   - When the framework was developed
   - The context in which it was created
   - How to cite it (author, date, URL)
   
   This citation metadata helps AI systems attribute the IP correctly.

5. **Build a definitions glossary** at `/frameworks/glossary/` — a single page defining every term used across frameworks. AI systems frequently surface definition pages from authoritative sources. High-value terms: buying group, signal-centric ABM, account activation, buying committee, intent signal.

---

## 5. Internal Linking Architecture

### Hub → Detail (Implemented)
Every framework card on the hub page links to its detail page with descriptive anchor text.

### Detail → Detail (Implemented)
Every detail page sidebar includes a "Related Frameworks" section with 3 links. Current mapping:

| Source Page | Related 1 | Related 2 | Related 3 |
|-------------|-----------|-----------|-----------|
| buying-group-mapping | buying-group-orchestration | account-activation-gap | signal-centric-abm |
| buying-group-orchestration | buying-group-mapping | signal-centric-abm | account-activation-gap |
| account-activation-gap | buying-group-mapping | signal-centric-abm | marketing-execution-gap |
| signal-centric-abm | buying-group-orchestration | account-activation-gap | buying-group-mapping |
| ai-buying-committee | signal-centric-abm | buying-group-mapping | marketing-execution-gap |
| marketing-execution-gap | signal-centric-abm | account-activation-gap | ai-buying-committee |

### Detail → Blog (Implemented)
Every detail page sidebar includes a "Related Articles" section linking to relevant blog posts on `/blog/`. Current links point to existing blog articles. Update these as new articles are published.

### Blog → Frameworks (Recommended Action)
Add a "Related Framework" callout block to each blog article that references a framework. Template:

```html
<div class="blog-framework-cta">
  <p>This article references the <strong>[Framework Name]</strong>.</p>
  <a href="/frameworks/[slug]/">Explore the Full Framework →</a>
</div>
```

This creates bidirectional linking between blog content and framework pages — reinforcing topical authority signals.

### Homepage → Frameworks (Recommended Action)
Add a "Frameworks" link to the main navigation (already done in the framework pages' nav HTML — verify it is also added to the root `index.html` nav). Confirm the footer navigation also includes the Frameworks link on all site pages.

---

## 6. Google Image Search Optimisation

### What Is Already Built
Every SVG diagram in the frameworks section includes:
- `<title id="[id]">` — descriptive title text
- `<desc id="[id]">` — full paragraph description of what the diagram shows
- `role="img"` on the `<svg>` element
- `aria-labelledby="[title-id] [desc-id]"` pairing
- ERM Advisory watermark text within the SVG

The `<figcaption>` under each diagram includes: framework name · section context · "ERM Advisory · Erik R. Miller"

### Required: Generate PNG Exports
To rank in Google Image Search independently, PNG versions of each diagram must be placed at the following paths:

| Framework | PNG Path | OG Image Path |
|-----------|----------|---------------|
| Hub page | /frameworks/og-frameworks-hub.png | Same |
| buying-group-mapping | /frameworks/buying-group-mapping/og-buying-group-mapping.png | Same |
| buying-group-orchestration | /frameworks/buying-group-orchestration/og-buying-group-orchestration.png | Same |
| account-activation-gap | /frameworks/account-activation-gap/og-account-activation-gap.png | Same |
| signal-centric-abm | /frameworks/signal-centric-abm/og-signal-centric-abm.png | Same |
| ai-buying-committee | /frameworks/ai-buying-committee/og-ai-buying-committee.png | Same |
| marketing-execution-gap | /frameworks/marketing-execution-gap/og-marketing-execution-gap.png | Same |

**PNG specifications:**
- Minimum dimensions: 1200 × 630px (OG standard)
- Preferred: 1600 × 900px or 2400 × 1260px for retina
- File naming: kebab-case, descriptive, no generic names (never `image.png`)
- Embed copyright metadata in EXIF: `© 2026 Erik R. Miller · ERM Advisory · erikrmiller.com`

**Generation approach:** Export SVGs to PNG using a headless browser (Puppeteer/Playwright) at 2x scale, or use Figma/Sketch export. Each exported image should match the SVG source exactly.

### Additional Image SEO Practices
1. Add explicit `<img>` tags (alongside SVG) for each diagram using the PNG export, with complete `alt`, `title`, and `loading="lazy"` attributes. The `alt` text should be a full description sentence, not just the diagram title.
2. Submit framework pages to Google Search Console after deployment and request indexing.
3. Use the `ImageObject` schema block with `contentUrl`, `thumbnailUrl`, `width`, `height`, and `description` properties populated from the PNG exports.

---

## 7. Image Filename & Alt Text Standards

Every framework diagram must follow this standard:

```
Filename:    [framework-slug]-diagram-erm-advisory.png
Alt text:    "[Framework Name] diagram showing [what it depicts] — ERM Advisory"
Title attr:  "[Framework Name] — ERM Advisory B2B Framework"
Caption:     "[Framework Name] · [Section/Subtitle] · ERM Advisory · Erik R. Miller"
```

### Examples
```
buying-group-mapping-diagram-erm-advisory.png
alt="Buying Group Mapping Framework diagram showing five B2B buying committee 
     stakeholder roles: Economic Buyer at center, Champion, Technical Evaluator, 
     End User, and Procurement — ERM Advisory"
```

```
signal-centric-abm-diagram-erm-advisory.png
alt="Signal-Centric ABM Operating Model — four concentric rings showing Account 
     Selection at center, Intent Intelligence, Multi-Channel Orchestration, and 
     Revenue Activation at the outermost layer — ERM Advisory"
```

---

## 8. Performance & Technical SEO

### What Is Already Implemented
- Canonical tags on every page
- `robots` meta: `index, follow`
- Breadcrumb schema (assists sitelinks in SERPs)
- Open Graph + Twitter Card tags on every page
- Font preconnect hints (`fonts.googleapis.com`, `fonts.gstatic.com`)
- `loading="lazy"` not needed for inline SVG (no HTTP request)
- Semantic HTML5 landmarks: `<main>`, `<article>`, `<aside>`, `<nav>`, `<section>`, `<figure>`, `<figcaption>`
- WCAG 2.1 AA: skip link, focus ring, `aria-label`, `aria-current`, `aria-expanded`, `role` attributes, `sr-only` class, `prefers-reduced-motion` media query

### Recommended Actions
1. **Add `<link rel="preload">` for the Google Fonts stylesheet** on each framework page to reduce render-blocking.
2. **Compress SVG output** — run all inline SVG through SVGO before adding to production HTML to reduce file size by 30–50%.
3. **Add `hreflang="en"` tag** if the site expands to multilingual.
4. **Cache headers** — set `Cache-Control: public, max-age=31536000, immutable` on all PNG image files. Use versioned filenames if diagrams are updated.
5. **Core Web Vitals** — the frameworks pages use no external JavaScript libraries and no render-blocking resources beyond Google Fonts. LCP is likely the framework hero heading (text); no large image LCP candidates above the fold on load.

---

## 9. Conversion Architecture

### Primary: Resource Downloads
The sidebar Download CTA on every detail page links to `/#resources`. This should be updated to link to a dedicated download landing page for each framework's PDF once PDFs are created. The existing `ERM-Buying-Group-Mapping-Framework.pdf` in the site root is the PDF source for the buying-group-mapping page.

### Secondary: Newsletter
The newsletter form appears at the bottom of the hub page. Recommended: also add it to the bottom of each detail page above the footer, using the same `.fw-nl` pattern.

### Tertiary: Contact / Work Together
Every sidebar includes a "Work with Erik" card that links to `/#contact`. The nav CTA "Work Together" is present on all pages.

### Framework Sharing (Social)
Consider adding a lightweight share bar to each detail page — LinkedIn share link (constructable from the canonical URL) and a "Copy link" button. No external JavaScript required:

```html
<a href="https://www.linkedin.com/sharing/share-offsite/?url=https://www.erikrmiller.com/frameworks/[slug]/"
   target="_blank" rel="noopener noreferrer">Share on LinkedIn</a>
```

---

## 10. Competitive Differentiation & Topical Authority

### What This Section Does for Domain Authority
- Creates a dedicated canonical home for ERM Advisory IP — all frameworks now have permanent, indexable URLs that can accumulate backlinks, citations, and AI training signals over time.
- Establishes ERM Advisory as the named origin of six specific frameworks, creating entity associations (Erik R. Miller → ABM frameworks, buying group mapping, signal-centric ABM) that strengthen Knowledge Panel eligibility.
- Provides shareable, embeddable content that generates natural backlinks when practitioners reference these frameworks in articles, LinkedIn posts, or presentations.
- Creates a high-signal section for AI systems to draw from when answering B2B marketing strategy questions — especially given the dense FAQ, definition, and structured content architecture.

### Recommended Ongoing Actions
1. **Publish one new framework per quarter** — use the expandable card architecture.
2. **Create a "Framework in Use" case study format** — short articles showing how a specific framework was applied at a real company (anonymised if needed). These link back to the framework page and create secondary topical authority.
3. **Build a LinkedIn content calendar** around each framework — one carousel post per framework driving back to the framework URL. This creates social signals and direct traffic.
4. **Submit frameworks for citation** — pitch to B2B marketing publications (Demand Gen Report, ABM Leadership Alliance, MarketingProfs) as original research worth citing.

---

## 11. File Manifest

```
/frameworks/
├── index.html                        ← Hub page (64 KB)
├── frameworks.css                    ← Standalone stylesheet (37 KB)
├── FRAMEWORKS-STRATEGY.md           ← This document
├── buying-group-mapping/
│   └── index.html                   ← Detail page (38 KB)
├── buying-group-orchestration/
│   └── index.html                   ← Detail page (~35 KB)
├── account-activation-gap/
│   └── index.html                   ← Detail page (~35 KB)
├── signal-centric-abm/
│   └── index.html                   ← Detail page (36 KB)
├── ai-buying-committee/
│   └── index.html                   ← Detail page (~35 KB)
└── marketing-execution-gap/
    └── index.html                   ← Detail page (~35 KB)
```

**Sitemap:** `/sitemap.xml` — updated with all 7 framework URLs at priority 0.85–0.90.

**Stylesheet pattern:** All pages currently use inline `<style>` blocks matching the existing site pattern. `frameworks.css` is provided as a standalone reference and for future use if the site migrates to an external stylesheet architecture.

---

*ERM Advisory · Erik R. Miller · erikrmiller.com · June 2026*
