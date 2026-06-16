---
id: HUE-023
title: Regeneration service
type: task
status: done
milestone: 8
batch: services
layer: services
depends_on: [HUE-022, HUE-021]
implements: [FR-32, FR-33]
tests_required: true
estimate: 3
---

## Background
Regeneration re-runs detection on the stored photograph and, on confirmation, replaces the palette and type in place — same id, same image (FR-33). Requiring a garment-bound regeneration token is how FR-32 is enforced: there is no field-edit path (architecture §4.2).

## Technical requirements
- `app/services/garment_service.py` (regeneration path): accept a regeneration token bound to the garment; replace colour rows and type in place, same `id`, same `image_file`; stamp `regenerated_at`
- Token rules: absent / expired / consumed / bound to a different garment → rejected (the §2.10 `409` cases)
- Re-derive families server-side (FR-1) and validate the palette as in confirm-save
- FR-32 enforcement: replacement only completes a regeneration; no other mutation path exists

## Definition of done (acceptance criteria)
- [x] Confirmed regeneration replaces palette + type in place (same id/image), sets `regenerated_at` (FR-33)
- [x] Invalid/expired/foreign/consumed tokens are rejected; without a valid token nothing changes (FR-32)
- [x] Server-side family derivation and palette validation applied
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
Regeneration-flow tests (§7.3): `regenerate` leaves record+image untouched and returns a §2.3-shaped proposal + `garment_id`; replacement keeps id/image, sets `regenerated_at`, consumes the token (second attempt → 409); foreign/expired tokens → 409; the FR-32 'no field-edit path' assertion.

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: added `confirm_regeneration` and `RegenerationTokenError` to `garment_service.py`; `_update_garment_in_place` helper deletes old colour rows (flush) then inserts new ones; token consumed via `staging.move()` (same-content overwrite of stored image); `tests/services/test_regeneration_service.py` (15 tests — happy path, token consumed, family re-derivation, missing/expired/foreign/unbound token all → RegenerationTokenError, type + palette validation). `make test` → 716 passed, 1 skipped, 0 warnings.
- Sanity: `cd backend && .venv/bin/pytest tests/services/test_regeneration_service.py -q`
