# ─────────────────────────────────────────────────────────────────────────────
# Hueniform — project Makefile
# Prerequisites: Python 3.12, Node.js (needed only for make setup)
# One-time online step: make setup
# After setup, all other targets run entirely offline (NFR-1, NFR-8).
# ─────────────────────────────────────────────────────────────────────────────

PYTHON_BIN ?= $(shell python3.12 --version >/dev/null 2>&1 && echo python3.12 || \
               (python3.13 --version >/dev/null 2>&1 && echo python3.13) || \
               echo python3)
VENV       := backend/.venv
PY         := $(VENV)/bin/python
PIP        := $(VENV)/bin/pip
UVICORN    := $(VENV)/bin/uvicorn
PYTEST     := $(VENV)/bin/pytest
COVERAGE   := $(VENV)/bin/coverage

.PHONY: setup run dev \
        test test-backend test-frontend \
        test-model test-perf test-e2e test-all

# ─── One-time setup (requires internet) ──────────────────────────────────────
setup:
	test -d $(VENV) || $(PYTHON_BIN) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -e "backend/[dev]"
	cd frontend && npm ci
	cd frontend && npm run build
	@# HUE-020 adds: fetch the rembg model into data/models/
	@# HUE-005 adds: playwright install chromium firefox
	@echo "setup complete."

# ─── Single offline run command (NFR-2) ──────────────────────────────────────
# Completed by HUE-038: adds staging sweep and full SPA serving.
run:
	@echo "Hueniform → http://127.0.0.1:8000"
	$(UVICORN) app.main:app --host 127.0.0.1 --port 8000

# ─── Development server (completed by HUE-038) ───────────────────────────────
dev:
	@echo "Full dev target (Uvicorn reload + Vite proxy together) arrives in HUE-038."
	@echo "To run Vite alone: cd frontend && npm run dev"

# ─── Default test gate: backend unit+integration + frontend components ────────
test: test-backend test-frontend

test-backend:
	@echo "Backend test tooling arrives in HUE-004; skipping."

test-frontend:
	@echo "Frontend test tooling arrives in HUE-005; skipping."

# ─── Heavier optional gates (definition-of-done for specific ticket types) ───
test-model:
	@echo "Model test suite (make test-model) arrives in HUE-020; skipping."

test-perf:
	@echo "Performance suite (make test-perf) arrives in HUE-039; skipping."

test-e2e:
	@echo "E2E smoke suite (make test-e2e) arrives in HUE-040; skipping."

test-all: test test-model test-perf test-e2e
