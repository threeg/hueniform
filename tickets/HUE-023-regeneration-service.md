---
id: HUE-023
title: Regeneration service
type: task
status: todo
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
- [ ] Confirmed regeneration replaces palette + type in place (same id/image), sets `regenerated_at` (FR-33)
- [ ] Invalid/expired/foreign/consumed tokens are rejected; without a valid token nothing changes (FR-32)
- [ ] Server-side family derivation and palette validation applied
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Regeneration-flow tests (§7.3): `regenerate` leaves record+image untouched and returns a §2.3-shaped proposal + `garment_id`; replacement keeps id/image, sets `regenerated_at`, consumes the token (second attempt → 409); foreign/expired tokens → 409; the FR-32 'no field-edit path' assertion.

## Notes
- 2026-06-15 — created
