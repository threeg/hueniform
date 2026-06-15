---
id: HUE-012
title: Wardrobe and scenario fixtures
type: task
status: todo
milestone: 8
batch: tooling
layer: tooling
depends_on: [HUE-009, HUE-010]
implements: [NFR-9]
tests_required: true
estimate: 3
---

## Background
The slot, ranking and suggestion-evaluation tests need engineered wardrobes built from matcher value types (test strategy §11.2). Building them once, after the `Garment`/`Colour` types exist, gives one definition usable as plain values for unit tests and (later) as persisted rows for integration tests.

## Technical requirements
- `backend/tests/fixtures/wardrobes.py`: factory functions returning plain matcher values — `single_valid_outfit()`, `two_valid_outfits()`, `neutral_fallback_only()`, `no_valid_outfit_constrained_by(slot)`, `rich_echo_wardrobe()` (§11.2)
- Each factory documented with the FR it exists to pin down
- Construction uses only the `Garment`/`Colour` types and the taxonomy (no evaluator dependency — evaluation is the test's job)
- Designed so the same definitions can later materialise as persisted rows (one definition, two materialisations)

## Definition of done (acceptance criteria)
- [ ] All five engineered scenario factories present and documented with their FR
- [ ] Factories return well-formed garments (valid palettes summing to 100, valid types)
- [ ] No dependency on harmony/slots/ranking evaluation in construction
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/` and `api/` suites import these factories. A self-check test asserts each factory's garments are structurally valid. Load-bearing for HUE-013, HUE-014 and the §7.4 suggestion tests.

## Notes
- 2026-06-15 — created
