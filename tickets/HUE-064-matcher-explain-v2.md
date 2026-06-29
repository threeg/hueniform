---
id: HUE-064
title: matcher.explain — new slot vocabulary and neutral-based vs neutral-fallback wording
type: task
status: done
milestone: 14
batch: matcher
layer: matcher
depends_on: [HUE-061, HUE-063, HUE-015]
implements: [FR-37, FR-38, NFR-9]
tests_required: true
estimate: 2
---

## In plain English
Updates the plain-English reasons the app gives for each outfit suggestion so they describe the new layered tops, one-piece items and accessories, and clearly explain when a look is built around neutrals.

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
- [x] Explanations use the new slot vocabulary and name one-piece/adornment roles correctly (FR-37)
- [x] First-class neutral-based vs neutral-fallback wording is faithful to the result (FR-38)
- [x] Rendered only from `EvaluationResult` (the §4.9 structural-purity check still holds)
- [x] HUE-059 snapshot explanation goldens updated and committed (§4.10)
- [x] Tests added/updated per §12.2 and passing in `make test`; matcher 100% gate holds (§12.3.3)
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_explain.py` (§4.9) — construction and covariance tests over the new vocabulary
and the neutral-based/fallback wording; the §4.9.4 integration oracle still ties rendered text
to the evaluation. Snapshot explanation diff reviewed.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-06-19 — implemented. Added `_SLOT_LABELS` dict to `explain.py` mapping slot keys to human-readable labels (`lower_body` → `lower body`, `outer` → `outer layer`, `mid` → `mid-layer`). Updated `render()` with two new role-label branches: one-piece garments (dress/jumpsuit in lower_body) get `"one-piece"` instead of `"anchor"`; minor adornments (glasses, earrings, necklace, watch, ring, bracelet) get `"adornment"` instead of `"neutral"`. First-class neutral-based vs fallback wording already correctly distinguished by `is_fallback` flag. `explanations.json` snapshot updated: `lower_body:` → `lower body:` in all entries. New `TestSlotVocabulary` class (7 tests): lower-body label with space, outer-layer and mid-layer labels, one-piece role, minor-adornment role, first-class-neutral not labelled fallback, fallback wording distinct from first-class. Updated `test_all_requested_slots_appear` to use `_SLOT_LABELS` for the assertion. `make test` passes: 997 backend + 134 frontend, 0 failures; matcher 100% line+branch.
- Sanity test: `cd backend && .venv/bin/pytest tests/matcher/test_explain.py -q`

## QA steps
No frontend UI changes in this ticket.
