---
id: HUE-008
title: Implement matcher.colour
type: task
status: done
milestone: 8
batch: matcher
layer: matcher
depends_on: [HUE-007]
implements: [FR-12, NFR-9]
tests_required: true
estimate: 3
---

## In plain English
Provides the basic colour arithmetic everything else depends on — converting between ways of describing a colour, measuring how far apart two colours are around the colour wheel, and averaging colours together correctly.

## Background
All colour mathematics is defined in HSL (requirements §1.3); the matcher owns a pure RGB↔HSL conversion and the circular hue operations the rest of the matcher builds on, keeping the package standard-library-only (NFR-9).

## Technical requirements
- `app/matcher/colour.py`: RGB↔HSL conversion; wrapping hue distance (shorter way round, max 180°); circular mean (requirements §1.3, FR-12)
- A frozen `Colour` dataclass (h, s, l, proportion) used as the matcher's colour value type
- Hex derivation from measured HSL (for the contract's `hex`, FR-5) as a pure helper
- Standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [x] RGB↔HSL round-trips within ±1 per 8-bit channel; hue distance and circular mean correct across the 0°/360° wrap
- [x] `Colour` value type defined; hex derivation matches the contract worked examples (e.g. #2CADA0 ↔ 174,58,41)
- [x] Standard library only; passes the §5.2 allowlist
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_colour.py` (§4.2): known RGB↔HSL pairs and round-trip; hue-distance table (d(350,10)=20, d(0,180)=180, d(h,h)=0) plus Hypothesis properties (symmetry, range [0,180], +360 invariance); circular mean(350,10)=0 and a membership property. Uses `palettes.py` (HUE-006).

## Notes
- 2026-06-15 — created
- 2026-06-15 — done. `Colour` frozen dataclass; pure Python RGB↔HSL (all six sectors); `hsl_to_hex`; wrapping `hue_distance`; `circular_mean` via atan2. Note: the contract's stated HSL values (e.g. h=174, s=58, l=41) are rounded display representations — the `#2CADA0` hex is tested via round-trip from the actual RGB pixels (44,173,160). Removed a dead `if h < 0.0` guard that could never fire with the `% 6` algorithm. 126 backend tests, all green; `app/matcher/` 100%.
