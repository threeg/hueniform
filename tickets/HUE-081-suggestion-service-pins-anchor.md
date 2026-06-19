---
id: HUE-081
title: Suggestion service — pins and colour/scheme anchor
type: task
status: todo
milestone: 14
batch: services
layer: services
depends_on: [HUE-068, HUE-063]
implements: [FR-44, FR-45]
tests_required: true
estimate: 3
---

## Background
E06 (F1/F2): add **pins** (FR-44) and **colour/scheme anchors** (FR-45) to the suggestion
service. A pin forces a garment into its slot in every combination; a colour-family anchor
requires that family on an anchor garment; a named-scheme anchor requires that matched scheme.
Both compose with the FR-51 selection and the FR-52 per-category constraint (HUE-068) and use
the HUE-063 ranking/pruning. Unsatisfiable pins/anchors resolve as the FR-43 zero result.

## Technical requirements
- `app/services/suggestion_service.py`:
  - **Pins (FR-44)**: each pin narrows its slot to one garment (the slot becomes selected); the garment's category must map to the slot key; multiple pins hold simultaneously; a one-piece pin to `lower_body` excludes a separately selected `base` (FR-50.2)
  - **Anchor (FR-45)**: prune candidates whose scheme set lacks `anchor.family` on an anchor garment, and/or whose matched scheme ≠ `anchor.scheme`; both when both given
  - Composition with FR-52 (a pin must agree with a same-slot constraint) and the count
  - Unsatisfiable pin/anchor → zero result with the reason (FR-43); imports `matcher`/`storage`, not `api`

## Definition of done (acceptance criteria)
- [ ] Pins honoured in every combination; multiple pins; category→slot agreement; one-piece/base exclusion (FR-44, FR-50.2)
- [ ] Colour-family and named-scheme anchors prune correctly; both compose (FR-45)
- [ ] Pin/constraint agreement enforced; unsatisfiable → zero result with reason (FR-43, FR-52)
- [ ] Tests added/updated per §12.2 and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`services/test_suggestion_service.py` (§4.7, §7.4) with a seeded RNG: pin honoured / unsatisfiable
pin → zero; family-only, scheme-only and both anchors; pin↔constraint agreement; the §4.9.4
oracle over engineered wardrobes.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
