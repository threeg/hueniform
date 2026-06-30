---
id: HUE-074
title: Garment-detail category edit UI
type: story
status: done
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-067, HUE-036]
implements: [FR-46]
tests_required: true
estimate: 2
---

## In plain English
Lets the owner correct what kind of clothing an item is straight from the item's own page, without re-running the photo analysis, while its photo and colours stay the same.

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
- [x] Open a garment → click "Edit" beside the category heading → region-grouped picker opens with current category pre-selected → select a different category → click Save → heading updates in place; palette and photo unchanged
- [x] Click Edit → click Cancel → picker closes, heading unchanged
- [x] Confirm there is no direct palette edit (only Regenerate)

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
- 2026-06-30 — implemented. Added inline category editor to `GarmentDetail.tsx`: "Edit" button
  beside the category heading opens a region-grouped picker (taxonomy from `useTaxonomy()`);
  current category pre-selected (`aria-pressed`); Save sends `PATCH /api/garments/{id}` via new
  `usePatchGarment` hook (added to `queries.ts`, `patchGarment` already in `endpoints.ts`);
  on success cache is updated (`setQueryData`) and picker closes; Cancel closes without network
  call. Updated action hint caption to match wireframe §04 (category editable / colours
  regenerate-only). 7 new tests in `GarmentDetail.test.tsx`; 1059 backend + 156 frontend pass,
  zero warnings.
- Sanity test: `cd frontend && npx vitest run src/routes/GarmentDetail.test.tsx -t "category edit" 2>&1 | tail -5`
