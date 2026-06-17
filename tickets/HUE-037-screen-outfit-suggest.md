---
id: HUE-037
title: Outfit request and suggestion results screen
type: story
status: done
milestone: 8
batch: frontend
layer: frontend
depends_on: [HUE-032]
implements: [FR-17, FR-36, FR-37, FR-38, FR-39, FR-40, FR-41, FR-42, FR-43]
tests_required: true
estimate: 5
---

## User story
As the owner
I want to request an outfit with chosen optional slots and see ranked suggestions
so that I get harmonious combinations with an explanation of why they work.

## Acceptance criteria

**Scenario 1: Request and see results**
- Given the Suggest-outfit page with the slot panel on top
- When I choose optional slots and request
- Then up to three result cards render best-first with a scheme chip, per-slot tiles and a non-empty explanation (FR-37/FR-39)

**Scenario 2: Fallback and fewer-than-three**
- Given only neutral-based fallbacks exist
- When results return with `fallback: true`
- Then those cards carry a 'Neutral-based fallback' label (FR-43a); fewer than three render when fewer exist (FR-39)

**Scenario 3: Zero results**
- Given no combination is possible
- When the response is empty
- Then the `explanation` and `hint` are rendered verbatim, naming the constraining slot (FR-43b)

**Scenario 4: Empty requested slot**
- Given a requested slot has no garments
- When I request
- Then the `409 empty_slots` message renders on the request panel (FR-36)

## Technical approach
- One page at `/suggest` (Milestone 4 decision): slot panel persists above results
- `POST /api/suggestions` composing the `include` body; required slots always included (FR-17); rank by card position, no score numbers
- Scheme chip; echo line from the `echoes` array; fallback label; zero-result `explanation`+`hint`; `409` rendering (contract §2.12)

## Design references
- Wireframes: docs/04-wireframes/05-outfit-request.md (searching, `409 empty_slots`) and 06-suggestion-results.md (zero+hint, fallback-labelled, fewer-than-three)

## Tests
- `OutfitSuggest.test.tsx` (§10.1): slot panel composes `include`; result cards (rank, scheme chip, echo line, fallback label); zero-result `explanation`+`hint` verbatim (FR-43b); `409 empty_slots` rendering (FR-36)
- FR-37/FR-38/FR-39/FR-40/FR-41/FR-42 surfaces via MSW; covered end-to-end by E2E journeys 2 and 3 (HUE-040, §9)

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
- 2026-06-17 — implemented. `Suggest.tsx` replaces placeholder: request panel with required
  slots as locked chips (FR-17), four optional toggle chips (FR-36), all four keys sent
  explicitly in the include body; result cards with rank, scheme chip, slot tiles (wearing
  order, thumbnail + palette strip, links to detail), verbatim explanation (FR-38), echo lines
  with family swatches; fallback label (FR-43a); zero-results explanation+hint verbatim (FR-43b);
  409 empty_slots banner + per-chip "none in wardrobe" marker (FR-36); "Suggest again" (FR-42).
  21 new tests; 132/132 pass, zero warnings.
  Sanity: `cd frontend && npm run test -- src/routes/OutfitSuggest.test.tsx`
