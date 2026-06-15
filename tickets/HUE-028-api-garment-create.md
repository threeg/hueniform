---
id: HUE-028
title: Garment create endpoint
type: task
status: todo
milestone: 8
batch: api
layer: api
depends_on: [HUE-027, HUE-022, HUE-026]
implements: [FR-6, FR-25, FR-29, FR-30, FR-31]
tests_required: true
estimate: 3
---

## Background
`POST /api/garments` (contract §2.5) confirms a detection: it validates the palette and type, then the garment service moves the image, generates the thumbnail and creates the garment in one transaction, consuming the token.

## Technical requirements
- `POST /api/garments` with `detection_token`, `type`, `colours` (`ColourIn`); validate 1–4 colours summing to 100 (FR-6/FR-29) and the type (FR-31)
- Delegate to the garment service (HUE-022); server-side family derivation (contract §1.6)
- Errors: `404 detection_not_found` (unknown/expired/consumed), `422 invalid_palette`, `422 invalid_type` (contract §2.5)
- `201` returns the full `Garment` (FR-25, FR-30)

## Definition of done (acceptance criteria)
- [ ] Valid confirm returns the saved `Garment` (201); token consumed; both tables written via the service
- [ ] `422 invalid_palette`/`invalid_type` and `404 detection_not_found` returned per contract §2.5
- [ ] A garment cannot be saved without a confirmed palette and a type (FR-30/FR-31)
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` create cases (§7.2, §7.3): success body matches `Garment`; palette boundary rejections; wrong-implied-family input stored as the server's derivation (cross-checked vs `matcher.taxonomy`); consumed-token 404.

## Notes
- 2026-06-15 — created
