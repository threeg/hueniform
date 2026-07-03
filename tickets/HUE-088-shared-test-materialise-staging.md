---
id: HUE-088
title: Shared test helpers for DB materialisation and image staging
type: task
status: todo
milestone: 14
batch: cleanup
layer: tooling
depends_on: [HUE-068, HUE-082]
implements: []
tests_required: true
estimate: 2
---

## In plain English

Tidies up repeated test helper code that creates garments in the database and stages
fake images, so both the service and API test suites share a single, well-tested copy.

## Background

`/verify` of the v0.2.0 batch identified two sets of duplicated test helpers:

1. **`_materialise()` appears in both `tests/services/test_suggestion_service.py`
   (lines 42–67) and `tests/api/test_suggestions.py` (lines 40–67).** The functions
   are near-identical; the only difference is whether family is a placeholder
   (`"Red"`) or derived via `classify()`.

2. **Image staging helpers appear in both `tests/api/test_garments.py` (lines 30–46:
   `_tiny_jpeg()` / `_stage()`) and `tests/services/conftest.py` (lines 35–50:
   `_make_jpeg_bytes()` / `_stage_image()`).** Both create minimal valid JPEGs and
   stage them with identical logic; only the pixel dimensions differ cosmetically.

## Technical requirements

1. **Extract `materialise_garments(engine, garments, derive_families=False)`** into
   `tests/conftest.py` (or a dedicated `tests/helpers/db.py`). When
   `derive_families=True`, call `classify()` for accurate family values; otherwise
   use a placeholder. Remove the two private copies.

2. **Extract `make_test_jpeg(colour=(200, 30, 30))` and
   `stage_test_image(staging_dir, data=None)`** into `tests/conftest.py`. Remove the
   duplicate definitions from `test_garments.py` and `services/conftest.py`.

3. All existing tests must continue to pass without behavioural change.

## Definition of done (acceptance criteria)

- [ ] `materialise_garments()` shared helper replaces both private `_materialise()` copies
- [ ] `make_test_jpeg()` and `stage_test_image()` shared helpers replace both private image helpers
- [ ] No duplicated helper code remains across `tests/services/` and `tests/api/`
- [ ] `make test` passes with zero warnings
- [ ] Ticket status + notes updated in the same commit

## Tests / verification

No new tests required — this is a pure refactor. Existing tests cover all paths.

`cd backend && .venv/bin/pytest tests/services/ tests/api/ -q`

## Notes

- 2026-07-03 — created by `/verify` review of v0.2.0 batch.
