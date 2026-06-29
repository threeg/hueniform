---
id: HUE-003
title: Frontend skeleton and navigation shell
type: task
status: done
milestone: 7
batch: scaffolding
layer: frontend
depends_on: [HUE-001]
implements: [NFR-7]
tests_required: false
estimate: 3
---

## In plain English
Builds the basic layout the user will see — a fixed side menu with the main pages it links to — with placeholder pages for now, so the look and the moving-between-screens work before the real screens are filled in.

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
- [x] Vite + TS + React app builds (`vite build`) and runs (`vite dev`)
- [x] Sidebar shell and all routes render placeholders; routing works
- [x] TanStack Query provider mounted; dev proxy to `/api` configured
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
Pure scaffolding/styling. Verified by the app building and the sidebar routes resolving. Component and routing tests arrive with the screen tickets; the frontend test harness is HUE-005.

`tests_required: false` — exemption category: **build-plumbing / pure-styling** (toolchain and shell; screen behaviour is in HUE-033–037).

## Notes
- 2026-06-15 — created
- 2026-06-15 — done: Vite 6 + TypeScript + React 18 SPA under `frontend/`. `createBrowserRouter` with layout route — App renders fixed 190 px sidebar + `<Outlet>`; routes `/`, `/add`, `/add/confirm`, `/garments/:id`, `/suggest` each render a placeholder heading. `TanStack Query v5` provider in `main.tsx`. Vite dev proxy `/api` → `http://127.0.0.1:8000` in `vite.config.ts`. `npm run build` passes (85 modules, 240 kB JS). `make setup` updated to run `npm ci && npm run build`. CSS Modules layout; 1024 px min-width (NFR-7). `vite-env.d.ts` needed for CSS Module type resolution.
