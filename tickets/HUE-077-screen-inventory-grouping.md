---
id: HUE-077
title: Grouped inventory view with order toggle
type: story
status: done
milestone: 14
batch: frontend
layer: frontend
depends_on: [HUE-067, HUE-035]
implements: [FR-35, FR-47, NFR-6]
tests_required: true
estimate: 3
---

## In plain English
Shows the wardrobe neatly grouped by kind of clothing, with each group laid out as a colour spectrum or by date added, and lets the owner filter by kind and colour together.

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
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy §12.2 and passing in `make test`
- [ ] Matcher-touching work: n/a
- [ ] Detection-touching work: n/a
- [ ] Evaluation/inventory-perf-touching work: `make test-perf` passes (§12.3.5) — server half re-baselined in HUE-084
- [ ] User-flow-touching work: `make test-e2e` passes (§12.3.6) — deferred to HUE-085
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit (§12.3.7)

## Notes
- 2026-06-18 — created (Milestone 13 ticket generation)
- 2026-07-02 — implemented. Added order toggle (Hue / Date added) wired to `?order=` URL param
  and passed through `useGarments({ order })`. The flat garment list is grouped by walking it and
  collecting consecutive same-category items into section+header blocks
  (`data-testid="group-header-{category}"`). Category dropdown changed from a flat list to
  region-grouped `<optgroup>` elements (Head / Upper body / Lower body / Feet) using a static
  mapping that mirrors the taxonomy structure. `clearFilters` updated to preserve the `order` param.
  7 new frontend tests added (order toggle render + state, order URL param, grouping headers,
  optgroup structure); 1112 backend + 188 frontend tests pass at zero warnings.
- Sanity test: `cd frontend && npm run test -- Inventory --run`

## QA steps
- [ ] Load /wardrobe → expect garments grouped by category with "Category · N" headers; Hue
  button is active (darker); garments within a group form a colour spectrum
- [ ] Click "Date added" toggle → button becomes active; garments within each group reorder
  newest-first (verify by checking thumbnails order changes if you have multiple garments
  of the same category)
- [ ] Apply category filter (e.g. Jumper) + colour filter (e.g. Teal) → expect only matching
  garments, updated count, "Clear filters" button; click Clear → both dropdowns reset, all
  garments return; order toggle state is preserved after clearing filters
- [ ] Refresh with ?order=date in the URL → Date added button is active on mount
- [ ] Open the Type dropdown → expect four `<optgroup>` sections labelled Head, Upper body,
  Lower body, Feet each containing their respective categories
