---
id: HUE-032
title: Frontend API client, query layer and shared components
type: task
status: todo
milestone: 8
batch: frontend
layer: frontend
depends_on: [HUE-003, HUE-005, HUE-006]
implements: [FR-5]
tests_required: true
estimate: 5
---

## Background
Every screen needs a typed API client, TanStack Query hooks and the shared visual components (wireframes §3) before it can be built. Per the contract the frontend is built against the contract and MSW independently of the backend.

## Technical requirements
- A typed client + TanStack Query hooks for every endpoint, derived from the contract (`contract-examples.ts`, HUE-006)
- Error-envelope handling surfacing the plain-language `message` (never the `code`) (contract §1.3)
- Shared components (wireframes §3): Swatch (renders `hex`, FR-5), Palette strip (position order, width ∝ proportion), Garment card, Error banner, Warning banner, Loading state
- Type-label capitalisation helper (the eight FR-16 identifiers); built against MSW handlers (HUE-006)

## Definition of done (acceptance criteria)
- [ ] Typed client + query hooks cover every contract endpoint; errors surface the `message` only
- [ ] Shared components render swatches from `hex` (FR-5), palette strips in position order, cards, banners, loading states
- [ ] Components tested against MSW with the contract example bodies
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Vitest + RTL + MSW (§10.1): swatch renders the `hex`; palette strip orders by position with proportional widths; error banner shows `message` not `code`; query hooks consume the contract-shaped handlers.

## Notes
- 2026-06-15 — created
