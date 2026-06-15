---
id: HUE-021
title: Detection service and staging orchestration
type: task
status: todo
milestone: 8
batch: services
layer: services
depends_on: [HUE-019, HUE-017]
implements: [FR-24, FR-26, FR-27, FR-28]
tests_required: true
estimate: 5
---

## Background
The detection service orchestrates the upload→detect step (architecture §2.4, §4.1): stage the validated file, run the pipeline, persist the proposal in the sidecar, and expose it for confirm-and-correct — writing nothing to the database (FR-24).

## Technical requirements
- `app/services/detection_service.py`: stage the upload (HUE-017), run the pipeline (HUE-019), write the proposal + `fallback_used` + content type to the sidecar, return token, expiry, colours, image info
- Regeneration variant: run the pipeline on a stored photograph, returning a token bound to the `garment_id`
- Honour the TTL and the startup sweep (HUE-017); detection inside tests uses the §6.2 injected seams
- May import `detection`, `storage` and `matcher` (dependency rule); not `api`

## Definition of done (acceptance criteria)
- [ ] Staging the upload + running the pipeline returns a contract-shaped proposal; nothing written to the DB (FR-24)
- [ ] `fallback_used` surfaced for the FR-27 warning; proposal classified per the taxonomy (FR-26, FR-28)
- [ ] Regeneration produces a garment-bound token; TTL/sweep honoured
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Service/integration tests (§7.3) with injected detection seams: staging creates file+sidecar and nothing in the DB; the proposal shape matches §2.3; regeneration binds the token to the garment; expiry handling. Default gate; the real model is exercised via `make test-model` where composed.

## Notes
- 2026-06-15 — created
