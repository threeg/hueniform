---
id: HUE-E07
title: Edit a garment's category
type: epic
status: todo
milestone: 14
batch: services
layer: services
depends_on: []
implements: [FR-32, FR-46]
tests_required: false
estimate: 3
---

## Summary
Deliver v0.2.0 feature F3: allow the **category** of a saved garment to be edited directly,
without re-running detection and without the confirm-and-correct flow (FR-46). This narrows
the FR-32 immutability rule so the type field is editable; the palette stays regenerate-only
(FR-33). Small and additive — a single editable field whose change flows straight into
suggestion eligibility. It needs the new FR-16 category allowlist (E08) to validate against,
but is otherwise independent of the matcher rewrite.

## Scope
- **In scope:**
  - Garment-service direct category edit (validate against the FR-16 allowlist; touch nothing
    else — same id, image, palette, `regenerated_at`)
  - `PATCH /api/garments/{id}` (FR-46) and its `404`/`422` cases
  - The garment-detail category-edit UI
- **Out of scope:** palette editing (regenerate-only, FR-33); brand/season/notes/availability
  and multi-photo (deferred, brief F3).

## Success criteria
All child tickets done; the owner can change a saved garment's category from garment detail
without re-detection; the garment keeps its id, image and palette and immediately groups and
suggests under the new category; the palette remains changeable only via regenerate.

## Children
- HUE-072 — Garment service: direct category edit
- HUE-073 — PATCH /api/garments/{id} — edit category
- HUE-074 — Garment-detail category edit UI

## References
- docs/02-requirements.md §6.5 (FR-32 amended, FR-46)
- docs/03-architecture.md §3.1, §4.2
- docs/03-api-contract.md §2.10a
- docs/05-test-strategy.md §7.2, §10.1
- docs/04-wireframes/04-garment-detail.md

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
