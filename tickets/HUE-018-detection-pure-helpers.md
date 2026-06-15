---
id: HUE-018
title: Detection pure helpers
type: task
status: done
milestone: 8
batch: detection
layer: detection
depends_on: [HUE-009]
implements: [FR-6, FR-27]
tests_required: true
estimate: 3
---

## Background
Detection's deterministic helpers — proportion integerisation, same-family cluster merging, k-selection and the minimum-foreground fallback predicate — are pure and belong in the default gate (test strategy §6.1). Detection may import only `matcher.taxonomy`, `matcher.colour` and `matcher.constants` (contract 3).

## Technical requirements
- `app/detection/` pure helpers: proportion integerisation (largest-remainder) so cluster weights → integer percentages summing to exactly 100, every entry ≥1, ordering preserved (FR-6)
- Same-family cluster merging: centroids classifying into one family (via `matcher.taxonomy`) merge, weights added
- k-selection heuristic (inertia elbow) over k=1…4
- Minimum-foreground fallback predicate (FR-27): mask coverage below the `constants` threshold → fallback
- Imports limited to `matcher.taxonomy`/`colour`/`constants` plus maths libs (contract 3)

## Definition of done (acceptance criteria)
- [x] Integerisation sums to exactly 100 with ≥1 each and preserved ordering (FR-6)
- [x] Same-family merge and k-selection correct on synthetic inputs; fallback predicate correct at the boundary (FR-27)
- [x] Detection imports only the permitted matcher submodules (import-linter contract 3 holds)
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`backend/tests/detection/test_*.py` (§6.1): integerisation Hypothesis property over weight vectors; same-family merge; k-selection on synthetic inertia curves with known elbows; fallback-predicate boundary rows (§4.3 method).

## Notes
- 2026-06-15 — created
- 2026-06-15 — done: `app/detection/helpers.py` with `to_proportions`, `merge_clusters`, `select_k`, `is_foreground_sufficient`; `MINIMUM_FOREGROUND` and `K_ELBOW_FACTOR` added to `matcher.constants`; 29 tests (including Hypothesis property) in `tests/detection/test_helpers.py`; 614 passed, zero warnings, 100% matcher gate, import-linter contract 3 held.
