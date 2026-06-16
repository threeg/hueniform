---
id: HUE-045
title: API error code constants and dead validate_palette removal
type: task
status: todo
milestone: 8
batch: cleanup
layer: api
depends_on: [HUE-031]
implements: []
tests_required: true
estimate: 1
---

## Background

`/verify` of the API batch identified two issues: (1) error codes like
`"garment_not_found"` and `"invalid_palette"` are raw string literals across ~15
call sites with no single source of truth, and (2) `schemas.validate_palette()`
is dead code — the module docstring says endpoints should call it, but validation
actually happens in the service layer.

## Technical requirements

1. **Define error code constants** in `app/api/errors.py` (e.g.
   `GARMENT_NOT_FOUND = "garment_not_found"`). Replace all string literals in
   `detections.py`, `garments.py`, and `suggestions.py` with these constants.

2. **Remove dead `validate_palette`** from `app/api/schemas.py:202-218` and
   update the module docstring (lines 6-7) to reflect that palette validation
   lives in the service layer.

## Definition of done (acceptance criteria)

- [ ] Every `AppError` call references a constant from `errors.py`, not a string literal
- [ ] `validate_palette` removed from `schemas.py`; module docstring updated
- [ ] All existing API tests still pass unchanged
- [ ] `make test` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure refactor + dead code removal. Existing tests cover
all error paths.

`cd backend && .venv/bin/pytest tests/api/ -q`

## Notes

- 2026-06-16 — created by `/verify` review of API batch (HUE-025–031).
