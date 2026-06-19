---
id: HUE-066
title: GET /api/taxonomy — regions/slots model
type: task
status: todo
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
- [ ] `families` includes Cream and matches §2.2; `regions` matches §2.2 field-for-field
- [ ] `layer_order`/`mandatory`/`default_selected`/one-piece flags present exactly where specified
- [ ] Slot keys are `mid`/`outer`; categories per slot are the FR-16 sets
- [ ] Tests added/updated per §12.2 and passing in `make test`; import contracts kept
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_taxonomy.py` (§7.2): the twenty families with Cream canonical; the `regions` array
asserted against contract §2.2 (slots, labels, roles, `layer_order`, `mandatory`,
`default_selected`, one-piece flags); every canonical classifies into its own family.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
