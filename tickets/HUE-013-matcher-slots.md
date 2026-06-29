---
id: HUE-013
title: Implement matcher.slots
type: task
status: done
milestone: 8
batch: matcher
layer: matcher
depends_on: [HUE-010, HUE-011, HUE-012]
implements: [FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-22, NFR-9]
tests_required: true
estimate: 5
---

## In plain English
Sets the rules for how an outfit is put together — which kinds of garment can fill which positions, which layer sets the tone when clothes are layered, and which pieces are hidden underneath and so don't need to match.

## Background
Slots define which garments can occupy which roles in an outfit: type-to-slot eligibility (FR-16/FR-17), anchor identification with layering dominance (FR-18/FR-19), the covered-layer constraint (FR-20) and echo-slot qualification with echo recording (FR-21/FR-22).

## Technical requirements
- `app/matcher/slots.py`: type→slot eligibility and required-slot composition (FR-16, FR-17)
- Anchor identification: bottom + upper-body layers, outermost dominant (jacket > jersey > top) (FR-18)
- Scheme-set assembly: dominant-layer primaries + bottom primaries + all anchors' secondaries; covered-layer primaries excluded (FR-19, FR-20)
- Covered-layer constraint (FR-20) and echo-slot qualification (FR-21): each primary/secondary is neutral, in-scheme or an echo of an anchor colour
- Record minor-colour echoes for the bonus (FR-22, FR-11); standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [ ] All three layering permutations resolve the correct anchors and dominant layer (FR-18)
- [ ] Scheme set assembled per FR-19; covered layers constrained per FR-20; echo slots qualified per FR-21
- [ ] Minor-colour echoes recorded (FR-22); type-to-slot eligibility enforced (FR-16/FR-17)
- [ ] Standard library only; passes the §5.2 allowlist
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_slots.py` (§4.6): the three dominance permutations; scheme-set assembly and covered-layer exclusion; covered-layer pass/fail/all-neutral; per-slot echo qualification including minor echoes recorded; FR-16/FR-17 over the engineered wardrobes (HUE-012).

## Notes
- 2026-06-15 — created
- 2026-06-15 — done. `app/matcher/slots.py`: GARMENT_TYPES/REQUIRED_SLOTS/OPTIONAL_SLOTS/ECHO_SLOTS constants (FR-16/FR-17); `dominant_layer`/`covered_upper_layers`/`get_anchor_types` (FR-18); `SchemeSet` + `build_scheme_set` with covered-layer-primary exclusion (FR-19/FR-20); `get_anchor_chromatic_families`; `check_covered_layer` (FR-20); `check_anchor_secondaries` (FR-9); `EchoQualification` + `qualify_echo_slot` (FR-21/FR-22). `tests/matcher/test_slots.py`: 69 tests covering all three layering permutations, scheme-set assembly, covered-layer branches, echo-slot qualification, minor-echo recording, and wardrobe-fixture integration. 466 backend tests, all green; app/matcher/ 100% line+branch.
