---
id: HUE-034
title: Confirm-and-correct screen
type: story
status: todo
milestone: 8
batch: frontend
layer: frontend
depends_on: [HUE-032, HUE-033]
implements: [FR-5, FR-27, FR-28, FR-29, FR-30, FR-31, FR-33]
tests_required: true
estimate: 5
---

## User story
As the owner
I want to confirm or correct the detected palette and tag the garment's type
so that the garment is saved with colours I trust and a type.

## Acceptance criteria

**Scenario 1: Confirm the proposal**
- Given a detection proposal with swatches, family names and proportions (FR-28)
- When I accept it unchanged, choose a type and save
- Then `POST /api/garments` is sent with the token, type and colours and the garment is saved (FR-30)

**Scenario 2: Correct the palette**
- Given the proposal is shown with the proportion editor
- When I adjust proportions, remove a colour, or add one manually by family (canonical HSL from `GET /api/taxonomy`)
- Then the live total updates and proportions are normalised to 100 on save (FR-29)

**Scenario 3: Type is mandatory**
- Given no type is selected
- When I view the save control
- Then save is disabled until a type is chosen from the segmented row of eight (FR-31, Milestone 4 decision)

**Scenario 4: Regeneration variant**
- Given I arrived via Regenerate from garment detail (FR-33)
- When I confirm
- Then `PUT /api/garments/{id}` is sent with the regeneration token

## Technical approach
- Confirm-and-correct screen at `/add/confirm`; proportion editor (numeric steppers + live total + stacked preview bar)
- `GET /api/detections/{token}/image` preview; `GET /api/taxonomy` for manual-add families; `POST /api/garments` / `PUT /api/garments/{id}` (contract §2.2, §2.4, §2.5, §2.10)
- Swatches render measured `hex` (FR-5); fallback warning banner (FR-27); warn before discarding edits on leave

## Design references
- Wireframe: docs/04-wireframes/02-confirm-and-correct.md (states: saving, save failure, fallback warning, sum≠100, manual-add open, regeneration variant)

## Tests
- `ConfirmCorrect.test.tsx` (§10.1): proportion editor steppers/live total/normalise-on-save (FR-29); colour removal; manual add applying canonical HSL; type picker save-disabled-until-chosen (FR-30/FR-31); fallback banner (FR-27)
- FR-5/FR-28/FR-33 via MSW; covered end-to-end by E2E journey 1 (HUE-040, §9)

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
