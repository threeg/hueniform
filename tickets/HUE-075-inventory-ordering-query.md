---
id: HUE-075
title: Inventory ordering (hue spectrum / date) in the read query
type: task
status: todo
milestone: 14
batch: services
layer: services
depends_on: [HUE-022, HUE-047]
implements: [FR-47, NFR-6]
tests_required: true
estimate: 3
---

## Background
F6: the inventory read gains a within-group **ordering** by hue (a colour spectrum, the
default) or by date added (newest first) (FR-47). Ordering is applied in the service/query
layer over the existing rows and indices — no schema change (architecture §3.1). Grouping by
category is a frontend concern (the list arrives ordered by category, then by the chosen key).

## Technical requirements
- `app/services/garment_service.py` (or the inventory query) — accept an `order` ∈ `hue`/`date`:
  - `hue` (default): order by each garment's **primary-colour hue** (the `position = 0` colour, FR-7); **neutral-primary** garments (no hue, FR-3) ordered **after** the chromatic spectrum in a stable, defined order
  - `date`: by `created_at`, newest first
- The list is ordered by **category, then the chosen `order` key** (so the client can group by walking it)
- Stays within NFR-6 at 500 garments using existing indices; no schema/index change

## Definition of done (acceptance criteria)
- [ ] `hue` orders each category group as a spectrum by primary hue with neutrals trailing in a stable order (FR-47)
- [ ] `date` orders newest-first; list ordered by category then `order` key
- [ ] No schema change; NFR-6 server-half holds (perf is HUE-084)
- [ ] Tests added/updated per §12.2 and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`services/test_garment_service.py` (§7.2): ordering asserted as a property over a wardrobe with
known primaries (chromatic in hue order, neutral-primary garments trailing) for `hue`; newest-first
for `date`; category-then-key ordering. NFR-6 server-half perf is HUE-084.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
