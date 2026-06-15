---
id: HUE-001
title: Initialise the repository
type: task
status: todo
milestone: 7
batch: scaffolding
layer: repo
depends_on: []
implements: [NFR-3]
tests_required: false
estimate: 2
---

## Background
There is no version-controlled project yet beyond the approved documents. This ticket establishes the single repository (brief §13) so all later work — code and tickets together — lands in one honest history. It unblocks every other ticket.

## Technical requirements
- Initialise a git repository with the brief §13 top-level layout: `/docs`, `/tickets`, `/backend`, `/frontend`, `/scripts`, `/data`
- Add a root `README.md` describing the project, the single-command run (forward reference to NFR-2) and the docs/tickets layout
- Add `.gitignore` covering `/data` runtime state (NFR-3), Python venv/caches, `node_modules`, `frontend/dist`, Hypothesis and coverage caches, and OS cruft (e.g. `.DS_Store`)
- Commit the existing `docs/` and `tickets/` (template, CONVENTIONS, BOARD, all ticket files) as the project's first substantive commit
- Add a licence file if the owner requires one (note in the body; default: omit for a private single-user tool)

## Definition of done (acceptance criteria)
- [ ] Repository initialised with the brief §13 directory layout
- [ ] `README.md` and `.gitignore` present; `/data` is gitignored
- [ ] `docs/` and `tickets/` committed
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Build-plumbing ticket: verified by inspection that the repository initialises, the directory layout matches brief §13, and `git status` is clean after committing docs and tickets. No automated tests.

`tests_required: false` — exemption category: **build-plumbing** (repository initialisation; no numbered-requirement behaviour).

## Notes
- 2026-06-15 — created
