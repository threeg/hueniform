---
id: HUE-012
title: Wardrobe and scenario fixtures
type: task
status: done
milestone: 8
batch: tooling
layer: tooling
depends_on: [HUE-009, HUE-010]
implements: [NFR-9]
tests_required: true
estimate: 3
---

## In plain English
Builds a set of carefully designed sample wardrobes — each one set up to test a particular situation, like having two good outfits or none at all — so the outfit-matching rules can be checked against known, predictable cases.

## Background
The slot, ranking and suggestion-evaluation tests need engineered wardrobes built from matcher value types (test strategy §11.2). Building them once, after the `Garment`/`Colour` types exist, gives one definition usable as plain values for unit tests and (later) as persisted rows for integration tests.

## Technical requirements
- `backend/tests/fixtures/wardrobes.py`: factory functions returning plain matcher values — `single_valid_outfit()`, `two_valid_outfits()`, `neutral_fallback_only()`, `no_valid_outfit_constrained_by(slot)`, `rich_echo_wardrobe()` (§11.2)
- Each factory documented with the FR it exists to pin down
- Construction uses only the `Garment`/`Colour` types and the taxonomy (no evaluator dependency — evaluation is the test's job)
- Designed so the same definitions can later materialise as persisted rows (one definition, two materialisations)

## Definition of done (acceptance criteria)
- [x] All five engineered scenario factories present and documented with their FR
- [x] Factories return well-formed garments (valid palettes summing to 100, valid types)
- [x] No dependency on harmony/slots/ranking evaluation in construction
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/` and `api/` suites import these factories. A self-check test asserts each factory's garments are structurally valid. Load-bearing for HUE-013, HUE-014 and the §7.4 suggestion tests.

## Notes
- 2026-06-15 — created
- 2026-06-15 — done. Five factories in `tests/fixtures/wardrobes.py`: `single_valid_outfit` (complementary Red/Teal, FR-15); `two_valid_outfits` (two distinct Red tops, FR-40); `neutral_fallback_only` (all-neutral anchors, FR-13 §1); `no_valid_outfit_constrained_by(slot)` (echo-slot Blue or clashing Chartreuse/Blue anchors, FR-43); `rich_echo_wardrobe` (Red primary 87% + Teal minor 13% on top, FR-11). Self-check test validates structural validity. 396 backend tests, all green; app/matcher/ 100%.
