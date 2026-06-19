---
id: HUE-074
title: Garment-detail category edit UI
type: story
status: todo
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-067, HUE-036]
implements: [FR-46]
tests_required: true
estimate: 2
---

## User story
As the owner
I want to change a saved garment's category directly from its detail page
so that I can re-tag a garment without re-running detection.

## Acceptance criteria

**Scenario 1: Edit category in place**
- Given a garment detail page
- When I change the category and confirm
- Then a `PATCH /api/garments/{id}` with `{ category }` is issued and the new category is shown; the palette and photo are unchanged (FR-46)

**Scenario 2: Palette stays regenerate-only**
- Given the detail page
- When I look for palette editing
- Then there is no direct palette edit — only Regenerate (FR-32/FR-33)

## Technical approach
- Add an inline category editor on garment detail issuing `PATCH /api/garments/{id}` (contract §2.10a); category options from `GET /api/taxonomy` `regions`
- Regenerate/delete unchanged; no palette edit path

## Design references
- Wireframe: docs/04-wireframes/04-garment-detail.md (category edit affordance)

## Tests
- `GarmentDetail.test.tsx` (§10.1): category edit issues `PATCH` with `{ category }` and reflects the new category; no palette-edit affordance; error states from MSW
- Covered end-to-end by E2E journey 2 (HUE-085)

## QA steps
- [ ] Open a garment → change its category → expect it updates in place, palette/photo unchanged
- [ ] Confirm there is no direct palette edit (only Regenerate)

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
