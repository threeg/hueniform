---
id: HUE-076
title: GET /api/garments — order parameter and category filter rename
type: task
status: todo
milestone: 14
batch: api
layer: api
depends_on: [HUE-075, HUE-029]
implements: [FR-35, FR-47]
tests_required: true
estimate: 2
---

## Background
Expose the FR-47 ordering and complete the `type` → `category` rename on the inventory
endpoint (contract §2.6). Filters still combine as AND; the response is a flat list already
ordered by category then the chosen `order` key, plus `total`.

## Technical requirements
- `GET /api/garments` query params (all optional, AND): `category` (one FR-16 category — renamed from `type`), `family`, `order` ∈ `hue` (default) / `date`, `limit`/`offset` (default 500/0)
- Response `{ "garments": [GarmentSummary], "total": N }`; each `GarmentSummary` carries `category`
- `family` matches any role; `total` is the full match count before pagination
- **Errors**: `422 invalid_filter` for an unknown `category`, `family` or `order`

## Definition of done (acceptance criteria)
- [ ] `category`/`family`/`order`/`limit`/`offset` per contract §2.6; `order=hue` default
- [ ] List ordered by category then `order` key; `GarmentSummary.category` present
- [ ] `422 invalid_filter` for unknown `category`/`family`/`order`
- [ ] Tests added/updated per §12.2 and passing in `make test`; import contracts kept
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` (§7.2): `category`-only/`family`-only/combined filters; `order=hue`
(neutrals-last) and `order=date`; `category` rename asserted (no `type`); `422 invalid_filter`
for each unknown value; `total` under `limit`/`offset`.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
