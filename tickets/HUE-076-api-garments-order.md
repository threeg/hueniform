---
id: HUE-076
title: Garment API — complete type→category field rename (POST/PUT bodies, GET param, response shapes)
type: task
status: done
milestone: 14
batch: api
layer: api
depends_on: [HUE-029]
implements: [FR-16, FR-35]
tests_required: true
estimate: 2
---

## Background
Complete the v0.2.0 `type` → `category` rename (contract §1.3, §2.5, §2.6, §2.7) across all
garment API shapes. The DB column stays `type` (architecture §3.1); only the API layer changes.
Ordering (FR-47) and `total` are deferred to HUE-086, which depends on this ticket.

The rename was done on the frontend in HUE-067 but not on the backend, breaking POST /api/garments
and causing `g.category` to be `undefined` on the inventory screen.

## Technical requirements
- `GarmentSummary`: rename field `type` → `category` (contract §1.2); update `converters.py`
- `GarmentDetail`: rename field `type` → `category` (contract §1.2); update `converters.py`
- `GarmentCreateRequest`: rename field `type` → `category` (contract §2.5)
- `GarmentUpdateRequest` (regeneration PUT body): rename field `type` → `category` (contract §2.8)
- `GET /api/garments` query param `type` → `category` (contract §2.6); filter behaviour unchanged
- Router (`garments.py`): `body.type` → `body.category` at all call sites
- Update `garment_service.py` type-filter call site if it passes the raw query param name
- **Errors**: `422 invalid_category` *(renamed — v0.2.0, was `invalid_type`)* for unknown category on create/update

## Definition of done (acceptance criteria)
- [ ] All garment response shapes carry `category` (not `type`); no `type` key in API output
- [ ] `POST /api/garments` accepts `category`; rejects unknown value with `422 invalid_category`
- [ ] `PUT /api/garments/{id}` (regeneration) accepts `category`
- [ ] `GET /api/garments` filter param is `category`; `type` param rejected with `422 invalid_filter`
- [ ] Tests added/updated per §12.2 and passing in `make test`; import contracts kept
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` (§7.2): all response assertions updated to `"category"` (not `"type"`);
POST/PUT request bodies use `category`; `422 invalid_category` on unknown value; GET filter uses
`category` param.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-06-24 — scope updated: ordering (FR-47) and `total` split to HUE-086; this ticket narrowed
  to the complete `type`→`category` rename. Dependency on HUE-075 removed (rename is independent
  of the ordering service work).
- 2026-06-24 — implemented. Renamed `type` → `category` in `GarmentSummary`, `GarmentDetail`,
  `GarmentCreateRequest`, `GarmentUpdateRequest` (schemas.py); `INVALID_TYPE` → `INVALID_CATEGORY`
  (errors.py); `garment_to_summary` converter updated (converters.py); `garments.py` router updated
  (`body.type` → `body.category`, GET param `type` → `category`, error code updated); all
  `test_garments.py` and one `test_suggestions.py` assertion updated. 1043 backend + 135 frontend
  pass, zero warnings.
- Sanity test: `cd backend && .venv/bin/pytest tests/api/test_garments.py -q`
