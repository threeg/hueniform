---
id: HUE-091
title: Use pre-computed family in anchor family filter
type: task
status: todo
milestone: 14
batch: cleanup
layer: services
depends_on: [HUE-087]
implements: []
tests_required: true
estimate: 2
---

## In plain English

The anchor colour filter currently re-derives each garment's colour families from
scratch; this ticket switches it to use the families already stored in the database,
avoiding ~1,500 redundant classification calls per request.

## Background

`/verify` of the v0.2.0 batch identified that `_apply_anchor_family_filter()` in
`suggestion_service.py` (lines 286–307) re-classifies every garment's colours from
HSL to derive family membership:

```python
families = {_classify(c.h, c.s, c.l) for c in g.colours}
```

The `family` field is already computed at garment-confirm time and stored on
`GarmentColourRow`. The loaded `Colour` dataclass carries this value, so the filter
can read it directly instead of re-classifying.

## Technical requirements

1. Replace the `{_classify(c.h, c.s, c.l) for c in g.colours}` comprehension with
   `{c.family for c in g.colours}` (or equivalent access to the pre-computed field).
2. Verify the `Colour` dataclass (or equivalent) carries `family` from the DB load
   path; if not, thread it through from `_load_wardrobe()`.
3. Behaviour must be identical — same filter semantics, same error conditions.

## Definition of done (acceptance criteria)

- [ ] `_apply_anchor_family_filter()` reads pre-computed family, not re-classified HSL
- [ ] No `_classify()` call remains in the filter path
- [ ] All existing suggestion service and API tests pass unchanged
- [ ] `make test` passes with zero warnings
- [ ] `make test-perf` still passes (NFR-5)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — this is a pure optimisation. Existing tests verify behaviour.

`cd backend && .venv/bin/pytest tests/services/test_suggestion_service.py tests/api/test_suggestions.py -q`

## Notes

- 2026-07-03 — created by `/verify` review of v0.2.0 batch.
