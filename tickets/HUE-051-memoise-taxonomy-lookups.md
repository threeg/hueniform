---
id: HUE-051
title: Memoise taxonomy lookups in Suggest, Wardrobe and AddConfirm
type: task
status: todo
milestone: 8
batch: cleanup
layer: frontend
depends_on: [HUE-034, HUE-035, HUE-037]
implements: []
tests_required: true
estimate: 2
---

## Background

`/verify` of the frontend batch identified repeated `taxonomy.families.find()`
lookups without memoisation in three route components:

- `Suggest.tsx:195-208` — `familyHex()` performs a linear search for every echo
  in every combination rendered (O(combos × echoes × families)).
- `Wardrobe.tsx:50-52` — `selectedFamily` lookup runs on every render even when
  taxonomy hasn't changed.
- `AddConfirm.tsx:229-237` — an IIFE performs `taxonomy.families.find()` inline
  on every render when the add-colour panel is open.

## Technical requirements

1. **Suggest.tsx** — pre-build a `Map<string, string>` (family name → hex) via
   `useMemo` keyed on `[taxonomy]`. Replace `familyHex()` with a direct map
   lookup.

2. **Wardrobe.tsx** — wrap the `selectedFamily` lookup and `hslToHex` call in
   `useMemo` keyed on `[taxonomy, familyFilter]`.

3. **AddConfirm.tsx** — replace the IIFE with a `useMemo` that computes the
   preview hex, keyed on `[taxonomy, newFamily]`.

## Definition of done (acceptance criteria)

- [ ] All three taxonomy lookups wrapped in `useMemo` with correct dependency arrays
- [ ] No `taxonomy.families.find()` call outside a memoisation boundary
- [ ] All existing frontend tests still pass unchanged
- [ ] `make test-frontend` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure refactor. Existing tests cover all paths.

`cd frontend && npx vitest run`

## Notes

- 2026-06-17 — created by `/verify` review of frontend batch (HUE-032–037).
