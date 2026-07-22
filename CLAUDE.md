# CLAUDE.md — Canonical Working Agreement for erikrmiller.com

**This file is the single source of truth for where and how the ERM Advisory
website is developed. Read it before touching anything.**

Established: 2026-07-09 (workspace audit & standardization).

---

## 1. The one canonical location

| | |
|---|---|
| **Canonical repo (local)** | `~/Documents/erikrmiller-site/` |
| **GitHub repo** | `https://github.com/646RX-hub/erikrmiller.com` |
| **Default branch** | `main` |
| **Live domain** | `https://erikrmiller.com` |
| **Hosting** | GitHub Pages, served from `main` (custom domain via `CNAME`) |

The Git repository is the **only** location where website development happens.
There is no other valid copy. If you are editing a file that is not inside this
repo, stop.

> Folder-name note: macOS may display this directory as
> `Documents:erikrmiller-site:`. It is the same folder as
> `~/Documents/erikrmiller-site/`.

---

## 2. Mandatory pre-flight check (run before EVERY website task)

```bash
pwd                 # must be inside ~/Documents/erikrmiller-site
git status          # confirm branch + known/clean working tree
git remote -v       # must show 646RX-hub/erikrmiller.com
git branch          # confirm current branch (normally main)
```

**Expected**

- `pwd` ends in `erikrmiller-site`
- `git remote -v` -> `origin  https://github.com/646RX-hub/erikrmiller.com.git`
- current branch is `main` (or a deliberate feature branch)

**If any check fails — wrong folder, wrong remote, detached HEAD, or the folder
is not a Git repo — STOP and tell Erik before making any changes.**

---

## 3. Hard rules

1. **Never edit a website folder that is not the active Git repository.**
   Never edit `~/Documents/Claude/Projects/My Website` — it is a stale, non-Git
   copy (see PROJECT_STRUCTURE.md).
2. **Never assume another website copy exists** unless a fresh audit proves it.
3. All publishing follows `WORKFLOW.md` and `ERM-LAUNCH-STANDARD.md`.
4. Working/preview files (`index-*-working.html`, `*-preview.html`,
   `commit-framework-launch.sh`, `_drafts/`, `content-tracker.xlsx`,
   `COWORK_BRIEFING.md`) are gitignored and must never be deployed or committed.
5. Do not delete or move website copies without explicit confirmation from Erik.

---

## 4. Subsystems (all inside the canonical repo)

| Subsystem | Location |
|---|---|
| Search index — build | `scripts/build-search-index.py` |
| Search index — validate | `scripts/validate-search-index.py` |
| Search index — data | `assets/search/search-index.json` |
| Sitemap | `sitemap.xml` (regenerated on publish) |
| robots.txt | `robots.txt` |
| Nav SSOT + validator | `partials/nav.html`, `scripts/validate-nav.py`, `scripts/build-nav.py` |
| Footer SSOT + validator | `partials/footer.html`, `scripts/build-footer.py`, `scripts/validate-footer.py` |
| Blog card validator | `scripts/validate-blog-cards.py` |
| CI (push/PR to main) | `.github/workflows/` (validate-nav, validate-footer, validate-blog-cards, indexnow) |
| Launch standard | `ERM-LAUNCH-STANDARD.md` |
| Editorial standards | `docs/ERM-EDITORIAL-STANDARDS.md` |

**Command Center** and **Social Studio** are NOT part of this repo. They live in
the separate `ERM Content Production Engine` project
(`09_Research_OS/ERM_Command_Center.html`, `ERM_Social_Studio.html`), generated
by `09_Research_OS/Automation/build_command_center.py`. See PROJECT_STRUCTURE.md
for the Command Center path correction applied 2026-07-09 (its `SITE` now
points to the canonical repo, not the stale `My Website` copy).

---

## 5. Deployment

GitHub Pages auto-deploys the `main` branch (no separate build step, no
`gh-pages` branch). Normal publish: commit to `main` -> push -> Pages rebuilds ->
live at `erikrmiller.com`. Full sequence in WORKFLOW.md.
