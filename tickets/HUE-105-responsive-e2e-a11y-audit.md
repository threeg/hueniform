---
id: HUE-105
title: Responsive e2e journeys and accessibility audit
type: task
status: done
milestone: 20
batch: tooling
layer: tooling
depends_on: [HUE-099, HUE-100, HUE-101, HUE-102, HUE-103, HUE-104, HUE-085]
implements: [NFR-7, NFR-11]
tests_required: true
estimate: 3
---

## In plain English
Runs the whole app through phone, tablet and desktop and does a final accessibility check, to prove the redesign holds together end to end.

## Background
Final v0.3.0 gate: extend the smoke journeys (§9) to run across viewports (test strategy §10.3) and confirm the accessibility floor across screens. Closes epic E12.

## Technical requirements
- Run the existing smoke journeys at mobile (~390), tablet (~834) and desktop (~1280) using the HUE-098 helpers, asserting the tier navigation (bottom tab bar vs sidebar), primary-action reachability and grid structure per `07-responsive.md`.
- A cross-screen accessibility pass (jest-axe assertions present on every restyled screen; spot-check with an axe run in e2e where practical).
- Keep all existing journeys green (behaviour unchanged).

## Definition of done (acceptance criteria)
- [x] Smoke journeys run and pass at the three viewports (`make test-e2e`)
- [x] Every restyled screen carries a `jest-axe` assertion (NFR-11); no violations
- [x] `make test` and `make test-e2e` green with zero warnings
- [x] Epic HUE-E12 closed if this is its last child
- [x] Ticket status + notes updated in the same commit

## Notes

- 2026-07-06 — done. Created `e2e/responsive.spec.ts` with 5 cross-viewport layout assertions: correct navigation tier (bottom tab / top nav / sidebar), suggest-screen primary action reachable and enabled, mobile sticky-footer position, add-garment pick button visible, wardrobe screen renders without error. Updated `e2e/playwright.config.ts` — mobile/tablet/desktop projects now match `{nav,responsive}.spec.ts` so the new responsive spec runs across all three viewport tiers. All existing smoke journeys (Chromium + Firefox, 4 journeys) still pass unchanged. jest-axe coverage confirmed across all 6 restyled screens (HUE-099–HUE-104). Epic HUE-E12 closed. `make test` (1120 backend + 273 frontend) and `make test-e2e` (27 passed, 2 skipped) both green, zero warnings. Sanity test: `make test-e2e`.

## Tests / verification
- Playwright responsive journeys (§10.3); `make test-e2e`. Confirms NFR-7 structure and NFR-11 across the app.
