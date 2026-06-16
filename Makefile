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
UVICORN      := $(VENV)/bin/uvicorn
PYTEST       := $(VENV)/bin/pytest
COVERAGE     := $(VENV)/bin/coverage
LINT_IMPORTS := $(VENV)/bin/lint-imports

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
	cd frontend && npx playwright install chromium firefox
	mkdir -p data/models
	U2NET_HOME=$(CURDIR)/data/models $(PY) -c \
	    "import rembg; rembg.new_session('u2net'); print('rembg model ready.')"
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
	cd backend && $(CURDIR)/$(LINT_IMPORTS)
	cd backend && HYPOTHESIS_PROFILE=deterministic \
	    $(CURDIR)/$(PYTEST) -m "not model and not perf" \
	    --cov=app --cov-branch --cov-report=term-missing
	cd backend && $(CURDIR)/$(COVERAGE) report \
	    --include="app/matcher/*" --fail-under=100

test-frontend:
	cd frontend && npm run test

# ─── Heavier optional gates (definition-of-done for specific ticket types) ───
test-model:
	cd backend && U2NET_HOME=$(CURDIR)/data/models HYPOTHESIS_PROFILE=deterministic \
	    $(CURDIR)/$(PYTEST) -m model \
	    --cov=app --cov-branch --cov-report=term-missing

test-perf:
	cd backend && $(CURDIR)/$(PYTEST) -m perf

test-e2e:
	cd frontend && npx playwright test --config ../e2e/playwright.config.ts

test-all: test test-model test-perf test-e2e
