---
id: HUE-054
title: Deduplicate GARMENT_TYPES constant in backend
type: task
status: done
milestone: 8
batch: cleanup
layer: services
depends_on: [HUE-013, HUE-016, HUE-025]
implements: []
tests_required: true
estimate: 1
---

## Background

`/verify` of the complete MVP identified that the 8 garment type strings are
independently defined in three backend modules:

- `backend/app/matcher/slots.py:27` (`GARMENT_TYPES` frozenset)
- `backend/app/storage/models.py:18` (tuple in CheckConstraint)
- `backend/app/api/schemas.py:13` (frozenset)

A type-list change would require updating all three. Frontend duplication is
acceptable (separate language/tier), but within the backend a single source of
truth should exist.

## Technical requirements

1. **Canonical source:** `matcher.slots.GARMENT_TYPES` is the architectural
   owner (FR-16 lives in the matcher layer). Keep it there.

2. **Storage import:** `storage/models.py` must not import from matcher
   (import-linter contract #4). Instead, define a `GARMENT_TYPES` constant
   in `storage/models.py` that is verified to match the matcher constant via
   a test in `tests/test_architecture.py`.

3. **API import:** `api/schemas.py` may import from matcher via services, or
   more directly since the import-linter contract allows api→matcher for
   constants. Import `GARMENT_TYPES` from `matcher.slots` and remove the
   local definition.

4. **Architecture test:** Add a test in `tests/test_architecture.py` that
   asserts `storage.models.GARMENT_TYPES == matcher.slots.GARMENT_TYPES`
   to catch drift.

## Definition of done (acceptance criteria)

- [x] `api/schemas.py` imports `GARMENT_TYPES` from `matcher.slots`
- [x] Architecture test verifies storage and matcher constants match
- [x] All 5 import-linter contracts still pass
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

`cd backend && .venv/bin/pytest tests/test_architecture.py tests/api/ -q`

## Notes

- 2026-06-18 — created by `/verify` complete MVP review.
- 2026-06-18 — implemented: `api/schemas.py` local definition removed; imports `GARMENT_TYPES` from `matcher.slots` with `app.api.schemas -> app.matcher.slots` added to contract #5 `ignore_imports` (narrow exception for compile-time constant). `storage/models.py` retains its own tuple (required for `CheckConstraint`). `test_garment_types_consistent` added to `test_architecture.py`. 149 API+arch tests passed, all 5 contracts kept.
