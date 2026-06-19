---
id: HUE-077
title: Grouped inventory view with order toggle
type: story
status: todo
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-067, HUE-035]
implements: [FR-35, FR-47, NFR-6]
tests_required: true
estimate: 3
---

## User story
As the owner
I want my wardrobe grouped by category and orderable by colour or date
so that I can browse it as a tidy, scannable spectrum.

## Acceptance criteria

**Scenario 1: Grouped, hue-ordered (default)**
- Given the inventory page
- When it loads with the default order
- Then garments are grouped by category with a header + count per group; within a group they form a hue spectrum with neutral-primary garments after the chromatic spectrum (FR-47)

**Scenario 2: Order toggle**
- Given the inventory
- When I switch the order to Date added
- Then each group orders newest-first (FR-47)

**Scenario 3: Combined filters**
- Given category and colour filters
- When both are active
- Then the list matches category AND family (any role), with a clear-filters affordance and updated count (FR-35)

## Technical approach
- Read the flat ordered list from `GET /api/garments` (`order=hue|date`, `category` filter) and **group by `category`** by walking it (contract §2.6); per-group header + count
- Order toggle (Hue default / Date added); category dropdown region-grouped; colour dropdown with swatches; measured-colour palette strips (FR-5)
- Empty-wardrobe / empty-filter / loading / load-failure states (HANDOFF-03)

## Design references
- Wireframes: docs/04-wireframes/03-inventory.md; HANDOFF-03-inventory.md (all seven states)

## Tests
- `Wardrobe.test.tsx` (§10.1): grouping by walking the ordered list; order toggle issues `order=hue|date`; combined filters issue the right params; neutrals-after-spectrum; empty/loading/error states
- Covered end-to-end by E2E journey 1 (HUE-085)

## QA steps
- [ ] Load inventory → expect per-category groups with headers/counts, Hue spectrum default
- [ ] Switch to Date added → expect newest-first within each group
- [ ] Apply category + colour filters → expect AND match and updated count; clear filters works

## Definition of done
- [ ] Acceptance criteria met
- [ ] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher-touching work: n/a
- [ ] Detection-touching work: n/a
- [ ] Evaluation/inventory-perf-touching work: `make test-perf` passes (§12.3.5) — server half re-baselined in HUE-084
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6) — deferred to HUE-085
- [ ] QA steps recorded and repeated in the chat completion report
- [ ] Ticket status + notes updated in the same commit (§12.3.7)

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
