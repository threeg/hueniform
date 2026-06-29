---
id: HUE-010
title: Implement matcher.roles
type: task
status: done
milestone: 8
batch: matcher
layer: matcher
depends_on: [HUE-009]
implements: [FR-6, FR-7, FR-8, FR-9, FR-10, FR-11, NFR-9]
tests_required: true
estimate: 3
---

## In plain English
Works out the part each colour plays in a garment — the main colour, supporting colours, or just a small accent — based on how much of the garment it covers, so outfit suggestions can treat dominant and minor colours differently.

## Background
Colour roles (primary / dual-primary / secondary / minor) are derived from proportions at evaluation time, never persisted (architecture §2.2), so FR-7 has a single source of truth. This module also classifies secondary compatibility (FR-9) and records minor echoes (FR-11).

## Technical requirements
- `app/matcher/roles.py`: a frozen `Garment` value type (type + ordered `Colour` list) and role derivation per FR-7 (largest proportion = primary, saturation tie-break; any ≥30% is primary → dual-primary; ≥15% & <30% secondary; <15% minor)
- Primary-qualification helper for FR-8 (dual-primary qualifies only if both primaries qualify)
- Secondary-compatibility classification (neutral / in-scheme / echo) for FR-9
- Minor colours never disqualify (FR-10); expose minor colours for the echo bonus (FR-11)
- Proportions validated as summing to 100 across 1–4 colours (FR-6); standard library only (NFR-9)

## Definition of done (acceptance criteria)
- [x] Role derivation total and stable for any valid palette; dual-primary detected; tie-break by saturation
- [x] FR-8/FR-9/FR-10/FR-11 helpers correct (one example per branch plus a failing example)
- [x] Standard library only; passes the §5.2 allowlist
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable (`make test` matcher coverage gate: 100% line+branch on app/matcher/ (§12.3.3))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`matcher/test_roles.py` (§4.4): boundary rows for the 30/15 cut-offs; saturation tie-break; FR-8 one-pass-one-fail disqualification; FR-10 minor-harmlessness property; FR-9/FR-11 secondary classification branches; Hypothesis totality over valid palettes.

## Notes
- 2026-06-15 — created
- 2026-06-15 — done. `Garment` and `GarmentRoles` frozen dataclasses; `validate_palette` (FR-6); `derive_roles` — dominant via proportion+saturation key, then ≥30% secondary-primary promotion, bucket sort with saturation tie-break preserved; `all_primaries_qualify` (FR-8); `classify_secondary` (FR-9: neutral→in_scheme→echo→None); `minor_echo_families` (FR-11). 306 backend tests, all green; `app/matcher/` 100% line+branch.
