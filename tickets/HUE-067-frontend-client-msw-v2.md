---
id: HUE-067
title: Frontend API client and MSW handlers — v0.2.0 contract
type: task
status: done
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-032]
implements: [FR-16]
tests_required: true
estimate: 3
---

## In plain English
Brings the app's screens up to date with the new clothing kinds and outfit-request options so that each screen can be built and tested against the agreed behaviour before the visible features are added.

## Background
The frontend is built against the contract independently of the backend (CONVENTIONS §4.5).
Before the v0.2.0 screen tickets, the typed API client and the MSW handlers/contract-examples
must mirror the rewritten contract so every screen test runs offline against contract-shaped
responses. This is the frontend foundation the E06–E10 screen tickets depend on.

## Technical requirements
- Typed API client + `frontend/src/test/contract-examples.ts` + `handlers.ts` updated for:
  - `GET /api/taxonomy` `regions` array and `Cream` family (§2.2)
  - `GarmentSummary`/`Garment` field rename `type` → `category` (§1.2)
  - `GET /api/garments` `order` param and `category` filter (§2.6)
  - `PATCH /api/garments/{id}` `{ category }` (§2.10a)
  - `POST /api/suggestions` request `{ slots, pins, anchor, count }` (slots value `true`/`false`/`{categories}`) and the combination/`409 empty_slots`/`422 invalid_request` responses, including first-class `neutral-based` vs `fallback: true` (§2.12)
- Handlers remain an executable mirror of `docs/03-api-contract.md`; fully offline

## Definition of done (acceptance criteria)
- [ ] Client types and MSW handlers match the v0.2.0 contract examples exactly
- [ ] `type` → `category` propagated through client/types/handlers
- [ ] Suggestion request/response and taxonomy `regions` shapes available to screen tests
- [ ] Tests added/updated per §12.2 and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
Component tests across screens consume these handlers (§10.1, §11.4); a handler-shape sanity
test asserts the documented example bodies parse into the typed client. No backend dependency.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-06-19 — implemented. `types.ts`: `GarmentSummary`/`Garment`/`GarmentCreateRequest`/`GarmentUpdateRequest` rename `type`→`category`; `InventoryParams` adds `category`/`order`; `PatchGarmentRequest` added; `TaxonomySlot`/`TaxonomyRegion` added; `TaxonomyResponse` gains `regions?`; `SuggestionRequest` updated to v0.2.0 `slots/pins/anchor/count`; `SuggestionResponse` gains `requested_count?`. `endpoints.ts`: `getGarments` sends `category=`; `patchGarment` added. `contract-examples.ts`: Cream family added (20 total), full `regions` array (4 regions/17 slots), `GARMENT_DETAIL.category='jumper'`, `SUGGESTION_RESPONSE` slots updated to v0.2.0 (`base`/`lower_body`). `handlers.ts`: PATCH handler added. Components updated: `GarmentCard`, `GarmentDetail`, `Wardrobe`, `AddConfirm`, `Suggest` (`include`→`slots`). `typeLabel.ts`: 40 v0.2.0 categories with title-case fallback. All tests updated; 1033 backend + 134 frontend pass, zero warnings.
- Sanity test: `cd frontend && npx vitest run 2>&1 | tail -5`

## QA steps
- `make run` → open browser → add a garment → confirm screen shows all 40 category buttons
- Wardrobe filter dropdown shows v0.2.0 categories (T-shirt, Jumper, Trousers, etc.)
- Garment detail heading shows 'Jumper' for a garment with category='jumper'
