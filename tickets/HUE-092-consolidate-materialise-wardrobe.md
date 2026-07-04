---
id: HUE-092
title: Consolidate materialise_wardrobe into shared materialise_garments
type: task
status: done
milestone: 14
batch: cleanup
layer: tooling
depends_on: [HUE-088]
implements: []
tests_required: true
estimate: 1
---

## In plain English

Removes the last copy-pasted garment-insertion helper so there is exactly one
function to call when tests need garments in the database.

## Background

HUE-088 extracted `materialise_garments(engine, garments, *, derive_families=False)`
into `tests/conftest.py`, consolidating copies from the service and API test suites.
However, `tests/fixtures/wardrobes.py` still contains a near-identical
`materialise_wardrobe(engine, garments)` (lines 229-258) that always derives
families — equivalent to calling the shared helper with `derive_families=True`.

`materialise_wardrobe` is used by:
- `tests/perf/test_bounds.py` (line 42)
- `scripts/seed_test_wardrobe.py` (line 50)

## Technical requirements

1. Replace `materialise_wardrobe` callers with
   `materialise_garments(..., derive_families=True)`.
2. Remove `materialise_wardrobe()` from `tests/fixtures/wardrobes.py`.
3. Update imports in `tests/perf/test_bounds.py` and
   `scripts/seed_test_wardrobe.py`.

## Definition of done (acceptance criteria)

- [ ] `materialise_wardrobe` no longer exists in the codebase
- [ ] All callers use `materialise_garments` from `tests/conftest.py`
- [ ] `make test` passes with zero warnings
- [ ] `make test-perf` passes
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure deduplication. Existing perf and suggestion tests
cover all paths.

`cd backend && .venv/bin/pytest tests/perf/ tests/services/test_suggestion_service.py tests/api/test_suggestions.py -q`

## Notes

- 2026-07-03 — created by `/verify` review of cleanup batch HUE-088-091.
- 2026-07-03 — done. Removed `materialise_wardrobe()` from `tests/fixtures/wardrobes.py` along with its now-unused imports (`uuid`, `datetime`/`timezone`, `Session`, `Engine`, `GarmentColourRow`, `GarmentRow`, `classify`). Updated `tests/perf/test_bounds.py` to import `materialise_garments` from `tests.conftest` and call it with `derive_families=True`. `make test` (1120+188, zero warnings) and `make test-perf` pass. Sanity test: `cd backend && .venv/bin/pytest tests/perf/ tests/services/test_suggestion_service.py tests/api/test_suggestions.py -q`
