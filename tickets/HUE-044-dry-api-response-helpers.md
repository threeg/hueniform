---
id: HUE-044
title: DRY API response conversion helpers
type: task
status: todo
milestone: 8
batch: cleanup
layer: api
depends_on: [HUE-031]
implements: []
tests_required: true
estimate: 2
---

## Background

`/verify` of the API batch identified `ColourOut` construction logic duplicated
in four places and `GarmentResult → GarmentSummary` conversion duplicated in two
modules. Divergence risk if the schema changes.

## Technical requirements

1. **Extract shared `colour_out()` helper** — the identical 7-field `ColourOut`
   construction appears in:
   - `app/api/garments.py:52-60` (`_colours_out`)
   - `app/api/suggestions.py:34-39` (inline in `_result_to_summary`)
   - `app/api/detections.py:87-98` (inline in `upload_and_detect`)
   Move to `app/api/schemas.py` or a new `app/api/converters.py`; import from all
   three route modules.

2. **Unify `GarmentSummary` builder** — `garments.py:63-70` (`_to_summary`) and
   `suggestions.py:29-42` (`_result_to_summary`) perform the same transformation.
   Consolidate into one function alongside the colour helper.

3. **Extract `_require_garment()` helper** — four identical
   `try: get_garment(...) except GarmentNotFoundError: raise AppError(404, ...)`
   blocks in `garments.py` (lines 166-167, 180-181, 194-195, 305-306). Replace
   with a single helper.

## Definition of done (acceptance criteria)

- [ ] `ColourOut` construction exists in exactly one place
- [ ] `GarmentSummary` construction exists in exactly one place
- [ ] `_require_garment` replaces four identical try/except blocks
- [ ] All existing API tests still pass unchanged
- [ ] `make test` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure refactor. Existing tests cover all paths.

`cd backend && .venv/bin/pytest tests/api/ -q`

## Notes

- 2026-06-16 — created by `/verify` review of API batch (HUE-025–031).
