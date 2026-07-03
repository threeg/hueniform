---
id: HUE-090
title: Replace hardcoded slot strings with matcher constants
type: task
status: todo
milestone: 14
batch: cleanup
layer: services
depends_on: [HUE-068]
implements: []
tests_required: true
estimate: 1
---

## In plain English

Swaps raw `"lower_body"` and `"base"` strings in the suggestion service for the
named constants that already exist in the matcher, making future slot renames safer.

## Background

`/verify` of the v0.2.0 batch identified five occurrences of hardcoded slot name
strings in `suggestion_service.py` (lines 442–444, 480–482) where named constants
already exist:

- `"lower_body"` → `C.MANDATORY_SLOT`
- `"base"` → `C.ONE_PIECE_UPPER_SLOT`

Using the constants ensures consistency with the matcher and reduces the risk of
silent breakage if slot keys are ever renamed.

## Technical requirements

1. Replace `"lower_body"` at lines 442, 443, 480 with `C.MANDATORY_SLOT`.
2. Replace `"base"` at lines 444, 482 with `C.ONE_PIECE_UPPER_SLOT`.
3. No behavioural change — values are identical.

## Definition of done (acceptance criteria)

- [ ] No raw `"lower_body"` or `"base"` slot strings remain in `suggestion_service.py`
- [ ] All references use `C.MANDATORY_SLOT` / `C.ONE_PIECE_UPPER_SLOT`
- [ ] `make test` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — this is a pure rename. Existing tests verify behaviour.

`cd backend && .venv/bin/pytest tests/services/test_suggestion_service.py -q`

## Notes

- 2026-07-03 — created by `/verify` review of v0.2.0 batch.
