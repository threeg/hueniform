---
id: HUE-035
title: Inventory browser screen
type: story
status: done
milestone: 8
batch: frontend
layer: frontend
depends_on: [HUE-032]
implements: [FR-35, NFR-6]
tests_required: true
estimate: 3
---

## In plain English
The main screen that shows your whole wardrobe as a grid of clothing items, letting you narrow it down by type and colour so you can find a particular garment quickly.

## User story
As the owner
I want to browse my wardrobe and filter it by type and colour
so that I can find garments quickly.

## Acceptance criteria

**Scenario 1: Browse all garments**
- Given I open Wardrobe (`/`)
- When the inventory loads
- Then a card grid of thumbnails, palette strips and type labels is shown (FR-35)

**Scenario 2: Combine filters**
- Given the filter bar above the grid
- When I select a type and a colour family
- Then `GET /api/garments` is called with both parameters (AND) and the grid updates (FR-35)

**Scenario 3: Empty states**
- Given an empty wardrobe or a filter matching nothing
- When the result is empty
- Then the appropriate empty state is shown

## Technical approach
- Inventory screen at `/`; card grid + filter bar above (Milestone 4 decision)
- `GET /api/garments` with combinable `type`+`family`; family dropdown with canonical swatches from `GET /api/taxonomy`
- TanStack Query caching so filter changes stay responsive (NFR-6 browser half — manual check at 500)

## Design references
- Wireframe: docs/04-wireframes/03-inventory.md (states: empty wardrobe, empty filter result, skeleton grid, load failure, filtered)

## Tests
- `Inventory.test.tsx` (§10.1): filter bar populated from `GET /api/taxonomy`; combined filters issue the right query parameters; empty-result state (FR-35)
- Server half of NFR-6 asserted in HUE-039; covered by E2E journey 1's filter step (HUE-040, §9)

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher-touching work: 100% line+branch on app/matcher/ holds (§12.3.3) — not applicable
- [ ] Detection-touching work: `make test-model` passes (§12.3.4) — not applicable
- [ ] Evaluation/inventory-perf-touching work: `make test-perf` passes (§12.3.5) — not applicable
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6) — deferred to HUE-040
- [x] Ticket status + notes updated in the same commit (§12.3.7)

## Notes
- 2026-06-15 — created
- 2026-06-17 — implemented. `Wardrobe.tsx` replaces the placeholder: filter bar with type
  + family dropdowns (family options sourced from `GET /api/taxonomy`), filter state synced
  to URL search params, card grid using `GarmentCard`, three empty/error states, result count.
  Family swatch shown next to the select for the currently selected family (native `<select>`
  cannot render coloured swatches per option; per-option swatches would require a custom
  combobox, deferred). 92/92 tests pass, zero warnings.
  Sanity: `cd frontend && npm run test -- src/routes/Inventory.test.tsx`
