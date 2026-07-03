---
id: HUE-083
title: Outfit-request pin picker and anchor controls
type: story
status: done
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-071]
implements: [FR-44, FR-45]
tests_required: true
estimate: 3
---

## In plain English
Adds the on-screen controls that let the owner choose one garment to build an outfit around, or pick a colour family and style of colour combination, so they can ask for ideas like "suggest something around this jacket" or "an outfit around teal".

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
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy §12.2 and passing in `make test`
- [x] Matcher-touching work: n/a
- [x] Detection-touching work: n/a
- [x] Evaluation/inventory-perf-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6) — deferred to HUE-085
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit (§12.3.7)

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-07-02 — implemented. Added pin picker modal (inventory garments shown; "Pin to
  request" and "Suggest outfits around this" actions); removable pin chips (slot →
  garment id); one-piece pin auto-deselects base via extended `isOnePieceOnly` check.
  Added anchor section: family swatch chips (single-select + clear) and scheme segmented
  row (Any + 5 named schemes). `handleSuggest` builds `pins` and `anchor` fields in the
  request when set. 15 new tests across two suites. 1109 backend + 181 frontend tests
  pass, zero warnings.
- Sanity test: `cd frontend && npx vitest run src/routes/Suggest.test.tsx --reporter=verbose 2>&1 | grep -E "pin picker|anchor controls|passed"`

## QA steps
- [ ] Open /suggest → expect a "Pin a garment" button and "Build around a colour" section with family chips and scheme row
- [ ] Click "Pin a garment" → picker modal opens; one garment card visible; close with × or backdrop
- [ ] Click "Pin to request" on a jumper → modal closes; pin chip (thumbnail + "Jumper" label + ×) appears; clicking Suggest outfits includes `pins.mid` in the request
- [ ] Click × on a pin chip → chip disappears and pin is removed from subsequent requests
- [ ] Click "Suggest outfits around this" → modal closes, pin chip appears, and request is fired immediately (results appear without clicking Suggest)
- [ ] Pin a dress → Base chip is disabled and the one-piece note shows
- [ ] Click a colour family chip (e.g. Teal) → chip highlights; clicking Suggest sends `anchor.family = "Teal"`; clicking the chip again deselects (or use Clear); anchor absent from next request
- [ ] Click Analogous in the scheme row → button highlights; request includes `anchor.scheme = "analogous"`; clicking Any reverts; anchor absent from next request
- [ ] Select Teal + Analogous together → request includes both; results show outfits around teal analogous combos
