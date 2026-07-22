# WAG-01 — Post-Deployment Production Audit

**Site:** https://erikrmiller.com
**Commit audited:** `5240be6` (OI PUB-06), branch `main`, working tree clean, in sync with `origin/main`
**Audit date:** 2026-07-21
**Roles:** Editor in Chief · Technical SEO Lead · Accessibility Auditor · QA Lead

---

## Method and Scope

The live site is GitHub Pages serving `main` with no build step, so the repository at `HEAD` is byte-identical to what is served. The audit crawled all **81 tracked HTML files** (77 real pages + 4 redirect stubs), resolved **every** internal `href`/`src` against the deployed file tree, parsed all JSON-LD, validated `sitemap.xml` against the indexable page set, inspected `search-index.json`, ran all four repository validators, and spot-verified findings against the live domain over HTTPS.

**Stated limitation:** JavaScript was not executed. Runtime console errors, live Core Web Vitals (LCP/INP/CLS), and rendered colour contrast on composited backgrounds were not measured. Contrast findings below are computed from the CSS token values and are mathematically certain where the background is a declared solid token; one case flagged "verify" depends on scroll state. A browser-based pass is recommended to close these out.

---

# Executive Summary

## Overall Site Health

The site is in **strong structural health** and materially better engineered than most sites of this size. Link integrity is near-perfect (3 broken links across roughly 2,900 resolved internal references). The sitemap is exact — 73 URLs, zero stale, zero missing, zero duplicates, correct `lastmod` on every entry. Canonicals are self-referencing and correct on all 73 indexable pages. Structured data coverage is unusually deep (FAQPage on 52 pages, BreadcrumbList on 52, DefinedTermSet on 10). All four CI validators pass.

The problems are not architectural. They are **coverage gaps and drift** — places where a newer standard was adopted and never backfilled across the older cohort.

## Production Readiness Score

**84 / 100**

| Domain | Score | Note |
|---|---|---|
| Crawlability & indexation | 97 | Sitemap and canonicals are exemplary |
| Internal link integrity | 92 | 3 broken links, one on a primary CTA |
| SEO metadata | 82 | 26 over-length titles, 12 over-length descriptions |
| Structured data / AEO | 88 | Deep coverage, inconsistent entity graph |
| Site search | 58 | **Frameworks and Resources are entirely unsearchable** |
| Accessibility (WCAG 2.2 AA) | 68 | Two site-wide contrast failures, 21-page landmark gap |
| Content consistency | 80 | Blog ordering bug, series continuity gap |
| Asset hygiene / naming | 70 | Four competing naming conventions, ~1.2 MB dead assets |
| Governance | 75 | Source-of-truth docs not in version control |

## Critical Findings (4)

1. **C-01** — The primary download CTA on `/frameworks/buying-group-mapping/download/` returns 404. Verified live.
2. **C-02** — Site search returns zero results for all Frameworks and Resources content: 32 indexable pages, including every lead-magnet page, are absent from the search index.
3. **C-03** — Gold brand text (`--gold` #b8922a) on cream/warm backgrounds measures **2.43:1** against a 4.5:1 AA requirement. Site-wide.
4. **C-04** — 21 pages have no `<main>` landmark and no skip link, including `/blog/` and `/icp/`.

## Medium Findings (11)

Blog index out of chronological order in two places · Two broken links to a non-existent post · OI series articles 02–04 do not link forward to PUB-06 · 26 titles exceed SERP truncation · 12 meta descriptions exceed truncation · 8 production pages carry a divergent footer that the footer validator silently skips · 4 redirect stubs lack `noindex` · Search index descriptions contain raw HTML entities · Four heading-hierarchy skips · Unlabeled email input on `/blog/` · No `:focus` styles on 20 pages.

## Minor Findings (9)

17 unreferenced assets (~1.2 MB) · Four competing PDF naming conventions · Duplicate `ERM-AI-Visibility-Scorecard.pdf` · 8.6 MB unoptimised MP4 · 1.8 MB PNG · ASCII-art diagram used in prose · 13 tables without `<caption>` · 5 `target="_blank"` links without `rel="noopener"` · One OG image at 2400×1260 while all others are 1200×630.

## Recommendations — Priority Order

**Fix before further promotion (1–2 hours):** C-01, C-02, the blog ordering bug, and the two broken links. These are the ones a CTO, a buyer, or Googlebot will actually hit.

**Fix this sprint (half day):** C-03 and C-04. Both are mechanical: swap `--gold` for the existing `--gold-a11y` token on light surfaces, and backfill `<main>` + skip link into the 21-page older cohort.

**Fix before the next publication (2–3 hours):** Title and description length pass, OI series forward-links, footer standardisation on the 8 divergent pages, and closing the footer-validator blind spot so this class of drift fails CI instead of passing silently.

---

# Issue Log

## CRITICAL

### C-01 — Primary download CTA returns 404

- **Severity:** Critical
- **URL:** `https://erikrmiller.com/frameworks/buying-group-mapping/download/`
- **Problem:** The page's primary button, "↓ Download PDF — Free", links to `/ERM-Buying-Group-Mapping-Framework.pdf`. That file does not exist at the site root. The actual file lives at `/resources/ERM-Buying-Group-Mapping-Framework.pdf`. Verified 404 on the live domain.
- **Why it matters:** This is a dedicated conversion page whose only purpose is delivering that PDF. Every visitor who reaches it — from the frameworks hub, from `/frameworks/all/`, from search — hits a dead end at the moment of conversion. It is also the single worst thing an enterprise evaluator can find on a site presented as production-ready.
- **Recommended fix:** Move the PDF to the site root to match the convention used by the other five framework downloads, or repoint the `href` to `/resources/ERM-Buying-Group-Mapping-Framework.pdf`. The first option is preferable — the other five all serve from root, and consistency prevents recurrence.

### C-02 — Frameworks and Resources are entirely absent from site search

- **Severity:** Critical
- **URL:** Site-wide (`assets/search/search-index.json`)
- **Problem:** The search index contains 56 documents covering the blog, homepage anchors, and `/icp/`. It contains **zero** entries for `/frameworks/*` (19 pages) or `/resources/*` (12 pages), and also omits `/about/`, `/blog/`, and `/visual-library/`. A user pressing ⌘K and typing "buying group mapping", "signal-centric ABM", or "share of model worksheet" gets nothing back, despite dedicated pages existing for each.
- **Why it matters:** Frameworks and resources are the site's commercial assets. Making them unsearchable while indexing homepage anchor fragments inverts the value hierarchy. `validate-search-index.py` passes because it only asserts that blog entries are carded — it has no completeness assertion against the sitemap, so the gap is invisible to CI.
- **Recommended fix:** Extend `scripts/build-search-index.py` to ingest `/frameworks/` and `/resources/` (plus `/about/` and `/visual-library/`). Then add an assertion to `validate-search-index.py`: every non-stub URL in `sitemap.xml` must appear in the index or sit on an explicit exemption list. Consider dropping the 15 homepage/`/icp/` anchor-fragment documents, which dilute relevance and carry empty descriptions.

### C-03 — Brand gold fails AA contrast on light surfaces

- **Severity:** Critical (WCAG 2.2 SC 1.4.3 Contrast (Minimum), Level AA)
- **URL:** Site-wide — homepage `.impact` section, `.imp-l`, `.imp-hl em`, `.w-intro em`, `.hst-l`, `.g-pin-label`, and the `.nav-cta` "Work Together" button in the shared nav
- **Problem:** Measured ratios against the declared background tokens:

  | Foreground | Background | Ratio | AA requirement | Result |
  |---|---|---|---|---|
  | `--gold` #b8922a | `--cream` #edeae0 | **2.43:1** | 4.5:1 | Fail |
  | `--gold` #b8922a | `--paper` #f7f4ee | **2.66:1** | 4.5:1 | Fail |
  | `--gold` #b8922a | `--warm` #e5e0d4 | **2.22:1** | 4.5:1 | Fail |
  | `--gold-lt` #d4ac4e | `--cream` #edeae0 | **1.78:1** | 4.5:1 | Fail |

  The affected text is small — 0.5rem to 0.75rem uppercase labels and kickers — so the large-text 3:1 exemption does not apply. The same gold on `--ink` (#0c0b09) measures 6.73:1 and **passes**; the dark-section usage in `.global` and `.approach` is fine.
- **Why it matters:** This is the most common AA failure in real audits and the first thing an accessibility lead will find. It affects the persistent nav CTA and the homepage impact section — the highest-traffic surfaces on the site.
- **Recommended fix:** A `--gold-a11y` token already exists at #7a5e12 (**5.57:1** on paper — passes) and is used in 15 places on the homepage, so the remediation was started and not finished. Complete it: on any light-background surface, replace `color:var(--gold)` with `color:var(--gold-a11y)`. Leave `--gold` for dark sections and for non-text decorative use (borders, dots, rules), which 1.4.3 does not govern.
- **Verify in browser:** `.nav-cta` sits in a transparent nav that becomes `rgba(12,11,9,0.94)` on scroll. It passes when stuck; it needs visual confirmation against each page's hero at scroll position 0.

### C-04 — 21 pages have no `<main>` landmark and no skip link

- **Severity:** Critical (WCAG 2.2 SC 2.4.1 Bypass Blocks, Level A; SC 1.3.1 Info and Relationships)
- **URLs:** `/blog/`, `/icp/`, `/404.html`, `/resources/erm-buying-group-mapping-framework/`, and 17 blog articles — `/blog/account-activation-gap-icp-target-account-list/`, `/blog/ai-agents-for-marketing-teams/`, `/blog/ai-marketing-operating-system/`, `/blog/how-i-cut-content-production-time/`, `/blog/human-in-the-loop-content-activation/`, `/blog/icp-development-the-framework-i-use-every-time/`, `/blog/icp-vs-tam-vs-personas/`, `/blog/intent-data-is-mostly-hype/`, `/blog/running-marketing-across-four-continents/`, `/blog/sales-enablement-that-sales-actually-uses/`, `/blog/the-mql-is-dead/`, `/blog/why-firmographic-icps-fail/`, `/blog/why-most-abm-programs-fail/`, `/blog/why-your-ai-marketing-stack-isnt-working/`, `/blog/year-one-gtm-seven-questions/`
- **Problem:** These pages have no `<main>` element, no `role="main"`, and no "Skip to main content" link. Newer pages — the entire OI series, all framework pages — have both. This is an older cohort that was never backfilled.
- **Why it matters:** Bypass Blocks is **Level A**, not AA. It is the floor, not the target. A keyboard or screen-reader user landing on `/blog/` must tab through the full navigation on every page load with no way out. `/blog/` is the site's second-most-important page.
- **Recommended fix:** Wrap the content body in `<main id="main-content">` and add the standard skip link already present on newer templates. Add a landmark assertion to a validator so no future page ships without it.

---

## MEDIUM

### M-01 — Blog index is out of chronological order

- **URL:** `https://erikrmiller.com/blog/`
- **Problem:** Two cards are out of sequence:
  - Position 9 `enterprise-marketing-operating-system/` (June 25, 2026) appears **before** position 10 `share-of-model-board-report/` (July 1, 2026)
  - Position 38 `icp-development-the-framework-i-use-every-time/` (April 8, 2026) appears **before** position 39 `why-most-abm-programs-fail/` (April 27, 2026)
- **Why it matters:** The stated contract of the blog landing page is newest-first. A visible ordering error on a page whose entire job is ordering undermines confidence in everything below it, and an editor notices it immediately.
- **Recommended fix:** Reorder the two card pairs in `blog/index.html`. Add a chronological-order assertion to `scripts/validate-blog-cards.py` — it currently validates card *presence* but not *sequence*.

### M-02 — Two broken links to a post that does not exist

- **URL:** `https://erikrmiller.com/blog/marketing-execution-gap/`
- **Problem:** Two anchors point to `/blog/marketing-leadership-maturity-model/`. No such page exists; verified 404 live.
- **Why it matters:** Broken internal links leak crawl budget, break the reader's path mid-article, and signal an unfinished content plan.
- **Recommended fix:** Publish the maturity-model article, or repoint both links to the closest live equivalent (`/frameworks/marketing-execution-gap/` or `/blog/revenue-execution-gap/`). Add a link-integrity check to CI — the crawl used for this audit runs in under two seconds and would have caught both this and C-01 pre-deploy.

### M-03 — OI series articles 02–04 do not link forward to PUB-06

- **URLs:** `/blog/executive-listening-tour/`, `/blog/beyond-the-org-chart/`, `/blog/evidence-based-alignment/`

| Article | →01 | →02 | →03 | →04 | →05 | →06 |
|---|---|---|---|---|---|---|
| PUB-01 cornerstone | — | ✓ | ✓ | ✓ | ✓ | ✓ |
| PUB-02 listening tour | ✓ | — | ✓ | ✓ | ✓ | **✗** |
| PUB-03 beyond org chart | ✓ | ✓ | — | ✓ | ✓ | **✗** |
| PUB-04 evidence-based alignment | ✓ | ✓ | ✓ | — | ✓ | **✗** |
| PUB-05 findings to action | ✓ | ✓ | ✓ | ✓ | — | ✓ |
| PUB-06 what CEOs expect | ✓ | ✓ | ✓ | ✓ | ✓ | — |

- **Problem:** The "Continue the Series" blocks in 02, 03, and 04 were written before PUB-06 published and were not backfilled. Publication order, dates, breadcrumbs, and all backward links are correct — the gap is forward-only.
- **Why it matters:** A reader entering the series at article 2 or 3 — which is what organic search delivers — reaches the end of the series listing and never learns PUB-06 exists. PUB-06 is the sponsor-side capstone and the strongest commercial article in the set.
- **Recommended fix:** Add the PUB-06 entry to the series block in 02, 03, and 04. Longer term, generate the series block from a single manifest so publishing article *n* updates articles *1…n−1* automatically.

### M-04 — 26 page titles exceed SERP display width

- **Problem:** Titles over roughly 60–65 characters truncate in Google. Worst offenders:

| URL | Length |
|---|---|
| `/blog/share-of-model-board-report/` | 113 |
| `/blog/from-findings-to-action/` | 111 |
| `/blog/demand-creation-vs-demand-capture/` | 110 |
| `/blog/ai-buying-committee-b2b-vendor-research/` | 109 |
| `/blog/recommendation-ladder-ai-search/` | 103 |
| `/blog/signal-centric-abm-operating-model/` | 101 |
| `/blog/executive-listening-tour/` | 100 |
| `/blog/sixth-seat-ai-agent-buying-committee/` | 95 |
| `/resources/erm-buying-group-mapping-framework/` | 94 |

  Plus 17 more between 66 and 90 characters.
- **Why it matters:** The truncated tail is invisible in SERPs and often carries the differentiating phrase. It also affects how the page is summarised in AI answers, where the title is a primary signal.
- **Recommended fix:** Rewrite to ≤ 60 characters plus the ` | Erik R. Miller` suffix, front-loading the query-matching phrase. Add a length check to the launch checklist.

### M-05 — 12 meta descriptions exceed truncation length

- **Problem:** Descriptions over roughly 155–160 characters truncate. Longest: `/blog/revenue-execution-gap/` (296), `/frameworks/ai-visibility-architecture/` (276), `/blog/demand-creation-vs-demand-capture/` (259), `/blog/share-of-model-board-report/` (249), `/blog/signal-centric-abm-operating-model/` (214), `/blog/recommendation-ladder-ai-search/` (211), `/resources/machine-customer-readiness-index/` (210), `/blog/marketing-execution-gap/` (203), plus four more between 188 and 197.
- **Why it matters:** The call to action usually lives at the end of the sentence, which is the part that gets cut.
- **Recommended fix:** Trim to 150–158 characters with the value proposition in the first clause.

### M-06 — 8 production pages carry a divergent footer, and the validator does not catch it

- **URLs:** All six `/frameworks/*/download/` pages, plus `/resources/marketing-operating-system-blueprint/` and `/resources/share-of-model-measurement-worksheet/`
- **Problem:** These pages ship a reduced footer — copyright line plus two social links — instead of the standard footer with the bio block, Navigate column, Connect column, and five social links. `validate-footer.py` reports **PASS** on 65 pages while `validate-nav.py` validates 73. The 8-page delta is exactly the divergent set: the validator does not fail them, it silently omits them.
- **Why it matters:** Two problems. The user-facing one: the framework download pages are the site's conversion endpoints and they drop the newsletter CTA and the navigation that would move a converted visitor deeper. The systemic one is worse — a validator that reports PASS while skipping non-conforming pages provides false assurance, and every future audit inherits that blind spot.
- **Recommended fix:** Standardise the footer on all 8 pages. Then change `validate-footer.py` to enumerate its page set from the same source as `validate-nav.py` and **fail** on any production page lacking the canonical footer rather than excluding it.

### M-07 — Four redirect stubs are missing `noindex`

- **URLs:** `/1/feed/`, `/blog.html`, `/blog/category/guides-how-to/`, `/cv--resume.html`
- **Problem:** Seven legacy redirect stubs exist. Three (`/about.html`, `/ebooks/`, `/ebooks/ai-agents-for-marketing-teams/`) correctly carry `meta robots: noindex`. These four do not. All seven correctly carry a cross-canonical to their destination and are correctly excluded from `sitemap.xml`.
- **Why it matters:** The canonical tag is a hint, not a directive. Without `noindex`, these thin stubs can be indexed and surfaced, producing a "Redirecting…" title in search results. Low probability, trivial cost to eliminate.
- **Recommended fix:** Add `<meta name="robots" content="noindex, follow">` to the four stubs. Better still, replace the meta-refresh stubs with real 301s. GitHub Pages cannot issue those from a static file, so if 301s matter here, the redirect layer belongs in front of Pages.

### M-08 — Search index contains raw, undecoded HTML entities

- **Problem:** Search result descriptions render literal entity codes. Examples:
  - `/blog/ai-buying-committee-b2b-vendor-research/` → "your buyer**&#39;**s AI has already compared vendors"
  - `/blog/consensus-engine-why-ai-recommends/` → "AI doesn**&rsquo;**t rank… ERM Advisory**&rsquo;**s operating model"
  - Three homepage anchor documents are affected as well.
- **Why it matters:** Visible encoding artifacts in a search overlay read as a broken product. On a site whose editorial standard uses proper typographic apostrophes throughout the prose, this is a jarring inconsistency.
- **Recommended fix:** Apply `html.unescape()` to title and description fields in `scripts/build-search-index.py`, and add an entity-pattern assertion to `validate-search-index.py`.

### M-09 — Heading hierarchy skips

- **URLs:** `/blog/agentic-execution-gap/` and `/blog/buying-group-orchestration-abm-strategy/` (`h1` → `h3`); `/blog/ai-agents-for-marketing-teams/` and `/blog/ai-marketing-operating-system/` (`h2` → `h4`)
- **Problem:** Heading levels skip a rank, breaking the document outline.
- **Why it matters:** WCAG 2.2 SC 1.3.1. Screen-reader users navigate long-form articles by heading level; a skipped rank implies a missing section. These are 3,000+ word articles where heading navigation is the primary reading strategy.
- **Recommended fix:** Demote or promote the offending headings to close the gap. Add a heading-order check to the article launch checklist.

### M-10 — Unlabeled email input on the blog newsletter form

- **URL:** `https://erikrmiller.com/blog/`
- **Problem:** `<input class="bnl-inp" placeholder="Your work email" type="email">` has no `<label>`, no `aria-label`, and no `aria-labelledby`. Its only accessible name is the placeholder, which disappears on focus.
- **Why it matters:** WCAG 2.2 SC 3.3.2 (Labels or Instructions) and SC 4.1.2 (Name, Role, Value). A screen-reader user hears "edit text, blank." Placeholder-as-label is one of the most cited form failures in the field.
- **Recommended fix:** Add a visually-hidden `<label for>` or `aria-label="Your work email"`. Verified clean elsewhere: the 100 radio inputs on `/resources/machine-customer-readiness-index/` use implicit `<label>` wrapping inside 20 correctly paired `<fieldset>`/`<legend>` blocks — that form is well built.

### M-11 — No `:focus` styling on 20 pages

- **URLs:** The same older cohort as C-04, plus `/404.html` and the `/ebooks/` stubs
- **Problem:** No `:focus` or `:focus-visible` rule appears in these documents, so keyboard users get only the browser default — which is suppressed on several elements. `/blog/` additionally declares `outline:none` with no `:focus-visible` replacement.
- **Why it matters:** WCAG 2.2 SC 2.4.7 (Focus Visible) and the newer SC 2.4.11 (Focus Not Obscured). Combined with C-04's missing skip links, these pages are difficult to operate without a mouse.
- **Recommended fix:** Add the shared `:focus-visible` treatment used on newer templates. Since nav and footer are already extracted to `assets/nav/nav.css` and `assets/footer/footer.css`, the cleanest fix is a small shared `assets/base/a11y.css` linked site-wide, which also removes the recurrence risk.

---

## MINOR

| ID | Issue | Detail | Recommended fix |
|---|---|---|---|
| N-01 | 17 unreferenced assets (~1.2 MB) | `pg1–pg5.png` (808 KB, root), `.preview_v5_p01.png`, `og-ai-agents-demand-gen.png`, `assets/images/erm-traditional-vs-ai-search.{png,svg}`, seven orphaned SVGs under `/blog/agentic-execution-gap/`, `/blog/marketing-execution-gap/` and `/blog/revenue-execution-gap/`, and `frameworks/erm-revenue-execution-system/og-erm-revenue-execution-system.png` | Delete. `pg1–pg5.png` and `.preview_v5_p01.png` are working artifacts that should never have been committed — add matching patterns to `.gitignore` |
| N-02 | Four competing PDF naming conventions | `Erik-R-Miller-ERM-Advisory-*` (7 files, newest), `ERM-*` (9), `AI-Agents-for-*` (7), and one lowercase outlier `erm-demand-architecture-framework.pdf`. `ERM-LAUNCH-STANDARD.md` documents `ERM-<Name>.pdf`, which the seven newest files do not follow — so either the standard is stale or the files are non-conforming | Pick one convention, document it in `ERM-LAUNCH-STANDARD.md`, rename with redirects, and add a naming assertion to CI. The OI series alone spans both: PUB-02 ships `ERM-Executive-Listening-Tour-Interview-Guide.pdf` while PUB-03 through 06 ship `Erik-R-Miller-ERM-Advisory-*` |
| N-03 | Duplicate PDF | `ERM-AI-Visibility-Scorecard.pdf` exists at root and at `frameworks/ai-visibility-architecture/` | Keep one, repoint references |
| N-04 | 8.6 MB unoptimised video | `erik-miller-nyc.mp4` is the single largest asset on the site — 38% of total payload | Re-encode at a lower bitrate or move to a CDN/streaming host. Confirm `preload="none"` and a `poster` frame |
| N-05 | 1.8 MB PNG | `erik-r-miller-b2b-marketing-leader-personal-website-thumbnail.png` | Convert to WebP with PNG fallback; expect roughly 80% reduction |
| N-06 | ASCII-art diagram in prose | `/blog/ai-agents-for-marketing-teams/` renders a five-layer architecture diagram as ASCII art — 35 double-hyphen runs in the text layer | Screen readers read this character by character. Replace with the inline-SVG-plus-`<title>` pattern used in the OI series, which is done well |
| N-07 | 13 tables without `<caption>` | Seven pages including `/blog/ai-powered-icp-development/`, `/blog/demand-creation-vs-demand-capture/`, `/blog/the-hidden-abm-problem-buying-groups/` | Add `<caption>`. `<th>` usage is correct throughout — this is the last gap for SC 1.3.1 on tables |
| N-08 | 5 `target="_blank"` links without `rel="noopener"` | `/blog/how-i-cut-content-production-time/`, `/blog/icp-development-the-framework-i-use-every-time/`, `/blog/running-marketing-across-four-continents/`, `/blog/the-mql-is-dead/`, `/blog/why-most-abm-programs-fail/` | Add `rel="noopener noreferrer"` |
| N-09 | OG image dimension outlier | `/blog/revenue-execution-gap/` ships 2400×1260 while all 26 others are exactly 1200×630 | Harmless but inconsistent; normalise |

---

## GOVERNANCE OBSERVATIONS

**G-01 — The declared source-of-truth documents are not in version control.** `CLAUDE.md`, `PROJECT_STRUCTURE.md`, and `WORKFLOW.md` are untracked. `CLAUDE.md` states these are "the operational source of truth for this project," yet they exist only on one machine, are not on GitHub, have no history, and are one `rm` away from gone. **Recommendation:** `git add` and commit all three.

**G-02 — A transient uncommitted change was observed mid-audit.** Early in the audit the working tree contained an uncommitted modification adding `<link rel="stylesheet" href="/assets/type/type.css">` to 75 pages, alongside an untracked `assets/type/` directory. The change reverted before the audit completed and the tree is now clean at `5240be6`. It is flagged because, had those 75 files been committed without `git add assets/type/`, every page on the site would have issued a 404 request for a missing stylesheet — verified: `/assets/type/type.css` currently 404s live. **Recommendation:** when a change touches both an asset directory and the pages referencing it, commit both in one commit, and add a CI check that every local `href`/`src` in changed files resolves to a tracked file.

**G-03 — CI has no link-integrity or landmark gate.** The four existing validators cover nav, footer, blog cards, and search index. The crawl that found C-01, C-02, M-01, and M-02 runs in under two seconds. **Recommendation:** add a link-resolution job to `.github/workflows/`.

---

# Positive Findings

These are genuinely above the standard for a site of this size and deserve to be stated plainly.

**Sitemap is exact.** 73 URLs. Zero stale entries, zero missing pages, zero duplicates, zero non-canonical hosts, `lastmod` present and plausible on every single entry, valid XML. Redirect stubs and `noindex` pages are correctly excluded. This is the cleanest part of the site, and most sites never get here.

**Canonicals are perfect.** Every one of the 73 indexable pages has a self-referencing canonical that matches its URL exactly. No chains, no conflicts, no duplicates, no missing tags. The seven redirect stubs correctly cross-canonical to their destinations.

**Link integrity is near-perfect.** Roughly 2,900 internal references resolved across 81 files, producing 3 broken links. Zero missing-trailing-slash redirects, zero uppercase-path inconsistencies, zero `www.` host links, zero broken asset references. Trailing-slash discipline is consistent site-wide.

**Structured data is deep and well-formed.** 52 pages carry both `FAQPage` and `BreadcrumbList`. Ten pages carry `DefinedTermSet` — a genuinely sophisticated AEO signal most B2B sites do not implement. Every JSON-LD block on the site parses without error. `HowTo`, `ItemList`, `Book`, `BookSeries`, `TechArticle`, and `DigitalDocument` are used appropriately where they apply.

**All four validators pass, and the SSOT architecture works.** Navigation is identical across 73 pages. The footer is identical across the 65 it checks. Every one of 39 blog articles has a corresponding index card, no drafts leak into production, and the search index count reconciles. Extracting nav and footer to `partials/` with build-and-validate scripts is the right architecture and it is holding.

**The Organizational Intelligence series is editorially excellent.** Publication order is correct and dates are sequential (Jul 11 → 13 → 14 → 15 → 16 → 20). Breadcrumbs are present on all six. Every article carries `BlogPosting` + `FAQPage` + `BreadcrumbList` + `DefinedTermSet`. Backward linking is complete — every article links to every predecessor. Downloadable workbooks are attached and resolve correctly on all five that have them. PUB-06 is particularly well constructed: strong entity definitions, primary-source citations to McKinsey and HBR with working links, a six-question FAQ, correct OG and Twitter metadata, and two accessible inline SVG diagrams with full text descriptions.

**Accessibility is genuinely good on the newer cohort.** `lang` is present on every page. The OI series and all framework pages have `<main>`, skip links, `:focus` styles, correct heading order, and inline SVGs with proper `role` and `<title>`. The MCRI scorecard's 100-input assessment form is correctly built with 20 `<fieldset>`/`<legend>` pairs and implicit labels — that is careful work. The existence of a `--gold-a11y` token proves contrast remediation was deliberately started.

**robots.txt is correct.** Clean `Allow: /`, correct absolute sitemap reference, no accidental disallows, no blocked assets.

**Typography and editorial quality are high.** Zero mojibake, zero encoding corruption, zero TODO/TK/placeholder text, zero broken lists, proper typographic apostrophes and em-dashes across 48 of 54 long-form pages. The six files with straight apostrophes contain one or two instances each, all inside first-person contractions.

**A custom 404 page exists** with navigation and recovery links, correctly `noindex`ed and correctly excluded from the sitemap.

**Asset discipline is mostly sound.** 26 of 27 OG images are exactly 1200×630. Total tracked payload is 22.7 MB, of which 10.4 MB is two files — the rest of the site is lean.

---

# AI Search Readiness (AEO / GEO)

**Current state: strong foundation, one structural gap.**

What is working: `FAQPage` on 52 pages directly feeds answer engines. `DefinedTermSet`/`DefinedTerm` on 10 pages is the single highest-leverage AEO signal on the site — it explicitly tells a model "this is a named concept with a canonical definition," which is exactly how proprietary frameworks earn citations. PUB-06's "The Short Answer" block at the top of the article is textbook answer-engine formatting: a self-contained, extractable, roughly 90-word answer before the argument begins. Primary-source citations with working outbound links to McKinsey and HBR raise citation-worthiness. Question-formatted H2s ("Why Do So Many Executive Transitions Fail?", "How Do You Tell Thoughtful Leadership from Inactivity?") match conversational query patterns.

**The gap — entity graph inconsistency.** `Organization` schema appears on only 11 of 77 pages and `Person` on only 14. There is no consistent `@id` linking author and publisher across the site, so an answer engine crawling `/blog/why-most-abm-programs-fail/` and `/frameworks/signal-centric-abm/` has no structural evidence they belong to the same entity. `WebSite` appears once, on the homepage, which is correct — but it lacks the `publisher` `@id` reference that would anchor the graph.

**Recommendations, in leverage order:**

1. **Establish a canonical entity graph.** Emit `Organization` (`@id: https://erikrmiller.com/#organization`) and `Person` (`@id: https://erikrmiller.com/#erik-r-miller`) once on the homepage with full `sameAs` arrays for the five social profiles already in the footer. On every other page, reference those `@id`s from `author` and `publisher` rather than re-declaring the entities. This is the highest-value AEO change available and it is mechanical.
2. **Fix C-02.** Frameworks and Resources being unsearchable on-site correlates with weak internal signal to the pages you most want cited. Site search and internal linking feed the same relevance model.
3. **Extend `DefinedTermSet` to every proprietary framework.** The Ninety-Day Compact, Share of Model, the Recommendation Ladder, the Consensus Engine, and the Machine Customer Readiness Index are exactly the named concepts that earn model citations. Ten pages have it; roughly 25 should.
4. **Add "The Short Answer" blocks to older articles.** PUB-06 does this. Backfilling the top 10 organic articles is high-return, low-effort.
5. **Add `speakable` markup** to the answer blocks on those top 10 articles.
6. **Fix the title lengths (M-04).** Titles are a primary summarisation signal for AI answers, and a 113-character title gets truncated in that context too.

---

# Final Recommendation

## READY WITH MINOR RECOMMENDATIONS

The live site is stable, correctly indexed, structurally sound, and safe to remain in production. Nothing here warrants a rollback and nothing damages the site's standing with search engines. The sitemap, canonical, link-integrity, and structured-data work is materially better than the baseline for sites of this size, and the SSOT-plus-validator architecture is the right long-term foundation.

Two qualifications on that verdict, stated plainly for the record:

**C-01 should be fixed today.** A 404 on the primary CTA of a conversion page is a five-minute fix and the single most damaging thing an enterprise evaluator could encounter. It does not change the deployment verdict, but it should not survive the week.

**C-03 and C-04 place the site below WCAG 2.2 AA today.** Missing skip links on 21 pages is a **Level A** failure, not AA. If this site is subject to a formal accessibility commitment — a VPAT, a procurement requirement, an ADA-exposure posture — then the honest status is *not conformant*, and the accurate verdict in that context is **READY WITH MINOR RECOMMENDATIONS, CONDITIONAL ON ACCESSIBILITY REMEDIATION**. Both fixes are mechanical and estimated at half a day combined.

**Recommended sequence:**

1. **Today (~1 hour):** C-01, M-02, M-01 — the two broken-link sets and the blog ordering.
2. **This week (~half day):** C-03 and C-04 — swap `--gold` → `--gold-a11y` on light surfaces; backfill `<main>` and skip links across the 21-page cohort.
3. **This sprint (~1 day):** C-02 search coverage; M-03 series forward-links; M-06 footer standardisation; M-04 and M-05 title and description pass.
4. **Before the next publication:** close the CI gaps — link resolution, landmark presence, chronological ordering, footer strictness, search-index completeness. Every critical and medium finding in this report is mechanically detectable, which means none of them needs to be found by an auditor again.

---

*Audit performed against commit `5240be6` on branch `main`, working tree clean and synchronised with `origin/main`. All 81 tracked HTML files parsed; all internal references resolved against the deployed file tree; findings C-01, M-02, and G-02 independently verified against the live domain over HTTPS. JavaScript execution, runtime console inspection, and Core Web Vitals field measurement were out of scope and are recommended as a follow-on browser-based pass.*
