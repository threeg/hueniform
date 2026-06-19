---
id: HUE-084
title: Performance re-baseline at count 25 and wardrobe_500 update
type: task
status: todo
milestone: 14
batch: tooling
layer: tooling
depends_on: [HUE-079, HUE-076, HUE-039]
implements: [NFR-5, NFR-6]
tests_required: true
estimate: 3
---

## Background
NFR-5 is re-baselined for v0.2.0: an outfit request must return in under 2 s at 500 garments
**including at the maximum count of 25** (the cap is count-independent). The `wardrobe_500`
fixture is updated to the new FR-16 categories so the worst case is realistic; the NFR-6 server
half now covers the `order` values (test strategy §8.2).

## Technical requirements
- `backend/tests/fixtures/wardrobes.py::wardrobe_500()` — distribute across the **FR-16 categories** (all slots incl. one-piece and adornments) and the family taxonomy (incl. Cream), seeded/reproducible (§11.2)
- `backend/tests/perf/test_bounds.py` (`perf`): `POST /api/suggestions` with all slots selected and `count = 25` < 2 s (median of 3); a `count = 3` run for comparison (NFR-5); `GET /api/garments` combined `category`+`family` filters with each `order` value < 1 s (median of 3) (NFR-6 server half)
- `make test-perf` runs them; excluded from `make test`

## Definition of done (acceptance criteria)
- [ ] `wardrobe_500()` updated to the FR-16 categories, seeded/reproducible
- [ ] NFR-5 asserted at all-slots/count 25 (median of 3) and count-independence checked (§8.2)
- [ ] NFR-6 server half asserted across `order` values; both pass on the owner's machine
- [ ] `make test-perf` runs them; excluded from the default gate
- [ ] Tests added/updated per §12.2 and passing in `make test`; `make test-perf` green (§12.3.5)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`perf/test_bounds.py` (§8.2): the count-25 and count-3 suggestion timings and the inventory
filter/order timings at 500 garments, median of 3. Mandatory in DoD for suggestion-/inventory-query
tickets (§12.3.5).

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
