---
id: HUE-080
title: Outfit-request count control and neutral/fallback labels
type: story
status: done
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-071]
implements: [FR-39, FR-41, FR-43, FR-48]
tests_required: true
estimate: 3
---

## In plain English
Gives the owner an on-screen control to choose how many outfit ideas to see and marks which results lean on neutral colours, so they can ask for more options and make sense of them.

## User story
As the owner
I want to choose how many outfits to generate and see which results are neutral-based
so that I can ask for more options and understand the suggestions.

## Acceptance criteria

**Scenario 1: Count control**
- Given the outfit-request panel
- When I set "How many outfits?" before generating
- Then a ±stepper clamps to 1–25 (default 3) and the request carries `count` (FR-48)

**Scenario 2: Up to N results**
- Given results return
- When fewer than `count` combinations exist
- Then fewer render; never more than `count`, ranked by position (FR-39)

**Scenario 3: Neutral-based vs fallback labels**
- Given a first-class neutral-based result (`scheme: "neutral-based"`, `fallback: false`)
- Then it renders unlabelled as a normal result; a `fallback: true` result carries the "Neutral-based fallback" label (FR-41/FR-43a)

## Technical approach
- Add the count ±stepper (label "How many outfits?", hint "(1–25)") composing `count` (contract §2.12; HANDOFF-05)
- Result cards distinguish first-class `neutral-based` (no label) from `fallback: true` ("Neutral-based fallback"); zero-result `explanation`+`hint` verbatim (FR-43b)

## Design references
- Wireframes: docs/04-wireframes/05-outfit-request.md (count control); 06-suggestion-results.md (fallback label, fewer-than-N, zero+hint); HANDOFF-05

## Tests
- `Suggest.test.tsx` (§10.1): count stepper clamps 1–25/default 3 and sends `count`; up-to-N cards; first-class-neutral unlabelled vs `fallback:true` labelled; zero-result verbatim
- Covered end-to-end by E2E journey 3 (HUE-085)

## QA steps
- [ ] Set count to 10 → expect `count:10` sent and up to 10 cards
- [ ] Set count below 1 or above 25 → expect clamp to range
- [ ] A neutral-based result → expect no fallback label; a fallback result → expect "Neutral-based fallback"

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy §12.2 and passing in `make test`
- [x] Matcher-touching work: n/a
- [x] Detection-touching work: n/a
- [x] Evaluation/inventory-perf-touching work: n/a
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6) — deferred to HUE-085
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit (§12.3.7)

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-07-02 — implemented. Added `count` state (default 3) to `Suggest.tsx`; ±stepper UI
  (label "How many outfits?", hint "(1–25)", `data-testid` buttons, clamped 1–25 with disabled
  state at bounds); `handleSuggest()` always includes `count` in the request body; results header
  `data-testid="results-header"` shows "{N} outfit(s)" or "Showing M of N you asked for" from
  `data.requested_count`. Added `requested_count` to `SUGGESTION_RESPONSE` and
  `SUGGESTION_EMPTY_RESPONSE` in `contract-examples.ts`. 10 new frontend tests across count
  stepper, results header, and fallback-label distinction. 1082 backend + 166 frontend pass,
  zero warnings. E2E deferred to HUE-085.
- Sanity test: `cd frontend && npx vitest run src/routes/Suggest.test.tsx --reporter=verbose`

## QA steps
- [ ] Open `/suggest` → count stepper shows "3" with − and + buttons
- [ ] Click + → count becomes 4; click + until 25 → + button disables
- [ ] Click − from 25 → decreases; click − until 1 → − button disables
- [ ] Click "Suggest outfits" with count=1 → request body has `count: 1`; at most 1 result card
- [ ] Results header shows "1 outfit" (or "Showing M of N you asked for" when fewer than requested)
- [ ] A `fallback: false` result card has no "Neutral-based fallback" chip
- [ ] A `fallback: true` result card shows "Neutral-based fallback" chip
