---
id: HUE-063
title: matcher.ranking refinements — first-class neutral, diversity, top-N, seedable RNG
type: task
status: todo
milestone: 14
batch: matcher
layer: matcher
depends_on: [HUE-061, HUE-062, HUE-014]
implements: [FR-39, FR-40, FR-41, FR-42, FR-43, FR-48, NFR-5, NFR-10]
tests_required: true
estimate: 5
---

## Background
Refine `matcher.ranking` for F5/F7 over the rewritten slot model (HUE-061): make all-neutral
outfits **first-class** (not fallbacks), strengthen **diversity**, return the user-chosen
**count**, slim the fallback ladder, and make the variety randomness **seedable** so the
matcher stays deterministic under test (NFR-10). All on top of HUE-061's structural rewrite;
the HUE-059 snapshot ranking goldens are updated in this commit.

## Technical requirements
- `app/matcher/ranking.py`:
  - **First-class neutral-based**: an empty (all-neutral) scheme set scores `NEUTRAL_BASED_STRENGTH = 0.98`, ranking just below a perfect chromatic scheme and above weaker ones; `scheme = neutral-based`, `fallback = false` (FR-41)
  - **Echo bonus** credits all distinct chromatic echoes, including minor-adornment echoes (FR-41.2, FR-22)
  - **Diversity**: `WEIGHT_VARIETY = 15` applied greedily during selection, with **anchor-interleaved enumeration** so distinct anchor garments are reached before the count-independent `MAX_ANCHOR_CANDIDATES` cap (FR-41.3)
  - **Top-*N* selection**: return up to *N* (1–25) distinct combinations best-first, `rank` from 1; fewer when fewer exist; the cap does not scale with *N* (FR-39, FR-40, FR-48, NFR-5)
  - **Slimmed fallback ladder**: only when the main enumeration finds no FR-15 combination — retry neutral-only (`fallback = true`), else zero with the constraining slot named (FR-43)
  - **Seedable RNG (NFR-10)**: the shuffle/interleave draw from an **injected `random.Random`**; no global random state; the result object distinguishes first-class neutral-based from a neutral fallback
- Standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [ ] All-neutral outfits rank first-class at 0.98; the neutral-vs-fallback distinction is in the result object (FR-41/FR-43)
- [ ] Minor-adornment echoes credited; diversity raised with anchor-interleaved enumeration (FR-22, FR-41)
- [ ] Up to *N* distinct results (1–25), cap count-independent (FR-39, FR-40, FR-48, NFR-5)
- [ ] Injected RNG; no global state; two seeds → independent streams (NFR-10, FR-42)
- [ ] HUE-059 snapshot ranking/scores updated and committed (§4.10)
- [ ] Tests added/updated per §12.2 and passing in `make test`; matcher 100% gate holds (§12.3.3)
- [ ] `make test-perf` re-checked where applicable (full perf re-baseline is HUE-084)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_ranking.py` (§4.7) — first-class neutral boundary pairs; echo bonus incl. minor
adornments; raised variety + interleave reachability with a fixed seed; top-*N* at N=1 and 25;
slimmed fallback ladder; injected-RNG independence and no-global-state. Snapshot diff reviewed.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
