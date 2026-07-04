---
id: HUE-093
title: Drop import aliases for shared test helpers
type: task
status: done
milestone: 14
batch: cleanup
layer: tooling
depends_on: [HUE-092]
implements: []
tests_required: true
estimate: 1
---

## In plain English

Renames test call sites to use the canonical helper names, removing confusing
aliases that make the codebase harder to search.

## Background

When HUE-088 extracted shared helpers into `tests/conftest.py`, the service test
files aliased the new names back to the old private names to avoid renaming every
call site:

- `make_test_jpeg as _make_jpeg_bytes` (`test_garment_service.py`,
  `test_regeneration_service.py`)
- `stage_test_image as _stage_image` (same files)
- `materialise_garments as _materialise` (`test_suggestion_service.py`)

The API test files already use the canonical names. The inconsistency makes
grepping for helper usage unreliable and hides the refactor from future readers.

## Technical requirements

1. In `tests/services/test_garment_service.py`: import `make_test_jpeg` and
   `stage_test_image` without aliases; rename all `_make_jpeg_bytes` call sites
   to `make_test_jpeg` and all `_stage_image` call sites to `stage_test_image`.
2. In `tests/services/test_regeneration_service.py`: same as above.
3. In `tests/services/test_suggestion_service.py`: import `materialise_garments`
   without alias; rename all `_materialise` call sites to `materialise_garments`.

## Definition of done (acceptance criteria)

- [ ] No aliased imports of shared test helpers remain in service tests
- [ ] All call sites use canonical names matching the function definitions
- [ ] `make test` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure rename. Existing tests cover all paths.

`cd backend && .venv/bin/pytest tests/services/ -q`

## Notes

- 2026-07-03 — created by `/verify` review of cleanup batch HUE-088-091.
- 2026-07-03 — done. Removed `as _make_jpeg_bytes`, `as _stage_image`, and `as _materialise` aliases from `tests/services/test_garment_service.py`, `test_regeneration_service.py`, and `test_suggestion_service.py`. Renamed all call sites to `make_test_jpeg`, `stage_test_image`, and `materialise_garments` respectively. `make test` (1120+188, zero warnings) passes. Sanity test: `cd backend && .venv/bin/pytest tests/services/ -q`
