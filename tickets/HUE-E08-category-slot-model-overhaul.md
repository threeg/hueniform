---
id: HUE-E08
title: Category & slot-model overhaul
type: epic
status: todo
milestone: 14
batch: matcher
layer: matcher
depends_on: []
implements: [FR-16, FR-17, FR-18, FR-19, FR-20, FR-21, FR-22, FR-36, FR-49, FR-50, FR-51, FR-52, NFR-9]
tests_required: false
estimate: 8
---

## Summary
Deliver v0.2.0 feature F4: redesign the garment-type taxonomy and the rigid outfit
structure into the **category ≠ slot ≠ region** model (requirements §5). The garment
taxonomy expands to the FR-16 categories; the upper-body layer stack grows from three to
**four** (`base → shirt → mid → outer`, outermost dominant); one-piece garments span the
lower-body and `base` slots; adornments split into statement/minor tiers; required slots
become configurable and mostly-removable with a mandatory lower-body floor; and a request
may constrain a slot to a subset of its categories (FR-52). This is **foundational and the
highest-risk workstream** — it rewrites the 100 %-covered deterministic matcher — so it is
sequenced first and led by the golden-file snapshot baseline (HUE-059).

## Scope
- **In scope:**
  - The matcher snapshot baseline captured before any rewrite (HUE-059)
  - `matcher.constants` and `matcher.slots` rewritten for the region/slot/adornment model
  - The `garments.type` category value-set change and the one-off data migration
  - `GET /api/taxonomy` regions/slots model
  - The suggestion service + endpoint **slot-selection** rewrite (FR-36/FR-51) and the
    **per-category slot constraint** (FR-52)
  - Frontend API-client/MSW update to the v0.2.0 contract; the confirm-and-correct category
    picker and the outfit-request slot selector / category checklist
- **Out of scope (other epics):** the Cream family and ranking/quality changes (E09); the
  suggestion count (E09); pins and colour/scheme anchors (E06); inventory grouping/ordering
  (E10); category edit (E07). Metadata, availability and multi-photo remain deferred (brief F3).

## Success criteria
All child tickets done; the matcher implements requirements §5 over the new model with the
100 % line+branch gate intact and the import contracts unchanged; the snapshot baseline is
in place and every behavioural change is a reviewed diff; the owner can request an outfit
over the new configurable slots (defaults + removable, mandatory lower body) and constrain a
slot to chosen categories, within NFR-5.

## Children
- HUE-059 — Matcher golden-file snapshot baseline
- HUE-060 — matcher.constants v0.2.0 (category/slot model and new named values)
- HUE-061 — matcher.slots rewrite (regions, four-layer stack, one-piece, adornment tiers)
- HUE-065 — Storage category value-set and data migration
- HUE-066 — GET /api/taxonomy regions/slots model
- HUE-067 — Frontend API client and MSW handlers — v0.2.0 contract
- HUE-068 — Suggestion service: slot-selection and per-category constraint rewrite
- HUE-069 — POST /api/suggestions: slot-selection and constraint request/response
- HUE-070 — Confirm-and-correct category picker
- HUE-071 — Outfit-request slot selector and category-constraint checklist

## References
- docs/02-requirements.md §2.1, §5 (FR-16–FR-22, FR-49–FR-52), §6.7
- docs/03-architecture.md §2.2, §3.1, §4.3
- docs/03-api-contract.md §1.3, §1.3a, §2.2, §2.12
- docs/05-test-strategy.md §4.1, §4.6, §4.10, §7.2, §7.4, §7.5
- docs/spikes/2026-06-18-f4-category-slot-model.md
- docs/04-wireframes/05-outfit-request.md, HANDOFF-05-outfit-request.md

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
