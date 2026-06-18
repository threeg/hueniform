---
id: HUE-042
title: DRY garment_service internal helpers
type: task
status: done
milestone: 8
batch: cleanup
layer: services
depends_on: [HUE-022, HUE-023]
implements: []
tests_required: true
estimate: 1
---

## Background

`/verify` of the services batch identified three copy-paste blocks inside
`app/services/garment_service.py` and one dead constant in
`tests/services/test_suggestion_service.py`.

## Technical requirements

1. **Extract `_validate_type(garment_type)`** — the identical 4-line type-guard
   block appears in both `confirm` (lines 146–149) and `confirm_regeneration`
   (lines 236–239).
2. **Extract `_build_saved_colours(colours, families)`** — the identical 12-line
   comprehension building `SavedColour` tuples appears in `confirm`
   (lines 180–191) and `_update_garment_in_place` (lines 366–377).
3. **Extract `_add_colour_rows(session, garment_id, colours, families)`** — the
   identical insert loop appears in `_insert_garment` (lines 304–315) and
   `_update_garment_in_place` (lines 351–362).
4. **Remove dead `_RNG`** — `test_suggestion_service.py` line 74 defines
   `_RNG = random.Random(42)` which is never used (every call site uses the
   `_rng()` factory).

## Definition of done (acceptance criteria)

- [x] Three extracted helpers replace six duplicated blocks
- [x] Dead `_RNG` constant removed
- [x] All existing service tests still pass
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — this is a pure refactor. Existing tests cover all paths.

`cd backend && .venv/bin/pytest tests/services/ -q`

## Notes

- 2026-06-16 — created by `/verify` review of services batch (HUE-021–024).
- 2026-06-17 — done. Extracted `_validate_type`, `_build_saved_colours`, and `_add_colour_rows` into the `# Internal helpers` section; replaced all six duplicated blocks. Removed dead `_RNG = random.Random(42)` from test_suggestion_service.py. `make test` 892 passed, zero warnings.
