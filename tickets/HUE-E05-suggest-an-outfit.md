---
id: HUE-E05
title: Suggest an outfit
type: epic
status: done
milestone: 8
batch: services
layer: services
depends_on: []
implements: [FR-17, FR-36, FR-37, FR-38, FR-39, FR-40, FR-41, FR-42, FR-43, NFR-5]
tests_required: false
estimate: 8
---

## Summary
Deliver brief success criterion 3: the owner requests an outfit choosing which optional slots to include and receives up to three ranked, harmonious combinations, each with a plain-language explanation generated from the actual evaluation, with a neutral-based fallback ladder.

## Scope
- **In scope:**
  - The suggestion service: anchor enumeration, capping, the matcher-driven evaluation and ranking, the fallback ladder
  - The suggestions endpoint and all its response shapes (found / zero / fail-fast)
  - The combined outfit-request + results screen
- **Out of scope:**
  - Weather, wear-tracking and any roadmap behaviour (brief out of scope)
  - Persisting suggestions (computed, not stored)

## Success criteria
All child tickets done; the owner can request an outfit with chosen optional slots and receive at least one harmonious combination with an explanation, within NFR-5; brief success criterion 3 is met and the E2E 'request an outfit' journey passes.

## Children
- HUE-024 — Suggestion service: enumeration, ranking and the fallback ladder
- HUE-031 — Suggestions endpoint
- HUE-037 — Outfit request and suggestion results screen

## References
- docs/01-project-brief.md §11 (criterion 3)
- docs/02-requirements.md §5, §7
- docs/03-api-contract.md §2.12
- docs/04-wireframes/05-outfit-request.md, 06-suggestion-results.md

## Notes
- 2026-06-15 — created
