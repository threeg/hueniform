---
id: HUE-062
title: matcher.taxonomy — the Cream family
type: task
status: todo
milestone: 14
batch: matcher
layer: matcher
depends_on: [HUE-060, HUE-009]
implements: [FR-2, NFR-9]
tests_required: true
estimate: 2
---

## Background
Pale warm near-neutrals (cream, ecru, ivory, off-white) were *measured* correctly but
mis-classified as chromatic Yellow in v0.1.0 (they fell outside White, Grey and Beige/Tan).
Add **Cream** as neutral family order 8 (requirements §2.1, FR-2), using the HUE-060
constants. This is the F5 near-neutral taxonomy fix; it shifts some classifications, so the
HUE-059 snapshot is updated in this commit.

## Technical requirements
- `app/matcher/taxonomy.py` — add the **Cream** rule (order 8): `CREAM_H_LOW ≤ H ≤ CREAM_H_HIGH and CREAM_S_LOW ≤ S ≤ CREAM_S_HIGH and L > CREAM_L_MIN`, evaluated after White/Grey/Beige-Tan; Cream is neutral and carries no hue for harmony (FR-3)
- Beige/Tan keeps `L ≤ 88`, Cream owns `L > 88` for the shared `S ≤ 45` band; Cream's hue ceiling 70° (vs Beige/Tan's 60°); White (order 2) unchanged
- Cream's canonical HSL classifies into Cream; the family count becomes **twenty**
- Standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [ ] Cream classifies the ecru/white-jeans case (≈ H52, S28, L90) and the boundary rows hold (§4.3)
- [ ] Ordering correct: White before Cream; Beige/Tan→Cream hand-off at L=88; hue ceiling at 70°; S ceiling at 45
- [ ] Cream is neutral (FR-3); twenty families total; canonical → Cream
- [ ] HUE-059 snapshot classifications updated and committed (§4.10)
- [ ] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher coverage gate (100% line+branch) holds (§12.3.3)
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_taxonomy.py` (§4.3) — the Cream boundary rows (Beige/Tan hand-off, hue ceiling,
S edge, White-before-Cream order, the worked example) and the totality Hypothesis property
updated to twenty families. A pale-near-neutral detection fixture (§11.1) for the model suite.

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
