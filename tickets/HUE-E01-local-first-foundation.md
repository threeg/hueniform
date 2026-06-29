---
id: HUE-E01
title: Local-first foundation and meta-goal
type: epic
status: done
milestone: 8
batch: scaffolding
layer: repo
depends_on: []
implements: [NFR-1, NFR-2, NFR-3, NFR-7, NFR-8, NFR-9]
tests_required: false
estimate: 8
---

## In plain English
The groundwork that makes the whole app run entirely on the owner's own computer with no internet needed, started and used with a single command, along with the safety checks that keep its building blocks tidy as everything else is added.

## Summary
Establish the single repository, the backend and frontend skeletons, the test tooling and quality gates, and the single-command run — everything that makes Hueniform a local-first, offline, single-command application whose process is itself a deliverable (brief meta-goal). This epic delivers the architecture's dependency-rule enforcement and the test harness every other epic relies on.

## Scope
- **In scope:**
  - Repository initialisation, structure and the committed docs/tickets (brief §13)
  - Backend skeleton: package layout, app factory, settings/data-dir seam, Makefile targets
  - Frontend skeleton: Vite + TypeScript + React, routing, sidebar shell, dev proxy
  - Test tooling: pytest, coverage, Hypothesis, import-linter + std-library allowlist, Vitest + RTL + MSW, Playwright; the make targets
  - Shared test fixtures (synthetic image generator, masks, palette tables, MSW handlers)
  - Single-command run and production static serving (NFR-2); the performance and E2E capstones
- **Out of scope:**
  - Any colour logic, detection, persistence behaviour, endpoints or screens (their own epics)
  - A hosted CI service (test strategy §13: none for MVP)

## Success criteria
All child tickets are done; `make setup` then `make run` starts the app offline with a single command and prints the URL (NFR-2); the dependency rule is enforced by `make test`; brief success criteria 4–6 (local/offline single command; every milestone documented; tickets tracked as Markdown and updated as work completes) are met.

## Children
- HUE-001 — Initialise the repository
- HUE-002 — Backend skeleton and application settings
- HUE-003 — Frontend skeleton and navigation shell
- HUE-004 — Backend test tooling and dependency-rule gate
- HUE-005 — Frontend test tooling and Playwright harness
- HUE-006 — Shared test fixtures and palette tables
- HUE-025 — API foundation: schemas, error envelope, health, static serving
- HUE-032 — Frontend API client, query layer and shared components
- HUE-038 — Single-command run and production serving
- HUE-039 — Performance suite and 500-garment fixture
- HUE-040 — End-to-end smoke suite

## References
- docs/01-project-brief.md §11 (success criteria 4–6), §13
- docs/03-architecture.md §2.1, §5, §7.1
- docs/05-test-strategy.md §2, §5, §9, §11, §12

## Notes
- 2026-06-15 — created
