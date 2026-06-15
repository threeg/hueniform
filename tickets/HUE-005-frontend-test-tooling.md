---
id: HUE-005
title: Frontend test tooling and Playwright harness
type: task
status: todo
milestone: 7
batch: tooling
layer: tooling
depends_on: [HUE-003]
implements: [NFR-7]
tests_required: true
estimate: 3
---

## Background
Frontend component tests and the E2E smoke suite need their toolchain in place before screens are built (test strategy §2, §9, §10), all running offline after `make setup`.

## Technical requirements
- Vitest + React Testing Library configured; Vitest coverage (v8 provider), reported not gated (§2.3)
- MSW (Mock Service Worker) set up for in-process, offline request interception (§10.1); empty handler module placeholder filled in HUE-006
- Playwright config with **Chromium and Firefox** projects (NFR-7, §9); `playwright install chromium firefox` invoked by `make setup`
- `e2e/` directory and `playwright.config.ts` with a `webServer` launching the production-style process (journeys added in HUE-040)
- `Makefile`: `test-frontend` (`vitest run --coverage`) folded into `make test`; `test-e2e` (Playwright)

## Definition of done (acceptance criteria)
- [ ] Vitest + RTL + MSW configured and runnable; coverage reported
- [ ] Playwright config with Chromium + Firefox projects; `make setup` installs the browsers
- [ ] `make test-frontend` runs (part of `make test`); `make test-e2e` target exists (journeys in HUE-040)
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
A trivial Vitest smoke test (renders the app shell) confirms the harness runs offline. MSW handlers and Playwright journeys are added in HUE-006 and HUE-040 respectively.

## Notes
- 2026-06-15 — created
