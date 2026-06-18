---
id: HUE-049
title: Extract shared GARMENT_TYPES constant and remove TYPE_LABELS duplication
type: task
status: done
milestone: 8
batch: cleanup
layer: frontend
depends_on: [HUE-032, HUE-034, HUE-035]
implements: []
tests_required: true
estimate: 1
---

## Background

`/verify` of the frontend batch identified two duplication issues around garment
type constants:

1. The 8-element `GARMENT_TYPES` array is defined independently in both
   `AddConfirm.tsx:12-15` and `Wardrobe.tsx:9-11`.
2. `Wardrobe.tsx:13-16` defines a local `TYPE_LABELS` object that duplicates the
   mapping already available via the `typeLabel()` utility function in
   `frontend/src/utils/typeLabel.ts`.

## Technical requirements

1. **Export `GARMENT_TYPES`** from `frontend/src/utils/typeLabel.ts` as a single
   source of truth for the ordered array of garment type identifiers.

2. **Import in consumers** — replace the local arrays in `AddConfirm.tsx` and
   `Wardrobe.tsx` with the shared import.

3. **Remove `TYPE_LABELS`** from `Wardrobe.tsx` — use the existing `typeLabel()`
   function instead of the local lookup object.

## Definition of done (acceptance criteria)

- [x] `GARMENT_TYPES` defined in exactly one place and imported by consumers
- [x] `TYPE_LABELS` object removed from `Wardrobe.tsx`; `typeLabel()` used instead
- [x] All existing frontend tests still pass unchanged
- [x] `make test-frontend` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure refactor. Existing tests cover all paths.

`cd frontend && npx vitest run`

## Notes

- 2026-06-17 — created by `/verify` review of frontend batch (HUE-032–037).
- 2026-06-17 — implemented: exported `GARMENT_TYPES` from `typeLabel.ts`; removed local definitions from `AddConfirm.tsx` and `Wardrobe.tsx`; replaced `TYPE_LABELS[t]` with `typeLabel(t)`. 133 tests passed, zero warnings.
