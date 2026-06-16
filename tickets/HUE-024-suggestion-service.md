---
id: HUE-024
title: Suggestion service: enumeration, ranking and the fallback ladder
type: task
status: done
milestone: 8
batch: services
layer: services
depends_on: [HUE-015, HUE-014, HUE-013, HUE-016]
implements: [FR-36, FR-37, FR-38, FR-39, FR-40, FR-41, FR-42, FR-43, NFR-5]
tests_required: true
estimate: 5
---

## Background
The suggestion service drives the outfit flow (architecture §4.3): load the inventory by type, fail fast on an empty requested slot (FR-36), enumerate anchors-first under `MAX_ANCHOR_CANDIDATES` with an injected shuffle (FR-42, NFR-5), evaluate and rank via the pure matcher, apply the fallback ladder, and render explanations from each `EvaluationResult` (FR-38).

## Technical requirements
- `app/services/suggestion_service.py`: load inventory grouped by type; fail fast naming every empty requested slot (FR-36)
- Anchor enumeration (bottom × outermost upper layer × covered layers), shuffled via an **injected `random.Random`** and capped by `MAX_ANCHOR_CANDIDATES` (NFR-5, FR-42)
- Evaluate with `matcher.slots`/`harmony`, score and select with `matcher.ranking` (≤3 distinct, best-first — FR-39/FR-40/FR-41), echo slots qualified with minor echoes recorded (FR-11/FR-22)
- Fallback ladder (FR-43): all-neutral anchors + neutral echo slots flagged as fallback; else zero results with the constraining slot named + hint
- Render `explanation` from each `EvaluationResult` via `matcher.explain` (FR-37, FR-38); imports `matcher`, `storage`; not `api`

## Definition of done (acceptance criteria)
- [x] Empty requested slot → fail fast naming the slots (FR-36)
- [x] Up to 3 distinct ranked combinations returned, each harmonious per FR-15; explanations rendered from the EvaluationResult (FR-37/FR-38)
- [x] Fallback ladder produces flagged neutral-based results or a named-constraint zero result (FR-43); enumeration capped + shuffled (NFR-5, FR-42)
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test-perf` for evaluation/enumeration (§12.3.5)) — deferred to HUE-039 (perf suite does not yet exist)
- [x] Ticket status + notes updated in the same commit

## Tests / verification
Service-level tests over engineered wardrobes (HUE-012) with a seeded RNG, plus the §8.1 invariant pattern and the §4.9.4 oracle (re-evaluate each returned combination; assert scheme/echoes/explanation match). Exact-outcome wardrobes pin the fallback rungs and the zero-result shape. Perf at 500 garments is HUE-039.

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `app/services/suggestion_service.py`; `EmptySlotsError`, `EchoRecord`, `SuggestionCombination`, `SuggestionResult` types; `suggest(include_optional, engine, rng)` loads wardrobe via `id(garment)` identity index (matcher↔DB bridge), calls `matcher.ranking.rank`, handles zero-result sentinel (constraining_slot → hint), builds combinations with `matcher.explain.render` explanations; `tests/services/test_suggestion_service.py` (23 tests — FR-36 fail-fast, normal combinations, §4.9.4 oracle re-evaluation, neutral-based scheme, zero-result with hint). `make test` → 739 passed, 1 skipped, 0 warnings. `make test-perf` deferred to HUE-039 (perf suite not yet built).
- Sanity: `cd backend && .venv/bin/pytest tests/services/test_suggestion_service.py -q`
