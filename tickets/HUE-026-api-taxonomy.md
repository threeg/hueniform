---
id: HUE-026
title: Taxonomy endpoint
type: task
status: todo
milestone: 8
batch: api
layer: api
depends_on: [HUE-025, HUE-009]
implements: [FR-1, FR-2, FR-3, FR-4, FR-5, FR-29]
tests_required: true
estimate: 2
---

## Background
The UI needs the palette taxonomy for family pickers (manual colour adds, FR-29) and legend display (FR-5). `GET /api/taxonomy` exposes the matcher's families with canonical HSL and, for chromatic families, the representative hue and arc (contract §2.2).

## Technical requirements
- `GET /api/taxonomy`: all nineteen families from `matcher.taxonomy`; `neutral` flag; `canonical` HSL per family; `representative_hue` + `hue_arc` on chromatic families only
- Each `canonical` classifies into its own family (the contract §2.2 invariant)
- Pure read from the matcher; no persistence

## Definition of done (acceptance criteria)
- [ ] Response lists all nineteen families with `neutral` and `canonical`; chromatic families carry `representative_hue`+`hue_arc` (contract §2.2)
- [ ] Every `canonical` classifies into its own family (cross-checked against `matcher.taxonomy`)
- [ ] Tests added/updated per test strategy §12.2 (or exemption stated below) and passing in `make test`
- [ ] Relevant extra gate green where applicable ((none — default gate only))
- [ ] Ticket status + notes updated in the same commit

## Tests / verification
`api/test_taxonomy.py` (§7.2): nineteen families; arc/representative present exactly on chromatic families; each canonical self-classifies (assertion calls `matcher.taxonomy` directly).

## Notes
- 2026-06-15 — created
