---
id: HUE-043
title: Shared conftest for service tests
type: task
status: done
milestone: 8
batch: cleanup
layer: tooling
depends_on: [HUE-021, HUE-022, HUE-023, HUE-024]
implements: []
tests_required: true
estimate: 1
---

## Background

`/verify` of the services batch identified duplicated test fixtures and helpers
across the four service test files.

## Technical requirements

Create `backend/tests/services/conftest.py` and extract:

1. **`engine` fixture** — the `make_engine / init_db / yield / dispose` pattern
   appears identically in `test_garment_service.py`, `test_regeneration_service.py`
   and `test_suggestion_service.py`.
2. **`dirs` fixture** — the staging/images/thumbnails triad appears identically
   in `test_garment_service.py` and `test_regeneration_service.py`.
3. **`_make_jpeg_bytes`** — identical image-byte factory in
   `test_garment_service.py` and `test_regeneration_service.py`.
4. **`_stage_image` / `_stage_upload`** — functionally identical staging helpers
   in `test_garment_service.py` and `test_regeneration_service.py`.

Remove the per-file copies and import from the shared conftest (or let pytest
discover the fixtures automatically).

## Definition of done (acceptance criteria)

- [x] Shared `conftest.py` created with the extracted fixtures/helpers
- [x] Per-file duplicates removed
- [x] All existing service tests still pass
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — this is a pure refactor. Existing tests cover all paths.

`cd backend && .venv/bin/pytest tests/services/ -q`

## Notes

- 2026-06-16 — created by `/verify` review of services batch (HUE-021–024).
- 2026-06-17 — done. Created `tests/services/conftest.py` with `engine` and `dirs` fixtures (auto-discovered) and `_make_jpeg_bytes` / `_stage_image` helpers (imported explicitly). Removed per-file copies from test_garment_service.py, test_regeneration_service.py, and test_suggestion_service.py; renamed `_stage_upload` → `_stage_image` in the regen file. `_stage_regen_token` stays local to regen (unique to that file). 892 passed, zero warnings.
