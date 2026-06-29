---
id: HUE-078
title: Suggestion service — count and refined ranking integration
type: task
status: todo
milestone: 14
batch: services
layer: services
depends_on: [HUE-068, HUE-063]
implements: [FR-39, FR-41, FR-43, FR-48]
tests_required: true
estimate: 3
---

## In plain English
Lets the owner decide how many outfit ideas to receive at once, and makes clear which ideas are built around neutral colours, so the suggestions are easier to understand.

## Background
F7/F5: thread the user-chosen **count** *N* (1–25, default 3) through the suggestion service and
surface the refined ranking (first-class neutral-based vs neutral fallback) from HUE-063. Builds
on the slot-selection rewrite (HUE-068); the cap stays count-independent (NFR-5).

## Technical requirements
- `app/services/suggestion_service.py` — accept `count` *N* (default `COUNT_DEFAULT`); return up to *N* distinct combinations best-first (FR-39, FR-48); reject out-of-range at the API boundary
- Surface the HUE-063 result distinction: first-class `neutral-based` (`fallback=false`) vs the neutral-fallback retry (`fallback=true`) and the zero-result with the constraining slot (FR-41, FR-43)
- Selecting *N* from the capped pool only; the cap does not scale with *N* (NFR-5)

## Definition of done (acceptance criteria)
- [ ] Up to *N* (1–25) distinct combinations returned; default 3; fewer when fewer exist (FR-39, FR-48)
- [ ] First-class neutral-based vs neutral-fallback vs zero-result surfaced correctly (FR-41, FR-43)
- [ ] Cap count-independent (NFR-5; full perf re-baseline is HUE-084)
- [ ] Tests added/updated per §12.2 and passing in `make test`
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`services/test_suggestion_service.py` (§7.4): count at N=1 and 25 and default; fewer-than-N;
first-class-neutral vs fallback vs zero-result distinction over engineered wardrobes with a
seeded RNG; the §4.9.4 oracle. Perf is HUE-084.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
