---
id: HUE-022
title: Garment service: confirm-save and delete
type: task
status: todo
milestone: 8
batch: services
layer: services
depends_on: [HUE-021, HUE-016, HUE-017, HUE-009]
implements: [FR-1, FR-25, FR-29, FR-30, FR-34]
tests_required: true
estimate: 5
---

## Background
Confirming a detection saves a garment in one transaction (architecture §4.1): re-derive every family server-side from submitted HSL (FR-1), validate count and the sum of 100, move the staged image, generate the thumbnail and insert both tables. Delete removes the record (cascade) and its files (FR-34).

## Technical requirements
- `app/services/garment_service.py`: consume the detection token; re-derive `family` from submitted HSL via `matcher.taxonomy` (FR-1 — never trust a client family); validate 1–4 colours summing to 100 (FR-6/FR-29)
- One transaction: move staged image → `data/images/`, generate thumbnail, insert `garments` + `garment_colours`; abandonment leaves nothing (FR-24, FR-30)
- Atomicity: a mid-confirmation failure (e.g. thumbnail generation) leaves no rows and no moved image
- Delete: remove the record (cascade to colours) and the image + thumbnail files (FR-34)
- Imports `storage`, `matcher.taxonomy`, the detection service; not `api`

## Definition of done (acceptance criteria)
- [ ] Save re-derives families server-side, validates the palette, and creates the garment + colours in one transaction (FR-1, FR-29, FR-30)
- [ ] Staged image moved and thumbnail generated (FR-25); a forced mid-save failure rolls back fully (atomicity)
- [ ] Delete removes record, colour rows (cascade) and both files (FR-34)
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Lifecycle tests (§7.3): confirm consumes the token, moves the image, inserts both tables; second confirm with the same token → consumed; server-side family derivation cross-checked against `matcher.taxonomy`; forced-failure atomicity; delete cascade + file removal.

## Notes
- 2026-06-15 — created
