# WORKFLOW.md — erikrmiller.com

Established: 2026-07-09. How work gets published on erikrmiller.com. This and
`ERM-LAUNCH-STANDARD.md` govern all future website work.

---

## 0. Golden rule

All website work happens in the canonical repo only:
`~/Documents/erikrmiller-site/` (GitHub: `646RX-hub/erikrmiller.com`, branch
`main`). Never edit `~/Documents/Claude/Projects/My Website`.

---

## 1. Pre-flight (before EVERY task) — required

```bash
cd ~/Documents/erikrmiller-site
pwd                 # ends in erikrmiller-site
git status          # clean/known tree, on main
git remote -v       # origin -> github.com/646RX-hub/erikrmiller.com
git branch          # confirm branch
```

If any check fails (wrong folder, wrong remote, detached HEAD, not a repo):
**STOP and tell Erik. Make no changes.**

---

## 2. Standard publish workflow (blog post / page)

1. Confirm pre-flight (above).
2. Build the page from the correct template into the right path
   (e.g. `blog/<slug>/index.html`, `resources/<slug>/index.html`). Follow the
   writing rules in `COWORK_BRIEFING.md` and `docs/ERM-EDITORIAL-STANDARDS.md`.
3. Update indexes that reference the new page: homepage feature, `blog.html`,
   relevant hub (`frameworks/index.html` or `resources/index.html`).
4. Regenerate machine surfaces:
   ```bash
   python3 scripts/build-search-index.py     # updates assets/search/search-index.json
   # update sitemap.xml with the new URL(s)
   ```
5. Run all validators (these also run in CI on push):
   ```bash
   python3 scripts/validate-nav.py
   python3 scripts/validate-footer.py
   python3 scripts/validate-blog-cards.py
   python3 scripts/validate-search-index.py
   ```
6. QA: JSON-LD parses, zero broken links, WCAG AA contrast, heading hierarchy,
   meta description 150-160 chars. Flagship launches must additionally meet every
   item in `ERM-LAUNCH-STANDARD.md`.

---

## 3. Commit & deploy

```bash
git add -A
git commit -m "New post: <title>"     # or a clear, specific message
git push origin main
```

- **Deployment is automatic.** GitHub Pages rebuilds `main` and serves it at
  `erikrmiller.com` (custom domain via `CNAME`). There is no separate build step
  and no `gh-pages` branch.
- CI workflows in `.github/workflows/` (validate-nav, validate-footer,
  validate-blog-cards, indexnow) run on push/PR to `main`. A red check means the
  change drifted from an SSOT — fix before relying on it being live.
- Confirm the live URL after Pages finishes (usually 1-2 min):
  `https://erikrmiller.com/blog/<slug>/`.

### Feature branches
For larger changes use a branch (e.g. `footer-ssot-refactor`), open a PR into
`main`, let CI run, then merge. Existing branches: `main`,
`feature/share-of-model-workbench`, `footer-ssot-refactor`, `publish-ce`.

---

## 4. Subsystem quick reference

| Task | Command / file |
|---|---|
| Rebuild search index | `python3 scripts/build-search-index.py` |
| Validate search index | `python3 scripts/validate-search-index.py` |
| Update sitemap | edit `sitemap.xml` (add `<loc>` for new URLs) |
| robots.txt | `robots.txt` (points to `https://erikrmiller.com/sitemap.xml`) |
| Nav change | edit `partials/nav.html`, run `build-nav.py`, then `validate-nav.py` |
| Footer change | edit `partials/footer.html`, run `build-footer.py`, then `validate-footer.py` |
| Command Center / Social Studio | separate project — `ERM Content Production Engine/09_Research_OS/` (see PROJECT_STRUCTURE.md) |

---

## 5. Handling the stale copy (`My Website`)

Do not edit or deploy from it. Before it is removed, its drift must be
reconciled, not lost:

1. Diff each differing file against the repo:
   ```bash
   diff -u ~/Documents/erikrmiller-site/index.html "~/Documents/Claude/Projects/My Website/index.html"
   ```
   (repeat for `robots.txt`, `about.html`, and anything else flagged in the audit)
2. Port any wanted change into the canonical repo, commit, push.
3. Only then archive/remove the stale copy — with Erik's explicit confirmation.
4. Command Center `SITE` has already been repointed to
   `~/Documents/erikrmiller-site/` (2026-07-09). Regenerate on Erik's machine
   with `python3 build_command_center.py` to refresh the views.

---

## 6. Rules for all future development

- One repo. One branch of truth (`main`). No parallel copies.
- Pre-flight before every task; stop on failure.
- Never deploy gitignored working/preview files.
- Keep nav, footer, search index, and sitemap in sync via their scripts.
- Update `CLAUDE.md` / `PROJECT_STRUCTURE.md` / `WORKFLOW.md` when the setup
  changes so they stay the single source of truth.
