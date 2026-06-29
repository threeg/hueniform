---
id: HUE-059
title: Matcher golden-file snapshot baseline
type: task
status: done
milestone: 14
batch: matcher
layer: matcher
depends_on: [HUE-015]
implements: []
tests_required: true
estimate: 3
---

## In plain English
Records exactly what outfit and colour suggestions the app produces today, before a big overhaul begins, so that any later change in its recommendations is clearly visible and intentional rather than an accidental slip.

## Background
The E08 slot-model rewrite changes the rules of the 100 %-covered, deterministic matcher
(layer stack 3→4, one-piece, adornment tiers, Cream, all-neutral/diversity ranking). Per
`docs/meta/method-improvements.md` #2, F4 spike §6 and architecture §2.2, a **golden-file
snapshot of the *current* matcher output must be captured and committed before any slot-model
code changes**, so every behavioural change later surfaces as an explicit, reviewable diff
rather than a silent regression. This is the **first E08 ticket**, ahead of HUE-060/HUE-061.
It captures behaviour only; it changes no production code.

## Technical requirements
- `backend/tests/matcher/test_snapshot.py` and `backend/tests/matcher/snapshots/` (test strategy §4.10), with three golden files:
  1. **Classifications** — the §11.3 palette tables plus each family's canonical HSL → family name
  2. **Ranking** — the engineered scenario wardrobes (§11.2), each evaluated with a **fixed seed** (the existing injected `random.Random`) → returned combinations' ordering, scheme, and numeric score components
  3. **Explanations** — each of those combinations → its rendered `explain` text
- Comparison is **exact**; float scores serialised at a **fixed precision** (rounded decimal strings) so the seed makes it reproducible and platform-float noise cannot flake it
- A documented regeneration path (a `--snapshot-update` flag / small `make` target); the goldens are read-only in the test otherwise
- Captured against the **current (pre-rewrite) matcher** — no changes to `app/matcher/`

## Definition of done (acceptance criteria)
- [x] Three golden files committed, generated from current matcher output, exact-compared with fixed-precision scores (§4.10)
- [x] Regeneration path documented; goldens otherwise read-only
- [x] `test_snapshot.py` is in the default gate and green; no `app/matcher/` production change
- [x] Tests added per test strategy §12.2 and passing in `make test`
- [x] Matcher coverage gate (100% line+branch on app/matcher/) still holds (§12.3.3)
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_snapshot.py` (§4.10) compares live matcher output against the committed goldens;
it must pass on the unchanged matcher. The snapshot becomes the regression oracle for the E08
rewrite (HUE-060+): each intended behavioural change re-runs `--snapshot-update` and commits
the changed goldens alongside the code.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-06-19 — implemented: `test_snapshot.py` + `snapshots/` created; three golden files generated (classifications: 36 HSL inputs → family names; ranking: 5 scenario wardrobes × seeded rank(); explanations: rendered text for each result). `--snapshot-update` pytest option registered in top-level `conftest.py`; `make snapshot-update` Makefile target added. Milestone 14 marked in-progress. 889 backend tests passed (3 new), matcher 100% coverage gate held, 134 frontend tests passed.
