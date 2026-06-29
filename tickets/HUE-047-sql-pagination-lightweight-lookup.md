---
id: HUE-047
title: SQL-level pagination and lightweight garment lookup
type: task
status: done
milestone: 8
batch: cleanup
layer: services
depends_on: [HUE-029, HUE-030]
implements: []
tests_required: true
estimate: 2
---

## In plain English
Makes browsing the wardrobe and opening garment photos quicker by only fetching the information actually needed at the time, so the app stays responsive as the collection grows.

## Background

`/verify` of the API batch identified two efficiency issues in
`garment_service.py`:

1. `list_garments()` loads all matching rows into Python, counts with `len()`,
   then slices for pagination. This defeats SQL-level pagination and scales
   poorly beyond the 500-garment baseline.

2. `get_garment_image()` and `get_garment_thumbnail()` call `get_garment()`
   which fetches all colour rows, but only the file path is needed. The
   `regenerate_garment` endpoint has the same issue.

## Technical requirements

1. **SQL-level pagination** in `list_garments()` (`garment_service.py:180-204`):
   - Apply `.offset(offset).limit(limit)` to the SQL query itself.
   - Use a separate `count()` query (or window function) for the total.
   - Verify the family-filter subquery still works correctly with SQL pagination.

2. **Lightweight garment metadata lookup** — add a function (e.g.
   `get_garment_metadata(garment_id, engine)`) that fetches only the
   `GarmentRow` without joining colour rows. Use it in:
   - `garments.py` image/thumbnail endpoints (lines 172-197)
   - `garments.py` regenerate endpoint (line 213) where only the image filename
     is needed.

## Definition of done (acceptance criteria)

- [x] `list_garments` uses SQL-level offset/limit; Python-side slicing removed
- [x] `total` count derived from a SQL query, not `len(all_rows)`
- [x] Image, thumbnail, and regenerate endpoints no longer load colour rows
- [x] All existing tests still pass unchanged
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

Existing read/filter/pagination tests in `test_garments.py` validate correctness.
Should land before HUE-039 (performance suite) to ensure pagination is efficient
at 500 garments.

`cd backend && .venv/bin/pytest tests/api/test_garments.py -q`

## Notes

- 2026-06-16 — created by `/verify` review of API batch (HUE-025–031).
- 2026-06-17 — implemented: `list_garments` now uses `func.count()` + SQL offset/limit via a `_apply_filters` closure; added `GarmentMetadata` dataclass and `get_garment_metadata()`; added `require_garment_metadata()` to converters; image, thumbnail, and regenerate endpoints use the lightweight lookup. 885 passed, zero warnings.
