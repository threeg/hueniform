---
id: HUE-071
title: Outfit-request slot selector and category-constraint checklist
type: story
status: todo
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-067, HUE-037]
implements: [FR-36, FR-49, FR-50, FR-51, FR-52]
tests_required: true
estimate: 5
---

## User story
As the owner
I want to choose which slots an outfit request includes and constrain a slot to specific categories
so that I can ask for, say, a beach outfit or "lower body = shorts/skirt only".

## Acceptance criteria

**Scenario 1: Slot selection over the defaults**
- Given the outfit-request panel grouped by region (Head / Upper body / Lower body / Feet)
- When I toggle slots
- Then the FR-51 defaults start selected, `lower_body` is locked-on (mandatory), and the request `slots` map overrides only what I changed (FR-51)

**Scenario 2: Category constraint**
- Given a multi-category slot (e.g. Lower body)
- When I tick a subset in its category checklist
- Then the slot value becomes `{ "categories": [...] }`; un-ticking the last reverts to "any" (never empty) (FR-52)

**Scenario 3: One-piece constraint auto-deselects base**
- Given I constrain Lower body to one-piece categories only (dress/jumpsuit)
- Then Base is auto-deselected with the note "A dress covers the base layer…" (FR-50.2)

**Scenario 4: Empty requested slot**
- Given a selected slot has no garments
- When I request
- Then the `409 empty_slots` message renders verbatim with the slot chip flagged "none in wardrobe" (FR-36)

## Technical approach
- Rebuild the request panel composing `{ slots }` (values `true`/`false`/`{categories}`) from `GET /api/taxonomy` `regions`; `lower_body` locked-on (contract §1.3a, §2.12)
- Results structure reads the slot-keyed combinations (one-piece once); scheme chip, per-slot tiles, explanation, echoes; `409` rendering. Count/pins/anchor are added by HUE-080/HUE-083
- Slot keys/labels per HANDOFF-05 (Base/Shirt/Mid-layer/Outer layer); no garment names

## Design references
- Wireframes: docs/04-wireframes/05-outfit-request.md (default, category-constrained, empty-slot states); HANDOFF-05-outfit-request.md

## Tests
- `Suggest.test.tsx` (§10.1): defaults + `lower_body` locked; toggles compose `slots`; category checklist → `{categories}`, last-untick reverts to "any"; one-piece auto-deselect note; `409 empty_slots` verbatim + per-chip flag
- Covered end-to-end by E2E journeys 3/4 (HUE-085)

## QA steps
- [ ] Open `/suggest` → expect default slots selected, Lower body locked-on
- [ ] Constrain Lower body to shorts/skirt → expect `{categories}` sent; untick all → reverts to "any"
- [ ] Constrain Lower body to dress only → expect Base auto-deselected with the note
- [ ] Request a slot with no garments → expect verbatim `409` message + "none in wardrobe"

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
