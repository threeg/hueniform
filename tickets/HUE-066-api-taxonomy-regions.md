---
id: HUE-066
title: GET /api/taxonomy — regions/slots model
type: task
status: done
milestone: 14
batch: api
layer: api
depends_on: [HUE-061, HUE-062, HUE-026]
implements: [FR-16, FR-49, FR-50, FR-51]
tests_required: true
estimate: 3
---

## Background
`GET /api/taxonomy` becomes a backward-compatible **superset**: the `families` array gains
`Cream` (via HUE-062), and a new `regions` array describes the slot/region model the UI needs
to render category pickers and the slot selector (contract §2.2, FR-16, FR-49–FR-51). The slot
model is derived from `matcher.slots`; the endpoint stays a thin translation layer.

## Technical requirements
- `GET /api/taxonomy` response per contract §2.2:
  - `families` — twenty families incl. `Cream` (neutral, `canonical` only); `representative_hue`/`hue_arc` only on the twelve chromatic families
  - `regions` — `head`/`upper_body`/`lower_body`/`feet`, each slot with `slot` key, `label`, `categories`, `role` ∈ `anchor`/`statement`/`minor`
  - `layer_order` only on `base(0)/shirt(1)/mid(2)/outer(3)`; `mandatory: true` only on `lower_body`; `default_selected` on `base`/`lower_body`/`socks`/`shoes`; `one_piece_categories`/`one_piece_also_occupies` only on `lower_body`
- Slot keys `mid`/`outer` (not `jersey`/`jacket`); derived from the matcher slot model
- `api` imports only `services`/schemas (or the taxonomy service), never `matcher.slots` directly if that breaks contract 5 — follow the existing taxonomy-endpoint pattern (HUE-026)

## Definition of done (acceptance criteria)
- [x] `families` includes Cream and matches §2.2; `regions` matches §2.2 field-for-field
- [x] `layer_order`/`mandatory`/`default_selected`/one-piece flags present exactly where specified
- [x] Slot keys are `mid`/`outer`; categories per slot are the FR-16 sets
- [x] Tests added/updated per §12.2 and passing in `make test`; import contracts kept
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_taxonomy.py` (§7.2): the twenty families with Cream canonical; the `regions` array
asserted against contract §2.2 (slots, labels, roles, `layer_order`, `mandatory`,
`default_selected`, one-piece flags); every canonical classifies into its own family.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-06-19 — implemented. `taxonomy_service.py` gains `list_regions()` returning 4 regions / 17 slots. `schemas.py` gains `SlotOut` and `RegionOut`; `TaxonomyResponse` now includes `regions`. `taxonomy.py` updated to build and return regions. 28 new tests added to `test_taxonomy.py`. 1033 backend + 134 frontend tests pass; matcher coverage 100%.
- Sanity test: `cd backend && .venv/bin/pytest tests/api/test_taxonomy.py -q`

## QA steps
- `make run` → `curl -s http://127.0.0.1:8000/api/taxonomy | python3 -m json.tool | grep -A2 '"regions"'` — should see the regions array
- Check `regions[0]["region"] == "head"` and `regions[-1]["region"] == "feet"`
