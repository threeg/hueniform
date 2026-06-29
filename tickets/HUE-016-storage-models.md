---
id: HUE-016
title: Storage models and database engine
type: task
status: done
milestone: 8
batch: storage
layer: storage
depends_on: [HUE-002]
implements: [NFR-3]
tests_required: true
estimate: 5
---

## In plain English
Sets up how the wardrobe is saved on the computer — the structure for storing each garment and its colours, with safeguards that keep the saved information valid and tidy, including removing a garment's colours when the garment itself is deleted.

## Background
Persistence is two SQLModel tables (architecture §3.1): `garments` and `garment_colours`, with the CHECK constraints, indices, foreign keys and journal mode the architecture specifies. Storage imports nothing from the matcher (dependency rule, test strategy §5.1 contract 4).

## Technical requirements
- `app/storage/models.py`: `garments` (id PK UUID4, type with CHECK over the eight FR-16 values, image_file, thumbnail_file, created_at, regenerated_at nullable) and `garment_colours` (id, garment_id FK ON DELETE CASCADE, position 0–3, h/s/l, family, proportion 1–100 CHECK)
- Engine/session module with `PRAGMA foreign_keys = ON`, WAL journal mode, schema init if absent
- Indices `idx_garments_type`, `idx_colours_family`, `idx_colours_garment` (architecture §3.1, NFR-6)
- `family` stored denormalised (derived server-side on write — the value comes from the service, per the dependency rule); per-garment proportion sum validated in the service layer, not here
- Storage imports nothing from `app.matcher`/`detection`/`services`/`api` (contract 4)

## Definition of done (acceptance criteria)
- [x] Both tables created with the documented columns, CHECK constraints and indices
- [x] `PRAGMA foreign_keys = ON` and WAL active; `ON DELETE CASCADE` works
- [x] Storage layer imports nothing from matcher/detection/services/api (import-linter contract 4 holds)
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`backend/tests/api/`/integration tests use a real SQLite file in a temporary `data/` (§7.1). Model-level tests assert the CHECK constraints reject bad types/proportions, the indices exist, and cascade delete removes colour rows. Exercised heavily by the lifecycle tests (§7.3).

## Notes
- 2026-06-15 — created
- 2026-06-15 — implemented. `app/storage/models.py` (new): `GarmentRow` and `GarmentColourRow` SQLModel tables with CHECK constraints (type allowlist, proportion 1–100), FK with `ondelete="CASCADE"`, and the three required indices. `app/storage/engine.py` (new): `make_engine` with `@event.listens_for(engine, "connect")` to set `PRAGMA foreign_keys = ON` and `PRAGMA journal_mode = WAL`, plus `init_db` (idempotent `create_all`) and `get_session` for FastAPI DI. Tests use `session.flush()` between garment and colour inserts to avoid undefined insertion order with no ORM relationship. 554 tests; import-linter contract 4 holds.
