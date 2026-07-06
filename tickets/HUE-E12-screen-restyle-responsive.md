---
id: HUE-E12
title: Screen restyle and responsive
type: epic
status: done
milestone: 20
layer: frontend
depends_on: [HUE-E11]
implements: [NFR-11, NFR-7]
tests_required: false
estimate: 8
---

## In plain English
Applies the new look and the mobile/tablet/desktop layouts to each of the six screens, one screen at a time, without changing what they do.

## Summary
With the foundation (E11) in place, restyle each screen to the design system and make it reflow across mobile/tablet/desktop per the responsive wireframes. Behaviour, data and contracts are unchanged; each screen keeps its automated e2e journey green and adds accessibility assertions.

## Scope
- **In scope:** restyle + responsive layout for upload/detect, confirm-and-correct, inventory, garment detail, outfit request, suggestion results; per-screen accessibility; the responsive e2e + accessibility audit.
- **Out of scope:** new features, screens, fields or contract changes.

## Success criteria
All children `done`; every screen matches the design system and reflows per `07-responsive.md`; `make test` and `make test-e2e` green; NFR-11 assertions pass on every screen.

## Children
- HUE-099 — Restyle Upload & detect
- HUE-100 — Restyle Confirm-and-correct
- HUE-101 — Restyle Inventory (Wardrobe)
- HUE-102 — Restyle Garment detail
- HUE-103 — Restyle Outfit request
- HUE-104 — Restyle Suggestion results
- HUE-105 — Responsive e2e journeys and accessibility audit

## References
- docs/06-design-system.md; docs/04-wireframes/ (01–07); docs/05-test-strategy.md §10.3; docs/02-requirements.md NFR-7, NFR-11

## Notes
- 2026-07-05 — created (Milestone 19 ticket generation)
- 2026-07-06 — done. All children (HUE-099–HUE-105) done. `make test` (1120 backend + 273 frontend) and `make test-e2e` (27 passed, 2 skipped) green with zero warnings.
