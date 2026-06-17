---
id: HUE-E04
title: Browse the wardrobe
type: epic
status: done
milestone: 8
batch: frontend
layer: frontend
depends_on: []
implements: [FR-35, NFR-6]
tests_required: false
estimate: 5
---

## Summary
Deliver brief success criterion 2: the owner browses the inventory, filtered by garment type and by colour family, with the two filters combinable, responsive at 500 garments.

## Scope
- **In scope:**
  - Inventory listing endpoint with combinable type AND family filters and pagination
  - The inventory browser screen: card grid, filter bar, empty/loading/error states
  - Thumbnail serving
- **Out of scope:**
  - Editing garments in place (brief: no field editing)
  - Suggestion (its own epic)

## Success criteria
All child tickets done; the owner can view all garments and filter by type and colour family, combined, with the server half of NFR-6 asserted by `make test-perf`; brief success criterion 2 is met.

## Children
- HUE-029 — Garment read endpoints and inventory filters
- HUE-035 — Inventory browser screen

## References
- docs/01-project-brief.md §11 (criterion 2)
- docs/02-requirements.md §6.6 (FR-35)
- docs/03-api-contract.md §2.6, §2.8
- docs/04-wireframes/03-inventory.md

## Notes
- 2026-06-15 — created
