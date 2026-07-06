---
id: HUE-113
title: Wardrobe visual fidelity
type: story
status: done
milestone: 20
batch: cleanup
layer: frontend
depends_on: [HUE-101]
implements: []
tests_required: true
estimate: 2
---

## In plain English
The wardrobe screen's order toggle, category group headers, card styling and result-count placement don't match the prototype. The toggle and headers should be pill-shaped, cards need tweaked radii and a thinner palette strip, and the garment count should sit beside the page title.

## User story
As the owner
I want the wardrobe's visual details to match the design
so that filters, groups and cards look as intended.

## Acceptance criteria

**Scenario 1: Pill-shaped order toggle**
- Given the filter bar
- When the Hue / Date added toggle renders
- Then it is pill-shaped (`border-radius: 999px`), the active option has `background: #c66a4a; color: #fff; font-weight: 600; border-radius: 999px`, inactive shows `color: #a08a72`

**Scenario 2: Pill-badge group headers**
- Given garments grouped by category
- When a group header renders (e.g. "Shirt 4")
- Then it is a pill badge: `background: #f3e6d4; border-radius: 999px; padding: 7px 16px` with the count in a white sub-pill (`background: #fff; border-radius: 999px; font: 600 11px 'Space Mono'`)

**Scenario 3: Card tweaks**
- Given the garment card grid
- When cards render
- Then `border-radius: 13px`, palette strip height is 8 px (not 12 px)

**Scenario 4: Desktop grid**
- Given a desktop viewport
- When the card grid renders
- Then it uses `grid-template-columns: repeat(4, 1fr); gap: 18px`

**Scenario 5: Result count position**
- Given garments loaded
- When the page title row renders
- Then the count (e.g. "137 garments") sits to the right of the "Wardrobe" heading, not inside the filter bar

## Technical approach
- Update `Wardrobe.module.css`: pill-radius on order toggle + active style; new `.groupBadge` and `.groupCount` classes replacing the current border-bottom header; card `border-radius: 13px`; fixed 4-column grid at desktop; move count beside heading
- Update `Wardrobe.tsx`: restructure the group header markup to a pill badge with a count sub-pill; move the result count into the title row
- Pass `height={8}` to `<PaletteStrip>` in the garment card (or change the default)
- No behaviour, route or contract change

## Design references
- Prototype: `docs/designs/heuniform/project/Hueniform App.dc.html` — Screen 03 state A (lines ~436–477: title + count row, filter pills, order toggle, group pill badges, card grid)
- Screenshots: `docs/designs/heuniform/project/screenshots/01-s.png` (desktop wardrobe)

## Tests
- Update `Inventory.test.tsx`: assert group headers render as pill badges; assert count is within the title row; `jest-axe` clean

## QA steps
- [x] Open `/` at desktop: garment count beside the "Wardrobe" heading (not in filter bar)
- [x] Order toggle: pill-shaped, Hue = clay fill, Date added = muted text
- [x] Group headers: pill badges with warm tint background and white count sub-pill
- [x] Cards: 4-column grid, rounded corners, thin (8 px) palette strip
- [x] Resize to mobile: grid goes to 2 columns, toggle and badges still render correctly

## Definition of done
- [x] Acceptance criteria met
- [x] Tests added/updated per test strategy and passing in `make test`
- [x] Matcher-touching work: n/a
- [x] User-flow-touching work: `make test-e2e` — 27 passed, 2 skipped, zero failures
- [x] QA steps recorded and repeated in the chat completion report
- [x] Ticket status + notes updated in the same commit

## Notes
- 2026-07-06 — created (visual-fidelity audit of v0.3.0 against prototype)
- 2026-07-06 — done. Added `.titleRow` + `<h1 class="title">Wardrobe</h1>` to `Wardrobe.tsx`; moved result-count span there (out of filter bar). Group headers restructured to `<h2 class="groupBadge">` with a `<span class="groupCount">` sub-pill. Order toggle changed to pill style: `--radius-pill` on outer + each button, inner padding, transparent inactive background; active buttons use clay fill + `--weight-semibold`. Added `@media (min-width: 1024px)` for 4-column grid. `GarmentCard.tsx` passes `height={8}` to PaletteStrip; card `border-radius` changed from `--radius-lg` to `--radius-md`. Tests: 285 passed; e2e: 27 passed, 2 skipped. Sanity test: `cd frontend && npx vitest run src/routes/Inventory.test.tsx`.
