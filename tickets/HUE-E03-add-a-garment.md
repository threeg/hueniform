---
id: HUE-E03
title: Add a garment
type: epic
status: done
milestone: 8
batch: services
layer: services
depends_on: []
implements: [FR-23, FR-24, FR-25, FR-26, FR-27, FR-28, FR-29, FR-30, FR-31, FR-32, FR-33, FR-34]
tests_required: false
estimate: 8
---

## In plain English
Everything needed to add a piece of clothing to the wardrobe: upload its photo, have the app work out its colours, let the owner confirm or correct them and tag the type, then save it, with the option to redo the colours or remove it later.

## Summary
Deliver brief success criterion 1: the owner uploads a garment photo, the app proposes the colours with proportions, the owner confirms or corrects them and saves the garment with a type tag, and can later regenerate or delete it. Spans detection, storage, the relevant services, endpoints and screens.

## Scope
- **In scope:**
  - Photo upload, validation and storage
  - Automatic colour detection with the segmentation fallback
  - The confirm-and-correct flow (proportions, manual add/remove, type tag)
  - Save as one transaction; thumbnail generation
  - Regenerate (token-gated, in place) and delete
- **Out of scope:**
  - Automatic garment-type recognition (brief out of scope)
  - Outfit suggestion (its own epic)
  - Inventory browsing (its own epic)

## Success criteria
All child tickets done; the owner can upload a photo, see a proposed palette with proportions, confirm or correct it, choose a type and save; regenerate and delete work; brief success criterion 1 is met and the E2E 'add a garment' journey passes.

## Children
- HUE-018 — Detection pure helpers
- HUE-019 — Detection pipeline orchestration
- HUE-020 — Real-model detection integration and setup model fetch
- HUE-021 — Detection service and staging store orchestration
- HUE-022 — Garment service: confirm-save and delete
- HUE-023 — Regeneration service
- HUE-026 — Taxonomy endpoint
- HUE-027 — Detections endpoints
- HUE-028 — Garment create endpoint
- HUE-030 — Garment regenerate, replace and delete endpoints
- HUE-033 — Upload and detect screen
- HUE-034 — Confirm-and-correct screen
- HUE-036 — Garment detail screen

## References
- docs/01-project-brief.md §11 (criterion 1)
- docs/02-requirements.md §6.1–§6.5
- docs/03-api-contract.md §2.3–§2.5, §2.9–§2.11
- docs/04-wireframes/01-upload-detect.md, 02-confirm-and-correct.md, 04-garment-detail.md

## Notes
- 2026-06-15 — created
