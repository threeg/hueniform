---
id: HUE-039
title: Performance suite and 500-garment fixture
type: task
status: todo
milestone: 8
batch: tooling
layer: tooling
depends_on: [HUE-031, HUE-029, HUE-024]
implements: [NFR-5, NFR-6]
tests_required: true
estimate: 3
---

## Background
NFR-5 and the server half of NFR-6 are asserted at the 500-garment scale (test strategy §8.2) using a seeded, reproducible wardrobe, in a `perf`-marked suite excluded from the default gate.

## Technical requirements
- `backend/tests/fixtures/wardrobes.py::wardrobe_500()`: 500 garments from a seeded RNG with a realistic distribution across the eight types and the family taxonomy, materialised through the storage layer (§11.2)
- `scripts/seed_test_wardrobe.py` (or a make target) seeds a running instance for E2E and manual NFR-6 checks
- `backend/tests/perf/test_bounds.py` marked `perf`: `POST /api/suggestions` (all optional slots) < 2 s, median of 3 (NFR-5); `GET /api/garments` combined filters < 1 s, median of 3 (NFR-6 server half)
- `make test-perf` runs the suite; excluded from `make test`

## Definition of done (acceptance criteria)
- [ ] `wardrobe_500()` seeded and reproducible; seeding CLI/target available
- [ ] NFR-5 and NFR-6-server-half assertions present (median of 3) and passing on the owner's machine
- [ ] `make test-perf` runs them; they are excluded from the default gate
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test-perf` (§12.3.5))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`perf/test_bounds.py` marked `perf` (§8.2): the two timing assertions at 500 garments, median of 3. NFR-4 lives in the `model` suite. Mandatory in DoD for suggestion-/inventory-query-touching tickets (§12.3.5).

## Notes
- 2026-06-15 — created
