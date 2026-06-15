---
id: HUE-002
title: Backend skeleton and application settings
type: task
status: todo
milestone: 7
batch: scaffolding
layer: tooling
depends_on: [HUE-001]
implements: [NFR-1, NFR-2, NFR-3]
tests_required: false
estimate: 3
---

## Background
The backend needs its package skeleton, dependency management and the app-factory + settings seam the test harness depends on (test strategy §7.1) before any layer can be built. This ticket stands up the structure without implementing behaviour.

## Technical requirements
- Python 3.12 virtual environment; `pyproject.toml` with pinned application dependencies (FastAPI, Uvicorn, SQLModel, Pillow, NumPy, scikit-learn, rembg/onnxruntime) — test deps added in HUE-004
- Package layout per architecture §2.1: `backend/app/{main.py, api/, services/, detection/, matcher/, storage/}` with empty `__init__.py` placeholders
- An app factory in `main.py` returning a configured FastAPI instance (routers mounted by later tickets); a **settings object** reading the `data/` root from an environment variable so tests can point it at a temporary directory (test strategy §7.1)
- Bind to localhost only; no outbound calls configured (NFR-1, NFR-8)
- `Makefile` with `setup`, `run`, `dev` targets (stubs that later tickets complete — architecture §5): `run` is the single offline command (NFR-2)
- Ensure the `data/` directory and its `images/`, `thumbnails/`, `staging/`, `models/` subdirectories are created on startup if absent (NFR-3)

## Definition of done (acceptance criteria)
- [ ] Package skeleton present per architecture §2.1; imports cleanly
- [ ] App factory builds a FastAPI app; settings read the data-dir root from the environment
- [ ] `Makefile` targets `setup`/`run`/`dev` exist (run/setup completed by later tickets)
- [ ] `data/` layout created on startup
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Build-plumbing ticket. Verified by `python -c 'from app.main import create_app; create_app()'` succeeding and the data-dir seam honouring a temporary path. The conftest fixtures that exercise this seam are added in HUE-004; no behaviour tests here.

`tests_required: false` — exemption category: **build-plumbing** (skeleton and settings; behaviour arrives with later tickets).

## Notes
- 2026-06-15 — created
