---
id: HUE-086
title: GET /api/garments — order parameter, total and pagination
type: task
status: done
milestone: 14
batch: api
layer: api
depends_on: [HUE-075, HUE-076]
implements: [FR-47]
tests_required: true
estimate: 2
---

## In plain English
Lets the wardrobe list be sorted either by colour or by when each garment was added, and reports how many garments match so the list can be shown in pages.

## Background
Expose the FR-47 ordering on the inventory endpoint (contract §2.6), completing the garment list
API. Ordering in the service layer lands in HUE-075; this ticket wires it through the API layer.
The `type`→`category` rename that unblocked this is in HUE-076.

## Technical requirements
- `GET /api/garments` query params (all optional, AND): `category`, `family`, `order` ∈ `hue`
  (default) / `date`, `limit` (default 500), `offset` (default 0)
- Response `{ "garments": [GarmentSummary], "total": N }`; flat list ordered by category then
  the chosen `order` key; `total` is the full match count before pagination
- `family` filter matches any role
- **Errors**: `422 invalid_filter` for unknown `order` value (category/family already validated)

## Definition of done (acceptance criteria)
- [x] `order`/`limit`/`offset` per contract §2.6; `order=hue` default
- [x] Response carries `total`; list ordered category then `order` key
- [x] `422 invalid_filter` for unknown `order`
- [x] Tests added/updated per §12.2 and passing in `make test`
- [ ] `make test-perf` re-baselined (deferred to HUE-084)
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` (§7.2): `order=hue` (neutrals-last) and `order=date`; `total` present;
`limit`/`offset` pagination; `422 invalid_filter` for unknown `order`.

## Notes
- 2026-06-24 — created; split from HUE-076 (scope narrowed to rename only)
- 2026-07-02 — implemented. Added `order: str = Query(default='hue')` to
  `list_garments_endpoint` and passed it through to `list_garments()`. The service
  (HUE-075) already validates the value and raises `InvalidFilterError`; the existing
  handler maps that to 422. Three new tests: `order=hue` accepted, `order=date` accepted,
  unknown order → 422 `invalid_filter`. 1112 backend + 181 frontend tests pass.
- Sanity test: `cd backend && .venv/bin/pytest tests/api/test_garments.py::TestListGarments -q`
