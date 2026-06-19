---
id: HUE-070
title: Confirm-and-correct category picker
type: story
status: todo
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-067, HUE-034]
implements: [FR-30, FR-31]
tests_required: true
estimate: 2
---

## User story
As the owner
I want to assign one of the new FR-16 categories when confirming a garment
so that the garment is tagged with the right category for grouping and suggestions.

## Acceptance criteria

**Scenario 1: Region-grouped category picker**
- Given the confirm-and-correct screen for a detected garment
- When I open the category picker
- Then the categories are the FR-16 set, grouped by region (from `GET /api/taxonomy`), with the renamed vocabulary (no `jersey`; `mid`/`outer` layers)

**Scenario 2: Save gated on category**
- Given a confirmed palette
- When no category is chosen
- Then save stays disabled until exactly one category is selected (FR-30/FR-31)

## Technical approach
- Update the confirm-and-correct screen's picker to read `regions`/`categories` from `GET /api/taxonomy` (contract §2.2); the request field is `category` (contract §2.5)
- No change to the proportion editor (FR-29)

## Design references
- Wireframe: docs/04-wireframes/02-confirm-and-correct.md (category picker state)

## Tests
- `AddConfirm.test.tsx` (§10.1): category picker populated from taxonomy `regions`; save-disabled-until-chosen (FR-30/FR-31); `category` sent in the create body
- Covered end-to-end by E2E journey 1 (HUE-085)

## QA steps
- [ ] Upload a garment → open the category picker → expect FR-16 categories grouped by region
- [ ] Leave category unset → expect Save disabled; choose one → expect Save enabled

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
