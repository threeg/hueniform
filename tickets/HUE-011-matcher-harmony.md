---
id: HUE-011
title: Implement matcher.harmony
type: task
status: done
milestone: 8
batch: matcher
layer: matcher
depends_on: [HUE-009, HUE-008]
implements: [FR-12, FR-13, FR-14, FR-15, NFR-9]
tests_required: true
estimate: 5
---

## In plain English
Judges whether a set of colours go well together and, if so, names the kind of pleasing combination they form — such as shades of one colour, neighbouring colours, or opposites — while treating neutrals as always fitting in.

## Background
Harmony is evaluated over the scheme set by clustering hues (FR-12) and testing schemes in the FR-13 order (neutral-based → monochromatic → analogous → complementary → triadic), first match wins, with neutrals never counting against a scheme (FR-3, FR-14).

## Technical requirements
- `app/matcher/harmony.py`: hue clustering (within a 30° arc, circular-mean cluster hue, including across the 0° wrap) per FR-12
- Ordered scheme test per FR-13 with the documented tolerances (complementary 180°±20°, triadic 120°±15°, analogous within 60°)
- Empty scheme set → neutral-based; monochromatic-over-analogous precedence on first match
- Neutral transparency (FR-3, FR-14); exposes the matched scheme and the deviation needed for scheme strength (FR-41.1)
- Tolerances from `constants.py`; standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [x] Clustering correct including the wrap; scheme test returns the first matching scheme in FR-13 order
- [x] Tolerance boundaries correct (the §4.5 rows); neutrals never change the matched scheme (FR-14)
- [x] FR-15's harmony predicate composes scheme-set satisfaction (exercised end-to-end in slots/ranking)
- [x] Standard library only; passes the §5.2 allowlist
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_harmony.py` (§4.5): clustering within/across the wrap; one pass+one fail per scheme and the order itself (mono-over-analogous, empty→neutral-based); tolerance boundary rows (complementary 159.9/160/180/200/200.1, triadic 105/135 edges, analogous 60/60.1); neutral-transparency examples + Hypothesis property.

## Notes
- 2026-06-15 — created
- 2026-06-15 — done. `SchemeResult` frozen dataclass (scheme, deviation); `_arc_span` via max-gap formula (handles wrap correctly, including duplicate hues); `cluster_hues` — greedy sort + circular-wrap merge; `evaluate_scheme` — FR-13 order (neutral-based → mono → analogous → complementary → triadic), each with the correct tolerance; `is_harmonious` predicate. Float tolerance `_FLOAT_TOL=1e-9` guards `atan2` drift on exact boundaries. 366 backend tests, all green; `app/matcher/` 100% line+branch.
