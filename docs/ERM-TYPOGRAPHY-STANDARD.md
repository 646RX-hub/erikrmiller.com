# ERM Advisory — Supporting Label Typography Standard

**Status:** Governing standard. **This is the single source of truth.**
**Owner:** Erik R. Miller · ERM Advisory
**Established:** 2026-07-21 · **Approved scope:** supporting labels only.
**Implemented by:** `assets/type/type.css` · **Enforced by:** `scripts/validate-type.py`

Any earlier draft, proposal, or scale that conflicts with this document is void.

---

## 1. What problem this solves

New articles are built by copying the previous article's page — including its
entire inline `<style>` block (`OI-PRODUCTION-HANDOFF.md` §4). Typography values
therefore propagate forward permanently. Supporting labels had drifted to
8.32px against 17px body copy: **0.50× body**, which reads as a footnote rather
than as structure.

This standard exists to stop that inheritance. It is **not** a typography
redesign.

## 2. Scope

**Governed (supporting labels only):**

- Section overlines and uppercase section labels
- Timeline labels, card labels, framework labels
- Table category cells, chips and badges
- In-article action labels (back link, breadcrumb, read-more, CTA link)
- Footer column headings

**Explicitly NOT governed — unchanged by this standard:**

- Hero / display type
- H1–H6 hierarchy
- Lead paragraphs
- Body copy and its line-height
- Spacing rhythm, colour, layout
- Navigation *(see §6)*

These establish the site's editorial character and are deliberately untouched.

## 3. The governing principle

> **Nothing may become smaller than it is today.**
> Existing typography may stay the same or grow. Any reduction requires explicit
> approval, case by case, before implementation.

Every value in §4 is larger than the declaration it supersedes. Verified: **55
selectors change, 0 reduced.**

## 4. The scale

| Token | Mobile ≤768 | Desktop | ≥1600 | Weight | Leading | Tracking | Transform |
|---|---|---|---|---|---|---|---|
| `--type-overline` | 13px | **15px** | 16px | 700 | 1.45 | 0.14em | uppercase |
| `--type-label` | 13px | **13px** | 13px | 700 | 1.40 | 0.11em | uppercase |
| `--type-action` | 13px | **13px** | 13px | 600 | — | 0.10em | uppercase |

**Why 15px for section overlines.** Against 17px body that is 0.88× — clearly a
label, clearly subordinate to a 25px H3. At 18px it would outrank body copy and
compete with card titles. The brief was "intentional, not oversized."

**Why tracking falls as size rises** (0.26em → 0.14em). Heavy tracking was
compensation for undersized type. Once the size is correct it reads as noise and
slows the eye. Labels get larger and calmer at the same time.

**Why 13px is the floor.** Below it, uppercase Syne at weight 700 stops reading
as a deliberate label. The floor holds at every viewport; nothing shrinks on
mobile.

## 5. The minimum standard

> **No supporting label renders below 13px.** The only exceptions are legally
> required fine print and image or data attributions.

## 6. Navigation — approved but deferred

Nav links currently render at 9.6px, and the nav row **already overflows at
1024px by 33px** at that size. Correcting it means a layout change (gap,
padding, and hamburger breakpoint), not a type change. Measured with real Syne
metrics: at 14px with a 1.25rem gap and 2.5rem padding the row needs 1088px, so
the hamburger breakpoint must move from 768px to ~1150px.

That is a layout change to shared chrome affecting every page at 768–1150px. It
is **out of scope for this release** to keep regression risk minimal, and is
tracked as its own change. Recorded here so it remains a decision, not an
oversight.

## 7. How to change typography

Change the **token** in `assets/type/type.css`. Never set a label size on a page.

```bash
python3 scripts/install-type.py     # link the layer on a new page (idempotent)
python3 scripts/validate-type.py    # regression guard; runs in CI
```

The validator fails the build if a page is missing the layer, or if a page uses
`!important` to force a governed label back below the floor. It *reports* legacy
ungoverned labels without failing — that backlog is deliberately out of scope.

## 8. Accessibility — measured, not assumed

WCAG 2.2 AA sets no minimum font size, so the 13px floor is stricter than the
specification by intent.

**Colour was not left alone.** Raising label size exposed a pre-existing contrast
failure: brand gold `#b8922a` measures **2.43:1 on cream** and **2.66:1 on paper**,
against the 4.5:1 that AA requires for normal-size text. A 15px or 13px bold label
is *not* "large text" (that threshold is 18.66px bold / 24px regular), so the
exception does not apply.

Two scoped corrections were made, colour only:

| Surface | Token | Value | Applies to | Measured |
|---|---|---|---|---|
| Light (paper / cream) | `--type-label-on-light` | `#7a5e12` | 21 governed label selectors | **5.08–5.57:1** |
| Ink (gold, low alpha) | `--type-label-on-ink-gold` | `rgba(184,146,42,0.88)` | `.se-cite` | **5.41:1** (was 3.07:1) |
| Ink (muted, low alpha) | `--type-label-on-ink-mute` | `rgba(247,244,238,0.55)` | `.ah-read`, `.ah-date` | **5.79:1** (was 2.68:1) |

`#7a5e12` is the same hue as brand gold, darkened until it passes. **Brand gold is
unchanged on ink**, where it already measures 6.29–6.73:1, and unchanged everywhere
outside governed labels — headings, rules, borders, icons, backgrounds and the
brand palette are untouched.

**Result: 54 governed label/background pairings tested, 54 pass at 4.5:1 or better.**
Minimum across the whole governed set: **4.87:1** (`.art-back`, `.cl-cadence-label`).

New supporting labels on light surfaces inherit the accessible colour by being
added to the token's selector list in `assets/type/type.css`. Never hard-code a
label colour on a page.
