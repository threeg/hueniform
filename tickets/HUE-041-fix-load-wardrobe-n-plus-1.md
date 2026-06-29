---
id: HUE-041
title: Fix N+1 query in suggestion_service _load_wardrobe
type: task
status: done
milestone: 8
batch: cleanup
layer: services
depends_on: [HUE-024]
implements: []
tests_required: true
estimate: 2
---

## In plain English
Speeds up outfit suggestions by gathering all the wardrobe's colour information in one go instead of fetching it piece by piece, which keeps the app fast even with hundreds of garments.

## Background

`/verify` of the services batch identified an N+1 query pattern in
`app/services/suggestion_service.py:_load_wardrobe`.  The function executes one
`SELECT` against `GarmentRow`, then inside the loop issues a separate
`SELECT … WHERE garment_id = ?` for each row's colour records.  At the NFR-5
scale (500 garments) this compounds into 501 queries per suggestion request and
will likely fail `make test-perf`.

## Technical requirements

- Replace the per-garment colour query with a single bulk
  `SELECT * FROM garment_colours` (or `WHERE garment_id IN (…)`), grouped in
  Python by `garment_id`.
- Preserve the existing `Garment` construction and `id(g) → GarmentRow` identity
  index contract — callers must not change.
- The `idx_colours_garment` index already exists to support this pattern.
- Honour the dependency rule: `services` may import `storage` and `matcher`.

## Definition of done (acceptance criteria)

- [x] `_load_wardrobe` issues at most 2 queries (garments + colours), not N+1
- [x] All existing `test_suggestion_service.py` tests still pass
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

Existing test suite covers correctness; the structural change can be verified by
inspecting the query count (or by confirming `make test-perf` at 500 garments
once HUE-039 lands).

`cd backend && .venv/bin/pytest tests/services/test_suggestion_service.py -q`

## Notes

- 2026-06-16 — created by `/verify` review of services batch (HUE-021–024).
  Critical: should be promoted into the main sequence before HUE-039
  (performance suite) to avoid a gate failure.
- 2026-06-16 — done: replaced N+1 loop in `_load_wardrobe` with two bulk queries
  (one for `GarmentRow`, one for all `GarmentColourRow`); colours grouped in Python
  by `garment_id`. Identity index contract unchanged. `make test` → 739 passed,
  1 skipped, 0 warnings.
- Sanity: `cd backend && .venv/bin/pytest tests/services/test_suggestion_service.py -q`
