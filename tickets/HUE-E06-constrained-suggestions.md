---
id: HUE-E06
title: Constrained suggestions
type: epic
status: todo
milestone: 14
batch: services
layer: services
depends_on: []
implements: [FR-44, FR-45, NFR-7]
tests_required: false
estimate: 5
---

## Summary
Deliver v0.2.0 features F1 (build around a chosen garment) and F2 (build around a colour
scheme). An outfit request may **pin a specific garment** to its slot (FR-44) and/or **anchor
to a colour** — a target family and/or a named FR-13 scheme (FR-45); the suggester returns
only harmonious combinations honouring the constraints and fails fast with a clear message
when none exist. These build on the E08 slot model and per-category constraint, with which
pins and anchors compose, and on the E09 ranking changes.

## Scope
- **In scope:**
  - Suggestion service: pin enforcement and colour/scheme anchor pruning (FR-44, FR-45)
  - The suggestions endpoint `pins` and `anchor` request fields and their `422` validation
  - The outfit-request pin picker (with "Suggest outfits around this") and anchor controls
  - The reworked-journey end-to-end smoke suite (capstone for the v0.2.0 user flows)
- **Out of scope:** the per-category slot constraint FR-52 (delivered in E08, with which a pin
  composes); the slot model itself (E08); count and ranking quality (E09).

## Success criteria
All child tickets done; the owner can pin a garment and/or anchor to a colour family or named
scheme and receive only combinations that honour every constraint (or a clear zero-result
explanation); pins and anchors compose with the FR-51 selection and the FR-52 constraint; the
reworked e2e journeys pass on Chromium and Firefox (NFR-7).

## Children
- HUE-081 — Suggestion service: pins and colour/scheme anchor
- HUE-082 — POST /api/suggestions: pins and anchor request and validation
- HUE-083 — Outfit-request pin picker and anchor controls
- HUE-085 — End-to-end smoke suite update (v0.2.0 journeys)

## References
- docs/02-requirements.md §6.7 (FR-36, FR-44, FR-45)
- docs/03-architecture.md §4.3 (steps 1–3, 6)
- docs/03-api-contract.md §2.12 (`pins`, `anchor`, the `422` cases)
- docs/05-test-strategy.md §4.7, §7.4, §9
- docs/04-wireframes/05-outfit-request.md, HANDOFF-05-outfit-request.md

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
