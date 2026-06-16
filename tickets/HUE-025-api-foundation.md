---
id: HUE-025
title: API foundation: schemas, error envelope, health, static serving
type: task
status: done
milestone: 8
batch: api
layer: api
depends_on: [HUE-002, HUE-016]
implements: [NFR-2]
tests_required: true
estimate: 5
---

## Background
Every endpoint shares the Pydantic schemas, the error envelope, the status-code mapping and the static SPA mount (API contract §1, architecture §2.4). This foundation lands before the resource endpoints so each adds only its own routing.

## Technical requirements
- `app/api/schemas.py`: `ColourIn`/`ColourOut`, `GarmentSummary`, `Garment`, request/response models per contract §1.1–§1.2, with the documented validation (0≤h<360, 0≤s,l≤100, proportion 1–100, 1–4 colours)
- Error envelope + exception handlers mapping to the contract §1.3 codes/statuses (400/404/409/413/422/500) with plain-language `message`
- `GET /api/health` → `{status, version}` for the launch script (NFR-2)
- Static SPA mount at `/` with history-API fallback to `index.html`; `/api` prefix; same-origin (no CORS in production) (architecture §5)
- Client-supplied `family` never trusted on input (contract §1.6); `api` imports only `services` + schemas (contract 1/5)

## Definition of done (acceptance criteria)
- [x] Shared schemas validate per contract §1.1; error envelope and status mapping match contract §1.3
- [x] `GET /api/health` returns the documented body (NFR-2); SPA static mount + history fallback configured
- [x] `api` imports only `services` and schemas; nothing imports `api` (import-linter contracts 1 and 5 hold)
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`api/` contract tests (§7.2): the error envelope for each documented code; schema validation boundary rows (0/5 colours, sums 99/101, h=360, proportion=0 → 422); health body; static mount serves index with history fallback. TestClient against the real app factory.

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `app/api/schemas.py` (ColourIn/ColourOut, GarmentSummary, GarmentDetail,
  validate_palette, GARMENT_TYPES); `app/api/errors.py` (AppError, register_error_handlers — 404/409/422/500
  all use the contract §1.3 envelope; RequestValidationError uses jsonable_encoder to ensure Pydantic v2
  error dicts are JSON-serialisable); `app/api/health.py` (GET /api/health → {status, version}); updated
  `app/main.py` (spa_dir Settings field; register_error_handlers; health router at /api; SPA catch-all with
  /api prefix guard and history-API fallback); `tests/api/test_api_foundation.py` (32 tests — health body,
  envelope per code, ColourIn boundaries, validate_palette, static mount + fallback). Import-linter contracts
  1+5 green. `make test` → 771 passed, 1 skipped, 0 warnings.
- Sanity: `cd backend && .venv/bin/pytest tests/api/test_api_foundation.py -q`
