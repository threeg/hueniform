---
id: HUE-029
title: Garment read endpoints and inventory filters
type: task
status: todo
milestone: 8
batch: api
layer: api
depends_on: [HUE-025, HUE-022]
implements: [FR-35, NFR-6]
tests_required: true
estimate: 3
---

## Background
Inventory browsing (contract §2.6–§2.8): list garments with combinable type AND colour-family filters and pagination, fetch one garment, and serve image/thumbnail bytes. The family filter matches any role; both filter columns are indexed (NFR-6).

## Technical requirements
- `GET /api/garments` with optional `type`, `family` (matches any role), `limit`/`offset` (defaults 500/0), combinable as AND; returns `{garments: [GarmentSummary], total}` (FR-35)
- `GET /api/garments/{id}` → full `Garment`; `404 garment_not_found`
- `GET /api/garments/{id}/image` and `/thumbnail` → binary; `404 garment_not_found`
- Unknown `type`/`family` → `422 invalid_filter`; indexed queries for NFR-6 (perf asserted in HUE-039)

## Definition of done (acceptance criteria)
- [ ] Type-only, family-only and combined AND filters return the right garments; `total` correct under limit/offset (FR-35)
- [ ] Family filter matches any role including minor; unknown values → `422 invalid_filter`
- [ ] Detail and image/thumbnail endpoints return correct bodies / 404
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test-perf` for inventory queries (§12.3.5))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` filter cases (§7.2): type/family/combined over a seeded wardrobe; family matches minor role; `total` under limit/offset; `422 invalid_filter`; detail + image/thumbnail bodies and 404. Perf at 500 in HUE-039.

## Notes
- 2026-06-15 — created
