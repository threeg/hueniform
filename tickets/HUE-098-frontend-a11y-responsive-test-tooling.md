---
id: HUE-098
title: Frontend accessibility and responsive test tooling
type: task
status: done
milestone: 20
batch: tooling
layer: tooling
depends_on: [HUE-005]
implements: [NFR-11, NFR-7]
tests_required: true
estimate: 2
---

## In plain English
Adds the test plumbing that lets us automatically check the app is accessible and works at different screen sizes.

## Background
Test strategy §10.3 introduces `jest-axe` (accessibility) in the component gate and Playwright viewport runs (responsive) in the e2e gate. This ticket wires the tooling so screen tickets can use it. All tooling is installed by `make setup` and runs offline (test strategy §3).

## Technical requirements
- Add `jest-axe` (axe-core) to the Vitest + RTL setup with a shared `expectNoAxeViolations` helper and the AA ruleset scoped to contrast + name/role/value.
- Add Playwright viewport presets (mobile ~390, tablet ~834, desktop ~1280) and a helper to run a journey across tiers.
- Ensure both run offline after `make setup`; no new network dependency.

## Definition of done (acceptance criteria)
- [x] `jest-axe` wired into the component harness with a shared helper; a smoke assertion proves it runs
- [x] Playwright viewport presets + per-tier journey helper added
- [x] Everything runs under `make test` / `make test-e2e` offline
- [x] Ticket status + notes updated in the same commit

## Tests / verification
- A trivial component a11y assertion and a single cross-viewport Playwright smoke prove the harness works. `cd frontend && npm run test -- axe --run`.

## Notes

- 2026-07-05 — done. Created `frontend/src/test/a11y.ts` — shared axe helper: `configureAxe` with `runOnly: wcag2a + wcag2aa`, exported `expectNoAxeViolations(container)` shorthand. Updated `frontend/src/test/setup.ts` to call `expect.extend(toHaveNoViolations)` globally. Created `frontend/src/test/axe-smoke.test.tsx` (3 tests: Banner error/warning + LoadingState) — proves harness runs, reachable via `npm run test -- axe --run`. Refactored `shared-components.test.tsx` and `AppShell.test.tsx` to use `expectNoAxeViolations` from `./a11y` and drop their local `expect.extend`. Created `e2e/viewports.ts` with `VIEWPORTS` constants (mobile 390, tablet 834, desktop 1280) and `forEachViewport(page, fn)` helper for per-tier journey assertions. Updated `e2e/playwright.config.ts` with three new responsive projects (mobile/tablet/desktop, scoped to `nav.spec.ts`); existing chromium/firefox projects scoped to `smoke.spec.ts`. Created `e2e/nav.spec.ts` (2 tests: correct nav tier visible, all three destinations reachable) — runs in all three viewport projects. `make test` (1120 backend + 261 frontend, zero warnings). Sanity test: `cd frontend && npm run test -- axe --run`.
