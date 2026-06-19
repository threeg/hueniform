---
id: HUE-065
title: Storage category value-set and data migration
type: task
status: todo
milestone: 14
batch: storage
layer: storage
depends_on: [HUE-016]
implements: [FR-16]
tests_required: true
estimate: 3
---

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
- [ ] New CHECK allowlist = FR-16 categories; old values rejected after migration
- [ ] Migration maps every old value per the rules; ambiguous `bottom`/`accessory` use the documented default and stay editable (FR-46)
- [ ] Idempotent; row counts, images and colour rows unchanged
- [ ] Tests added/updated per §12.2 and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`storage/test_migration.py` (or `api/test_migration.py`) per §7.5: a v0.1.0-schema/value-set
fixture under `tests/fixtures/legacy/`; assert the unambiguous mappings exactly, the ambiguous
defaults plus re-editability, the new-CHECK pass, idempotency, and untouched ids/images/colours.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
