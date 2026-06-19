---
id: HUE-E09
title: Suggestion quality & count
type: epic
status: todo
milestone: 14
batch: matcher
layer: matcher
depends_on: []
implements: [FR-2, FR-39, FR-40, FR-41, FR-42, FR-43, FR-48, NFR-5, NFR-10]
tests_required: false
estimate: 8
---

## Summary
Deliver v0.2.0 features F5 (suggestion quality) and F7 (configurable count). The diagnostic
conclusions are already settled in requirements §9.1: add the **Cream** neutral family (FR-2)
for pale warm near-neutrals; make **all-neutral outfits first-class results** scored at
`NEUTRAL_BASED_STRENGTH` (FR-41/FR-43); strengthen **diversity** with a raised variety
penalty and anchor-interleaved enumeration (FR-41); make the variety randomness **seedable**
(NFR-10) so the matcher stays unit-testable; and let the user choose **how many** outfits to
generate (1–25, default 3 — FR-48/FR-39), with NFR-5 re-baselined at the maximum count. F7's
higher count is what makes the F5 diversity fix necessary, so they ship together.

## Scope
- **In scope:**
  - `matcher.taxonomy` — the Cream family (FR-2)
  - `matcher.ranking` — first-class neutral-based scoring, raised variety + anchor-interleave,
    top-*N* selection, the slimmed fallback ladder, and the injected/seedable RNG (NFR-10)
  - `matcher.explain` — the first-class-neutral vs neutral-fallback wording
  - The suggestion service + endpoint **count** parameter and the neutral/fallback response
  - The frontend count stepper and the neutral/fallback result labels
  - The NFR-5 perf re-baseline at count 25 / 500 garments
- **Out of scope (other epics):** the slot model and FR-52 (E08); pins/anchor (E06);
  inventory ordering (E10). No separate diagnostic spike — the decisions are settled (§9.1).

## Success criteria
All child tickets done; an all-neutral outfit surfaces as a normal ranked result; pale
cream/ecru garments classify as Cream; requesting 25 outfits returns up to 25 distinct,
genuinely varied combinations within NFR-5 at 500 garments (re-baselined in `test-perf`); the
matcher stays pure with a fixed seed giving deterministic output (NFR-10) and the 100 % gate
intact.

## Children
- HUE-062 — matcher.taxonomy: the Cream family
- HUE-063 — matcher.ranking refinements (first-class neutral, diversity, top-N, seedable RNG)
- HUE-064 — matcher.explain: neutral-based vs neutral-fallback wording
- HUE-078 — Suggestion service: count and refined ranking integration
- HUE-079 — POST /api/suggestions: count field and neutral/fallback response
- HUE-080 — Outfit-request count control and neutral/fallback labels
- HUE-084 — Performance re-baseline at count 25 and wardrobe_500 update

## References
- docs/02-requirements.md §2.1 (FR-2), §7 (FR-39–FR-43, FR-48), NFR-5, NFR-10
- docs/03-architecture.md §2.2, §4.3
- docs/03-api-contract.md §1.5, §2.2, §2.12
- docs/05-test-strategy.md §4.1, §4.3, §4.7, §4.10, §7.4, §8.1, §8.2
- docs/spikes/2026-06-18-f4-category-slot-model.md §4 (decisions 4–6)
- docs/04-wireframes/06-suggestion-results.md

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
