---
id: HUE-009
title: Implement matcher.taxonomy
type: task
status: done
milestone: 8
batch: matcher
layer: matcher
depends_on: [HUE-008, HUE-006]
implements: [FR-1, FR-2, FR-3, FR-4, FR-5, NFR-9]
tests_required: true
estimate: 5
---

## In plain English
Decides, for any given colour, which single named colour family it belongs to — sorting out the neutrals like black, white and grey first, then the brighter colours around the wheel — in a consistent way that the rest of the app relies on.

## Background
The taxonomy maps any HSL value to exactly one family, deterministically (FR-1): ordered neutral rules first, then the twelve chromatic 30° arcs with half-open boundaries (FR-2, FR-4). This is the classification every other layer relies on and the most boundary-sensitive module.

## Technical requirements
- `app/matcher/taxonomy.py`: the FR-2 neutral rules evaluated first in table order (Black, White, Grey, Navy, Denim, Brown, Beige/Tan), then chromatic arcs; first match wins
- Half-open arc boundaries (FR-4): a hue equal to a boundary belongs to the arc starting at it (H=15° is Orange)
- Neutrals carry no hue for harmony (FR-3): expose the neutral/chromatic distinction
- Canonical HSL per family (for `GET /api/taxonomy` and manual colour adds); each canonical classifies into its own family
- Thresholds come from `constants.py`; standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [x] Classification is total and deterministic over valid HSL; exactly one of the nineteen families returned (FR-1)
- [x] Neutral ordering (FR-2) and half-open arcs (FR-4) correct at every boundary; neutral/chromatic flag exposed (FR-3)
- [x] Each family's canonical value classifies into its own family
- [x] Standard library only; passes the §5.2 allowlist
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_taxonomy.py` (§4.3): the full boundary-value tables (every comparison at the edge ±0.1) from `palettes.py` — Black/White/Grey/Navy↔Denim ordering, Denim S edge, Brown/Beige gap, all twelve FR-4 arc boundaries; ordered-evaluation rows (FR-2); canonical-value self-classification; Hypothesis totality/determinism/neutral-xor-chromatic/arc-membership (FR-1).

## Notes
- 2026-06-15 — created
- 2026-06-15 — done. `FAMILIES` registry (7 neutrals + 12 chromatics); `classify()` evaluates the 7 FR-2 neutral rules first, then maps h to a chromatic arc via a single index expression `_CHROMATIC_NAMES[int((h-345)%360//30)%12]` — no fallback line, always covered. `is_neutral()` and `canonical_hsl()` expose the neutral/chromatic distinction and contract canonical values. 272 backend tests, all green; `app/matcher/` 100% line+branch.
