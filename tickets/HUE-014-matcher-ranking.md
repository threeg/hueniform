---
id: HUE-014
title: Implement matcher.ranking
type: task
status: todo
milestone: 8
batch: matcher
layer: matcher
depends_on: [HUE-013, HUE-011]
implements: [FR-39, FR-40, FR-41, FR-42, FR-43, NFR-9]
tests_required: true
estimate: 5
---

## Background
Ranking composes the score (scheme strength, echo bonus, variety), enforces distinctness and the cap of three, and implements the fallback ladder, producing the `EvaluationResult` that explanation renders from. Enumeration's shuffle takes an injected `random.Random` so unit tests are exactly reproducible (§4.7).

## Technical requirements
- `app/matcher/ranking.py`: the `EvaluationResult` value (matched scheme, per-garment roles, echoes found, score components, and on failure the constraining slot)
- Score composition in descending weight: scheme strength (FR-41.1), echo bonus (FR-41.2), variety factor (FR-41.3), weights from `constants.py`
- Up to 3 distinct combinations, best-first (FR-39, FR-40); variety applied greedily so results don't all reuse the same garments
- Fallback ladder (FR-43): all-neutral anchors + neutral echo slots; else zero results with the constraining slot named
- Injected `random.Random` for the shuffle (FR-42 at system level; deterministic in tests); standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [ ] Scheme strength orders correctly (180° over 165°; narrower analogous over wider; mono/neutral perfect)
- [ ] Echo bonus and variety order correctly; never more than 3; all pairwise distinct (FR-39, FR-40)
- [ ] Fallback ladder produces flagged neutral-based results, else an EvaluationResult naming the constraining slot (FR-43)
- [ ] Standard library only; passes the §5.2 allowlist
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_ranking.py` (§4.7) with a seeded `random.Random`: scheme-strength, echo-bonus and variety ordering; distinctness and the cap; exactly-two-valid returns two; fallback ladder's two rungs and the zero-result EvaluationResult against a wardrobe engineered so one slot is provably the constraint (HUE-012).

## Notes
- 2026-06-15 — created
