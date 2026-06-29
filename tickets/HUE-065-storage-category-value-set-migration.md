---
id: HUE-065
title: Storage category value-set and data migration
type: task
status: done
milestone: 14
batch: storage
layer: storage
depends_on: [HUE-016]
implements: [FR-16]
tests_required: true
estimate: 3
---

## In plain English
Updates the list of clothing kinds the wardrobe recognises to the new, fuller set, and carefully relabels any items already saved under the old names so nothing is lost or mislabelled.

## Background
The `garments.type` column keeps its name and shape, but its **allowed value set** changes to
the FR-16 categories (architecture §3.1). Existing rows carry v0.1.0 values that would fail
the new CHECK, so a one-off **data migration** runs before the new allowlist is applied. The
DB column name stays `type` (the API exposes it as `category`); no schema/column/index change.
`storage` imports nothing from the upper layers (dependency rule), so the allowlist is
maintained here independently of `matcher`.

## Technical requirements
- Update the `garments.type` CHECK allowlist to the FR-16 categories (architecture §3.1)
- One-off migration of existing rows, run before the new CHECK:
  - Carry over unchanged: `jacket`, `socks`, `shoes`, `hat`
  - `jersey` → `jumper`; `top` → `t_shirt`
  - `bottom` → a **defined default** among `trousers`/`jeans`/`shorts`/`skirt` (documented), re-categorisable via FR-46
  - `accessory` → a **defined default** among the adornment categories (documented), re-categorisable via FR-46
- Idempotent; touches only `type`; leaves `id`, `image_file`, colour rows and counts intact
- WAL/foreign-keys/cascade behaviour unchanged

## Definition of done (acceptance criteria)
- [x] New CHECK allowlist = FR-16 categories; old values rejected after migration
- [x] Migration maps every old value per the rules; ambiguous `bottom`/`accessory` use the documented default and stay editable (FR-46)
- [x] Idempotent; row counts, images and colour rows unchanged
- [x] Tests added/updated per §12.2 and passing in `make test`
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`storage/test_migration.py` (or `api/test_migration.py`) per §7.5: a v0.1.0-schema/value-set
fixture under `tests/fixtures/legacy/`; assert the unambiguous mappings exactly, the ambiguous
defaults plus re-editability, the new-CHECK pass, idempotency, and untouched ids/images/colours.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-06-19 — implemented. `storage/models.py` GARMENT_TYPES updated to all 40 FR-16 categories. `storage/migration.py` added: v0.1.0 → v0.2.0 table-rename migration, idempotent, maps `top`→`t_shirt`, `bottom`→`trousers`, `jersey`→`jumper`, `accessory`→`glasses`; jacket/socks/shoes/hat pass through. `engine.py` calls `migrate()` before `create_all()`. `matcher/slots.py` constants updated to v0.2.0 (GARMENT_TYPES = ALL_CATEGORIES, REQUIRED_SLOTS = DEFAULT_SLOTS). `matcher/ranking.py` backward-compat translation removed. `suggestion_service.py` empty-slot check now groups by slot via `category_to_slot()`. All test fixtures and tests updated to FR-16 category names. 1014 backend + 134 frontend tests pass; matcher coverage 100%.
- Sanity test: `cd backend && .venv/bin/pytest tests/storage/test_migration.py -q`

## QA steps
- `make run` → open app → add a garment (the new-DB path must work)
- Confirm the garment is saved with a type from the FR-16 list (inspect via GET /api/garments)
