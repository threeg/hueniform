---
id: HUE-003
title: Frontend skeleton and navigation shell
type: task
status: todo
milestone: 7
batch: scaffolding
layer: frontend
depends_on: [HUE-001]
implements: [NFR-7]
tests_required: false
estimate: 3
---

## Background
The React SPA needs its toolchain, routing and the fixed-sidebar shell (wireframes §2–§3) before any screen can be built. Per the contract, the frontend is built against the API contract independently of the backend, so this skeleton stands alone.

## Technical requirements
- Vite + TypeScript + React app under `frontend/`
- React Router with the three sidebar routes (wireframes §2): `/` Wardrobe, `/add` Add garment, `/suggest` Suggest outfit; plus `/garments/:id` and `/add/confirm`
- TanStack Query provider configured (server-state caching for NFR-6)
- CSS Modules styling; the fixed 190 px left sidebar + main column frame (wireframes §3); desktop only, 1024 px min width (NFR-7)
- Vite dev server proxying `/api` to Uvicorn (architecture §2.5, §5 `make dev`)
- Placeholder route components so navigation renders; real screens arrive in HUE-033–037

## Definition of done (acceptance criteria)
- [ ] Vite + TS + React app builds (`vite build`) and runs (`vite dev`)
- [ ] Sidebar shell and all routes render placeholders; routing works
- [ ] TanStack Query provider mounted; dev proxy to `/api` configured
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Pure scaffolding/styling. Verified by the app building and the sidebar routes resolving. Component and routing tests arrive with the screen tickets; the frontend test harness is HUE-005.

`tests_required: false` — exemption category: **build-plumbing / pure-styling** (toolchain and shell; screen behaviour is in HUE-033–037).

## Notes
- 2026-06-15 — created
