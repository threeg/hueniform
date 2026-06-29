---
id: HUE-055
title: Type-safe colour_out converter with Protocol
type: task
status: done
milestone: 8
batch: cleanup
layer: api
depends_on: [HUE-044]
implements: []
tests_required: true
estimate: 1
---

## In plain English
Tightens up the behind-the-scenes handling of colour information so mistakes are caught automatically during development, making the app more reliable as it changes.

## Background

`/verify` of the complete MVP identified that `colour_out()` in
`backend/app/api/converters.py` accepts an untyped `object` parameter and
uses `# type: ignore[attr-defined]` on all seven field accesses. This defeats
static type checking and masks potential errors if the shape of `SavedColour`
or `ColourProposal` changes.

## Technical requirements

1. **Define a `ColourLike` Protocol** (in `converters.py` or `schemas.py`)
   with the 7 required attributes: `h`, `s`, `l`, `family`, `neutral`,
   `hex`, `proportion`.

2. **Type the `colour_out()` parameter** as `ColourLike` instead of `object`.

3. **Remove all `# type: ignore[attr-defined]`** comments from the function.

4. **Verify** that `SavedColour` (from `garment_service`) and
   `ColourProposal` (from `detection_service`) structurally satisfy the
   protocol without requiring explicit inheritance.

## Definition of done (acceptance criteria)

- [x] `ColourLike` Protocol defined with all 7 attributes
- [x] `colour_out()` parameter typed as `ColourLike`
- [x] No `type: ignore` comments in `converters.py`
- [x] All existing API tests still pass unchanged
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure type-safety refactor. Existing tests cover all paths.

`cd backend && .venv/bin/pytest tests/api/ -q`

## Notes

- 2026-06-18 — created by `/verify` complete MVP review.
- 2026-06-18 — implemented: `ColourLike` Protocol defined in `converters.py` with all 7 attributes; `colour_out()` parameter typed as `ColourLike`; all three `# type: ignore[attr-defined]` comments removed. 146 API tests passed.
