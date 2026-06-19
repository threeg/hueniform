---
id: HUE-061
title: matcher.slots rewrite — regions, four-layer stack, one-piece, adornment tiers
type: task
status: todo
milestone: 14
batch: matcher
layer: matcher
depends_on: [HUE-060, HUE-013]
implements: [FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-22, FR-49, FR-50, FR-51, NFR-9]
tests_required: true
estimate: 8
---

## Background
The heart of E08: rewrite `matcher.slots` from the v0.1.0 fixed 1:1 type-to-slot model to the
v0.2.0 region/slot/category model (requirements §5; F4 spike). It adds **no new harmony
mathematics** — a statement adornment reuses the v0.1.0 echo-slot primitive and a minor
adornment the minor-colour primitive (architecture §2.2) — so the matcher stays pure and the
import contracts/allowlist are unchanged. To keep `make test` and the 100 % gate green, the
`EvaluationResult`/anchor changes are made **additive** where possible and the `ranking`/`explain`
call-sites are adapted to compile; their v0.2.0 *behaviour* is HUE-063/HUE-064. Every
behavioural shift is captured as a HUE-059 snapshot diff committed with this ticket.

## Technical requirements
- `app/matcher/slots.py` rewritten to:
  - Map each FR-16 category to exactly one slot; categories sharing a slot are **matcher-equivalent** (FR-16, FR-49.5)
  - The four-level upper-body stack `base → shirt → mid → outer`, outermost present layer dominant (`outer > mid > shirt > base`) (FR-18); renamed slot keys `mid`/`outer`
  - **One-piece** (`dress`/`jumpsuit`): lower-body anchor that also occupies `base`, never demoted to a covered layer, counted once when uncovered (FR-18, FR-19, FR-50.2)
  - Scheme-set assembly across the new anchors (dominant-layer + lower-body primaries + all anchors' secondaries) (FR-19)
  - Covered-layer constraint generalised across up to three covered layers (FR-20)
  - Two adornment tiers — **statement** (echo-constrained, can disqualify) and **minor** (never disqualifies); echoes of any chromatic anchor colour recorded, including minor-anchor/minor-adornment echoes (FR-21, FR-22)
  - Mutual-exclusion groups (lower-body exclusivity; one-piece spanning) and the mandatory lower-body floor with otherwise-optional slots (FR-50, FR-51)
- Standard library only (NFR-9); ranking/explain adapted only enough to keep the gate green

## Definition of done (acceptance criteria)
- [ ] Category→slot mapping and matcher-equivalence-within-a-slot enforced (FR-16, FR-49.5)
- [ ] Four-layer dominance, one-piece behaviour, covered-layer constraint ×4, and the two adornment tiers correct (FR-18–FR-22)
- [ ] Mutual-exclusion groups and the mandatory lower-body floor enforced (FR-50, FR-51)
- [ ] Standard library only; passes the §5.2 allowlist; import contracts unchanged
- [ ] HUE-059 snapshot updated for the intended changes and committed in this commit (§4.10)
- [ ] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher coverage gate (100% line+branch on app/matcher/) holds (§12.3.3)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_slots.py` rewritten per §4.6: category→slot mapping and equivalence; four-layer
dominance permutations; scheme-set assembly with one-piece counted once; covered-layer across
four layers; statement vs minor tiers and echo recording; mutual exclusion and the mandatory
floor. The HUE-059 snapshot diff is reviewed as part of the change.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
