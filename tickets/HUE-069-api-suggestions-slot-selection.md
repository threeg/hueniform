---
id: HUE-069
title: POST /api/suggestions — slot-selection and constraint request/response
type: task
status: todo
milestone: 14
batch: api
layer: api
depends_on: [HUE-068, HUE-066, HUE-031]
implements: [FR-36, FR-49, FR-50, FR-51, FR-52]
tests_required: true
estimate: 3
---

## Background
Rewrite the `POST /api/suggestions` request/response to the v0.2.0 shape (contract §2.12) for
the slot-selection model and the per-category constraint. Pins, anchor and count are added by
HUE-082 (E06) and HUE-079 (E09); this ticket lands the `slots` map (`true`/`false`/`{categories}`),
the slot-keyed response with one-piece-once and first-class `neutral-based`, and the relevant
error envelopes.

## Technical requirements
- Request: `{ "slots": { <key>: true | false | { "categories": [...] } } }`, layered over the FR-51 defaults; an empty body `{}` means the defaults and the default count
- Response (combinations): `slots` keyed by slot key, one-piece appearing once under `lower_body`; `scheme` non-null incl. `neutral-based`; `fallback`; `echoes`; `explanation` (contract §2.12)
- Zero-result shape with `explanation` + `hint`
- Errors: `409 empty_slots` (`details.empty_slots`); `422 invalid_request` for an unknown slot key, `lower_body: false` (mandatory), an empty/invalid category constraint (`details.slot`/`invalid_categories`), or a contradictory `lower_body` one-piece-only constraint with `base` selected
- Thin translation over `suggestion_service`; non-determinism permitted (FR-42), within NFR-5

## Definition of done (acceptance criteria)
- [ ] Request/response/zero-result shapes match contract §2.12 exactly (slots bool|{categories})
- [ ] One-piece appears once under `lower_body`; `neutral-based` is first-class (`fallback: false`)
- [ ] `409 empty_slots` and the FR-51/FR-52 `422 invalid_request` cases returned per contract
- [ ] Tests added/updated per §12.2 and passing in `make test`; import contracts kept
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_suggestions.py` (§7.4, §8.1): the FR-42-safe invariants over the selected slots, the
§4.9.4 oracle, the slots-map forms, the `409`/`422` cases (mandatory floor, constraint
validation, one-piece+base contradiction). Perf is HUE-084.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
