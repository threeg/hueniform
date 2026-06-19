---
id: HUE-079
title: POST /api/suggestions — count field and neutral/fallback response
type: task
status: todo
milestone: 14
batch: api
layer: api
depends_on: [HUE-078, HUE-069]
implements: [FR-39, FR-41, FR-43, FR-48]
tests_required: true
estimate: 2
---

## Background
Add the `count` field and the neutral/fallback response semantics to `POST /api/suggestions`
(contract §2.12). Builds on the slot-selection endpoint (HUE-069); pins/anchor are HUE-082.

## Technical requirements
- Request: optional `count` integer **1–25**, **default 3**; `requested_count` echoes the effective count
- Response: `combinations` holds at most `count`, fewer when fewer exist (FR-39); each combination's `scheme` may be `neutral-based` with `fallback: false` (first-class, FR-41); `fallback: true` only for the neutral-fallback retry (FR-43a); zero-result shape with `explanation` + `hint`
- **Errors**: `422 invalid_request` for `count` outside 1–25 (`details: { "count": N }`)

## Definition of done (acceptance criteria)
- [ ] `count` accepted (default 3); `requested_count` echoed; at most `count` returned (FR-39, FR-48)
- [ ] First-class `neutral-based` (`fallback:false`) vs `fallback:true` distinguished per §2.12 (FR-41, FR-43)
- [ ] `422 invalid_request` for `count` out of 1–25 with `details.count`
- [ ] Tests added/updated per §12.2 and passing in `make test`; import contracts kept
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_suggestions.py` (§7.4): `count` at 1/25/default and out-of-range `422`; `requested_count`
echo; first-class-neutral vs fallback response shapes; fewer-than-count. Perf is HUE-084.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
