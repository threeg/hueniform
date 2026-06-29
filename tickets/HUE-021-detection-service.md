---
id: HUE-021
title: Detection service and staging orchestration
type: task
status: done
milestone: 8
batch: services
layer: services
depends_on: [HUE-019, HUE-017]
implements: [FR-24, FR-26, FR-27, FR-28]
tests_required: true
estimate: 5
---

## In plain English
Manages the step where someone uploads a garment photo: it puts the photo in the temporary holding area, works out its colours, and hands back the suggested result for the owner to check and correct, all without committing anything to the permanent wardrobe yet.

## Background
The detection service orchestrates the upload→detect step (architecture §2.4, §4.1): stage the validated file, run the pipeline, persist the proposal in the sidecar, and expose it for confirm-and-correct — writing nothing to the database (FR-24).

## Technical requirements
- `app/services/detection_service.py`: stage the upload (HUE-017), run the pipeline (HUE-019), write the proposal + `fallback_used` + content type to the sidecar, return token, expiry, colours, image info
- Regeneration variant: run the pipeline on a stored photograph, returning a token bound to the `garment_id`
- Honour the TTL and the startup sweep (HUE-017); detection inside tests uses the §6.2 injected seams
- May import `detection`, `storage` and `matcher` (dependency rule); not `api`

## Definition of done (acceptance criteria)
- [x] Staging the upload + running the pipeline returns a contract-shaped proposal; nothing written to the DB (FR-24)
- [x] `fallback_used` surfaced for the FR-27 warning; proposal classified per the taxonomy (FR-26, FR-28)
- [x] Regeneration produces a garment-bound token; TTL/sweep honoured
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
Service/integration tests (§7.3) with injected detection seams: staging creates file+sidecar and nothing in the DB; the proposal shape matches §2.3; regeneration binds the token to the garment; expiry handling. Default gate; the real model is exercised via `make test-model` where composed.

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `app/services/detection_service.py` with `run_detection` and `run_regeneration`; `ColourProposal` and `DetectionResult` dataclasses; hex via `hsl_to_hex`, neutral via `taxonomy.is_neutral`; expires_at read from sidecar; `tests/services/test_detection_service.py` (24 tests across 5 classes — staging I/O, result shape, sidecar fields, fallback surface, regeneration + TTL sweep). `make test` → 671 passed, 1 skipped, 0 warnings.
- Sanity: `cd backend && .venv/bin/pytest tests/services/test_detection_service.py -q`
