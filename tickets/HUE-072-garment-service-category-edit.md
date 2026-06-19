---
id: HUE-072
title: Garment service — direct category edit
type: task
status: todo
milestone: 14
batch: services
layer: services
depends_on: [HUE-065, HUE-022]
implements: [FR-32, FR-46]
tests_required: true
estimate: 2
---

## Background
F3: a saved garment's **category** becomes directly editable without re-detection or the
confirm-and-correct flow (FR-46), narrowing FR-32 so only the type field is editable; the
palette stays regenerate-only (FR-33). A single-field service operation that validates against
the FR-16 allowlist and touches nothing else.

## Technical requirements
- `app/services/garment_service.py` — an `edit_category(id, category)` operation: validate the
  category against the FR-16 allowlist; write only `garments.type`; leave `id`, `image_file`,
  `thumbnail_file`, colour rows and `regenerated_at` unchanged
- Unknown garment → not-found; invalid category → validation error (mapped to `422` at the API)
- No palette path here (regenerate-only, FR-32/FR-33); imports `storage`, not `api`

## Definition of done (acceptance criteria)
- [ ] Category edit changes only `garments.type`; everything else unchanged (FR-46)
- [ ] Validates against the FR-16 allowlist; not-found and invalid-category paths covered
- [ ] Palette untouched; no re-detection (FR-32/FR-33)
- [ ] Tests added/updated per §12.2 and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`services/test_garment_service.py` (§7.2/§7.3): edit changes category only (re-read asserts
image/palette/`regenerated_at` unchanged); invalid category rejected; suggestion eligibility
follows the new category (cross-checked via a follow-up evaluation).

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
