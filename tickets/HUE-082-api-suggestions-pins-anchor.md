---
id: HUE-082
title: POST /api/suggestions — pins and anchor request and validation
type: task
status: done
milestone: 14
batch: api
layer: api
depends_on: [HUE-081, HUE-069]
implements: [FR-44, FR-45]
tests_required: true
estimate: 2
---

## In plain English
Lets an outfit request say "build this around a chosen garment" or "around a particular colour", and makes sure such requests are sensible, sending back a clear message when the choice can't actually be honoured.

## Background
Add the `pins` and `anchor` request fields to `POST /api/suggestions` and their `422` validation
(contract §2.12). Completes the v0.2.0 request `{ slots, pins, anchor, count }` over the
slot-selection (HUE-069) and count (HUE-079) work.

## Technical requirements
- Request: `pins` (map slot key → garment `id`); `anchor` (`{ "family"?, "scheme"? }`)
- Response: the pinned garment appears in its slot in every combination; `echoes` may include minor-adornment echoes
- **Errors (`422 invalid_request`)**: a pin whose garment id is unknown, or whose category does not map to the pinned slot key, or that disagrees with a same-slot category constraint; two pins for one slot; an unknown `anchor.family`/`anchor.scheme`; a contradictory one-piece pin to `lower_body` with `base` selected (FR-50.2)
- **200 — no combination** (unsatisfiable pin/anchor): the zero-result shape with `explanation` + `hint` (FR-43, FR-44, FR-45)

## Definition of done (acceptance criteria)
- [x] `pins`/`anchor` accepted per §2.12; pinned garment present in every combination
- [x] The FR-44/FR-45/FR-50.2 `422 invalid_request` cases returned per contract
- [x] Unsatisfiable pin/anchor → zero-result with `explanation`+`hint` (FR-43)
- [x] Tests added/updated per §12.2 and passing in `make test`; import contracts kept
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_suggestions.py` (§7.4): `pins`/`anchor` honoured in the FR-42-safe invariants; the
full `422` set (unknown/ mismatched/ duplicate pin, unknown family/scheme, one-piece+base);
unsatisfiable → zero-result shape; the §4.9.4 oracle.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-07-02 — implemented. Added `AnchorIn` schema to `schemas.py`; added `pins` and
  `anchor` fields to `SuggestionRequest`. Updated `suggestions.py` to extract
  `anchor_family`/`anchor_scheme` from the anchor object and pass `pins` to `suggest()`;
  added exception handlers for `InvalidPinError` (422 with `slot`/`garment_id` details)
  and `InvalidAnchorError` (422). Two new test classes: `TestPinsField` (6 tests) and
  `TestAnchorField` (7 tests). 1109 backend + 166 frontend tests pass, zero warnings.
- Sanity test: `cd backend && .venv/bin/pytest tests/api/test_suggestions.py::TestPinsField tests/api/test_suggestions.py::TestAnchorField -v`
