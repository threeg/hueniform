---
id: HUE-060
title: matcher.constants v0.2.0 — category/slot model and new named values
type: task
status: done
milestone: 14
batch: matcher
layer: matcher
depends_on: [HUE-059, HUE-007]
implements: [NFR-9]
tests_required: true
estimate: 3
---

## Background
The v0.2.0 model introduces many new contractual constants (requirements §1.4, §2.1, §5, §7).
They all live in `matcher.constants` so they can be tuned in one place and asserted by the
drift guard (test strategy §4.1). This ticket adds the constant **definitions** only; the
behaviour that consumes them is implemented by the submodule tickets (HUE-061–HUE-064). The
`matcher` stays standard-library-only (NFR-9). Captured behaviour shifts (e.g. Cream is not
*used* until HUE-062) surface in the HUE-059 snapshot when their consuming ticket lands.

## Technical requirements
- `app/matcher/constants.py` — add, as named constants (requirements §1.4):
  - **Cream** thresholds: `CREAM_H_LOW=20`, `CREAM_H_HIGH=70`, `CREAM_S_LOW=10`, `CREAM_S_HIGH=45`, `CREAM_L_MIN=88` (FR-2)
  - **Ranking**: `NEUTRAL_BASED_STRENGTH=0.98`, `WEIGHT_VARIETY=15` (raised from 5), with `WEIGHT_SCHEME_STRENGTH=100`, `WEIGHT_ECHO_BONUS=10` retained (FR-41)
  - **Count**: `COUNT_MIN=1`, `COUNT_MAX=25`, `COUNT_DEFAULT=3` (FR-48)
  - **Slot model**: the FR-16 category set; the slot keys; the four-level upper-body layer order `base → shirt → mid → outer`; the statement vs minor adornment membership; the default-selected slots (`base`, `lower_body`, `socks`, `shoes`); the mandatory `lower_body` floor; the one-piece categories and the `base` slot they also occupy (FR-16, FR-49–FR-51)
- Standard library only; no behaviour change in other submodules yet
- Old v0.1.0 type/slot constants superseded by the new sets (note any removed names)

## Definition of done (acceptance criteria)
- [x] Every new constant present with its contractual value; old superseded ones removed/renamed
- [x] `test_constants.py` asserts each value and the named-set membership/order (renamed keys `mid`/`outer`, dropped `jersey` category) per §4.1
- [x] Standard library only; passes the §5.2 allowlist
- [x] Tests added/updated per test strategy §12.2 and passing in `make test`
- [x] Matcher coverage gate (100% line+branch) holds (§12.3.3)
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_constants.py` (§4.1) — the drift guard extended to every new value and named set,
each failure message citing the requirements section. No snapshot change expected from this
ticket alone (constants are not yet consumed).

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-06-19 — implemented: added Cream thresholds (FR-2 rule 8), raised `WEIGHT_VARIETY` 5→15, added `NEUTRAL_BASED_STRENGTH=0.98`, `COUNT_MIN/MAX/DEFAULT`, and the full §5 slot model (`UPPER_BODY_LAYERS`, `ALL_SLOTS`, `ALL_CATEGORIES`, `CATEGORY_SLOT`, `ONE_PIECE_CATEGORIES`, `ONE_PIECE_UPPER_SLOT`, `STATEMENT_ADORNMENT_SLOTS`, `MINOR_ADORNMENT_SLOTS`, `DEFAULT_SLOTS`, `MANDATORY_SLOT`). `jersey` absent from `ALL_CATEGORIES`; slot keys `mid`/`outer` replace v0.1.0 `jersey`/`jacket`. `test_constants.py` extended with 23 new drift-guard assertions. 912 backend tests passed, matcher 100% coverage gate held, 134 frontend tests passed. No snapshot change (constants not yet consumed).

## QA steps
N/A — constants-only change; no user-visible behaviour.
