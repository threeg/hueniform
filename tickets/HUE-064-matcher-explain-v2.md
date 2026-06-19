---
id: HUE-064
title: matcher.explain — new slot vocabulary and neutral-based vs neutral-fallback wording
type: task
status: todo
milestone: 14
batch: matcher
layer: matcher
depends_on: [HUE-061, HUE-063, HUE-015]
implements: [FR-37, FR-38, NFR-9]
tests_required: true
estimate: 2
---

## Background
`explain.render` must describe the v0.2.0 model: the four-layer vocabulary (`mid`/`outer`
labels), one-piece garments, the two adornment tiers, and the distinction between a
**first-class neutral-based** outfit and a **neutral fallback** (FR-37, FR-38). It renders
text **only** from the `EvaluationResult` (architecture §2.2), so it cannot drift from the
evaluation. Builds on HUE-061 (slot vocabulary) and HUE-063 (the neutral/fallback result fields).

## Technical requirements
- `app/matcher/explain.py` — render: the matched scheme including `neutral-based`; each
  garment's role and slot using the new labels (Base/Shirt/Mid-layer/Outer layer, lower body,
  one-piece, adornments); each recorded echo (family, from/to slot), including minor-adornment
  echoes; wording that distinguishes a first-class neutral-based outfit from a neutral fallback
- Rendered purely from `EvaluationResult`; standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [ ] Explanations use the new slot vocabulary and name one-piece/adornment roles correctly (FR-37)
- [ ] First-class neutral-based vs neutral-fallback wording is faithful to the result (FR-38)
- [ ] Rendered only from `EvaluationResult` (the §4.9 structural-purity check still holds)
- [ ] HUE-059 snapshot explanation goldens updated and committed (§4.10)
- [ ] Tests added/updated per §12.2 and passing in `make test`; matcher 100% gate holds (§12.3.3)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_explain.py` (§4.9) — construction and covariance tests over the new vocabulary
and the neutral-based/fallback wording; the §4.9.4 integration oracle still ties rendered text
to the evaluation. Snapshot explanation diff reviewed.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
