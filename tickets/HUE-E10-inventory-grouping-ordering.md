---
id: HUE-E10
title: Inventory grouping & ordering
type: epic
status: todo
milestone: 14
batch: frontend
layer: frontend
depends_on: []
implements: [FR-35, FR-47, NFR-6]
tests_required: false
estimate: 3
---

## Summary
Deliver v0.2.0 feature F6: replace the flat, filter-only inventory with garments **grouped by
category**, orderable within each group by **hue — as a colour spectrum (the default)** — or
by **date added, newest first** (FR-47). The existing category/colour filters are retained
(FR-35). Mostly frontend with a small ordering addition in the read query; independent of the
matcher. NFR-6 (responsive at 500 garments) continues to apply.

## Scope
- **In scope:**
  - Service/query ordering by primary-colour hue (neutrals after the chromatic spectrum) and
    by `created_at` newest-first (FR-47)
  - `GET /api/garments` `order` parameter and the `type` → `category` filter rename (FR-35, FR-47)
  - The grouped inventory view, the order toggle and the category-grouped filter UI
- **Out of scope:** search, multi-sort and multi-photo (out of scope, FR-47); any schema change.

## Success criteria
All child tickets done; the inventory shows per-category groups with headers and counts;
within a group, Hue (default) orders as a spectrum with neutral-primary garments trailing, and
Date added orders newest-first; combinable category-AND-family filters still work; the view
stays responsive at 500 garments (NFR-6, server half in `test-perf`).

## Children
- HUE-075 — Inventory ordering (hue spectrum / date) in the read query
- HUE-076 — GET /api/garments: order parameter and category filter rename
- HUE-077 — Grouped inventory view with order toggle

## References
- docs/02-requirements.md §6.6 (FR-35 extended, FR-47), NFR-6
- docs/03-architecture.md §3.1
- docs/03-api-contract.md §2.6
- docs/05-test-strategy.md §7.2, §8.2, §10.1
- docs/04-wireframes/03-inventory.md, HANDOFF-03-inventory.md

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
