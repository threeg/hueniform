---
id: HUE-070
title: Confirm-and-correct category picker
type: story
status: done
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-067, HUE-034]
implements: [FR-30, FR-31]
tests_required: true
estimate: 2
---

## In plain English
Lets the owner pick what kind of clothing an item is when adding it, choosing from a tidy list grouped by where it is worn on the body, so each item is labelled correctly.

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
- [ ] Run `make dev`, upload a garment → on the confirm screen, the category picker shows four region headings (Head, Upper body, Lower body, Feet) each with the correct chip buttons beneath
- [ ] Leave category unset → Save button is disabled; click any category chip → Save button becomes enabled
- [ ] Click "Trousers", then "T-shirt" — only the last clicked chip shows as selected (aria-pressed=true)

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
- 2026-06-24 — implemented. `AddConfirm.tsx` picker rewritten: removed static `GARMENT_TYPES` array; replaced with `taxonomy?.regions?.map(...)` grouping each region under an `<h3>` heading; `REGION_LABELS` maps region keys to "Head / Upper body / Lower body / Feet"; section `aria-label` changed from "Garment type" to "Garment category". CSS updated: `.typePicker` is now a column flex container, new `.regionGroup` (flex-wrap) and `.regionHeading` (small-caps label) classes added. `ConfirmCorrect.test.tsx` updated: all category-button lookups changed from synchronous `getByRole` to async `findByRole`; count test uses `findAllByRole` to wait for taxonomy load; new region-heading test added. 1043 backend + 135 frontend pass, zero warnings.
- Sanity test: `cd frontend && npx vitest run src/routes/ConfirmCorrect.test.tsx`
