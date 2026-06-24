---
id: HUE-068
title: Suggestion service — slot-selection and per-category constraint rewrite
type: task
status: done
milestone: 14
batch: services
layer: services
depends_on: [HUE-061, HUE-063, HUE-064, HUE-065, HUE-024]
implements: [FR-17, FR-18, FR-19, FR-20, FR-36, FR-49, FR-50, FR-51, FR-52, NFR-5]
tests_required: true
estimate: 5
---

## Background
Rewrite `suggestion_service` for the v0.2.0 outfit flow (architecture §4.3): resolve the
**selected slot set** by layering the request over the FR-51 defaults, enforce the **mandatory
lower-body floor**, load the inventory grouped by category, run the new anchors-first
enumeration over the four-layer/one-piece model, and apply the **per-category slot constraint**
(FR-52) as a request-time candidate filter. Pins and colour/scheme anchors are added later
(E06); the count is added in HUE-078 (E09) — this ticket establishes the slot-selection core
with the default count.

## Technical requirements
- `app/services/suggestion_service.py`:
  - Resolve selected slots from `{slots}` (bool) over the FR-51 defaults; enforce the mandatory `lower_body` floor; **fail fast** (FR-36) on empty selection / no lower body / a selected slot with no eligible garment (`409 empty_slots` naming the slots) / an unknown slot key
  - Anchor enumeration over `lower_body` × present upper layers (`base`/`shirt`/`mid`/`outer`), one-piece spanning `lower_body`+`base` and excluding a separate `base`/lower-body (FR-18, FR-50); interleaved + capped via the injected RNG (NFR-5, NFR-10)
  - **Per-category slot constraint (FR-52)**: narrow a slot's candidate set to the requested subset of its own categories; reject an empty list or a category not in the slot; a `lower_body` one-piece-only constraint excludes a separately selected `base` (FR-50.2)
  - Evaluate/rank via the rewritten matcher (HUE-061/063/064); render explanations from each `EvaluationResult` (FR-37/FR-38); imports `matcher`, `storage`; not `api`
- Per-category constraint adds **no new matcher maths** (categories within a slot are equivalent)

## Definition of done (acceptance criteria)
- [ ] Selected-slot resolution over FR-51 defaults with the mandatory floor; fail-fast paths correct (FR-36, FR-51)
- [ ] New enumeration over four-layer/one-piece anchors, interleaved + capped (FR-18, FR-50, NFR-5)
- [ ] FR-52 candidate filter applied and validated; one-piece/base exclusion honoured (FR-50.2, FR-52)
- [ ] Explanations from `EvaluationResult`; layer rule kept (imports not `api`)
- [ ] Tests added/updated per §12.2 and passing in `make test`; `make test-perf` is HUE-084
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`services/test_suggestion_service.py` (§7.4, §8.1) with a seeded RNG: default/partial slot
selection (beach example), the mandatory floor, fail-fast `409`/unknown-key, the FR-52
candidate filter and its `422` cases, one-piece spanning, and the §4.9.4 oracle over engineered
wardrobes. Perf at 500 garments/count 25 is HUE-084.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-06-24 — implemented. `suggestion_service.py` rewritten: new `suggest(slots_request: dict[str, bool | list[str]], engine, rng)` signature; slot resolution over FR-51 defaults; mandatory `lower_body` floor (raises `InvalidSlotError`); `InvalidCategoryFilterError` for empty/wrong-slot category lists; `_apply_category_filters` filters wardrobe before `rank`; one-piece/base auto-exclusion (FR-50.2); `_SLOT_CATEGORIES` map computed from `C.CATEGORY_SLOT`. `pyproject.toml` import-linter `ignore_imports` updated for new `suggestion_service → matcher.constants` edge. **API layer (HUE-069 scope)** also landed here: `schemas.py` gains `SlotConstraint` + `SuggestionRequest.slots`; `suggestions.py` router updated to translate `slots` dict to service format and handle `InvalidCategoryFilterError`; `api/test_suggestions.py` updated to `slots` key and mandatory-floor 422 test. Service tests updated from `frozenset` to dict; new test classes: `TestSlotDeselection`, `TestMandatoryFloor`, `TestCategoryFilter`, `TestOnePieceExclusion`. 1043 backend + 134 frontend pass, zero warnings, 1 expected skip.
- Sanity test: `cd backend && .venv/bin/pytest tests/services/test_suggestion_service.py -q`

## QA steps
- None — no UI changes in this ticket.
