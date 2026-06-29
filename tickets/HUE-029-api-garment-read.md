---
id: HUE-029
title: Garment read endpoints and inventory filters
type: task
status: done
milestone: 8
batch: api
layer: api
depends_on: [HUE-025, HUE-022]
implements: [FR-35, NFR-6]
tests_required: true
estimate: 3
---

## In plain English
Lets the screens browse the wardrobe: list the garments with the option to filter by clothing type and by colour family together, look at a single item in detail, and fetch each garment's photo and preview picture.

## Background
Inventory browsing (contract §2.6–§2.8): list garments with combinable type AND colour-family filters and pagination, fetch one garment, and serve image/thumbnail bytes. The family filter matches any role; both filter columns are indexed (NFR-6).

## Technical requirements
- `GET /api/garments` with optional `type`, `family` (matches any role), `limit`/`offset` (defaults 500/0), combinable as AND; returns `{garments: [GarmentSummary], total}` (FR-35)
- `GET /api/garments/{id}` → full `Garment`; `404 garment_not_found`
- `GET /api/garments/{id}/image` and `/thumbnail` → binary; `404 garment_not_found`
- Unknown `type`/`family` → `422 invalid_filter`; indexed queries for NFR-6 (perf asserted in HUE-039)

## Definition of done (acceptance criteria)
- [x] Type-only, family-only and combined AND filters return the right garments; `total` correct under limit/offset (FR-35)
- [x] Family filter matches any role including minor; unknown values → `422 invalid_filter`
- [x] Detail and image/thumbnail endpoints return correct bodies / 404
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test-perf` for inventory queries (§12.3.5)) — deferred to HUE-039 which implements the perf suite
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` filter cases (§7.2): type/family/combined over a seeded wardrobe; family matches minor role; `total` under limit/offset; `422 invalid_filter`; detail + image/thumbnail bodies and 404. Perf at 500 in HUE-039.

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `garment_service.py` — `InvalidFilterError`, `GarmentPage`, `_VALID_FAMILIES`,
  `_row_to_result`, `list_garments`, `get_garment`; `schemas.py` — `InventoryResponse`; `garments.py`
  — GET /api/garments (type/family/limit/offset filters), GET /api/garments/{id}, /image, /thumbnail;
  `test_garments.py` extended with 20 new read tests (filters, minor-role match, pagination, 404,
  image/thumbnail serving). `make test-perf` gate deferred to HUE-039 (perf suite not yet built);
  indexes on `type` and `family` already in schema from HUE-016. `make test` → 842 passed, 1
  skipped, 0 warnings; all 5 import contracts kept.
- Sanity: `cd backend && .venv/bin/pytest tests/api/test_garments.py -q`
