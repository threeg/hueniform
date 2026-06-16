---
id: HUE-031
title: Suggestions endpoint
type: task
status: done
milestone: 8
batch: api
layer: api
depends_on: [HUE-025, HUE-024]
implements: [FR-17, FR-36, FR-37, FR-38, FR-39, FR-40, FR-41, FR-42, FR-43, NFR-5]
tests_required: true
estimate: 5
---

## Background
`POST /api/suggestions` (contract §2.12) is the outfit request: required slots always included, optional slots selected via `include`. It returns up to three ranked combinations, the zero-result shape with a hint, or `409 empty_slots`, all driven by the suggestion service.

## Technical requirements
- `POST /api/suggestions` with `include` (optional slots; omitted default false); required slots always included (FR-17)
- Combinations found: ≤3 ranked best-first, each with `scheme`, `slots`, `echoes`, `explanation`, `fallback` (contract §2.12, FR-39/FR-40/FR-41)
- Zero results: `{combinations: [], explanation, hint}` naming the constraining slot (FR-43b)
- `409 empty_slots` (with `details.empty_slots`) for an empty requested slot (FR-36); `422 invalid_request` for unknown slot keys
- Non-determinism permitted across identical requests (FR-42); within NFR-5 at 500 garments (perf in HUE-039)

## Definition of done (acceptance criteria)
- [x] Found/zero/fail-fast response shapes match contract §2.12 exactly (FR-36–FR-43)
- [x] `fallback: true` marks neutral-based fallbacks; zero result carries `explanation`+`hint` naming the constraint
- [x] `409 empty_slots` and `422 invalid_request` returned per contract
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test-perf` for suggestion evaluation (§12.3.5)) — deferred to HUE-039 which implements the perf suite
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_suggestions.py` (§7.4, §8.1): the FR-42-safe invariant pattern (≤3 distinct, correct slots/types) plus the §4.9.4 oracle (re-evaluate returned combinations; assert scheme/echoes/explanation match); exact-outcome wardrobes for the fallback rungs and zero-result; `409 empty_slots`/`422 invalid_request`.

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `suggestion_service.py` — `InvalidSlotError`, `OPTIONAL_SLOTS` import,
  slot-key validation inside `suggest()` (keeps the API layer free of direct `matcher.slots`
  imports, contract 5 preserved); `garment_service.py` — `get_garments_by_ids` batch loader
  (2-query pattern for colour hydration); `schemas.py` — `SuggestionRequest`, `EchoOut`,
  `CombinationOut`, `SuggestionResponse`; `suggestions.py` (new) — POST /api/suggestions;
  `main.py` wired; `test_suggestions.py` — 26 tests covering found shape (FR-42-safe
  invariants), §4.9.4 oracle (scheme + echo oracle over known wardrobes), zero-result,
  optional slot inclusion/exclusion, 409/422 error paths. `make test-perf` gate deferred
  to HUE-039. `make test` → 888 passed, 1 skipped, 0 warnings; 5 import contracts kept.
- Sanity: `cd backend && .venv/bin/pytest tests/api/test_suggestions.py -q`
