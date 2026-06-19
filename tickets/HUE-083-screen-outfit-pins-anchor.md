---
id: HUE-083
title: Outfit-request pin picker and anchor controls
type: story
status: todo
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-071]
implements: [FR-44, FR-45]
tests_required: true
estimate: 3
---

## User story
As the owner
I want to build an outfit around a chosen garment or a colour scheme
so that I can ask "suggest around this jacket" or "an outfit around teal".

## Acceptance criteria

**Scenario 1: Pin a garment**
- Given the "Build around a garment" section
- When I open the picker and pin a garment
- Then a removable pin chip appears and the request `pins` maps the slot key → garment id; "Suggest outfits around this" pins-and-generates in one action (FR-44)

**Scenario 2: One-piece pin auto-deselects base**
- Given I pin a one-piece (dress/jumpsuit) to Lower body
- Then Base is auto-deselected with the note (FR-50.2)

**Scenario 3: Colour/scheme anchor**
- Given the "Build around a colour" section
- When I choose a colour family and/or a scheme
- Then the request `anchor` carries `{ family?, scheme? }`; scheme options include Any/Neutral-based/Monochromatic/Analogous/Complementary/Triadic (FR-45)

**Scenario 4: Unsatisfiable**
- Given no combination honours the pin/anchor
- Then the zero-result `explanation` + `hint` render verbatim (FR-43)

## Technical approach
- Add the pin picker modal (wardrobe browse; "Pin to request" / "Suggest outfits around this") and removable pin chips, composing `pins` (contract §2.12); a one-piece pin auto-deselects `base`
- Add the colour-family swatch chips and the segmented scheme row composing `anchor` (FR-45)
- Reuse the results structure from HUE-071/HUE-080; no garment names (HANDOFF-05)

## Design references
- Wireframes: docs/04-wireframes/05-outfit-request.md (pinned state, pin picker, anchor section); HANDOFF-05

## Tests
- `Suggest.test.tsx` (§10.1): pin picker composes `pins`; one-piece pin auto-deselects base with note; anchor composes `{family,scheme}`; unsatisfiable → zero-result verbatim
- Covered end-to-end by E2E (HUE-085)

## QA steps
- [ ] Pin a jacket → expect a pin chip and `pins` in the request; results all include it
- [ ] Pin a dress to Lower body → expect Base auto-deselected with the note
- [ ] Choose family Teal + scheme Analogous → expect `anchor:{family,scheme}` and matching results
- [ ] Pin something impossible → expect verbatim zero-result explanation + hint

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher-touching work: n/a
- [ ] Detection-touching work: n/a
- [ ] Evaluation/inventory-perf-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6) — deferred to HUE-085
- [ ] QA steps recorded and repeated in the chat completion report
- [ ] Ticket status + notes updated in the same commit (§12.3.7)

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
