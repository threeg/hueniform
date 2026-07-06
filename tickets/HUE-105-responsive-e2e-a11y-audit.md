---
id: HUE-105
title: Responsive e2e journeys and accessibility audit
type: task
status: todo
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
- [ ] Smoke journeys run and pass at the three viewports (`make test-e2e`)
- [ ] Every restyled screen carries a `jest-axe` assertion (NFR-11); no violations
- [ ] `make test` and `make test-e2e` green with zero warnings
- [ ] Epic HUE-E12 closed if this is its last child
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
- Playwright responsive journeys (§10.3); `make test-e2e`. Confirms NFR-7 structure and NFR-11 across the app.
