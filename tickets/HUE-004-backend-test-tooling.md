---
id: HUE-004
title: Backend test tooling and dependency-rule gate
type: task
status: done
milestone: 7
batch: tooling
layer: tooling
depends_on: [HUE-002]
implements: [NFR-9]
tests_required: true
estimate: 5
---

## In plain English
Puts the automatic checks in place that catch mistakes the moment they appear and make sure each part of the app only relies on the parts it is allowed to, so every later piece of work is kept honest from its very first change.

## Background
The test strategy's default gate, coverage policy and the architecture's dependency-rule enforcement must exist before any backend code is written, so every later ticket is gated from its first commit (test strategy §2, §5, §12).

## Technical requirements
- Add pinned test dependencies to `pyproject.toml`: pytest, pytest-cov (branch mode), Hypothesis, import-linter
- `conftest.py` with the app-factory, temporary-`data/`-dir and `TestClient` fixtures (test strategy §7.1) — real SQLite file, not `:memory:`
- Register `model` and `perf` markers with `--strict-markers` (§2.2)
- Hypothesis derandomised profile for the gate (`derandomize=True`, §4.8)
- import-linter contracts in `pyproject.toml` per test strategy §5.1 (contracts 1–5: the forbidden edges and the layered `api → services → {detection, matcher, storage}` rule)
- `tests/test_architecture.py`: the bespoke std-library allowlist walking `app/matcher/` with `ast` and asserting every import root is in `sys.stdlib_module_names` or `app.matcher` (§5.2)
- `Makefile` targets: `test`, `test-backend` (runs `lint-imports` then pytest excluding `model`/`perf` with `--cov=app --cov-branch`, then the matcher 100% gate `coverage report --include="app/matcher/*" --fail-under=100`), `test-model`, `test-perf`, `test-all` (§2.2)

## Definition of done (acceptance criteria)
- [x] pytest + coverage + Hypothesis + import-linter installed and pinned
- [x] conftest fixtures (tmp data-dir, TestClient) available; markers registered with `--strict-markers`
- [x] import-linter contracts 1–5 declared; `tests/test_architecture.py` std-library allowlist present (runs vacuously until matcher modules exist)
- [x] `make test` / `test-backend` / `test-model` / `test-perf` / `test-all` targets work; matcher coverage gate wired
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
The dependency-rule tests *are* this ticket's tests: `lint-imports` (contracts 1–5) and `tests/test_architecture.py` (§5.2) run in `make test-backend`. They pass vacuously now and bite the moment any later ticket adds an illegal import. A trivial `test_health`-style placeholder confirms the harness runs.

## Notes
- 2026-06-15 — created
- 2026-06-15 — done: dev deps added to pyproject.toml [dev] group: pytest 9.1, pytest-cov 7.1, hypothesis 6.155, import-linter 2.11, httpx2 (starlette 1.3 deprecated httpx in TestClient). conftest.py: `app_settings`/`test_app`/`client` fixtures using tmp_path + create_app(); Hypothesis "deterministic" (derandomize=True) and "default" profiles registered, loaded via HYPOTHESIS_PROFILE env var. 5 import-linter contracts in pyproject.toml (forbidden + 1 covering api-is-a-leaf, matcher-is-pure, detection-allowed-matcher-submodules, storage-isolation, api-bypasses-services). test_architecture.py: stdlib allowlist (ast walk, rglob) + trivial harness test — both pass vacuously on empty skeleton. make test-backend: lint-imports → pytest (5 contracts KEPT, 2 tests) → matcher 100% coverage gate (0 stmts, 100%). make test runs clean.
