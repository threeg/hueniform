---
id: HUE-007
title: Implement matcher.constants
type: task
status: todo
milestone: 8
batch: matcher
layer: matcher
depends_on: [HUE-004]
implements: [NFR-9]
tests_required: true
estimate: 2
---

## Background
Requirements §1.4 makes every numeric threshold contractual and requires it to be a named constant so it can be tuned in one place. This module is the single source of those values; the drift-guard test (§4.1) makes tuning a constant force a recorded requirements change.

## Technical requirements
- `app/matcher/constants.py`: named constants for arc width (30), the FR-2 neutral-rule thresholds, role cut-offs (30 and 15), complementary tolerance (20), triadic tolerance (15), analogous arc (60), the ranking weights, and `MAX_ANCHOR_CANDIDATES`
- Standard library only (NFR-9); no framework imports
- Each constant documented with the requirements section it mirrors

## Definition of done (acceptance criteria)
- [ ] Every threshold named in requirements §1.4 present as a constant with the documented value
- [ ] Module imports only the standard library (passes the §5.2 allowlist)
- [ ] `matcher/test_constants.py` asserts each value against the requirements, with failure messages citing the section (§4.1)
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`backend/tests/matcher/test_constants.py` (§4.1): every constant asserted equal to its documented value; each assertion's message cites the requirements §1.4 row it mirrors. Drives the matcher coverage gate.

## Notes
- 2026-06-15 — created
