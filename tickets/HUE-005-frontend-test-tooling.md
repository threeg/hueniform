---
id: HUE-005
title: Frontend test tooling and Playwright harness
type: task
status: done
milestone: 7
batch: tooling
layer: tooling
depends_on: [HUE-003]
implements: [NFR-7]
tests_required: true
estimate: 3
---

## In plain English
Sets up the tools for automatically checking that the screens work correctly and that a user can click through a whole journey, including testing in more than one web browser, so screens can be tested as soon as they are built.

## Background
Frontend component tests and the E2E smoke suite need their toolchain in place before screens are built (test strategy §2, §9, §10), all running offline after `make setup`.

## Technical requirements
- Vitest + React Testing Library configured; Vitest coverage (v8 provider), reported not gated (§2.3)
- MSW (Mock Service Worker) set up for in-process, offline request interception (§10.1); empty handler module placeholder filled in HUE-006
- Playwright config with **Chromium and Firefox** projects (NFR-7, §9); `playwright install chromium firefox` invoked by `make setup`
- `e2e/` directory and `playwright.config.ts` with a `webServer` launching the production-style process (journeys added in HUE-040)
- `Makefile`: `test-frontend` (`vitest run --coverage`) folded into `make test`; `test-e2e` (Playwright)

## Definition of done (acceptance criteria)
- [x] Vitest + RTL + MSW configured and runnable; coverage reported
- [x] Playwright config with Chromium + Firefox projects; `make setup` installs the browsers
- [x] `make test-frontend` runs (part of `make test`); `make test-e2e` target exists (journeys in HUE-040)
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
A trivial Vitest smoke test (renders the app shell) confirms the harness runs offline. MSW handlers and Playwright journeys are added in HUE-006 and HUE-040 respectively.

## Notes
- 2026-06-15 — created
- 2026-06-15 — done. Vitest 3 + RTL + MSW 2 wired; `src/App.test.tsx` smoke test passes. Playwright config at `e2e/playwright.config.ts` with Chromium + Firefox projects. `make test` gate passes (2 backend tests, 1 frontend test, 5 import-linter contracts, matcher 100% coverage). Used `httpx2` (not `httpx`) for starlette 1.3 TestClient compatibility; MSW handler stub in `src/test/handlers.ts` filled by HUE-006.
