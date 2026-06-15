---
id: HUE-038
title: Single-command run and production serving
type: task
status: todo
milestone: 8
batch: tooling
layer: tooling
depends_on: [HUE-025, HUE-032, HUE-020]
implements: [NFR-1, NFR-2, NFR-3, NFR-8]
tests_required: true
estimate: 3
---

## Background
NFR-2 requires a single command that serves both backend and frontend locally and prints the URL. This ties the skeletons together: `make setup` (online, once) and `make run` (offline) per architecture §5.

## Technical requirements
- `make setup` (online, once): create the venv, install pinned deps, fetch the rembg model (HUE-020), install frontend deps and build the SPA into `frontend/dist/`, `playwright install`
- `make run` (offline, NFR-2): init `data/` + schema if absent, sweep the staging store, start one Uvicorn process serving `/api` and the built SPA at `/` (history fallback), print `http://127.0.0.1:8000`
- Bind to localhost only; no outbound calls at runtime (NFR-1, NFR-8); all state under `data/` (NFR-3)
- Health-gate the printed URL on `GET /api/health` (NFR-2)

## Definition of done (acceptance criteria)
- [ ] `make setup` then `make run` starts the app offline with one command and prints the URL (NFR-2)
- [ ] Built SPA served at `/` with history fallback; `/api` under the same origin; runtime makes no outbound calls (NFR-1, NFR-8)
- [ ] `data/` initialised and swept on startup (NFR-3)
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test-e2e` (the webServer boots this process, §12.3.6))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Verified by the E2E `webServer` booting the production-style process (HUE-040, §9) and the health probe (§7.2). `make run` is the NFR-2 single command; `make setup` itself is verified by being run (§3).

## Notes
- 2026-06-15 — created
