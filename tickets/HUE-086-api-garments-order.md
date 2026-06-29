---
id: HUE-086
title: GET /api/garments — order parameter, total and pagination
type: task
status: todo
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
- [ ] `order`/`limit`/`offset` per contract §2.6; `order=hue` default
- [ ] Response carries `total`; list ordered category then `order` key
- [ ] `422 invalid_filter` for unknown `order`
- [ ] Tests added/updated per §12.2 and passing in `make test`; `make test-perf` re-baselined
  (HUE-084 depends on this)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` (§7.2): `order=hue` (neutrals-last) and `order=date`; `total` present;
`limit`/`offset` pagination; `422 invalid_filter` for unknown `order`.

## Notes
- 2026-06-24 — created; split from HUE-076 (scope narrowed to rename only)
