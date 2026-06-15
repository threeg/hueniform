# Hueniform

A local-first, single-user web application that builds a digital wardrobe from garment
photographs, detects each garment's colours, and suggests harmonious outfits using colour theory.

## Quick start

```sh
make setup   # one-time, requires internet: installs deps, fetches rembg model, builds SPA
make run     # offline thereafter: starts the app and prints the URL
```

Open `http://127.0.0.1:0` in a browser (the exact port is printed by `make run`).

## Repository layout

```
docs/       project documentation (brief, requirements, architecture, API contract, test strategy)
tickets/    one Markdown file per ticket; BOARD.md is the execution order
backend/    FastAPI application (Python 3.12)
frontend/   React + TypeScript SPA (Vite)
scripts/    run / setup entry points
data/       runtime state — gitignored (SQLite database, images, thumbnails, staging, models)
```

See `docs/01-project-brief.md` for the full scope and goals, and `docs/00-milestone-plan.md` for
current project status.

## Documentation

| Document | Purpose |
|---|---|
| `docs/01-project-brief.md` | Scope, goals, out-of-scope |
| `docs/02-requirements.md` | Functional and non-functional requirements |
| `docs/03-architecture.md` | Module layout, data model, dependency rule |
| `docs/03-api-contract.md` | Authoritative HTTP contract |
| `docs/04-wireframes/` | Screen designs and navigation |
| `docs/05-test-strategy.md` | Frameworks, conventions, definition of done |
| `docs/00-milestone-plan.md` | Milestones and current build status |

## Ticket system

Work is tracked entirely in Markdown. `tickets/BOARD.md` lists every implementation ticket in
topological order. Each ticket file contains the acceptance criteria and is updated in the same
commit as the code it describes. See `tickets/CONVENTIONS.md` for the system rules.
