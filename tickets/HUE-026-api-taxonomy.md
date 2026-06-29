---
id: HUE-026
title: Taxonomy endpoint
type: task
status: done
milestone: 8
batch: api
layer: api
depends_on: [HUE-025, HUE-009]
implements: [FR-1, FR-2, FR-3, FR-4, FR-5, FR-29]
tests_required: true
estimate: 2
---

## In plain English
Provides the screens with the full list of colour families the app recognises, along with a representative colour for each, so the owner can pick from them when adding a colour by hand and so the colour legend can be displayed.

## Background
The UI needs the palette taxonomy for family pickers (manual colour adds, FR-29) and legend display (FR-5). `GET /api/taxonomy` exposes the matcher's families with canonical HSL and, for chromatic families, the representative hue and arc (contract §2.2).

## Technical requirements
- `GET /api/taxonomy`: all nineteen families from `matcher.taxonomy`; `neutral` flag; `canonical` HSL per family; `representative_hue` + `hue_arc` on chromatic families only
- Each `canonical` classifies into its own family (the contract §2.2 invariant)
- Pure read from the matcher; no persistence

## Definition of done (acceptance criteria)
- [x] Response lists all nineteen families with `neutral` and `canonical`; chromatic families carry `representative_hue`+`hue_arc` (contract §2.2)
- [x] Every `canonical` classifies into its own family (cross-checked against `matcher.taxonomy`)
- [x] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [x] Relevant extra gate green where applicable ((none — default gate only))
- [x] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_taxonomy.py` (§7.2): nineteen families; arc/representative present exactly on chromatic families; each canonical self-classifies (assertion calls `matcher.taxonomy` directly).

## Notes
- 2026-06-15 — created
- 2026-06-16 — done: `app/services/taxonomy_service.py` (list_families → plain dicts, satisfying
  contract 5 no-direct-matcher-import rule); `app/api/taxonomy.py` (GET /taxonomy, response_model_exclude_none
  keeps representative_hue/hue_arc absent on neutrals); added CanonicalHSL/FamilyOut/TaxonomyResponse to
  schemas.py; wired taxonomy_router in main.py. Also fixed pyproject.toml contract 5 — the "forbidden" type
  does transitive checking, so added ignore_imports listing every legitimate services→lower-layer import edge
  (17 entries); future service imports to lower layers must be added there. `make test` → 784 passed, 1
  skipped, 0 warnings; all 5 import-linter contracts kept.
- Sanity: `cd backend && .venv/bin/pytest tests/api/test_taxonomy.py -q`
