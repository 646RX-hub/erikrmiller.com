# ERM Flagship Launch Standard (Permanent)

Established July 8, 2026 with the Machine Customer Readiness Index launch.
Every flagship ERM framework launches as a complete resource ecosystem — never as separate components.

## Required components for every flagship release

1. **Executive article** — flagship blog template, Short Answer + Executive Summary + FAQ (matching FAQPage schema exactly), Key Takeaways, source-verified citations (every statistic checked against the original source; nothing paraphrased from memory).
2. **Interactive web resource** — `/resources/<slug>/`, resource template inheriting flagship widths and typography; client-side only, live scoring, executive-briefing results (score, level, strongest/weakest, first wall, priority, recommended next framework), no-refresh reset.
3. **Downloadable executive workbook PDF** — branded ink/gold, cover, instructions, worksheet pages, board-summary one-pager, notes, executive learning path with clickable links and QR codes. Root filename: `ERM-<Name>.pdf`.
4. **Interactive calculator, assessment, or worksheet** where appropriate — DOM-tested edge cases before ship.
5. **Dedicated OG image** — 1200×630, <300 KB, `erm-<slug>-og-image.png` in the page directory; referenced in og, twitter, and schema.
6. **Homepage feature update** — featured section + ItemList schema, newest publication first.
7. **Blog index update** — post card (and featured card for pillars).
8. **Resource hub update** — fn-card with accurate meta chips.
9. **Full QA before PASS** — all four validators (nav, footer, search index, blog cards), JSON-LD parse, zero broken links (pages + PDF annotations + JS-embedded links), WCAG AA contrast computed (not assumed), heading hierarchy, fieldset/legend semantics, sitemap + search index regenerated, meta descriptions 150–160 chars.

## Editorial standards

Executive language throughout: no jargon without an inline plain-English explanation; questions answerable by a CMO/CRO/RevOps leader without a second document. Framework names retained, with executive subtitles ("Can AI understand your company?"). Dense multi-concept sentences become scannable lists. Supporting-label floor: **no uppercase label below 13px** — section overlines 15px, card/timeline/chip labels 13px; 1rem+ for instructional text. Governed by `docs/ERM-TYPOGRAPHY-STANDARD.md` and `assets/type/type.css`; enforced by `scripts/validate-type.py`. The former 0.62rem (9.9px) floor is retired. Headings, lede and body copy are unchanged and out of scope.

## Terminology registry

Tiers: Invisible · Legible · Transactable · **Agent Ready** (no hyphen as tier name; "Agent-Ready" hyphenated only as adjective in framework names). Dimensions: Machine Legibility · Verifiable Substance · Transaction Readiness · Governance · Discoverability. Scoring: 20 questions × 1–5 → /100; bands 20–44 / 45–64 / 65–84 / 85–100; level capped by any dimension ≤ 8.
