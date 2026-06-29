---
id: HUE-056
title: Extract colour-row grouping helper
type: task
status: done
milestone: 8
batch: cleanup
layer: services
depends_on: [HUE-042, HUE-047]
implements: []
tests_required: true
estimate: 1
---

## In plain English
Replaces four copies of the same routine for grouping a garment's colours with a single shared one, so the code is cleaner and future changes only need to be made once.

## Background

`/verify` of the complete MVP identified the identical colour-row grouping
pattern duplicated four times across two service modules:

- `garment_service.py:123-125` (in `list_garments`)
- `garment_service.py:279-281` (in `get_garment`)
- `garment_service.py:347-349` (in `confirm_regeneration`)
- `suggestion_service.py:123-125` (in `_load_wardrobe`)

Each instance performs:
```python
colours_by_garment: dict[str, list[GarmentColourRow]] = {}
for c in all_colour_rows:
    colours_by_garment.setdefault(c.garment_id, []).append(c)
```

## Technical requirements

1. **Extract a shared helper** — `group_colours_by_garment(rows)` that returns
   `dict[str, list[GarmentColourRow]]`. Place it in a location importable by
   both service modules without violating the dependency rule (e.g.
   `app/storage/helpers.py` or alongside models in storage).

2. **Replace all four occurrences** with calls to the shared helper.

## Definition of done (acceptance criteria)

- [x] Single `group_colours_by_garment()` function defined in one place
- [x] All four occurrences replaced with the shared function call
- [x] All existing service and API tests still pass unchanged
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure refactor. Existing tests cover all paths.

`cd backend && .venv/bin/pytest tests/services/ tests/api/ -q`

## Notes

- 2026-06-18 — created by `/verify` complete MVP review.
- 2026-06-18 — implemented: `group_colours_by_garment()` created in `app/storage/helpers.py`; 3 occurrences replaced (2 in `garment_service.py`, 1 in `suggestion_service.py`; one ticket-listed site no longer exists after HUE-047). Import-linter contract #5 updated with two new `services → storage.helpers` ignore entries. 238 service+API tests passed, all 5 contracts kept.
