---
id: HUE-030
title: Garment regenerate, replace and delete endpoints
type: task
status: done
milestone: 8
batch: api
layer: api
depends_on: [HUE-029, HUE-023, HUE-027]
implements: [FR-32, FR-33, FR-34]
tests_required: true
estimate: 3
---

## Background
Regenerate/replace/delete (contract §2.9–§2.11): `POST …/regenerate` returns a fresh proposal bound to the garment; token-gated `PUT` replaces palette+type in place (the FR-32 enforcement — no field-edit path); `DELETE` removes the record and files.

## Technical requirements
- `POST /api/garments/{id}/regenerate`: §2.3-shaped proposal + `garment_id`, record/image untouched; `404 garment_not_found`
- `PUT /api/garments/{id}` with `regeneration_token`, `type`, `colours`: replace in place via the service; `404 garment_not_found`; `409 invalid_regeneration_token` (absent/expired/consumed/foreign); `422` as §2.5
- `DELETE /api/garments/{id}`: `204`; `404 garment_not_found` (UI owns the confirmation step)
- FR-32: `PUT` without a valid regeneration token always fails — proving no field-edit path

## Definition of done (acceptance criteria)
- [x] Regenerate returns a garment-bound proposal leaving the record/image untouched (FR-33)
- [x] `PUT` replaces in place (same id/image, `regenerated_at` set); all `409` token cases handled (FR-32/FR-33)
- [x] `DELETE` returns 204 and removes record + files (FR-34)
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` regeneration/delete cases (§7.3): the full regeneration flow; `409` token cases; the FR-32 'no valid token → always fails' assertion; delete 204 + cascade + file removal.

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `garments.py` extended with `POST /api/garments/{id}/regenerate`,
  `PUT /api/garments/{id}`, `DELETE /api/garments/{id}`; `schemas.py` — `GarmentUpdateRequest`,
  `RegenerationProposalResponse`; `test_garments.py` extended with 22 new HUE-030 tests
  (regenerate shape + record-unchanged assertion, FR-32 no-field-edit, all PUT token cases,
  delete 204 + cascade + double-delete). `run_regeneration` mocked in regenerate tests to
  avoid loading the rembg model; PUT tests use `staging.stage(garment_id=...)` directly.
  `make test` → 862 passed, 1 skipped, 0 warnings; all 5 import contracts kept;
  `app/api/garments.py` 100% line+branch coverage.
- Sanity: `cd backend && .venv/bin/pytest tests/api/test_garments.py -q`
