---
id: HUE-067
title: Frontend API client and MSW handlers — v0.2.0 contract
type: task
status: todo
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-032]
implements: [FR-16]
tests_required: true
estimate: 3
---

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
