---
id: HUE-054
title: Deduplicate GARMENT_TYPES constant in backend
type: task
status: todo
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

- [ ] `api/schemas.py` imports `GARMENT_TYPES` from `matcher.slots`
- [ ] Architecture test verifies storage and matcher constants match
- [ ] All 5 import-linter contracts still pass
- [ ] `make test` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

`cd backend && .venv/bin/pytest tests/test_architecture.py tests/api/ -q`

## Notes

- 2026-06-18 — created by `/verify` complete MVP review.
