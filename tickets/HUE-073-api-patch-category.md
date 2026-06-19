---
id: HUE-073
title: PATCH /api/garments/{id} — edit category
type: task
status: todo
milestone: 14
batch: api
layer: api
depends_on: [HUE-072, HUE-030]
implements: [FR-32, FR-46]
tests_required: true
estimate: 2
---

## Background
`PATCH /api/garments/{id}` is the direct, single-field category edit (contract §2.10a, FR-46) —
the only field-edit path permitted by the amended FR-32. It carries no regeneration token and
never touches the palette, image or id; the token-gated `PUT` (§2.10) remains the only palette
path. Thin translation over the HUE-072 service operation.

## Technical requirements
- `PATCH /api/garments/{id}` with body `{ "category": <FR-16 category> }` (exactly one field)
- **200**: the full updated `Garment` (`regenerated_at` unchanged); only `category` differs
- **Errors**: `404 garment_not_found`; `422 invalid_category` (off-allowlist); `422 invalid_request` (missing `category`, or any field other than `category`)
- Imports `services` only; never touches the palette (FR-32/FR-33)

## Definition of done (acceptance criteria)
- [ ] `PATCH` changes only the category; `id`/image/palette/`regenerated_at` unchanged (FR-46)
- [ ] `404`/`422 invalid_category`/`422 invalid_request` per contract §2.10a
- [ ] `PUT` remains the only palette path (FR-32) — asserted that `PATCH` does not alter colours
- [ ] Tests added/updated per §12.2 and passing in `make test`; import contracts kept
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_garments.py` (§7.2): the one-field PATCH success (re-read asserts palette/image/`regenerated_at`
unchanged); `404`; `422 invalid_category`; `422 invalid_request` (missing/extra field); a
follow-up suggestion call shows eligibility follows the new category.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
