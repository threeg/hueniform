---
id: HUE-036
title: Garment detail screen
type: story
status: todo
milestone: 8
batch: frontend
layer: frontend
depends_on: [HUE-032, HUE-034, HUE-035]
implements: [FR-32, FR-33, FR-34]
tests_required: true
estimate: 3
---

## User story
As the owner
I want to view a garment and regenerate or delete it
so that I can fix a bad detection or remove a garment I no longer own.

## Acceptance criteria

**Scenario 1: View a garment**
- Given I click a card in the inventory
- When the detail screen opens at `/garments/{id}`
- Then the full-size image and palette are shown with a '← Wardrobe' link preserving filters

**Scenario 2: Regenerate**
- Given the detail screen
- When I choose Regenerate
- Then `POST /api/garments/{id}/regenerate` runs and I enter confirm-and-correct with the regeneration token (FR-33)

**Scenario 3: Delete with confirmation**
- Given the detail screen
- When I choose Delete and confirm in the dialogue
- Then `DELETE /api/garments/{id}` is issued and I return to the inventory (FR-34)

**Scenario 4: No field editing**
- Given a saved garment
- When I view it
- Then there is no field-edit control — only Regenerate and Delete (FR-32)

## Technical approach
- Detail screen at `/garments/{id}`; `GET /api/garments/{id}`, `POST …/regenerate`, `DELETE …` (contract §2.7, §2.9, §2.11)
- Delete confirmation dialogue before issuing `DELETE` (FR-34 UI half); no editable fields (FR-32)

## Design references
- Wireframe: docs/04-wireframes/04-garment-detail.md (states: regenerate pending, delete confirmation dialogue)

## Tests
- `GarmentDetail.test.tsx` (§10.1): regenerate enters confirm-and-correct with the token; delete confirmation step precedes `DELETE` (FR-34); no edit control present (FR-32/FR-33)

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher-touching work: 100% line+branch on app/matcher/ holds (§12.3.3)
- [ ] Detection-touching work: `make test-model` passes (§12.3.4)
- [ ] Evaluation/inventory-perf-touching work: `make test-perf` passes (§12.3.5)
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6)
- [ ] Ticket status + notes updated in the same commit (§12.3.7)

## Notes
- 2026-06-15 — created
