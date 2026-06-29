---
id: HUE-039
title: Performance suite and 500-garment fixture
type: task
status: done
milestone: 8
batch: tooling
layer: tooling
depends_on: [HUE-031, HUE-029, HUE-024, HUE-041]
implements: [NFR-5, NFR-6]
tests_required: true
estimate: 3
---

## In plain English
Builds a large pretend wardrobe of 500 items and checks the app still responds quickly when suggesting outfits and filtering clothes, so it never feels sluggish even for someone with a big collection.

## Background
NFR-5 and the server half of NFR-6 are asserted at the 500-garment scale (test strategy §8.2) using a seeded, reproducible wardrobe, in a `perf`-marked suite excluded from the default gate.

## Technical requirements
- `backend/tests/fixtures/wardrobes.py::wardrobe_500()`: 500 garments from a seeded RNG with a realistic distribution across the eight types and the family taxonomy, materialised through the storage layer (§11.2)
- `scripts/seed_test_wardrobe.py` (or a make target) seeds a running instance for E2E and manual NFR-6 checks
- `backend/tests/perf/test_bounds.py` marked `perf`: `POST /api/suggestions` (all optional slots) < 2 s, median of 3 (NFR-5); `GET /api/garments` combined filters < 1 s, median of 3 (NFR-6 server half)
- `make test-perf` runs the suite; excluded from `make test`

## Definition of done (acceptance criteria)
- [x] `wardrobe_500()` seeded and reproducible; seeding CLI/target available
- [x] NFR-5 and NFR-6-server-half assertions present (median of 3) and passing on the owner's machine
- [x] `make test-perf` runs them; they are excluded from the default gate
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable (`make test-perf` (§12.3.5))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`perf/test_bounds.py` marked `perf` (§8.2): the two timing assertions at 500 garments, median of 3. NFR-4 lives in the `model` suite. Mandatory in DoD for suggestion-/inventory-query-touching tickets (§12.3.5).

## Notes
- 2026-06-15 — created
- 2026-06-17 — implemented. `wardrobe_500(seed=42)` added to `tests/fixtures/wardrobes.py`
  with `materialise_wardrobe()` helper; realistic slot distribution across all 8 types and
  all 19 taxonomy families. `backend/tests/perf/test_bounds.py` added with session-scoped
  500-garment client; 2 perf-marked tests (NFR-5: suggestion median 3 runs < 2s; NFR-6
  server half: garment filter median 3 runs < 1s). `scripts/seed_test_wardrobe.py` and
  `make seed-wardrobe` target added for E2E / manual NFR-6 checks.
  `matcher/ranking._enumerate_outfits` refactored to use per-slot shuffle + `islice` for
  both anchor and echo combos (removing the `cap` parameter) — this eliminated a
  combinatorial explosion in the neutral fallback and constraining-slot paths that previously
  materialised up to 30M+ tuples at 500 garments. `MAX_ECHO_COMBOS = 50` added to
  `matcher/constants`. 100% matcher coverage gate maintained (146 stmts, 72 branches).
  Observed timings: suggestion ~530ms (< 2s NFR-5), inventory 2ms (< 1s NFR-6).
  890 backend + 132 frontend pass; `make test-perf` passes in 2.3s total.
  Sanity: `make test-perf`
