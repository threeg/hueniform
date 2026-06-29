---
id: HUE-040
title: End-to-end smoke suite
type: task
status: done
milestone: 8
batch: tooling
layer: tooling
depends_on: [HUE-033, HUE-034, HUE-035, HUE-036, HUE-037, HUE-027, HUE-028, HUE-029, HUE-030, HUE-031, HUE-020, HUE-038]
implements: [NFR-7]
tests_required: true
estimate: 5
---

## In plain English
Automatically clicks through the real app from start to finish to prove the main journeys work, adding a garment, asking for an outfit, and handling an empty request, so problems are caught before anyone uses it.

## Background
A thin Playwright smoke suite proves the assembled system works against the genuinely built app — especially valuable given AI-driven implementation (test strategy §9). Three journeys, Chromium and Firefox (NFR-7), nothing mocked.

## Technical requirements
- Playwright `webServer` launches the production-style Uvicorn process (built SPA, real detection with the real model, temporary `data/`) (HUE-038)
- Journey 1 — add a garment: upload a synthetic fixture → confirm-and-correct (adjust a proportion, select a type; save disabled until chosen) → save → appears in inventory and survives type+family filtering
- Journey 2 — request an outfit: against a pre-seeded engineered wardrobe (HUE-039 seeding) request one optional slot → ranked cards with scheme chip, per-slot tiles, non-empty explanation; 'Suggest again' returns a valid response
- Journey 3 — empty-slot rejection: request a slot with no garments → `409 empty_slots` renders on the request panel
- Chromium + Firefox projects (NFR-7); skip with an explicit message if the model or browsers are missing

## Definition of done (acceptance criteria)
- [x] All three journeys pass on Chromium and Firefox against the built app with the real model (NFR-7)
- [x] `webServer` boots the production-style process; suite skips clearly if model/browsers absent
- [x] `make test-e2e` runs the suite
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable (`make test-e2e` (§12.3.6))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`e2e/*.spec.ts` (§9): the three journeys, asserting user-visible behaviour only (contract details are §7's job). Mandatory in DoD for user-flow-touching tickets (§12.3.6); part of `make test-all` at milestone completion.

## Notes
- 2026-06-15 — created
- 2026-06-17 — implemented and passing. `e2e/smoke.spec.ts` runs three serial journeys (empty-slot rejection first while wardrobe is empty, add-garment second, outfit-request third against a seeded wardrobe). `playwright.config.ts` writes the temp data-dir path to `.e2e-data-dir` at config-eval time; the spec reads that file instead of importing the config to avoid running side-effects twice. The webServer command cleans and recreates the temp dir inline so cleanup runs exactly once regardless of how many times Playwright evaluates the config. The `NODE_PATH` env var in `make test-e2e` makes `@playwright/test` resolvable from `e2e/`. Count assertions use `/[1-9]/` rather than exact counts because both browser projects share one server and one DB. 6/6 pass; `make test` zero warnings.
