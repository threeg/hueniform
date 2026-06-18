---
id: HUE-046
title: Shared API test conftest
type: task
status: done
milestone: 8
batch: cleanup
layer: tooling
depends_on: [HUE-031]
implements: []
tests_required: true
estimate: 1
---

## Background

`/verify` of the API batch identified that every API test file independently
creates `Settings(data_dir=..., spa_dir="no-spa")` and
`TestClient(create_app(settings))`. Four copies of the same setup pattern exist
across `test_detections.py`, `test_garments.py`, `test_suggestions.py`, and
`test_taxonomy.py`.

## Technical requirements

1. **Create `backend/tests/api/conftest.py`** with shared fixtures:
   - `api_settings(tmp_path)` — returns `Settings` with `spa_dir="no-spa"` and
     subdirectories created.
   - `api_client(api_settings)` — returns `TestClient(create_app(api_settings))`
     with context manager lifecycle.

2. **Remove duplicate fixtures** from `test_detections.py`, `test_garments.py`,
   `test_suggestions.py`, and `test_taxonomy.py`; import from conftest instead.

3. `test_api_foundation.py` has intentionally complex setup (test router
   injection) — keep its `client()` local but have it reuse the base
   `api_settings` fixture where possible.

## Definition of done (acceptance criteria)

- [x] `backend/tests/api/conftest.py` exists with shared fixtures
- [x] No duplicate settings/client fixtures in individual API test files
- [x] All existing API tests still pass unchanged
- [x] `make test` passes with zero warnings
- [x] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — pure refactor. All existing tests validate the fixtures
work correctly.

`cd backend && .venv/bin/pytest tests/api/ -q`

## Notes

- 2026-06-16 — created by `/verify` review of API batch (HUE-025–031).
  Complements HUE-043 (shared conftest for service tests).
- 2026-06-17 — implemented: `conftest.py` created with `api_settings` and `api_client` fixtures; duplicate fixtures removed from `test_detections.py`, `test_garments.py`, `test_suggestions.py`, `test_taxonomy.py`; `test_api_foundation.py` `client()` reuses `api_settings`. 885 passed, zero warnings.
