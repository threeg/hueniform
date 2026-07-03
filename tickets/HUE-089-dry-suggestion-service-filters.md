---
id: HUE-089
title: Unify suggestion_service wardrobe filter functions
type: task
status: done
milestone: 14
batch: cleanup
layer: services
depends_on: [HUE-087]
implements: []
tests_required: true
estimate: 3
---

## In plain English

Three nearly identical filtering functions in the suggestion service are merged into
one, removing copy-paste and eliminating redundant per-garment slot lookups that run
up to 2,000 times per request.

## Background

`/verify` of the v0.2.0 batch identified that `suggestion_service.py` contains three
wardrobe-filtering functions with identical structure:

- `_apply_category_filters()` (lines 198–216)
- `_apply_pins()` (lines 268–283)
- `_apply_anchor_family_filter()` (lines 286–307)

Each scans the full wardrobe, calls `category_to_slot()` per garment, then
keeps/discards based on a slot-specific predicate. With a 500-garment wardrobe this
produces ~2,000 redundant `category_to_slot()` lookups per request because the slot
is recomputed in every pass.

## Technical requirements

1. **Cache slot derivation** — compute `category_to_slot()` once per garment (e.g.
   during `_load_wardrobe()` or as a pre-pass) and attach the result to the garment
   or store in a lookup dict.

2. **Unify the filter pattern** — extract a single
   `_filter_wardrobe(wardrobe, slot_predicate)` helper (or equivalent functional
   composition) that the three callers invoke with their specific predicate. The
   empty-slot check (lines 493–496) should also reuse the cached slots.

3. Behaviour must be identical — same filtering semantics, same error conditions.

## Definition of done (acceptance criteria)

- [ ] Single generic filter helper replaces three copy-paste functions
- [ ] `category_to_slot()` called at most once per garment per request
- [ ] Empty-slot check reuses cached slot data
- [ ] All existing suggestion service and API tests pass unchanged
- [ ] `make test` passes with zero warnings
- [ ] `make test-perf` still passes (NFR-5)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — this is a pure refactor. Existing tests cover all paths.

`cd backend && .venv/bin/pytest tests/services/test_suggestion_service.py tests/api/test_suggestions.py -q`

## Notes

- 2026-07-03 — created by `/verify` review of v0.2.0 batch.
- 2026-07-03 — done. Replaced `_apply_category_filters`, `_apply_pins`, and `_apply_anchor_family_filter` with a single `_filter_wardrobe(wardrobe, slots_for, predicate)` helper. Added a `slots_for: dict[int, str]` pre-pass immediately after `_load_wardrobe()` to call `category_to_slot()` once per garment; all three filter calls and the empty-slot check now read from this dict instead of re-calling the function. Pin validation also uses the cached slot. `make test` passes (1120+188, zero warnings); `make test-perf` passes. Sanity test: `cd backend && .venv/bin/pytest tests/services/test_suggestion_service.py tests/api/test_suggestions.py -q`
